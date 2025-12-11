# **1. Introduction**

In this project, I implemented of full ETL Pipeline, that demonstrates

1. **Extracting** raw JSON data from multiple Keepa API endpoints
2. **Transforming** Keepa JSON objects into normalized CSV datasets
3. Building a **Medallion Architecture** (Bronze, Silver, Gold) entirely in **Snowflake SQL**
4. Loading transformed datasets into the **Bronze Layer**
5. Cleaning, validating, and standardizing data in the **Silver Layer**
6. Designing a full **Star Schema** in the **Gold Layer**, including dimension and fact tables
7. Creating **business-ready analytical views** for Power BI visualizations

**Goal:** Convert complex Amazon retail data into actionable business insights using a clean, scalable analytical architecture.

---

# **2. Keepa API Endpoints Used**

To support real retail analytics, the project requires enriched product & seller data. This is achieved by extracting multiple data types from different Keepa endpoints.

Some Keep Endpoints used to extract relevant data are:

1. **[Category Lookup](https://keepa.com/#!discuss/t/category-lookup/113): **

   Used to extract category IDs and names for downstream filtering.

   - **Output:** Category lookup CSV
   - **Target leaf categories:**
     - All-in-One Computers
     - Tower Computers
     - Mini Computers
     - Traditional Laptop Computers
     - 2 in 1 Laptop Computers
     - Computer Tablets

   ---

2. **[Product Finder](https://keepa.com/#!discuss/t/product-finder/5473): **

   To Extract All the Products ASINS Within each of extracted Categories**

   - **Output:** CSV with ASIN and category_id

   ---

3. **[Products](https://keepa.com/#!discuss/t/products/110) ednpoint: **

   Extracts full product objects including:

   - Listing attributes
   - Price history
   - Stats for 365 days
   - BuyBox history
   - Offer details
   - Ratings
   - Seller information

   **Output**: JSON response of all the input JSONS.

   - **Requirements:** 

     - Send HTML header requests to capture each product response( could use extra tokens)

       1. `stats` of past 365 days

       1. `history` to capture hystorical data

       1. `offers` minimum number of offers per products

       1. `rating`

       1. `buybox`

       1. `stock`

   - **Limitation:** 

     - Due to limitation on tokens per hour on my Keepa Subscription, the automated python Script was crutial to make sure of complete extraction of data. 
       - Split ASINs into manageable chunks
       - Request each chunk with required HTML headers
       - Save result of each church as a JSON files
       - Merge all product responses into one combined JSON

   ---

4. **[Seller Object](https://keepa.com/#!discuss/t/seller-object/791): **

   Captures all seller-related information for sellers appearing in product offers.

   1. **Output**: CSV containing Sellers who are only selling product ASINS.
   2. **Process**:
      1. Extract unique seller IDs from merged product JSON
      2. Write seller IDs to CSV
      3. Request seller objects via Keepa Seller endpoint
      4. Store seller JSON response

**Example of Product JSON Response - [product object](https://discuss.keepa.com/t/product-object/116)**

<img width="848" height="529" alt="Screenshot 2025-12-10 at 5 57 26 PM" src="https://github.com/user-attachments/assets/01af1ff3-1469-44b6-b109-0f6eeb5ab667" />


**Example of Seller JSON Response - [Seller Information](https://keepa.com/#!discuss/t/seller-information/790)**
<img width="848" height="552" alt="Screenshot 2025-12-10 at 6 04 06 PM" src="https://github.com/user-attachments/assets/4a4619c8-e96c-4793-83e8-0123a0403f3d" />


---

# 3) Data transformation:

Raw JSON is not directly usable → transformation is required.

**Approach:** 

- Understand Keepa JSON structure using documentation
- Create a Python script to read each product/seller JSON
- Normalize nested objects
- Generate flat, readable CSV files for Snowflake ingestion

**Result:** The result is a complete set of transformed datasets covering:

- Products
- Categories
- BuyBox details
- Sellers
- Offers
- Ratings
- Historical stats
<img width="966" height="206" alt="Screenshot 2025-12-10 at 6 09 52 PM" src="https://github.com/user-attachments/assets/64e8514c-4437-4aa7-9bf2-1ac8420f71b1" />

---

# **4. Snowflake Setup (Warehouse, Database, Schemas)**

A dedicated Snowflake environment was created for the Medallion Architecture. Created objects listed bellow:

- **Warehouse** → compute engine for ETL 
- **Database** → `amazon_data_db`
- **Schemas:**
  - **Bronze** → raw transformed CSVs
  - **Silver** → cleaned and standardized
  - **Gold** → dimension, fact, and analytical views
<img width="854" height="453" alt="Screenshot 2025-12-10 at 2 20 31 PM" src="https://github.com/user-attachments/assets/a494ab40-76e5-4af2-90f8-7db125c053e2" />


---

# **5. Bronze Layer**

The Bronze Layer contains **all transformed CSV files**, loaded directly into Snowflake.

<img width="765" height="395" alt="Screenshot 2025-12-10 at 5 17 55 PM" src="https://github.com/user-attachments/assets/37080c8e-5803-42a5-b758-d3ef0203b87e" />


**Example dataset: `static.csv` loaded into Bronze.**
<img width="1091" height="357" alt="Screenshot 2025-12-10 at 6 15 51 PM" src="https://github.com/user-attachments/assets/b3c896ff-ce3c-4b48-b8d1-fedc4df96d01" />


---

# 6. Silver Layer, Cleaning & Standardization

The Silver Layer converts raw transformed data into **trustworthy, validated, and analysis-ready tables**.

### **Key Cleaning Operations**

- ### **A. Handling Nulls and Duplicates**

  - Drop or impute invalid/null fields
  - Use ranking to retain only the most recent or highest-priority record
  - Ensure **one row** per **seller**/**product** when appropriate

### **B. Schema & Naming Standardization**

- Standardize column names
- Remove unused or duplicated columns
- Define clear table grain (row meaning)

### **C. Data Type Normalization**

- Convert prices, ratings, review counts into numerics
- Convert timestamps into proper date formats
- Normalize boolean strings into 0/1

### **D. Business Rule Corrections**

- Replace **negative** values with **zero**
- Cap `discount%` within logical bounds (0–100%)
- Fix malformed or missing fields

### **E. Text Normalization**

- Trimmed whitespace
- Lowercase/uppercase standardization
- Removal of hidden Unicode characters

The result is a clean analytical foundation, ready for modeling in the Gold Layer.

**Screenshot bellow shows the cleaned tables within the silver layer Schema:**
<img width="766" height="371" alt="Screenshot 2025-12-10 at 6 21 12 PM" src="https://github.com/user-attachments/assets/3539eba0-2486-4f8c-9b77-86a6f7b1999e" />



**Example of Transformed `static.csv` within Silver Layer:**
<img width="1361" height="348" alt="Screenshot 2025-12-10 at 6 20 03 PM" src="https://github.com/user-attachments/assets/03124496-677c-4071-aa9b-9faf2657cb9a" />


**Example data cleaning queries on `seller_data`:**
<img width="852" height="427" alt="Screenshot 2025-12-10 at 6 26 06 PM" src="https://github.com/user-attachments/assets/8bcc16b6-c1a6-44fa-9cdb-df44885ff66b" />

**Example data cleaning queries on `buy_box_winner`:**
<img width="1035" height="370" alt="Screenshot 2025-12-10 at 6 28 37 PM" src="https://github.com/user-attachments/assets/51ff934c-b50a-4d39-bc92-3d0795269743" />

---

# 7. Gold Layer, Dimensions & Facts

Once the Silver tables were fully cleaned, the Gold Layer was built to support BI queries and advanced analytics.

- **All cleaned Silver tables are transformed into:**

  - **Dimension tables** → descriptive business entities

  - **Fact tables** → measurable, numerical events

  - **Analytical views** → ready for Power BI and advanced analysis

- **Purpose of Dimensions**

  - Provide identifiers

  - Normalize categorical data

  - Simplify to use in Power BI filters

  - Enable analytics at multiple grouping levels

---

### **1. Dimension Layer (Business Entities)**

The Gold Layer includes several dimensions that standardize business attributes for filtering, drill-downs, and grouping.

### **Key Dimensions**

| Dimension                | Purpose                              |
| ------------------------ | ------------------------------------ |
| **dim_product**          | Assigns product_id to each ASIN      |
| **dim_brand**            | Standardized brand lookup            |
| **dim_category**         | Full hierarchical category structure |
| **dim_product_category** | Maps products to all category levels |
| **dim_sellers**          | Cleaned seller identifiers           |
| **dim_condition**        | Product condition classifications    |
| **dim_fba**              | FBA vs FBM                           |
| **dim_is_amazon**        | Amazon vs Third-Party                |
| **dim_price_ranges**     | Price bucket dimension               |
| **dim_rating_buckets**   | Rating bucket dimension              |
| **dim_historical_types** | Maps historical metrics to IDs       |
| **dim_best_seller**      | BuyBox winner classification         |

---

### Example Dimension: 

### 1. Category Dimension Modeling

Creates a full hierarchical parent-child mapping for:

```nginx
root → Electronics → Computers & Accessories → Desktops → Minis
```

This enables category drilldowns in Power BI.

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.dim_category AS
-- CTE 1: Get Parent category name to the main transformed table, assign root to Department
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
SELECT * FROM amazon_data_db.gold.dim_category ORDER BY "parent_category_id";
```
<img width="811" height="172" alt="Screenshot 2025-12-10 at 6 52 32 PM" src="https://github.com/user-attachments/assets/de6b42f5-1a75-4949-a135-32237a27da45" />
<img width="811" height="415" alt="Screenshot 2025-12-10 at 6 51 51 PM" src="https://github.com/user-attachments/assets/52abe5bd-f795-4d27-9d38-4ef7ef5e95ff" />

---

### 2. **Brand Lookup dimension table `dim_brand`**

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.dim_brand AS 
WITH distinct_brands AS (
    SELECT DISTINCT "brand" FROM amazon_data_db.silver.static
)
SELECT 
    ROW_NUMBER() OVER(ORDER BY "brand") AS "brand_id", 
    "brand"
FROM distinct_brands;
SELECT * FROM amazon_data_db.gold.dim_brand;
```
<img width="304" height="297" alt="Screenshot 2025-12-10 at 7 03 52 PM" src="https://github.com/user-attachments/assets/63da46ed-efd1-49d7-a156-42e0b13f163b" />

---

### 3. **Best seller dimension table `dim_best_seller`**

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.dim_best_seller(
    "winner_id" INT,
    "winner_category" STRING
);
INSERT INTO amazon_data_db.gold.dim_best_seller VALUES
    (1, 'Amazon'),
    (2, 'buyBox_seller'),
    (3, 'None');
```
<img width="304" height="193" alt="Screenshot 2025-12-10 at 7 05 56 PM" src="https://github.com/user-attachments/assets/da0d92f0-74de-43fc-a17c-87a7ced63f52" />

---

### 2. Fact Layer (Measurable Data)

### 1) Static Fact Tables:

1. ### **`fact_product`: **

   Central fact table containing the latest product information:

   - Pricing (Amazon price, minimum new/used, MSRP)
   - Ratings & reviews
   - Category leaf assignment
   - Offer counts (new, used, refurbished)
   - Amazon availability
   - Recent month sales

   **This table drives most summary-level product reporting.**

| product_id | brand_id | leaf_category | recent_month_sales | rating | total_reviews | availability_amazon | amazon_price | min_new_price | min_used_price | manufacturer_price | new_count | used_count | refurbished_count | rating_range_id |
| ---------- | -------- | ------------- | ------------------ | ------ | ------------- | ------------------- | ------------ | ------------- | -------------- | ------------------ | --------- | ---------- | ----------------- | --------------- |
| 1          | 41       | 14            | 0                  | 5      | 1             | 0                   | 0            | 0             | 0              | 1438               | 0         | 0          | 0                 | 1               |
| 2          | 119      | 13            | 0                  | 4.2    | 271           | 0                   | 0            | 0             | 0              | 0                  | 0         | 0          | 0                 | 2               |
| 3          | 41       | 14            | 0                  | 5      | 4             | 0                   | 0            | 0             | 0              | 0                  | 0         | 0          | 0                 | 1               |
| 4          | 68       | 15            | 0                  | 4.3    | 971           | 0                   | 0            | 0             | 0              | 216                | 0         | 0          | 0                 | 2               |
| 5          | 41       | 14            | 0                  | 4.8    | 11            | 0                   | 0            | 0             | 0              | 0                  | 0         | 0          | 0                 | 1               |
| 6          | 13       | 13            | 50                 | 4      | 444           | 0                   | 0            | 120           | 85             | 699                | 4         | 6          | 0                 | 2               |
| 7          | 13       | 13            | 300                | 4.1    | 3541          | 0                   | 0            | 83            | 72             | 350                | 12        | 15         | 27                | 2               |
| 8          | 114      | 13            | 0                  | 4.2    | 36            | 0                   | 0            | 0             | 0              | 0                  | 0         | 0          | 0                 | 2               |
| 9          | 41       | 14            | 0                  | 5      | 5             | 0                   | 0            | 0             | 0              | 0                  | 0         | 0          | 0                 | 1               |
| 10         | 9        | 13            | 0                  | 3.8    | 322           | 0                   | 0            | 0             | 0              | 168                | 0         | 0          | 0                 | 3               |

---

2. ### **`fact_buybox`: **

Contains BuyBox winner information -  buybox winner can be Amazon or Merchant:

- Seller_id of BuyBox winner
- Winning price
- Condition
- FBA / Prime / free shipping flags
- Availability status
- Used BuyBox details (used_seller_id, used_price, used_condition_id)

**Used to Analyse:**

- Amazon vs Third-Party competition
- How fulfillment affects BuyBox wins
- Price competitiveness

| product_id | seller_id | price | price_range_id | condition_id | is_amazon | is_fba | is_prime | new_fba_count | new_fbm_count | used_seller_id | used_price | used_condition_id | used_fbm_count | is_free_shipping | availability_id |
| ---------- | --------- | ----- | -------------- | ------------ | --------- | ------ | -------- | ------------- | ------------- | -------------- | ---------- | ----------------- | -------------- | ---------------- | --------------- |
| 6          | 677       | 120   | 2              | 1            | 0         | 1      | 1        | 0             | 1             |                | 0          | 0                 | 7              | 1                | 1               |
| 7          | 1097      | 83    | 1              | 1            | 0         | 1      | 1        | 0             | 5             |                | 0          | 0                 | 13             | 1                | 6               |
| 11         | 105       | 51    | 1              | 1            | 0         | 0      | 1        | 0             | 2             |                | 0          | 0                 | 0              | 1                | 1               |
| 12         | 210       | 145   | 2              | 1            | 0         | 0      | 0        | 0             | 1             |                | 0          | 0                 | 0              | 0                | 1               |
| 14         | 704       | 1230  | 6              | 1            | 0         | 1      | 1        | 0             | 1             |                | 0          | 0                 | 0              | 1                | 1               |
| 19         | 36        | 161   | 2              | 1            | 0         | 0      | 1        | 0             | 8             |                | 0          | 0                 | 17             | 1                | 6               |
| 21         | 1037      | 86    | 1              | 1            | 0         | 0      | 0        | 0             | 18            |                | 0          | 0                 | 17             | 0                | 1               |
| 23         | 542       | 890   | 5              | 0            | 0         | 0      | 0        | 0             | 1             |                | 0          | 0                 | 0              | 0                | 6               |
| 24         | 1039      | 90    | 1              | 1            | 0         | 1      | 1        | 0             | 7             |                | 0          | 0                 | 11             | 1                | 1               |
| 25         | 181       | 101   | 2              | 1            | 0         | 0      | 1        | 0             | 8             |                | 0          | 0                 | 4              | 1                | 6               |

---

3. ### **`fact_sellers`: **

Seller performance snapshot:

- Rating and rating_count
- Positive/negative rating history (30/60/90 days)
- Ownership rate
- FBA flag

**Useful for identifying:**

- Seller reputation
- Reliable vs unreliable sellers
- BuyBox impact of seller quality

| seller_id | rating_count | rating | negative_rating_90_days | positive_rating_90_days | new_ownership_rate | used_ownership_rate |
| --------- | ------------ | ------ | ----------------------- | ----------------------- | ------------------ | ------------------- |
| 809       | 3            | 33     | 1                       | 0.0                     | 50                 | 0                   |
| 151       | 113          | 68     | 1                       | 61.0                    | 23                 | 5                   |
| 1034      | 534          | 90     | 0                       | 90.0                    | 0                  | 0                   |
| 754       | 2201         | 99     | 0                       | 57.0                    | 0                  | 0                   |
| 448       | 613          | 99     | 1                       | 98.0                    | 79                 | 0                   |
| 9         | 414          | 86     | 1                       | 69.0                    | 28                 | 0                   |
| 420       | 1543         | 91     | 0                       | 80.0                    | 0                  | 0                   |
| 108       | 722          | 83     | 0                       | 75.0                    | 33                 | 17                  |
| 190       | 4188         | 89     | 0                       | 77.0                    | 8                  | 0                   |
| 881       | 11           | 82     | 1                       | 82.0                    | 25                 | 0                   |

---

4. ### **`fact_seller_profile` : **

Have information regarding Products within each brand that each seller sells. (Each seller can sell multiple brands.)

1. Seller-to-brand behavior:
   - seller_id
   - brand_id
   - number of products sold per brand
   - average monthly sale ranking

2. **Useful for identifying:**
   - Seller performance dashboards
   - Brand-level seller concentration analysis


| seller_id | brand_id | selling_count | avg_monthly_sale_rank |
| --------- | -------- | ------------- | --------------------- |
| 793       | 156      | 964           | 65946                 |
| 793       | 161      | 438           | 113810                |
| 793       | 154      | 409           | 124170                |
| 231       | 156      | 276           | 67343                 |
| 231       | 161      | 276           | 150519                |
| 231       | 154      | 263           | 125839                |
| 550       | 154      | 22            | 141641                |
| 550       | 161      | 8             | 245336                |
| 701       | 156      | 43            | 55724                 |
| 701       | 161      | 1             | 29639                 |

---

5. ### **`fact_product_category`**

   Maps each product to its hierarchical category levels.

   Used for:

   - Product-level slicing
   - Category rollups
   - Multi-level visuals in Power BI

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.fact_product_category AS
-- CTE 1: Add parent Category to category table
WITH product_category AS(
    SELECT 
        "asin",
        "category_name",
        COALESCE(LAG("category_name") OVER(PARTITION BY "asin" ORDER BY "category_level"), 'root') AS "parent_category",
        "category_level"
    FROM amazon_data_db.silver.categories
)
-- Final Query: Join to the ids dim_category on both category and parent category columns Lookup table to assign id to category_id
SELECT 
    p."product_id", 
    c1."category_id" AS "category_id", 
    "category_level",
FROM product_category AS pc 
JOIN amazon_data_db.gold.dim_category AS c1 ON c1."category_name" = pc."category_name"
JOIN amazon_data_db.gold.dim_products AS p USING("asin")
```

**Output Fact table For `product_id = 1` :**
<img width="861" height="274" alt="Screenshot 2025-12-10 at 9 23 05 PM" src="https://github.com/user-attachments/assets/4c3275d5-63b1-481b-8d45-a818b3ddfdb1" />

---

### 2) **Historical fact data:** 

Historical datasets support time-series trends, forecasting, feature engineering, and long-term behavioral analysis.

### Use cases:

1. **Predictive analysis**

   1. Use data to use as feature engineering features to predict feature **trends** in `sale`, `revenue`,  `BuyBox sellers`
   2. To Decide on applying `coupon` and `Descount`, in the feature either:
      1. During Sale season periods (Black Friday, Christmas,etc..) \
      2. Time to time discounts to improve sale and revenue
   3. Predict feature sales during Next Sale season (Black Friday, Christmas,etc..) based on past sales.

2. **Static analysis:**

   1. Show the previous treand over time
   2. Used for aggregate values based on timeframes

   ---

### **Table Deffinitions:**

1. **`fact_avg_stats`**

   Rolling averages across 30/60/90 days.
   Used to:

   - Smooth price fluctuations
   - Identify trends
   - Feed ML models

<img width="460" height="538" alt="Screenshot 2025-12-10 at 11 05 37 PM" src="https://github.com/user-attachments/assets/ede94d60-f1f8-46c8-b28a-cef1b506460c" /> <img width="305" height="696" alt="Screenshot 2025-12-10 at 11 16 03 PM" src="https://github.com/user-attachments/assets/2e5fc0af-80bb-4e31-8865-1d46e319367a" />


   ---

2. **`fact_historical_data`:** 

   The most detailed time-series table:

   1. Usecase:
      1. forecasting sales
      2. Discount Descision
      3. BuyBox trends.
   2. Covers:
      - Amazon prices
      - Market prices
      - Ratings
      - Offer counts
      - Competitor signals

<img width="452" height="538" alt="Screenshot 2025-12-10 at 11 07 52 PM" src="https://github.com/user-attachments/assets/894d64bd-6a03-45b7-afba-632d13d78c8f" /> <img width="305" height="696" alt="Screenshot 2025-12-10 at 11 16 03 PM" src="https://github.com/user-attachments/assets/6a4a2f29-40d4-429e-94a2-c86dde64ab92" />

   ---

3. **`fact_buy_box_winners`:** 

   Historical BuyBox performance:

   - Who won
   - Percent of wins
   - Average winning price
   - Offers per condition

   Supports BuyBox prediction and competition analysis.
<img width="922" height="538" alt="Screenshot 2025-12-10 at 11 06 22 PM" src="https://github.com/user-attachments/assets/01e87c11-4295-40de-92c8-8fe1c68ff1ea" />


   ---

4. **`fact_coupon_history`:**

   Tracks:

   - When coupons were applied
   - Discount percentage

   Useful for:

   - Designing discount strategies
   - Predicting sales lift during promotions
<img width="441" height="538" alt="Screenshot 2025-12-10 at 11 07 07 PM" src="https://github.com/user-attachments/assets/a2b702bb-ac14-4584-922d-25530a738fec" />


   ---

5. **`fact_offer_history`:** 

   1. Tracks every marketplace offer historically:
      - seller_id
      - offer_price
      - latest price date
      - condition_id
      - is_amazon / is_fba / is_prime
   2. Used to analyze:
      - Price competition
      - Seller reliability
      - Offer volatility
<img width="922" height="538" alt="Screenshot 2025-12-10 at 11 08 41 PM" src="https://github.com/user-attachments/assets/c2a9b3d7-c4d8-4426-8d8b-9a3b96d64c02" />


   ---

6. **`fact_buy_box_history`**

   A lighter BuyBox timeline for:

   1. Feature engineering
   2. Simple trend modeling
<img width="368" height="538" alt="Screenshot 2025-12-10 at 11 09 45 PM" src="https://github.com/user-attachments/assets/4e5840b8-10f6-413c-a15e-367f5d1ebd32" />


   ---

7. **`fact_monthly_sold`:** 

   Monthly sales quantity for each product.

   Used for:

   - Seasonal trend analysis
   - Sales forecasting
   - Revenue modeling
<img width="333" height="538" alt="Screenshot 2025-12-10 at 11 10 33 PM" src="https://github.com/user-attachments/assets/5106d36e-e052-4970-94ce-56729b97c8f8" />

---

# 8. Business Analysis

### 8.1. Price Comparison

Query information:

- `buyBox_winner_id`: Shows rows that the amazon was buybox winner
- `best_price_winner`: Compares whos price is the best among all
  - Lowes New Price Can be from buy box winners (amazon | Third-Party)
  - From None (meaning Lowest Price from another seller that might have low rating or other bad features)

Extractable Analysis:

- Finding Cases When Amazon/Third-Party has competitive price
- Finding Cases When Lowest Price Comes from bad seller not in buyBox
- Discount strategy
- Stock availability of Amazon Products
  - Usual Availability 
  - Availability When no Price existed
- Stock availability of Buy Box (Can be amazon)
- Free shipping

```SQL
CREATE OR REPLACE TABLE amazon_data_db.gold.vw_all_products AS
WITH amazon_seller_id AS (
    SELECT "seller_id"
    FROM amazon_data_db.gold.dim_sellers
    WHERE "seller_name" LIKE '%Amazon%'
    
), amazon_buyBox_winner AS(
    SELECT 
        "product_id", 1 AS "buyBox_winner_id", "price", "price_range_id", "availability_id", 
        "condition_id", "is_fba", "is_prime", "is_free_shipping"
    FROM amazon_data_db.gold.fact_buybox
    WHERE "seller_id" = (SELECT "seller_id" FROM amazon_seller_id)
    UNION ALL
    SELECT 
        "product_id", 2 AS "buyBox_winner", "price", "price_range_id", "availability_id",
        "condition_id", "is_fba", "is_prime", "is_free_shipping"
    FROM amazon_data_db.gold.fact_buybox
    WHERE "seller_id" != (SELECT "seller_id" FROM amazon_seller_id)
)
SELECT 
    f."product_id", 
    "brand_id", "recent_month_sales", "rating", "total_reviews", 
    bb."buyBox_winner_id",
    CASE 
        WHEN "amazon_price" = "min_new_price" AND "min_new_price" > 0 THEN 1
        WHEN bb."price" = "min_new_price" AND "min_new_price" > 0 THEN 2
        WHEN bb."price" != "min_new_price" AND "amazon_price" != "min_new_price" AND "min_new_price" > 0 THEN 3
        ELSE bb."buyBox_winner_id"
    END AS "best_price_winner",
    "amazon_price",
    bb."price" AS "buyBox_price",
    "min_new_price",
    "min_used_price",
    "availability_amazon",
    bb."availability_id" AS "buyBox_availability", 
    bb."condition_id", bb."is_fba", bb."is_prime", bb."is_free_shipping",
    CASE 
        WHEN "rating" >= 4.5 THEN 1
        WHEN "rating" BETWEEN 4 and 4.5 THEN 2
        WHEN "rating" BETWEEN 3 AND 4 THEN 3
        WHEN "rating" < 3 THEN 4
        WHEN "rating" IS NULL THEN 5
    END AS "rating_range_id",
    CASE 
        WHEN bb."price" < 100 THEN 1
        WHEN bb."price" BETWEEN 100 AND 200 THEN 2
        WHEN bb."price" BETWEEN 200 AND 300 THEN 3
        WHEN bb."price" BETWEEN 300 AND 500 THEN 4
        WHEN bb."price" BETWEEN 500 AND 1000 THEN 5
        WHEN bb."price" > 1000 THEN 6
    END AS "price_range_id"
FROM amazon_data_db.gold.fact_product AS f
JOIN amazon_buyBox_winner AS bb USING("product_id");
```



# 









