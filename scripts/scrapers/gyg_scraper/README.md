# Scraper Progress Report: From V1 to V2

This document outlines the development journey of the GetYourGuide scraper, detailing the initial testing phase in Version 1, the robust improvements implemented in Version 2, and the technical architecture used to ensure reliability.

## 1. Version 1: The "Proof of Concept"

**Goal:**
The first version was designed as a **single-city test (Berlin)**. The objective was to validate the core scraping logic—navigating pagination, identifying tour cards, and extracting basic details—before scaling up to a larger dataset. By focusing on just one city, we could quickly identify structural inconsistencies in the website's HTML without waiting for long scraping cycles.

**Problems Identified in V1:**
During this testing phase, we discovered critical gaps in the data extraction logic:

* **❌ Missing Languages ("N/A"):** Many tours returned "N/A" for languages. We realized the scraper only looked for a "Live Tour Guide." It failed to capture language data for self-guided activities (e.g., Hop-on Hop-off buses, museums) that rely on **Audio Guides**.
* **❌ Vague Meeting Points:** Some activities had no descriptive text for the meeting point (e.g., just a button saying "Open in Google Maps"), resulting in empty or useless data.
* **❌ Limited Scope:** The script was hardcoded for a single URL, making it impossible to scrape multiple cities without manual code changes.

---

## 2. Version 2: Multi-City Scale & Data Fixes

Building on the findings from V1, Version 2 addresses the data gaps and introduces scalability.

### Key Improvements

**1. Fixing the "N/A" Languages Issue**
To solve the missing language data, we implemented a fallback logic:

* **Primary Check:** The scraper first looks for the standard `#icon-label-tourGuides` (Live Guide).
* **Secondary Check:** If that is missing, it now explicitly checks for `#icon-label-audioGuides` (Audio Guide).
* **Result:** Self-guided tours now correctly list their available languages instead of returning "N/A".

**2. Enhanced Meeting Point Data**
To address vague meeting locations, we added a new data field: `meeting_point_maps_link`.

* **Logic:** The scraper now extracts the specific Google Maps URL from the meeting point section.
* **Benefit:** Even if the text description is missing or generic (e.g., "Open in Google Maps"), the JSON now includes the precise map link, ensuring the user always knows where to go. We also improved the extraction to handle different HTML layouts (`.meeting-points-block` vs `section.activity-meeting-point`).

**3. Scalability: Multi-City Support**
The hardcoding limitations of V1 were removed.

* **New Architecture:** The script now iterates through a dictionary of cities (`MY_CITIES`), automatically scraping **Berlin, Cologne, Munich, Hamburg, Frankfurt, Stuttgart, Dusseldorf, Dortmund, Essen, and Leipzig**.
* **Output:** It generates individual JSON files for each city (e.g., `berlin_tours.json`) plus a combined master file (`all_cities_tours.json`).

### Summary of Data Structure Changes

| Feature | Version 1 (Test Phase) | Version 2 (Production Ready) |
| --- | --- | --- |
| **Scope** | Single City (Berlin) to test behavior. | Multi-City Loop (10+ German cities). |
| **Languages** | Often "N/A" (Live Guide check only). | **Complete** (Checks Live Guide + Audio Guide). |
| **Meeting Point** | Text description only (often empty). | Text + **Google Maps Link** (`meeting_point_maps_link`). |
| **Output** | Single JSON file. | Individual files + Master merged file. |

---

## 3. Technical Architecture & Stealth Measures

Both versions are built on **Python** using **Playwright** and **fake-useragent** to ensure reliable data extraction while avoiding common anti-bot mechanisms.

* **Playwright (Browser Automation):**
We chose Playwright over simpler libraries (like BeautifulSoup) because GetYourGuide is a dynamic, JavaScript-heavy website. Playwright allows us to render the full DOM, interact with "Show More" pagination buttons, and handle cookie consent banners just like a real user.
* **Stealth & Anti-Blocking:**
* **Fake User-Agent:** We use `fake_useragent` to generate random, valid browser signatures (User Agents) for every session. This prevents the scraper from being easily identified as a bot script.
* **Headless Customization:** We launch the browser in headless mode but include arguments like `--disable-blink-features=AutomationControlled` to hide standard automation flags. We also inject a script to remove the `navigator.webdriver` property, a common "tell" for bot detection.
* **Human-like Behavior:** To mimic human interaction, we added random `time.sleep` intervals between clicks, pagination loads, and city transitions.



### Example Output (v2)

As seen in the result below, we now successfully capture the map link even when the text description is generic:

```json
{
    "title": "Bubble Planet: An Experience Museum for All Your Senses",
    "price": "€22",
    "link": "...",
    "duration": "1 hour",
    "languages": "German",
    "meeting_point": "Open in Google Maps",
    "meeting_point_maps_link": "https://maps.google.com/?q=@52.49629592895508,13.45350456237793"
}

```