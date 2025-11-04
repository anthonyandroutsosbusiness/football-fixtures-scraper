import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

BASE_URL = "https://websites.sportstg.com"

# This is the direct link to the external platform (Sportstg/GameDay)
# which is the true source of the tables.
TARGET_PAGES = {
    # This link now points to the STANDINGS for the specific competition ID 
    "Alex_Moore_Standings": "/comp_info.cgi?a=LADDER&compID=746736&client=1-10023-0-0-0",

    # You will need to find the specific compID for other leagues and add them here!
}
# NOTE: You must also change BASE_URL above to "https://websites.sportstg.com"
TARGET_PAGES = {
    # Example: Fixtures for Saturday 11s Men's
    "Saturday_11s_Fixtures": "/fixtures-and-standings/saturday-11s-men's-fixtures-202526/",
    
    # Example: Standings for Alex Moore 7aside
    "Alex_Moore_Standings": "/fixtures-and-standings/alex-moore-7aside-2025/",
    
    # ADD all other links you need to scrape here (e.g., Sunday 11s, 5aside, etc.)
}

def scrape_and_save_data():
    all_data = {}
    output_dir = 'data'
    # Create the 'data' folder
    os.makedirs(output_dir, exist_ok=True) 

    for name, path in TARGET_PAGES.items():
        url = BASE_URL + path
        print(f"Scraping {name} from: {url}")
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status() # Check for bad status codes

            # Pandas attempts to find and read all HTML tables on the page
            tables = pd.read_html(response.text)
            
            if tables:
                # Assuming the main table is the first one found (tables[0]).
                # If not, you may need to manually inspect the page source to find the correct index.
                df = tables[0] 
                
                # Basic cleaning: replace spaces with underscores and lower case column names
                df.columns = [col.replace(' ', '_').lower() for col in df.columns]
                
                # Save the cleaned table data as a JSON file
                filename = os.path.join(output_dir, f'{name.lower()}.json')
                df.to_json(filename, orient='records', indent=4)
                all_data[name] = f"Successfully scraped and saved {len(df)} records to {filename}"
            else:
                all_data[name] = "No tables found on page or table structure is JavaScript-driven."
                
        except Exception as e:
            all_data[name] = f"An error occurred while scraping {name}: {e}"
            
    # Save a run log with the current time
    with open(os.path.join(output_dir, 'last_run.txt'), 'w') as f:
        f.write(f"Last scrape completed: {datetime.now().isoformat()}\n")
        f.write(json.dumps(all_data, indent=4))
        
    print("Scraping finished. Check the 'data' directory for results.")

if __name__ == "__main__":

    scrape_and_save_data()
