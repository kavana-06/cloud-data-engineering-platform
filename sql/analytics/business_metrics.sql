USE cloud_analytics;

-- =========================================================
-- 1. Overall Business Metrics
-- =========================================================

SELECT
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_key) AS total_customers,
    ROUND(
        SUM(profit) / SUM(sales) * 100,
        2
    ) AS profit_margin_percentage
FROM fact_sales;


-- =========================================================
-- 2. Revenue and Profit by Year
-- =========================================================

SELECT
    d.year,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY d.year
ORDER BY d.year;


-- =========================================================
-- 3. Sales by Region
-- =========================================================

SELECT
    l.region,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    SUM(f.quantity) AS total_quantity
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.region
ORDER BY total_sales DESC;


-- =========================================================
-- 4. Sales by Category
-- =========================================================

SELECT
    p.category,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    SUM(f.quantity) AS total_quantity
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_sales DESC;


-- =========================================================
-- 5. Sales by Sub-Category
-- =========================================================

SELECT
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.category,
    p.sub_category
ORDER BY total_sales DESC;


-- =========================================================
-- 6. Top 10 Products by Sales
-- =========================================================

SELECT
    p.product_id,
    p.product_name,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_name
ORDER BY total_sales DESC
LIMIT 10;


-- =========================================================
-- 7. Top 10 Customers by Sales
-- =========================================================

SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_key = c.customer_key
GROUP BY
    c.customer_id,
    c.customer_name,
    c.segment
ORDER BY total_sales DESC
LIMIT 10;


-- =========================================================
-- 8. Monthly Sales Trend
-- =========================================================

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- =========================================================
-- 9. Average Order Value
-- =========================================================

SELECT
    ROUND(
        SUM(sales) / COUNT(DISTINCT order_id),
        2
    ) AS average_order_value
FROM fact_sales;


-- =========================================================
-- 10. Most Profitable Products
-- =========================================================

SELECT
    p.product_id,
    p.product_name,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY
    p.product_id,
    p.product_name
ORDER BY total_profit DESC
LIMIT 10;
