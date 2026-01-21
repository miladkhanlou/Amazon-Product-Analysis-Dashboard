import numpy as np
import pandas as pd
import os
import json
import datetime
from datetime import datetime

price_history_map = {
    0: "amazon_price",
    1: "new_price",
    2: "used_price",
    3: "sales_rank",
    4: "list_price",
    6: "refurbished_price",
    7: "new_fbm_price",
    8: "lightning_deal_price",
    9: "warehouse_price",
    10: "new_fba_price",
    11: "new_offer_count",
    12: "used_offer_count",
    13: "refurbished_offer_count",
    15: "extra_info_updates",
    16: "rating",
    17: "review_count",
    18: "new_buybox_shipping_price",
    19: "used_new_shipping_price",
    20: "used_very_good_shipping_price",
    21: "used_good_shipping_price",
    22: "used_acceptable_shipping_price",
    27: "refurbished_shipping_price",
    28: "ebay_new_price",
    29: "ebay_used_price",
    30: "ebay_refurbished_price",
    32: "buybox_used_shipping_price",
    33: "prime_exclusive_price"
}

def convert_timestamp(keepa_timestamp):
    if keepa_timestamp is None:
        return None
    else:
        # Convert Keepa timestamp to integer if string
        keepa_timestamp = int(keepa_timestamp) if isinstance(keepa_timestamp, str) else keepa_timestamp
        # Convert Keepa timestamp to Unix timestamp
        unix_timestamp = (keepa_timestamp + 21564000) * 60
        # Convert to datetime object
        dt_object = datetime.fromtimestamp(unix_timestamp)
        return dt_object.strftime('%Y-%m-%d')

########## Products ##########
def transform_static(products):
    transformed_statics = []
    for product in products:
        stats = product.get("stats", {})        
        # basic info
        asin = product.get("asin", "")
        manufacturer = product.get("manufacturer", "")
        model = product.get("model", "")
        color = product.get("color", "")
        size = product.get("size", "")
        product_group = product.get("productGroup", "")
        brand = product.get("brand", "")
        title = product.get("title", "")
        
        # Last Updates
        last_rating_update = convert_timestamp(product.get("lastRatingUpdate", None)) if product.get("lastRatingUpdate") and product.get("lastRatingUpdate") > 0 else None
        last_price_change = convert_timestamp(product.get("lastPriceChange", None)) if product.get("lastPriceChange") and product.get("lastPriceChange") > 0 else None
        last_sold_update = convert_timestamp(product.get("lastSoldUpdate", None)) if product.get("lastSoldUpdate") and product.get("lastSoldUpdate") > 0 else None
        last_update = convert_timestamp(product.get("lastUpdate", None)) if product.get("lastUpdate") and product.get("lastUpdate") > 0 else None

        # releaseDate:
        date = product.get("releaseDate", None) if product.get("releaseDate", None) else None
        if date:
            # Convert integer date number 20250801 to date object
            release_date = datetime.strptime(str(date), '%Y%m%d').date()
        else:
            release_date = None
                    
        # monthlySold
        monthly_sold = product.get("monthlySold", None) if product.get("monthlySold", None) else 0

        # availabilityAmazon
        availability_amazon = product.get("availabilityAmazon", 0) if product.get("availabilityAmazon", 0) else 0
        # availability AmazonDelay
        delay = product.get("availabilityAmazonDelay", 0)
        if delay and len(delay) > 1 and delay[1] != delay[0]:
            availability_delay_indays = abs(round(delay[0]/60)-round(delay[1]/60))
        else:
            availability_delay_indays = 0

        # has reviews
        has_reviews = product.get("hasReviews", False) if product.get("hasReviews", False) else False
  
        # Categories
        categories = product.get("categoryTree", [])
        root_category_name = categories[0].get("name", "") if categories else ""
        root_category_id = categories[0].get("catId", "") if categories else ""
        leaf_category_name = categories[-1].get("name", "") if categories else ""
        leaf_category_id = categories[-1].get("catId", "") if categories else ""
        category_tree_path = ",".join([cat.get("name", "") for cat in categories]) if categories else "" 
        
        # current deals
        deals_data = product.get("deals", [])
        if not deals_data:
            access_type = ""
            deal_type = ""
            deal_start_time = None
            deal_end_time = None

        access_type = deals_data[0].get("accessType", "") if deals_data else ""
        deal_type = deals_data[0].get("badge", "") if deals_data else ""
        deal_start_time = convert_timestamp(deals_data[0].get("startTime", None)) if deals_data and deals_data[0].get("startTime") > 0 else None
        deal_end_time = convert_timestamp(deals_data[0].get("endTime", None)) if deals_data and deals_data[0].get("endTime") > 0 else None

        # Current Coupons
        coupon = product.get("coupon", [])
        if not coupon:
            discount_coupon = None
            subscribe_and_save_coupon = None    
        else:
            i = 0
            while i < len(coupon) - 1:
                discount_coupon = abs(coupon[i]) if coupon[i] else None
                subscribe_and_save_coupon = coupon[i + 1] if coupon[i + 1] else None
                i += 2
        
        # Current Prices and Ranks
        current_amazon_price = stats.get("current", [])[0] / 100.0 if stats.get("current", []) else 0
        current_new_price = stats.get("current", [])[1] / 100.0 if stats.get("current", []) else 0
        current_used_price = stats.get("current", [])[2] / 100.0 if stats.get("current", []) else 0
        current_list_price = stats.get("current", [])[4] / 100.0 if stats.get("current", []) else 0
        current_sales_rank = stats.get("current", [])[3] if stats.get("current", []) else 0
        current_new_count = stats.get("current", [])[11] if stats.get("current", []) else 0
        current_used_count = stats.get("current", [])[12] if stats.get("current", []) else 0
        current_refurbished_count = stats.get("current", [])[13] if stats.get("current", []) else 0
        current_new_rating = stats.get("current", [])[16] / 10 if stats.get("current", []) else 0
        current_total_reviews = stats.get("current", [])[17] if stats.get("current", []) else 0
        # specialFeatures:
        special_features = product.get("specialFeatures", [])
        special_features_str = ",".join(f for f in special_features if f) if special_features else ""
        
        # specificUsesForProduct:
        specific_uses_for_product = product.get("specificUsesForProduct", [])
        
        # Join list elements with comma, handle empty list
        specific_uses_for_product_str = ",".join(f for f in specific_uses_for_product if f) if specific_uses_for_product else ""

        # returnRate:
        return_rate = product.get("returnRate", "") if product.get("returnRate", "") else 0

        transformed_statics.append({
            "asin": asin,
            "brand": brand,
            "title": title,
            "manufacturer": manufacturer,
            "product_group": product_group,
            "model": model,
            "amazon_price": current_amazon_price,
            "new_price": current_new_price,
            "used_price": current_used_price,
            "list_price": current_list_price,
            "sales_rank": current_sales_rank,
            "new_count": current_new_count,
            "used_count": current_used_count,
            "refurbished_count": current_refurbished_count,
            "rating": current_new_rating,
            "total_reviews": current_total_reviews,
            "color": color,
            "release_date": release_date,
            "size": size,
            "has_reviews": has_reviews,
            "access_type": access_type,
            "deal_type": deal_type,
            "deal_start_time": deal_start_time,
            "deal_end_time": deal_end_time,
            "last_price_change": last_price_change,
            "special_features_str": special_features_str,
            "recent_month_sales": monthly_sold,
            "specific_uses_for_product_str": specific_uses_for_product_str,
            "root_category_name": root_category_name,
            "root_category_id": root_category_id,
            "leaf_category_name": leaf_category_name,
            "leaf_category_id": leaf_category_id,
            "discount_coupon": discount_coupon,
            "subscribe_and_save_coupon": subscribe_and_save_coupon,
            "last_rating_update": last_rating_update,
            "last_sold_update": last_sold_update,
            "last_update": last_update,
            "availability_amazon": availability_amazon,
            "availability_days": availability_delay_indays,
            "return_rate": return_rate,
            "category_tree_path": category_tree_path
        })
    print(f"Transformed {len(transformed_statics)} products.")
    return pd.DataFrame(transformed_statics)

########### Current Buy Box ##########
def transform_current_buy_box(products):
    transformed_current_buy_box = []
    for product in products:
        asin = product.get("asin", "")
        stats = product.get("stats", {})
        buy_box_seller = stats.get("buyBoxSellerId", "") if stats.get("buyBoxSellerId", "") else ""
        buy_boxed_used_seller = stats.get("buyBoxUsedSellerId", "") if stats.get("buyBoxUsedSellerId", "") else ""
        buy_box_price = stats.get("buyBoxPrice", 0) / 100.0 if stats.get("buyBoxPrice", 0) else 0
        buy_box_used_price = stats.get("buyBoxUsedPrice", 0) / 100.0 if stats.get("buyBoxUsedPrice", 0) else 0
        buy_box_availability = stats.get("buyBoxAvailabilityMessage", "") if stats.get("buyBoxAvailabilityMessage", "") else ""
        buy_box_condition = stats.get("buyBoxCondition", 0) if stats.get("buyBoxCondition", 0) else 0
        buy_box_is_amazon = stats.get("buyBoxIsAmazon", False) if stats.get("buyBoxIsAmazon") else False
        buy_box_is_fba = stats.get("buyBoxIsFBA", False) if stats.get("buyBoxIsFBA") else False
        buy_box_is_free_shipping = stats.get("buyBoxIsFreeShippingEligible", False) if stats.get("buyBoxIsFreeShippingEligible") else False
        buy_box_is_prime = stats.get("buyBoxIsPrimeEligible", False) if stats.get("buyBoxIsPrimeEligible") else False
        buy_box_is_used = stats.get("buyBoxIsUsed", False) if stats.get("buyBoxIsUsed") else False
        buy_box_max_quantity = stats.get("buyBoxMaxOrderQuantity", 0) if stats.get("buyBoxMaxOrderQuantity", 0) else 0
        buy_box_strikethrough_price = stats.get("buyBoxSavingBasis", 0) / 100.0 if stats.get("buyBoxSavingBasis", 0) else 0
        buy_box_shipping_country = stats.get("buyBoxShippingCountry", "") if stats.get("buyBoxShippingCountry", "") else ""
        used_condition = stats.get("buyBoxUsedCondition", 0) if stats.get("buyBoxUsedCondition", 0) else 0

        # buyBoxEligibleOfferCounts: want to grab values of each of  from this attribute:
        buy_box_eligible_offer_counts = product.get("buyBoxEligibleOfferCounts", [])
        if buy_box_eligible_offer_counts:
            new_fba_count = buy_box_eligible_offer_counts[0] if len(buy_box_eligible_offer_counts) > 0 else 0
            new_fbm_count = buy_box_eligible_offer_counts[1] if len(buy_box_eligible_offer_counts) > 1 else 0
            used_fba_count = buy_box_eligible_offer_counts[2] if len(buy_box_eligible_offer_counts) > 2 else 0
            used_fbm_count = buy_box_eligible_offer_counts[3] if len(buy_box_eligible_offer_counts) > 3 else 0
            refurbished_fba_count = buy_box_eligible_offer_counts[4] if len(buy_box_eligible_offer_counts) > 4 else 0
            refurbished_fbm_count = buy_box_eligible_offer_counts[5] if len(buy_box_eligible_offer_counts) > 5 else 0
        else:
            new_fba_count = 0
            new_fbm_count = 0
            used_fba_count = 0
            used_fbm_count = 0
            refurbished_fba_count = 0
            refurbished_fbm_count = 0
                    
        transformed_current_buy_box.append({
            "asin": asin,
            "seller_id": buy_box_seller,
            "price": buy_box_price,
            "availability": buy_box_availability,
            "condition_id": buy_box_condition,
            "is_amazon": buy_box_is_amazon,
            "is_fba": buy_box_is_fba,
            "is_free_shipping": buy_box_is_free_shipping,
            "is_prime": buy_box_is_prime,
            "is_used": buy_box_is_used,
            "max_quantity": buy_box_max_quantity,
            "strikethrough_price": buy_box_strikethrough_price,
            "new_fba_count": new_fba_count,
            "new_fbm_count": new_fbm_count,
            "used_seller_id": buy_boxed_used_seller,
            "used_price": buy_box_used_price,
            "used_condition_id": used_condition,
            "used_fba_count": used_fba_count,
            "used_fbm_count": used_fbm_count,
            "refurbished_fba_count": refurbished_fba_count,
            "refurbished_fbm_count": refurbished_fbm_count
        })
    print(f"Transformed {len(transformed_current_buy_box)} current buy box records.")
    return pd.DataFrame(transformed_current_buy_box)

########### Coupon History ##########
def transform_coupon_history(products):
    transformed_coupon_history = []
    for product in products:
        asin = product.get("asin", "")
        coupon_history = product.get("couponHistory", [])
        if coupon_history:
            i = 0
            while i < len(coupon_history) - 1:
                coupon_date = convert_timestamp(coupon_history[i]) if coupon_history[i] else None
                discount_coupon = abs(coupon_history[i + 1]) if coupon_history[i + 1] else None
                subscribe_and_save_coupon = abs(coupon_history[i + 2]) if coupon_history[i + 2] else None
                transformed_coupon_history.append({
                    "asin": asin,
                    "coupon_date": coupon_date,
                    "discount_coupon": discount_coupon,
                    "subscribe_and_save_coupon": subscribe_and_save_coupon
                })
                i += 3
    print(f"Transformed {len(transformed_coupon_history)} coupon history records.")
    return pd.DataFrame(transformed_coupon_history)

########### Buy Box Winners ##########
def transform_buy_box_winners(products):
    transform_buy_box = []
    for product in products:
        asin = product.get("asin", "")
        buy_box_winners = product.get("stats", {}).get("buyBoxStats", {})
        if not buy_box_winners:
            transform_buy_box.append({
                "asin": asin,
                "seller_id": None,
                "avg_price": 0,
                "avg_new_offer_count": 0,
                "avg_used_offer_count": 0,
                "is_fba": False,
                "percent_won": 0
            })
            continue
        
        for winners in buy_box_winners:
            winner_info = buy_box_winners.get(f"{winners}", "")
            transform_buy_box.append({
                "asin": asin,
                "seller_id": winners,
                "avg_price": winner_info.get("avgPrice", 0) / 100.0 if winner_info.get("avgPrice", 0) else 0,
                "avg_new_offer_count": winner_info.get("avgNewOfferCount", 0) if winner_info.get("avgNewOfferCount", 0) else 0,
                "avg_used_offer_count": winner_info.get("avgUsedOfferCount", 0) if winner_info.get("avgUsedOfferCount", 0) else 0,
                "is_fba": winner_info.get("isFBA", False) if winner_info.get("isFBA", False) else False,
                "percent_won": winner_info.get("percentageWon", 0) if winner_info.get("percentageWon", 0) else 0
            })
    print(f"Transformed {len(transform_buy_box)} buy box winners.")
    return pd.DataFrame(transform_buy_box)

########### Stats ##########
def transform_stats(products):
    transformed_avg_data = []
    for product in products:
        asin = product.get("asin", "")
        stats = product.get("stats", {})
        if stats:
            # Get average values from stats
            avg_attributes = ["avg", "avg30", "avg90", "avg180", "avg365"]
            for avg_attr in avg_attributes:
                stats_avg = stats.get(avg_attr, [])
                stats_avg_len = len(stats_avg)
                for index, price_type in price_history_map.items():
                    if index < stats_avg_len:
                        stat_value = stats_avg[index] if stats_avg[index] else 0
                        transformed_avg_data.append({
                            "asin": asin,
                            "type_id": index,
                            "avg_window": avg_attr,
                            "value": stat_value
                        })
    print(f"Transformed {len(transformed_avg_data)} stats records.")
    return pd.DataFrame(transformed_avg_data)

########## Historical Data ##########
def transform_historical_data(products):
    transformed_historical_data = []
    for product in products:
        asin = product.get("asin", "")
        csv_data = product.get("csv", {})
        if csv_data is None:
            transformed_historical_data.append({
                "asin": asin,
                "date": None,
                "type_id": None,
                "value": 0
            })
            continue
        csv_len = len(csv_data)
        for index, price_type in price_history_map.items():
            price_data = csv_data[index] if csv_data[index] and index < csv_len else []
            if price_data:
                i = 0
                while i < len(price_data) -1 :
                    date = convert_timestamp(price_data[i]) if price_data[i] and price_data[i] > 0 else None
                    price = price_data[i + 1] if price_data[i + 1] else 0
                    transformed_historical_data.append({
                        "asin": asin,
                        "date": date,
                        "type_id": index,
                        "value": price
                    })
                    i += 2
    print(f"Transformed {len(transformed_historical_data)} historical data records.")
    return pd.DataFrame(transformed_historical_data)

########### Categories ##########
def transform_categories(products):
    transformed_categories = []
    for product in products:
        asin = product.get("asin", "")
        category_tree = product.get("categoryTree", [])
        if category_tree:
            rank = 1
            for leaf in category_tree:
                transformed_categories.append({
                    "asin": asin,
                    "category_tree_path": ",".join([cat.get("name", "") for cat in category_tree]),
                    "category_name": leaf.get("name", ""),
                    "category_level": rank,
                })
                rank += 1
    print(f"Transformed {len(transformed_categories)} categories.")
    return pd.DataFrame(transformed_categories)

########## Offer History ##########
def transform_offer_history(products):
    transformed_offer_history = []
    for product in products:
        asin = product.get("asin", "")
        offer_history = product.get("offers", [])
        for offer in offer_history:
            seller_id = offer.get("sellerId", "") if offer.get("sellerId", "") else ""
            condition_id = offer.get("condition", 0) if offer.get("condition", 0) else 0
            is_amazon = offer.get("isAmazon", "") if offer.get("isAmazon", "") else False 
            is_fba = offer.get("isFBA", "") if offer.get("isFBA", "") else False
            is_prime = offer.get("isPrime", "") if offer.get("isPrime", "") else False
            # lates_price = offer.get("offerCSV", [])[-2] / 100.0 if offer.get("offerCSV", []) and len(offer.get("offerCSV", [])) >= 2 else 0
            # latest_price_date = convert_timestamp(offer.get("offerCSV", [])[-3]) if offer.get("offerCSV", []) and len(offer.get("offerCSV", [])) >= 3 and offer.get("offerCSV", [])[-3] > 0 else None
            offers_per_date = offer.get("offerCSV", [])
            # each 3 elements represents different data that needs to be extracted and appeneded to transformed_offer_history
            # date: 1st element, price: 2nd element, quantity: 3rd element
            j = 0
            while j < len(offers_per_date) - 2:
                offer_date = convert_timestamp(offers_per_date[j]) if offers_per_date[j] and offers_per_date[j] > 0 else None
                offer_price = offers_per_date[j + 1] / 100.0 if offers_per_date[j + 1] else 0
                offer_quantity = offers_per_date[j + 2] if offers_per_date[j + 2] else 0
                transformed_offer_history.append({
                    "asin": asin,
                    "seller_id": seller_id,
                    "date": offer_date,
                    "offer_price": offer_price,
                    "offer_quantity": offer_quantity,
                    "condition_id": condition_id,
                    "is_amazon": is_amazon,
                    "is_fba": is_fba,
                    "is_prime": is_prime
                })
                j += 3 #Update j to next set of 3 elements
            # transformed_offer_history.append({
            #     "asin": asin,
            #     "offer_id": offer_id,
            #     "seller_id": seller_id,
            #     "offer_price": lates_price,
            #     "latest_price_date": latest_price_date,
            #     "condition_id": condition_id,
            #     "is_amazon": is_amazon,
            #     "is_fba": is_fba,
            #     "is_prime": is_prime
            # })

    return pd.DataFrame(transformed_offer_history)
########## Buy Box History ##########
def transform_buy_box_history(products):
    transformed_buy_box_history = []
    for product in products:
        asin = product.get("asin", "")
        # buyBoxSellerIdHistory
        buyBoxSellerIdHistory = product.get("buyBoxSellerIdHistory", [])
        if buyBoxSellerIdHistory:
            i = 0
            while i < len(buyBoxSellerIdHistory):
                selling_date = convert_timestamp(buyBoxSellerIdHistory[i]) if buyBoxSellerIdHistory[i] else None
                seller_id = buyBoxSellerIdHistory[i + 1] if buyBoxSellerIdHistory[i + 1] else None
                transformed_buy_box_history.append({
                    "asin": asin,
                    "selling_date": selling_date,
                    "seller_id": seller_id
                })
                i += 2
    print(f"Transformed {len(transformed_buy_box_history)} buy box history records.")
    return pd.DataFrame(transformed_buy_box_history)

########## Product Monthly Sold ##########
def transform_monthly_sold(products):
    transformed_monthly_sold = []
    for product in products:
        asin = product.get("asin", "")
        monthly_sold = product.get("monthlySoldHistory", [])
        if monthly_sold:
            i = 0
            while i < len(monthly_sold):
                month = convert_timestamp(monthly_sold[i])if monthly_sold[i] and monthly_sold[i] else None
                sold = monthly_sold[i + 1] if monthly_sold[i + 1] > 0 else None
                transformed_monthly_sold.append({
                    "asin": asin,
                    "date": month,
                    "sold": sold
                })
                i += 2
    print(f"Transformed {len(transformed_monthly_sold)} monthly sold records.")
    return pd.DataFrame(transformed_monthly_sold)
  

def transform_json():
    print(f"\n{'='*60}\nStarting transformations of Amazon products\n{'='*60}")
    
    # Windows path
    data_dir="/mnt/c/Users/mfatol1/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/raw/products/all_products.json"
    OUT_DIR = "/mnt/c/Users/mfatol1/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/transformed"
    KEEPA_OUT_DIR = "/mnt/c/Users/mfatol1/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/transformed/keepa"


    # Mac OS path
    # data_dir="/Users/milad/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/raw/products/all_products.json"
    # OUT_DIR = "/Users/milad/Dropbox/2-Projects/2-Amazon_ASIN_Recent/output/staging/transformed"

    os.makedirs(OUT_DIR, exist_ok=True)
    
    with open(data_dir, "r") as file:
        data = json.load(file)
        products = data.get("products", [])
        
    # Trasnform and save each dataframe to CSV
    coupon_history_df = transform_coupon_history(products)
    coupon_history_df.to_csv(os.path.join(OUT_DIR, "historical_coupon.csv"), index=False)
    coupon_history_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_coupon.csv"), index=False)

    stats_df = transform_stats(products)
    stats_df.to_csv(os.path.join(OUT_DIR, "historical_stats.csv"), index=False)
    stats_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_stats.csv"), index=False)

    buy_box_history_df = transform_buy_box_history(products)
    buy_box_history_df.to_csv(os.path.join(OUT_DIR, "historical_buy_box.csv"), index=False)
    buy_box_history_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_buy_box.csv"), index=False)

    offer_history_df = transform_offer_history(products)
    offer_history_df.to_csv(os.path.join(OUT_DIR, "historical_offers.csv"), index=False)
    offer_history_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_offers.csv"), index=False)
    
    monthly_sold_df = transform_monthly_sold(products)
    monthly_sold_df.to_csv(os.path.join(OUT_DIR, "historical_monthly_sold.csv"), index=False)
    monthly_sold_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_monthly_sold.csv"), index=False)
    
    historical_data_df = transform_historical_data(products)
    historical_data_df.to_csv(os.path.join(OUT_DIR, "historical_data.csv"), index=False)
    historical_data_df.to_csv(os.path.join(KEEPA_OUT_DIR, "historical_data.csv"), index=False)
    
    static_df = transform_static(products)
    static_df.to_csv(os.path.join(OUT_DIR, "static.csv"), index=False)
    static_df.to_csv(os.path.join(KEEPA_OUT_DIR, "static.csv"), index=False)
    
    categories_df = transform_categories(products)
    categories_df.to_csv(os.path.join(OUT_DIR, "categories.csv"), index=False)
    categories_df.to_csv(os.path.join(KEEPA_OUT_DIR, "categories.csv"), index=False)

    buy_box_winners_df = transform_buy_box_winners(products)
    buy_box_winners_df.to_csv(os.path.join(OUT_DIR, "winners.csv"), index=False)
    
    buy_box_df = transform_current_buy_box(products)
    buy_box_df.to_csv(os.path.join(OUT_DIR, "buy_box.csv"), index=False)
    
    print(f"\n{'='*60}\n✅ All transformations completed and CSV files saved\n{'='*60}\n")
    
################################################## CSV KEYS ##################################################
if __name__ == "__main__":
    transform_json()
