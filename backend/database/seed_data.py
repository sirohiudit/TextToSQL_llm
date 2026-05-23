import sqlite3
import random
from faker import Faker
from pathlib import Path

fake = Faker()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# =========================
# CONFIG
# =========================

NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_ORDERS = 500
NUM_EMPLOYEES = 20

PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home",
    "Sports",
    "Books",
    "Beauty"
]

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Finance",
    "HR",
    "Operations"
]

# =========================
# INSERT CUSTOMERS
# =========================

customers = []

for _ in range(NUM_CUSTOMERS):
    customers.append((
        fake.first_name(),
        fake.last_name(),
        fake.unique.email(),
        fake.city(),
        fake.country(),
        fake.date_between(start_date="-3y", end_date="today")
    ))

cursor.executemany("""
INSERT INTO customers (
    first_name,
    last_name,
    email,
    city,
    country,
    signup_date
)
VALUES (?, ?, ?, ?, ?, ?)
""", customers)

print(f"Inserted {NUM_CUSTOMERS} customers")

# =========================
# INSERT PRODUCTS
# =========================

products = []

for _ in range(NUM_PRODUCTS):
    category = random.choice(PRODUCT_CATEGORIES)

    products.append((
        fake.word().capitalize() + " " + category[:-1],
        category,
        round(random.uniform(10, 1000), 2),
        random.randint(10, 500)
    ))

cursor.executemany("""
INSERT INTO products (
    product_name,
    category,
    price,
    stock_quantity
)
VALUES (?, ?, ?, ?)
""", products)

print(f"Inserted {NUM_PRODUCTS} products")

# =========================
# INSERT EMPLOYEES
# =========================

employees = []

for _ in range(NUM_EMPLOYEES):
    employees.append((
        fake.first_name(),
        fake.last_name(),
        random.choice(DEPARTMENTS),
        round(random.uniform(40000, 150000), 2),
        fake.date_between(start_date="-10y", end_date="today")
    ))

cursor.executemany("""
INSERT INTO employees (
    first_name,
    last_name,
    department,
    salary,
    hire_date
)
VALUES (?, ?, ?, ?, ?)
""", employees)

print(f"Inserted {NUM_EMPLOYEES} employees")

# =========================
# INSERT ORDERS
# =========================

orders = []

for _ in range(NUM_ORDERS):

    customer_id = random.randint(1, NUM_CUSTOMERS)

    order_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    total_amount = 0

    orders.append((
        customer_id,
        order_date,
        total_amount
    ))

cursor.executemany("""
INSERT INTO orders (
    customer_id,
    order_date,
    total_amount
)
VALUES (?, ?, ?)
""", orders)

print(f"Inserted {NUM_ORDERS} orders")

# =========================
# INSERT ORDER ITEMS
# =========================

order_items = []

for order_id in range(1, NUM_ORDERS + 1):

    num_items = random.randint(1, 5)

    order_total = 0

    for _ in range(num_items):

        product_id = random.randint(1, NUM_PRODUCTS)

        quantity = random.randint(1, 4)

        cursor.execute("""
        SELECT price
        FROM products
        WHERE product_id = ?
        """, (product_id,))

        price = cursor.fetchone()[0]

        subtotal = round(price * quantity, 2)

        order_total += subtotal

        order_items.append((
            order_id,
            product_id,
            quantity,
            subtotal
        ))

    # Update order total
    cursor.execute("""
    UPDATE orders
    SET total_amount = ?
    WHERE order_id = ?
    """, (round(order_total, 2), order_id))

cursor.executemany("""
INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    subtotal
)
VALUES (?, ?, ?, ?)
""", order_items)

print(f"Inserted {len(order_items)} order items")

# =========================
# SAVE
# =========================

conn.commit()
conn.close()

print("\nDatabase seeding completed successfully!")