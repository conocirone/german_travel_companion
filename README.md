# German Travel Companion

German Travel Companion is a Semantic Web project designed to model, store, and query tourism information for major German cities. It aggregates data about **Tours** (from GetYourGuide) and **Attractions** (from TripAdvisor), enriches it using Large Language Models (LLMs) to add semantic metadata (such as budget tiers and location settings), and populates an OWL Ontology.

The system facilitates complex queries such as "Which outdoor activities in Berlin have a 'Free' budget?" or "Which museums in Munich are open on Sundays?".

## Repository Structure

The repository is organized into the following directories:

### 1. `data/`
Contains the raw and processed JSON data sets.
- **`pre_llm_processing/`**: Raw data scraped directly from the sources.
  - `tripadvisor_data_final.json`: Raw attractions data.
  - `all_cities_tours.json`: Raw tours data.
- **`post_llm_processing/`**: Final datasets enriched with LLM analysis.
  - `trip_advisor_data_enriched_final.json`: Attractions with added fields like `budget_tier` and `location_setting`.
  - `all_cities_tours.json`: Tours with similar enrichment.

### 2. `ontologies/`
Contains the OWL ontology files.
- **`base_structure/`**: The schema (TBox) of the knowledge graph.
  - `german_city_tourism_final_d2.owl`: The core ontology definition without instances.
- **`populated/`**: The full knowledge graph (ABox).
  - `german_city_tourism_populated.owl`: The final ontology populated with thousands of individuals (tours and attractions) from the data files.

### 3. `scripts/`
Python scripts and notebooks for the entire pipeline.
- **`scrapers/`**: Scripts to scrape data from GetYourGuide and TripAdvisor.
  - `gyg_scraper/`: Scraper for GetYourGuide tours.
  - `trip_advisor_scraping/`: Scraper for TripAdvisor attractions.
- **`stats_generators/`**: Scripts to analyze the datasets.
  - `analyze_statistics_gyg.py`: Generates statistics for tours.
  - `analyze_statistics_trip_advisor.py`: Generates statistics for attractions.
- **`abox_population.py`**: The core script that takes the enriched JSON data and populates the base ontology to create the populated OWL file.
- **`travel_companion.ipynb`**: Notebook for TBox creation.
- **`rules_creation.ipynb`**: Notebook for rules creation.

### 4. `queries/`
- **`sparql_queries.md`**: A collection of Competency Questions and their corresponding SPARQL queries to demonstrate the capabilities of the ontology.

### 5. `stats/`
- Contains Markdown reports (`gyg_stats.md`, `trip_advisor_stats.md`) summarizing the data distribution (e.g., number of tours per city, budget distribution).

