# Savyant Systems – Sales & Inventory Management System
# API Documentation

## 1. Introduction

This document describes the REST APIs available in the Savyant Systems Sales & Inventory Management System.

**Base URL (local development):**
`http://127.0.0.1:5000`

**Backend:** Python Flask  
**Database:** MySQL  
**Request format:** JSON (except CSV import)  
**Authentication:** Session-based authentication using cookies.

## 2. Authentication and Permissions

The system supports two user roles:

| Role | Permissions |
|---|---|
| Admin | Full administrative access |
| Sales | Access to permitted customer, product, order, report and stock history operations |

Protected APIs require a valid login session. After login, the session cookie must be included in subsequent requests.

### Authentication endpoints

#### 2.1 Register User

- **Method:** POST
- **Endpoint:** `/api/auth/register`
- **Access:** Public

Creates a new user account.

#### 2.2 Login

- **Method:** POST
- **Endpoint:** `/api/auth/login`
- **Access:** Public

Authenticates a user and creates a session.

#### 2.3 Logout

- **Method:** POST
- **Endpoint:** `/api/auth/logout`
- **Access:** Login required

Logs out the current user and clears the session.

#### 2.4 Get Current User

- **Method:** GET
- **Endpoint:** `/api/auth/me`
- **Access:** Login required

Returns information about the currently logged-in user.

## 3. Customer Management APIs

Base endpoint: `/api/customers`

### 3.1 Create Customer

- **Method:** POST
- **Access:** Admin only

Request body:

```json
{
  "name": "ABC Technologies Pvt Ltd",
  "email": "abc@example.com",
  "mobile": "9876543210",
  "city": "Guntur"
}
```

Required:
- `name`

Optional:
- `email`
- `mobile`
- `city`

### 3.2 Get All Customers

- **Method:** GET
- **Endpoint:** `/api/customers`
- **Access:** Login required

Returns the customer list.

### 3.3 Get Customer by ID

- **Method:** GET
- **Endpoint:** `/api/customers/{customer_id}`
- **Access:** Login required

Example: `/api/customers/1`

### 3.4 Update Customer

- **Method:** PUT
- **Endpoint:** `/api/customers/{customer_id}`
- **Access:** Admin only

Request body:

```json
{
  "name": "ABC Technologies Updated",
  "email": "updated@example.com",
  "mobile": "9876543210",
  "city": "Vijayawada"
}
```

### 3.5 Change Customer Status

- **Method:** PATCH
- **Endpoint:** `/api/customers/{customer_id}/status`
- **Access:** Admin only

Request body:

```json
{
  "status": "inactive"
}
```

Allowed values: `active`, `inactive`.

## 4. Product Management APIs

Base endpoint: `/api/products`

### 4.1 Create Product

- **Method:** POST
- **Endpoint:** `/api/products`
- **Access:** Admin only

Request body:

```json
{
  "product_code": "LAP001",
  "name": "Dell Laptop",
  "category": "Electronics",
  "price": 58000.00,
  "stock_quantity": 10
}
```

Required:
- `product_code`
- `name`
- `price`

Optional:
- `category`
- `stock_quantity` (defaults to 0)

Validation:
- Price must be non-negative.
- Price supports up to two decimal places.
- Stock must be a non-negative whole number.
- Product code must be unique.

### 4.2 Get All Products

- **Method:** GET
- **Endpoint:** `/api/products`
- **Access:** Login required

Returns the product list, count and product details.

### 4.3 Get Product by ID

- **Method:** GET
- **Endpoint:** `/api/products/{product_id}`
- **Access:** Login required

### 4.4 Update Product

- **Method:** PUT
- **Endpoint:** `/api/products/{product_id}`
- **Access:** Admin only

Request body:

```json
{
  "name": "Updated Dell Laptop",
  "category": "Computers",
  "price": 47000.00
}
```

Required:
- `name`
- `price`

Optional:
- `category`

### 4.5 Change Product Status

- **Method:** PATCH
- **Endpoint:** `/api/products/{product_id}/status`
- **Access:** Admin only

Request body:

```json
{
  "status": "inactive"
}
```

Allowed values: `active`, `inactive`.

### 4.6 Adjust Product Stock

- **Method:** POST
- **Endpoint:** `/api/products/{product_id}/stock-adjustment`
- **Access:** Admin only

Request body:

```json
{
  "adjustment_type": "increase",
  "quantity": 5,
  "reason": "New stock received"
}
```

Allowed adjustment types:
- `increase`
- `decrease`

Quantity must be a positive whole number. Decreasing stock below zero is not allowed.

Stock adjustments are recorded in the stock movement history.

## 5. Sales Order Management APIs

Base endpoint: `/api/orders`

### 5.1 Create Draft Order

- **Method:** POST
- **Endpoint:** `/api/orders`
- **Access:** Login required

Request body:

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 7,
      "quantity": 2
    }
  ],
  "discount_percentage": 5
}
```

Fields:
- `customer_id`: Positive customer ID.
- `items`: Non-empty array of order items.
- `product_id`: Positive product ID.
- `quantity`: Positive whole number.
- `discount_percentage`: Optional; defaults to 0 and must be between 0 and 20.

Business rules:
- Duplicate products are not allowed in one order.
- Customer must exist and be active.
- Products must exist and be active.
- Product price is stored as a snapshot in the order item.
- Creating a draft order does not deduct stock.

### 5.2 Get Order Details

- **Method:** GET
- **Endpoint:** `/api/orders/{order_id}`
- **Access:** Login required

Returns order information and its items.

### 5.3 Confirm Order

- **Method:** POST
- **Endpoint:** `/api/orders/{order_id}/confirm`
- **Access:** Login required

Confirms a draft order.

Business rules:
- Stock is checked before confirmation.
- Stock is deducted when the order is confirmed.
- Insufficient stock prevents confirmation.
- Confirmation is protected against duplicate execution.
- Stock changes and movement records are handled transactionally.

### 5.4 Cancel Order

- **Method:** POST
- **Endpoint:** `/api/orders/{order_id}/cancel`
- **Access:** Login required

Cancels an order.

Business rules:
- Cancelling a confirmed order restores stock.
- Cancelling a draft order does not change stock.
- Stock restoration is recorded in stock movement history.
- Duplicate cancellation is prevented.

## 6. Stock Movement History API

Base endpoint: `/api/stock-movements`

### 6.1 Get Stock Movements

- **Method:** GET
- **Endpoint:** `/api/stock-movements`
- **Access:** Login required

Optional query parameters:

| Parameter | Description |
|---|---|
| `product_id` | Filter by product ID |
| `movement_type` | Filter by movement type |
| `limit` | Number of records; default 100, maximum 500 |

Example:

`GET /api/stock-movements?product_id=7&limit=50`

Supported movement types:
- `opening`
- `adjustment_in`
- `adjustment_out`
- `order_deduction`
- `order_restoration`

The response contains:
- `success`
- `count`
- `movements`

## 7. Reports APIs

Base endpoint: `/api/reports`

All report endpoints require login.

### 7.1 Customer Sales Report

- **Method:** GET
- **Endpoint:** `/api/reports/customer-sales`

Returns customer sales information based on confirmed orders.

Customers without orders are also included.

### 7.2 Product Sales Report

- **Method:** GET
- **Endpoint:** `/api/reports/product-sales`

Returns product sales information based on confirmed orders.

### 7.3 Low Stock Report

- **Method:** GET
- **Endpoint:** `/api/reports/low-stock`

Optional query parameter:

| Parameter | Default | Description |
|---|---:|---|
| `threshold` | 5 | Maximum stock quantity to include |

Example:

`GET /api/reports/low-stock?threshold=10`

Threshold must be a non-negative whole number.

## 8. CSV Product Import API

### 8.1 Import Products

- **Method:** POST
- **Endpoint:** `/api/products/import`
- **Access:** Admin only
- **Content-Type:** `multipart/form-data`

Form field:
- `file`: CSV file to upload.

Required CSV headers, in this exact order:

```csv
product_code,name,category,price,stock_quantity
```

Example CSV:

```csv
product_code,name,category,price,stock_quantity
CSV001,Wireless Mouse,Accessories,750.00,20
CSV002,Mechanical Keyboard,Accessories,2500.00,15
CSV003,USB Hub,Accessories,1200.00,10
CSV004,Monitor Stand,Accessories,1800.00,0
```

Validation rules:
- File must have a `.csv` extension.
- File must not be empty.
- File must use UTF-8 encoding.
- Required headers must match.
- Product code and name are required.
- Duplicate product codes in the file are rejected.
- Existing product codes are rejected.
- Price must be non-negative with up to two decimal places.
- Stock must be a non-negative whole number.
- All rows are validated before insertion.

Business rules:
- Import is all-or-nothing.
- If validation or database insertion fails, no partial import is committed.
- Products are created with active status.
- Positive opening stock creates an `opening` stock movement record.
- Zero opening stock does not create a stock movement.

Successful response includes:
- `success`
- `message`
- `total_imported`
- `products`

## 9. Common HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Request successful |
| 201 | Resource created successfully |
| 400 | Invalid request or validation error |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict, such as duplicate product code |
| 500 | Internal server error |

## 10. Example API Testing with cURL

### Login

```bash
curl -i -c cookies.txt \
-X POST http://127.0.0.1:5000/api/auth/login \
-H "Content-Type: application/json" \
-d '{"email":"admin@example.com","password":"your_password"}'
```

### Get Products

```bash
curl -i -b cookies.txt \
http://127.0.0.1:5000/api/products
```

### Create Customer

```bash
curl -i -b cookies.txt \
-X POST http://127.0.0.1:5000/api/customers \
-H "Content-Type: application/json" \
-d '{"name":"ABC Technologies Pvt Ltd","city":"Guntur"}'
```

### Import CSV

```bash
curl -i -b cookies.txt \
-X POST http://127.0.0.1:5000/api/products/import \
-F "file=@sample_data/products_valid.csv"
```

### Get Low Stock Report

```bash
curl -i -b cookies.txt \
"http://127.0.0.1:5000/api/reports/low-stock?threshold=5"
```

Replace the example login credentials with a valid admin account.

## 11. Important Business Rules

1. Monetary calculations use Python `Decimal` and MySQL `DECIMAL`.
2. Quantity values must be whole numbers.
3. Order discounts cannot exceed 20%.
4. Draft orders do not deduct stock.
5. Confirmed orders deduct stock.
6. Cancelling confirmed orders restores stock.
7. Stock cannot become negative.
8. Stock changes are recorded in stock movement history.
9. Product and customer records are deactivated instead of deleted.
10. Order item rates are stored as price snapshots.
11. Reports calculate sales using confirmed orders.
12. CSV imports use transaction-based all-or-nothing processing.

## 12. Conclusion

The API provides authentication, customer management, product management, sales order processing, stock movement tracking, reporting and CSV product import.

All protected endpoints use session-based authentication and role-based access control.