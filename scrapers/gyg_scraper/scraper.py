import time
import random
import json
import os
from playwright.sync_api import sync_playwright
from fake_useragent import UserAgent

# Dictionary of German cities with their GetYourGuide URLs
MY_CITIES = {
    'Berlin': 'https://www.getyourguide.com/berlin-l17/',
    'Cologne': 'https://www.getyourguide.com/cologne-l19/',
    'Munich': 'https://www.getyourguide.com/munich-l26/',
    'Hamburg': 'https://www.getyourguide.com/hamburg-l23/',
    'Frankfurt': 'https://www.getyourguide.com/frankfurt-l21/',
    'Stuttgart': 'https://www.getyourguide.com/stuttgart-l27/',
    'Dusseldorf': 'https://www.getyourguide.com/dusseldorf-l125/',
    'Dortmund': 'https://www.getyourguide.com/dortmund-l136/',
    'Essen': 'https://www.getyourguide.com/essen-l145/',
    'Leipzig': 'https://www.getyourguide.com/leipzig-l25/',
}

def scrape_getyourguide(city_name, city_url):
    ua = UserAgent()
    user_agent = ua.random
    
    data = []

    with sync_playwright() as p:
        # Launch browser (headless=True for Docker, False for debugging locally)
        browser = p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled', # Helps avoid simple bot detection
            '--start-maximized'
        ])
        
        # Create a context with a real user agent and viewport
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()

        # Stealth: Remove the 'navigator.webdriver' property
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print(f"🌍 [{city_name}] Navigating to {city_url}...")
        page.goto(city_url, wait_until="domcontentloaded", timeout=60000)
        
        # Handle Cookie Consent (Common blocker)
        try:
            # Adjust selector based on current site structure if needed
            page.wait_for_selector('button[id*="cookie"], button[class*="cookie"]', timeout=5000)
            page.click('button[id*="cookie"], button[class*="cookie"]')
            print("🍪 Cookies accepted.")
        except:
            print("🍪 No cookie banner found or already handled.")

        # --- PAGINATION LOOP ---
        max_pages = 2  # Limit to avoid infinite loops during testing
        while max_pages > 0:
            try:
                # Locator for the "Show more" button based on your snippet
                show_more_btn = page.locator(".show-more button")
                
                if show_more_btn.is_visible():
                    print("🖱️ 'Show more' button found. Clicking...")
                    
                    # Scroll to button to simulate human behavior
                    show_more_btn.scroll_into_view_if_needed()
                    time.sleep(random.uniform(1, 3)) # Human-like pause
                    
                    # Click and wait for network activity to settle
                    show_more_btn.click()
                    page.wait_for_load_state("networkidle") 
                    
                    # Small pause to let DOM update
                    time.sleep(random.uniform(2, 4))
                else:
                    print("✅ No more 'Show more' buttons visible.")
                    break
                max_pages -= 1
            except Exception as e:
                print(f"⚠️ Pagination ended or error: {e}")
                break

        # --- EXTRACTION ---
        print("🔍 Extracting tour data...")
        
        # Select all tour cards (Subject to class changes, inspecting common structure)
        # Note: Classes like 'vertical-activity-card__content' are common in GYG
        cards = page.locator("article").all()
        
        print(f"📊 Found {len(cards)} activities.")

        for card in cards:
            try:
                # Extract basic info (Adapting to generic structure due to dynamic classes)
                title = card.locator("h3").first.inner_text()
                
                # Try to get price from activity-price__text-price class
                price = "N/A"
                price_elem = card.locator(".activity-price__text-price")
                if price_elem.count() > 0:
                    price = price_elem.first.inner_text()
                
                # Link
                link = "N/A"
                if card.locator("a").count() > 0:
                    link = card.locator("a").first.get_attribute("href")
                    if link and link.startswith("/"):
                        link = "https://www.getyourguide.com" + link

                # Navigate to detail page to extract additional info
                duration = "N/A"
                languages = "N/A"
                meeting_point = "N/A"
                meeting_point_maps_link = "N/A"
                
                if link != "N/A":
                    try:
                        # Open detail page in a new tab
                        detail_page = context.new_page()
                        detail_page.add_init_script("""
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined
                            });
                        """)
                        
                        print(f"🔗 Navigating to detail page for: {title[:50]}...")
                        detail_page.goto(link, wait_until="domcontentloaded", timeout=60000)
                        time.sleep(random.uniform(2, 4))  # Wait for page to fully load
                        
                        # Extract Duration from key-detail-item-block with id icon-label-duration
                        try:
                            duration_block = detail_page.locator("#icon-label-duration")
                            if duration_block.count() > 0:
                                duration_text = duration_block.locator("dt .text-atom--body-strong").first.inner_text()
                                duration = duration_text.replace("Duration", "").strip()
                            else:
                                # Fallback: try div[data-ref="duration"]
                                alt_duration_block = detail_page.locator('div[data-ref="duration"]')
                                if alt_duration_block.count() > 0:
                                    # Look for span containing "Duration" text
                                    duration_span = alt_duration_block.locator("dt span").all()
                                    for span in duration_span:
                                        span_text = span.inner_text()
                                        if "Duration" in span_text:
                                            duration = span_text.replace("Duration", "").strip()
                                            break
                        except Exception as e:
                            print(f"⚠️ Could not extract duration: {e}")
                        
                        # Extract Languages from key-detail-item-block with id icon-label-tourGuides
                        try:
                            guides_block = detail_page.locator("#icon-label-tourGuides")
                            if guides_block.count() > 0:
                                languages = guides_block.locator("dd .text-atom--caption").first.inner_text()
                        except Exception as e:
                            print(f"⚠️ Could not extract languages: {e}")
                        
                        # Try alternative language sources (audio guide)
                        if languages == "N/A":
                            try:
                                audio_block = detail_page.locator("#icon-label-audioGuides")
                                if audio_block.count() > 0:
                                    languages = audio_block.locator("dd .text-atom--caption").first.inner_text()
                            except:
                                pass
                        
                        # Extract Meeting Point - handles two HTML structures:
                        # 1. Normal case: meeting-points-block with text description and maps link
                        # 2. Alternative case: activity-meeting-point section with only maps link
                        meeting_point_maps_link = "N/A"
                        try:
                            # Try normal case first: meeting-points-block
                            meeting_block = detail_page.locator(".meeting-points-block, #meeting-point-links")
                            if meeting_block.count() > 0:
                                meeting_text_elem = meeting_block.locator(".text-atom--body").first
                                if meeting_text_elem.count() > 0:
                                    meeting_point = meeting_text_elem.inner_text()
                                
                                # Extract Google Maps link if available
                                maps_link_elem = meeting_block.locator("a[href*='maps.google.com']")
                                if maps_link_elem.count() > 0:
                                    meeting_point_maps_link = maps_link_elem.first.get_attribute("href")
                            
                            # Fallback: alternative case with activity-meeting-point section
                            if meeting_point == "N/A" and meeting_point_maps_link == "N/A":
                                alt_meeting_block = detail_page.locator("section.activity-meeting-point, [data-test-id='activity-meeting-point']")
                                if alt_meeting_block.count() > 0:
                                    # Try to get any text content
                                    text_elem = alt_meeting_block.locator(".text-atom--body")
                                    if text_elem.count() > 0:
                                        meeting_point = text_elem.first.inner_text()
                                    
                                    # Extract Google Maps link from this alternative structure
                                    maps_link_elem = alt_meeting_block.locator("a[href*='maps.google.com']")
                                    if maps_link_elem.count() > 0:
                                        meeting_point_maps_link = maps_link_elem.first.get_attribute("href")
                        except Exception as e:
                            print(f"⚠️ Could not extract meeting point: {e}")
                        
                        detail_page.close()
                        
                    except Exception as e:
                        print(f"⚠️ Error navigating to detail page: {e}")

                data.append({
                    "title": title,
                    "price": price,
                    "link": link,
                    "duration": duration,
                    "languages": languages,
                    "meeting_point": meeting_point,
                    "meeting_point_maps_link": meeting_point_maps_link
                })
                print(f"✔️ Extracted: {title} | Duration: {duration} | Languages: {languages}, Price: {price}, Link: {link}, Meeting Point: {meeting_point[:30]}...")
            except Exception as e:
                print(f"⚠️ Error extracting card: {e}")
                continue

        browser.close()

    return data

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = 'tours_data'
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = {}
    
    for city_name, city_url in MY_CITIES.items():
        print(f"\n{'='*60}")
        print(f"🏙️  Starting scrape for {city_name}")
        print(f"{'='*60}")
        
        try:
            results = scrape_getyourguide(city_name, city_url)
            all_results[city_name] = results
            
            # Save individual city file
            city_filename = f"{output_dir}/{city_name.lower()}_tours.json"
            with open(city_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            
            print(f"🎉 [{city_name}] Done! Scraped {len(results)} items. Saved to {city_filename}")
            
            # Add delay between cities to avoid rate limiting
            time.sleep(random.uniform(5, 10))
            
        except Exception as e:
            print(f"❌ [{city_name}] Error scraping: {e}")
            continue
    
    # Save combined results
    with open(f'{output_dir}/all_cities_tours.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    total_items = sum(len(v) for v in all_results.values())
    print(f"\n{'='*60}")
    print(f"🎊 All done! Scraped {total_items} total items from {len(all_results)} cities.")
    print(f"📁 Results saved to {output_dir}/")
    print(f"{'='*60}")