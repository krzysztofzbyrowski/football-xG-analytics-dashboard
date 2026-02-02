import pandas as pd
import sqlite3
import os
import glob

# --- CONFIGURATION ---

# Define the base directory for the project.
# NOTE: If running this script from a location other than the project root,
# replace os.getcwd() with the absolute path to your project folder.
BASE_DIR = os.getcwd()

# Define directory paths relative to the base directory
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
XG_FILE_PATH = os.path.join(RAW_DATA_DIR, "xg_data_full.csv")
DB_PATH = os.path.join(BASE_DIR, "football_2526.db")

def load_and_merge_data():
    """
    Orchestrates the Extract, Transform, Load (ETL) process.

    This function performs the following steps:
    1. Clean Build: Removes the existing database to prevent schema conflicts.
    2. Extract: Loads Expected Goals (xG) data and League CSV files.
    3. Transform: Merges league data with xG metrics based on date and team names.
    4. Load: Persists the consolidated data into a SQLite database.
    """
    print("[INFO] Initiating database generation process...")

    # --- STEP 1: CLEAN BUILD (DATABASE RESET) ---
    # Remove the existing database file to ensure a fresh build.
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[INFO] Existing database removed: {os.path.basename(DB_PATH)}")
        except PermissionError:
            print("[ERROR] Could not remove the database file. Please ensure it is not open in another application (e.g., DB Browser, Excel).")
            return
    else:
        print("[INFO] No existing database found. A new one will be created.")

    # --- STEP 2: LOAD xG DATA ---
    xg_df = pd.DataFrame()
    if os.path.exists(XG_FILE_PATH):
        print(f"[INFO] xG data file found: {os.path.basename(XG_FILE_PATH)}")
        try:
            xg_df = pd.read_csv(XG_FILE_PATH)
            # Convert 'Date' column to datetime objects for accurate merging
            xg_df['Date'] = pd.to_datetime(xg_df['Date'])
            
            # Filter only relevant columns for the merge
            xg_cols = ['Date', 'HomeTeam', 'AwayTeam', 'xG_Home', 'xG_Away']
            xg_df = xg_df[xg_cols]
        except Exception as e:
            print(f"[ERROR] Failed to read xG file: {e}")
    else:
        print("[WARNING] xG data file not found. The database will be created without xG metrics.")

    # --- STEP 3: PROCESS LEAGUE FILES ---
    # Identify all CSV files in the raw data directory, excluding the xG file itself.
    all_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.csv"))
    csv_files = [f for f in all_files if "xg_data_full" not in f]

    if not csv_files:
        print("[ERROR] No league data CSV files found in the raw data directory.")
        return

    # Establish connection to the SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    total_matches = 0
    print(f"[INFO] Processing {len(csv_files)} league files...")

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        # Derive the database table name from the filename (e.g., 'E0.csv' -> 'E0')
        table_name = os.path.splitext(file_name)[0]
        
        print(f"[INFO] Processing file: {file_name} -> Table: [{table_name}]...", end=" ")

        try:
            # Load league match data
            df = pd.read_csv(file_path)
            
            # Standardize dates (football-data.co.uk typically uses DD/MM/YYYY format)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            
            # Merge with xG data if available
            if not xg_df.empty:
                # Use a left join to retain all league matches even if xG data is missing
                df = pd.merge(df, xg_df, on=['Date', 'HomeTeam', 'AwayTeam'], how='left')
            else:
                # Initialize empty xG columns to maintain schema consistency
                df['xG_Home'] = None
                df['xG_Away'] = None

            # Write the transformed data to the SQL database
            df.to_sql(table_name, conn, index=False)
            
            print(f"Success ({len(df)} records)")
            total_matches += len(df)

        except Exception as e:
            print(f"\n[ERROR] Failed to process {file_name}: {e}")

    conn.close()
    print("-" * 50)
    print(f"[INFO] ETL Process Completed. Total matches processed: {total_matches}")
    print(f"[INFO] Database saved at: {DB_PATH}")

if __name__ == "__main__":
    load_and_merge_data()