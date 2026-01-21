import json
import os
import pandas as pd
from datetime import datetime

# Windows file paths:
STAGING_DIR = "/mnt/c/Users/mfatol1/dropbox/2-projects/2-amazon_asin_recent/output/staging/"
OUT_DIR = os.path.join(STAGING_DIR, "transformed")
RAINFOREST_OUT_DIR = os.path.join(STAGING_DIR, "transformed", "rainforest")

# Create directories if they don't exist
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RAINFOREST_OUT_DIR, exist_ok=True)

def transform_products():
    transfomed_products = {}
    print("\n→ TRANSFORM PRODUCTS")
    all_single_products_path = os.path.join(STAGING_DIR, "raw_rainforest_outputs", "products", "single_products")
    # Transform Product Data
    base_keys = [
        "asin", 
        "date" , 
        "title", 
        "brand", 
        "product_seller", 
        "seller_id",
        "is_prime",
        "is_prime_exclusive_deal",
        "is_new", 
        "is_sold_by_amazon", 
        "is_fba", 
        "rating", 
        "ratings_total",
        "5_star_percentage",
        "5_star_count", 
        "4_star_percentage", 
        "4_star_count", 
        "3_star_percentage", 
        "3_star_count", 
        "2_star_percentage",
        "2_star_count", 
        "1_star_percentage",
        "1_star_count",
        "amazons_choice",
        "price", 
        "has_coupon", 
        "coupon_perc", 
        "stock_availability"
    ]
    for key in base_keys:
        transfomed_products.setdefault(key, [])

    for file in os.listdir(all_single_products_path):
        if not file.endswith(".json"):
            continue

        product_results = os.path.join(all_single_products_path, file)
        with open(product_results, "r") as file:
            data = json.load(file)
            
            capture_date = data.get("request_metadata", {}).get("created_at", "")
            ### Get the date from "created_at" and append to all rows as date format YYYY-MM-DD:
            dt = datetime.fromisoformat(capture_date.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%Y-%m-%d")

            
            ### Transform product details:
            prod = data.get("product")
            
            transfomed_products["asin"].append(prod.get("asin"))
            transfomed_products["date"].append(formatted_date)
            transfomed_products["title"].append(prod.get("title"))
            transfomed_products["brand"].append(prod.get("brand"))
            transfomed_products["is_prime"].append(prod.get("buybox_winner", {}).get("is_prime", ""))
            transfomed_products["is_prime_exclusive_deal"].append(prod.get("buybox_winner", {}).get("is_prime_exclusive_deal", "")) 
            transfomed_products["is_sold_by_amazon"].append(prod.get("buybox_winner", {}).get("fulfillment", {}).get("is_sold_by_amazon", ""))

            # is_fba
            transfomed_products["is_fba"].append(prod.get("buybox_winner", {}).get("fulfillment", {}).get("is_fulfilled_by_amazon", ""))
            
            # Seller_name
            if prod.get("buybox_winner", {}).get("fulfillment", {}).get("third_party_seller", ""):
                transfomed_products["product_seller"].append(prod.get("buybox_winner", {}).get("fulfillment", {}).get("third_party_seller", {}).get("name", ""))
            elif prod.get("buybox_winner", {}).get("fulfillment", {}).get("amazon_seller", ""):
                transfomed_products["product_seller"].append(prod.get("buybox_winner", {}).get("fulfillment", {}).get("amazon_seller", {}).get("name", ""))
            else:
                transfomed_products["product_seller"].append("")

            transfomed_products["seller_id"].append(prod.get("buybox_winner", {}).get("fulfillment", {}).get("third_party_seller", {}).get("id", ""))
                
            transfomed_products["amazons_choice"].append(prod.get("amazons_choice", {}).get("badge_text", ""))
            transfomed_products["is_new"].append(prod.get("buybox_winner", {}).get("condition", {}).get("is_new", ""))
            transfomed_products["rating"].append(prod.get("rating"))
            transfomed_products["ratings_total"].append(prod.get("ratings_total"))
            transfomed_products["price"].append(prod.get("buybox_winner", {}).get("price", {}).get("value"))
            transfomed_products["has_coupon"].append(prod.get("has_coupon", ""))
            transfomed_products["coupon_perc"].append(prod.get("coupon_text", ""))
            transfomed_products["stock_availability"].append(prod.get("buybox_winner", {}).get("availability", {}).get("type"))            
            
            # Rating Breakdown
            transfomed_products["5_star_percentage"].append(prod.get("rating_breakdown", {}).get("five_star", {}).get("percentage", ""))
            transfomed_products["5_star_count"].append(prod.get("rating_breakdown", {}).get("five_star", {}).get("count", ""))
            transfomed_products["4_star_percentage"].append(prod.get("rating_breakdown", {}).get("four_star", {}).get("percentage", ""))
            transfomed_products["4_star_count"].append(prod.get("rating_breakdown", {}).get("four_star", {}).get("count", ""))
            transfomed_products["3_star_percentage"].append(prod.get("rating_breakdown", {}).get("three_star", {}).get("percentage", ""))
            transfomed_products["3_star_count"].append(prod.get("rating_breakdown", {}).get("three_star", {}).get("count", ""))
            transfomed_products["2_star_percentage"].append(prod.get("rating_breakdown", {}).get("two_star", {}).get("percentage", ""))
            transfomed_products["2_star_count"].append(prod.get("rating_breakdown", {}).get("two_star", {}).get("count", ""))
            transfomed_products["1_star_percentage"].append(prod.get("rating_breakdown", {}).get("one_star", {}).get("percentage", ""))
            transfomed_products["1_star_count"].append(prod.get("rating_breakdown", {}).get("one_star", {}).get("count", ""))

    transfomed_products_df = pd.DataFrame(transfomed_products)

    # Drop Duplicated rows
    transfomed_products_df = transfomed_products_df.drop_duplicates()
    
    # Save to CSV
    transfomed_products_df.to_csv(f"{OUT_DIR}/products.csv", index=False, encoding='utf-8')
    transfomed_products_df.to_csv(f"{RAINFOREST_OUT_DIR}/products.csv", index=False, encoding='utf-8')
    return transfomed_products_df

def transform_search():
    print("\n→ TRANSFORM SEARCH DATA")
    search_path = os.path.join(STAGING_DIR, "raw_rainforest_outputs", "search", "single_search")
    search_data = []
    for file in os.listdir(search_path):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(search_path, file), "r", encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
            asin = data.get("request_parameters", {}).get("search_term", "")    
            search_results = data.get("search_results", [])
            for result in search_results:
                if result.get("asin") == asin:
                    recent_sales = result.get("recent_sales", "").split("+")[0] if result.get("recent_sales") else ""
                    recent_sales = recent_sales.replace("K", "000").strip() if "K" in recent_sales else recent_sales
                    search_data.append({
                        "asin": asin,
                        "recent_sales": recent_sales
                    })
                    break 
    # Convert to DataFrame
    search_data_df = pd.DataFrame(search_data)
    # recent_sales to integer
    search_data_df["recent_sales"] = pd.to_numeric(search_data_df["recent_sales"], errors='coerce').fillna(0).astype(int)
    
    # Drop Duplicated rows
    search_data_df = search_data_df.drop_duplicates()

    # Save to CSV
    search_data_df.to_csv(f"{OUT_DIR}/recent_sales.csv", index=False, encoding='utf-8')
    search_data_df.to_csv(f"{RAINFOREST_OUT_DIR}/recent_sales.csv", index=False, encoding='utf-8')
    return search_data_df
        
def transform_offers():
    print("\n→ TRANSFORM OFFERS")
    offers_path = os.path.join(STAGING_DIR, "raw_rainforest_outputs","offers", "single_offers")
    
    transformed_offers = []
    for files in os.listdir(offers_path):
        if files.endswith(".json"):
            with open(os.path.join(offers_path, files), "r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)

            # Check if file is not empty or invalid
            if not isinstance(data, dict):
                print(f"[SKIP] Invalid or empty JSON in: {files}")
                continue

            offers = data.get("offers")
            
            max_offers = 20
            if not offers:
                continue
            for offer in offers:
                transformed_offers.append({
                    "asin": data.get("request_parameters").get("asin"),
                    "seller_name": offer.get("seller", {}).get("name", ""),
                    "seller_id": offer.get("seller", {}).get("id", ""),
                    "buybox_winner": offer.get("buybox_winner", False),
                    "seller_rating": offer.get("seller", {}).get("rating", ""),
                    "seller_ratings_percentage_positive": offer.get("seller", {}).get("ratings_percentage_positive", ""),
                    "seller_ratings_total": offer.get("seller", {}).get("ratings_total", ""),
                    "is_new": offer.get("condition", {}).get("is_new", ""),
                    "is_prime": offer.get("is_prime", ""),
                    "price": offer.get("price", {}).get("value", ""),
                    "condition": offer.get("condition", {}).get("title", ""),
                    "is_fba": offer.get("delivery", {}).get("fulfilled_by_amazon", ""),
                    "is_free_shipping": offer.get("delivery", {}).get("price", {}).get("is_free", "")
                })
                        
    offers_data_df = pd.DataFrame(transformed_offers)
    offers_data_df = offers_data_df.drop_duplicates()
    # Save to CSV
    offers_data_df.to_csv(f"{OUT_DIR}/offers.csv", index=False, encoding='utf-8')
    offers_data_df.to_csv(f"{RAINFOREST_OUT_DIR}/offers.csv", index=False, encoding='utf-8')
    return offers_data_df

######################
# 2. Transform Stage
######################
def transform_stage():    
    # # Transform Product Data
    transform_products()
    
    # # Transform Offers Data
    # transform_offers()
    
    # # Transform Search Data
    # transformed_product_csv = os.path.join(OUT_DIR, "products.csv")
    # if os.path.exists(transformed_product_csv):
    #     transform_search()
    # else:
    #     print(f"[ERROR] File not found: {transformed_product_csv}")

if __name__ == "__main__":
    transform_stage()
