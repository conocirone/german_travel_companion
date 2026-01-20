import ollama
import ddgs
import json
import time

INPUT_FILE = "tripadvisor_data.json"
OUTPUT_FILE = "enriched_tripadvisor_data.json"
client = ollama.Client()
model = "llama3.1:latest"

def search_web(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with ddgs.DDGS() as search:
                results = [r['body'] for r in search.text(query, max_results=5, safesearch="off", region="de-de")]
                return " ".join(results)
        except Exception as e:
            print(f"Error searching web (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2) 
    return ""

def get_llm_fields(name, city, search_context):
    prompt = f"""
    Attraction: {name} in {city}
    Context: {search_context}
    
    Task: Classify this attraction based on the name and context.
    
    1. location_setting: 'indoor' or 'outdoor'
       - Museums, theaters, churches (interior visits) = indoor
       - Parks, squares, streets, monuments, outdoor markets = outdoor
    
    2. budget_tier: Based on the BASE ENTRY FEE to access the attraction ITSELF.
       - 'free': Public spaces (squares, streets, parks, neighborhoods, markets), monuments you can view from outside, churches with free entry, free museums
       - 'low': 1€-10€ entry fee
       - 'medium': 11€-20€ entry fee  
       - 'high': >20€ entry fee
       
    IMPORTANT: 
    - Ignore prices for guided tours, experiences, or activities - only consider the base entry fee.
    - Public squares (like Alexanderplatz, Potsdamer Platz), streets, parks, and neighborhoods are ALWAYS 'free'.
    - If unsure and it's a public outdoor space, default to 'free'.

    Return ONLY a valid JSON object. No intro text.
    Example: {{"location_setting": "indoor", "budget_tier": "medium"}}
    """
    response = client.generate(model=model, prompt=prompt, format="json")
    return response.response

with open(INPUT_FILE, 'r') as f:
    data = json.load(f)

print(f'Starting to enrich {len(data)} attractions...')

for i, item in enumerate(data):
    name = item.get('name')
    city = item.get('city')
    if not name or not city:
        print(f'Skipping item {i+1}/{len(data)}: Missing name or city')
        continue
    
    print(f'Processing item {i+1}/{len(data)}: {name} in {city}')
    search_context = search_web(f'{name} {city} ticket price official site')
    print(f'Search context: {search_context}')

    try:
        llm_fields = get_llm_fields(name, city, search_context)
        parsed_fields = json.loads(llm_fields)
        item.update(parsed_fields)
    except Exception as e:
        print(f'Error getting LLM fields for {name} in {city}: {e}')
        continue
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f'Enriched item {i+1}/{len(data)}: {name} in {city}')

print(f'Done! Enriched data saved to {OUTPUT_FILE}')