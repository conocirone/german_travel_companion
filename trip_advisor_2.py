from seleniumbase import SB
from selenium.webdriver.common.by import By
import random
import json
import os

STATE_FILE = "./processed_attractions.json"
DATA_FILE = "./tripadvisor_data.json"
index_spec_type_container = 0

MY_CITIES = {
    'Berlin': "https://www.tripadvisor.com/Attractions-g187323-Activities-oa0-Berlin.html",
    'Cologne': "https://www.tripadvisor.com/Attractions-g187371-Activities-a_allAttractions.true-Cologne_North_Rhine_Westphalia.html",
    'Munich': "https://www.tripadvisor.com/Attractions-g187309-Activities-a_allAttractions.true-Munich_Upper_Bavaria_Bavaria.html",
    'Hamburg': "https://www.tripadvisor.com/Attractions-g187331-Activities-a_allAttractions.true-Hamburg.html",
    'Frankfurt': "https://www.tripadvisor.com/Attractions-g187337-Activities-a_allAttractions.true-Frankfurt_Hesse.html",
    'Stuttgart': "https://www.tripadvisor.com/Attractions-g187291-Activities-a_allAttractions.true-Stuttgart_Baden_Wurttemberg.html",
    'Dusseldorf': "https://www.tripadvisor.com/Attractions-g187373-Activities-a_allAttractions.true-Dusseldorf_North_Rhine_Westphalia.html",
    'Dortmund': "https://www.tripadvisor.com/Attractions-g187372-Activities-a_allAttractions.true-Dortmund_North_Rhine_Westphalia.html",
    'Essen': "https://www.tripadvisor.com/Attractions-g187375-Activities-a_allAttractions.true-Essen_North_Rhine_Westphalia.html",
    'Leipzig': "https://www.tripadvisor.com/Attractions-g187400-Activities-c42-Leipzig_Saxony.html"
}


def load_memory():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_memory(memory):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(memory)), f, indent=2)


def append_data(record):
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    data.append(record)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_spec_type_by_index(sb, current_index):
    return sb.execute_script(f"""
        (function() {{
            var containers = document.querySelectorAll(
                "div.dxkoL.y div.NxKBB.BKifx.y div.alPVI.eNNhq.PgLKC.tnGGX.yzLvM"
            );
            
            var index = {current_index};
            
            // Safety check: if index is out of bounds
            if (index >= containers.length) {{
                return {{ text: null, used_index: index }};
            }}

            var root = containers[index];
            var node = root ? root.querySelector("div.biGQs._P.VImYz.ZNjnF") : null;
            var text = node ? node.innerText.trim() : "";

            // Check if this is a 'Tickets' junk container
            // If so, we look at the NEXT one (index + 1)
            if (text && text.includes('Admission Tickets Available')) {{
                index = index + 1; 
                if (index < containers.length) {{
                    root = containers[index];
                    node = root ? root.querySelector("div.biGQs._P.VImYz.ZNjnF") : null;
                    text = node ? node.innerText.trim() : null;
                }} else {{
                    text = null;
                }}
            }}

            // Return both the text and the final index we used
            return {{ text: text, used_index: index }};
        }})();
    """)

def scrape_operating_hours(sb):
    hours = {}

    container_selector = 'div[data-automation="attractionsPoiHoursForDay"]'
    if not sb.is_element_present(container_selector):
        return hours

    rows = sb.find_elements(f'{container_selector} > div')

    current_day = None
    days = ["Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"]

    for row in rows:
        text = row.text.strip()
        if not text:
            continue

        if text in days:
            current_day = text
            continue

        if current_day and ("AM" in text or "PM" in text):
            hours[current_day] = text

    return hours

def scrape_attraction_image(sb):
    try:
        selector = "picture.NhWcC img"
        
        if sb.is_element_visible(selector):
            return sb.get_attribute(selector, "src")

        fallback_selector = "div.ZGLUM img"
        if sb.is_element_visible(fallback_selector):
            return sb.get_attribute(fallback_selector, "src")
            
    except Exception:
        return None
        
    return None

def scrape_attraction_details(sb):
    selector = 'button.keqHA.f._S.G_.w'

    sb.sleep(1.5)
    buttons = sb.find_elements(selector)

    for i, btn in enumerate(buttons):
        text = btn.text.strip()
        if "Hours" in text or "Open" in text:
            sb.execute_script(f"""
                (function() {{
                    const btns = document.querySelectorAll('{selector}');
                    if (btns.length > {i}) {{
                        btns[{i}].scrollIntoView({{block: 'center'}});
                        btns[{i}].click();
                    }}
                }})();
            """)
            sb.sleep(2)

            if sb.is_element_present('div[data-automation="attractionsPoiHoursForDay"]'):
                return scrape_operating_hours(sb)

    return {}

def run_scraper():
    categories = ["Sights & Landmarks", "Museums", "Nightlife", "Nature & Parks"]
    processed = load_memory()

    with SB(
        uc=True,
        headless=False,
        ad_block=True,
        maximize=True,
        block_images=False
    ) as sb:

        for city_name, city_url in MY_CITIES.items():
            print(f"\nAnalyzing {city_name}")
            sb.open(city_url)
            sb.sleep(random.uniform(3, 5))

            for category in categories:
                print(f"\nCategory: {category}")
                sb.click(f'span:contains("{category}")')
                sb.sleep(random.uniform(3, 5))

                for page_num in range(1, 6):
                    print(f"\nPage {page_num}")
                    
                    index_spec_type_container = 0

                    card_selector = 'div.XfVdV.o.AIbhI'                    

                    attraction_elements = sb.find_elements(card_selector)

                    for i in range(len(attraction_elements)):
                        sb.sleep(random.uniform(1.5, 2.5))
                        current_elements = sb.find_elements(card_selector)

                        if i >= len(current_elements):
                            break

                        element = current_elements[i]
                        name = element.text.strip()
                        

                        if name and name[0].isdigit():
                            name = name.split(" ", 1)[-1]

                        unique_id = f"{city_name}|{category}|{name}"

                        if unique_id in processed:
                            print(f"Skipping already scraped: {name}")
                            index_spec_type_container += 1
                            continue

                        result_data = extract_spec_type_by_index(sb, index_spec_type_container)
                        spec_type = result_data['text']
                        index_spec_type_container = result_data['used_index'] + 1
                        print(f"\nScraping: {name}")
                        print(f"Spec type: {spec_type}")

                        try:
                            element.click()
                            sb.sleep(2)
                            sb.switch_to_newest_window()
                            try:
                                hours = scrape_attraction_details(sb)
                            except Exception as inner_e:
                                print('Could not scrape hours')
                                hours = None
                            
                            try:
                                image_url = scrape_attraction_image(sb)
                            except Exception as inner_e_:
                                image_url = None

                            record = {
                                "name": name,
                                "city": city_name,
                                "attraction_type": category,
                                "spec_type": spec_type,
                                "operating_hours": hours,
                                "image_url": image_url
                            }

                            append_data(record)
                            processed.add(unique_id)
                            save_memory(processed)

                            print("Saved successfully")

                        except Exception as e:
                            print(f"Error scraping {name}: {e}")

                        finally:
                            sb.switch_to_default_window()
                            sb.sleep(1)
                    
                if page_num < 5:
                        next_page_num = page_num + 1
                        print(f"\nAttempting to go to Page {next_page_num}...")

                        next_selector = f'a[aria-label="{next_page_num}"]'
                        
                        fallback_selector = 'a[aria-label="Next page"]'

                        found_next = False
                        
                        if sb.is_element_present(next_selector):
                            sb.scroll_to(next_selector)
                            sb.click(next_selector)
                            found_next = True
                        elif sb.is_element_present(fallback_selector):
                            sb.scroll_to(fallback_selector)
                            sb.click(fallback_selector)
                            found_next = True
                        
                        if found_next:
                            sb.sleep(random.uniform(5, 7))
                        else:
                            print(f"Could not find button for Page {next_page_num}. Stopping category.")
                            break


if __name__ == "__main__":
    run_scraper()
