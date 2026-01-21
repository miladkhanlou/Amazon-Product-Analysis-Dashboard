import requests
import json
import os
import pandas as pd
import time
# Snow flake account link:
# https://app.snowflake.com/xvzcrtg/chb65461/

# Keepa API Configuration:
base_url = "https://api.keepa.com/"
API_KEY = "vgdcn1uugof2bjdjniim9lk0phm6607msrj67531nkuqllb6b6krtmev94b3ne3i" #KEEPA

# API Configuration
base_url = "https://api.asindataapi.com/request"
API_KEY = "0F1F6FDD22E9480A81FE60385C18C2BF"

# Output Directories Configuration
OUT_DIR="/mnt/c/Users/mfatol1/dropbox/2-projects/2-amazon_asin_recent/output/staging"
product_directory = f"{OUT_DIR}/raw_rainforest_outputs/products"
single_offer_directory = f"{OUT_DIR}/raw_rainforest_outputs/offers/single_offers"
single_product_directory = f"{OUT_DIR}/raw_rainforest_outputs/products/single_products"
single_search_directory = f"{OUT_DIR}/raw_rainforest_outputs/search/single_search"

os.makedirs(single_product_directory, exist_ok=True)
os.makedirs(single_search_directory, exist_ok=True)
os.makedirs(single_offer_directory, exist_ok=True)

# Categories and Sub-Categories to Extract
categories = [
    {"name": "Computers & Accessories", "id": "541966"}
    ]
sub_categories = [
    # {"name": "Computers & Tablets", "id": "13896617011"}
    {"name": "Laptop Accessories", "id": "3011391011"}, 
    # {"name": "Monitors", "id":"1292115011"},
    # {"name": "Digital Cameras", "id":"1292115011"},
    # {"name": "Cell Phones & Accessories", "id":"2811119011"}
    ]

# Initialize global variables
visited_ids = set()
all_categories= {"category_results": []}
all_products = {"product": []}
failed_asins = []
batch_size = 300
batch_counter = 1
leaf_categories = []
     
###########################################   
# Save Json
###########################################   
def save_json(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

###########################################   
#           Extract Products              #
###########################################
def extract_products(asin, counter):
    product_params = {
        'api_key': API_KEY,
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': asin
    }
    try:
        reponse = requests.get(base_url, product_params)
        print(f"{counter} → [OK] Product Data for ASIN → {asin}")
        reponse.raise_for_status()
        product_response = reponse.json()
        
        if "product" in product_response:
            save_json(product_response, f"{single_product_directory}/{asin}.json")
        else:
            print(f"  [SKIP] No 'product' key in response for {asin}")
            failed_asins.append(asin)
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ASIN {asin} → {e}")
        failed_asins.append(asin)

    # # Optional: pause between requests to avoid throttling
    # time.sleep(0.3)

###########################################   
#             Extract Offers              #
###########################################
def extract_offers(asin, counter):
    """3. Product API Call"""
    offers_params = {
        'api_key': API_KEY,
        'type': 'offers',
        'amazon_domain': 'amazon.com',
        'asin': asin
    }
    try:
        offers_response = requests.get(base_url, offers_params).json()
        print(f"{counter} → [OK] Offer Data for ASIN → {asin}")
        offer_json_path = f"{single_offer_directory}/{asin}.json"
        save_json(offers_response, offer_json_path)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] ASIN {asin} → {e}")
        failed_asins.append(asin)
        
    # # Optional: pause between requests to avoid throttling
    # time.sleep(0.3)

###########################################   
#             Extract Search              #
###########################################
def extract_search(asin, counter):    
    """3. Product API Call"""
    offers_params = {
        'api_key': API_KEY,
        'type': 'search',
        'amazon_domain': 'amazon.com',
        'search_term': asin
    }
    offers_response = requests.get(base_url, offers_params).json()
    print(f"{counter} → [OK] search Data for ASIN → {asin}")
    search_json_path = f"{single_search_directory}/{asin}.json"
    save_json(offers_response, search_json_path)

###########################################   
#           Extraction By step            #
###########################################
def extract_stage():
    # 1. Load ASINs CSV
    asins = pd.read_csv(os.path.join(OUT_DIR, "raw", "asins", f"asins_all_computers.csv"))["asin"].dropna().tolist()
    print("ASINS TO PROCESS: ", len(asins))

    counter = 0
    for asin in asins:
        counter += 1
        extract_offers(asin, counter)
        extract_products(asin, counter)
        extract_search(asin, counter)
        print(f"\n{'-' * 70}\n")
        
###########################################   
#              Main Function              #
###########################################
if __name__ == "__main__":      
    extract_stage()
