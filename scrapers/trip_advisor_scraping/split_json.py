import json
import math

def split_json(input_file, num_parts=10):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Calculate the size of each chunk
    chunk_size = math.ceil(len(data) / num_parts)
    
    for i in range(num_parts):
        start = i * chunk_size
        end = start + chunk_size
        chunk = data[start:end]
        
        output_name = f'tripadvisor_part_{i+1}.json'
        with open(output_name, 'w') as f:
            json.dump(chunk, f, indent=4)
        print(f"Created {output_name} with {len(chunk)} items.")

split_json('tripadvisor_data.json')