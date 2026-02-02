@echo off
echo ========================================================
echo   FOOTBALL DATA PIPELINE - AUTO UPDATE
echo ========================================================

cd /d "%~dp0"

echo.
echo [1/3] Running League Scraper...
python src/scraper/football_data_scraper.py

echo.
echo [2/3] Running xG Scraper (Selenium)...
python src/scraper/xg_scraper.py

echo.
echo [3/3] Running ETL Data Loader...
python src/database/data_loader.py

echo.
echo ========================================================
echo   PIPELINE FINISHED SUCCESSFULLY
echo ========================================================

timeout /t 10