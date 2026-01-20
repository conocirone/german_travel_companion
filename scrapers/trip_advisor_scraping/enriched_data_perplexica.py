import json
import requests
import time
import os
import ollama

# --- CONFIGURATION FROM YOUR PROVIDERS DATA ---
INPUT_FILE = 'tripadvisor_data.json'
OUTPUT_FILE = 'enriched_tripadvisor_data_local.json'
API_URL = "http://localhost:3000/api/search"
client = ollama.Client()
model = "llama3.1:latest"
# IDs from your JSON output
OLLAMA_PROVIDER_ID = "5f4fce48-c818-4b41-9a6e-ee3e8d1c979e"
TRANSFORMERS_PROVIDER_ID = "320d9526-5a69-4e79-a2ee-23497799d2f8"

# Models (using llama3.1 for chat and a fast transformer for embedding)
CHAT_MODEL_KEY = "llama3.1:latest"
EMBED_MODEL_KEY = "Xenova/all-MiniLM-L6-v2" 

def get_perplexica_enrichment(name, city):
    payload = {
        "query": f"Is '{name}' in {city} indoor or outdoor? What is the base entry ticket price (free, <10e, 10-20e, >20e)?",
        "focusMode": "webSearch",
        "optimizationMode": "balanced",
        "history": [], 
        "sources": ["web"],
        "chatModel": {
            "providerId": OLLAMA_PROVIDER_ID,
            "key": CHAT_MODEL_KEY
        },
        "embeddingModel": {
            "providerId": TRANSFORMERS_PROVIDER_ID,
            "key": EMBED_MODEL_KEY
        }
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('message', '')
        else:
            print(f"  Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"  Request failed: {e}")
        return None

def parse_to_json(text, name, city):
    """Uses Ollama directly to structure the search result into JSON."""
    print(f'Context received: {text}')
    prompt = f"""
    Attraction: {name} in {city}
    Context: {text}
    
    Task: Extract the location_setting and budget_tier.
    
    RULES:
    1. If the context says the attraction is free with 'advance registration' or 'online booking', the budget_tier is 'free'.
    2. Ignore ALL mentions of 'guided tours', 'audio guides', or 'special events' prices. Only look for the cost to enter the gate/door.
    3. If the attraction is a public landmark, square, or monument (like the Reichstag dome or Brandenburg Gate), it is 'free' unless a mandatory ticket is mentioned.
    
    Classifications:
    - location_setting: 'indoor' (museums, buildings) or 'outdoor' (parks, squares, monuments).
    - budget_tier: 
        - 'free': 0€
        - 'low': 1€-10€ 
        - 'medium': 11€-20€ 
        - 'high': >20€

    Return ONLY JSON: {{"location_setting": "...", "budget_tier": "..."}}
    """

    try:
        response = client.generate(model=model, prompt=prompt, format="json")
        return response.response
    except:
        return {"location_setting": "unknown", "budget_tier": "unknown"}

# --- MAIN ENGINE ---
with open(INPUT_FILE, 'r') as f:
    attractions = json.load(f)

enriched_data = []
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r') as f:
        enriched_data = json.load(f)
processed = {item['name'] for item in enriched_data}

print(f"Processing {len(attractions)} items on M4 Pro...")

for i, item in enumerate(attractions):
    if item['name'] in processed:
        continue

    print(f"[{i+1}/{len(attractions)}] {item['name']}...")
    
    # 1. Search & Summarize
    raw_info = get_perplexica_enrichment(item['name'], item['city'])
    
    if raw_info:
        # 2. Convert to JSON fields
        fields_str = parse_to_json(raw_info, item['name'], item['city'])
        try:
            fields = json.loads(fields_str)
            item.update(fields)
            enriched_data.append(item)
            print(f'Enriched data: {enriched_data}')
        except json.JSONDecodeError as e:
            print(f"  Failed to parse JSON response: {e}")
            print(f"  Raw response: {fields_str}")
            # Fallback to unknown values
            item.update({"location_setting": "unknown", "budget_tier": "unknown"})
            enriched_data.append(item)

        # Save every 5 items
        if len(enriched_data) % 5 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(enriched_data, f, indent=4)
    

with open(OUTPUT_FILE, 'w') as f:
    json.dump(enriched_data, f, indent=4)

print("Finished! Data saved to enriched_tripadvisor_data_local.json")