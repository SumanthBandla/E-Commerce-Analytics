-- ============================================================================
-- E-COMMERCE ANALYTICS — SQL ANALYSIS
-- ----------------------------------------------------------------------------
-- Author   : E-Commerce Analytics Project
-- Database : MySQL 8.0+
-- Dataset  : data/ecommerce_dataset.csv (cleaned -> outputs/cleaned_data)
--
-- This script contains the full SQL analysis used to answer the business
-- questions. Every result can be cross-validated against the Python EDA
-- notebook and the Tableau dashboard KPIs.
--
-- Techniques demonstrated: SELECT, WHERE, GROUP BY, HAVING, ORDER BY, CASE,
-- aggregate functions, JOINs, CTEs, subqueries and window functions.
-- ============================================================================

-- ============================================================================
-- 0. DATABASE SETUP (run once, then import the CSV)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS ecommerce_analytics;
USE ecommerce_analytics;

-- Table definition mirrors the CLEANED dataset (25 columns)
CREATE TABLE IF NOT EXISTS orders (
    order_id          VARCHAR(20)   NOT NULL,
    order_date        DATE          NOT NULL,
    customer_id       VARCHAR(20)   NOT NULL,
    customer_name     VARCHAR(100)  NOT NULL,
    segment           VARCHAR(20)   NOT NULL,
    country           VARCHAR(30)   NOT NULL,
    state             VARCHAR(30)   NOT NULL,
    city              VARCHAR(30)   NOT NULL,
    region            VARCHAR(20)   NOT NULL,
    product_id        VARCHAR(20)   NOT NULL,
    product_name      VARCHAR(120)  NOT NULL,
    category          VARCHAR(30)   NOT NULL,
    sub_category      VARCHAR(30)   NOT NULL,
    sales             DECIMAL(12,2) NOT NULL,
    quantity          INT           NOT NULL,
    discount          DECIMAL(4,2)  NOT NULL,
    profit            DECIMAL(12,2) NOT NULL,
    shipping_cost     DECIMAL(12,2) NOT NULL,
    shipping_mode     VARCHAR(20)   NOT NULL,
    payment_mode      VARCHAR(25)   NOT NULL,
    year              INT           NOT NULL,
    month             INT           NOT NULL,
    quarter           INT           NOT NULL,
    order_year_month  VARCHAR(7)    NOT NULL,
    profit_margin_pct DECIMAL(8,2)  NOT NULL,
    PRIMARY KEY (order_id, product_id),
    INDEX idx_order_date (order_date),
    INDEX idx_region (region),
    INDEX idx_category (category)
);

-- Import the cleaned CSV (adjust the file path to your MySQL install)
-- LOAD DATA LOCAL INFILE 'outputs/cleaned_data/ecommerce_clean.csv'
--   INTO TABLE orders
--   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
--   LINES TERMINATED BY '\n'
--   IGNORE 1 LINES;

-- ============================================================================
-- SECTION 1: HIGH-LEVEL KPIs
-- ============================================================================

-- 1.1 Total sales (revenue)
SELECT 'Total Sales'             AS metric, ROUND(SUM(sales), 2)       AS value FROM orders
UNION ALL
-- 1.2 Total profit
SELECT 'Total Profit'            AS metric, ROUND(SUM(profit), 2)      AS value FROM orders
UNION ALL
-- 1.3 Total orders
SELECT 'Total Orders'            AS metric, COUNT(DISTINCT order_id)   AS value FROM orders
UNION ALL
-- 1.4 Total quantity sold
SELECT 'Total Quantity'          AS metric, SUM(quantity)              AS value FROM orders
UNION ALL
-- 1.5 Average order value
SELECT 'Average Order Value'     AS metric,
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2)                 AS value FROM orders
UNION ALL
-- 1.6 Overall profit margin (%)
SELECT 'Overall Profit Margin %' AS metric,
       ROUND(SUM(profit) / SUM(sales) * 100, 2)                        AS value FROM orders;

-- ============================================================================
-- SECTION 2: TIME-BASED ANALYSIS
-- ============================================================================

-- 2.1 Monthly sales & profit (strongest and weakest months)
SELECT
    CONCAT(YEAR(order_date), '-', LPAD(CAST(MONTH(order_date) AS CHAR), 2, '0')) AS year_month,
    COUNT(DISTINCT order_id)                                        AS orders,
    ROUND(SUM(sales), 2)                                            AS sales,
    ROUND(SUM(profit), 2)                                           AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)                        AS profit_margin_pct
FROM orders
GROUP BY year_month
ORDER BY year_month;

-- 2.2 Yearly sales, profit & orders
SELECT
    YEAR(order_date)                AS year,
    COUNT(DISTINCT order_id)        AS orders,
    ROUND(SUM(sales), 2)            AS sales,
    ROUND(SUM(profit), 2)           AS profit
FROM orders
GROUP BY YEAR(order_date)
ORDER BY year;

-- 2.3 Yearly growth analysis using a window function (LAG)
WITH yearly AS (
    SELECT
        YEAR(order_date)        AS year,
        ROUND(SUM(sales), 2)    AS sales,
        ROUND(SUM(profit), 2)   AS profit
    FROM orders
    GROUP BY YEAR(order_date)
)
SELECT
    year,
    sales,
    profit,
    LAG(sales)  OVER (ORDER BY year)                        AS prev_year_sales,
    ROUND((sales - LAG(sales) OVER (ORDER BY year)) /
          NULLIF(LAG(sales) OVER (ORDER BY year), 0) * 100, 2) AS yoy_growth_pct
FROM yearly
ORDER BY year;

-- 2.4 Peak selling month (overall, aggregated across all years)
SELECT
    MONTH(order_date)                                   AS month,
    ROUND(SUM(sales), 2)                                AS sales,
    ROUND(SUM(profit), 2)                               AS profit
FROM orders
GROUP BY MONTH(order_date)
ORDER BY sales DESC;

-- ============================================================================
-- SECTION 3: CATEGORY & PRODUCT ANALYSIS
-- ============================================================================

-- 3.1 Category performance (revenue, profit, margin, share)
SELECT
    category,
    COUNT(DISTINCT order_id)                            AS orders,
    ROUND(SUM(sales), 2)                                AS sales,
    ROUND(SUM(profit), 2)                               AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2)            AS profit_margin_pct,
    ROUND(SUM(sales) / SUM(SUM(sales)) OVER () * 100, 2) AS sales_share_pct
FROM orders
GROUP BY category
ORDER BY sales DESC;

-- 3.2 Sub-category performance
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2)     AS sales,
    ROUND(SUM(profit), 2)    AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY category, sub_category
ORDER BY sales DESC;

-- 3.3 Top 10 products by sales
SELECT
    product_name,
    category,
    sub_category,
    ROUND(SUM(sales), 2)   AS sales,
    ROUND(SUM(profit), 2)  AS profit
FROM orders
GROUP BY product_name, category, sub_category
ORDER BY sales DESC
LIMIT 10;

-- 3.4 Top 10 products by profit
SELECT
    product_name,
    category,
    ROUND(SUM(profit), 2)  AS profit,
    ROUND(SUM(sales), 2)   AS sales
FROM orders
GROUP BY product_name, category
ORDER BY profit DESC
LIMIT 10;

-- 3.5 Bottom 10 products by profit (weak performers)
SELECT
    product_name,
    category,
    ROUND(SUM(profit), 2)  AS profit,
    ROUND(SUM(sales), 2)   AS sales
FROM orders
GROUP BY product_name, category
ORDER BY profit ASC
LIMIT 10;

-- 3.6 Most sold products (by units)
SELECT
    product_name,
    SUM(quantity)          AS units_sold,
    ROUND(SUM(sales), 2)   AS sales
FROM orders
GROUP BY product_name
ORDER BY units_sold DESC
LIMIT 10;

-- 3.7 Product performance ranked within category (window function RANK)
WITH product_perf AS (
    SELECT
        product_name,
        category,
        ROUND(SUM(sales), 2)  AS sales,
        ROUND(SUM(profit), 2) AS profit,
        RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS sales_rank_in_cat
    FROM orders
    GROUP BY product_name, category
)
SELECT *
FROM product_perf
WHERE sales_rank_in_cat <= 3
ORDER BY category, sales_rank_in_cat;

-- 3.8 Products above their category average sales (correlated subquery)
SELECT
    p1.product_name,
    p1.category,
    ROUND(p1.sales, 2)          AS product_sales,
    ROUND(p2.cat_avg_sales, 2)  AS category_avg_sales
FROM
    (SELECT product_name, category, SUM(sales) AS sales
     FROM orders GROUP BY product_name, category) p1
JOIN
    (SELECT category, AVG(sales) AS cat_avg_sales
     FROM (SELECT product_name, category, SUM(sales) AS sales
           FROM orders GROUP BY product_name, category) x
     GROUP BY category) p2
  ON p1.category = p2.category
WHERE p1.sales > p2.cat_avg_sales
ORDER BY p1.sales DESC
LIMIT 10;

-- ============================================================================
-- SECTION 4: CUSTOMER ANALYSIS
-- ============================================================================

-- 4.1 Number of unique customers
SELECT COUNT(DISTINCT customer_id) AS unique_customers FROM orders;

-- 4.2 Top 10 customers by revenue
SELECT
    customer_id,
    customer_name,
    COUNT(DISTINCT order_id)       AS orders,
    ROUND(SUM(sales), 2)           AS sales,
    ROUND(SUM(profit), 2)          AS profit
FROM orders
GROUP BY customer_id, customer_name
ORDER BY sales DESC
LIMIT 10;

-- 4.3 Top 10 customers by profit
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(profit), 2)  AS profit,
    ROUND(SUM(sales), 2)   AS sales
FROM orders
GROUP BY customer_id, customer_name
ORDER BY profit DESC
LIMIT 10;

-- 4.4 Highest-revenue customers above a threshold (GROUP BY + HAVING)
SELECT
    customer_id,
    customer_name,
    ROUND(SUM(sales), 2) AS sales,
    COUNT(DISTINCT order_id) AS orders
FROM orders
GROUP BY customer_id, customer_name
HAVING SUM(sales) > 5000
ORDER BY sales DESC
LIMIT 20;

-- 4.5 Customer segment performance
SELECT
    segment,
    COUNT(DISTINCT customer_id)   AS customers,
    COUNT(DISTINCT order_id)      AS orders,
    ROUND(SUM(sales), 2)          AS sales,
    ROUND(SUM(profit), 2)         AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY segment
ORDER BY sales DESC;

-- 4.6 Average order value by segment (AVG per order via subquery)
SELECT
    segment,
    ROUND(AVG(order_value), 2) AS avg_order_value
FROM (
    SELECT
        segment,
        order_id,
        SUM(sales) AS order_value
    FROM orders
    GROUP BY segment, order_id
) order_level
GROUP BY segment
ORDER BY avg_order_value DESC;

-- 4.7 Top customer per segment (window function ROW_NUMBER)
WITH customer_ranking AS (
    SELECT
        customer_id,
        customer_name,
        segment,
        ROUND(SUM(sales), 2) AS sales,
        ROW_NUMBER() OVER (PARTITION BY segment ORDER BY SUM(sales) DESC) AS rn
    FROM orders
    GROUP BY customer_id, customer_name, segment
)
SELECT customer_id, customer_name, segment, sales
FROM customer_ranking
WHERE rn = 1;

-- ============================================================================
-- SECTION 5: GEOGRAPHIC ANALYSIS
-- ============================================================================

-- 5.1 Region performance
SELECT
    region,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2)     AS sales,
    ROUND(SUM(profit), 2)    AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY region
ORDER BY sales DESC;

-- 5.2 State performance (top 10)
SELECT
    state,
    region,
    ROUND(SUM(sales), 2)  AS sales,
    ROUND(SUM(profit), 2) AS profit
FROM orders
GROUP BY state, region
ORDER BY sales DESC
LIMIT 10;

-- 5.3 City performance (top 10)
SELECT
    city,
    state,
    ROUND(SUM(sales), 2)  AS sales
FROM orders
GROUP BY city, state
ORDER BY sales DESC
LIMIT 10;

-- 5.4 Region performance grouped into performance tiers (CASE)
SELECT
    region,
    ROUND(SUM(sales), 2) AS sales,
    CASE
        WHEN SUM(sales) >= 1100000 THEN 'High Performing'
        WHEN SUM(sales) >= 1050000 THEN 'Medium Performing'
        ELSE 'Low Performing'
    END AS performance_tier
FROM orders
GROUP BY region
ORDER BY sales DESC;

-- ============================================================================
-- SECTION 6: DISCOUNT & PROFIT ANALYSIS
-- ============================================================================

-- 6.1 Impact of discount level on profit (CASE buckets)
SELECT
    CASE
        WHEN discount = 0                 THEN '0%'
        WHEN discount <= 0.20             THEN 'Up to 20%'
        WHEN discount <= 0.40             THEN '20-40%'
        ELSE                                   '40%+'
    END                                   AS discount_bucket,
    COUNT(DISTINCT order_id)              AS orders,
    ROUND(SUM(sales), 2)                  AS sales,
    ROUND(SUM(profit), 2)                 AS profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END)
          / COUNT(*) * 100, 2)            AS loss_rate_pct
FROM orders
GROUP BY discount_bucket
ORDER BY discount_bucket;

-- 6.2 Average discount by category (which categories discount the most)
SELECT
    category,
    ROUND(AVG(discount), 3) AS avg_discount,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_pct
FROM orders
GROUP BY category
ORDER BY avg_discount DESC;

-- 6.3 Products with the highest average discount
SELECT
    product_id,
    product_name,
    category,
    ROUND(AVG(discount), 3) AS avg_discount,
    ROUND(SUM(sales), 2)    AS sales,
    ROUND(SUM(profit), 2)   AS profit
FROM orders
GROUP BY product_id, product_name, category
ORDER BY avg_discount DESC
LIMIT 10;

-- 6.4 Profit margin correlation to discount (per-order metrics, summarized)
SELECT
    ROUND(AVG(discount), 3) AS avg_discount,
    ROUND(AVG(profit_margin_pct), 2) AS avg_profit_margin_pct,
    COUNT(*)                AS orders
FROM orders
GROUP BY discount
ORDER BY discount;

-- ============================================================================
-- SECTION 7: ADVANCED ANALYSIS
-- ============================================================================

-- 7.1 Monthly sales with running total & monthly growth (CTE + window functions)
WITH monthly AS (
    SELECT
        CONCAT(YEAR(order_date), '-', LPAD(CAST(MONTH(order_date) AS CHAR), 2, '0')) AS year_month,
        ROUND(SUM(sales), 2)  AS sales,
        ROUND(SUM(profit), 2) AS profit
    FROM orders
    GROUP BY CONCAT(YEAR(order_date), '-', LPAD(CAST(MONTH(order_date) AS CHAR), 2, '0'))
)
SELECT
    year_month,
    sales,
    profit,
    ROUND(SUM(sales) OVER (ORDER BY year_month), 2) AS running_sales,
    ROUND(sales - LAG(sales) OVER (ORDER BY year_month), 2) AS monthly_change
FROM monthly
ORDER BY year_month;

-- 7.2 Customer lifetime value (CTE + subquery) - average spend per customer
WITH customer_value AS (
    SELECT
        customer_id,
        customer_name,
        SUM(sales)           AS total_spend,
        COUNT(DISTINCT order_id) AS orders,
        ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
    FROM orders
    GROUP BY customer_id, customer_name
)
SELECT
    CASE
        WHEN total_spend >= 15000 THEN 'Platinum'
        WHEN total_spend >= 8000  THEN 'Gold'
        WHEN total_spend >= 3000  THEN 'Silver'
        ELSE                           'Bronze'
    END AS customer_tier,
    COUNT(*) AS customers,
    ROUND(SUM(total_spend), 2) AS tier_revenue
FROM customer_value
GROUP BY customer_tier
ORDER BY tier_revenue DESC;

-- 7.3 Category preference by segment (CROSS-sectional JOIN of aggregates)
SELECT
    segment,
    category,
    ROUND(SUM(sales), 2)     AS sales,
    ROUND(SUM(sales) / SUM(SUM(sales)) OVER (PARTITION BY segment) * 100, 2)
                             AS pct_of_segment
FROM orders
GROUP BY segment, category
ORDER BY segment, sales DESC;

-- 7.4 Monthly sales heatmap data (Year x Month matrix for the dashboard)
SELECT
    YEAR(order_date)  AS year,
    MONTH(order_date) AS month,
    ROUND(SUM(sales), 2) AS sales
FROM orders
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY year, month;

-- ============================================================================
-- SECTION 8: BUSINESS QUESTIONS (summary view)
-- ============================================================================

-- Every business question answered in a single result set
SELECT 'Total revenue'                                  AS question,
       ROUND(SUM(sales), 2)                             AS answer
FROM orders
UNION ALL SELECT 'Total profit', ROUND(SUM(profit), 2) FROM orders
UNION ALL SELECT 'Best category by revenue',
       (SELECT category FROM orders GROUP BY category ORDER BY SUM(sales) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Best category by profit',
       (SELECT category FROM orders GROUP BY category ORDER BY SUM(profit) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Product with highest sales',
       (SELECT product_name FROM orders GROUP BY product_name ORDER BY SUM(sales) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Product with lowest profit',
       (SELECT product_name FROM orders GROUP BY product_name ORDER BY SUM(profit) ASC LIMIT 1) FROM orders
UNION ALL SELECT 'Customer with highest revenue',
       (SELECT customer_name FROM orders GROUP BY customer_name ORDER BY SUM(sales) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Best region by sales',
       (SELECT region FROM orders GROUP BY region ORDER BY SUM(sales) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Peak sales month',
       (SELECT MONTH(order_date) FROM orders GROUP BY MONTH(order_date) ORDER BY SUM(sales) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Peak profit month',
       (SELECT MONTH(order_date) FROM orders GROUP BY MONTH(order_date) ORDER BY SUM(profit) DESC LIMIT 1) FROM orders
UNION ALL SELECT 'Average order value',
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) FROM orders
UNION ALL SELECT 'Best customer segment',
       (SELECT segment FROM orders GROUP BY segment ORDER BY SUM(sales) DESC LIMIT 1) FROM orders;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
