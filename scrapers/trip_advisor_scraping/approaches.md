# Project Methodology: Data Collection & Enrichment Pipeline

This document outlines the technical architecture, challenges, and solutions implemented to build the dataset for the project. The process consisted of two main phases: **Web Scraping** (TripAdvisor) and **Data Enrichment** (LLM-based classification).

## Phase 1: Web Scraping Strategy

The goal was to scrape attraction data from TripAdvisor. However, TripAdvisor employs sophisticated anti-bot measures (fingerprinting, IP rate limiting, and CAPTCHAs) which required an iterative approach to solve.

### 1. Initial Attempt: Browser Automation (Camoufox + Playwright)
Our first approach utilized **Playwright** combined with **Camoufox**.
* **Technology:** Playwright is a modern automation library for end-to-end testing, and Camoufox is a customized Firefox browser designed to spoof browser fingerprints (user agent, screen resolution, etc.) to look like a legitimate human user.
* **Outcome:** Failed. While Camoufox successfully masked some browser properties, it was not sufficient to bypass TripAdvisor’s network-level bans. Our IP address was frequently flagged and banned.

### 2. Intermediate Attempt: Proxy Rotation
To address the IP banning issue, we implemented **Proxy Rotation**.
* **Technology:** We routed traffic through a pool of proxies to simulate requests coming from different users/locations.
* **Outcome:** Failed. We relied on free public proxies, which suffered from extremely high latency, low uptime, and poor reputation scores. The few working proxies were quickly detected and blacklisted by TripAdvisor after scraping only a handful of elements.

### 3. Final Solution: SeleniumBase
We migrated to **SeleniumBase**, a robust Python framework built on top of Selenium.
* **Why it worked:** Unlike standard Selenium, SeleniumBase includes a specific **"Undetected Mode" (UC Mode)**. This feature automatically manages the `chromedriver` binary to prevent detection by anti-bot services (like Cloudflare or Akamai) that check for automation flags in the browser's JavaScript execution context.
* **Result:** This allowed us to scrape the base dataset effectively without triggering IP bans or CAPTCHAs.

---

## Phase 2: Data Enrichment & Ontology Mapping

After scraping, the dataset was incomplete regarding our specific ontology requirements. We needed to map activities to two custom classes that are not explicitly listed on TripAdvisor:
1.  **LocationSetting:** `indoor` vs `outdoor`
2.  **BudgetTier:** `free`, `low` (1-10€), `medium` (11-20€), `high` (>20€)

To populate these fields, we needed an intelligent agent capable of reasoning and, if necessary, retrieving external pricing data.

### Approach 1: RAG with DuckDuckGo + Llama 3.1
We initially attempted a Retrieval-Augmented Generation (RAG) pipeline locally.
* **Workflow:** Use the `duckduckgo-search` library to find information about an attraction, then pass that context to **Llama 3.1** to classify it.
* **Limitations:** The search results were often irrelevant or contained generic SEO spam, providing misleading context to the LLM. This led to frequent hallucinations in the classification.

### Approach 2: AI Search (Perplexica) + Llama 3.1
We upgraded the retrieval mechanism to **Perplexica**, an open-source AI-powered search engine.
* **Technology:** Perplexica uses "Reasoning Mode" to understand the query intent better than a standard keyword search.
* **Advantages:** The context retrieved was significantly more accurate, leading to better classification by Llama 3.1.
* **Bottleneck:** Efficiency. The "Reasoning Mode" was computationally expensive and slow, taking approximately **1 minute per activity**. With nearly 2,000 attractions, this approach was unscalable.

### Final Solution: Gemini 1.5 Pro
To balance accuracy, speed, and cost, we migrated the enrichment pipeline to **Gemini 1.5 Pro**.

* **Key Advantages:**
    * **World Knowledge:** Gemini possesses a vast internal knowledge base regarding global landmarks and pricing, reducing the need for external search for every single item.
    * **Inference Speed:** Being a cloud-native model, it processes requests significantly faster than local LLM pipelines.
    * **Reasoning Capability:** It demonstrated superior zero-shot performance in understanding complex instructions regarding our pricing tiers.

#### The Prompt
We engineered the following prompt to ensure strict adherence to our JSON schema and ontology logic:

> Task: Classify the attractions in the json file based on the name and context. In case you are unsure about the price and the location setting look up online for the correct informations.
>    
>     1. location_setting: 'indoor' or 'outdoor'
>        - Museums, theaters, churches (interior visits) = indoor
>        - Parks, squares, streets, monuments, outdoor markets = outdoor
>    
>     2. budget_tier: Based on the BASE ENTRY FEE to access the attraction ITSELF.
>        - 'free': Public spaces (squares, streets, parks, neighborhoods, markets), monuments you can view from outside, churches with free entry, free museums
>        - 'low': 1€-10€ entry fee
>        - 'medium': 11€-20€ entry fee  
>        - 'high': >20€ entry fee
>        
>     IMPORTANT: 
>     - Ignore prices for guided tours, experiences, or activities - only consider the base entry fee.
>     - Public squares (like Alexanderplatz, Potsdamer Platz), streets, parks, and neighborhoods are ALWAYS 'free'.
>     - If unsure and it's a public outdoor space, default to 'free'.
>
>     Return ONLY a valid JSON file with JSON code. No intro text. You must add the two new fields to the ones which were already in the file
>     Example: {{"location_setting": "indoor", "budget_tier": "medium"}}

