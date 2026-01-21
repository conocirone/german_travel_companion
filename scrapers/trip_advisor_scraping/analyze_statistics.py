#!/usr/bin/env python3
"""
Script to analyze TripAdvisor attraction data and extract comprehensive statistics.
"""

import json
from collections import Counter, defaultdict
from typing import Dict, List, Any


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


def analyze_basic_stats(data: List[Dict]) -> Dict:
    """Extract basic statistics."""
    stats = {
        'total_attractions': len(data),
        'cities': set(),
        'attraction_types': set(),
        'spec_types': set(),
    }
    
    for item in data:
        if 'city' in item and item['city']:
            stats['cities'].add(item['city'])
        if 'attraction_type' in item and item['attraction_type']:
            stats['attraction_types'].add(item['attraction_type'])
        if 'spec_type' in item and item['spec_type']:
            stats['spec_types'].add(item['spec_type'])
    
    return stats


def count_by_field(data: List[Dict], field: str, top_n: int = None) -> List[tuple]:
    """Count attractions by a specific field."""
    counter = Counter()
    
    for item in data:
        value = item.get(field)
        if value:
            counter[value] += 1
    
    if top_n:
        return counter.most_common(top_n)
    return counter.most_common()


def count_by_city_and_type(data: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Count attractions by city and attraction type."""
    city_type_count = defaultdict(lambda: defaultdict(int))
    
    for item in data:
        city = item.get('city', 'Unknown')
        attraction_type = item.get('attraction_type', 'Unknown')
        city_type_count[city][attraction_type] += 1
    
    return dict(city_type_count)


def count_budget_tiers(data: List[Dict]) -> Counter:
    """Count attractions by budget tier."""
    return Counter(item.get('budget_tier', 'Unknown') for item in data)


def count_location_settings(data: List[Dict]) -> Counter:
    """Count attractions by location setting."""
    return Counter(item.get('location_setting', 'Unknown') for item in data)


def count_with_operating_hours(data: List[Dict]) -> Dict:
    """Count attractions with/without operating hours."""
    with_hours = sum(1 for item in data if item.get('operating_hours'))
    without_hours = len(data) - with_hours
    
    return {
        'with_operating_hours': with_hours,
        'without_operating_hours': without_hours,
        'percentage_with_hours': (with_hours / len(data) * 100) if data else 0
    }


def get_top_spec_types_per_city(data: List[Dict], top_n: int = 5) -> Dict[str, List[tuple]]:
    """Get top spec_types for each city."""
    city_spec_types = defaultdict(Counter)
    
    for item in data:
        city = item.get('city', 'Unknown')
        spec_type = item.get('spec_type', 'Unknown')
        city_spec_types[city][spec_type] += 1
    
    return {city: counter.most_common(top_n) for city, counter in city_spec_types.items()}


def main():
    # Load data
    filepath = 'trip_advisor_data_enriched_final.json'
    print(f"Loading data from {filepath}...")
    data = load_data(filepath)
    
    # Basic Statistics
    print_section("📊 BASIC STATISTICS")
    basic_stats = analyze_basic_stats(data)
    print(f"\nTotal Attractions: {basic_stats['total_attractions']:,}")
    print(f"Total Cities: {len(basic_stats['cities'])}")
    print(f"Total Attraction Types: {len(basic_stats['attraction_types'])}")
    print(f"Total Spec Types: {len(basic_stats['spec_types'])}")
    
    # Attractions by City
    print_section("🏙️  ATTRACTIONS BY CITY")
    city_counts = count_by_field(data, 'city')
    for i, (city, count) in enumerate(city_counts, 1):
        percentage = (count / len(data)) * 100
        print(f"{i:2d}. {city:30s} {count:4d} attractions ({percentage:5.2f}%)")
    
    # Attractions by Type
    print_section("🎭 ATTRACTIONS BY TYPE")
    type_counts = count_by_field(data, 'attraction_type')
    for i, (attr_type, count) in enumerate(type_counts, 1):
        percentage = (count / len(data)) * 100
        print(f"{i:2d}. {attr_type:35s} {count:4d} attractions ({percentage:5.2f}%)")
    
    # Top Spec Types
    print_section("🎯 TOP 20 SPEC TYPES")
    spec_type_counts = count_by_field(data, 'spec_type', top_n=20)
    for i, (spec_type, count) in enumerate(spec_type_counts, 1):
        percentage = (count / len(data)) * 100
        print(f"{i:2d}. {spec_type:50s} {count:4d} ({percentage:5.2f}%)")
    
    # Budget Tier Distribution
    print_section("💰 BUDGET TIER DISTRIBUTION")
    budget_counts = count_budget_tiers(data)
    budget_order = ['free', 'low', 'medium', 'high', 'Unknown']
    for tier in budget_order:
        if tier in budget_counts:
            count = budget_counts[tier]
            percentage = (count / len(data)) * 100
            print(f"{tier.capitalize():15s} {count:4d} attractions ({percentage:5.2f}%)")
    
    # Location Setting Distribution
    print_section("📍 LOCATION SETTING DISTRIBUTION")
    location_counts = count_location_settings(data)
    for setting, count in location_counts.most_common():
        percentage = (count / len(data)) * 100
        print(f"{setting.capitalize():15s} {count:4d} attractions ({percentage:5.2f}%)")
    
    # Operating Hours Statistics
    print_section("🕐 OPERATING HOURS STATISTICS")
    hours_stats = count_with_operating_hours(data)
    print(f"With Operating Hours:    {hours_stats['with_operating_hours']:4d} attractions ({hours_stats['percentage_with_hours']:.2f}%)")
    print(f"Without Operating Hours: {hours_stats['without_operating_hours']:4d} attractions ({100 - hours_stats['percentage_with_hours']:.2f}%)")
    
    # Attractions by City and Type
    print_section("🏙️ 🎭 ATTRACTIONS BY CITY AND TYPE")
    city_type_data = count_by_city_and_type(data)
    
    # Sort cities by total attractions
    sorted_cities = sorted(city_type_data.items(), 
                          key=lambda x: sum(x[1].values()), 
                          reverse=True)
    
    for city, types in sorted_cities[:10]:  # Show top 10 cities
        total = sum(types.values())
        print_subsection(f"{city} ({total} total attractions)")
        
        # Sort types by count
        sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)
        for attr_type, count in sorted_types:
            percentage = (count / total) * 100
            print(f"  • {attr_type:35s} {count:3d} ({percentage:5.2f}%)")
    
    # Top Spec Types per City
    print_section("🎯 TOP 5 SPEC TYPES PER CITY (Top 10 Cities)")
    top_spec_types = get_top_spec_types_per_city(data, top_n=5)
    
    # Get top 10 cities by attraction count
    top_cities = [city for city, _ in count_by_field(data, 'city', top_n=10)]
    
    for city in top_cities:
        if city in top_spec_types:
            print_subsection(city)
            for i, (spec_type, count) in enumerate(top_spec_types[city], 1):
                print(f"  {i}. {spec_type:50s} {count:3d}")
    
    # Budget Distribution by City
    print_section("💰 BUDGET TIER BY CITY (Top 10 Cities)")
    city_budget = defaultdict(Counter)
    
    for item in data:
        city = item.get('city', 'Unknown')
        budget = item.get('budget_tier', 'Unknown')
        city_budget[city][budget] += 1
    
    for city in top_cities:
        if city in city_budget:
            print_subsection(city)
            for tier in budget_order:
                if tier in city_budget[city]:
                    count = city_budget[city][tier]
                    total_city = sum(city_budget[city].values())
                    percentage = (count / total_city) * 100
                    print(f"  {tier.capitalize():15s} {count:3d} ({percentage:5.2f}%)")
    
    # Summary
    print_section("📈 SUMMARY")
    print(f"""
    Dataset Overview:
    • Total Attractions:        {len(data):,}
    • Cities Covered:           {len(basic_stats['cities'])}
    • Attraction Types:         {len(basic_stats['attraction_types'])}
    • Unique Spec Types:        {len(basic_stats['spec_types'])}
    
    Top City:                   {city_counts[0][0]} ({city_counts[0][1]} attractions)
    Most Common Type:           {type_counts[0][0]} ({type_counts[0][1]} attractions)
    Most Common Budget Tier:    {budget_counts.most_common(1)[0][0].capitalize()} ({budget_counts.most_common(1)[0][1]} attractions)
    Most Common Setting:        {location_counts.most_common(1)[0][0].capitalize()} ({location_counts.most_common(1)[0][1]} attractions)
    """)
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
