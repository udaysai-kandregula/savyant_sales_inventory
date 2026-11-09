
-- =====================================================
-- SAVYANT SALES AND INVENTORY MANAGEMENT SYSTEM
-- FIVE REQUIRED SQL QUERIES
-- =====================================================


-- 1. TOP 3 CUSTOMERS BY CONFIRMED SALES AMOUNT
-- Shows the three customers who generated the highest sales.

SELECT
    c.id AS customer_id,
    c.name AS customer_name,
    c.email,
    COUNT(so.id) AS total_orders,
    SUM(so.grand_total) AS total_sales
FROM customers c
INNER JOIN sales_orders so
    ON c.id = so.customer_id
WHERE so.status = 'confirmed'
GROUP BY c.id, c.name, c.email
ORDER BY total_sales DESC
LIMIT 3;


-- =====================================================
-- 2. TOP 3 PRODUCTS BY CONFIRMED QUANTITY SOLD
-- Shows the three most-sold products.

SELECT
    p.id AS product_id,
    p.product_code,
    p.name AS product_name,
    SUM(soi.quantity) AS total_quantity_sold,
    SUM(soi.amount) AS total_sales
FROM products p
INNER JOIN sales_order_items soi
    ON p.id = soi.product_id
INNER JOIN sales_orders so
    ON soi.sales_order_id = so.id
WHERE so.status = 'confirmed'
GROUP BY p.id, p.product_code, p.name
ORDER BY total_quantity_sold DESC
LIMIT 3;


-- =====================================================
-- 3. CUSTOMERS WHO HAVE NEVER PLACED AN ORDER
-- Includes customers without any sales order, regardless
-- of whether orders are draft, confirmed, or cancelled.

SELECT
    c.id AS customer_id,
    c.name AS customer_name,
    c.email,
    c.mobile,
    c.city
FROM customers c
LEFT JOIN sales_orders so
    ON c.id = so.customer_id
WHERE so.id IS NULL
ORDER BY c.name;


-- =====================================================
-- 4. MONTHLY CONFIRMED SALES
-- Shows confirmed sales grouped by month.

SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
    COUNT(id) AS total_orders,
    SUM(subtotal) AS total_subtotal,
    SUM(discount_amount) AS total_discount,
    SUM(grand_total) AS total_sales
FROM sales_orders
WHERE status = 'confirmed'
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY sales_month DESC;


-- =====================================================
-- 5. PRODUCTS BELOW A GIVEN STOCK THRESHOLD
-- Change the threshold value (5) as required.

SET @stock_threshold = 5;

SELECT
    id AS product_id,
    product_code,
    name AS product_name,
    category,
    stock_quantity,
    price
FROM products
WHERE stock_quantity < @stock_threshold
ORDER BY stock_quantity ASC, name ASC;
