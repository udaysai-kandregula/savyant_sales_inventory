
-- Savyant Sales and Inventory Management System
-- Database: savyant_inventory

USE savyant_inventory;

-- 1. USERS
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'sales') NOT NULL DEFAULT 'sales',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- 2. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    mobile VARCHAR(20),
    city VARCHAR(100),
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_name (name),
    INDEX idx_customer_status (status)
) ENGINE=InnoDB;


-- 3. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(12,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_product_price CHECK (price >= 0),
    CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0),

    INDEX idx_product_name (name),
    INDEX idx_product_status (status)
) ENGINE=InnoDB;


-- 4. SALES ORDERS
CREATE TABLE IF NOT EXISTS sales_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status ENUM('draft', 'confirmed', 'cancelled')
        NOT NULL DEFAULT 'draft',
    discount_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    grand_total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_order_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_order_discount
        CHECK (discount_percentage BETWEEN 0 AND 20),

    CONSTRAINT chk_order_subtotal CHECK (subtotal >= 0),
    CONSTRAINT chk_order_discount_amount CHECK (discount_amount >= 0),
    CONSTRAINT chk_order_grand_total CHECK (grand_total >= 0),

    INDEX idx_order_customer (customer_id),
    INDEX idx_order_status (status),
    INDEX idx_order_date (order_date),
    INDEX idx_order_creator (created_by)
) ENGINE=InnoDB;


-- 5. SALES ORDER ITEMS
CREATE TABLE IF NOT EXISTS sales_order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    rate DECIMAL(12,2) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,

    CONSTRAINT fk_item_order
        FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_item_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_item_quantity CHECK (quantity > 0),
    CONSTRAINT chk_item_rate CHECK (rate >= 0),
    CONSTRAINT chk_item_amount CHECK (amount >= 0),

    INDEX idx_item_order (sales_order_id),
    INDEX idx_item_product (product_id)
) ENGINE=InnoDB;


-- 6. STOCK MOVEMENTS
CREATE TABLE IF NOT EXISTS stock_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,

    movement_type ENUM(
        'opening',
        'adjustment_in',
        'adjustment_out',
        'order_deduction',
        'order_restoration'
    ) NOT NULL,

    quantity_change INT NOT NULL,
    related_order_id INT NULL,
    reason VARCHAR(255) NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_movement_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_movement_order
        FOREIGN KEY (related_order_id) REFERENCES sales_orders(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_movement_user
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_movement_quantity CHECK (quantity_change <> 0),

    INDEX idx_movement_product (product_id),
    INDEX idx_movement_order (related_order_id),
    INDEX idx_movement_date (created_at)
) ENGINE=InnoDB;
