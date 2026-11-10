// ==========================================
// Global Variables
// ==========================================

let csrf = '';
let me = null;
let products = [];
let customers = [];


// ==========================================
// Utility Functions
// ==========================================

const $ = s => document.querySelector(s);

const esc = s =>
    String(s ?? '').replace(/[&<>"']/g, c => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[c]));


// ==========================================
// CSRF Token
// ==========================================

async function token() {
    const r = await fetch('/api/csrf-token');
    csrf = (await r.json()).csrf_token;
}


// ==========================================
// API Helper Function
// ==========================================

async function api(url, opts = {}) {
    opts.credentials = 'same-origin';
    opts.headers = { ...(opts.headers || {}) };

    if (opts.body instanceof FormData) {
        // FormData request
    } else if (opts.body) {
        opts.headers['Content-Type'] = 'application/json';
    }

    if (!['GET', 'HEAD'].includes(opts.method || 'GET')) {
        opts.headers['X-CSRFToken'] = csrf;
    }

    const r = await fetch(url, opts);

    let d = {};

    try {
        d = await r.json();
    } catch { }

    if (!r.ok) {
        const details = Array.isArray(d.errors)
            ? '\n' + d.errors.join('\n')
            : '';

        throw Error(
            (d.message || `Request failed (${r.status})`) + details
        );
    }

    return d;
}


// ==========================================
// Notification Function
// ==========================================

function notice(msg, error = false) {
    $('#notice').textContent = msg;
    $('#notice').className = error ? 'error' : '';
}


// ==========================================
// Table Generator
// ==========================================

function table(rows, cols) {
    if (!rows?.length) {
        return '<p class="card muted">No records found.</p>';
    }

    return `
        <table>
            <thead>
                <tr>
                    ${cols.map(c => `<th>${esc(c[1])}</th>`).join('')}
                </tr>
            </thead>

            <tbody>
                ${rows.map(row => `
                    <tr>
                        ${cols.map(c => `<td>${esc(row[c[0]])}</td>`).join('')}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}


// ==========================================
// Authentication / Enter Application
// ==========================================

function enter(user) {
    me = user;

    $('#auth').hidden = true;
    $('#app').hidden = false;
    $('#userbar').hidden = false;

    $('#who').textContent = user.name;
    $('#role').textContent = user.role.toUpperCase();

    document.querySelectorAll('.admin-only').forEach(x => {
        x.hidden = user.role !== 'admin';
    });

    loadAll();
}


// ==========================================
// Load All Application Data
// ==========================================

async function loadAll() {
    try {
        await Promise.all([
            loadProducts(),
            loadCustomers()
        ]);

        $('#stats').innerHTML = `
            <div class="stat">
                <strong>${products.length}</strong>
                <span>Products in catalogue</span>
            </div>

            <div class="stat">
                <strong>${customers.length}</strong>
                <span>Customers</span>
            </div>

            <div class="stat">
                <strong>${me.role === 'admin' ? 'ADMIN' : 'SALES'}</strong>
                <span>Signed-in access</span>
            </div>
        `;

        await loadReports();

    } catch (e) {
        notice(e.message, true);
    }
}


// ==========================================
// Products Management
// ==========================================

async function loadProducts() {
    const d = await api('/api/products');

    products = d.products || [];

    renderProducts();
}


function renderProducts() {
    const q = ($('#productSearch')?.value || '').toLowerCase();

    const list = products.filter(p =>
        `${p.name} ${p.product_code} ${p.category}`
            .toLowerCase()
            .includes(q)
    );

    $('#productList').innerHTML = list.length
        ? `
            <table>
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>

                        ${me.role === 'admin' ? '<th>Stock action</th>' : ''}
                    </tr>
                </thead>

                <tbody>
                    ${list.map(p => `
                        <tr>
                            <td>${esc(p.product_code)}</td>
                            <td>${esc(p.name)}</td>
                            <td>${esc(p.category)}</td>
                            <td>${esc(p.price)}</td>
                            <td>${esc(p.stock_quantity)}</td>
                            <td>${esc(p.status)}</td>

                            ${me.role === 'admin' ? `
                                <td>
                                    <button
                                        class="secondary"
                                        onclick="adjustStock(${p.id})"
                                    >
                                        Adjust
                                    </button>
                                </td>
                            ` : ''}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `
        : '<p class="card muted">No products found.</p>';
}


// ==========================================
// Adjust Product Stock
// ==========================================

window.adjustStock = async id => {
    const type = prompt('Type increase or decrease:', 'increase');

    if (!['increase', 'decrease'].includes(type)) {
        return;
    }

    const qty = Number(prompt('Enter whole-number quantity:', '1'));

    if (!Number.isInteger(qty) || qty <= 0) {
        notice('Enter a positive whole number.', true);
        return;
    }

    const reason = prompt('Reason for this stock adjustment:');

    if (!reason?.trim()) {
        return;
    }

    try {
        await api(`/api/products/${id}/stock-adjustment`, {
            method: 'POST',
            body: JSON.stringify({
                adjustment_type: type,
                quantity: qty,
                reason
            })
        });

        await loadProducts();

        notice('Stock adjusted and movement recorded.');

    } catch (e) {
        notice(e.message, true);
    }
};


// ==========================================
// Customers Management
// ==========================================

async function loadCustomers() {
    const d = await api('/api/customers');

    customers = d.customers || [];

    $('#customerList').innerHTML = table(customers, [
        ['id', 'ID'],
        ['name', 'Customer'],
        ['email', 'Email'],
        ['mobile', 'Mobile'],
        ['city', 'City'],
        ['status', 'Status']
    ]);

    $('#orderCustomer').innerHTML =
        '<option value="">Choose customer</option>' +
        customers
            .filter(c => c.status === 'active')
            .map(c => `
                <option value="${c.id}">
                    ${esc(c.name)}
                </option>
            `)
            .join('');
}


// ==========================================
// Order Line Management
// ==========================================

function addLine() {
    const div = document.createElement('div');

    div.className = 'order-line';

    div.innerHTML = `
        <select class="line-product">
            <option value="">Select product</option>

            ${products
                .filter(p => p.status === 'active')
                .map(p => `
                    <option
                        value="${p.id}"
                        data-price="${p.price}"
                        data-stock="${p.stock_quantity}"
                    >
                        ${esc(p.name)} (stock ${p.stock_quantity})
                    </option>
                `)
                .join('')}
        </select>

        <input
            class="line-qty"
            type="number"
            min="1"
            step="1"
            value="1"
            placeholder="Quantity"
        >

        <input
            class="line-rate"
            type="text"
            readonly
            placeholder="Unit price"
        >

        <button
            type="button"
            class="secondary remove-line"
        >
            ×
        </button>
    `;

    $('#orderLines').append(div);

    div.querySelector('.line-product').onchange = e => {
        div.querySelector('.line-rate').value =
            e.target.selectedOptions[0].dataset.price || '';
    };

    div.querySelector('.remove-line').onclick = () => div.remove();
}


// ==========================================
// Reports Management
// ==========================================

async function loadReports() {
    const paths = [
        ['Customer sales', '/api/reports/customer-sales'],
        ['Product sales', '/api/reports/product-sales'],
        [
            'Low stock',
            '/api/reports/low-stock?threshold=' +
            ($('#threshold')?.value || 5)
        ]
    ];

    const results = await Promise.all(
        paths.map(async ([title, url]) => {
            try {
                const d = await api(url);

                return `
                    <div class="card">
                        <h3>${title}</h3>

                        ${table(
                            d.report || [],
                            Object.keys(d.report?.[0] || {}).map(k => [
                                k,
                                k.replaceAll('_', ' ')
                            ])
                        )}
                    </div>
                `;

            } catch (e) {
                return `
                    <div class="card">
                        <h3>${title}</h3>
                        <p class="muted">${esc(e.message)}</p>
                    </div>
                `;
            }
        })
    );

    $('#reportOutput').innerHTML = results.join('');
}


// ==========================================
// Order Details
// ==========================================

async function showOrder(id) {
    const d = await api('/api/orders/' + id);

    const o = d.order;

    $('#orderResult').innerHTML = `
        <div class="card">

            <h3>
                Order #${id} · ${esc(o.status)}
            </h3>

            <pre>${esc(JSON.stringify(o, null, 2))}</pre>

            ${o.status === 'draft' ? `
                <button id="confirmOrder">
                    Confirm order
                </button>
            ` : ''}

            ${o.status !== 'cancelled' ? `
                <button class="secondary" id="cancelOrder">
                    Cancel order
                </button>
            ` : ''}

        </div>
    `;


    // Confirm Order
    $('#confirmOrder')?.addEventListener('click', async () => {
        if (confirm('Confirm this order and deduct stock?')) {
            try {
                await api(`/api/orders/${id}/confirm`, {
                    method: 'POST',
                    body: '{}'
                });

                notice('Order confirmed.');

                showOrder(id);

            } catch (e) {
                notice(e.message, true);
            }
        }
    });


    // Cancel Order
    $('#cancelOrder')?.addEventListener('click', async () => {
        if (confirm('Cancel this order?')) {
            try {
                await api(`/api/orders/${id}/cancel`, {
                    method: 'POST',
                    body: '{}'
                });

                notice('Order cancelled.');

                showOrder(id);

            } catch (e) {
                notice(e.message, true);
            }
        }
    });
}


// ==========================================
// Login Form
// ==========================================

$('#loginForm').onsubmit = async e => {
    e.preventDefault();

    try {
        const d = await api('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(
                Object.fromEntries(new FormData(e.target))
            )
        });

        enter(d.user);

        notice('Welcome back.');

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Registration Form
// ==========================================

$('#registerForm').onsubmit = async e => {
    e.preventDefault();

    try {
        await api('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(
                Object.fromEntries(new FormData(e.target))
            )
        });

        notice('Account created. Sign in with your new account.');

        $('#registerForm').hidden = true;
        $('#loginForm').hidden = false;

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Login / Registration Navigation
// ==========================================

$('#showRegister').onclick = e => {
    e.preventDefault();

    $('#loginForm').hidden = true;
    $('#registerForm').hidden = false;
};


$('#showLogin').onclick = e => {
    e.preventDefault();

    $('#registerForm').hidden = true;
    $('#loginForm').hidden = false;
};


// ==========================================
// Logout
// ==========================================

$('#logout').onclick = async () => {
    try {
        await api('/api/auth/logout', {
            method: 'POST',
            body: '{}'
        });

    } catch { }

    location.reload();
};


// ==========================================
// Navigation Tabs
// ==========================================

document.querySelectorAll('.tab').forEach(b => {
    b.onclick = () => {

        document.querySelectorAll('.tab').forEach(x => {
            x.classList.toggle('active', x === b);
        });

        document.querySelectorAll('.panel').forEach(x => {
            x.hidden = x.id !== b.dataset.tab;
        });

        if (b.dataset.tab === 'stock') {
            loadStock();
        }
    };
});


// ==========================================
// Add Customer
// ==========================================

$('#customerForm').onsubmit = async e => {
    e.preventDefault();

    try {
        await api('/api/customers', {
            method: 'POST',
            body: JSON.stringify(
                Object.fromEntries(new FormData(e.target))
            )
        });

        e.target.reset();

        await loadCustomers();

        notice('Customer added.');

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Add Product
// ==========================================

$('#productForm').onsubmit = async e => {
    e.preventDefault();

    const f = Object.fromEntries(new FormData(e.target));

    f.price = Number(f.price);
    f.stock_quantity = Number(f.stock_quantity);

    try {
        await api('/api/products', {
            method: 'POST',
            body: JSON.stringify(f)
        });

        e.target.reset();

        await loadProducts();

        notice('Product added.');

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Product Search
// ==========================================

$('#productSearch').oninput = renderProducts;


// ==========================================
// CSV Product Import
// ==========================================

$('#csvForm').onsubmit = async e => {
    e.preventDefault();

    try {
        const d = await api('/api/products/import', {
            method: 'POST',
            body: new FormData(e.target)
        });

        notice(d.message);

        e.target.reset();

        await loadProducts();

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Create Order
// ==========================================

$('#addLine').onclick = addLine;


$('#orderForm').onsubmit = async e => {
    e.preventDefault();

    const lines = [
        ...document.querySelectorAll('.order-line')
    ].map(x => ({
        product_id: Number(
            x.querySelector('.line-product').value
        ),

        quantity: Number(
            x.querySelector('.line-qty').value
        )
    }));

    if (
        !lines.length ||
        lines.some(x =>
            !x.product_id ||
            !Number.isInteger(x.quantity) ||
            x.quantity <= 0
        )
    ) {
        notice('Add at least one product and valid quantity.', true);
        return;
    }

    try {
        const d = await api('/api/orders', {
            method: 'POST',

            body: JSON.stringify({
                customer_id: Number($('#orderCustomer').value),

                discount_percentage: Number(
                    e.target.discount_percentage.value
                ),

                items: lines
            })
        });

        notice(
            'Draft order created. ID: ' +
            (d.order_id || d.id || 'see response')
        );

        $('#orderResult').innerHTML = `
            <pre class="card">
                ${esc(JSON.stringify(d, null, 2))}
            </pre>
        `;

        e.target.reset();

        $('#orderLines').innerHTML = '';

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Order Lookup
// ==========================================

$('#orderLookup').onsubmit = async e => {
    e.preventDefault();

    try {
        await showOrder(e.target.id.value);

    } catch (x) {
        notice(x.message, true);
    }
};


// ==========================================
// Refresh Reports
// ==========================================

$('#loadReports').onclick = loadReports;


// ==========================================
// Stock Movement History
// ==========================================

async function loadStock() {
    try {
        const d = await api('/api/stock-movements');

        $('#stockList').innerHTML = table(d.movements, [
            ['product_name', 'Product'],
            ['movement_type', 'Type'],
            ['quantity_change', 'Change'],
            ['reason', 'Reason'],
            ['created_at', 'Date']
        ]);

    } catch (e) {
        $('#stockList').textContent = e.message;
    }
}


$('#loadStock').onclick = loadStock;


// ==========================================
// Application Initialization
// ==========================================

(async () => {
    try {
        await token();

        const d = await api('/api/auth/me');

        if (d.user) {
            enter(d.user);
        }

    } catch { }
})();
