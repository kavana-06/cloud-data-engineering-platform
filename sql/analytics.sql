-- ============================================================
-- Cloud Data Engineering & Analytics Platform
-- Analytics SQL Layer
-- ============================================================

USE cloud_analytics;


-- ============================================================
-- 1. Core Business KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_sales_records,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(profit) / SUM(sales) * 100, 2) AS profit_margin_percentage,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value
FROM fact_sales;


-- ============================================================
-- 2. Sales & Profit by Category
-- ============================================================

SELECT
    dp.category,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_product dp
    ON fs.product_key = dp.product_key
GROUP BY dp.category
ORDER BY total_sales DESC;


-- ============================================================
-- 3. Sales & Profit by Region
-- ============================================================

SELECT
    dl.region,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_location dl
    ON fs.location_key = dl.location_key
GROUP BY dl.region
ORDER BY total_sales DESC;


-- ============================================================
-- 4. Yearly Sales & Profit Trend
-- ============================================================

SELECT
    dd.year,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_date dd
    ON fs.date_key = dd.date_key
GROUP BY dd.year
ORDER BY dd.year;


-- ============================================================
-- 5. Monthly Sales Trend
-- ============================================================

SELECT
    dd.year,
    dd.month,
    dd.month_name,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_date dd
    ON fs.date_key = dd.date_key
GROUP BY
    dd.year,
    dd.month,
    dd.month_name
ORDER BY
    dd.year,
    dd.month;


-- ============================================================
-- 6. Top 10 Products by Sales
-- ============================================================

SELECT
    dp.product_name,
    dp.category,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_product dp
    ON fs.product_key = dp.product_key
GROUP BY
    dp.product_name,
    dp.category
ORDER BY total_sales DESC
LIMIT 10;


-- ============================================================
-- 7. Top 10 Products by Profit
-- ============================================================

SELECT
    dp.product_name,
    dp.category,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_product dp
    ON fs.product_key = dp.product_key
GROUP BY
    dp.product_name,
    dp.category
ORDER BY total_profit DESC
LIMIT 10;


-- ============================================================
-- 8. Loss-Making Products
-- ============================================================

SELECT
    dp.product_name,
    dp.category,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_product dp
    ON fs.product_key = dp.product_key
GROUP BY
    dp.product_name,
    dp.category
HAVING SUM(fs.profit) < 0
ORDER BY total_profit ASC
LIMIT 10;


-- ============================================================
-- 9. Sales & Profit by Segment
-- ============================================================

SELECT
    dc.segment,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit
FROM fact_sales fs
JOIN dim_customer dc
    ON fs.customer_key = dc.customer_key
GROUP BY dc.segment
ORDER BY total_sales DESC;


-- ============================================================
-- 10. Sales by Ship Mode
-- ============================================================

SELECT
    fs.ship_mode,
    ROUND(SUM(fs.sales), 2) AS total_sales,
    ROUND(SUM(fs.profit), 2) AS total_profit,
    SUM(fs.quantity) AS total_quantity
FROM fact_sales fs
GROUP BY fs.ship_mode
ORDER BY total_sales DESC;
