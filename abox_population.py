import json
import re
import ssl
from datetime import time as TimeType
from pathlib import Path
from typing import Dict, List, Optional, Set
from owlready2 import *
from datetime import datetime   

import urllib.request
ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = Path(__file__).parent
ONTOLOGY_PATH = BASE_DIR / "german_city_tourism_final_d2.owl"
TOURS_JSON_PATH = BASE_DIR / "data" / "all_cities_tours.json"
ATTRACTIONS_JSON_PATH = BASE_DIR / "data" / "trip_advisor_data_enriched_final.json"
OUTPUT_PATH = BASE_DIR / "german_city_tourism_populated.owl"

class OntologyPopulator:

    def __init__(self, ontology_path: Path):

        self.onto = get_ontology(f"file://{ontology_path}").load()

        # Avoid creating new individuals for existing ones
        self.cities: Dict[str, Thing] = {}
        self.budget_tiers: Dict[str, Thing] = {}
        self.location_settings: Dict[str, Thing] = {}
        self.days_of_week: Dict[str, Thing] = {}
        self.languages: Dict[str, Thing] = {}
        self.venue_types: Dict[str, Thing] = {}

        self._initialize_shared_individuals()

    def _initialize_shared_individuals(self):

            for tier in ['free', 'low', 'medium', 'high']:
                individual = self.onto.BudgetTier(f"budget_{tier}")
                self.budget_tiers[tier] = individual

            for setting in ['indoor', 'outdoor']:
                individual = self.onto.LocationSetting(f'location_{setting}')
                self.location_settings[setting] = individual

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days:
                individual = self.onto.DayOfWeek(f'day_{day.lower()}')
                self.days_of_week[day] = individual

            cities = ['Berlin', 'Cologne', 'Munich', 'Hamburg', 'Frankfurt', 'Stuttgart', 'Dusseldorf', 'Dortmund', 'Essen', 'Leipzig']
            for city in cities:
                individual = self.onto.City(f'city_{city.lower()}')
                # Store with lowercase key to match lookup logic
                self.cities[city.lower()] = individual

    def _get_or_create_language(self, language_name: str) -> Thing:
        if language_name not in self.languages:
            iri_name = f'lang_{language_name.lower().replace(" ", "_")}'
            individual = self.onto.Language(iri_name)
            self.languages[language_name] = individual
        return self.languages[language_name]

    def _sanitize_name_for_iri(self, name: str) -> str:
        """Convert name to valid IRI component."""
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[\s-]+', '_', sanitized)
        return sanitized.lower()
    
    def _parse_time(self, time_str: str) -> Optional[TimeType]:
        try: 
            if 'AM' in time_str or 'PM' in time_str:
                time_str = time_str.strip()
                if '-' in time_str:
                    time_str = time_str.split('-')[0].strip()

                parsed = datetime.strptime(time_str, '%I:%M %p')
                return parsed.time()
            else:
                parts = time_str.split(':')
                hour = int(parts[0])
                minute = int(parts[1])
                return TimeType(hour, minute)
        except Exception as e:
            print(f"Warning: Could not parse time '{time_str}': {e}")
            return None

    def _create_operating_hours(self, day: str, hours_str: str) -> Optional[Thing]:
        if not hours_str:
            return None

        # Format: 10:00 AM - 5:00 PM
        match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)', hours_str)
        if not match:
            print(f"Could not parse operating hours: {hours_str}")
            return None
        
        open_time_str = match.group(1)
        close_time_str = match.group(2)
        
        open_time = self._parse_time(open_time_str)
        close_time = self._parse_time(close_time_str)
        
        if not open_time or not close_time:
            print(f"Could not parse operating hours: {hours_str}")
            return None
        
        iri_name = f"hours_{day.lower()}_{open_time.hour}{open_time.minute}_{close_time.hour}{close_time.minute}"
        hours_individual = self.onto.OperatingHours(iri_name)
        hours_individual.appliesToDay = [self.days_of_week[day]]
        hours_individual.opensAt = open_time
        hours_individual.closesAt = close_time
        return hours_individual

    def populate_tours(self, tours_data: List[Dict]):
        """Populate Tour individuals from JSON data."""
        print(f"\nPopulating {len(tours_data)} tours...")
        
        for idx, tour_data in enumerate(tours_data, 1):
            try:
                # Create sanitized IRI name
                title = tour_data.get('title', f'tour_{idx}')
                iri_name = f"tour_{self._sanitize_name_for_iri(title)}_{idx}"
                
                # Create Tour individual
                tour = self.onto.Tour(iri_name)
                
                # Set city relationship
                if 'city' in tour_data and tour_data['city']:
                    city_key = tour_data['city'].lower()
                    if city_key in self.cities:
                        tour.isInCity = self.cities[city_key]
                
                # Set budget tier
                if 'budget_tier' in tour_data and tour_data['budget_tier']:
                    budget_key = tour_data['budget_tier'].lower()
                    if budget_key in self.budget_tiers:
                        tour.hasBudget = self.budget_tiers[budget_key]  
                
                # Set location setting
                if 'location_setting' in tour_data and tour_data['location_setting']:
                    setting_key = tour_data['location_setting'].lower()
                    if setting_key in self.location_settings:
                        tour.hasLocationSetting = self.location_settings[setting_key]  
                
                # Set duration
                if 'duration' in tour_data and tour_data['duration']:
                    duration_iri = f"duration_{self._sanitize_name_for_iri(tour_data['duration'])}_{idx}"
                    duration = self.onto.Duration(duration_iri)
                    tour.hasDuration = duration  
                
                # Set meeting point
                if 'meeting_point' in tour_data and tour_data['meeting_point']:
                    meeting_point_iri = f"meeting_point_{idx}"
                    meeting_point = self.onto.MeetingPoint(meeting_point_iri)
                    tour.hasMeetingPoint = meeting_point  
                
                # Set languages
                if 'languages' in tour_data and tour_data['languages']:
                    languages_str = tour_data['languages']
                    lang_list = [lang.strip() for lang in languages_str.split(',')]
                    lang_individuals = []
                    for lang_name in lang_list:
                        if lang_name:
                            lang = self._get_or_create_language(lang_name)
                            lang_individuals.append(lang)
                    if lang_individuals:
                        tour.hasLanguage = lang_individuals
                
                # Set tour URL link
                if 'link' in tour_data and tour_data['link']:
                    tour.hasURL = tour_data['link']  
                
            except Exception as e:
                error_msg = f"Error creating tour {idx} ({tour_data.get('title', 'unknown')}): {e}"
                print(f"  {error_msg}")
        
        print(f"Created tours")

    def populate_attractions(self, attractions_data: List[Dict]):
            print(f"\nPopulating {len(attractions_data)} attractions...")
            
            for idx, attr_data in enumerate(attractions_data, 1):
                try:
                    # Determine venue subclass based on attraction_type
                    attr_type = attr_data.get('attraction_type', '').lower()
                    
                    # Map to ontology classes
                    if 'museum' in attr_type:
                        venue_class = self.onto.Museum
                    elif 'park' in attr_type or 'garden' in attr_type:
                        venue_class = self.onto.Park
                    elif 'nightlife' in attr_type or 'bar' in attr_type or 'club' in attr_type:
                        venue_class = self.onto.NightlifeVenue
                    else:
                        # Default to Sight for landmarks, monuments, etc.
                        venue_class = self.onto.Sight
                    
                    # Create sanitized IRI name
                    name = attr_data.get('name', f'attraction_{idx}')
                    iri_name = f"venue_{self._sanitize_name_for_iri(name)}_{idx}"
                    
                    # Create venue individual
                    venue = venue_class(iri_name)
                    
                    # Set city relationship
                    if 'city' in attr_data and attr_data['city']:
                        city = attr_data['city'].lower()
                        if city in self.cities:
                            venue.isInCity = self.cities[city]
                    
                    # Set budget tier
                    if 'budget_tier' in attr_data and attr_data['budget_tier']:
                        budget_key = attr_data['budget_tier'].lower()
                        if budget_key in self.budget_tiers:
                            venue.hasBudget = self.budget_tiers[budget_key]  # Functional
                    
                    # Set location setting
                    if 'location_setting' in attr_data and attr_data['location_setting']:
                        setting_key = attr_data['location_setting'].lower()
                        if setting_key in self.location_settings:
                            venue.hasLocationSetting = self.location_settings[setting_key]  # Functional
                    
                    # Set operating hours
                    if 'operating_hours' in attr_data and attr_data['operating_hours']:
                        operating_hours = attr_data['operating_hours']
                        if isinstance(operating_hours, dict):
                            hours_list = []
                            for day, hours_str in operating_hours.items():
                                if hours_str and day in self.days_of_week:
                                    hours_individual = self._create_operating_hours(day, hours_str)
                                    if hours_individual:
                                        hours_list.append(hours_individual)
                            if hours_list:
                                venue.hasOperatingHours = hours_list
                    
                    # Set venue type
                    if 'spec_type' in attr_data and attr_data['spec_type']:
                        spec_type = attr_data['spec_type']
                        type_iri = f"type_{self._sanitize_name_for_iri(spec_type)}_{idx}"
                        
                        # Create appropriate VenueType subclass
                        if isinstance(venue, self.onto.Museum):
                            venue_type = self.onto.MuseumType(type_iri)
                            venue.hasMuseumType = [venue_type]
                        elif isinstance(venue, self.onto.Park):
                            venue_type = self.onto.ParkType(type_iri)
                            venue.hasParkType = [venue_type]
                        elif isinstance(venue, self.onto.NightlifeVenue):
                            venue_type = self.onto.ClubType(type_iri)
                            venue.hasClubType = [venue_type]
                        elif isinstance(venue, self.onto.Sight):
                            venue_type = self.onto.SightType(type_iri)
                            venue.hasSightType = [venue_type]
                    
                    # Set attraction image URL
                    if 'image_url' in attr_data and attr_data['image_url']:
                        venue.hasImageURL = attr_data['image_url']  # Functional
                    
                        
                except Exception as e:
                    error_msg = f"Error creating attraction {idx} ({attr_data.get('name', 'unknown')}): {e}"
                    print(f"  {error_msg}")
                    
            
            print(f"Created attractions")         

    def save(self, output_path: Path):
        self.onto.save(file=str(output_path), format="rdfxml")
        print('Ontology saved')

    
def main():
    with open(TOURS_JSON_PATH, 'r', encoding='utf-8') as f:
        tours_data = json.load(f)
    
    with open(ATTRACTIONS_JSON_PATH, 'r', encoding='utf-8') as f:
        attractions_data = json.load(f)
    
    populator = OntologyPopulator(ONTOLOGY_PATH)
    populator.populate_tours(tours_data)
    populator.populate_attractions(attractions_data)
    populator.save(OUTPUT_PATH)

if __name__ == '__main__':
    main()


                
            