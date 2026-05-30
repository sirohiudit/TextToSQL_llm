from app.inference.sql_generator import SQLGenerator


# =====================================
# SAMPLE DATABASE SCHEMA
# =====================================

schema = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    city TEXT,
    country TEXT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    total_amount REAL,

    FOREIGN KEY(customer_id)
    REFERENCES customers(customer_id)
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    subtotal REAL,

    FOREIGN KEY(order_id)
    REFERENCES orders(order_id),

    FOREIGN KEY(product_id)
    REFERENCES products(product_id)
);
"""


# =====================================
# USER QUESTION
# =====================================

question = """
Show the top 5 customers by total purchase amount
"""


# =====================================
# LOAD MODEL
# =====================================

generator = SQLGenerator()


# =====================================
# GENERATE SQL
# =====================================

sql = generator.generate_sql(
    schema=schema,
    question=question
)


# =====================================
# PRINT RESULT
# =====================================

print("\n" + "=" * 50)
print("GENERATED SQL")
print("=" * 50)
print(sql)
print("=" * 50)