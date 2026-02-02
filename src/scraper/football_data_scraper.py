import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- CONFIGURATION ---

BASE_URL = "https://www.football-data.co.uk/"

# Directory where the downloaded CSV files will be saved.
# NOTE: Modify the path below to your desired absolute local path if necessary.
# Defaults to a "data/raw" folder relative to the script execution location.
OUTPUT_DIRECTORY = os.path.join("data", "raw")

# Identifier for the target season (e.g., "2526" for 2025/2026)
SEASON_ID = "2526"

# Mapping of website endpoints to specific CSV filenames to download
# Format: "page_suffix": ["target_filename_substring"]
LEAGUES_TO_DOWNLOAD = {
    "englandm.php":        ["E0.csv"],       # Premier League
    "germanym.php":        ["D1.csv"],       # Bundesliga 1
    "italym.php":          ["I1.csv"],       # Serie A
    "spainm.php":          ["SP1.csv"],      # La Liga Primera
    "francem.php":         ["F1.csv"],       # Ligue 1
    "belgiumm.php":        ["B1.csv"],       # Belgian Jupiler League
    "switzerland.php":     [".csv"],         # Switzerland (Main CSV)
    "poland.php":          [".csv"]          # Poland (Main CSV)
}

# HTTP Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def download_file(url, folder):
    """
    Downloads a file from the specified URL and saves it to the target folder.

    Args:
        url (str): The direct URL of the file to download.
        folder (str): The local directory path where the file will be saved.
    """
    filename = url.split('/')[-1]
    local_path = os.path.join(folder, filename)
    
    try:
        print(f"[INFO] Downloading {filename}...")
        with requests.get(url, headers=HEADERS, stream=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[INFO] Successfully saved to {local_path}")
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")

def run_scraper():
    """
    Main execution function.
    Iterates through the defined leagues, parses the HTML, identifies valid CSV links
    based on the season ID, and initiates the download.
    """
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"[INFO] Created directory: {OUTPUT_DIRECTORY}")
    else:
        print(f"[INFO] Saving data to: {OUTPUT_DIRECTORY}")

    print(f"[INFO] Starting download process for Season {SEASON_ID}...")
    print("-" * 60)

    for page_suffix, targets in LEAGUES_TO_DOWNLOAD.items():
        full_url = urljoin(BASE_URL, page_suffix)
        
        try:
            response = requests.get(full_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all anchor tags with an href attribute
            csv_links = soup.find_all('a', href=True)
            
            found_count = 0
            for link in csv_links:
                href = link['href']
                
                # Filter for CSV files only
                if not href.lower().endswith('.csv'):
                    continue

                is_match = False
                
                # Logic for minor leagues (structure differs from major leagues)
                if page_suffix in ["switzerland.php", "poland.php"]:
                    # Exclude fixture files, keep main data files
                    if "fixture" not in href.lower(): 
                        is_match = True
                
                # Logic for major leagues (filtering by Season ID and target codes)
                elif SEASON_ID in href:
                    for target in targets:
                        if target in href:
                            is_match = True
                            break
                
                if is_match:
                    download_url = urljoin(BASE_URL, href)
                    download_file(download_url, OUTPUT_DIRECTORY)
                    found_count += 1

            if found_count == 0:
                print(f"[WARNING] No matching files found on page: {page_suffix}")
                
        except Exception as e:
            print(f"[ERROR] Error accessing {page_suffix}: {e}")

    print("-" * 60)
    print("[INFO] All download tasks finished.")

if __name__ == "__main__":
    run_scraper()