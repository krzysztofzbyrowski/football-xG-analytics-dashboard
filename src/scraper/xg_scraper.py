import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---

TARGET_SEASON = '2025'
TARGET_LEAGUES = ['EPL', 'La_liga', 'Bundesliga', 'Serie_A', 'Ligue_1']

# Mapping of team names from Understat source to the local database standard.
# NOTE: Do not modify these keys or values as they are essential for data integrity.
# Names are valid for clubs playing in the specified leagues during 2025/26 season.
TEAM_MAPPING = {
    "Arsenal": "Arsenal", "Manchester City": "Man City",
    "Aston Villa": "Aston Villa", "Manchester United": "Man United",
    "Chelsea": "Chelsea", "Liverpool": "Liverpool",
    "Fulham": "Fulham", "Brentford": "Brentford",
    "Newcastle United": "Newcastle", "Everton": "Everton",
    "Sunderland": "Sunderland", "Brighton": "Brighton",
    "Bournemouth": "Bournemouth", "Tottenham": "Tottenham",
    "Crystal Palace": "Crystal Palace", "Leeds": "Leeds",
    "Nottingham Forest": "Nott'm Forest", "West Ham": "West Ham",
    "Burnley": "Burnley", "Wolverhampton Wanderers": "Wolves",
    "Barcelona": "Barcelona", "Real Madrid": "Real Madrid",
    "Atletico Madrid": "Ath Madrid", "Villarreal": "Villarreal",
    "Espanyol": "Espanol", "Real Betis": "Betis",
    "Celta Vigo": "Celta", "Real Sociedad": "Sociedad",
    "Osasuna": "Osasuna", "Girona": "Girona",
    "Elche": "Elche", "Sevilla": "Sevilla",
    "Athletic Club": "Ath Bilbao", "Valencia": "Valencia",
    "Alaves": "Alaves", "Rayo Vallecano": "Vallecano",
    "Getafe": "Getafe", "Mallorca": "Mallorca",
    "Levante": "Levante", "Real Oviedo": "Oviedo",
    "Bayern Munich": "Bayern Munich", "Borussia Dortmund": "Dortmund",
    "Hoffenheim": "Hoffenheim", "VfB Stuttgart": "Stuttgart",
    "RasenBallsport Leipzig": "RB Leipzig", "Bayer Leverkusen": "Leverkusen",
    "Freiburg": "Freiburg", "Eintracht Frankfurt": "Ein Frankfurt",
    "Union Berlin": "Union Berlin", "FC Cologne": "FC Koln",
    "Borussia M.Gladbach": "M'gladbach", "Wolfsburg": "Wolfsburg",
    "Augsburg": "Augsburg", "Hamburger SV": "Hamburg",
    "Werder Bremen": "Werder Bremen", "Mainz 05": "Mainz",
    "St. Pauli": "St Pauli", "FC Heidenheim": "Heidenheim",
    "AC Milan": "Milan", "Inter": "Inter",
    "Roma": "Roma", "Napoli": "Napoli",
    "Juventus": "Juventus", "Como": "Como",
    "Atalanta": "Atalanta", "Bologna": "Bologna",
    "Lazio": "Lazio", "Udinese": "Udinese",
    "Sassuolo": "Sassuolo", "Cagliari": "Cagliari",
    "Genoa": "Genoa", "Cremonese": "Cremonese",
    "Parma Calcio 1913": "Parma", "Torino": "Torino",
    "Lecce": "Lecce", "Fiorentina": "Fiorentina",
    "Verona": "Verona", "Pisa": "Pisa",
    "Paris Saint Germain": "Paris SG", "Lens": "Lens",
    "Marseille": "Marseille", "Lyon": "Lyon",
    "Lille": "Lille", "Rennes": "Rennes",
    "Strasbourg": "Strasbourg", "Toulouse": "Toulouse",
    "Lorient": "Lorient", "Monaco": "Monaco",
    "Angers": "Angers", "Brest": "Brest",
    "Nice": "Nice", "Paris FC": "Paris FC",
    "Le Havre": "Le Havre", "Nantes": "Nantes",
    "Auxerre": "Auxerre", "Metz":"Metz"
}

def get_xg_data_selenium(leagues, season):
    """
    Scrapes Expected Goals (xG) data from Understat using Selenium.
    
    This function utilizes the 'datesData' variable exposed in the DOM 
    to retrieve structured JSON data directly, bypassing HTML parsing.

    Args:
        leagues (list): List of league identifiers used in the URL structure.
        season (str): The target season year.

    Returns:
        pd.DataFrame: A DataFrame containing match statistics and xG data.
    """
    all_matches = []
    
    print("[INFO] Initializing Chrome WebDriver with automated extraction options...")
    
    options = Options()
    # Mask automation to prevent anti-bot detection
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--start-maximized")

    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        for league in leagues:
            url = f"https://understat.com/league/{league}/{season}"
            print(f"[INFO] Accessing URL for league: {league}...")
            
            driver.get(url)
            
            # Pause execution to ensure all page assets and scripts load completely
            time.sleep(4)
            
            # Retrieve data directly from the browser's JavaScript memory variable 'datesData'
            # This avoids parsing the raw HTML source code.
            try:
                json_data = driver.execute_script("return datesData")
            except Exception as js_error:
                print(f"[ERROR] JavaScript Execution Failed: Could not retrieve 'datesData'. Page load might be incomplete. Details: {js_error}")
                continue

            if not json_data:
                print("[WARNING] The retrieved data object is empty.")
                continue

            # Process the retrieved data
            count = 0
            for match in json_data:
                # Process only completed matches where 'isResult' is True
                if match.get('isResult'):
                    
                    home_raw = match['h']['title']
                    away_raw = match['a']['title']
                    
                    match_data = {
                        'League': league,
                        'Date': match['datetime'],
                        'HomeTeam': TEAM_MAPPING.get(home_raw, home_raw),
                        'AwayTeam': TEAM_MAPPING.get(away_raw, away_raw),
                        'FTHG': int(match['goals']['h']),
                        'FTAG': int(match['goals']['a']),
                        'xG_Home': round(float(match['xG']['h']), 2),
                        'xG_Away': round(float(match['xG']['a']), 2)
                    }
                    all_matches.append(match_data)
                    count += 1
            
            print(f"[INFO] Successfully extracted {count} matches.")

    except Exception as e:
        print(f"[ERROR] Critical error during execution: {e}")
    finally:
        driver.quit()
        print("[INFO] Browser session closed.")

    if not all_matches:
        return pd.DataFrame()

    df = pd.DataFrame(all_matches)
    # Standardize date format to YYYY-MM-DD
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

if __name__ == "__main__":
    df_xg = get_xg_data_selenium(TARGET_LEAGUES, TARGET_SEASON)
    
    if not df_xg.empty:
        # Define the output directory.
        # NOTE: Update the path below to your preferred absolute location if necessary.
        # Defaults to "data/raw" relative to the script location.
        output_directory = os.path.join("data", "raw")
        
        # Ensure the directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        full_path = os.path.join(output_directory, "xg_data_full.csv")
        
        df_xg.to_csv(full_path, index=False)
        print(f"[INFO] Data successfully saved to: {full_path}")
        print(df_xg.head())
    else:
        print("[WARNING] No data was retrieved.")