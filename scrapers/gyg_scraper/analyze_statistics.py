#!/usr/bin/env python3
"""
Script to analyze GetYourGuide tour data and extract comprehensive statistics.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Tuple
from io import StringIO


class TeeOutput:
    """Write to both stdout and a file."""
    def __init__(self, file_path: str):
        self.terminal = sys.stdout
        self.file = open(file_path, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.file.flush()
    
    def close(self):
        self.file.close()


def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    print('=' * 80)


def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f"\n{title}")
    print('-' * 80)


def parse_price(price_str: str) -> Optional[float]:
    """
    Parse price string to float.
    Examples: '€21', '€77', 'From €50'
    """
    if not price_str or price_str == 'N/A':
        return None
    
    # Extract numeric value from price string
    match = re.search(r'€?\s*(\d+(?:[.,]\d+)?)', price_str.replace(',', '.'))
    if match:
        return float(match.group(1))
    return None


def parse_duration(duration_str: str) -> Optional[Tuple[float, float]]:
    """
    Parse duration string to hours (min, max).
    Examples: '2 hours', '2 - 4 hours', 'Valid 1 - 2 days', '5 minutes'
    """
    if not duration_str or duration_str == 'N/A':
        return None
    
    duration_lower = duration_str.lower()
    
    # Handle days
    if 'day' in duration_lower:
        day_match = re.search(r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*day', duration_lower)
        if day_match:
            min_days = float(day_match.group(1))
            max_days = float(day_match.group(2)) if day_match.group(2) else min_days
            return (min_days * 24, max_days * 24)
    
    # Handle hours
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*hour', duration_lower)
    if hour_match:
        min_hours = float(hour_match.group(1))
        max_hours = float(hour_match.group(2)) if hour_match.group(2) else min_hours
        return (min_hours, max_hours)
    
    # Handle minutes
    minute_match = re.search(r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*minute', duration_lower)
    if minute_match:
        min_mins = float(minute_match.group(1))
        max_mins = float(minute_match.group(2)) if minute_match.group(2) else min_mins
        return (min_mins / 60, max_mins / 60)
    
    return None


def get_price_tier(price: Optional[float]) -> str:
    """Categorize price into tiers."""
    if price is None:
        return 'Unknown'
    elif price == 0:
        return 'Free'
    elif price <= 25:
        return 'Budget (≤€25)'
    elif price <= 50:
        return 'Mid-range (€26-50)'
    elif price <= 100:
        return 'Premium (€51-100)'
    else:
        return 'Luxury (>€100)'


def get_duration_category(duration: Optional[Tuple[float, float]]) -> str:
    """Categorize duration into categories."""
    if duration is None:
        return 'Unknown'
    
    avg_duration = (duration[0] + duration[1]) / 2
    
    if avg_duration < 1:
        return 'Quick (<1 hour)'
    elif avg_duration <= 2:
        return 'Short (1-2 hours)'
    elif avg_duration <= 4:
        return 'Half-day (2-4 hours)'
    elif avg_duration <= 8:
        return 'Full-day (4-8 hours)'
    else:
        return 'Multi-day (>8 hours)'


def parse_languages(languages_str: str) -> List[str]:
    """Parse languages string to list."""
    if not languages_str or languages_str == 'N/A':
        return []
    
    # Split by comma and clean up
    languages = [lang.strip() for lang in languages_str.split(',')]
    return [lang for lang in languages if lang]


def analyze_basic_stats(data: List[Dict]) -> Dict:
    """Extract basic statistics."""
    stats = {
        'total_tours': len(data),
        'cities': set(),
        'unique_languages': set(),
    }
    
    for item in data:
        if 'city' in item and item['city']:
            stats['cities'].add(item['city'])
        
        languages = parse_languages(item.get('languages', ''))
        stats['unique_languages'].update(languages)
    
    return stats


def count_by_field(data: List[Dict], field: str, top_n: int = None) -> List[tuple]:
    """Count tours by a specific field."""
    counter = Counter()
    
    for item in data:
        value = item.get(field)
        if value:
            counter[value] += 1
    
    if top_n:
        return counter.most_common(top_n)
    return counter.most_common()


def analyze_prices(data: List[Dict]) -> Dict:
    """Analyze price statistics."""
    prices = []
    tier_counter = Counter()
    
    for item in data:
        price = parse_price(item.get('price', ''))
        if price is not None:
            prices.append(price)
        tier = get_price_tier(price)
        tier_counter[tier] += 1
    
    stats = {
        'min': min(prices) if prices else None,
        'max': max(prices) if prices else None,
        'avg': sum(prices) / len(prices) if prices else None,
        'median': sorted(prices)[len(prices) // 2] if prices else None,
        'count_with_price': len(prices),
        'count_without_price': len(data) - len(prices),
        'tier_distribution': tier_counter
    }
    
    return stats


def analyze_durations(data: List[Dict]) -> Dict:
    """Analyze duration statistics."""
    durations = []
    category_counter = Counter()
    
    for item in data:
        duration = parse_duration(item.get('duration', ''))
        if duration:
            durations.append(duration)
        category = get_duration_category(duration)
        category_counter[category] += 1
    
    avg_durations = [(d[0] + d[1]) / 2 for d in durations]
    
    stats = {
        'min_hours': min(d[0] for d in durations) if durations else None,
        'max_hours': max(d[1] for d in durations) if durations else None,
        'avg_hours': sum(avg_durations) / len(avg_durations) if avg_durations else None,
        'count_with_duration': len(durations),
        'count_without_duration': len(data) - len(durations),
        'category_distribution': category_counter
    }
    
    return stats


def analyze_languages(data: List[Dict]) -> Dict:
    """Analyze language statistics."""
    language_counter = Counter()
    tours_by_language_count = Counter()
    
    for item in data:
        languages = parse_languages(item.get('languages', ''))
        lang_count = len(languages)
        
        if lang_count == 0:
            tours_by_language_count['No languages specified'] += 1
        elif lang_count == 1:
            tours_by_language_count['1 language'] += 1
        elif lang_count <= 3:
            tours_by_language_count['2-3 languages'] += 1
        elif lang_count <= 6:
            tours_by_language_count['4-6 languages'] += 1
        else:
            tours_by_language_count['7+ languages'] += 1
        
        for lang in languages:
            language_counter[lang] += 1
    
    return {
        'language_counts': language_counter,
        'tours_by_language_variety': tours_by_language_count
    }


def analyze_tour_types(data: List[Dict]) -> Dict:
    """Analyze tour types based on title keywords."""
    type_keywords = {
        'Walking Tour': ['walking tour', 'walking'],
        'Bus Tour': ['bus tour', 'hop-on hop-off', 'hop on hop off', 'sightseeing tour'],
        'Boat Tour': ['boat', 'cruise', 'river'],
        'Day Trip': ['day trip', 'full-day', 'half-day', 'day tour'],
        'Food & Drink': ['food', 'beer', 'wine', 'culinary', 'pub crawl', 'oktoberfest', 'currywurst'],
        'Historical/WWII': ['wwii', 'world war', 'third reich', 'concentration camp', 'nazi', 'hitler', 'cold war'],
        'Castle/Palace': ['castle', 'palace', 'schloss', 'neuschwanstein'],
        'Museum': ['museum'],
        'Adventure/Activity': ['swing', 'climbing', 'bike', 'segway', 'escape room', 'adventure'],
        'Nightlife': ['pub crawl', 'nightlife', 'party', 'club'],
        'Private Tour': ['private'],
    }
    
    type_counter = Counter()
    
    for item in data:
        title = item.get('title', '').lower()
        matched = False
        
        for tour_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in title:
                    type_counter[tour_type] += 1
                    matched = True
                    break
            if matched:
                break
        
        if not matched:
            type_counter['Other'] += 1
    
    return type_counter


def count_by_city_and_price_tier(data: List[Dict]) -> Dict[str, Counter]:
    """Count tours by city and price tier."""
    city_price_tier = defaultdict(Counter)
    
    for item in data:
        city = item.get('city', 'Unknown')
        price = parse_price(item.get('price', ''))
        tier = get_price_tier(price)
        city_price_tier[city][tier] += 1
    
    return dict(city_price_tier)


def analyze_meeting_points(data: List[Dict]) -> Dict:
    """Analyze meeting point statistics."""
    with_maps_link = 0
    without_maps_link = 0
    
    for item in data:
        maps_link = item.get('meeting_point_maps_link', '')
        if maps_link and maps_link != 'N/A':
            with_maps_link += 1
        else:
            without_maps_link += 1
    
    return {
        'with_maps_link': with_maps_link,
        'without_maps_link': without_maps_link,
        'percentage_with_maps': (with_maps_link / len(data) * 100) if data else 0
    }


def main():
    # Set up output to both console and file
    output_file = 'statistics_report.txt'
    tee = TeeOutput(output_file)
    sys.stdout = tee
    
    try:
        # Load data
        filepath = 'tours_data/all_cities_tours.json'
        print(f"Loading data from {filepath}...")
    
        try:
            data = load_data(filepath)
        except FileNotFoundError:
            print(f"Error: File not found. Please run combine_tours.py first to generate {filepath}")
            return
    
        # Basic Statistics
        print_section("📊 BASIC STATISTICS")
        basic_stats = analyze_basic_stats(data)
        print(f"\nTotal Tours: {basic_stats['total_tours']:,}")
        print(f"Total Cities: {len(basic_stats['cities'])}")
        print(f"Total Languages Available: {len(basic_stats['unique_languages'])}")
    
        # Tours by City
        print_section("🏙️  TOURS BY CITY")
        city_counts = count_by_field(data, 'city')
        for i, (city, count) in enumerate(city_counts, 1):
            percentage = (count / len(data)) * 100
            print(f"{i:2d}. {city:20s} {count:4d} tours ({percentage:5.2f}%)")
    
        # Price Analysis
        print_section("💰 PRICE ANALYSIS")
        price_stats = analyze_prices(data)
    
        print_subsection("Price Range")
        if price_stats['min'] is not None:
            print(f"  Minimum Price:  €{price_stats['min']:.2f}")
            print(f"  Maximum Price:  €{price_stats['max']:.2f}")
            print(f"  Average Price:  €{price_stats['avg']:.2f}")
            print(f"  Median Price:   €{price_stats['median']:.2f}")
    
        print_subsection("Price Tier Distribution")
        tier_order = ['Free', 'Budget (≤€25)', 'Mid-range (€26-50)', 'Premium (€51-100)', 'Luxury (>€100)', 'Unknown']
        for tier in tier_order:
            if tier in price_stats['tier_distribution']:
                count = price_stats['tier_distribution'][tier]
                percentage = (count / len(data)) * 100
                print(f"  {tier:25s} {count:4d} tours ({percentage:5.2f}%)")
    
        # Duration Analysis
        print_section("⏱️  DURATION ANALYSIS")
        duration_stats = analyze_durations(data)
    
        print_subsection("Duration Range")
        if duration_stats['min_hours'] is not None:
            print(f"  Shortest Tour:  {duration_stats['min_hours']:.1f} hours")
            print(f"  Longest Tour:   {duration_stats['max_hours']:.1f} hours")
            print(f"  Average Length: {duration_stats['avg_hours']:.1f} hours")
    
        print_subsection("Duration Category Distribution")
        category_order = ['Quick (<1 hour)', 'Short (1-2 hours)', 'Half-day (2-4 hours)', 
                          'Full-day (4-8 hours)', 'Multi-day (>8 hours)', 'Unknown']
        for category in category_order:
            if category in duration_stats['category_distribution']:
                count = duration_stats['category_distribution'][category]
                percentage = (count / len(data)) * 100
                print(f"  {category:25s} {count:4d} tours ({percentage:5.2f}%)")
    
        # Language Analysis
        print_section("🌐 LANGUAGE ANALYSIS")
        lang_stats = analyze_languages(data)
    
        print_subsection("Top 15 Languages Offered")
        for i, (lang, count) in enumerate(lang_stats['language_counts'].most_common(15), 1):
            percentage = (count / len(data)) * 100
            print(f"  {i:2d}. {lang:20s} {count:4d} tours ({percentage:5.2f}%)")
    
        print_subsection("Language Variety per Tour")
        for variety, count in lang_stats['tours_by_language_variety'].most_common():
            percentage = (count / len(data)) * 100
            print(f"  {variety:25s} {count:4d} tours ({percentage:5.2f}%)")
    
        # Tour Types Analysis
        print_section("🎯 TOUR TYPE ANALYSIS (Based on Title Keywords)")
        tour_types = analyze_tour_types(data)
        for i, (tour_type, count) in enumerate(tour_types.most_common(), 1):
            percentage = (count / len(data)) * 100
            print(f"  {i:2d}. {tour_type:25s} {count:4d} tours ({percentage:5.2f}%)")
    
        # Meeting Point Analysis
        print_section("📍 MEETING POINT ANALYSIS")
        meeting_stats = analyze_meeting_points(data)
        print(f"  With Maps Link:    {meeting_stats['with_maps_link']:4d} tours ({meeting_stats['percentage_with_maps']:.2f}%)")
        print(f"  Without Maps Link: {meeting_stats['without_maps_link']:4d} tours ({100 - meeting_stats['percentage_with_maps']:.2f}%)")
    
        # Price Distribution by City
        print_section("💰 PRICE TIER BY CITY")
        city_price_data = count_by_city_and_price_tier(data)
    
        # Sort cities by total tours
        sorted_cities = sorted(city_price_data.items(), 
                              key=lambda x: sum(x[1].values()), 
                              reverse=True)
    
        for city, tiers in sorted_cities:
            total = sum(tiers.values())
            print_subsection(f"{city} ({total} total tours)")
            for tier in tier_order:
                if tier in tiers:
                    count = tiers[tier]
                    percentage = (count / total) * 100
                    print(f"    {tier:25s} {count:3d} ({percentage:5.2f}%)")
    
        # Duration Distribution by City
        print_section("⏱️  DURATION BY CITY")
        city_duration = defaultdict(Counter)
    
        for item in data:
            city = item.get('city', 'Unknown')
            duration = parse_duration(item.get('duration', ''))
            category = get_duration_category(duration)
            city_duration[city][category] += 1
    
        for city, _ in sorted_cities:
            categories = city_duration[city]
            total = sum(categories.values())
            print_subsection(f"{city} ({total} total tours)")
            for category in category_order:
                if category in categories:
                    count = categories[category]
                    percentage = (count / total) * 100
                    print(f"    {category:25s} {count:3d} ({percentage:5.2f}%)")
    
        # Summary
        print_section("📈 SUMMARY")
        most_common_tier = price_stats['tier_distribution'].most_common(1)[0] if price_stats['tier_distribution'] else ('N/A', 0)
        most_common_duration = duration_stats['category_distribution'].most_common(1)[0] if duration_stats['category_distribution'] else ('N/A', 0)
        most_common_lang = lang_stats['language_counts'].most_common(1)[0] if lang_stats['language_counts'] else ('N/A', 0)
        most_common_type = tour_types.most_common(1)[0] if tour_types else ('N/A', 0)
    
        avg_price_str = f"€{price_stats['avg']:.2f}" if price_stats['avg'] else 'N/A'
    
        print(f"""
    Dataset Overview:
    • Total Tours:              {len(data):,}
    • Cities Covered:           {len(basic_stats['cities'])}
    • Languages Available:      {len(basic_stats['unique_languages'])}
    
    Top City:                   {city_counts[0][0]} ({city_counts[0][1]} tours)
    Average Price:              {avg_price_str}
    Most Common Price Tier:     {most_common_tier[0]} ({most_common_tier[1]} tours)
    Most Common Duration:       {most_common_duration[0]} ({most_common_duration[1]} tours)
    Most Common Language:       {most_common_lang[0]} ({most_common_lang[1]} tours)
    Most Common Tour Type:      {most_common_type[0]} ({most_common_type[1]} tours)
        """)
    
        print("\n" + "=" * 80)
        print("Analysis complete!")
        print("=" * 80 + "\n")
    
    finally:
        # Restore stdout and close file
        sys.stdout = tee.terminal
        tee.close()
        print(f"Statistics saved to: {output_file}")


if __name__ == "__main__":
    main()
