# Extracting Relevant data

### 1. Keepa:

#### **Automated ETL Workflow:** 

1. **Category Expansion**
   - Extract **all sub-categories** under **Computers & Accessories**
   - Uses Keepa **`Category` endpoint**
   - Purpose: ensure **full category coverage** before product extraction
      **Keywords:** Category hierarchy, taxonomy, coverage
2. **ASIN Discovery**
   - Extract **~200 ASINs per sub-category**
   - Uses **`Product Finder` endpoint**
   - Ensures **broad and balanced product sampling**
      **Keywords:** ASIN sampling, scale, breadth
3. **Product-Level Extraction**
   - Pull **full product metadata per ASIN**
   - Uses **`Product` endpoint**
   - Includes pricing, ratings, offers, buy box signals
      **Keywords:** Product snapshot, metadata
4. **Seller Data Extraction**
   - Extract **seller IDs** from all product JSON responses
   - Consolidate seller IDs into a **single reference sheet**
   - Query **`Seller` endpoint** for seller attributes (`sid`, `name`, etc.)
   - Enables **seller-level analytics** across products
      **Keywords:** Seller dimension, normalization
5. **Transformation & Load**
   - Convert **raw JSON → structured tables**
   - Load into the **warehouse for analytics**
   - Enables historical trend analysis and joins
      **Keywords:** ETL, normalization, warehouse-ready

**KEEPA's token limitations:**  Keepa enforces **strict token-based rate limits**, preventing real-time full refreshes.

#### **Token Cost per Product (11 Tokens Total)**

- **1** → General product request
- **+6** → Offers (up to 10 offers per page)
- **+1** → Rating
- **+2** → Stock
- **+1** → Buy Box

### **Why Same-Day “True Latest” Data Is Not Possible**

- Minimum subscription allows **1,200 tokens per hour**
- Token regeneration rate: **1 token per minute**
- Each product requires **11 tokens**
- Result: **1 product every ~11 minutes**
- Makes it **impossible to refresh all products daily or hourly**

**Impact:**

- Cannot always capture **final Buy Box price** and **Recent Month's Sale**
- Cannot always capture **recent other offers**
- Cannot always capture **current Buy Box features**
  - `Prime`
  - `FBA`
  - `Condition`

### **List of datasets Transformed from Keepa:**

### 1. Categories

**Purpose:** Maps each ASIN to its full Amazon category hierarchy.

| Column               | Description                               | Example                                                     |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| `asin`               | Amazon product identifier                 | `B0FSL77PX2`                                                |
| `category_tree_path` | Full category hierarchy from root to leaf | `Electronics, Computers & Accessories, Computers & Tablets` |
| `category_name`      | Category name at this hierarchy level     | `Computers & Accessories`                                   |
| `category_level`     | Depth level in category tree (1 = root)   | `2`                                                         |



### 2. Historical Data

**Purpose:** Core time-series table storing **all historical price types** using Keepa type codes.

| Column    | Description                            | Example      |
| --------- | -------------------------------------- | ------------ |
| `asin`    | Product identifier                     | `B0FSL77PX2` |
| `date`    | Date of the recorded price snapshot    | `2025-10-13` |
| `type_id` | Keepa price type identifier (1–30+)    | `1`          |
| `value`   | Price or metric value (scaled integer) | `116900`     |

**`type_id` values represent historically for the same product:**

1. Amazon price, 
2. new price, 
3. used price,
4. buy box, 
5. lightning deal, 
6. etc.



### 3. Historical Buy Box

**Purpose:** Tracks **Buy Box ownership changes** over time.

| Column         | Description                      | Example          |
| -------------- | -------------------------------- | ---------------- |
| `asin`         | Product identifier               | `B0FSL77PX2`     |
| `selling_date` | Date Buy Box seller was recorded | `2025-10-13`     |
| `seller_id`    | Seller who owned the Buy Box     | `A1PA6795UKMFR9` |



### 4. Historical Monthly Sold

**Purpose:** Tracks **estimated monthly sales volume trends**.

| Column         | Description                    | Example      |
| -------------- | ------------------------------ | ------------ |
| `asin`         | Product identifier             | `B0FSL77PX2` |
| `date`         | Date of estimate               | `2025-10-13` |
| `monthly_sold` | Estimated units sold per month | `450`        |



### 5. Historical Offers

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



### 6. Historical Stats

**Purpose:** Stores **aggregated product reputation and engagement metrics**.

| Column       | What it represents                 | Example value |
| ------------ | ---------------------------------- | ------------- |
| `asin`       | Product ASIN                       | `B0FSL77PX2`  |
| `type_id`    | Keepa metric type being aggregated | `0`           |
| `avg_window` | Aggregation window label           | `avg`         |
| `value`      | Aggregated value                   | `-1`          |



### 7. Seller Profile

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

## 2. Rainforest — Extracting Relevant Data

### Automated ETL Workflow (Rainforest)

**Goal:** Use Rainforest to capture the **final, “static” snapshot** of **product** + **buy box** + **offers** + **recent sales** for the full product set (since Keepa can’t refresh everything same-day).

1. **Product extraction (ASIN-based)**
   1. Pull **Product** details for ASINs originally discovered via Keepa category workflow
   2. Endpoint: **`product`**
       **Keywords:** product snapshot, static attributes, buy box fields

1. **Offer extraction (per product)**
   1. Pull **all offers** for each ASIN
   2. Endpoint: **`offers`**
       **Keywords:** seller competition, multi-offer market, buy box winner

1. **Recent month sale extraction**
   1. Pull **recent_month_sale / recent_sales** per ASIN
   2. Endpoint: **`search`** (your workflow)
       **Keywords:** demand signal, sales velocity, “recent month”

1. **Transform & Load**



## **List of datasets Transformed from Keepa:**

### 1) `products.csv` — Rainforest Product Snapshot (1498 rows, 28 cols)

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



### 2) `offers.csv` — Rainforest Offer Competition (4362 rows, 13 cols)

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



## 3) `recent_sales.csv` — Recent Month Sales Signal (1150 rows, 2 cols)

| Column         | What it represents              | Example value |
| -------------- | ------------------------------- | ------------- |
| `asin`         | Product ASIN                    | `B00TREI0D4`  |
| `recent_sales` | Recent month sales signal/value | `200`         |





## Data Extraction Key takeaway:

- **Hybrid extraction strategy:**
   Combined **Keepa** for deep **historical time-series** data with **Rainforest** for **same-day, full-catalog snapshots**.
- **API-aware design:**
   Extraction logic was **built around API constraints** (token limits, rate throttling), not against them.
- **Category-driven coverage:**
   Started from **leaf categories** to ensure **complete and unbiased ASIN coverage**.
- **ASIN-centric pipeline:**
   All downstream extraction (products, offers, sales, sellers) was driven by a **single ASIN universe**.
- **Separation of concerns:**
  - Keepa → **historical trends & signals**
  - Rainforest → **final buy-box, live offers, recent sales**
- **Data completeness safeguards:**
   Missing **recent sales** from Rainforest were **backfilled using Keepa** when extracted within the same month.
- **Analytics-ready output:**
   Raw JSON responses were transformed into **fact- and dimension-ready tables** for warehouse analytics.
- **Scalable by design:**
   The workflow supports **thousands of products** without relying on real-time scraping.



## Data Cleaning – Key Issues (Silver Layer)

- **ASIN redirection:**
   Rainforest sometimes redirects Keepa ASINs to another ASIN within the same category, requiring **deduplication**.
- **Duplicate products:**
   Redirected ASINs caused **duplicate product rows** that had to be cleaned.
- **Amazon seller gaps:**
   Rainforest does not consistently provide **Amazon seller name or ID** (Amazon Retail / Resale).
- **Seller backfill:**
   Missing Amazon seller data was **enriched from Keepa** in the Silver layer.
- **Cross-API mismatch:**
   Differences between Keepa and Rainforest required **additional normalization logic** beyond standard cleaning.

---

# Medalian Architecture on Snowflake

## 1. Bronze Layer

- **Raw landing**: transformed + **uncleaned** data from **Keepa + RainforestAPI**

## 2. Silver Layer (Data Cleaning)

- **Nulls**
- **Duplicates**
- **Data types**
- **Boolean normalization**
- **Extra API cleaning**
  - **ASIN alignment** (Keepa ↔ Rainforest)
  - **ASIN redirection dedup**
  - **Amazon seller fixes** (Amazon / Amazon Resale name + ID, Amazon.com PID)

------

## Extra Cleaning Example (ASIN Alignment)

```sql
CREATE OR REPLACE TABLE amazon_data_db.silver.recent_sales AS
    SELECT 
        TRIM("asin") AS "asin", 
        "recent_sales"
    FROM amazon_data_db.bronze.recent_sales
    WHERE "asin" IN (
        SELECT DISTINCT "asin" 
        FROM amazon_data_db.bronze.static
    );
```

- **Final SELECT**: keeps only Rainforest recent_sales where ASIN exists in Keepa ASIN universe (`bronze.static`)

------

## Example: Step by step cleaning and preparing `silver.products` Silver layer

```sql
CREATE OR REPLACE TABLE amazon_data_db.silver.products AS
    WITH fill_null AS (
        SELECT 
            *, 
            CASE 
                WHEN "stock_availability" = 'in_stock' THEN 'In stock'
                WHEN "stock_availability" = 'not_in_stock' THEN 'Out of stock'
                ELSE 'Unknown'
            END AS "stock_availability_flag"
        FROM amazon_data_db.bronze.products
        WHERE "asin" IN (
            SELECT DISTINCT "asin" 
            FROM amazon_data_db.bronze.static
            )
    ),
    updated_product_sellers AS (
        SELECT 
            p."asin",
            CASE 
                WHEN p."product_seller" = 'Amazon' THEN 'ATVPDKIKX0DER'
                WHEN p."product_seller" = 'Amazon Resale' THEN 'A0001TVPMAZON'
                ELSE p."seller_id"
            END AS "seller_id",
            CASE 
                WHEN p."product_seller" = 'Amazon' THEN 'Amazon.com'
                ELSE p."product_seller"
            END AS "product_seller",
            p.* EXCLUDE ("asin", "seller_id", "product_seller")
        FROM fill_null AS p
    ),
    products_clean AS ( 
    SELECT 
        "asin", 
        "brand",
        "seller_id",
        "product_seller" AS "seller_name",
        REPLACE("stock_availability_flag", '_', ' ') AS "stock_availability",
        TO_DATE("date") AS "final_date",
        "rating", "ratings_total","price", 
        IFF(TRIM(LOWER("is_prime")) = 'true', 1, 0) AS "is_prime",
        IFF(TRIM(LOWER("is_fba")) = 'true', 1, 0) AS "is_fba",
        IFF(TRIM(LOWER("is_new")) = 'true', 1, 0) AS "is_new",
        IFF(TRIM(LOWER("is_sold_by_amazon")) = 'true', 1, 0) AS "is_amazon",
        "5_star_count", "5_star_percentage" / 100 AS "5_star_prct",
        "4_star_count", "4_star_percentage" / 100 AS "4_star_prct",
        "3_star_count", "3_star_percentage" / 100 AS "3_star_prct",
        "2_star_count", "2_star_percentage" / 100 AS "2_star_prct",
        "1_star_count", "1_star_percentage" / 100 AS "1_star_prct"
    FROM updated_product_sellers
    ),
    -- Find Duplicated ASINs
    duplicate_asins AS (
        SELECT 
            "asin",
            COUNT(*) AS duplicate_count
        FROM products_clean
        GROUP BY "asin"
        HAVING COUNT(*) > 1
    ),
    -- Deduplicate only those ASINs that are present in offers as buybox winners
    dedup_shared_in_offers AS (
        SELECT 
            p.*
        FROM products_clean p
        JOIN amazon_data_db.silver.offers o 
            ON p."asin" = o."asin"
            AND p."seller_name" = o."seller_name"
            AND o."is_buybox_winner" = 1
        WHERE p."asin" IN (SELECT "asin" FROM duplicate_asins)
    ),
    -- Exclude ASINs that are duplicated but not present in offers
    exclude_asins AS (
        SELECT * 
        FROM products_clean
        WHERE "asin" NOT IN (SELECT "asin" FROM duplicate_asins)
    )
    -- Merge dedup_shared_in_offers and exclude_asins
    SELECT * FROM dedup_shared_in_offers
    UNION ALL
    SELECT * FROM exclude_asins;
```

- **fill_null**: normalizes stock availability + filters to Keepa ASIN universe
- **updated_product_sellers**: fixes **Amazon / Amazon Resale** seller IDs + Amazon.com seller name
- **products_clean**: selects clean columns + normalizes booleans + star % to fractions + final date
- **duplicate_asins**: identifies duplicated ASINs after cleaning
- **dedup_shared_in_offers**: keeps only duplicate ASIN rows that match **Buy Box winner** in offers
- **exclude_asins**: keeps all non-duplicated ASIN rows
- **Final SELECT**: merges deduped duplicates + normal rows

------

# Seller inconsistancy fix

## `seller_data`

```sql
CREATE OR REPLACE VIEW amazon_data_db.silver.seller_data AS
    WITH distinct_seller_id_name AS (
        SELECT 
            DISTINCT "seller_id", 
            "seller_name"
        FROM amazon_data_db.bronze.offers
    ),
    add_name AS (
    SELECT 
        sd."seller_id",
        CASE 
            WHEN sn."seller_name" IS NOT NULL AND sd."seller_name" = sn."seller_name"  THEN sn."seller_name"
            WHEN sn."seller_name" IS NOT NULL AND sn."seller_name" <> sd."seller_name" THEN sn."seller_name"
            ELSE sd."seller_name"
        END AS "seller_name",
        sd.* EXCLUDE("seller_id", "seller_name")
    FROM amazon_data_db.bronze.seller_data AS sd
    LEFT JOIN distinct_seller_id_name AS sn
        ON sd."seller_id" = sn."seller_id"
    )
```

- **distinct_seller_id_name**: builds seller_id ↔ seller_name pairs from offers
- **add_name**: overwrites/standardizes seller_name using offers mapping when available

------

## `offers` (Amazon seller_id fill)

```
CREATE OR REPLACE TABLE amazon_data_db.silver.offers AS
    -- CTE 1: Get Amazon Seller_ID from seller_data
    WITH amazon_seller AS (
        SELECT 
            "seller_id", 
            "seller_name"
        FROM amazon_data_db.bronze.seller_data
        WHERE "seller_name" = 'Amazon.com'
        GROUP BY "seller_id", "seller_name"
    ),
    -- CTE 2: Update offers table with correct Amazon Seller Names
    updated_offers AS (
        SELECT 
            o."asin",
            CASE 
                WHEN o."seller_id" IS NULL AND a."seller_name" IS NOT NULL THEN a."seller_id"
                WHEN o."seller_id" IS NULL AND a."seller_name" IS NULL AND o."seller_name" LIKE '%Amazon%' THEN 'A01DKIAMAZON'
                ELSE o."seller_id"
            END AS "seller_id",
            o.* EXCLUDE ("asin", "seller_id")
        FROM amazon_data_db.bronze.offers AS o
        LEFT JOIN amazon_seller AS a
            ON o."seller_name" = a."seller_name"
    )
    -- CLEAN
    SELECT
        "asin", 
        "seller_id",
        "seller_name",  
        "price",
        IFF(TRIM(LOWER("buybox_winner")) = 'true', 1, 0) AS "is_buybox_winner", 
        "seller_rating",
        "seller_ratings_total", 
        "seller_ratings_percentage_positive" / 100 AS "seller_positive_prct",
        "condition",
        IFF(TRIM(LOWER("is_fba")) = 'true', 1, 0) AS "is_fba", 
        IFF(TRIM(LOWER("is_new")) = 'true', 1, 0) AS "is_new", 
        IFF(TRIM(LOWER("is_prime")) = 'true', 1, 0) AS "is_prime", 
        IFF(TRIM(LOWER("is_free_shipping")) = 'true', 1, 0) AS "is_free_shipping"
    FROM updated_offers
    WHERE "asin" IN (
        SELECT DISTINCT "asin" 
        FROM amazon_data_db.bronze.static
    );
```

- **amazon_seller**: pulls Amazon.com seller_id from seller reference
- **updated_offers**: fills NULL Amazon seller_id (or assigns custom Amazon PID)
- **Final SELECT**: normalizes flags + filters to Keepa ASIN universe

------

# Preparing Dimention and Fact Tables Examples

## Gold Dimensions / Gold Facts

## 1) `dim_sellers`

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.dim_sellers AS
    WITH distinct_sellers AS (
        SELECT "seller_id" AS "seller_pid", "seller_name"
        FROM amazon_data_db.silver.seller_data
        WHERE "seller_id" IS NOT NULL
        GROUP BY "seller_id", "seller_name"
    )
    SELECT 
        ROW_NUMBER() OVER(ORDER BY "seller_pid") AS "seller_id",
        "seller_name",
        "seller_pid"
    FROM distinct_sellers;
-- ADD AMAZON RESALE SELLER FROM silver Offer that we manually added it's ID (PID Here)
INSERT INTO amazon_data_db.gold.dim_sellers ("seller_id", "seller_name", "seller_pid")
    SELECT
        (SELECT MAX("seller_id") + 1 FROM amazon_data_db.gold.dim_sellers),
        'Amazon Resale',
        (SELECT "seller_id" FROM amazon_data_db.silver.offers WHERE "seller_name" = 'Amazon Resale' LIMIT 1);
```

- **distinct_sellers**: creates unique seller_pid + seller_name set for the dimension
- **Final SELECT**: assigns surrogate seller_id via ROW_NUMBER()

------

## 2) Category Buildup (`dim_category`)

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.dim_category AS
    WITH category_and_parents AS (
        SELECT 
            "asin",
            "category_name",
            ifnull(LAG("category_name") OVER(PARTITION BY "asin" ORDER BY "category_level"), 'root') AS "parent_category"
        FROM amazon_data_db.silver.categories
        )
        -- CTE 2: Get Unique categories from all category names and category parent names
        ,distict_categories AS (
            SELECT DISTINCT "category_name" 
            FROM category_and_parents
            UNION 
            SELECT DISTINCT "parent_category" AS "category_name"
            FROM category_and_parents    
        )
        -- CTE 3: Assign unique IDs to all of the category names we created in CTE2
        ,cat_id AS (
        SELECT 
            ROW_NUMBER() OVER(ORDER BY "category_name" ASC) AS "category_id",
            "category_name"
        FROM distict_categories
        ),
        -- CTE 4 (Optional): Assign 0 to root category_id
        final_cat_id AS (
        SELECT
            CASE WHEN "category_name" = 'root' THEN 0 ELSE "category_id" END AS "category_id",
            "category_name"
        FROM cat_id
        ),
        cat_par AS (
            SELECT DISTINCT "category_name", "parent_category", COUNT(*)
            FROM category_and_parents
            GROUP BY "category_name", "parent_category"
        )
        SELECT
            c1."category_name", 
            c2."category_name" AS "parent_category_name",
            c1."category_id", 
            c2."category_id" AS "parent_category_id"

        FROM cat_par AS  c 
        JOIN final_cat_id AS c1 ON c1."category_name" = c."category_name"
        JOIN final_cat_id AS c2 ON c2."category_name" = c."parent_category"
        ORDER BY c2."category_id" ASC;
```

- **category_and_parents**: derives parent category per ASIN using LAG() (root default)
- **distict_categories**: unions unique category names + parent category names
- **cat_id**: assigns IDs to every category_name
- **final_cat_id**: forces root category_id = 0
- **cat_par**: builds distinct category ↔ parent relationships
- **Final SELECT**: outputs category_id + parent_category_id mapping

------

## 3) **Fact Products** (`fact_product`)

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.fact_product AS
    -- Build Recent Month Sale Table
    WITH all_recent_sales AS(
        SELECT 
            p1."asin", 
            IFNULL(r."recent_sales", 0) AS "recent_sales", 
            IFNULL(p2."recent_month_sales", 0) AS "recent_month_sale"
        FROM amazon_data_db.silver.products AS p1
        LEFT JOIN amazon_data_db.silver.recent_sales as r USING("asin")
        LEFT JOIN amazon_data_db.silver.static AS p2 USING("asin")
    ),
    rebuild_recent_sales AS (
        SELECT
            dp."product_id",        
            CASE 
                WHEN rs."recent_sales" = 0 THEN rs."recent_month_sale"
                ELSE rs."recent_sales"
            END AS "recent_month_sale"
        FROM all_recent_sales AS rs
        JOIN amazon_data_db.gold.dim_products AS dp USING("asin")
    ),
    -- Build Product Base Table
    product_max_level AS (
        SELECT "product_id", MAX("category_level") AS "max_category"
        FROM amazon_data_db.gold.fact_product_category
        GROUP BY "product_id"
    )
    ,product_leaf_level AS (
        SELECT "product_id", "category_id" AS "leaf_category"
        FROM amazon_data_db.gold.fact_product_category
        WHERE ("product_id", "category_level") IN (SELECT "product_id", "max_category" FROM product_max_level)
    ),
    product_base AS (
        SELECT 
            dp."product_id",
            b."brand_id", 
            pl."leaf_category",
            IFNULL(p."rating", 0) AS "rating",
            CASE 
                WHEN p."rating" >= 4.5 THEN 1
                WHEN p."rating" BETWEEN 4 and 4.5 THEN 2
                WHEN p."rating" BETWEEN 3 AND 4 THEN 3
                WHEN p."rating" < 3 THEN 4
                WHEN p."rating" IS NULL THEN 5
            END AS "rating_range_id",
            IFNULL(p."ratings_total", 0) AS "ratings_total",
            IFNULL(p."rating" * LN(1+ NULLIF(p."ratings_total",0)), 0) AS "weighted_rating",
            IFNULL("5_star_prct" * 1.0 + "4_star_prct" * 0.8 + "3_star_prct" * 0.5 + "2_star_prct" * 0.2 + "1_star_prct" * 0.1, 0) AS "avg_star_score"

        FROM amazon_data_db.silver.products AS p
        LEFT JOIN amazon_data_db.gold.dim_products AS dp USING ("asin")
        LEFT JOIN amazon_data_db.gold.dim_brand AS b USING("brand")
        LEFT JOIN product_leaf_level AS pl USING("product_id")
    ), rating_rank AS (
    -- Final Table Selection
    SELECT
        p."product_id",
        r."recent_month_sale",
        p.* EXCLUDE("product_id"), 
        ROW_NUMBER() OVER(ORDER BY p."weighted_rating" DESC, p."rating" DESC, p."ratings_total" DESC, p."avg_star_score" DESC) AS "rating_rank",
    FROM product_base AS p
    LEFT JOIN rebuild_recent_sales AS r USING("product_id")
    )
    SELECT 
        *, 
        ROW_NUMBER() OVER(ORDER BY "recent_month_sale" DESC, "rating_rank" ASC) AS "sales_rank" 
    FROM rating_rank;
```

- **all_recent_sales**: combines Rainforest recent_sales + Keepa recent_month_sale by ASIN
- **rebuild_recent_sales**: chooses Rainforest sales unless zero, else Keepa fallback (mapped to product_id)
- **product_max_level**: finds deepest category_level per product_id
- **product_leaf_level**: selects the leaf category_id per product_id
- **product_base**: builds product metrics (brand, leaf category, rating buckets, weighted scores)
- **rating_rank**: ranks products by weighted rating signals + attaches recent_month_sale
- **Final SELECT**: ranks by recent_month_sale + rating_rank to produce sales_rank

------

## 4) `fact_buybox_products`

```sql
CREATE OR REPLACE VIEW amazon_data_db.gold.fact_buybox_products AS
    WITH pivoted AS (
        SELECT 
            p."asin",
            o."seller_id",
            o."seller_name",
            o."price",
            o."is_new",
            o."is_fba",
            o."is_prime",
            o."is_free_shipping",
            o."condition",
            o."is_buybox_winner",
            CASE 
                WHEN o."price" IS NULL THEN 'Out of stock' 
                ELSE 'In stock' 
            END AS "stock_availability"
        FROM amazon_data_db.silver.products AS p
        JOIN amazon_data_db.silver.offers AS o
            ON o."asin" = p."asin"
            AND o."seller_name" != p."seller_name"
            AND o."is_buybox_winner" = 1
        UNION ALL
        SELECT 
            p."asin",
            p."seller_id",
            p."seller_name",
            p."price",
            p."is_new",
            p."is_fba",
            p."is_prime",
            o."is_free_shipping",
            o."condition",
            o."is_buybox_winner",
            CASE 
                WHEN p."price" IS NULL THEN 'Out of stock' 
                ELSE 'In stock' 
            END AS "stock_availability"
        FROM amazon_data_db.silver.products AS p
        JOIN amazon_data_db.silver.offers AS o
            ON o."asin" = p."asin"
            AND o."seller_name" = p."seller_name"
            AND o."is_buybox_winner" = 1
        UNION ALL
        SELECT
            "asin",
            "seller_id",
            "seller_name",
            "price",
            "is_new",
            "is_fba",
            "is_prime",
            0 AS "is_free_shipping",
            'Unknown' AS "condition",
            1 AS "is_buybox_winner", 
            "stock_availability"
        FROM amazon_data_db.silver.products
        WHERE "seller_id" IS NULL
            OR "asin" NOT IN (
                SELECT DISTINCT "asin" 
                FROM amazon_data_db.silver.offers
            )
    ), 
    add_ids AS (
    SELECT 
        prd."product_id",
        s."seller_id",
        "price",
        CASE 
            WHEN "price" < 100 THEN 1
            WHEN "price" BETWEEN 100 AND 200 THEN 2
            WHEN "price" BETWEEN 200 AND 300 THEN 3
            WHEN "price" BETWEEN 300 AND 500 THEN 4
            WHEN "price" BETWEEN 500 AND 1000 THEN 5
            WHEN "price" > 1000 THEN 6
        END AS "price_range_id",
        "is_new",
        "is_fba",
        "is_prime",
        "is_free_shipping",
        c."condition_id",
        "is_buybox_winner",
        a."availability_id"
    FROM pivoted AS p
    LEFT JOIN amazon_data_db.gold.dim_sellers AS s 
        ON s."seller_pid" = p."seller_id"
    LEFT JOIN amazon_data_db.gold.dim_condition AS c 
        ON c."condition" = p."condition"
    LEFT JOIN amazon_data_db.gold.dim_buy_box_availability AS a 
        ON a."availability" = p."stock_availability"
    LEFT JOIN amazon_data_db.gold.dim_products AS prd USING("asin")
    )
    -- Add missing Seler IDs from fact_offers table
    SELECT 
        bp."product_id",    
        CASE 
            WHEN o."seller_id" IS NULL THEN bp."seller_id"
            ELSE o."seller_id" 
        END AS "seller_id",
        bp.* EXCLUDE ("product_id", "seller_id")
    FROM add_ids AS bp
    LEFT JOIN amazon_data_db.gold.fact_offers AS o
        ON bp."product_id" = o."product_id"
        AND bp."price" = o."price"
        AND o."is_buybox_winner" = 1
        AND bp."seller_id" IS NULL AND bp."price" IS NOT NULL
    ORDER BY bp."product_id";
    ;
```

- **pivoted**: assembles Buy Box rows across scenarios (winner differs, winner matches, fallback when missing offers/seller)
- **add_ids**: maps business fields to dimension IDs + assigns price_range_id + availability_id + condition_id
- **Final SELECT**: fills missing seller_id from fact_offers when Buy Box match exists

------

# Data Analysis

## 1) Top Seller Rating

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.t2_top_sellers AS
    WITH seller_base AS (
        SELECT 
            "seller_id",
            0.5 * "positive_rating_30_days" + 0.3 * "positive_rating_60_days" + 0.2 * "positive_rating_90_days" AS "stable_positive_pct",
            LN(1 + "total_rating_count") AS "review_weight",
            LN(1+ IFNULL("selling_count", 0)) AS "catalog_weight",
            "is_fba"
        FROM amazon_data_db.gold.fact_sellers
    ),
    seller_score AS (
    SELECT
        ROUND(IFNULL("stable_positive_pct" * "review_weight" * "catalog_weight", 0)) AS "seller_score",
        "seller_id",
        "stable_positive_pct",
        "review_weight",
        "catalog_weight",
        "is_fba"
    FROM seller_base
    )
    SELECT 
        ROW_NUMBER() OVER (ORDER BY "seller_score" DESC, "stable_positive_pct" DESC, "review_weight" DESC, "catalog_weight" DESC) AS "rating_rank",
        *
    FROM seller_score;
```

- **seller_base**: builds weighted stability + review weight + catalog weight per seller
- **seller_score**: computes final seller_score using stability × weights
- **Final SELECT**: ranks sellers by score and component strength

------

## 2) Black Friday Prices

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.t3_black_friday_prices AS
    WITH historical_prices AS(
        SELECT * 
            FROM amazon_data_db.gold.fact_historical_data
        WHERE "type_id" IN (0, 1, 4, 18)
    )
    ,grouped AS (
        SELECT 
            "product_id", 
            "type_id",
            ROUND(AVG("value"), 2) AS "value", 
            "date"
        FROM historical_prices
        WHERE "date" BETWEEN '2025-11-20' AND '2025-12-01'
        GROUP BY "product_id", "date", "type_id"
    ),
    joined AS (
        SELECT 
            g."product_id", 
            bb."price" AS "current_buyBox_price",
            CASE WHEN g."type_id" = 0 THEN g."value" END AS "amazon_price",
            CASE WHEN g."type_id" = 18 THEN g."value" END AS "buyBox_new_shipping_price",
            CASE WHEN g."type_id" = 1 THEN g."value" END AS "new_price",
            CASE WHEN g."type_id" = 4 THEN g."value" END AS "list_price",
            g."date"
        FROM grouped AS g
        LEFT JOIN amazon_data_db.gold.fact_buybox_products AS bb USING("product_id")
    ),
    get_min AS (
    SELECT 
        "product_id", 
        MIN("current_buyBox_price") AS "current_buyBox_price",
        MIN("amazon_price") AS "amazon_price",
        MIN("buyBox_new_shipping_price") AS "buyBox_new_shipping_price",
        MIN("new_price") AS "new_price",
        MIN("list_price") AS "list_price"
    FROM joined
    GROUP BY "product_id"
    ),
    best_price AS (
        SELECT 
            "product_id",
            "current_buyBox_price",
            LEAST(
                COALESCE("amazon_price", 9999999),
                COALESCE("buyBox_new_shipping_price", 9999999),
                COALESCE("new_price", 9999999),
                COALESCE("list_price", 9999999)
            ) AS "prime_lowest_price",
            "amazon_price",
            "buyBox_new_shipping_price",
            "new_price",
            "list_price"
        FROM get_min
    ),
    discounts AS (
    SELECT 
        "product_id",
        "current_buyBox_price",
        -- CASE
        --     WHEN "prime_lowest_price" = "amazon_price" THEN 1
        --     WHEN "prime_lowest_price" = "buyBox_new_shipping_price" THEN 2
        --     WHEN "prime_lowest_price" = "new_price" THEN 3
        --     WHEN "prime_lowest_price" = "list_price" THEN 4
        --     ELSE 0
        -- END AS "best_price_type_id",
        "prime_lowest_price",
        "amazon_price",
        "buyBox_new_shipping_price",
        "new_price",
        IFNULL("current_buyBox_price" - "prime_lowest_price", 0) AS "discount_amount",
        ("current_buyBox_price" - "prime_lowest_price") * 1.0 / "current_buyBox_price" * 100 AS "discount_prct"
    FROM best_price
    )
    SELECT 
        ROW_NUMBER() OVER (ORDER BY "discount_amount" DESC, "discount_prct" DESC) AS "discount_rank",
        *,
        CASE 
            WHEN "discount_amount" < 100 THEN 1
            WHEN "discount_amount" BETWEEN 100 AND 200 THEN 2
            WHEN "discount_amount" BETWEEN 200 AND 300 THEN 3
            WHEN "discount_amount" BETWEEN 300 AND 500 THEN 4
            WHEN "discount_amount" BETWEEN 500 AND 1000 THEN 5
            WHEN "discount_amount" > 1000 THEN 6
        END AS "price_range_id",
        CASE 
            WHEN "discount_prct" < 0.05 THEN 0
            WHEN "discount_prct" < 0.2 THEN 1
            WHEN "discount_prct" < 0.35 THEN 2
            WHEN "discount_prct" >= 0.35 THEN 3
            ELSE 4
        END AS "discopunt_level_id"
    FROM discounts;
```

- **historical_prices**: filters historical table to key BF price types (0,1,4,18)
- **grouped**: averages values per product/date/type within BF date window
- **joined**: attaches current Buy Box price to historical rows
- **get_min**: reduces multiple BF-day rows to per-product minimums
- **best_price**: selects prime_lowest_price across price candidates using LEAST()
- **discounts**: calculates discount_amount and discount_prct vs current Buy Box
- **Final SELECT**: ranks discounts + assigns price_range_id + discount_level_id

------

## 3) Pareto

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.rp_t1_pareto_analysis AS
    WITH best_ranks AS (
        SELECT 
            bb."product_id",
            p."recent_month_sale",
            SUM(p."recent_month_sale") OVER(ORDER BY p."recent_month_sale" DESC) AS "cumulative_sale",
            SUM(p."recent_month_sale") OVER () AS "total_sales",
            bb."price",
            p."rating", p."ratings_total",
            p."rating" * LN(1 + p."ratings_total") AS "rating_weighted_score",
            p."recent_month_sale" * bb."price" AS "revenue",
            p."rating_range_id",
            bb."price_range_id",
            bb."availability_id",
            bb."condition_id",
            bb."is_new",
            bb."is_fba",
            bb."is_free_shipping",
            bb."is_prime"
        FROM amazon_data_db.gold.fact_buybox_products AS bb
        JOIN amazon_data_db.gold.fact_product AS p USING("product_id")
        WHERE bb."price" IS NOT NULL
    ),
    cumulative_pct AS (
        SELECT 
            ROW_NUMBER() OVER(ORDER BY "rating_weighted_score" DESC) AS "rating_rank",
            *, 
            "cumulative_sale" * 1.0 / "total_sales" AS "cumulative_sale_percentage" 
        FROM best_ranks
    ),
    add_top20_flag AS (
        SELECT
            *, 
            CASE WHEN "cumulative_sale_percentage" <= 0.8 THEN 'Vital Few'
                    ELSE 'Trivial Many' 
                END AS "top_selling_categories"
        FROM cumulative_pct
    )
    SELECT 
        ROW_NUMBER() OVER(ORDER BY "revenue" DESC) AS "revenue_rank",
        *

    FROM add_top20_flag;
882 772
882 674
```

- **best_ranks**: builds sales + cumulative sales + rating score + revenue (Buy Box priced products only)
- **cumulative_pct**: computes cumulative_sale_percentage + rating_rank
- **add_top20_flag**: labels Vital Few vs Trivial Many using 80% cutoff
- **Final SELECT**: ranks by revenue and outputs full Pareto table

------

## 4) Revenue by date: Historical

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.t1_sale_revenue_by_date AS
    WITH sale_data AS (
        SELECT 
            c1."product_id",
            SUM(c1."sold") AS "sale",
            SUM(c1."sold") * AVG(c2."value") AS "revenue",
            AVG(c2."value") AS "price",
            c1."date",
            EXTRACT(MONTH FROM c1."date") AS "month",
            EXTRACT(YEAR FROM c1."date") AS "year"
        FROM amazon_data_db.gold.fact_monthly_sold AS c1
        JOIN amazon_data_db.gold.fact_historical_data AS c2 
            ON c1."product_id" = c2."product_id" 
            AND c1."date" = c2."date"
        WHERE c2."type_id" = 18 -- New buybox Shipping Price
        GROUP BY 
            c1."product_id",
            c1."date"
    ), 
    total_sale_revenue_in_year AS (
        SELECT 
            *,
            SUM("sale") OVER (PARTITION BY "month", "year") AS "total_sale_in_month",
            SUM("revenue") OVER (PARTITION BY "month", "year") AS "total_revenue_in_month",
            SUM("sale") OVER (PARTITION BY "year") AS "total_sale_in_year",
            SUM("revenue") OVER (PARTITION BY "year") AS "total_revenue_in_year"
        FROM sale_data
    )
    SELECT 
        "product_id",
        "sale",
        "revenue",
        "price",
        "date", 
        "month",
        "year",
        "sale" * 1.0 / "total_sale_in_month" AS "monthly_sale_share_pct",
        "revenue" * 1.0 / "total_revenue_in_month" AS "monthly_revenue_share_pct",
        "sale" * 1.0 / "total_sale_in_year" AS "yearly_sale_share_pct",
        "revenue" * 1.0 / "total_revenue_in_year" AS "yearly_revenue_share_pct"
    FROM total_sale_revenue_in_year;
```

- **sale_data**: aggregates sold + revenue by day using Buy Box shipping price (type_id=18)
- **total_sale_revenue_in_year**: computes monthly/yearly totals using window sums
- **Final SELECT**: outputs revenue/sale + monthly/yearly share percentages
