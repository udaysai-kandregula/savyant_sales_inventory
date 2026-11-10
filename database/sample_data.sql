-- ==========================================
-- Optional Demonstration Records
-- ==========================================
-- Run after schema.sql.
-- These inserts are safe to re-run without
-- creating duplicate product codes.


-- ==========================================
-- Insert Demo Customers
-- ==========================================

INSERT INTO customers (
    name,
    email,
    mobile,
    city,
    status
)
VALUES
    (
        'Aarav Technologies',
        'aarav@example.test',
        '9000000001',
        'Guntur',
        'active'
    ),
    (
        'Green Leaf Stores',
        'greenleaf@example.test',
        '9000000002',
        'Vijayawada',
        'active'
    ),
    (
        'Sunrise Traders',
        'sunrise@example.test',
        '9000000003',
        'Tenali',
        'active'
    );


-- ==========================================
-- Insert Demo Products
-- ==========================================

INSERT INTO products (
    product_code,
    name,
    category,
    price,
    stock_quantity,
    status
)
VALUES
    (
        'DEMO001',
        'Wireless Mouse',
        'Accessories',
        750.00,
        20,
        'active'
    ),
    (
        'DEMO002',
        'Mechanical Keyboard',
        'Accessories',
        2500.00,
        15,
        'active'
    ),
    (
        'DEMO003',
        'USB Hub',
        'Accessories',
        1200.00,
        10,
        'active'
    )

ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    category = VALUES(category),
    price = VALUES(price),
    stock_quantity = VALUES(stock_quantity),
    status = VALUES(status);