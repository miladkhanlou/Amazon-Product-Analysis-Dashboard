[PowerBi Dashboard](https://app.powerbi.com/view?r=eyJrIjoiMWY3Zjc4MWEtZTRhZC00NDJjLTljZjktMDU5ZjE5MjRhMDliIiwidCI6ImM3Y2EzYjc2LWVkYmUtNGYyNi1iZTljLTgzOWM2MjQ5ZDZiYiJ9&pageName=8b6051beb05050706ed7)
## Data Extraction Strategy (Keepa & Rainforest)

### Overall Extraction Approach

This project uses **two complementary data sources** to build a complete and reliable view of Amazon products, sellers, pricing, and sales behavior:

- **Keepa** is used for **historical data and seller completeness**
- **Rainforest** is used for **same-day live pricing, offers, and sales signals**


## 1. Keepa API:

**Keepa provides:**

- Long-term **historical pricing and sales trends**
- More complete **seller identification**
- Reliable product-level metadata

**It is also necessary because:**

- Rainforest does **not** provide complete seller identity when Amazon wins the Buy Box
- Historical sales trends are not available from Rainforest

### Keepa Extraction Steps (Conceptual)

1. **Extract Categories**
   - Identify all target Category and and subcategories.
   - Category and subcategories we target:
     - **Computers & Accessories** (main category)
       - **Computers & Tablets**
         - Desktops
           - All-in-Ones
           - Mini PCs
           - Towers
         - Laptops
           - Traditional Laptops
         - Tablets
       - **Tablet Accessories**
2. - **Extract Product ASINs**
     - Collect ASINs for all products under the selected categories
     - We extract 200 ASIN per category
3. - **Extract Product-Level Data**
     - Pricing history
     - Ratings and review distribution
     - Historical sales indicators
4. - **Extract Seller Names from Product Data**
     - Identify sellers associated with each product from all product results
5. - **Extract Detailed Seller Metadata**
     - For each seller, retrieve complete seller-level information
     - This data later serves as the **authoritative seller reference**

### Keepa API limitations

- **KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits per hour**, preventing real-time full refreshes.

- **Same day live buy box data:** Due to token limitation, Cannot always capture:

  - **final Buy Box price** and **Recent Month's Sale**

  - **recent other offers**

  - **current Buy Box features** (e.g `Prime`, `FBA`, `Condition`)

### **List of datasets Transformed from Keepa:**

##### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



##### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                                                  | Example      |
| --------- | ------------------------------------------------------------ | ------------ |
| `asin`    | Product identifier                                           | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot                          | `2025-10-13` |
| `type_id` | Keepa historically identifier (Amazon price, new price, used price, buy box price,  lightning deal, rating, monthly sale, etc. ) | `1`          |
| `value`   | Price or metric value (scaled integer)                       | `116900`     |



##### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



##### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



##### 5. Historical Offers

**Purpose:** Captures **seller-level offer competition** over time.

| Column           | What it represents               | Example value    |
| ---------------- | -------------------------------- | ---------------- |
| `asin`           | Product ASIN                     | `B0FSL77PX2`     |
| `seller_id`      | Seller offering the product      | `A1SH4EAPSJFCZH` |
| `date`           | Offer snapshot date              | `2025-10-13`     |
| `offer_price`    | Offer price at that time         | `1169.0`         |
| `offer_quantity` | Quantity captured (if available) | `0`              |
| `condition_id`   | Condition code for the offer     | `1`              |
| `is_amazon`      | Flag if seller is Amazon         | `0`              |
| `is_fba`         | Flag if Fulfilled by Amazon      | `1`              |
| `is_prime`       | Flag if Prime-eligible           | `1`              |



##### 6. Historicl Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



##### 7. Seller Profile

**Purpose:** Static **seller identity dimension**.

| Column             | What it represents                                 | Example value   |
| ------------------ | -------------------------------------------------- | --------------- |
| `seller_id`        | Seller identifier                                  | `AKZMCWIYNER20` |
| `selling_brand`    | Brand associated with seller (from your transform) | `apple`         |
| `selling_count`    | Count of items/records tied to this seller         | `26`            |
| `avg_30_sale_rank` | Avg 30-day sales rank signal                       | `4989`          |



### 8. Seller Data

**Purpose:** Tracks **seller performance and reputation metrics**.

| Column                    | What it represents                   | Example value                        |
| ------------------------- | ------------------------------------ | ------------------------------------ |
| `seller_id`               | Seller identifier                    | `AKZMCWIYNER20`                      |
| `seller_name`             | Seller display name                  | `AKZMCWIYNER20` *(varies by seller)* |
| `current_rating_count`    | Recent/current rating count          | `93`                                 |
| `total_rating_count`      | Total rating count                   | `1187`                               |
| `New_Ownership_Rate`      | Buy Box ownership rate for New       | `12`                                 |
| `used_Ownership_Rate`     | Buy Box ownership rate for Used      | `0`                                  |
| `is_fba`                  | Whether FBA appears dominant/flagged | `1`                                  |
| `positive_rating_30_days` | Positive ratings in last 30 days     | `88`                                 |
| `positive_rating_60_days` | Positive ratings in last 60 days     | `92`                                 |
| `positive_rating_90_days` | Positive ratings in last 90 days     | `88`                                 |
| `rating_count_30_days`    | Rating volume in last 30 days        | `17`                                 |
| `rating_count_60_days`    | Rating volume in last 60 days        | `36`                                 |
| `rating_count_90_days`    | Rating volume in last 90 days        | `114`                                |



---

## 2. Rainforest Extraction Steps

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Reuse ASINs from Keepa**
   - The same ASIN list extracted from Keepa is used as input
1. **Extract Live Product Data**
   - **Current prices** and **Buy Box** information
1. **Extract All Offers per ASIN**: (Third-party sellers, Fulfillment type, Prime eligibility , etc.)
1. **Extract Recent Monthly Sales**
   - Retrieved using Rainforest search endpoints
   - Provides short-term demand signals

### **List of datasets Transformed from Keepa:**

##### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

| Column                    | What it represents                           | Example value                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `asin`                    | Product ASIN                                 | `B00I9HPIUS`                                                 |
| `title`                   | Product title                                | `Dell OptiPlex 7020 MFF Mini Business Desktop Computer, ...` |
| `brand`                   | Brand name                                   | `‎Dell`                                                       |
| `price`                   | Product price (snapshot)                     | `109.0`                                                      |
| `product_seller`          | Seller name associated with product snapshot | `GS Global Management LLC`                                   |
| `seller_id`               | Seller ID associated with product snapshot   | `A1AFLMIRO3MS2G`                                             |
| `rating`                  | Product average rating                       | `5.0`                                                        |
| `ratings_total`           | Total rating count                           | `1.0`                                                        |
| `stock_availability`      | Stock status label                           | `not_in_stock`                                               |
| `is_prime`                | Prime-eligible flag                          | `True`                                                       |
| `is_prime_exclusive_deal` | Prime-exclusive deal flag                    | `False`                                                      |
| `is_sold_by_amazon`       | Sold-by-Amazon flag                          | `False`                                                      |
| `is_fba`                  | Fulfilled-by-Amazon flag                     | `False`                                                      |
| `is_new`                  | New condition flag                           | `True`                                                       |
| `amazons_choice`          | Amazon’s Choice badge field                  | `Amazon's Choice`                                            |
| `has_coupon`              | Coupon present flag                          | `True`                                                       |
| `coupon_perc`             | Coupon text/value captured                   | `Apply $1000 coupon`                                         |
| `5_star_percentage`       | 5-star percent                               | `100.0`                                                      |
| `5_star_count`            | 5-star count                                 | `1.0`                                                        |
| `4_star_percentage`       | 4-star percent                               | `0.0`                                                        |
| `4_star_count`            | 4-star count                                 | `0.0`                                                        |
| `3_star_percentage`       | 3-star percent                               | `0.0`                                                        |
| `3_star_count`            | 3-star count                                 | `0.0`                                                        |
| `2_star_percentage`       | 2-star percent                               | `0.0`                                                        |
| `2_star_count`            | 2-star count                                 | `0.0`                                                        |
| `1_star_percentage`       | 1-star percent                               | `0.0`                                                        |
| `1_star_count`            | 1-star count                                 | `0.0`                                                        |
| `date`                    | Extraction date                              | `2026-01-13`                                                 |



##### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

| Column                               | What it represents                       | Example value              |
| ------------------------------------ | ---------------------------------------- | -------------------------- |
| `asin`                               | Product ASIN                             | `B00TREI0D4`               |
| `seller_name`                        | Offer seller name                        | `GS Global Management LLC` |
| `seller_id`                          | Offer seller ID                          | `A1AFLMIRO3MS2G`           |
| `buybox_winner`                      | Whether this offer is the Buy Box winner | `True`                     |
| `seller_rating`                      | Seller rating score                      | `4.5`                      |
| `seller_ratings_percentage_positive` | Seller % positive ratings                | `91.0`                     |
| `seller_ratings_total`               | Seller total rating count                | `98.0`                     |
| `is_new`                             | Offer is new condition flag              | `False`                    |
| `is_prime`                           | Offer is Prime-eligible flag             | `False`                    |
| `price`                              | Offer price                              | `109.0`                    |
| `condition`                          | Offer condition text                     | `Refurbished - Excellent`  |
| `is_fba`                             | Offer fulfilled by Amazon                | `False`                    |
| `is_free_shipping`                   | Offer has free shipping                  | `True`                     |



##### 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |



---

## Known Cross-Source Limitations

#### 1. Seller Identity Gaps

- When **Amazon or Amazon Resale wins the Buy Box**, `RainforestAPI`:
  - Does **not** return Amazon seller IDs
  - Only returns IDs for other sellers
- Amazon Resale seller identity is also incomplete in Keepa

**Because of this:**

- Seller identity must be **completed after extraction**
- Seller data from Keepa is used to **enrich Rainforest results**
- Amazon Resale seller IDs are **manually assigned** to ensure visibility

#### 2. ASIN & Naming Mismatches

- ASIN naming and structure differ between Keepa and Rainforest
- Direct alignment is not always possible at extraction time

**This requires:**

- Additional normalization
- Post-load reconciliation in Snowflake



---

## Transform Raw JSON files & Load to snowflake Bronze Layer Schema

- Convert **raw JSON → structured tables**
- Load into the **warehouse for analytics**
- Enables historical trend analysis and joins
  **Keywords:** ETL, normalization, warehouse-ready



---

## Data Cleaning – Key Issues (Silver Layer clean up)

1. **Main Data Cleaning:**

   - Nulls
   - Duplicates
   - Data types
   - Boolean normalization

2. **Post-Extraction Cleanup In Silver Layer**

   - **ASIN redirection:** Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
   - **Amazon seller gaps:** Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
     - **Seller backfill:** Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
   - **Duplicate products:** Redirected ASINs caused **duplicate product rows** that had to be cleaned.

   - **Product** and seller **records** are **normalized** for reporting
   - **Cross-API mismatch:** Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

   **This step ensures:**

   - Amazon retail performance is not undercounted
   - Seller-level analytics are accurate
   - Power BI dashboards reflect true marketplace structure



# Data Modeling

- ## Gold Layer – Fact Tables

  ### `gold.fact_product`

  - Main **product performance** fact table (sales, revenue-related metrics, rating metrics, ranks)
  - Includes **sales rank** and **rating rank** used in product-level dashboards

  ### `gold.fact_product_category`

  - Bridge table mapping each product to its **category levels**
  - Supports category drill-down and leaf-category analysis

  ### `gold.fact_offers`

  - Offer-level fact table for **all seller offers per product**
  - Used for seller comparisons, pricing competition, condition-based offer analysis

  ### `gold.fact_buybox_products` (VIEW)

  - Buy Box snapshot fact view per product
  - Includes buy box winner attributes (price, Prime, FBA, condition, availability) with IDs for filtering

  ### `gold.fact_sellers`

  - Seller-level performance fact table
  - Includes seller metrics like selling count, rating counts, positivity signals, and seller type flags

  ------

  ## Gold Layer – Historical Fact Tables

  ### `gold.fact_historical_data`

  - Long-form historical time series per product (date, type, value)
  - Used for trends like price history, sales rank history, and other Keepa-style historical tracking

  ### `gold.fact_avg_stats`

  - Pre-calculated rolling/average statistics per product by window (avg, 30/90/180/365)
  - Supports smoothed trend reporting and benchmark comparisons

  ### `gold.fact_offer_history`

  - Historical offer tracking per product and seller over time
  - Used for understanding offer price changes and seller behavior trends

  ### `gold.fact_buy_box_history`

  - Buy Box winner history (which seller owned the Buy Box over time)
  - Supports churn / stability analysis of Buy Box ownership

  ### `gold.fact_coupon_history`

  - Coupon/discount history per product over time
  - Used for promotion and pricing strategy analysis

  ### `gold.fact_monthly_sold`

  - Monthly sales volume history per product
  - Supports year/month sales trend visuals (like your 2025 monthly sales chart)

  ------

  ## Gold Layer – Dimension Tables

  ### `gold.dim_products`

  - Product lookup dimension (ASIN → product_id)
  - Used to connect all facts consistently to product identity

  ### `gold.dim_brand`

  - Brand lookup dimension
  - Supports brand-level grouping and filtering

  ### `gold.dim_sellers`

  - Seller lookup dimension (seller_id + seller name + seller PID)
  - Includes added seller identity coverage (e.g., Amazon Resale entry)

  ### `gold.dim_condition`

  - Condition lookup dimension (new/used/etc.)
  - Used in offer-level and buy box analysis

  ### `gold.dim_category`

  - Category hierarchy dimension (category_id + parent_category_id relationships)
  - Supports multi-level category drill-down in Power BI

  ### `gold.dim_buy_box_availability`

  - Availability label dimension (in stock / out of stock / other)
  - Used to standardize stock status filtering in buy box visuals

  ## Gold Layer – Lookup Dimensions (Buckets / Flags)

  ### `gold.dim_price_ranges`

  - Standard price tier buckets (under 100, 100–200, …)
  - Used for price segmentation and filtering

  ### `gold.dim_rating_buckets`

  - Standard rating tiers (4.5+, 4.0–4.5, 3–4, under 3, unrated)
  - Used for quality segmentation and filtering

  ### `gold.dim_months`

  - Month lookup (month_id → month name)
  - Used for time-based visuals and readable month labeling

  ### `gold.dim_fba`

  - Fulfillment bucket dimension (FBA vs Merchant)
  - Used for fulfillment analysis slicers/segmenting

  ### `gold.dim_prime`

  - Prime flag dimension (Prime vs Non-Prime)
  - Used for Prime comparisons across dashboards

  ### `gold.dim_is_new`

  - New vs Used/Refurbished flag dimension
  - Used to segment offer/buy box behavior by newness

  ### `gold.dim_seller_type`

  - Seller type bucket (Amazon vs 3rd party)
  - Used to separate Amazon retail behavior from marketplace sellers

  ### `gold.dim_historical_types`

  - Historical metric type dictionary (type_id → metric name)
  - Used to interpret `fact_historical_data` time-series values

  ### `gold.dim_sale_comparison`

  - Sales trend classification (Increasing/Decreasing/Stable/No Data)
  - Used for trend labeling and comparison visuals

  ### `gold.dim_best_price_black_friday`

  - Best price type classification (Amazon price, Buy Box new, New price, List price, etc.)
  - Used for “best deal” / promo analysis

  ### `gold.dim_discount_level`

  - Discount intensity bucket (No discount, Small, Medium, Aggressive, Clearance)
  - Used for discount strategy segmentation



----

# Power BI Dashboard Overview:

## 1. Power BI Filters:

**Filter Characteristic:**

- All filters are built using **dimension tables** from the Gold layer
- Filters are connected to reporting visuals through **ID-based relationships**
- Changing any filter updates **all visuals and KPIs consistently**
- Filters allow users to segment data by:
  - **Categories:** Category filtering uses a **hierarchical structure** instead of a flat dimension
    - Category selections cascade across **all hierarchy levels**
  - Seller characteristics (FBA, FBM)
  - Prime eligibility
  - Condition and availability
  - Price and rating ranges



## 2. Products Tab

#### 1. **Top 10 Best Rated Sellers (Composite Score)**

**Seller Ranking – Methodology**

- Sellers are ranked using a **composite performance score**, not a single metric
- The goal is to measure **seller reliability**, not just popularity or volume

**How the Seller Ranking Is Calculated**: The ranking score is built by combining multiple seller performance signals:

- **Seller Rating Quality + Rating Volume**

  - Higher average ratings contribute more to the score
  - Reflects overall customer satisfaction

  - Sellers with more reviews are weighted higher
  - Prevents sellers with very few ratings from ranking unfairly high

- **Sales Activity**

  - Incorporates sales-related signals to represent real marketplace presence
  - Ensures inactive or low-impact sellers are not over-ranked

- **Each component is weighted so that:**

  - High ratings alone are not enough

  - High volume alone is not enough

  - Strong performance requires **both quality and consistency**

## 3. Sellers Tab

## 4. Prime Week and Competitor Analysis 
](https://app.powerbi.com/view?r=eyJrIjoiODRkZjEwYTMtOTIyZi00NTE1LTk4YWQtMDEzOWIxOTk0ZTBhIiwidCI6ImM3Y2EzYjc2LWVkYmUtNGYyNi1iZTljLTgzOWM2MjQ5ZDZiYiJ9

# Extracting Relevant data

## Data Extraction Strategy (Keepa & Rainforest)

### Overall Extraction Approach

This project uses **two complementary data sources** to build a complete and reliable view of Amazon products, sellers, pricing, and sales behavior:

- **Keepa** is used for **historical data and seller completeness**
- **Rainforest** is used for **same-day live pricing, offers, and sales signals**





## 1. Keepa API:

**Keepa provides:**

- Long-term **historical pricing and sales trends**
- More complete **seller identification**
- Reliable product-level metadata

**It is also necessary because:**

- Rainforest does **not** provide complete seller identity when Amazon wins the Buy Box
- Historical sales trends are not available from Rainforest

### Keepa Extraction Steps (Conceptual)

1. **Extract Categories**
   - Identify all target Category and and subcategories.
   - Category and subcategories we target:
     - **Computers & Accessories** (main category)
       - **Computers & Tablets**
         - Desktops
           - All-in-Ones
           - Mini PCs
           - Towers
         - Laptops
           - Traditional Laptops
         - Tablets
       - **Tablet Accessories**
2. - **Extract Product ASINs**
     - Collect ASINs for all products under the selected categories
     - We extract 200 ASIN per category
3. - **Extract Product-Level Data**
     - Pricing history
     - Ratings and review distribution
     - Historical sales indicators
4. - **Extract Seller Names from Product Data**
     - Identify sellers associated with each product from all product results
5. - **Extract Detailed Seller Metadata**
     - For each seller, retrieve complete seller-level information
     - This data later serves as the **authoritative seller reference**

### Keepa API limitations

- **KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits per hour**, preventing real-time full refreshes.

- **Same day live buy box data:** Due to token limitation, Cannot always capture:

  - **final Buy Box price** and **Recent Month's Sale**

  - **recent other offers**

  - **current Buy Box features** (e.g `Prime`, `FBA`, `Condition`)

### **List of datasets Transformed from Keepa:**

##### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



##### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                                                  | Example      |
| --------- | ------------------------------------------------------------ | ------------ |
| `asin`    | Product identifier                                           | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot                          | `2025-10-13` |
| `type_id` | Keepa historically identifier (Amazon price, new price, used price, buy box price,  lightning deal, rating, monthly sale, etc. ) | `1`          |
| `value`   | Price or metric value (scaled integer)                       | `116900`     |



##### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



##### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



##### 5. Historical Offers

**Purpose:** Captures **seller-level offer competition** over time.

| Column           | What it represents               | Example value    |
| ---------------- | -------------------------------- | ---------------- |
| `asin`           | Product ASIN                     | `B0FSL77PX2`     |
| `seller_id`      | Seller offering the product      | `A1SH4EAPSJFCZH` |
| `date`           | Offer snapshot date              | `2025-10-13`     |
| `offer_price`    | Offer price at that time         | `1169.0`         |
| `offer_quantity` | Quantity captured (if available) | `0`              |
| `condition_id`   | Condition code for the offer     | `1`              |
| `is_amazon`      | Flag if seller is Amazon         | `0`              |
| `is_fba`         | Flag if Fulfilled by Amazon      | `1`              |
| `is_prime`       | Flag if Prime-eligible           | `1`              |



##### 6. Historicl Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



##### 7. Seller Profile

**Purpose:** Static **seller identity dimension**.

| Column             | What it represents                                 | Example value   |
| ------------------ | -------------------------------------------------- | --------------- |
| `seller_id`        | Seller identifier                                  | `AKZMCWIYNER20` |
| `selling_brand`    | Brand associated with seller (from your transform) | `apple`         |
| `selling_count`    | Count of items/records tied to this seller         | `26`            |
| `avg_30_sale_rank` | Avg 30-day sales rank signal                       | `4989`          |



### 8. Seller Data

**Purpose:** Tracks **seller performance and reputation metrics**.

| Column                    | What it represents                   | Example value                        |
| ------------------------- | ------------------------------------ | ------------------------------------ |
| `seller_id`               | Seller identifier                    | `AKZMCWIYNER20`                      |
| `seller_name`             | Seller display name                  | `AKZMCWIYNER20` *(varies by seller)* |
| `current_rating_count`    | Recent/current rating count          | `93`                                 |
| `total_rating_count`      | Total rating count                   | `1187`                               |
| `New_Ownership_Rate`      | Buy Box ownership rate for New       | `12`                                 |
| `used_Ownership_Rate`     | Buy Box ownership rate for Used      | `0`                                  |
| `is_fba`                  | Whether FBA appears dominant/flagged | `1`                                  |
| `positive_rating_30_days` | Positive ratings in last 30 days     | `88`                                 |
| `positive_rating_60_days` | Positive ratings in last 60 days     | `92`                                 |
| `positive_rating_90_days` | Positive ratings in last 90 days     | `88`                                 |
| `rating_count_30_days`    | Rating volume in last 30 days        | `17`                                 |
| `rating_count_60_days`    | Rating volume in last 60 days        | `36`                                 |
| `rating_count_90_days`    | Rating volume in last 90 days        | `114`                                |



---

## 2. Rainforest Extraction Steps

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Reuse ASINs from Keepa**
   - The same ASIN list extracted from Keepa is used as input
1. **Extract Live Product Data**
   - **Current prices** and **Buy Box** information
1. **Extract All Offers per ASIN**: (Third-party sellers, Fulfillment type, Prime eligibility , etc.)
1. **Extract Recent Monthly Sales**
   - Retrieved using Rainforest search endpoints
   - Provides short-term demand signals

### **List of datasets Transformed from Keepa:**

##### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

| Column                    | What it represents                           | Example value                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `asin`                    | Product ASIN                                 | `B00I9HPIUS`                                                 |
| `title`                   | Product title                                | `Dell OptiPlex 7020 MFF Mini Business Desktop Computer, ...` |
| `brand`                   | Brand name                                   | `‎Dell`                                                       |
| `price`                   | Product price (snapshot)                     | `109.0`                                                      |
| `product_seller`          | Seller name associated with product snapshot | `GS Global Management LLC`                                   |
| `seller_id`               | Seller ID associated with product snapshot   | `A1AFLMIRO3MS2G`                                             |
| `rating`                  | Product average rating                       | `5.0`                                                        |
| `ratings_total`           | Total rating count                           | `1.0`                                                        |
| `stock_availability`      | Stock status label                           | `not_in_stock`                                               |
| `is_prime`                | Prime-eligible flag                          | `True`                                                       |
| `is_prime_exclusive_deal` | Prime-exclusive deal flag                    | `False`                                                      |
| `is_sold_by_amazon`       | Sold-by-Amazon flag                          | `False`                                                      |
| `is_fba`                  | Fulfilled-by-Amazon flag                     | `False`                                                      |
| `is_new`                  | New condition flag                           | `True`                                                       |
| `amazons_choice`          | Amazon’s Choice badge field                  | `Amazon's Choice`                                            |
| `has_coupon`              | Coupon present flag                          | `True`                                                       |
| `coupon_perc`             | Coupon text/value captured                   | `Apply $1000 coupon`                                         |
| `5_star_percentage`       | 5-star percent                               | `100.0`                                                      |
| `5_star_count`            | 5-star count                                 | `1.0`                                                        |
| `4_star_percentage`       | 4-star percent                               | `0.0`                                                        |
| `4_star_count`            | 4-star count                                 | `0.0`                                                        |
| `3_star_percentage`       | 3-star percent                               | `0.0`                                                        |
| `3_star_count`            | 3-star count                                 | `0.0`                                                        |
| `2_star_percentage`       | 2-star percent                               | `0.0`                                                        |
| `2_star_count`            | 2-star count                                 | `0.0`                                                        |
| `1_star_percentage`       | 1-star percent                               | `0.0`                                                        |
| `1_star_count`            | 1-star count                                 | `0.0`                                                        |
| `date`                    | Extraction date                              | `2026-01-13`                                                 |



##### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

| Column                               | What it represents                       | Example value              |
| ------------------------------------ | ---------------------------------------- | -------------------------- |
| `asin`                               | Product ASIN                             | `B00TREI0D4`               |
| `seller_name`                        | Offer seller name                        | `GS Global Management LLC` |
| `seller_id`                          | Offer seller ID                          | `A1AFLMIRO3MS2G`           |
| `buybox_winner`                      | Whether this offer is the Buy Box winner | `True`                     |
| `seller_rating`                      | Seller rating score                      | `4.5`                      |
| `seller_ratings_percentage_positive` | Seller % positive ratings                | `91.0`                     |
| `seller_ratings_total`               | Seller total rating count                | `98.0`                     |
| `is_new`                             | Offer is new condition flag              | `False`                    |
| `is_prime`                           | Offer is Prime-eligible flag             | `False`                    |
| `price`                              | Offer price                              | `109.0`                    |
| `condition`                          | Offer condition text                     | `Refurbished - Excellent`  |
| `is_fba`                             | Offer fulfilled by Amazon                | `False`                    |
| `is_free_shipping`                   | Offer has free shipping                  | `True`                     |



##### 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |



---

## Known Cross-Source Limitations

#### 1. Seller Identity Gaps

- When **Amazon or Amazon Resale wins the Buy Box**, `RainforestAPI`:
  - Does **not** return Amazon seller IDs
  - Only returns IDs for other sellers
- Amazon Resale seller identity is also incomplete in Keepa

**Because of this:**

- Seller identity must be **completed after extraction**
- Seller data from Keepa is used to **enrich Rainforest results**
- Amazon Resale seller IDs are **manually assigned** to ensure visibility

#### 2. ASIN & Naming Mismatches

- ASIN naming and structure differ between Keepa and Rainforest
- Direct alignment is not always possible at extraction time

**This requires:**

- Additional normalization
- Post-load reconciliation in Snowflake



---

## Transform Raw JSON files & Load to snowflake Bronze Layer Schema

- Convert **raw JSON → structured tables**
- Load into the **warehouse for analytics**
- Enables historical trend analysis and joins
  **Keywords:** ETL, normalization, warehouse-ready



---

## Data Cleaning – Key Issues (Silver Layer clean up)

1. **Main Data Cleaning:**

   - Nulls
   - Duplicates
   - Data types
   - Boolean normalization

2. **Post-Extraction Cleanup In Silver Layer**

   - **ASIN redirection:** Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
   - **Amazon seller gaps:** Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
     - **Seller backfill:** Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
   - **Duplicate products:** Redirected ASINs caused **duplicate product rows** that had to be cleaned.

   - **Product** and seller **records** are **normalized** for reporting
   - **Cross-API mismatch:** Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

   **This step ensures:**

   - Amazon retail performance is not undercounted
   - Seller-level analytics are accurate
   - Power BI dashboards reflect true marketplace structure



# Data Modeling

- ## Gold Layer – Fact Tables

  ### `gold.fact_product`

  - Main **product performance** fact table (sales, revenue-related metrics, rating metrics, ranks)
  - Includes **sales rank** and **rating rank** used in product-level dashboards

  ### `gold.fact_product_category`

  - Bridge table mapping each product to its **category levels**
  - Supports category drill-down and leaf-category analysis

  ### `gold.fact_offers`

  - Offer-level fact table for **all seller offers per product**
  - Used for seller comparisons, pricing competition, condition-based offer analysis

  ### `gold.fact_buybox_products` (VIEW)

  - Buy Box snapshot fact view per product
  - Includes buy box winner attributes (price, Prime, FBA, condition, availability) with IDs for filtering

  ### `gold.fact_sellers`

  - Seller-level performance fact table
  - Includes seller metrics like selling count, rating counts, positivity signals, and seller type flags

  ------

  ## Gold Layer – Historical Fact Tables

  ### `gold.fact_historical_data`

  - Long-form historical time series per product (date, type, value)
  - Used for trends like price history, sales rank history, and other Keepa-style historical tracking

  ### `gold.fact_avg_stats`

  - Pre-calculated rolling/average statistics per product by window (avg, 30/90/180/365)
  - Supports smoothed trend reporting and benchmark comparisons

  ### `gold.fact_offer_history`

  - Historical offer tracking per product and seller over time
  - Used for understanding offer price changes and seller behavior trends

  ### `gold.fact_buy_box_history`

  - Buy Box winner history (which seller owned the Buy Box over time)
  - Supports churn / stability analysis of Buy Box ownership

  ### `gold.fact_coupon_history`

  - Coupon/discount history per product over time
  - Used for promotion and pricing strategy analysis

  ### `gold.fact_monthly_sold`

  - Monthly sales volume history per product
  - Supports year/month sales trend visuals (like your 2025 monthly sales chart)

  ------

  ## Gold Layer – Dimension Tables

  ### `gold.dim_products`

  - Product lookup dimension (ASIN → product_id)
  - Used to connect all facts consistently to product identity

  ### `gold.dim_brand`

  - Brand lookup dimension
  - Supports brand-level grouping and filtering

  ### `gold.dim_sellers`

  - Seller lookup dimension (seller_id + seller name + seller PID)
  - Includes added seller identity coverage (e.g., Amazon Resale entry)

  ### `gold.dim_condition`

  - Condition lookup dimension (new/used/etc.)
  - Used in offer-level and buy box analysis

  ### `gold.dim_category`

  - Category hierarchy dimension (category_id + parent_category_id relationships)
  - Supports multi-level category drill-down in Power BI

  ### `gold.dim_buy_box_availability`

  - Availability label dimension (in stock / out of stock / other)
  - Used to standardize stock status filtering in buy box visuals

  ## Gold Layer – Lookup Dimensions (Buckets / Flags)

  ### `gold.dim_price_ranges`

  - Standard price tier buckets (under 100, 100–200, …)
  - Used for price segmentation and filtering

  ### `gold.dim_rating_buckets`

  - Standard rating tiers (4.5+, 4.0–4.5, 3–4, under 3, unrated)
  - Used for quality segmentation and filtering

  ### `gold.dim_months`

  - Month lookup (month_id → month name)
  - Used for time-based visuals and readable month labeling

  ### `gold.dim_fba`

  - Fulfillment bucket dimension (FBA vs Merchant)
  - Used for fulfillment analysis slicers/segmenting

  ### `gold.dim_prime`

  - Prime flag dimension (Prime vs Non-Prime)
  - Used for Prime comparisons across dashboards

  ### `gold.dim_is_new`

  - New vs Used/Refurbished flag dimension
  - Used to segment offer/buy box behavior by newness

  ### `gold.dim_seller_type`

  - Seller type bucket (Amazon vs 3rd party)
  - Used to separate Amazon retail behavior from marketplace sellers

  ### `gold.dim_historical_types`

  - Historical metric type dictionary (type_id → metric name)
  - Used to interpret `fact_historical_data` time-series values

  ### `gold.dim_sale_comparison`

  - Sales trend classification (Increasing/Decreasing/Stable/No Data)
  - Used for trend labeling and comparison visuals

  ### `gold.dim_best_price_black_friday`

  - Best price type classification (Amazon price, Buy Box new, New price, List price, etc.)
  - Used for “best deal” / promo analysis

  ### `gold.dim_discount_level`

  - Discount intensity bucket (No discount, Small, Medium, Aggressive, Clearance)
  - Used for discount strategy segmentation



----

# Power BI Dashboard Overview:

## 1. Power BI Filters:

**Filter Characteristic:**

- All filters are built using **dimension tables** from the Gold layer
- Filters are connected to reporting visuals through **ID-based relationships**
- Changing any filter updates **all visuals and KPIs consistently**
- Filters allow users to segment data by:
  - **Categories:** Category filtering uses a **hierarchical structure** instead of a flat dimension
    - Category selections cascade across **all hierarchy levels**
  - Seller characteristics (FBA, FBM)
  - Prime eligibility
  - Condition and availability
  - Price and rating ranges



## 2. Products Tab

#### 1. **Top 10 Best Rated Sellers (Composite Score)**

**Seller Ranking – Methodology**

- Sellers are ranked using a **composite performance score**, not a single metric
- The goal is to measure **seller reliability**, not just popularity or volume

**How the Seller Ranking Is Calculated**: The ranking score is built by combining multiple seller performance signals:

- **Seller Rating Quality + Rating Volume**

  - Higher average ratings contribute more to the score
  - Reflects overall customer satisfaction

  - Sellers with more reviews are weighted higher
  - Prevents sellers with very few ratings from ranking unfairly high

- **Sales Activity**

  - Incorporates sales-related signals to represent real marketplace presence
  - Ensures inactive or low-impact sellers are not over-ranked

- **Each component is weighted so that:**

  - High ratings alone are not enough

  - High volume alone is not enough

  - Strong performance requires **both quality and consistency**

## 3. Sellers Tab

## 4. Prime Week and Competitor Analysis )
](https://app.powerbi.com/view?r=eyJrIjoiODRkZjEwYTMtOTIyZi00NTE1LTk4YWQtMDEzOWIxOTk0ZTBhIiwidCI6ImM3Y2EzYjc2LWVkYmUtNGYyNi1iZTljLTgzOWM2MjQ5ZDZiYiJ9

# Data Extraction Strategy (Keepa & Rainforest)

### Overall Extraction Approach

This project uses **two complementary data sources** to build a complete and reliable view of Amazon products, sellers, pricing, and sales behavior:

- **Keepa** is used for **historical data and seller completeness**
- **Rainforest** is used for **same-day live pricing, offers, and sales signals**





## 1. Keepa API:

**Keepa provides:**

- Long-term **historical pricing and sales trends**
- More complete **seller identification**
- Reliable product-level metadata

**It is also necessary because:**

- Rainforest does **not** provide complete seller identity when Amazon wins the Buy Box
- Historical sales trends are not available from Rainforest

### Keepa Extraction Steps (Conceptual)

1. **Extract Categories**
   - Identify all target Category and and subcategories.
   - Category and subcategories we target:
     - **Computers & Accessories** (main category)
       - **Computers & Tablets**
         - Desktops
           - All-in-Ones
           - Mini PCs
           - Towers
         - Laptops
           - Traditional Laptops
         - Tablets
       - **Tablet Accessories**
2. - **Extract Product ASINs**
     - Collect ASINs for all products under the selected categories
     - We extract 200 ASIN per category
3. - **Extract Product-Level Data**
     - Pricing history
     - Ratings and review distribution
     - Historical sales indicators
4. - **Extract Seller Names from Product Data**
     - Identify sellers associated with each product from all product results
5. - **Extract Detailed Seller Metadata**
     - For each seller, retrieve complete seller-level information
     - This data later serves as the **authoritative seller reference**

### Keepa API limitations

- **KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits per hour**, preventing real-time full refreshes.

- **Same day live buy box data:** Due to token limitation, Cannot always capture:

  - **final Buy Box price** and **Recent Month's Sale**

  - **recent other offers**

  - **current Buy Box features** (e.g `Prime`, `FBA`, `Condition`)

### **List of datasets Transformed from Keepa:**

##### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



##### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                                                  | Example      |
| --------- | ------------------------------------------------------------ | ------------ |
| `asin`    | Product identifier                                           | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot                          | `2025-10-13` |
| `type_id` | Keepa historically identifier (Amazon price, new price, used price, buy box price,  lightning deal, rating, monthly sale, etc. ) | `1`          |
| `value`   | Price or metric value (scaled integer)                       | `116900`     |



##### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



##### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



##### 5. Historical Offers

**Purpose:** Captures **seller-level offer competition** over time.

| Column           | What it represents               | Example value    |
| ---------------- | -------------------------------- | ---------------- |
| `asin`           | Product ASIN                     | `B0FSL77PX2`     |
| `seller_id`      | Seller offering the product      | `A1SH4EAPSJFCZH` |
| `date`           | Offer snapshot date              | `2025-10-13`     |
| `offer_price`    | Offer price at that time         | `1169.0`         |
| `offer_quantity` | Quantity captured (if available) | `0`              |
| `condition_id`   | Condition code for the offer     | `1`              |
| `is_amazon`      | Flag if seller is Amazon         | `0`              |
| `is_fba`         | Flag if Fulfilled by Amazon      | `1`              |
| `is_prime`       | Flag if Prime-eligible           | `1`              |



##### 6. Historicl Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



##### 7. Seller Profile

**Purpose:** Static **seller identity dimension**.

| Column             | What it represents                                 | Example value   |
| ------------------ | -------------------------------------------------- | --------------- |
| `seller_id`        | Seller identifier                                  | `AKZMCWIYNER20` |
| `selling_brand`    | Brand associated with seller (from your transform) | `apple`         |
| `selling_count`    | Count of items/records tied to this seller         | `26`            |
| `avg_30_sale_rank` | Avg 30-day sales rank signal                       | `4989`          |



### 8. Seller Data

**Purpose:** Tracks **seller performance and reputation metrics**.

| Column                    | What it represents                   | Example value                        |
| ------------------------- | ------------------------------------ | ------------------------------------ |
| `seller_id`               | Seller identifier                    | `AKZMCWIYNER20`                      |
| `seller_name`             | Seller display name                  | `AKZMCWIYNER20` *(varies by seller)* |
| `current_rating_count`    | Recent/current rating count          | `93`                                 |
| `total_rating_count`      | Total rating count                   | `1187`                               |
| `New_Ownership_Rate`      | Buy Box ownership rate for New       | `12`                                 |
| `used_Ownership_Rate`     | Buy Box ownership rate for Used      | `0`                                  |
| `is_fba`                  | Whether FBA appears dominant/flagged | `1`                                  |
| `positive_rating_30_days` | Positive ratings in last 30 days     | `88`                                 |
| `positive_rating_60_days` | Positive ratings in last 60 days     | `92`                                 |
| `positive_rating_90_days` | Positive ratings in last 90 days     | `88`                                 |
| `rating_count_30_days`    | Rating volume in last 30 days        | `17`                                 |
| `rating_count_60_days`    | Rating volume in last 60 days        | `36`                                 |
| `rating_count_90_days`    | Rating volume in last 90 days        | `114`                                |



---

## 2. Rainforest Extraction Steps

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Reuse ASINs from Keepa**
   - The same ASIN list extracted from Keepa is used as input
1. **Extract Live Product Data**
   - **Current prices** and **Buy Box** information
1. **Extract All Offers per ASIN**: (Third-party sellers, Fulfillment type, Prime eligibility , etc.)
1. **Extract Recent Monthly Sales**
   - Retrieved using Rainforest search endpoints
   - Provides short-term demand signals

### **List of datasets Transformed from Keepa:**

##### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

| Column                    | What it represents                           | Example value                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `asin`                    | Product ASIN                                 | `B00I9HPIUS`                                                 |
| `title`                   | Product title                                | `Dell OptiPlex 7020 MFF Mini Business Desktop Computer, ...` |
| `brand`                   | Brand name                                   | `‎Dell`                                                       |
| `price`                   | Product price (snapshot)                     | `109.0`                                                      |
| `product_seller`          | Seller name associated with product snapshot | `GS Global Management LLC`                                   |
| `seller_id`               | Seller ID associated with product snapshot   | `A1AFLMIRO3MS2G`                                             |
| `rating`                  | Product average rating                       | `5.0`                                                        |
| `ratings_total`           | Total rating count                           | `1.0`                                                        |
| `stock_availability`      | Stock status label                           | `not_in_stock`                                               |
| `is_prime`                | Prime-eligible flag                          | `True`                                                       |
| `is_prime_exclusive_deal` | Prime-exclusive deal flag                    | `False`                                                      |
| `is_sold_by_amazon`       | Sold-by-Amazon flag                          | `False`                                                      |
| `is_fba`                  | Fulfilled-by-Amazon flag                     | `False`                                                      |
| `is_new`                  | New condition flag                           | `True`                                                       |
| `amazons_choice`          | Amazon’s Choice badge field                  | `Amazon's Choice`                                            |
| `has_coupon`              | Coupon present flag                          | `True`                                                       |
| `coupon_perc`             | Coupon text/value captured                   | `Apply $1000 coupon`                                         |
| `5_star_percentage`       | 5-star percent                               | `100.0`                                                      |
| `5_star_count`            | 5-star count                                 | `1.0`                                                        |
| `4_star_percentage`       | 4-star percent                               | `0.0`                                                        |
| `4_star_count`            | 4-star count                                 | `0.0`                                                        |
| `3_star_percentage`       | 3-star percent                               | `0.0`                                                        |
| `3_star_count`            | 3-star count                                 | `0.0`                                                        |
| `2_star_percentage`       | 2-star percent                               | `0.0`                                                        |
| `2_star_count`            | 2-star count                                 | `0.0`                                                        |
| `1_star_percentage`       | 1-star percent                               | `0.0`                                                        |
| `1_star_count`            | 1-star count                                 | `0.0`                                                        |
| `date`                    | Extraction date                              | `2026-01-13`                                                 |



##### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

| Column                               | What it represents                       | Example value              |
| ------------------------------------ | ---------------------------------------- | -------------------------- |
| `asin`                               | Product ASIN                             | `B00TREI0D4`               |
| `seller_name`                        | Offer seller name                        | `GS Global Management LLC` |
| `seller_id`                          | Offer seller ID                          | `A1AFLMIRO3MS2G`           |
| `buybox_winner`                      | Whether this offer is the Buy Box winner | `True`                     |
| `seller_rating`                      | Seller rating score                      | `4.5`                      |
| `seller_ratings_percentage_positive` | Seller % positive ratings                | `91.0`                     |
| `seller_ratings_total`               | Seller total rating count                | `98.0`                     |
| `is_new`                             | Offer is new condition flag              | `False`                    |
| `is_prime`                           | Offer is Prime-eligible flag             | `False`                    |
| `price`                              | Offer price                              | `109.0`                    |
| `condition`                          | Offer condition text                     | `Refurbished - Excellent`  |
| `is_fba`                             | Offer fulfilled by Amazon                | `False`                    |
| `is_free_shipping`                   | Offer has free shipping                  | `True`                     |



##### 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |



---

## Known Cross-Source Limitations

#### 1. Seller Identity Gaps

- When **Amazon or Amazon Resale wins the Buy Box**, `RainforestAPI`:
  - Does **not** return Amazon seller IDs
  - Only returns IDs for other sellers
- Amazon Resale seller identity is also incomplete in Keepa

**Because of this:**

- Seller identity must be **completed after extraction**
- Seller data from Keepa is used to **enrich Rainforest results**
- Amazon Resale seller IDs are **manually assigned** to ensure visibility

#### 2. ASIN & Naming Mismatches

- ASIN naming and structure differ between Keepa and Rainforest
- Direct alignment is not always possible at extraction time

**This requires:**

- Additional normalization
- Post-load reconciliation in Snowflake



---

## Transform Raw JSON files & Load to snowflake Bronze Layer Schema

- Convert **raw JSON → structured tables**
- Load into the **warehouse for analytics**
- Enables historical trend analysis and joins
  **Keywords:** ETL, normalization, warehouse-ready



---

## Data Cleaning – Key Issues (Silver Layer clean up)

1. **Main Data Cleaning:**

   - Nulls
   - Duplicates
   - Data types
   - Boolean normalization

2. **Post-Extraction Cleanup In Silver Layer**

   - **ASIN redirection:** Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
   - **Amazon seller gaps:** Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
     - **Seller backfill:** Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
   - **Duplicate products:** Redirected ASINs caused **duplicate product rows** that had to be cleaned.

   - **Product** and seller **records** are **normalized** for reporting
   - **Cross-API mismatch:** Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

   **This step ensures:**

   - Amazon retail performance is not undercounted
   - Seller-level analytics are accurate
   - Power BI dashboards reflect true marketplace structure



# Data Modeling

- ## Gold Layer – Fact Tables

  ### `gold.fact_product`

  - Main **product performance** fact table (sales, revenue-related metrics, rating metrics, ranks)
  - Includes **sales rank** and **rating rank** used in product-level dashboards

  ### `gold.fact_product_category`

  - Bridge table mapping each product to its **category levels**
  - Supports category drill-down and leaf-category analysis

  ### `gold.fact_offers`

  - Offer-level fact table for **all seller offers per product**
  - Used for seller comparisons, pricing competition, condition-based offer analysis

  ### `gold.fact_buybox_products` (VIEW)

  - Buy Box snapshot fact view per product
  - Includes buy box winner attributes (price, Prime, FBA, condition, availability) with IDs for filtering

  ### `gold.fact_sellers`

  - Seller-level performance fact table
  - Includes seller metrics like selling count, rating counts, positivity signals, and seller type flags

  ------

  ## Gold Layer – Historical Fact Tables

  ### `gold.fact_historical_data`

  - Long-form historical time series per product (date, type, value)
  - Used for trends like price history, sales rank history, and other Keepa-style historical tracking

  ### `gold.fact_avg_stats`

  - Pre-calculated rolling/average statistics per product by window (avg, 30/90/180/365)
  - Supports smoothed trend reporting and benchmark comparisons

  ### `gold.fact_offer_history`

  - Historical offer tracking per product and seller over time
  - Used for understanding offer price changes and seller behavior trends

  ### `gold.fact_buy_box_history`

  - Buy Box winner history (which seller owned the Buy Box over time)
  - Supports churn / stability analysis of Buy Box ownership

  ### `gold.fact_coupon_history`

  - Coupon/discount history per product over time
  - Used for promotion and pricing strategy analysis

  ### `gold.fact_monthly_sold`

  - Monthly sales volume history per product
  - Supports year/month sales trend visuals (like your 2025 monthly sales chart)

  ------

  ## Gold Layer – Dimension Tables

  ### `gold.dim_products`

  - Product lookup dimension (ASIN → product_id)
  - Used to connect all facts consistently to product identity

  ### `gold.dim_brand`

  - Brand lookup dimension
  - Supports brand-level grouping and filtering

  ### `gold.dim_sellers`

  - Seller lookup dimension (seller_id + seller name + seller PID)
  - Includes added seller identity coverage (e.g., Amazon Resale entry)

  ### `gold.dim_condition`

  - Condition lookup dimension (new/used/etc.)
  - Used in offer-level and buy box analysis

  ### `gold.dim_category`

  - Category hierarchy dimension (category_id + parent_category_id relationships)
  - Supports multi-level category drill-down in Power BI

  ### `gold.dim_buy_box_availability`

  - Availability label dimension (in stock / out of stock / other)
  - Used to standardize stock status filtering in buy box visuals

  ## Gold Layer – Lookup Dimensions (Buckets / Flags)

  ### `gold.dim_price_ranges`

  - Standard price tier buckets (under 100, 100–200, …)
  - Used for price segmentation and filtering

  ### `gold.dim_rating_buckets`

  - Standard rating tiers (4.5+, 4.0–4.5, 3–4, under 3, unrated)
  - Used for quality segmentation and filtering

  ### `gold.dim_months`

  - Month lookup (month_id → month name)
  - Used for time-based visuals and readable month labeling

  ### `gold.dim_fba`

  - Fulfillment bucket dimension (FBA vs Merchant)
  - Used for fulfillment analysis slicers/segmenting

  ### `gold.dim_prime`

  - Prime flag dimension (Prime vs Non-Prime)
  - Used for Prime comparisons across dashboards

  ### `gold.dim_is_new`

  - New vs Used/Refurbished flag dimension
  - Used to segment offer/buy box behavior by newness

  ### `gold.dim_seller_type`

  - Seller type bucket (Amazon vs 3rd party)
  - Used to separate Amazon retail behavior from marketplace sellers

  ### `gold.dim_historical_types`

  - Historical metric type dictionary (type_id → metric name)
  - Used to interpret `fact_historical_data` time-series values

  ### `gold.dim_sale_comparison`

  - Sales trend classification (Increasing/Decreasing/Stable/No Data)
  - Used for trend labeling and comparison visuals

  ### `gold.dim_best_price_black_friday`

  - Best price type classification (Amazon price, Buy Box new, New price, List price, etc.)
  - Used for “best deal” / promo analysis

  ### `gold.dim_discount_level`

  - Discount intensity bucket (No discount, Small, Medium, Aggressive, Clearance)
  - Used for discount strategy segmentation



----

# Power BI Dashboard Overview:

## 1. Power BI Filters:

**Filter Characteristic:**

- All filters are built using **dimension tables** from the Gold layer
- Filters are connected to reporting visuals through **ID-based relationships**
- Changing any filter updates **all visuals and KPIs consistently**
- Filters allow users to segment data by:
  - **Categories:** Category filtering uses a **hierarchical structure** instead of a flat dimension
    - Category selections cascade across **all hierarchy levels**
  - Seller characteristics (FBA, FBM)
  - Prime eligibility
  - Condition and availability
  - Price and rating ranges



## 2. Products Tab

### 1. **Top 10 Best Rated Sellers (Composite Score)**

**Seller Ranking – Methodology**

- Sellers are ranked using a **composite performance score**, not a single metric
- The goal is to measure **seller reliability**, not just popularity or volume

**How the Seller Ranking Is Calculated**: The ranking score is built by combining multiple seller performance signals:

- **Seller Rating Quality + Rating Volume**

  - Higher average ratings contribute more to the score
  - Reflects overall customer satisfaction

  - Sellers with more reviews are weighted higher
  - Prevents sellers with very few ratings from ranking unfairly high

- **Sales Activity**

  - Incorporates sales-related signals to represent real marketplace presence
  - Ensures inactive or low-impact sellers are not over-ranked

- **Each component is weighted so that:**

  - High ratings alone are not enough

  - High volume alone is not enough

  - Strong performance requires **both quality and consistency**

## 3. Sellers Tab

## 4. Prime Week and Competitor Analysis )
](https://app.powerbi.com/view?r=eyJrIjoiODRkZjEwYTMtOTIyZi00NTE1LTk4YWQtMDEzOWIxOTk0ZTBhIiwidCI6ImM3Y2EzYjc2LWVkYmUtNGYyNi1iZTljLTgzOWM2MjQ5ZDZiYiJ9

# Data Extraction Strategy (Keepa & Rainforest)

### Overall Extraction Approach

This project uses **two complementary data sources** to build a complete and reliable view of Amazon products, sellers, pricing, and sales behavior:

- **Keepa** is used for **historical data and seller completeness**
- **Rainforest** is used for **same-day live pricing, offers, and sales signals**

---

## 1. Keepa API:

**Keepa provides:**

- Long-term **historical pricing and sales trends**
- More complete **seller identification**
- Reliable product-level metadata

**It is also necessary because:**

- Rainforest does **not** provide complete seller identity when Amazon wins the Buy Box
- Historical sales trends are not available from Rainforest

### Keepa Extraction Steps (Conceptual)

1. **Extract Categories**
   - Identify all target Category and and subcategories.
   - Category and subcategories we target:
     - **Computers & Accessories** (main category)
       - **Computers & Tablets**
         - Desktops
           - All-in-Ones
           - Mini PCs
           - Towers
         - Laptops
           - Traditional Laptops
         - Tablets
       - **Tablet Accessories**
2. - **Extract Product ASINs**
     - Collect ASINs for all products under the selected categories
     - We extract 200 ASIN per category
3. - **Extract Product-Level Data**
     - Pricing history
     - Ratings and review distribution
     - Historical sales indicators
4. - **Extract Seller Names from Product Data**
     - Identify sellers associated with each product from all product results
5. - **Extract Detailed Seller Metadata**
     - For each seller, retrieve complete seller-level information
     - This data later serves as the **authoritative seller reference**

### Keepa API limitations

- **KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits per hour**, preventing real-time full refreshes.

- **Same day live buy box data:** Due to token limitation, Cannot always capture:

  - **final Buy Box price** and **Recent Month's Sale**

  - **recent other offers**

  - **current Buy Box features** (e.g `Prime`, `FBA`, `Condition`)


### **List of datasets Transformed from Keepa:**

##### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



##### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                                                  | Example      |
| --------- | ------------------------------------------------------------ | ------------ |
| `asin`    | Product identifier                                           | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot                          | `2025-10-13` |
| `type_id` | Keepa historically identifier (Amazon price, new price, used price, buy box price,  lightning deal, rating, monthly sale, etc. ) | `1`          |
| `value`   | Price or metric value (scaled integer)                       | `116900`     |



##### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



##### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



##### 5. Historical Offers

**Purpose:** Captures **seller-level offer competition** over time.

| Column           | What it represents               | Example value    |
| ---------------- | -------------------------------- | ---------------- |
| `asin`           | Product ASIN                     | `B0FSL77PX2`     |
| `seller_id`      | Seller offering the product      | `A1SH4EAPSJFCZH` |
| `date`           | Offer snapshot date              | `2025-10-13`     |
| `offer_price`    | Offer price at that time         | `1169.0`         |
| `offer_quantity` | Quantity captured (if available) | `0`              |
| `condition_id`   | Condition code for the offer     | `1`              |
| `is_amazon`      | Flag if seller is Amazon         | `0`              |
| `is_fba`         | Flag if Fulfilled by Amazon      | `1`              |
| `is_prime`       | Flag if Prime-eligible           | `1`              |



##### 6. Historicl Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



##### 7. Seller Profile

**Purpose:** Static **seller identity dimension**.

| Column             | What it represents                                 | Example value   |
| ------------------ | -------------------------------------------------- | --------------- |
| `seller_id`        | Seller identifier                                  | `AKZMCWIYNER20` |
| `selling_brand`    | Brand associated with seller (from your transform) | `apple`         |
| `selling_count`    | Count of items/records tied to this seller         | `26`            |
| `avg_30_sale_rank` | Avg 30-day sales rank signal                       | `4989`          |



### 8. Seller Data

**Purpose:** Tracks **seller performance and reputation metrics**.

| Column                    | What it represents                   | Example value                        |
| ------------------------- | ------------------------------------ | ------------------------------------ |
| `seller_id`               | Seller identifier                    | `AKZMCWIYNER20`                      |
| `seller_name`             | Seller display name                  | `AKZMCWIYNER20` *(varies by seller)* |
| `current_rating_count`    | Recent/current rating count          | `93`                                 |
| `total_rating_count`      | Total rating count                   | `1187`                               |
| `New_Ownership_Rate`      | Buy Box ownership rate for New       | `12`                                 |
| `used_Ownership_Rate`     | Buy Box ownership rate for Used      | `0`                                  |
| `is_fba`                  | Whether FBA appears dominant/flagged | `1`                                  |
| `positive_rating_30_days` | Positive ratings in last 30 days     | `88`                                 |
| `positive_rating_60_days` | Positive ratings in last 60 days     | `92`                                 |
| `positive_rating_90_days` | Positive ratings in last 90 days     | `88`                                 |
| `rating_count_30_days`    | Rating volume in last 30 days        | `17`                                 |
| `rating_count_60_days`    | Rating volume in last 60 days        | `36`                                 |
| `rating_count_90_days`    | Rating volume in last 90 days        | `114`                                |



---

# 2. Rainforest Extraction Steps

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Reuse ASINs from Keepa**
   - The same ASIN list extracted from Keepa is used as input
1. **Extract Live Product Data**
   - **Current prices** and **Buy Box** information
1. **Extract All Offers per ASIN**: (Third-party sellers, Fulfillment type, Prime eligibility , etc.)
1. **Extract Recent Monthly Sales**
   - Retrieved using Rainforest search endpoints
   - Provides short-term demand signals

### **List of datasets Transformed from Keepa:**

##### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

| Column                    | What it represents                           | Example value                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `asin`                    | Product ASIN                                 | `B00I9HPIUS`                                                 |
| `title`                   | Product title                                | `Dell OptiPlex 7020 MFF Mini Business Desktop Computer, ...` |
| `brand`                   | Brand name                                   | `‎Dell`                                                       |
| `price`                   | Product price (snapshot)                     | `109.0`                                                      |
| `product_seller`          | Seller name associated with product snapshot | `GS Global Management LLC`                                   |
| `seller_id`               | Seller ID associated with product snapshot   | `A1AFLMIRO3MS2G`                                             |
| `rating`                  | Product average rating                       | `5.0`                                                        |
| `ratings_total`           | Total rating count                           | `1.0`                                                        |
| `stock_availability`      | Stock status label                           | `not_in_stock`                                               |
| `is_prime`                | Prime-eligible flag                          | `True`                                                       |
| `is_prime_exclusive_deal` | Prime-exclusive deal flag                    | `False`                                                      |
| `is_sold_by_amazon`       | Sold-by-Amazon flag                          | `False`                                                      |
| `is_fba`                  | Fulfilled-by-Amazon flag                     | `False`                                                      |
| `is_new`                  | New condition flag                           | `True`                                                       |
| `amazons_choice`          | Amazon’s Choice badge field                  | `Amazon's Choice`                                            |
| `has_coupon`              | Coupon present flag                          | `True`                                                       |
| `coupon_perc`             | Coupon text/value captured                   | `Apply $1000 coupon`                                         |
| `5_star_percentage`       | 5-star percent                               | `100.0`                                                      |
| `5_star_count`            | 5-star count                                 | `1.0`                                                        |
| `4_star_percentage`       | 4-star percent                               | `0.0`                                                        |
| `4_star_count`            | 4-star count                                 | `0.0`                                                        |
| `3_star_percentage`       | 3-star percent                               | `0.0`                                                        |
| `3_star_count`            | 3-star count                                 | `0.0`                                                        |
| `2_star_percentage`       | 2-star percent                               | `0.0`                                                        |
| `2_star_count`            | 2-star count                                 | `0.0`                                                        |
| `1_star_percentage`       | 1-star percent                               | `0.0`                                                        |
| `1_star_count`            | 1-star count                                 | `0.0`                                                        |
| `date`                    | Extraction date                              | `2026-01-13`                                                 |



##### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

| Column                               | What it represents                       | Example value              |
| ------------------------------------ | ---------------------------------------- | -------------------------- |
| `asin`                               | Product ASIN                             | `B00TREI0D4`               |
| `seller_name`                        | Offer seller name                        | `GS Global Management LLC` |
| `seller_id`                          | Offer seller ID                          | `A1AFLMIRO3MS2G`           |
| `buybox_winner`                      | Whether this offer is the Buy Box winner | `True`                     |
| `seller_rating`                      | Seller rating score                      | `4.5`                      |
| `seller_ratings_percentage_positive` | Seller % positive ratings                | `91.0`                     |
| `seller_ratings_total`               | Seller total rating count                | `98.0`                     |
| `is_new`                             | Offer is new condition flag              | `False`                    |
| `is_prime`                           | Offer is Prime-eligible flag             | `False`                    |
| `price`                              | Offer price                              | `109.0`                    |
| `condition`                          | Offer condition text                     | `Refurbished - Excellent`  |
| `is_fba`                             | Offer fulfilled by Amazon                | `False`                    |
| `is_free_shipping`                   | Offer has free shipping                  | `True`                     |



##### 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |



---

# Known Cross-Source Limitations

#### 1. Seller Identity Gaps

- When **Amazon or Amazon Resale wins the Buy Box**, `RainforestAPI`:
  - Does **not** return Amazon seller IDs
  - Only returns IDs for other sellers
- Amazon Resale seller identity is also incomplete in Keepa

**Because of this:**

- Seller identity must be **completed after extraction**
- Seller data from Keepa is used to **enrich Rainforest results**
- Amazon Resale seller IDs are **manually assigned** to ensure visibility

#### 2. ASIN & Naming Mismatches

- ASIN naming and structure differ between Keepa and Rainforest
- Direct alignment is not always possible at extraction time

**This requires:**

- Additional normalization
- Post-load reconciliation in Snowflake



---

# Transform Raw JSON files & Load to snowflake Bronze Layer Schema

- Convert **raw JSON → structured tables**
- Load into the **warehouse for analytics**
- Enables historical trend analysis and joins
  **Keywords:** ETL, normalization, warehouse-ready



---

# Data Cleaning – Key Issues (Silver Layer clean up)

1. **Main Data Cleaning:**

   - Nulls
   - Duplicates
   - Data types
   - Boolean normalization

2. **Post-Extraction Cleanup In Silver Layer**

   - **ASIN redirection:** Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
   - **Amazon seller gaps:** Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
     - **Seller backfill:** Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
   - **Duplicate products:** Redirected ASINs caused **duplicate product rows** that had to be cleaned.

   - **Product** and seller **records** are **normalized** for reporting
   - **Cross-API mismatch:** Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

   **This step ensures:**

   - Amazon retail performance is not undercounted
   - Seller-level analytics are accurate
   - Power BI dashboards reflect true marketplace structure

---

# Data Modeling

### 1. Gold Layer – Fact Tables

#### `gold.fact_product`

- Main **product performance** fact table (sales, revenue-related metrics, rating metrics, ranks)
- Includes **sales rank** and **rating rank** used in product-level dashboards

#### `gold.fact_product_category`

- Bridge table mapping each product to its **category levels**
- Supports category drill-down and leaf-category analysis

#### `gold.fact_offers`

- Offer-level fact table for **all seller offers per product**
- Used for seller comparisons, pricing competition, condition-based offer analysis

#### `gold.fact_buybox_products` (VIEW)

- Buy Box snapshot fact view per product
- Includes buy box winner attributes (price, Prime, FBA, condition, availability) with IDs for filtering

#### `gold.fact_sellers`

- Seller-level performance fact table
- Includes seller metrics like selling count, rating counts, positivity signals, and seller type flags

------

### 2. Gold Layer – Historical Fact Tables

#### `gold.fact_historical_data`

- Long-form historical time series per product (date, type, value)
- Used for trends like price history, sales rank history, and other Keepa-style historical tracking

#### `gold.fact_avg_stats`

- Pre-calculated rolling/average statistics per product by window (avg, 30/90/180/365)
- Supports smoothed trend reporting and benchmark comparisons

#### `gold.fact_offer_history`

- Historical offer tracking per product and seller over time
- Used for understanding offer price changes and seller behavior trends

#### `gold.fact_buy_box_history`

- Buy Box winner history (which seller owned the Buy Box over time)
- Supports churn / stability analysis of Buy Box ownership

#### `gold.fact_coupon_history`

- Coupon/discount history per product over time
- Used for promotion and pricing strategy analysis

#### `gold.fact_monthly_sold`

- Monthly sales volume history per product
- Supports year/month sales trend visuals (like your 2025 monthly sales chart)

------

## 3. Gold Layer – Dimension Tables

### `gold.dim_products`

- Product lookup dimension (ASIN → product_id)
- Used to connect all facts consistently to product identity

### `gold.dim_brand`

- Brand lookup dimension
- Supports brand-level grouping and filtering

### `gold.dim_sellers`

- Seller lookup dimension (seller_id + seller name + seller PID)
- Includes added seller identity coverage (e.g., Amazon Resale entry)

### `gold.dim_condition`

- Condition lookup dimension (new/used/etc.)
- Used in offer-level and buy box analysis

### `gold.dim_category`

- Category hierarchy dimension (category_id + parent_category_id relationships)
- Supports multi-level category drill-down in Power BI

### `gold.dim_buy_box_availability`

- Availability label dimension (in stock / out of stock / other)
- Used to standardize stock status filtering in buy box visuals

---

## 4. Gold Layer – Lookup Dimensions (Buckets / Flags)

### `gold.dim_price_ranges`

- Standard price tier buckets (under 100, 100–200, …)
- Used for price segmentation and filtering

### `gold.dim_rating_buckets`

- Standard rating tiers (4.5+, 4.0–4.5, 3–4, under 3, unrated)
- Used for quality segmentation and filtering

### `gold.dim_months`

- Month lookup (month_id → month name)
- Used for time-based visuals and readable month labeling

### `gold.dim_fba`

- Fulfillment bucket dimension (FBA vs Merchant)
- Used for fulfillment analysis slicers/segmenting

### `gold.dim_prime`

- Prime flag dimension (Prime vs Non-Prime)
- Used for Prime comparisons across dashboards

### `gold.dim_is_new`

- New vs Used/Refurbished flag dimension
- Used to segment offer/buy box behavior by newness

### `gold.dim_seller_type`

- Seller type bucket (Amazon vs 3rd party)
- Used to separate Amazon retail behavior from marketplace sellers

### `gold.dim_historical_types`

- Historical metric type dictionary (type_id → metric name)
- Used to interpret `fact_historical_data` time-series values

### `gold.dim_sale_comparison`

- Sales trend classification (Increasing/Decreasing/Stable/No Data)
- Used for trend labeling and comparison visuals

### `gold.dim_best_price_black_friday`

- Best price type classification (Amazon price, Buy Box new, New price, List price, etc.)
- Used for “best deal” / promo analysis

### `gold.dim_discount_level`

- Discount intensity bucket (No discount, Small, Medium, Aggressive, Clearance)
- Used for discount strategy segmentation



----

# Power BI Dashboard Overview

## 1. Power BI Filters

### Filter Characteristics

- All filters are built using **Gold-layer dimension tables**
- Filters are connected to visuals using **ID-based relationships**
- Any filter selection updates **all KPIs and visuals consistently**
- Filters support segmentation by:
  - **Categories**
    - Implemented as a **hierarchical structure**, not a flat dimension
    - Selections cascade across **all category levels**
  - Seller fulfillment type (FBA / FBM)
  - Prime eligibility
  - Product condition and availability
  - Price ranges and rating ranges

------

## 2. Products Tab

### 2.1 Main Product KPI Cards

The main KPI cards summarize the overall product landscape:

1. Total number of products
2. Total recent-month sales
3. Total recent-month revenue
4. Total number of brands

All KPIs are fully filter-responsive.

------

### 2.2 Top Products per Category (Weighted Ranking)

- Identifies **top product(s) within each category**
- Uses a **weighted ranking score**, not raw star ratings
- Ranking combines:
  - Rating quality
  - Recent-month sales (log-scaled to reduce extreme volume bias)
  - Star distribution weighting (5★ highest → 1★ lowest)
- Power BI displays only **Top-ranked products per category**
- Conditional formatting highlights:
  - Revenue contribution
  - Relative rating strength

------

### 2.3 Top Selling vs Rating Rank

- Ranks products by **recent-month sales**
- Displays product **rating and rating rank** alongside sales rank
- Highlights that **top-selling products are not always top-rated**
- Data bars and color scaling expose mismatches between volume and quality

------

### 2.4 Pareto (80/20) Revenue Concentration

- Applies Pareto analysis to product revenue
- Includes:
  - **Two KPI cards** showing revenue share of top 20% vs bottom 80% of products
  - **Pareto chart** showing cumulative revenue contribution
- Identifies the **“vital few” products** driving most revenue

------

### 2.5 2025 Monthly Sales & Revenue Trend

- Uses **Keepa historical sales data**
- Displays monthly:
  - Total units sold
  - Total revenue
- Reveals pricing mix behavior:
  - High sales volume with low revenue → lower-priced products dominate
  - Lower sales volume with high revenue → higher-priced products dominate

------

## 3. Sellers Tab

### 3.1 Seller KPI Cards

- Total number of sellers (Amazon vs third-party)
- Current **top-rated seller**, including number of listings
  - Rated using a **composite score**:
    - Rating quality
    - Review volume
    - Recent positivity (30/60/90 days)
    - Total listings
- Seller with the **highest number of active products**

------

### 3.2 Top 10 Best Rated Sellers (Composite Score)

- Sellers are ranked using a **composite performance score**
- Score components:
  1. **Rating quality**
     - Positive ratings in last **30 / 60 / 90 days**
     - Most weight given to recent 30 days (0.5 / 0.3 / 0.2)
  2. **Rating volume**
     - Log-scaled number of reviews
  3. **Sales activity**
     - Log-scaled seller sales volume
- Prevents sellers with:
  - Few reviews
  - Low activity
     from ranking unfairly high
- Conditional coloring highlights how ranking depends on **all three signals**
- Key insight:
  - High star rating alone ≠ best seller
  - High positive percentage alone ≠ reliable seller

------

### 3.3 Top 5 Selling Sellers vs Positive Rating %

- Bar chart comparing:
  - Recent-month sales volume
  - Positive review percentage
- Highlights sellers with strong sales but weak satisfaction (and vice versa)

------

### 3.4 2025 Amazon vs Third-Party Seller Comparison

- Uses **Keepa historical data**
- Compares monthly count of Amazon vs third-party sellers during 2025
- Key insight:
  - In most months, **third-party sellers outnumber Amazon sellers**

------

### 3.5 Product Features & Seller Type (Donut Charts)

- Prime vs non-Prime seller distribution
- FBA vs merchant-fulfilled distribution
- New vs non-new product offerings

------

## 4. Prime Week & Competitive Analysis

### 4.1 Prime Week Price Comparison (Black Friday & Cyber Monday)

- Compares current prices with:
  - Black Friday prices
  - Cyber Monday prices
- Conditional coloring highlights:
  - Higher
  - Equal
  - Lower prices vs historical deals
- Key insights:
  - Not all products were discounted during Prime Week
  - Some current prices outperform Prime Week deals

------

### 4.2 Prime Week Discount Levels

- Distribution of discount intensity:
  - Aggressive
  - Medium
  - Small
  - No discount
- Key insight:
  - Majority of discounted products were **aggressively discounted (>40%)**

------

### 4.3 Prime Week Discount by Price Tier

- Shows discounted products by price range
- Key insight:
  - Most discounted products were priced **under $100**

------

### 4.4 Price Comparison & Discount Strategy – KPIs

- Best discounted product (Hot Deal)
- Discount percentage and discount amount
- Distribution of:
  - Over-priced products
  - Competitively priced products
- Average discount metrics

------

### 4.5 Competitive Pricing Gaps (vs Market Offers)

- Evaluates pricing using **multiple signals**:
  1. Historical average product price
  2. Other Buy Box offers
  3. Lowest marketplace offers
  4. External market prices (e.g., eBay)
  5. Recent sales decline signals
- Calculates an overall **pricing gap score**
- Applies **price-tier–aware discount strategy**:
  - Conservative discounts for low-priced items
  - Larger adjustments for higher-priced products
- Produces a final **recommended discount percentage**
- Balances:
  - Competitiveness
  - Revenue protection
  - Buy Box recovery

------

### 4.6 Discount Level Distribution

- Shows suggested discount intensity per product
- Key insight:
  - Many over-priced products required **no discount**
  - A smaller subset required **aggressive adjustments**

------

### 4.7 Discount Price Tier Distribution

- Shows over-priced products by price range
- Key insight:
  - Most over-priced products were priced **above $1,000**

------)
](https://app.powerbi.com/view?r=eyJrIjoiODRkZjEwYTMtOTIyZi00NTE1LTk4YWQtMDEzOWIxOTk0ZTBhIiwidCI6ImM3Y2EzYjc2LWVkYmUtNGYyNi1iZTljLTgzOWM2MjQ5ZDZiYiJ9

# Data Extraction Strategy (Keepa & Rainforest)

### Overall Extraction Approach

This project uses **two complementary data sources** to build a complete and reliable view of Amazon products, sellers, pricing, and sales behavior:

- **Keepa** is used for **historical data and seller completeness**
- **Rainforest** is used for **same-day live pricing, offers, and sales signals**

---

## 1. Keepa API:

**Keepa provides:**

- Long-term **historical pricing and sales trends**
- More complete **seller identification**
- Reliable product-level metadata

**It is also necessary because:**

- Rainforest does **not** provide complete seller identity when Amazon wins the Buy Box
- Historical sales trends are not available from Rainforest

### Keepa Extraction Steps (Conceptual)

1. **Extract Categories**
   - Identify all target Category and and subcategories.
   - Category and subcategories we target:
     - **Computers & Accessories** (main category)
       - **Computers & Tablets**
         - Desktops
           - All-in-Ones
           - Mini PCs
           - Towers
         - Laptops
           - Traditional Laptops
         - Tablets
       - **Tablet Accessories**
2. - **Extract Product ASINs**
     - Collect ASINs for all products under the selected categories
     - We extract 200 ASIN per category
3. - **Extract Product-Level Data**
     - Pricing history
     - Ratings and review distribution
     - Historical sales indicators
4. - **Extract Seller Names from Product Data**
     - Identify sellers associated with each product from all product results
5. - **Extract Detailed Seller Metadata**
     - For each seller, retrieve complete seller-level information
     - This data later serves as the **authoritative seller reference**

### Keepa API limitations

- **KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits per hour**, preventing real-time full refreshes.

- **Same day live buy box data:** Due to token limitation, Cannot always capture:

  - **final Buy Box price** and **Recent Month's Sale**

  - **recent other offers**

  - **current Buy Box features** (e.g `Prime`, `FBA`, `Condition`)


### **List of datasets Transformed from Keepa:**

##### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



##### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                                                  | Example      |
| --------- | ------------------------------------------------------------ | ------------ |
| `asin`    | Product identifier                                           | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot                          | `2025-10-13` |
| `type_id` | Keepa historically identifier (Amazon price, new price, used price, buy box price,  lightning deal, rating, monthly sale, etc. ) | `1`          |
| `value`   | Price or metric value (scaled integer)                       | `116900`     |



##### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



##### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



##### 5. Historical Offers

**Purpose:** Captures **seller-level offer competition** over time.

| Column           | What it represents               | Example value    |
| ---------------- | -------------------------------- | ---------------- |
| `asin`           | Product ASIN                     | `B0FSL77PX2`     |
| `seller_id`      | Seller offering the product      | `A1SH4EAPSJFCZH` |
| `date`           | Offer snapshot date              | `2025-10-13`     |
| `offer_price`    | Offer price at that time         | `1169.0`         |
| `offer_quantity` | Quantity captured (if available) | `0`              |
| `condition_id`   | Condition code for the offer     | `1`              |
| `is_amazon`      | Flag if seller is Amazon         | `0`              |
| `is_fba`         | Flag if Fulfilled by Amazon      | `1`              |
| `is_prime`       | Flag if Prime-eligible           | `1`              |



##### 6. Historicl Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



##### 7. Seller Profile

**Purpose:** Static **seller identity dimension**.

| Column             | What it represents                                 | Example value   |
| ------------------ | -------------------------------------------------- | --------------- |
| `seller_id`        | Seller identifier                                  | `AKZMCWIYNER20` |
| `selling_brand`    | Brand associated with seller (from your transform) | `apple`         |
| `selling_count`    | Count of items/records tied to this seller         | `26`            |
| `avg_30_sale_rank` | Avg 30-day sales rank signal                       | `4989`          |



### 8. Seller Data

**Purpose:** Tracks **seller performance and reputation metrics**.

| Column                    | What it represents                   | Example value                        |
| ------------------------- | ------------------------------------ | ------------------------------------ |
| `seller_id`               | Seller identifier                    | `AKZMCWIYNER20`                      |
| `seller_name`             | Seller display name                  | `AKZMCWIYNER20` *(varies by seller)* |
| `current_rating_count`    | Recent/current rating count          | `93`                                 |
| `total_rating_count`      | Total rating count                   | `1187`                               |
| `New_Ownership_Rate`      | Buy Box ownership rate for New       | `12`                                 |
| `used_Ownership_Rate`     | Buy Box ownership rate for Used      | `0`                                  |
| `is_fba`                  | Whether FBA appears dominant/flagged | `1`                                  |
| `positive_rating_30_days` | Positive ratings in last 30 days     | `88`                                 |
| `positive_rating_60_days` | Positive ratings in last 60 days     | `92`                                 |
| `positive_rating_90_days` | Positive ratings in last 90 days     | `88`                                 |
| `rating_count_30_days`    | Rating volume in last 30 days        | `17`                                 |
| `rating_count_60_days`    | Rating volume in last 60 days        | `36`                                 |
| `rating_count_90_days`    | Rating volume in last 90 days        | `114`                                |



---

# 2. Rainforest Extraction Steps

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Reuse ASINs from Keepa**
   - The same ASIN list extracted from Keepa is used as input
1. **Extract Live Product Data**
   - **Current prices** and **Buy Box** information
1. **Extract All Offers per ASIN**: (Third-party sellers, Fulfillment type, Prime eligibility , etc.)
1. **Extract Recent Monthly Sales**
   - Retrieved using Rainforest search endpoints
   - Provides short-term demand signals

### **List of datasets Transformed from Keepa:**

##### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

| Column                    | What it represents                           | Example value                                                |
| ------------------------- | -------------------------------------------- | ------------------------------------------------------------ |
| `asin`                    | Product ASIN                                 | `B00I9HPIUS`                                                 |
| `title`                   | Product title                                | `Dell OptiPlex 7020 MFF Mini Business Desktop Computer, ...` |
| `brand`                   | Brand name                                   | `‎Dell`                                                       |
| `price`                   | Product price (snapshot)                     | `109.0`                                                      |
| `product_seller`          | Seller name associated with product snapshot | `GS Global Management LLC`                                   |
| `seller_id`               | Seller ID associated with product snapshot   | `A1AFLMIRO3MS2G`                                             |
| `rating`                  | Product average rating                       | `5.0`                                                        |
| `ratings_total`           | Total rating count                           | `1.0`                                                        |
| `stock_availability`      | Stock status label                           | `not_in_stock`                                               |
| `is_prime`                | Prime-eligible flag                          | `True`                                                       |
| `is_prime_exclusive_deal` | Prime-exclusive deal flag                    | `False`                                                      |
| `is_sold_by_amazon`       | Sold-by-Amazon flag                          | `False`                                                      |
| `is_fba`                  | Fulfilled-by-Amazon flag                     | `False`                                                      |
| `is_new`                  | New condition flag                           | `True`                                                       |
| `amazons_choice`          | Amazon’s Choice badge field                  | `Amazon's Choice`                                            |
| `has_coupon`              | Coupon present flag                          | `True`                                                       |
| `coupon_perc`             | Coupon text/value captured                   | `Apply $1000 coupon`                                         |
| `5_star_percentage`       | 5-star percent                               | `100.0`                                                      |
| `5_star_count`            | 5-star count                                 | `1.0`                                                        |
| `4_star_percentage`       | 4-star percent                               | `0.0`                                                        |
| `4_star_count`            | 4-star count                                 | `0.0`                                                        |
| `3_star_percentage`       | 3-star percent                               | `0.0`                                                        |
| `3_star_count`            | 3-star count                                 | `0.0`                                                        |
| `2_star_percentage`       | 2-star percent                               | `0.0`                                                        |
| `2_star_count`            | 2-star count                                 | `0.0`                                                        |
| `1_star_percentage`       | 1-star percent                               | `0.0`                                                        |
| `1_star_count`            | 1-star count                                 | `0.0`                                                        |
| `date`                    | Extraction date                              | `2026-01-13`                                                 |



##### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

| Column                               | What it represents                       | Example value              |
| ------------------------------------ | ---------------------------------------- | -------------------------- |
| `asin`                               | Product ASIN                             | `B00TREI0D4`               |
| `seller_name`                        | Offer seller name                        | `GS Global Management LLC` |
| `seller_id`                          | Offer seller ID                          | `A1AFLMIRO3MS2G`           |
| `buybox_winner`                      | Whether this offer is the Buy Box winner | `True`                     |
| `seller_rating`                      | Seller rating score                      | `4.5`                      |
| `seller_ratings_percentage_positive` | Seller % positive ratings                | `91.0`                     |
| `seller_ratings_total`               | Seller total rating count                | `98.0`                     |
| `is_new`                             | Offer is new condition flag              | `False`                    |
| `is_prime`                           | Offer is Prime-eligible flag             | `False`                    |
| `price`                              | Offer price                              | `109.0`                    |
| `condition`                          | Offer condition text                     | `Refurbished - Excellent`  |
| `is_fba`                             | Offer fulfilled by Amazon                | `False`                    |
| `is_free_shipping`                   | Offer has free shipping                  | `True`                     |



##### 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |



---

# Known Cross-Source Limitations

#### 1. Seller Identity Gaps

- When **Amazon or Amazon Resale wins the Buy Box**, `RainforestAPI`:
  - Does **not** return Amazon seller IDs
  - Only returns IDs for other sellers
- Amazon Resale seller identity is also incomplete in Keepa

**Because of this:**

- Seller identity must be **completed after extraction**
- Seller data from Keepa is used to **enrich Rainforest results**
- Amazon Resale seller IDs are **manually assigned** to ensure visibility

#### 2. ASIN & Naming Mismatches

- ASIN naming and structure differ between Keepa and Rainforest
- Direct alignment is not always possible at extraction time

**This requires:**

- Additional normalization
- Post-load reconciliation in Snowflake



---

# Transform Raw JSON files & Load to snowflake Bronze Layer Schema

- Convert **raw JSON → structured tables**
- Load into the **warehouse for analytics**
- Enables historical trend analysis and joins
  **Keywords:** ETL, normalization, warehouse-ready



---

# Data Cleaning – Key Issues (Silver Layer clean up)

1. **Main Data Cleaning:**

   - Nulls
   - Duplicates
   - Data types
   - Boolean normalization

2. **Post-Extraction Cleanup In Silver Layer**

   - **ASIN redirection:** Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
   - **Amazon seller gaps:** Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
     - **Seller backfill:** Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
   - **Duplicate products:** Redirected ASINs caused **duplicate product rows** that had to be cleaned.

   - **Product** and seller **records** are **normalized** for reporting
   - **Cross-API mismatch:** Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

   **This step ensures:**

   - Amazon retail performance is not undercounted
   - Seller-level analytics are accurate
   - Power BI dashboards reflect true marketplace structure

---

# Data Modeling

### 1. Gold Layer – Fact Tables

#### `gold.fact_product`

- Main **product performance** fact table (sales, revenue-related metrics, rating metrics, ranks)
- Includes **sales rank** and **rating rank** used in product-level dashboards

#### `gold.fact_product_category`

- Bridge table mapping each product to its **category levels**
- Supports category drill-down and leaf-category analysis

#### `gold.fact_offers`

- Offer-level fact table for **all seller offers per product**
- Used for seller comparisons, pricing competition, condition-based offer analysis

#### `gold.fact_buybox_products` (VIEW)

- Buy Box snapshot fact view per product
- Includes buy box winner attributes (price, Prime, FBA, condition, availability) with IDs for filtering

#### `gold.fact_sellers`

- Seller-level performance fact table
- Includes seller metrics like selling count, rating counts, positivity signals, and seller type flags

------

### 2. Gold Layer – Historical Fact Tables

#### `gold.fact_historical_data`

- Long-form historical time series per product (date, type, value)
- Used for trends like price history, sales rank history, and other Keepa-style historical tracking

#### `gold.fact_avg_stats`

- Pre-calculated rolling/average statistics per product by window (avg, 30/90/180/365)
- Supports smoothed trend reporting and benchmark comparisons

#### `gold.fact_offer_history`

- Historical offer tracking per product and seller over time
- Used for understanding offer price changes and seller behavior trends

#### `gold.fact_buy_box_history`

- Buy Box winner history (which seller owned the Buy Box over time)
- Supports churn / stability analysis of Buy Box ownership

#### `gold.fact_coupon_history`

- Coupon/discount history per product over time
- Used for promotion and pricing strategy analysis

#### `gold.fact_monthly_sold`

- Monthly sales volume history per product
- Supports year/month sales trend visuals (like your 2025 monthly sales chart)

------

## 3. Gold Layer – Dimension Tables

### `gold.dim_products`

- Product lookup dimension (ASIN → product_id)
- Used to connect all facts consistently to product identity

### `gold.dim_brand`

- Brand lookup dimension
- Supports brand-level grouping and filtering

### `gold.dim_sellers`

- Seller lookup dimension (seller_id + seller name + seller PID)
- Includes added seller identity coverage (e.g., Amazon Resale entry)

### `gold.dim_condition`

- Condition lookup dimension (new/used/etc.)
- Used in offer-level and buy box analysis

### `gold.dim_category`

- Category hierarchy dimension (category_id + parent_category_id relationships)
- Supports multi-level category drill-down in Power BI

### `gold.dim_buy_box_availability`

- Availability label dimension (in stock / out of stock / other)
- Used to standardize stock status filtering in buy box visuals

---

## 4. Gold Layer – Lookup Dimensions (Buckets / Flags)

### `gold.dim_price_ranges`

- Standard price tier buckets (under 100, 100–200, …)
- Used for price segmentation and filtering

### `gold.dim_rating_buckets`

- Standard rating tiers (4.5+, 4.0–4.5, 3–4, under 3, unrated)
- Used for quality segmentation and filtering

### `gold.dim_months`

- Month lookup (month_id → month name)
- Used for time-based visuals and readable month labeling

### `gold.dim_fba`

- Fulfillment bucket dimension (FBA vs Merchant)
- Used for fulfillment analysis slicers/segmenting

### `gold.dim_prime`

- Prime flag dimension (Prime vs Non-Prime)
- Used for Prime comparisons across dashboards

### `gold.dim_is_new`

- New vs Used/Refurbished flag dimension
- Used to segment offer/buy box behavior by newness

### `gold.dim_seller_type`

- Seller type bucket (Amazon vs 3rd party)
- Used to separate Amazon retail behavior from marketplace sellers

### `gold.dim_historical_types`

- Historical metric type dictionary (type_id → metric name)
- Used to interpret `fact_historical_data` time-series values

### `gold.dim_sale_comparison`

- Sales trend classification (Increasing/Decreasing/Stable/No Data)
- Used for trend labeling and comparison visuals

### `gold.dim_best_price_black_friday`

- Best price type classification (Amazon price, Buy Box new, New price, List price, etc.)
- Used for “best deal” / promo analysis

### `gold.dim_discount_level`

- Discount intensity bucket (No discount, Small, Medium, Aggressive, Clearance)
- Used for discount strategy segmentation

----

# Power BI Dashboard Overview

## 1. Power BI Filters

### Filter Characteristics

- All filters are built using **Gold-layer dimension tables**
- Filters are connected to visuals using **ID-based relationships**
- Any filter selection updates **all KPIs and visuals consistently**
- Filters support segmentation by:
  - **Categories**
    - Implemented as a **hierarchical structure**, not a flat dimension
    - Selections cascade across **all category levels**
  - Seller fulfillment type (FBA / FBM)
  - Prime eligibility
  - Product condition and availability
  - Price ranges and rating ranges
<img width="287" height="869" alt="Screenshot 2026-01-24 at 12 27 58 AM" src="https://github.com/user-attachments/assets/4a9bc473-495a-4322-84da-4506bd2b6721" />

------

## 2. Products Tab

### 2.1 Main Product KPI Cards

The main KPI cards summarize the overall product landscape:

1. Total number of products
2. Total recent-month sales
3. Total recent-month revenue
4. Total number of brands

All KPIs are fully filter-responsive.
<img width="856" height="184" alt="Screenshot 2026-01-24 at 12 05 14 AM" src="https://github.com/user-attachments/assets/e15b65ec-ec84-4fe9-ac41-6a05bc489c1b" />

------

### 2.2 Top Rated Products per Category (Weighted Ranking)

- Identifies **top product(s) within each category**
- Uses a **weighted ranking score**, not raw star ratings
- Ranking combines:
  - Rating quality
  - Recent-month sales (log-scaled to reduce extreme volume bias)
  - Star distribution weighting (5★ highest → 1★ lowest)
- Power BI displays only **Top-ranked products per category**
- Conditional formatting highlights:
  - Revenue contribution
  - Relative rating strength
<img width="476" height="396" alt="Screenshot 2026-01-24 at 12 04 11 AM" src="https://github.com/user-attachments/assets/a51c4aec-0e64-4819-984a-f996570bf96d" />

------

### 2.3 Top Selling vs Rating Rank

- Ranks products by **recent-month sales**
- Displays product **rating and rating rank** alongside sales rank
- Highlights that **top-selling products are not always top-rated**
- Data bars and color scaling expose mismatches between volume and quality
<img width="476" height="394" alt="Screenshot 2026-01-24 at 12 04 54 AM" src="https://github.com/user-attachments/assets/c8a52ce9-75d3-4083-bb0e-1a52ba5746ae" />

------

### 2.4 Pareto (80/20) Revenue Concentration

- Applies Pareto analysis to product revenue
- Includes:
  - **Two KPI cards** showing revenue share of top 20% vs bottom 80% of products
  - **Pareto chart** showing cumulative revenue contribution
- Identifies the **“vital few” products** driving most revenue
<img width="401" height="205" alt="Screenshot 2026-01-24 at 12 05 03 AM" src="https://github.com/user-attachments/assets/a3da4a26-f55b-4726-b7ab-42cd0d564513" />
<img width="782" height="396" alt="Screenshot 2026-01-24 at 12 04 32 AM" src="https://github.com/user-attachments/assets/96d9cc27-c3e1-4953-8468-0f34a0c91d2a" />

------

### 2.5 2025 Monthly Sales & Revenue Trend

- Uses **Keepa historical sales data**
- Displays monthly:
  - Total units sold
  - Total revenue
- Reveals pricing mix behavior:
  - High sales volume with low revenue → lower-priced products dominate
  - Lower sales volume with high revenue → higher-priced products dominate
<img width="779" height="396" alt="Screenshot 2026-01-24 at 12 04 40 AM" src="https://github.com/user-attachments/assets/7f45b243-7b1c-4f42-906d-d11c886e8ec3" />

------

## 3. Sellers Tab

### 3.1 Seller KPI Cards

- Total number of sellers (Amazon vs third-party)
- Current **top-rated seller**, including number of listings
  - Rated using a **composite score**:
    - Rating quality
    - Review volume
    - Recent positivity (30/60/90 days)
    - Total listings
- Seller with the **highest number of active products**
<img width="633" height="184" alt="Screenshot 2026-01-24 at 12 05 31 AM" src="https://github.com/user-attachments/assets/9bf9dcbd-34d5-4000-ac46-c8f74786d6c2" />

------

### 3.2 Top 10 Best Rated Sellers (Composite Score)

- Sellers are ranked using a **composite performance score**
- Score components:
  1. **Rating quality**
     - Positive ratings in last **30 / 60 / 90 days**
     - Most weight given to recent 30 days (0.5 / 0.3 / 0.2)
  2. **Rating volume**
     - Log-scaled number of reviews
  3. **Sales activity**
     - Log-scaled seller sales volume
- Prevents sellers with:
  - Few reviews
  - Low activity
    from ranking unfairly high
- Conditional coloring highlights how ranking depends on **all three signals**
- Key insight:
  - High star rating alone ≠ best seller
  - High positive percentage alone ≠ reliable seller
<img width="637" height="387" alt="Screenshot 2026-01-24 at 12 05 37 AM" src="https://github.com/user-attachments/assets/c6fde663-775a-4b77-bc29-b4b2ce197216" />

------

### 3.3 Top 5 Selling Sellers vs Positive Rating %

- Bar chart comparing:
  - Recent-month sales volume
  - Positive review percentage
- Highlights sellers with strong sales but weak satisfaction (and vice versa)
<img width="637" height="386" alt="Screenshot 2026-01-24 at 12 05 49 AM" src="https://github.com/user-attachments/assets/15295058-86d7-4a1c-891b-81aa18e32962" />

------

### 3.4 2025 Amazon vs Third-Party Seller Comparison

- Uses **Keepa historical data**
- Compares monthly count of Amazon vs third-party sellers during 2025
- Key insight:
  - In most months, **third-party sellers outnumber Amazon sellers**
<img width="644" height="386" alt="Screenshot 2026-01-24 at 12 05 56 AM" src="https://github.com/user-attachments/assets/38438315-c46b-4e34-ac3f-015310561513" />

------

### 3.5 Product Features & Seller Type (Donut Charts)

- Prime vs non-Prime seller distribution
- FBA vs merchant-fulfilled distribution
- New vs non-new product offerings
<img width="638" height="581" alt="Screenshot 2026-01-24 at 12 06 04 AM" src="https://github.com/user-attachments/assets/a6bf0df6-f1c7-4da5-9166-8d7d7d8c8adf" />

------

## 4. Prime Week & Competitive Analysis

### 4.1 Prime Week Price Comparison (Black Friday & Cyber Monday)
- Compares current prices with:
  - Black Friday prices
  - Cyber Monday prices
- Conditional coloring highlights:
  - Higher
  - Equal
  - Lower prices vs historical deals
- Key insights:
  - Not all products were discounted during Prime Week
  - Some current prices outperform Prime Week deals
<img width="636" height="581" alt="Screenshot 2026-01-24 at 12 06 31 AM" src="https://github.com/user-attachments/assets/bff3664d-df93-4ddf-8e5c-82433e10ef60" />

------

### 4.2 Prime Week Discount Levels and Price Tier
- Distribution of discount intensity (Discount Levels):
  - Aggressive
  - Medium
  - Small
  - No discount
  - **Key insight:**
  -    Majority of discounted products were **aggressively discounted (>40%)**
- Prime Week Product Price Tier:
   - Shows discounted products by price range
   - **Key insight:**
     - Most discounted products were priced **under $100**
<img width="636" height="385" alt="Screenshot 2026-01-24 at 12 06 41 AM" src="https://github.com/user-attachments/assets/934489ba-5e76-4c5b-9f7b-98e45a8fc5d0" />

------

### 4.3 Price Comparison & Discount Strategy – KPIs
- Best discounted product (Hot Deal)
- Discount percentage and discount amount
- Distribution of:
  - Over-priced products
  - Competitively priced products
- Average discount metrics
<img width="638" height="184" alt="Screenshot 2026-01-24 at 12 06 24 AM" src="https://github.com/user-attachments/assets/658d52c4-ba11-444e-bdcc-0fb2d6d262de" />

------

### 4.5 Competitive Pricing Gaps & Discount Recommendation (vs Market Offers)
- Evaluates pricing using **multiple signals**:
  1. Historical average product price
  2. Other Buy Box offers
  3. Lowest marketplace offers
  4. External market prices (e.g., eBay)
  5. Recent sales decline signals
- Calculates an overall **pricing gap score**
- Applies **price-tier–aware discount strategy**:
  - Conservative discounts for low-priced items
  - Larger adjustments for higher-priced products
- Produces a final **recommended discount percentage**
- Balances:
  - Competitiveness
  - Revenue protection
  - Buy Box recovery
<img width="638" height="382" alt="Screenshot 2026-01-24 at 12 06 17 AM" src="https://github.com/user-attachments/assets/fcb2a7ae-a3a5-4a1a-a9d6-64c9923ce42b" />

------

### 4.6 Discount Level and Price Tier Distribution:
- Discount Level:
   - Shows suggested discount intensity per product
   - Key insight:
     - Many over-priced products required **no discount**
     - A smaller subset required **aggressive adjustments**
- Price Tier:
   - Shows over-priced products by price range
   - Key insight:
     - Most over-priced products were priced **above $1,000**
<img width="639" height="385" alt="Screenshot 2026-01-24 at 12 06 48 AM" src="https://github.com/user-attachments/assets/77686ba6-ff28-45e2-9e05-94dd92555e06" />

------
