# 1. Product Data Analysis

### 1. Unified Product Pricing & Buy Box View

- Purpose of `vw_all_products`

  - Combines **product-level stats** and **Buy Box details** into one analytical table
  - Designed for **price comparison, Buy Box analysis, and product performance reporting**
  - Avoids repeating complex joins and CASE logic across multiple queries
  - Acts as the **main entry point** for product-level analysis in Power BI

- **Logic Used to Build the View:**

  - **Step 1 - Identify Amazon seller**

    - `amazon_seller_id` CTE finds all the `seller_id`s where **seller** is **amazon**

    ```sql
    CREATE OR REPLACE TABLE amazon_data_db.gold.vw_all_products AS
    -- Step 1 – Identify Amazon seller
    WITH amazon_seller_id AS (
        SELECT "seller_id"
        FROM amazon_data_db.gold.dim_sellers
        WHERE "seller_name" LIKE '%Amazon%'
        
    ), 
    ```

    

  - **Step 2 – Classify Buy Box winner**

    - `amazon_buyBox_winner` CTE unpivots 2 parts of `fact_buybox`: 
      - If Buy Box winner is Amazon → `buyBox_winner_id = 1 (`seller_id` in `seller_id`s in `amazon_seller_id` ) `
      - If Buy Box winner is not Amazon → `buyBox_winner_id = 2` (`seller_id` not in `seller_id`s extracted from `amazon_seller_id` ) 
    - Therefore we have `buyBox_winner_id` column that defines who is buybox winner.

    ```sql
    -- Step 2 – Classify Buy Box winner
    amazon_buyBox_winner AS(
        SELECT 
            "product_id", 
      			1 AS "buyBox_winner_id", 
      			"price", 
      			"price_range_id", 
            "availability_id", 
            "condition_id", "is_fba", "is_prime", "is_free_shipping"
        FROM amazon_data_db.gold.fact_buybox
        WHERE "seller_id" = (SELECT "seller_id" FROM amazon_seller_id)
        UNION ALL
        SELECT 
            "product_id", 
      			2 AS "buyBox_winner", 
      			"price", 
      			"price_range_id", 
            "availability_id",
            "condition_id", "is_fba", "is_prime", "is_free_shipping"
        FROM amazon_data_db.gold.fact_buybox
        WHERE "seller_id" != (SELECT "seller_id" FROM amazon_seller_id)
    )
    ```

    

  - **Step 3 – Join to product stats**

    - Now that we have information about buybox winners, we join CTE2 with `fact_product` to add `buybox` data to out static product data
    - **Static Product columns:**
      - `recent_month_sales` , `rating` , `total_reviews` , `leaf_category` , `availability_amazon`
      -  amazon_price , min_new_price 
      - `rating_rank_score`: We want to calculate true rating not only based on rating stars so calculation will be 
        - `rating * LN(1+total_reviews)`
          - LN(1+total_reviews) helps to reduce the impact of products with too many reviews on the total rating calculation
    - New Columns from `amazon_buyBox_winner` CTE:
      - `buyBox_availability` , 
      - `buyBox_winner_id` (`0` or `1`)
      - `buyBox_price`
    - New Columns Created after the join:
      - `best_price_winner` (1, 2, 3): 
        - If amazon Price is the lowest price → `1`
        - If Merchant is the lowest price → 2
        - If none are offering lowest price → 3
      - `rating_range_id`
      - `price_range_id`

    ```sql
    -- Step 3 – Join to product stats
    SELECT 
        f."product_id", 
        "brand_id", 
        "recent_month_sales", 
        "rating", 
        "total_reviews", 
        bb."buyBox_winner_id",
        "amazon_price",
        "leaf_category",
        bb."price" AS "buyBox_price",
        "min_new_price",
        "min_used_price",
        "availability_amazon",
        ROW_NUMBER() OVER (ORDER BY "recent_month_sales" DESC) AS "sales_rank",
        bb."availability_id" AS "buyBox_availability", 
        bb."condition_id", bb."is_fba", bb."is_prime", bb."is_free_shipping",
        CASE 
            WHEN "amazon_price" = "min_new_price" AND "min_new_price" > 0 THEN 1
            WHEN bb."price" = "min_new_price" AND "min_new_price" > 0 THEN 2
            WHEN bb."price" != "min_new_price" AND "amazon_price" != "min_new_price" AND "min_new_price" > 0 THEN 3
            ELSE bb."buyBox_winner_id"
        END AS "best_price_winner",
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

---

## 2. Reliable Products 
<img width="465" height="393" alt="Screenshot 2025-12-11 at 6 53 57 AM" src="https://github.com/user-attachments/assets/e5b7f05e-9789-4a22-9f76-02ff758d12ba" />
In order to grab top rated products:

1. Use the `rating_rank_score` values that scored products' rating , which we calculated before in `all_products`	
2. Using window function we `Rank` products based on rating score and `recent_month_sales` in case of tie

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.vw_t1_top_notch_rated_products AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY "rating_rank_score" DESC, "recent_month_sales" DESC) AS "RANK",
    *
FROM amazon_data_db.gold.vw_all_products 
WHERE "rating" IS NOT NULL 
    AND "total_reviews" IS NOT NULL 
    AND "rating_rank_score" IS NOT NULL;
```

---

## 3. Total Revenue by year and month If Amazon Sold all Products
<img width="787" height="393" alt="Screenshot 2025-12-11 at 6 54 10 AM" src="https://github.com/user-attachments/assets/edaec2fc-0f80-4d1f-ba18-ca2d446f407a" />

- **Step1 - Extract average Amazon price by product–year–month **

  - Extract `Month` and `Year` from `date`
  - Extract **Average** **amazon Prices** for **each product** 

  ```sql
  CREATE OR REPLACE TABLE amazon_data_db.gold.vw_t1_product_sale_by_month_year AS
  WITH selling_price AS (
      SELECT 
          "product_id",
          ROUND(AVG("value"),2) AS "avg_amazon_price",
          EXTRACT(MONTH FROM "date") AS "month",
          EXTRACT(YEAR FROM "date") AS "year"
      FROM amazon_data_db.gold.fact_historical_data
      WHERE "type_id" = 0
      GROUP BY 
          "product_id",
          EXTRACT(MONTH FROM "date"), 
          EXTRACT(YEAR FROM "date")
  ),
  ```
  

- **Step2 -  Extract total sales by product–year–month**

  - Extract `Month` and `Year` from `date`
  - Extract **Total** **sale** for **each product** 

  ```sql
  -- Step2 - CTE2: Total Sale
  sales AS (
      SELECT 
          "product_id",
          SUM("sold") AS "total_sales",
          EXTRACT(MONTH FROM "date") AS "month",
          EXTRACT(YEAR FROM "date") AS "year"
      FROM amazon_data_db.gold.fact_monthly_sold
      GROUP BY 
          "product_id",
          EXTRACT(MONTH FROM "date"),
          EXTRACT(YEAR FROM "date")
  )
  ```

- **Step3 - Join on product + year + month, compute revenue**

  ```sql
  -- Step3 - Total Sale + Avg Price + Revenue for each Product in each Month and year
  SELECT 
      s1."product_id", 
      s1."avg_amazon_price", 
      s2."total_sales",
      s2."total_sales" * s1."avg_amazon_price" AS "revenue",
      s1."month",
      s1."year"    
  FROM selling_price AS s1
  JOIN sales AS s2 
  ON s1."product_id" = s2."product_id"
  AND s1."month" = s2."month" 
  AND s1."year" = s2."year";
  ```

### **Total Revenue and Unit sold by Month+Year **

In PowerBI We import above Table and filter the Visual by **year** or **month**

- **Total monthly revenue in 2025 representation in SQL:**

```sql
SELECT 
    "month",
    ROUND(SUM("revenue"), 0) AS "total_revenue",
    ROUND(AVG("avg_amazon_price"), 2) AS "avg_price"
FROM amazon_data_db.gold.vw_t1_product_sale_by_month_year
WHERE "year" = 2025
GROUP BY "month"
ORDER BY "month";
```

| month | total_revenue | avg_price |
| ----- | ------------- | --------- |
| 1     | 469987036     | 910.35    |
| 2     | 207426751     | 896.53    |
| 3     | 186093566     | 783.30    |
| 4     | 396171085     | 832.93    |
| 5     | 469794155     | 878.27    |
| 6     | 348058345     | 879.02    |
| 7     | 1011158422    | 915.93    |
| 8     | 697597366     | 953.08    |
| 9     | 796316215     | 1003.82   |
| 10    | 1070814116    | 895.09    |
| 11    | 1484147       | 1119.79   |


---

## 4. Top-Selling Products – Pareto (80/20) Revenue View
<img width="486" height="400" alt="Screenshot 2025-12-11 at 6 54 23 AM" src="https://github.com/user-attachments/assets/b40e80e1-f01b-446c-9495-86cc58da9623" />


This view identifies the **top-selling products** based on **recent month sales and revenue**, and applies a **Pareto (80/20) classification**. 

- **STEP 1 — Build Product Revenue & Cumulative Sales Table**
  - Join `vw_all_products` with `fact_avg_stats` to get an average price (`avg_value`)
  - Compute : `revenue = avg_value * recent_month_sales`
  - Using Window function generate:
    - `cumulative_sale`: Running total of sales ordered highest To lowest
    - `total_sales`: total sales across all products

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.vw_t1_top20_selling_products AS
WITH best_ranks AS (
SELECT 
        "product_id", 
        "rating", 
        "total_reviews",
        s."avg_value" AS "price", 
        "recent_month_sales",
        s."avg_value" * "recent_month_sales" AS "revenue",
        "condition_id", 
        "is_fba", "is_free_shipping", 
        "brand_id", 
        SUM("recent_month_sales") OVER(ORDER BY "recent_month_sales" DESC) AS "cumulative_sale",
        SUM("recent_month_sales") OVER () AS "total_sales",
        "buyBox_availability" AS "availability_id", 
        "rating_range_id",
        "price_range_id",
    FROM amazon_data_db.gold.vw_all_products AS p
    JOIN amazon_data_db.gold.fact_avg_stats AS s USING("product_id")
    WHERE s."avg_window_id" = 0 AND s."type_id" = 1
),
```

- **STEP 2 — Calculate Cumulative Percentage of Sales**
  - Compute **cumulative sale percentage**: `cumulative_sale_percentage = cumulative_sale / total_sales`

```sql
cumulative_pct AS (
	SELECT 
		*, 
        "cumulative_sale" * 1.0 / "total_sales" AS "cumulative_sale_percentage" 
	FROM best_ranks
),
```

- **STEP 3 — Classify Products Using the 80/20 Rule**
  - Label products by their Cumulative sale percentage:
    - `"Vital Few"` **(top 80% of cumulative sales)**
    - `"Trivial Many"` **(remaining 20%)**
  - Meaning:
    - IF **cumulative percentage** <= 0.8 → `"Vital Few"`
    - Else → `"Trivial Many"`

```sql
add_top20_flag AS (
	SELECT
		*, 
        CASE WHEN "cumulative_sale_percentage" <= 0.8 THEN 'Vital Few' ELSE 'Trivial Many' END AS "top_selling_categories"
    FROM cumulative_pct
)
```

- **STEP 4 — Rank Products by Revenue**
  - Assign a revenue rank to each product (highest → lowest) and finalize the view.

```sql
SELECT 
	ROW_NUMBER() OVER(ORDER BY "revenue" DESC) AS revenue_rnk,
	*
FROM add_top20_flag;

```

---

# Seller Data Analysis:

## 1. **Seller Detail Enrichment View**

- **Step 1 - Compute Seller Listing Totals**
  - Number of product listings per seller
  - Count of new vs used listings
  - Count of `FBA` vs `FBM` listings
  - Count of **Amazon Retail** vs **Third-Party** **Seller** offers

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.vw_all_seller_detail AS
WITH seller_totals AS (
    SELECT
        "seller_id",
        COUNT(*) AS "product_listed",
        SUM(CASE WHEN "condition_id" = 1 THEN 1 ELSE 0 END) AS "new_count",
        SUM(CASE WHEN "condition_id" = 2 THEN 1 ELSE 0 END) AS "used_count",
        SUM(CASE WHEN "is_fba" = 1 THEN 1 ELSE 0 END) AS "FBA_count", --Fullfilled by Amazon
        SUM(CASE WHEN "is_fba" = 2 THEN 1 ELSE 0 END) AS "FBM_count", -- Fulfillment by Merchant"
        SUM(CASE WHEN "is_amazon" = 1 THEN 1 ELSE 0 END) AS "count_Amazon_retail",
        SUM(CASE WHEN "is_amazon" = 2 THEN 1 ELSE 0 END) AS "count_Third_Party_Seller",
    FROM amazon_data_db.gold.fact_offer_history
    GROUP BY "seller_id"
),
```

- **STEP 2 — Determine Best Offer for Each Product**
  - Identify the lowest offer price per product within the **same condition** and **category** to ensure **fairness**
  - NOTE:  (e.g., Used vs New offers are not mixed).

```sql
product_best_offers AS (
    SELECT s1."product_id", s2."seller_id", s1."best_offer", s1."condition_id"
    FROM (
        SELECT 
            "product_id", "condition_id", 
            MIN("offer_price") AS "best_offer"
        FROM amazon_data_db.gold.fact_offer_history
        GROUP BY "product_id", "condition_id" ORDER BY "product_id"
    ) AS s1
    JOIN amazon_data_db.gold.fact_offer_history AS s2 
        ON s1."product_id" = s2."product_id" AND 
        s1."best_offer" = s2."offer_price"
)
```

- **STEP 3 — Count How Many Times Each Seller Provides the Best Offer**
  - Useful for identifying aggressive, price-competitive sellers
  - Helps identify potential “loss-leader” sellers or consistent competitors

```sql
,best_offers AS (
    SELECT "seller_id", COUNT(*) best_offer_count
    FROM product_best_offers
    GROUP BY "seller_id" 
), 
```

- **STEP 4 — Combine Listing Totals With Best Offer Counts**
  - Seller listing metrics (new, used, FBA, FBM, Amazon/3P counts)
  - Number of times seller offers the best (lowest) price

```sql
joined AS (
    SELECT 
        tot."seller_id", 
        tot."product_listed",
        b.best_offer_count AS "count_best_offer_price",
        tot."new_count",
        tot."used_count",
        tot."FBA_count",
        tot."FBM_count",
        tot."count_Amazon_retail",
        tot."count_Third_Party_Seller",
    FROM seller_totals AS tot 
    JOIN best_offers AS b USING ("seller_id")
    ORDER BY tot."seller_id"
)
```

- **STEP 5 — Add Seller Performance Metrics From fact_sellers**
  - Rating count
  - Positive rating percentages (30/60/90 days)
  - New vs used ownership rates
  - Fulfillment flag (`is_fba`)

```sql
SELECT
    j."seller_id",
    j."product_listed", 
    j."count_best_offer_price",
    j."new_count",
    j."used_count", 
    j."FBA_count", 
    j."FBM_count", 
    j."count_Amazon_retail",
    j."count_Third_Party_Seller",
    f."is_fba",
    f."rating_count",
    f."positive_rating_30_days" AS "p_rate_30_perc", 
    f."positive_rating_60_days" AS "p_rate_60_perc", 
    f."positive_rating_90_days" AS "p_rate_90_perc",
    f."new_ownership_rate" AS "new_listing_perc",
    f."used_ownership_rate" AS "used_listing_perc"
FROM joined AS j
JOIN amazon_data_db.gold.fact_sellers AS f USING ("seller_id");
```

---

## 2. Top Sellers

This table ranks sellers in two different ways:

1. **Sale Rank** → based on **how active they are**
2. **Rating Rank** → based on **how strong and stable their ratings are**

Steps: 

- **STEP 1 — Bring in Seller Detail Metrics**
  - Start from the enriched seller detail view and select only the columns required for scoring and ranking.

```sql
WITH all_sellers AS (
    SELECT 
        "seller_id", 
        "product_listed", 
        "count_best_offer_price", 
        "new_listing_perc",
        "used_listing_perc", 
        "rating_count" AS "total_reviews",
        "p_rate_30_perc", 
        "p_rate_60_perc", 
        "p_rate_90_perc"
    FROM amazon_data_db.gold.vw_all_seller_detail
),
```

- **STEP 2 — Compute Weighted Stability & Log-Based Weights**

  - Create intermediate metrics that describe **seller stability and importance**, using:

    - Weighted positive rating percentage
    - Log-based scaling for reviews and catalog size

  - **Calculations:**

    1. ```review_weight = LN(1 + total_reviews)```

       - More reviews → higher weight
       - Uses log so 10 vs 1000 reviews doesn’t explode

    2. ```catalog_weight = LN(1 + product_listed)```

       1. More listing → higher importance
       2. Also log-scaled

    3. `stable_positive_pct`

       - This rewards sellers who are **consistently positive, especially recently**
       - Recent Positive Ratings have Higher weight
         - 30-day > 60 days > 90 days

       ```txt
       0.5 * p_rate_30_perc +
       0.3 * p_rate_60_perc +
       0.2 * p_rate_90_perc
       ```

  ```sql
  calculations AS (
      SELECT
          "seller_id", 
          "count_best_offer_price", 
          "new_listing_perc",
          "used_listing_perc", 
          "product_listed", 
          "total_reviews",
          LN(1 + "total_reviews") AS "review_weight",
          LN(1+ "product_listed") AS "catalog_weight",
          0.5 * "p_rate_30_perc" + 0.3 * "p_rate_60_perc" + 0.2 * "p_rate_90_perc" AS "stable_positive_pct"
      FROM all_sellers
  ),
  ```

  - **STEP 3 — Build Seller Score and Normalize Positive %**
    - Combine stability, reviews, and catalog size into a single **seller_score**
    - Higher when:
      - **Positive ratings** are **strong** and **stable**
      - There are **many reviews**
      - More selling Products (Larger Catalog)
      - ```seller_score = "stable_positive_pct" * "review_weight" * "catalog_weight"```

  ```sql
  final_calculation AS (
      SELECT
          ROUND(IFNULL("stable_positive_pct" * "review_weight" * "catalog_weight", 0)) AS "seller_score",
          "seller_id", 
          "count_best_offer_price", 
          "new_listing_perc",
          "used_listing_perc", 
          "product_listed", 
          "total_reviews",
          "stable_positive_pct" / 100 AS "positive_pct"
      FROM calculations
  )
  ```

  **STEP 4 — Assign Sale Rank and Rating Rank**

  - `sale_rank`: High product_listed + high positive_pct → better rank
  - `rating_rank`: High seller_score + many reviews + decent catalog → better rank

  ```sql
  SELECT 
      ROW_NUMBER() OVER (ORDER BY "product_listed" DESC, "positive_pct" DESC, "positive_pct" DESC) AS sale_rank,
      ROW_NUMBER() OVER (ORDER BY "seller_score" DESC, "total_reviews" DESC, "product_listed" DESC) AS rating_rank,
      *
  FROM final_calculation;
  ```

  ---

# Discount Strategy (Discount Suggestion)

This table recommends a **discount percentage per product** by combining:

- **Amazon** vs **Buy Box** price gaps
- **Amazon** vs **its own historical price**
- **Amazon** vs **eBay** price gaps
- **Sales performance** vs **category median**

The output gives us:

- A **discount_score** (0–1 scaled)
- A **discount_level**: `NO_DISCOUNT`, `SMALL`, `MEDIUM`, `AGGRESSIVE`
- A **recommended_discount_pct** (0–1)
- A **discounted_price`** = `amazon_price * recommended_discount_pct`

## Steps to execute:

- **STEP 1 — Average Monthly eBay Prices**

  - Get average **eBay new and used prices** per product, based on historical stats.

  - **Uses `fact_avg_stats` where:**

    - `type_id = 28` → eBay new avg price

    - `type_id = 29` → eBay used avg price

    - `avg_window_id = 0` → Past 30 days data

```sql
CREATE OR REPLACE TABLE amazon_data_db.gold.t2_discount_suggestion AS
-- CTE1: Get Average Monthly Prices for eBay
WITH ebay_avg_monthly_prices AS (
    SELECT 
        "product_id", 
        MAX(CASE WHEN "type_id" = 28 THEN "avg_value" END) AS "new_avg_ebay",
        MAX(CASE WHEN "type_id" = 29 THEN "avg_value" END) AS "used_avg_ebay"
    FROM amazon_data_db.gold.fact_avg_stats
    WHERE "type_id" IN (28, 29) AND "avg_window_id" = 0
    GROUP BY "product_id"
),
```

- **STEP 2 — Average Monthly Amazon Prices**

  - Get average **Amazon new and used prices** per product.

  - **Uses `fact_avg_stats` where:**

    - `type_id = 1` → Amazon new avg price

    - `type_id = 2` → Amazon used avg price

    - Same averaging window: `avg_window_id = 0`

```sql
-- CTE2: Get Average Monthly Prices for Amazon Prices
amazon_avg_monthly_prices AS (
    SELECT 
        "product_id", 
        MAX(CASE WHEN "type_id" = 1 THEN "avg_value" END) AS "new_avg_amazon",
        MAX(CASE WHEN "type_id" = 2 THEN "avg_value" END) AS "used_avg_amazon"
    FROM amazon_data_db.gold.fact_avg_stats
    WHERE "type_id" IN (1, 2) AND "avg_window_id" = 0
    GROUP BY "product_id"
),
```

- **STEP 3 — Get Leaf Category for Each Product**
  - Assign each product to its **leaf-level category**
  - used later to compute category **median sales**.

```sql
leaf_category AS(
    SELECT 
        "product_id", 
        MAX("category_level") AS "level_leaf",
        MAX("category_id") AS "category_id"
    FROM amazon_data_db.gold.fact_product_category
    GROUP BY "product_id"
),
```

- **STEP 4 — Build Base Table With Prices & Context**
  - Combine **product details**, **Buy Box price**, **Amazon prices**, **eBay prices**, **sales**, and **category** into one **base dataset.**

```sql
-- CTE3: Base Table with necessary fields (including buy box price, amazon and ebay avg prices, category for median sales)
base AS (
    SELECT 
        f."product_id",
        f."rating",
        f."total_reviews",
        f."amazon_price", 
        f."new_price",
        b."price" AS "new_buy_box_price",
        ap."new_avg_amazon", 
        ep."new_avg_ebay",
        f."recent_month_sales",
        c."category_id"
    FROM amazon_data_db.star_schema.fact_product AS f
    JOIN amazon_data_db.star_schema.fact_current_buybox AS b USING("product_id")
    JOIN leaf_category AS c USING("product_id")
    LEFT JOIN amazon_avg_monthly_prices AS ap USING("product_id")
    LEFT JOIN ebay_avg_monthly_prices AS ep USING("product_id")
    WHERE f."amazon_price" IS NOT NULL
),
```

- **STEP 5 — Compute Category Median Sales**
  - To find if whether a product is **selling slower than its peers** :
    - Add the **median sales per category** for each product, so we can evaluate .
      - Uses `MEDIAN(recent_month_sales)` as **window function**
      - Partitioned by `category_id`:  median sales within each category

```sql
-- CTE4: Calculate Median Sales per Category
base_with_median AS (
    SELECT
        *,
        MEDIAN("recent_month_sales") OVER(PARTITION BY "category_id") AS "median_sales_cat"
    FROM base
),
```

- **STEP 6 — Build Discount Signals**
  - Create **four normalized discount signals (0–1)** that capture different discount reasons:
    1. **comp_buybox** – **Amazon** vs **Buy Box** price gap
    2. **hist_overpricing** – **Amazon** vs **its own** **historical** **avg price**
    3. **ebay_overpricing** – **Amazon** vs **eBay’s** avg price
    4. **sales_slow** – **Sales** versus category **median**
  - Logic:
    1. **Competitive vs Buy Box (comp_buybox)**
       - If **Amazon price** <= **Buy Box price** → 0 (no issue)
       - Else: ```(amazon_price - new_buy_box_price) / new_buy_box_price```
         - capped at 20%, then scaled to 0–1
    2. **Historical Overpricing (hist_overpricing)**
       - If Amazon price <= its own avg → 0
       - Else: `(amazon_price - new_avg_amazon) / new_avg_amazon`
         - apped and scaled like above
    3. **eBay Overpricing (ebay_overpricing)**
       - If Amazon price <= eBay avg → 0
       - Else: `(amazon_price - new_avg_ebay) / new_avg_ebay`, 
         - capped and scaled
    4. **Sales Slowdown (sales_slow)**
       - If median is null/0 → 0
       - Else: `1 - min( recent_month_sales / median_sales_cat, 1 )`
       - So if sales are < median → higher signal (closer to 1)

```sql
-- CTE5: Calculate Discount Signals 
signals AS (
    SELECT
        *,
        CASE 
            WHEN "amazon_price" <= "new_buy_box_price"  OR "new_buy_box_price" IS NULL THEN 0
            ELSE LEAST(("amazon_price"-"new_buy_box_price") / IFNULL("new_buy_box_price", 0), 0.2) / 0.2
        END AS comp_buybox,

        CASE 
            WHEN "amazon_price" <= "new_avg_amazon" OR IFNULL("new_avg_amazon", 0) = 0 THEN 0
            ELSE LEAST(GREATEST(("amazon_price" - "new_avg_amazon") / IFNULL("new_avg_amazon", 0), 0), 0.2) / 0.2
        END AS hist_overpricing,
  
        CASE 
            WHEN "amazon_price" <= "new_avg_ebay" OR IFNULL("new_avg_ebay", 0) = 0 THEN 0
            ELSE LEAST(("amazon_price" - "new_avg_ebay") / IFNULL("new_avg_ebay", 0), 0.2) / 0.2
        END AS ebay_overpricing,  

        CASE 
            WHEN "median_sales_cat" IS NULL OR "median_sales_cat" = 0 THEN 0
            ELSE 1-LEAST("recent_month_sales"/"median_sales_cat", 1)
        END AS sales_slow    
    FROM base_with_median
),
```

- **STEP 7 — Compute Overall Discount Score**
  - Combine the four signals into a **single discount_score** between 0 and 1.
  - Highest To lowest signals: 
    1. Buy Box Comparison , **40%**
    2. Historical Comparisn, 25%
    3. Ebay comparison, **20%**
    4. Slow sale, **10%**

```sql
-- CTE6: Calculate Overall Discount Score based on weighted signals
scored AS (
    SELECT 
        *, 
        0.4 * comp_buybox
        + 0.25 * hist_overpricing 
        + 0.20 * ebay_overpricing 
        + 0.15 * sales_slow AS "discount_score"
    FROM signals
),
```

- STEP 8 — Determine Extra rule for Maximum Discount Cap
  - Assign a **maximum allowed discount percentage** based on current Amazon price.
  - **Rules:**
    - `Price` >= `1000` → **max 10%**
    - `300`–`999.99` → **max 20%**
    - `100`–`299.99` → **max 25%**
    - Else → **max 35%**

```sql
-- CTE7: Determine Maximum Discount Percentage based on Amazon Price
priced AS (
    SELECT 
        *,
        CASE
            WHEN "amazon_price" >= 1000 THEN 10
            WHEN "amazon_price" BETWEEN 300 AND 999.99 THEN 20
            WHEN "amazon_price" BETWEEN 100 AND 299.99 THEN 25
            ELSE 35
        END AS "max_discount_pct"
    FROM scored
),
```

- **STEP 9 — Classify Discount Level & Raw %**
  - Turn **discount_score** into:
    - A **discount_level** label
    - A **raw_pct** suggestion = `discount_score * max_discount_pct`
  - **Levels:**
    - `< 0.1` → `NO_DISCOUNT`
    - `< 0.2` → `SMALL`
    - `< 0.35` → `MEDIUM`
    - Else → `AGGRESSIVE`

```sql
-- CTE8: Final Discount Level and Recommended Discount Percentage
final_cte AS (
    SELECT
        *, 
        CASE 
            WHEN "discount_score" < 0.1 THEN 'NO_DISCOUNT'
            WHEN "discount_score" < 0.2 THEN 'SMALL'
            WHEN "discount_score" < 0.35 THEN 'MEDIUM'
            ELSE 'AGGRESSIVE'
        END AS "discount_level",
        ROUND("discount_score" * "max_discount_pct", 0) AS "raw_pct"
    FROM priced
),
```

- **STEP 10 — Add Metadata & Final Recommended %**
  - Rules:
    - If `NO_DISCOUNT` → **0**
    - `SMALL` → `min(raw_pct, max_discount_pct * 0.5) / 100`
    - `MEDIUM` → `min(raw_pct, max_discount_pct * 0.8) / 100`
    - `AGGRESSIVE` → full `max_discount_pct / 100`
    - Adds:
      - `rating_range_id`
      - `price_range_id`
      - Seller & availability metadata from `views.all_products`

```sql
finaled AS (
    SELECT
        f."product_id",
        f."rating",
        f."total_reviews",
        "amazon_price", 
        f."new_price",
        f."new_buy_box_price",
        f."new_avg_amazon", 
        f."new_avg_ebay",
        f."recent_month_sales",
        f."discount_score",
        f."discount_level",
        f."category_id",
        "price_range_id",
        "rating_range_id",
        bb."condition_id", 
        bb."is_amazon", bb."is_amazon_fba", bb."is_fba", "is_free_shipping", 
        bb."brand_id", 
        bb."availability_id", 
        CASE 
            WHEN "discount_level" = 'NO_DISCOUNT' THEN 0
            WHEN "discount_level" = 'SMALL' THEN LEAST("raw_pct", "max_discount_pct" * 0.5) / 100 -- * 0.5 small discount
            WHEN "discount_level" = 'MEDIUM' THEN LEAST("raw_pct", "max_discount_pct" * 0.8) / 100 -- * 0.8 medium discount
            WHEN "discount_level" = 'AGGRESSIVE' THEN "max_discount_pct" / 100 -- 100% for aggressive discount
            ELSE "max_discount_pct" / 100
        END AS "recommended_discount_pct"
    FROM final_cte as f
    JOIN amazon_data_db.views.all_products AS bb USING("product_id")
)
SELECT 
    "product_id",
    "discount_level",
    "recommended_discount_pct", 
    "recommended_discount_pct" * "amazon_price" AS "discounted_price",
    "discount_score"
FROM finaled
ORDER BY "product_id";

```



