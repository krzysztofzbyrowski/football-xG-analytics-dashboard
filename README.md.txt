# Football Data Engineering Pipeline

Automated ETL pipeline for collecting and analyzing football data (match stats and xG) using Python.

## Features
- **Scraping:** Collects match results from football-data.co.uk and xG data from Understat.
- **Automation:** Uses Selenium and BeautifulSoup for data extraction.
- **Database:** Merges data sources into a SQLite database.

## Project Structure
- `src/scraper/`: Scripts for data collection.
- `src/database/`: ETL scripts for data merging and loading.

## How to run
1. Install dependencies: `pip install -r requirements.txt`
2. Run scrapers.
3. Run data loader.