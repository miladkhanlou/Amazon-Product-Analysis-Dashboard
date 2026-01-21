import requests
import json
import csv
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import urllib.parse
import keepa
from dotenv import load_dotenv

# add argument to indicate the stage of extraction
# import relevant python package
import argparse

stage_of_extraction = 6
category_to_download = "2_in_1_Laptop_Computers_asins"

"""
"Traditional_Laptop_Computers_asins": 1, 
"Tower_Computers_asins" : 2, 
"Mini_Computers_asins": 3, 
"Computer_Tablets_asins": 4, 
"All-in-One_Computers_asins": 5, 
"2_in_1_Laptop_Computers_asins": 6
"""

# Global Variables
asins = []
all_products = []  

# -----------------------------
# CONFIGURATION
# -----------------------------
load_dotenv()
API_KEY = os.getenv("KEEPA_API_KEY")  # Replace with your Keepa API key
OUT_DIR=os.getenv("OUT_DIR")  # Output directory

CATEGORY_ID = 13896603011   # All-in-One Computers

# Finder API endpoint
BASE_URL = os.getenv("BASE_URL")

# Number of results per page (Keepa max is usually 1500)
PER_PAGE = 9

# Optional: categories from full hierarchy
TARGET_CATEGORY = 13896603011

# Create a list of category ID tree to fetch from 493964 > 541966 > 13896617011 > 565098 > 13896603011
CATEGORY_PATH = [
    ["493964", "541966", "13896617011", "565098", "13896603011"], # All-in-One Computers
    ["493964", "541966", "13896617011", "565098", "13896597011"], # Tower Computers
    ["493964", "541966", "13896617011", "565098", "13896591011"], # Mini Computers
    ["493964", "541966", "13896617011", "565108", "13896615011"], # Traditional Laptop Computers
    ["493964", "541966", "13896617011", "565108", "13896609011"], # 2 in 1 Laptop Computers
    ["493964", "541966", "13896617011", "565098", "1232597011"]  # Computer Tablets
]

# Category ID to Name mapping (for reference)
CATEGORY_ID_NAME_MAP = {"13896603011": "All-in-One Computers",
                        "13896597011": "Tower Computers",
                        "13896591011": "Mini Computers",
                        "13896615011": "Traditional Laptop Computers",
                        "13896609011": "2 in 1 Laptop Computers",
                        "1232597011": "Computer Tablets"
                       }
# -----------------------------
def get_asins_from_category(category_id, category_name):
    """Fetch ASINs from a Keepa Finder query for one page."""
    selection = {
        # Price difference Filters
        "deltaPercent_lte": 50,  # at most 50% price drop in last 30 days
        "deltaPercent_gte": 5,  # at least 10% price drop in last 30 days
        
        # Basic Filters:
        "page": stage_of_extraction,
        "perPage": 50,
        "domain": 1,
        "categories_include": category_id,   # leaf category only
        "productType": 0,                    # 0 = all, 1 = Amazon only, 2 = Marketplace only
    }
    
    # Set Prefix for output based on the extra filter other than the Basic filters:
    prefix = "deltaPercent"
    
    # Encode JSON for inclusion in URL
    selection_str = json.dumps(selection)
    encoded_selection = urllib.parse.quote(selection_str)
    
    url = f"{BASE_URL}?key={API_KEY}&domain=1&selection={encoded_selection}"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Check for ASINs in response
        if "asinList" not in data:
            print("[FAIL] No ASINs returned. Full response:")
            return [], prefix

        # Save raw response for debugging in json file:
        with open(f"{OUT_DIR}/output/staging/raw/asins/{prefix}_asin_finder_{category_name}.json", "w") as f:
            json.dump(data, f, indent=2)
        
        # Debugging information
        print(f"[OK] Page Retrieved {len(data['asinList'])} ASINs.")
        asin_list = data["asinList"]
        return asin_list, prefix
        
    except Exception as e:
        print(f"[FAIL] Error fetching data from Keepa API: {e}\n")
        return [], prefix

def extract_asins():
    for path in CATEGORY_PATH:
        category_name = CATEGORY_ID_NAME_MAP.get(path[-1], "Unknown")
        category_id = path[-1]
        print(f"Fetching ASINs for category path: {' > '.join(path)}")
        
        extracted_asins, prefix = get_asins_from_category(category_id, category_name)
        if not extracted_asins or len(extracted_asins) == 0:
            print("No ASINs found for this category path.")
            continue
        
        for asin in extracted_asins:
            asins.append({"category_id": category_id, "category_name": category_name, "asin": asin})
    # Save ASINs to CSV
    if asins:
        asins_df = pd.DataFrame(asins)
        asins_df.to_csv(os.path.join(OUT_DIR, "output", "staging", "raw", "asins", f"asins_{stage_of_extraction}.csv"), index=False)
        print(f"ASINs saved to {os.path.join(OUT_DIR, 'output', 'staging', 'raw', 'asins', f'asins_{stage_of_extraction}.csv')}")
    else:
        print("No ASINs found for this category path.")
    return prefix


### Remove duplicate ASINs from the CSV file
def remove_duplicates(file_path):
    try:
        df = pd.read_csv(os.path.join(file_path, f"asins_{stage_of_extraction}.csv"))
        initial_count = len(df)
        df.drop_duplicates(subset=['asin'], inplace=True)
        final_count = len(df)
        df.to_csv(os.path.join(file_path, f"asins_cleaned_{stage_of_extraction}.csv"), index=False)
        print(f"Removed {initial_count - final_count} duplicate ASINs. {final_count} unique ASINs remain.")
    except Exception as e:
        print(f"Error removing duplicates: {e}")

def chunk_list(list, size):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(list), size):
        yield list[i:i + size]
    
def get_products_from_asins():
    # Load ASINs from CSV 
    ###################################################################
    ########### A. Using with stage_of_extraction variable ###########
    ###################################################################
    # asins_df = pd.read_csv(os.path.join(OUT_DIR, "output", "staging", "raw", "asins", f"asins_{stage_of_extraction}.csv"))
    # distinct_categories = asins_df['category_name'].unique().tolist()
    # asins_list = []
    # for category in distinct_categories:
    #     category_asins = asins_df[asins_df['category_name'] == category]['asin'].tolist()
    #     asins_list.extend(category_asins[:120])  # Limit to first 20 ASINs per category for testing
    
    ###################################################################
    ########### B. Using with category_to_download variable ###########
    ###################################################################
    asins_df = pd.read_csv(os.path.join(OUT_DIR, "output", "staging", "raw", "asins", f"{category_to_download}.csv"))
    asins_list = asins_df['asin'].tolist()
    
    
    # Initialize Keepa API
    api = keepa.Keepa(API_KEY)
    
    # Set timeout and other parameters
    api.timeout = 120
    chunk_size = 2
    max_retries = 3
    retry_backoff = 2  # Exponential backoff multiplier
    try:
        # Fetch product data in chunks of 2 ASINs:
        for chunk_idx, chunk in enumerate(chunk_list(asins_list, chunk_size), start=1):
            products_fetched = False
            current_retry = 0
            wait_time = 2
            while not products_fetched and current_retry <= max_retries:
                try:
                    products = api.query(
                        chunk,
                        domain="US",
                        aplus=1,           # Include A+ content (enabled by default)
                        stats=365,         # Get statistics for the last 180 days
                        offers=20,         # Include offer information (enabled by default) +6
                        history=True,      # Include historical price and rank data (enabled by default)
                        days=365,          # Fetch 365 days of history
                        videos=0,          # Do not include video information
                        rating=1,          # Include rating and review count history +1
                        buybox=1,           # Include Buy Box history +1
                        stock = 1          # Include stock history +2
                    )
                    # Total of extra token = 10 tokens per ASIN
                    
                    all_products.extend(products)
                    products_fetched = True

                # If an error occurs, retry up to max_retries times with exponential backoff:
                except Exception as e:
                    print(f"Error fetching product data for chunk {chunk_idx}: {e}")
                    current_retry += 1
                    error_msg = str(e)
                    
                    # Check for timeout errors specifically
                    if "Read timed out" in error_msg or "timeout" in error_msg.lower():
                        print(f"  ⚠ Timeout error: {e}")
                    else:
                        print(f"  ✗ Error: {e}")
                        
                    # Retry logic for timeout errors
                    if current_retry <= max_retries:
                        print(f"  ⏳ Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        wait_time *= retry_backoff  # Exponential backoff
                        
                    # If a different error occurs, log it and stop retrying
                    else:
                        print(f"  ✗ Failed after {max_retries} retries. Skipping chunk {chunk_idx}")
            
            # Pause between chunks to avoid rate limiting
            if chunk_idx < len(list(chunk_list(asins_list, chunk_size))):
                time.sleep(1.5)
                
            # Short pause between chunks
            time.sleep(1)
            
    # If error occurs outside of retries, just save whatever we have fetched so far:
    except Exception as e:
        print(f"Unexpected error: {e}")
        
    # Save all fetched products to JSON
    OUT_PATH = os.path.join(OUT_DIR, "output", "staging", "raw", "products", f"all_products_{stage_of_extraction}.json")
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    
    if all_products:
        with open(OUT_PATH, "w") as f:
            json.dump({"products": all_products}, f, indent=2, ensure_ascii=False,
          default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o))
        print(f"Product data saved to {OUT_PATH}")
    else:
        print("No product data fetched.")

def validate_downloaded():
    asins_df = pd.read_csv(os.path.join(OUT_DIR, "output", "staging", "raw", "asins", f"asins_{stage_of_extraction}.csv"))["asin"].tolist()
    json_file = os.path.join(OUT_DIR, "output", "staging", "raw", "products", f"all_products_{stage_of_extraction}.json")
    
    with open(json_file, "r") as f:
        data = json.load(f)
        downloaded_asins = [product['asin'] for product in data['products']]    
    missing_asins = set(asins_df) - set(downloaded_asins)
    print(f"Total ASINs expected: {len(asins_df)}")
    print(f"Total ASINs downloaded: {len(downloaded_asins)}")
    print(f"Total missing ASINs: {len(missing_asins)}")
    if missing_asins:
        print("Missing ASINs:")
        for asin in missing_asins:
            print(asin)
    else:
        print("All ASINs downloaded successfully.")
    
    
    

# ----------------------------- M A I N -----------------------------
if __name__== "__main__":
    # Extract ASINs:
    extract_asins()
    
    # # Remove Duplicate ASINs
    remove_duplicates(os.path.join(OUT_DIR, "output", "staging", "raw", "asins"))

    # Get Products from ASINs
    get_products_from_asins()
    
    # # Validate Downloaded Products
    validate_downloaded()


