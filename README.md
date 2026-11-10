# Savyant Sales and Inventory Management System

A Flask and MySQL-based Sales and Inventory Management System designed to manage customers, products, sales orders, inventory, and business reports.

## 1. Project Overview

The Savyant Sales and Inventory Management System helps businesses manage their daily sales and inventory operations through REST APIs.

The system supports role-based access for administrators and sales users. It also maintains stock movement history and provides sales and inventory reports.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | REST API development |
| MySQL | Relational database |
| PyMySQL | Python-MySQL connectivity |
| HTML, CSS, JavaScript | Planned frontend |
| Git and GitHub | Version control |
| Pytest | Testing framework |
| CSV | Bulk product import |

## 3. Main Features

### Authentication and Authorization
- User registration and login.
- Secure password hashing.
- Session-based authentication.
- Admin and Sales roles.
- Role-based API access.

### Customer Management
- Add new customers.
- View customer information.
- Update customer details.
- Activate or deactivate customers.

### Product Management
- Add and update products.
- View product details.
- Activate or deactivate products.
- Adjust stock quantities.
- Prevent negative inventory.

### Sales Order Management
- Create draft sales orders.
- Confirm sales orders.
- Cancel sales orders.
- Apply discounts between 0% and 20%.
- Calculate order totals using decimal arithmetic.
- Automatically deduct stock when an order is confirmed.
- Restore stock when a confirmed order is cancelled.
- Prevent duplicate confirmation and cancellation.

### Stock Movement History
- Record opening stock.
- Record stock increases and decreases.
- Record order deductions and restorations.
- View stock movement history.

### Reports
- Customer-wise sales report.
- Product-wise sales report.
- Low-stock product report.

### CSV Product Import
- Import multiple products using CSV files.
- Validate product details and stock quantities.
- Detect duplicate product codes.
- Prevent partial imports when validation fails.
- Record opening stock movements.

## 4. Database Structure

The application uses a MySQL database named `savyant_inventory`.

It contains six main tables:

| Table | Description |
|---|---|
| users | Stores user accounts and roles |
| customers | Stores customer information |
| products | Stores product details and stock |
| sales_orders | Stores sales order information |
| sales_order_items | Stores products included in orders |
| stock_movements | Maintains inventory movement history |

Database schema: `database/schema.sql`

Required SQL queries: `database/queries.sql`

## 5. Project Structure

```text
savyant_sales_inventory/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── database/
│   ├── __init__.py
│   ├── db.py
│   ├── schema.sql
│   ├── queries.sql
│   └── test_db.py
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── customers.py
│   ├── products.py
│   ├── orders.py
│   ├── product_import.py
│   ├── stock_movements.py
│   └── reports.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── auth_decorators.py
│   ├── customer_service.py
│   ├── product_service.py
│   ├── order_service.py
│   ├── csv_import_service.py
│   ├── stock_service.py
│   ├── report_service.py
│   └── test_auth.py
│
├── sample_data/
│   ├── products_valid.csv
│   └── products_invalid.csv
│
└── README.md
```

## 6. Installation and Setup

### Prerequisites

Install the following:

- Python
- MySQL Server
- MySQL Workbench (recommended)
- Git

### Step 1: Clone the repository

```bash
git clone https://github.com/udaysai-kandregula/savyant_sales_inventory.git
```

Navigate into the project:

```bash
cd savyant_sales_inventory
```

### Step 2: Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows Git Bash:

```bash
source venv/Scripts/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

## 7. Database Configuration

Open MySQL Workbench and create the database:

```sql
CREATE DATABASE savyant_inventory;
```

Select and execute the SQL script:

```text
database/schema.sql
```

This creates the six required database tables.

## 8. Environment Configuration

Copy the example file to `.env` in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your own MySQL configuration:

```env
SECRET_KEY=your_secure_secret_key

DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=savyant_inventory
DB_PORT=3306
```

Replace the example values with your local configuration.

**Important:** Never commit `.env` or expose database credentials on GitHub.

## 9. Run the Application

Activate the virtual environment:

```bash
source venv/Scripts/activate
```

Start the Flask application:

```bash
python app.py
```

The application runs locally at:

```text
http://127.0.0.1:5000
```

## 10. Application Routes

### General Routes

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application home |
| GET | `/health` | Application health check |

### Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a sales user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Get logged-in user |


### Customer APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/customers` | Create customer |
| GET | `/api/customers` | List customers |
| GET | `/api/customers/<id>` | Get customer |
| PUT | `/api/customers/<id>` | Update customer |
| PATCH | `/api/customers/<id>/status` | Change customer status |

### Product APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/products` | Create product |
| GET | `/api/products` | List products |
| GET | `/api/products/<id>` | Get product |
| PUT | `/api/products/<id>` | Update product |
| PATCH | `/api/products/<id>/status` | Change product status |
| POST | `/api/products/<id>/stock-adjustment` | Adjust stock |
| POST | `/api/products/import` | Import products using CSV |

### Sales Order APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/orders` | Create draft order |
| GET | `/api/orders/<id>` | Get order details |
| POST | `/api/orders/<id>/confirm` | Confirm order |
| POST | `/api/orders/<id>/cancel` | Cancel order |

### Stock Movement APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/stock-movements` | View stock movement history |

Optional filters include `product_id`, `movement_type`, and `limit`.

### Reports APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/customer-sales` | Customer sales report |
| GET | `/api/reports/product-sales` | Product sales report |
| GET | `/api/reports/low-stock` | Low-stock report |

Example:

```text
/api/reports/low-stock?threshold=5
```

All APIs use JSON responses unless the endpoint handles file uploads.

Authentication and role permissions apply to protected endpoints.

## 11. Business Rules

- Product stock cannot become negative.
- Product quantities must be whole numbers.
- Monetary values use decimal precision.
- Discounts must be between 0% and 20%.
- Draft orders do not affect inventory.
- Confirmed orders deduct stock.
- Cancelling confirmed orders restores stock.
- Cancelling draft orders does not affect stock.
- Stock changes are recorded in stock movement history.
- Customer and product records are deactivated instead of deleted.
- Sales reports consider confirmed orders.


## 12. Testing

### Python Syntax Validation

Run the following command to check Python syntax:

```bash
python -m py_compile app.py routes/*.py services/*.py
```

### Manual API Testing

The application has been tested manually using curl.

Integration checks covered:

- Application health and authentication.
- Admin and Sales role permissions.
- Customer CRUD operations.
- Product management and stock adjustments.
- Stock movement history.
- Sales order creation, confirmation and cancellation.
- Reports and SQL queries.
- CSV import validation and authorization.

### Automated Testing

The project includes automated pytest coverage for authentication, authorization, validation, reports, CSV imports, CSRF protection, rate limiting and sales-order ownership. Run the test suite using:

```bash
python -m pytest -v
```


## 13. Git and Version Control

The project uses Git feature branches for development.

Main branch:

```text
main
```

Feature branches include:

- feature/authorization
- feature/customer-management
- feature/product-management
- feature/sales-order-management
- feature/reports
- feature/sql-queries
- feature/csv-import

## 14. Future Improvements

- Develop a responsive web frontend.
- Integrate frontend pages with Flask REST APIs.
- Add dashboard visualizations.
- Improve reporting and export capabilities.

## 15. Author

**Project:** Savyant Sales and Inventory Management System

**Repository:** [GitHub - savyant_sales_inventory](https://github.com/udaysai-kandregula/savyant_sales_inventory)
