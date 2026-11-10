# Frontend guide

The Flask app serves `templates/index.html` at `/`. CSS is in `static/css/style.css`; browser logic is in `static/js/app.js`. The frontend uses the Fetch API and same-origin session cookies. It fetches a CSRF token from `/api/csrf-token` and sends it as `X-CSRFToken` for state-changing requests.

## Available screens

- Sign in and Sales-user registration.
- Dashboard counts.
- Customer and product listing; Admin can add records.
- Admin stock adjustment (increase/decrease) with a required reason.
- Admin CSV product import.
- Draft order creation with multiple product lines and 0–20% discount.
- Order lookup, confirmation and cancellation (backend checks ownership/role and stock).
- Customer sales, product sales and low-stock reports.
- Stock movement history.

The browser displays convenience validation only. The Flask services remain authoritative for permissions, prices, totals, stock availability and order state.
