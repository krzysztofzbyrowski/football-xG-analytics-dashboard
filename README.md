# Football Data Engineering Pipeline & xG Analytics ⚽

## Project Overview
This project implements a robust **End-to-End (E2E) Data Pipeline** designed to consolidate football match data from disparate sources into a unified analytical database. 

The core objective of this system is to bridge the gap between **traditional match statistics** (goals, corners, cards) and **advanced metrics** (Expected Goals - xG). By integrating these two distinct datasets, the pipeline enables deeper performance analysis, allowing for the identification of team overperformance and underperformance trends.

## 🏗️ Data Architecture

The system aggregates data from two independent sources, requiring complex entity mapping and data normalization:

1.  **Primary Source (Match Stats):** * *Source:* `football-data.co.uk`
    * *Data:* Full-time results, half-time scores, shots, corners, red/yellow cards.
    * *Method:* HTTP Request Scraping.

2.  **Secondary Source (Advanced Metrics):**
    * *Source:* `Understat.com`
    * *Data:* Expected Goals (xG) and Expected Goals Against (xGA).
    * *Method:* Dynamic scraping using **Selenium** (JavaScript execution extraction).

## ⚙️ Key Features

* **Multi-Source Integration:** Successfully merges datasets with different schema structures and naming conventions (e.g., handling "Man City" vs. "Manchester City" discrepancies via a custom mapping layer).
* **Automated ETL Process:** * **Extract:** Scrapers run automatically to fetch the latest CSVs and JSON payloads.
    * **Transform:** Pandas is used for cleaning, date standardization, and fuzzy matching of team entities.
    * **Load:** Cleaned data is persisted into a **SQLite** relational database for efficient querying.
* **Scalability:** The modular design allows for easy addition of new leagues or data sources.
* **Scheduler Ready:** Scripts are optimized to run via Task Scheduler or Cron jobs for weekly updates.

## 🛠️ Tech Stack

* **Language:** Python 3.11+
* **Data Manipulation:** Pandas, NumPy
* **Web Scraping:** Selenium (Chrome WebDriver), BeautifulSoup4, Requests
* **Database:** SQLite
* **Version Control:** Git & GitHub

## 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/football-data-pipeline.git](https://github.com/YOUR_USERNAME/football-data-pipeline.git)
    cd football-data-pipeline
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the pipeline:**
    You can run the modules individually or use the batch script.
    * *Step 1 (Scrape Leagues):* `python src/scraper/football_data_scraper.py`
    * *Step 2 (Scrape xG):* `python src/scraper/xg_scraper.py`
    * *Step 3 (ETL & Merge):* `python src/database/data_loader.py`

4.  **Automated Scheduling (Optional):**
    To run the pipeline automatically (e.g., weekly), utilize the provided batch script `run_pipeline.bat`.
    * Open **Windows Task Scheduler**.
    * Create a Basic Task.
    * Set the trigger to **Weekly**.
    * Action: **Start a program** -> select `run_pipeline.bat`.

## 📊 Sample Insights
Once the database is built, analysts can run queries to find statistical anomalies, such as:
* Teams with high xG but low actual goal count (Underperformers).
* Defensive efficiency analysis (Goals Conceded vs. xGA).
* Home vs. Away performance splits.

---
*Author: Krzysztof Zbyrowski*