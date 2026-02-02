import json
import os
import re
from collections import Counter
from typing import List, Dict, Any

def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_price(price_str: str) -> float:
    """Extract numeric value from price string."""
    if not price_str:
        return 0.0
    # Remove currency symbols and convert to float
    clean_price = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(clean_price)
    except ValueError:
        return 0.0

def analyze_prices(data: List[Dict]) -> Dict[str, float]:
    """Calculate price statistics."""
    prices = []
    for item in data:
        p = parse_price(item.get('price', ''))
        if p > 0:
            prices.append(p)
    
    if not prices:
        return {'min': 0, 'max': 0, 'avg': 0}
        
    return {
        'min': min(prices),
        'max': max(prices),
        'avg': sum(prices) / len(prices)
    }

def count_languages(data: List[Dict]) -> Counter:
    """Count occurrences of each language."""
    lang_counter = Counter()
    for item in data:
        langs = item.get('languages', '')
        if langs:
            # specific fix for "Spanish, English..."
            for lang in langs.split(','):
                lang_counter[lang.strip()] += 1
    return lang_counter

def main():
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path to data file: ../../data/post_llm_processing/all_cities_tours.json
    data_path = os.path.join(script_dir, '../../data/post_llm_processing/all_cities_tours.json')
    # Path to output file: ../../stats/gyg_stats.md
    output_path = os.path.join(script_dir, '../../stats/gyg_stats.md')
    
    # Create stats directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Loading data from {data_path}...")
    try:
        data = load_data(data_path)
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return

    output = []
    
    def add_line(text=""):
        output.append(str(text))
        
    def add_section(title):
        add_line("=" * 80)
        add_line(f"{title:^80}")
        add_line("=" * 80)
        add_line()

    # 1. Basic Statistics
    cities = set(item.get('city') for item in data if item.get('city'))
    lang_counts = count_languages(data)
    price_stats = analyze_prices(data)
    
    add_section("📊 BASIC STATISTICS")
    add_line(f"Total Tours:      {len(data):,}")
    add_line(f"Total Cities:     {len(cities)}")
    add_line(f"Total Languages:  {len(lang_counts)}")
    add_line(f"Price Range:      €{price_stats['min']:.2f} - €{price_stats['max']:.2f} (Avg: €{price_stats['avg']:.2f})")
    add_line()

    # 2. Tours by City
    add_section("🏙️  TOURS BY CITY")
    city_counter = Counter(item.get('city') for item in data if item.get('city'))
    for i, (city, count) in enumerate(city_counter.most_common(), 1):
        percentage = (count / len(data)) * 100
        add_line(f"{i:2d}. {city:<30s} {count:4d} tours ({percentage:5.2f}%)")
    add_line()

    # 3. Top 10 Duration Types
    add_section("⏱️  TOP 10 DURATION TYPES")
    duration_counter = Counter(item.get('duration') for item in data if item.get('duration'))
    for i, (dur, count) in enumerate(duration_counter.most_common(10), 1):
        percentage = (count / len(data)) * 100
        add_line(f"{i:2d}. {dur:<30s} {count:4d} tours ({percentage:5.2f}%)")
    add_line()

    # 4. Top 10 Languages
    add_section("🗣️  TOP 10 LANGUAGES")
    for i, (lang, count) in enumerate(lang_counts.most_common(10), 1):
        percentage = (count / len(data)) * 100 # Note: sum of % > 100% since multiple langs per tour
        add_line(f"{i:2d}. {lang:<30s} {count:4d} tours ({percentage:5.2f}%)")
    add_line()

    # 5. Budget Tier Distribution
    add_section("💰 BUDGET TIER DISTRIBUTION")
    budget_counter = Counter(item.get('budget_tier', 'Unknown') for item in data)
    budget_order = ['Free', 'Low', 'Medium', 'High']
    
    for tier_name in budget_order:
        count = 0
        if tier_name in budget_counter:
            count = budget_counter[tier_name]
        elif tier_name.lower() in budget_counter:
            count = budget_counter[tier_name.lower()]
            
        if count > 0:
            percentage = (count / len(data)) * 100
            add_line(f"{tier_name:<15s} {count:4d} tours ({percentage:5.2f}%)")
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
            add_line(f"{loc_name:<15s} {count:4d} tours ({percentage:5.2f}%)")
    add_line()

    # 7. Summary
    add_section("📈 SUMMARY")
    
    most_common_city = city_counter.most_common(1)[0] if city_counter else ("N/A", 0)
    most_common_lang = lang_counts.most_common(1)[0] if lang_counts else ("N/A", 0)
    
    summary_text = f"""    Dataset Overview:
    • Total Tours:              {len(data):,}
    • Cities Covered:           {len(cities)}
    • Most Expensive:           €{price_stats['max']:.2f}
    • Average Price:            €{price_stats['avg']:.2f}
    
    Most Common City:           {most_common_city[0]} ({most_common_city[1]} tours)
    Most Common Language:       {most_common_lang[0]} ({most_common_lang[1]} tours)"""
    
    add_line(summary_text)

    # Output
    final_output = "\n".join(output)
    print(final_output)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print(f"\nStats saved to {output_path}")

if __name__ == "__main__":
    main()
