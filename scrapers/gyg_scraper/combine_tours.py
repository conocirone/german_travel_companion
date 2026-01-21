#!/usr/bin/env python3
"""
Script to combine all city tour JSON files into a single all_cities_tours.json file.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def load_json(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: List[Dict[str, Any]], filepath: str):
    """Save JSON data to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def extract_city_from_filename(filename: str) -> str:
    """Extract city name from filename (e.g., 'berlin_tours.json' -> 'Berlin')."""
    city = filename.replace('_tours.json', '')
    return city.capitalize()


def combine_all_tours(tours_dir: str, output_file: str) -> Dict[str, int]:
    """
    Combine all city tour JSON files into a single file.
    
    Args:
        tours_dir: Directory containing city tour JSON files
        output_file: Path to the output combined JSON file
        
    Returns:
        Dictionary with statistics about the combination process
    """
    all_tours = []
    stats = {
        'cities_processed': 0,
        'total_tours': 0,
        'tours_per_city': {}
    }
    
    # Get all JSON files in the tours directory
    tours_path = Path(tours_dir)
    json_files = sorted(tours_path.glob('*_tours.json'))
    
    for json_file in json_files:
        # Skip the all_cities_tours.json file if it exists
        if json_file.name == 'all_cities_tours.json':
            continue
            
        city_name = extract_city_from_filename(json_file.name)
        
        try:
            tours = load_json(str(json_file))
            
            # Add city field to each tour
            for tour in tours:
                tour['city'] = city_name
            
            all_tours.extend(tours)
            stats['cities_processed'] += 1
            stats['tours_per_city'][city_name] = len(tours)
            stats['total_tours'] += len(tours)
            
            print(f"✓ Loaded {len(tours):3d} tours from {city_name}")
            
        except json.JSONDecodeError as e:
            print(f"✗ Error loading {json_file.name}: {e}")
        except Exception as e:
            print(f"✗ Unexpected error loading {json_file.name}: {e}")
    
    # Save combined data
    save_json(all_tours, output_file)
    print(f"\n{'=' * 60}")
    print(f"Combined {stats['total_tours']} tours from {stats['cities_processed']} cities")
    print(f"Saved to: {output_file}")
    print('=' * 60)
    
    return stats


def main():
    # Define paths
    script_dir = Path(__file__).parent
    tours_dir = script_dir / 'tours_data'
    output_file = tours_dir / 'all_cities_tours.json'
    
    print("=" * 60)
    print("GetYourGuide Tours Combiner")
    print("=" * 60)
    print(f"\nSource directory: {tours_dir}")
    print(f"Output file: {output_file}\n")
    
    if not tours_dir.exists():
        print(f"Error: Tours directory not found: {tours_dir}")
        return
    
    stats = combine_all_tours(str(tours_dir), str(output_file))
    
    # Print summary
    print("\n📊 Summary by City:")
    print("-" * 40)
    for city, count in sorted(stats['tours_per_city'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {city:15s}: {count:3d} tours")


if __name__ == "__main__":
    main()
