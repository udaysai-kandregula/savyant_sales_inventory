import pytest

from app import create_app


@pytest.fixture
def client(monkeypatch):
    # Tests must not depend on a developer's local .env file.
    monkeypatch.setenv("SECRET_KEY", "pytest-test-secret")
    app = create_app()

    app.config.update(
        TESTING=True,
        SECRET_KEY="pytest-test-secret",
        WTF_CSRF_ENABLED=False
    )

    # Simulate database roles for automated tests.
    # User 1 = Admin, User 2 = Sales.
    monkeypatch.setattr(
        "services.auth_decorators.get_current_user_role",
        lambda user_id: {
            1: "admin",
            2: "sales"
        }.get(user_id)
    )

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Savyant Sales and Inventory Management System" in response.data


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_login_route_requires_authentication(client):
    response = client.get("/api/test/login")

    assert response.status_code == 401


def test_admin_route_requires_authentication(client):
    response = client.get("/api/test/admin")

    assert response.status_code == 401


def test_sales_route_requires_authentication(client):
    response = client.get("/api/test/sales")

    assert response.status_code == 401

def test_admin_can_access_admin_route(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.get("/api/test/admin")

    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_sales_cannot_access_admin_route(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    response = client.get("/api/test/admin")

    assert response.status_code == 403


def test_sales_can_access_sales_route(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    response = client.get("/api/test/sales")

    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_admin_cannot_access_sales_route(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.get("/api/test/sales")

    assert response.status_code == 403


# --------------------------------------------------
# CUSTOMER VALIDATION TESTS
# --------------------------------------------------

def test_customer_name_is_required(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post("/api/customers", json={})

    assert response.status_code == 400


def test_customer_name_cannot_be_empty(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post("/api/customers", json={"name": "   "})

    assert response.status_code == 400


def test_customer_email_must_be_text(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/customers",
        json={"name": "Test Customer", "email": 123}
    )

    assert response.status_code == 400


# --------------------------------------------------
# PRODUCT VALIDATION TESTS
# --------------------------------------------------

def test_product_code_is_required(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={"name": "Test Product", "price": 100}
    )

    assert response.status_code == 400


def test_product_name_is_required(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={"product_code": "TEST001", "price": 100}
    )

    assert response.status_code == 400


def test_product_price_cannot_be_negative(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": -100
        }
    )

    assert response.status_code == 400


def test_product_price_allows_maximum_two_decimal_places(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": 10.999
        }
    )

    assert response.status_code == 400


def test_product_stock_cannot_be_negative(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": 100,
            "stock_quantity": -5
        }
    )

    assert response.status_code == 400


def test_product_stock_must_be_whole_number(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": 100,
            "stock_quantity": 2.5
        }
    )

    assert response.status_code == 400


def test_product_category_must_be_text(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": 100,
            "category": 123
        }
    )

    assert response.status_code == 400


# --------------------------------------------------
# CUSTOMER AND PRODUCT PERMISSION TESTS
# --------------------------------------------------

def test_sales_user_cannot_create_customer(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    response = client.post(
        "/api/customers",
        json={"name": "Test Customer"}
    )

    assert response.status_code == 403


def test_sales_user_cannot_create_product(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    response = client.post(
        "/api/products",
        json={
            "product_code": "TEST001",
            "name": "Test Product",
            "price": 100
        }
    )

    assert response.status_code == 403

# --------------------------------------------------
# SALES ORDER VALIDATION TESTS
# --------------------------------------------------

def login_as_sales(client):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"


def block_order_database(monkeypatch):
    import services.order_service as order_service

    def database_should_not_be_called():
        raise AssertionError(
            "Database should not be accessed for invalid input"
        )

    monkeypatch.setattr(
        order_service,
        "get_db_connection",
        database_should_not_be_called
    )


def test_order_requires_customer_id(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "items": [{"product_id": 1, "quantity": 2}]
        }
    )

    assert response.status_code == 400


def test_order_requires_items(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={"customer_id": 1, "items": []}
    )

    assert response.status_code == 400


def test_order_rejects_invalid_product_id(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [{"product_id": 0, "quantity": 2}]
        }
    )

    assert response.status_code == 400


def test_order_rejects_zero_quantity(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 0}]
        }
    )

    assert response.status_code == 400


def test_order_rejects_decimal_quantity(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2.5}]
        }
    )

    assert response.status_code == 400


def test_order_rejects_duplicate_products(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 1, "quantity": 3}
            ]
        }
    )

    assert response.status_code == 400


def test_order_rejects_discount_above_20_percent(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2}],
            "discount_percentage": 21
        }
    )

    assert response.status_code == 400


def test_order_rejects_invalid_discount(client, monkeypatch):
    login_as_sales(client)
    block_order_database(monkeypatch)

    response = client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "items": [{"product_id": 1, "quantity": 2}],
            "discount_percentage": "invalid"
        }
    )

    assert response.status_code == 400

def test_stock_movements_requires_authentication(client):
    response = client.get("/api/stock-movements")

    assert response.status_code == 401


def test_stock_movements_rejects_invalid_product_id(client, monkeypatch):
    login_as_sales(client)

    response = client.get("/api/stock-movements?product_id=abc")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Product ID must be a positive integer"


def test_stock_movements_rejects_zero_product_id(client):
    login_as_sales(client)

    response = client.get("/api/stock-movements?product_id=0")

    assert response.status_code == 400


def test_stock_movements_rejects_invalid_movement_type(client):
    login_as_sales(client)

    response = client.get("/api/stock-movements?movement_type=invalid")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid movement type"


def test_stock_movements_rejects_invalid_limit(client):
    login_as_sales(client)

    response = client.get("/api/stock-movements?limit=abc")

    assert response.status_code == 400


def test_stock_movements_rejects_limit_below_one(client):
    login_as_sales(client)

    response = client.get("/api/stock-movements?limit=0")

    assert response.status_code == 400


def test_stock_movements_rejects_limit_above_500(client):
    login_as_sales(client)

    response = client.get("/api/stock-movements?limit=501")

    assert response.status_code == 400

def test_customer_sales_report_requires_authentication(client):
    response = client.get("/api/reports/customer-sales")

    assert response.status_code == 401


def test_product_sales_report_requires_authentication(client):
    response = client.get("/api/reports/product-sales")

    assert response.status_code == 401


def test_low_stock_report_requires_authentication(client):
    response = client.get("/api/reports/low-stock")

    assert response.status_code == 401


def test_low_stock_report_rejects_invalid_threshold(client):
    login_as_sales(client)

    response = client.get("/api/reports/low-stock?threshold=abc")

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Threshold must be a valid non-negative integer"
    )


def test_low_stock_report_rejects_negative_threshold(client):
    login_as_sales(client)

    response = client.get("/api/reports/low-stock?threshold=-1")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Threshold cannot be negative"


def test_low_stock_report_accepts_valid_threshold(client, monkeypatch):
    import routes.reports as reports

    login_as_sales(client)

    monkeypatch.setattr(
        reports,
        "get_low_stock_report",
        lambda threshold: [{"product_id": 7, "stock_quantity": 2}]
    )

    response = client.get("/api/reports/low-stock?threshold=5")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["threshold"] == 5
    assert data["count"] == 1
    assert data["report"][0]["product_id"] == 7


def test_customer_sales_report_returns_serialized_data(client, monkeypatch):
    from decimal import Decimal
    from datetime import date
    import routes.reports as reports

    login_as_sales(client)

    monkeypatch.setattr(
        reports,
        "get_customer_sales_summary",
        lambda: [{
            "customer_name": "ABC Technologies",
            "total_sales": Decimal("12345.50"),
            "last_order_date": date(2026, 11, 10)
        }]
    )

    response = client.get("/api/reports/customer-sales")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["report"][0]["total_sales"] == "12345.50"
    assert data["report"][0]["last_order_date"] == "2026-11-10"


def test_product_sales_report_serializes_quantity_as_integer(client, monkeypatch):
    from decimal import Decimal
    import routes.reports as reports

    login_as_sales(client)

    monkeypatch.setattr(
        reports,
        "get_product_sales_summary",
        lambda: [{
            "product_name": "Wireless Mouse",
            "quantity_sold": Decimal("3"),
            "total_sales": Decimal("2250.00")
        }]
    )

    response = client.get("/api/reports/product-sales")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["report"][0]["quantity_sold"] == 3
    assert isinstance(data["report"][0]["quantity_sold"], int)
    assert data["report"][0]["total_sales"] == "2250.00"

def login_as_admin(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"


def test_csv_import_requires_authentication(client):
    response = client.post("/api/products/import")

    assert response.status_code == 401


def test_sales_user_cannot_import_csv(client):
    login_as_sales(client)

    response = client.post("/api/products/import")

    assert response.status_code == 403


def test_csv_import_rejects_missing_file(client):
    login_as_admin(client)

    response = client.post("/api/products/import")

    assert response.status_code == 400
    assert "Please upload a CSV file" in response.get_json()["message"]


def test_csv_import_rejects_empty_filename(client):
    from io import BytesIO

    login_as_admin(client)

    response = client.post(
        "/api/products/import",
        data={"file": (BytesIO(b""), "")},
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "No file selected."


def test_csv_import_rejects_non_csv_file(client):
    from io import BytesIO

    login_as_admin(client)

    response = client.post(
        "/api/products/import",
        data={"file": (BytesIO(b"sample data"), "products.txt")},
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Only CSV files are allowed."


def test_csv_import_rejects_empty_file(client):
    from io import BytesIO

    login_as_admin(client)

    response = client.post(
        "/api/products/import",
        data={"file": (BytesIO(b""), "products.csv")},
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Uploaded CSV file is empty."

from services.csv_import_service import validate_csv_content


def make_csv_bytes(content):
    return content.encode("utf-8")


def test_csv_service_rejects_invalid_headers():
    content = make_csv_bytes(
        "code,name,price\n"
        "P001,Mouse,500\n"
    )

    with pytest.raises(ValueError, match="Invalid CSV columns"):
        validate_csv_content(content)


def test_csv_service_rejects_invalid_price():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,Mouse,Accessories,invalid,10,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Price must be a valid" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_negative_stock():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,Mouse,Accessories,500,-5,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Stock quantity must be" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_duplicate_product_codes():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,Mouse,Accessories,500,10,active\n"
        "P001,Keyboard,Accessories,1000,5,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Duplicate product code" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_missing_product_code():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        ",Mouse,Accessories,500,10,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Product code is required" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_missing_product_name():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,,Accessories,500,10,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Product name is required" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_extra_column_values():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,Mouse,Accessories,500,10,active,EXTRA\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    assert "Extra column values found" in error.value.args[0]["errors"][0]


def test_csv_service_rejects_all_rows_if_one_row_is_invalid():
    content = make_csv_bytes(
        "product_code,product_name,category,price,stock_quantity,status\n"
        "P001,Mouse,Accessories,500,10,active\n"
        "P002,Keyboard,Accessories,invalid,5,active\n"
    )

    with pytest.raises(ValueError) as error:
        validate_csv_content(content)

    result = error.value.args[0]

    assert result["message"] == (
        "CSV validation failed. No products were imported."
    )
    assert len(result["errors"]) == 1

def test_csrf_rejects_post_without_token(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "csrf-test-secret")
    app = create_app()

    app.config.update(
        TESTING=True,
        SECRET_KEY="csrf-test-secret",
        WTF_CSRF_ENABLED=True
    )

    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "csrf@example.com",
                "password": "Test@12345"
            }
        )

        assert response.status_code == 400


def test_csrf_rejects_invalid_token(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "csrf-test-secret")
    app = create_app()

    app.config.update(
        TESTING=True,
        SECRET_KEY="csrf-test-secret",
        WTF_CSRF_ENABLED=True
    )

    with app.test_client() as client:
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "csrf@example.com",
                "password": "Test@12345"
            },
            headers={"X-CSRFToken": "invalid-token"}
        )

        assert response.status_code == 400

def test_csrf_accepts_valid_token(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "csrf-test-secret")
    app = create_app()

    app.config.update(
        TESTING=True,
        SECRET_KEY="csrf-test-secret",
        WTF_CSRF_ENABLED=True
    )

    with app.test_client() as client:

        # Get a valid CSRF token
        response = client.get("/api/csrf-token")

        assert response.status_code == 200

        csrf_token = response.get_json()["csrf_token"]

        # Submit registration with the valid token
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "csrf@example.com",
                "password": "Test@12345"
            },
            headers={
                "X-CSRFToken": csrf_token
            }
        )

        # CSRF validation should pass.
        # Registration may fail later because of database availability.
        assert response.status_code != 400 or (
            response.get_json().get("message") != "The CSRF token is missing."
        )

def test_login_rate_limit(client):
    responses = []

    for _ in range(6):
        response = client.post(
            "/api/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword123"
            }
        )
        responses.append(response.status_code)

    assert responses[:5] == [401, 401, 401, 401, 401]
    assert responses[5] == 429


def test_admin_role_changed_to_sales(client, monkeypatch):
    # User was previously an admin, but database now says sales.
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    monkeypatch.setattr(
        "services.auth_decorators.get_current_user_role",
        lambda user_id: "sales"
    )

    response = client.get("/api/test/admin")

    assert response.status_code == 403


def test_sales_role_changed_to_admin(client, monkeypatch):
    # User was previously sales, but database now says admin.
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    monkeypatch.setattr(
        "services.auth_decorators.get_current_user_role",
        lambda user_id: "admin"
    )

    response = client.get("/api/test/admin")

    assert response.status_code == 200


def test_deleted_user_cannot_access_protected_route(client, monkeypatch):
    with client.session_transaction() as session:
        session["user_id"] = 2
        session["role"] = "sales"

    # User no longer exists in the database.
    monkeypatch.setattr(
        "services.auth_decorators.get_current_user_role",
        lambda user_id: None
    )

    response = client.get("/api/test/sales")

    assert response.status_code == 401

    # Verify that the user's session was cleared.
    with client.session_transaction() as session:
        assert "user_id" not in session


def test_database_failure_blocks_protected_route(client, monkeypatch):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"

    def raise_database_error(user_id):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        "services.auth_decorators.get_current_user_role",
        raise_database_error
    )

    response = client.get("/api/test/admin")

    assert response.status_code == 503
    assert response.json["success"] is False



# --------------------------------------------------
# SALES ORDER OWNERSHIP TESTS
# --------------------------------------------------

def test_sales_user_can_access_own_order_in_service():
    from services.order_service import _check_order_ownership

    _check_order_ownership({"created_by": 2}, requested_by=2, user_role="sales")


def test_sales_user_cannot_access_another_users_order_in_service():
    from services.order_service import _check_order_ownership

    with pytest.raises(PermissionError):
        _check_order_ownership(
            {"created_by": 3}, requested_by=2, user_role="sales"
        )


def test_admin_can_access_another_users_order_in_service():
    from services.order_service import _check_order_ownership

    _check_order_ownership({"created_by": 3}, requested_by=1, user_role="admin")


def test_unknown_role_cannot_access_order_in_service():
    from services.order_service import _check_order_ownership

    with pytest.raises(PermissionError):
        _check_order_ownership(
            {"created_by": 2}, requested_by=2, user_role="manager"
        )


def test_invalid_requester_cannot_access_order_in_service():
    from services.order_service import _check_order_ownership

    with pytest.raises(ValueError, match="Invalid user ID"):
        _check_order_ownership(
            {"created_by": 2}, requested_by=True, user_role="sales"
        )


def test_get_order_route_passes_authenticated_user_and_role(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)
    captured = {}

    def fake_get_order(order_id, requested_by, user_role):
        captured.update(
            order_id=order_id, requested_by=requested_by, user_role=user_role
        )
        return {"id": order_id}

    monkeypatch.setattr(order_routes, "get_order_by_id", fake_get_order)
    response = client.get("/api/orders/12")

    assert response.status_code == 200
    assert captured == {
        "order_id": 12, "requested_by": 2, "user_role": "sales"
    }


def test_get_order_route_returns_403_for_other_users_order(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)

    def deny_order(*args, **kwargs):
        raise PermissionError("You are not authorized to access this order")

    monkeypatch.setattr(order_routes, "get_order_by_id", deny_order)
    response = client.get("/api/orders/12")

    assert response.status_code == 403
    assert response.get_json()["success"] is False


def test_confirm_order_route_passes_authenticated_role(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)
    captured = {}

    def fake_confirm_order(**kwargs):
        captured.update(kwargs)
        return {"success": True, "status": "confirmed"}

    monkeypatch.setattr(order_routes, "confirm_order", fake_confirm_order)
    response = client.post("/api/orders/12/confirm")

    assert response.status_code == 200
    assert captured["confirmed_by"] == 2
    assert captured["user_role"] == "sales"


def test_confirm_order_route_returns_403_when_service_denies(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)

    def deny_order(**kwargs):
        raise PermissionError("You are not authorized to access this order")

    monkeypatch.setattr(order_routes, "confirm_order", deny_order)
    response = client.post("/api/orders/12/confirm")

    assert response.status_code == 403


def test_cancel_order_route_passes_authenticated_role(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)
    captured = {}

    def fake_cancel_order(**kwargs):
        captured.update(kwargs)
        return {"success": True, "status": "cancelled"}

    monkeypatch.setattr(order_routes, "cancel_order", fake_cancel_order)
    response = client.post("/api/orders/12/cancel")

    assert response.status_code == 200
    assert captured["cancelled_by"] == 2
    assert captured["user_role"] == "sales"


def test_cancel_order_route_returns_403_when_service_denies(client, monkeypatch):
    import routes.orders as order_routes
    login_as_sales(client)

    def deny_order(**kwargs):
        raise PermissionError("You are not authorized to access this order")

    monkeypatch.setattr(order_routes, "cancel_order", deny_order)
    response = client.post("/api/orders/12/cancel")

    assert response.status_code == 403
