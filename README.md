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

### 1. Fact Tables

1. `fact_product`
   - Central fact table containing **product-level performance metrics**
   - Stores sales, revenue, pricing, rating signals, and time-based measures
   - Connects to all dimensions using IDs
   - Drives **all KPIs and core visuals**

### `dim_product`

- Stores product identifiers and descriptive attributes
- Used to display product names and group metrics by product

------

### `dim_provider` (Seller / Fulfillment)

- Unified seller and fulfillment reference
- Used for:
  - Amazon vs third-party analysis
  - Seller-level filtering and comparison

------

### `dim_category`

- Stores category hierarchy data
- Used to build **multi-level category drill-downs** in Power BI
- Not a flat dimension due to parent–child relationships

------

### `dim_prime`

- Identifies Prime eligibility
- Enables Prime vs non-Prime comparisons across visuals

------

### `dim_condition`

- Describes product condition (new, used, etc.)
- Used for pricing and rating analysis by condition

------

### `dim_rating_range`

- Groups products into rating buckets
- Supports quality-based filtering and segmentation

------

### `dim_price_range`

- Categorizes products into price tiers
- Used for price-based analysis and comparisons

------

### `dim_stock_availability`

- Indicates product availability status
- Used to analyze sales and revenue impact of availability

------

## 

----

# Power BI Dashboard Overview:

## 1. Power BI Filters:

**Filter Characteristic:**

- All filters are built using **dimension tables** from the Gold layer
- Filters are connected to reporting visuals through **ID-based relationships**
- Changing any filter updates **all visuals and KPIs consistently**
- Filters allow users to segment data by:
  - Product attributes
  - Seller characteristics
  - Prime eligibility
  - Condition and availability
  - Price and rating ranges

Main Filters:

1. Categories: Category filtering uses a **hierarchical structure** instead of a flat dimension
   1. Categories Dimention 

- Category filtering uses a **hierarchical structure** instead of a flat dimension
- Category selections cascade across **all hierarchy levels**
- Filters are designed to:
  - Narrow analysis scope
  - Compare segments
  - Validate KPI changes in real time

## 2. Products Tab

## 3. Sellers Tab

## 4. Prime Week and Competitor Analysis 
