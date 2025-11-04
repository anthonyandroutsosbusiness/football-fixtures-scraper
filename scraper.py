import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# BASE_URL is the domain of the data provider (Sportstg/GameDay)
BASE_URL = "https://websites.sportstg.com"
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the unique IDs for each competition and the file name you want
# You may need to verify these IDs if your leagues change!
# ----------------------------------------------------------------------
TARGET_COMPETITIONS = {
    # FIXTURES Pages (a=R)
    "Saturday_11s_Mens_Fixtures": "753894",
    "Sunday_11s_Fixtures": "753896",
    "Alex_Moore_7aside_Fixtures": "753895",
    "Boyd_Wilson_Mon_Fixtures": "753893",
    
    # STANDINGS Pages (a=LADDER) - Keep one for your index.html
    "Alex_Moore_Standings": "746736"
}
# ----------------------------------------------------------------------

def get_fixtures_url(comp_id):
    """Constructs the URL for the next week's fixtures on the Sportstg platform."""
    
    # Calculate the date for the upcoming weekend (e.g., this Saturday)
    # The 'Round' system often doesn't update on Monday, so targeting the date is safer.
    today = datetime.now()
    # Find the next Saturday (weekday 5)
    days_until_saturday = (5 - today.weekday() + 7) % 7
    if days_until_saturday == 0:
        # If today is Saturday, target this Saturday.
        next_saturday = today 
    else:
        # Otherwise, target the next Saturday.
        next_saturday = today + timedelta(days=days_until_saturday)
        
    date_param = next_saturday.strftime('%Y-%m-%d')
    
    # URL structure for FIXTURES on Sportstg (a=R)
    url = f"{BASE_URL}/comp_info.cgi?a=ROUND&compID={comp_id}&round={date_param}&client=1-10023-0-0-0"
    return url

def get_standings_url(comp_id):
    """Constructs the URL for the standings page."""
    # URL structure for STANDINGS on Sportstg (a=LADDER)
    return f"{BASE_URL}/comp_info.cgi?a=LADDER&compID={comp_id}&client=1-10023-0-0-0"

def scrape_and_save_data():
    all_data = {}
    
    for name, comp_id in TARGET_COMPETITIONS.items():
        if 'Fixtures' in name:
            url = get_fixtures_url(comp_id)
            print(f"Generating FIXTURES URL for {name} for this week: {url}")
        elif 'Standings' in name:
            url = get_standings_url(comp_id)
            print(f"Generating STANDINGS URL for {name}: {url}")
        else:
            continue
            
        try:
            # Use requests to get the page content
            response = requests.get(url, timeout=30) # Increased timeout to 30s
            response.raise_for_status() 

            # Pandas attempts to find and read all HTML tables on the page
            tables = pd.read_html(response.text)
            
            if tables:
                # Assuming the required table is the first one found (tables[0]).
                df = tables[0]
                
                # Clean up column names for easy JSON/JS access
                df.columns = [col.replace(' ', '_').replace('.', '').lower() for col in df.columns]
                
                # Save the data
                filename = os.path.join(OUTPUT_DIR, f'{name.lower()}.json')
                df.to_json(filename, orient='records', indent=4)
                all_data[name] = f"SUCCESS: Scraped and saved {len(df)} records to {filename}"
            else:
                all_data[name] = f"FAILED: No tables found on URL: {url}"
                
        except Exception as e:
            all_data[name] = f"ERROR: An error occurred while scraping {name}: {e}"
            
    # Save a run log
    with open(os.path.join(OUTPUT_DIR, 'last_run.txt'), 'w') as f:
        f.write(f"Last scrape completed: {datetime.now().isoformat()}\n")
        f.write(json.dumps(all_data, indent=4))
        
    print("Scraping finished. Check the 'data' directory for results.")

if __name__ == "__main__":
    scrape_and_save_data()
