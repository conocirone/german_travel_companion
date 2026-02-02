import json
import os
from collections import Counter
from typing import List, Dict, Any

def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

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
    counter = Counter()
    for item in data:
        value = item.get(field)
        if value:
            counter[value] += 1
    
    if top_n:
        return counter.most_common(top_n)
    return counter.most_common()

def main():
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path to data file: ../../../data/post_llm_processing/trip_advisor_data_enriched_final.json
    data_path = os.path.join(script_dir, '../../data/post_llm_processing/trip_advisor_data_enriched_final.json')
    # Path to output file: ../../../stats/trip_advisor_stats.md (Project Root Stats)
    output_path = os.path.join(script_dir, '../../stats/trip_advisor_stats.md')
    
    # Create stats directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Loading data from {data_path}...")
    try:
        data = load_data(data_path)
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        # Try fallback to current directory if user moved it manually, just in case
        try:
            data = load_data('trip_advisor_data_enriched_final.json')
            print("Found data in current directory.")
        except FileNotFoundError:
            return

    output = []
    
    def add_line(text=""):
        output.append(str(text))
        
    def add_section(title):
        add_line("=" * 80)
        add_line(f"{title:^80}")
        add_line("=" * 80)
        add_line()

    basic_stats = analyze_basic_stats(data)
    
    # 1. Basic Statistics
    add_section("📊 BASIC STATISTICS")
    add_line(f"Total Attractions: {basic_stats['total_attractions']:,}")
    add_line(f"Total Cities: {len(basic_stats['cities'])}")
    add_line(f"Total Attraction Types: {len(basic_stats['attraction_types'])}")
    add_line(f"Total Spec Types: {len(basic_stats['spec_types'])}")
    add_line()

    # 2. Attractions by City
    add_section("🏙️  ATTRACTIONS BY CITY")
    city_counts = count_by_field(data, 'city')
    for i, (city, count) in enumerate(city_counts, 1):
        percentage = (count / len(data)) * 100
        add_line(f"{i:2d}. {city:<30s} {count:4d} attractions ({percentage:5.2f}%)")
    add_line()

    # 3. Attractions by Type
    add_section("🎭 ATTRACTIONS BY TYPE")
    type_counts = count_by_field(data, 'attraction_type')
    for i, (attr_type, count) in enumerate(type_counts, 1):
        percentage = (count / len(data)) * 100
        add_line(f"{i:2d}. {attr_type:<35s} {count:4d} attractions ({percentage:5.2f}%)")
    add_line()

    # 4. Top 20 Spec Types
    add_section("🎯 TOP 20 SPEC TYPES")
    spec_type_counts = count_by_field(data, 'spec_type', top_n=20)
    for i, (spec_type, count) in enumerate(spec_type_counts, 1):
        percentage = (count / len(data)) * 100
        add_line(f"{i:2d}. {spec_type:<50s} {count:4d} ({percentage:5.2f}%)")
    add_line()

    # 5. Budget Tier Distribution
    add_section("💰 BUDGET TIER DISTRIBUTION")
    budget_counter = Counter(item.get('budget_tier', 'Unknown') for item in data)
    budget_order = ['Free', 'Low', 'Medium', 'High']
    
    for tier_name in budget_order:
        # Check both capitalized and lowercase to be safe
        count = 0
        if tier_name in budget_counter:
            count = budget_counter[tier_name]
        elif tier_name.lower() in budget_counter:
            count = budget_counter[tier_name.lower()]
            
        if count > 0:
            percentage = (count / len(data)) * 100
            add_line(f"{tier_name:<15s} {count:4d} attractions ({percentage:5.2f}%)")
    add_line()

    # 6. Location Setting Distribution
    add_section("📍 LOCATION SETTING DISTRIBUTION")
    loc_counter = Counter(item.get('location_setting', 'Unknown') for item in data)
    loc_order = ['Indoor', 'Outdoor']
    
    for loc_name in loc_order:
        count = 0
        if loc_name in loc_counter:
            count = loc_counter[loc_name]
        elif loc_name.lower() in loc_counter:
            count = loc_counter[loc_name.lower()]
            
        if count > 0:
            percentage = (count / len(data)) * 100
            add_line(f"{loc_name:<15s} {count:4d} attractions ({percentage:5.2f}%)")
    add_line()

    # 7. Operating Hours Statistics
    add_section("🕐 OPERATING HOURS STATISTICS")
    with_hours = sum(1 for item in data if item.get('operating_hours'))
    without_hours = len(data) - with_hours
    if len(data) > 0:
        pct_with = (with_hours / len(data)) * 100
        pct_without = (without_hours / len(data)) * 100
    else:
        pct_with = 0
        pct_without = 0
    
    add_line(f"With Operating Hours:     {with_hours:4d} attractions ({pct_with:.2f}%)")
    add_line(f"Without Operating Hours: {without_hours:4d} attractions ({pct_without:.2f}%)")
    add_line()
    add_line()

    # 8. Summary
    add_section("📈 SUMMARY")
    
    most_common_type = type_counts[0] if type_counts else ("N/A", 0)
    most_common_budget = budget_counter.most_common(1)[0] if budget_counter else ("N/A", 0)
    most_common_setting = loc_counter.most_common(1)[0] if loc_counter else ("N/A", 0)
    
    # helper to capitalize if string
    def safe_cap(s):
        return s.capitalize() if isinstance(s, str) else str(s)

    summary_text = f"""    Dataset Overview:
    • Total Attractions:        {basic_stats['total_attractions']:,}
    • Cities Covered:           {len(basic_stats['cities'])}
    • Attraction Types:         {len(basic_stats['attraction_types'])}
    • Unique Spec Types:        {len(basic_stats['spec_types'])}
    
    Most Common Type:           {most_common_type[0]} ({most_common_type[1]} attractions)
    Most Common Budget Tier:    {safe_cap(most_common_budget[0])} ({most_common_budget[1]} attractions)
    Most Common Setting:        {safe_cap(most_common_setting[0])} ({most_common_setting[1]} attractions)"""
    
    add_line(summary_text)

    # Output
    final_output = "\n".join(output)
    print(final_output)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print(f"\nStats saved to {output_path}")  # Only file name relative to script for brevity

if __name__ == "__main__":
    main()
