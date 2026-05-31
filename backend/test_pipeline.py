from app.inference.sql_generator import SQLGenerator
from database.query_executor import QueryExecutor


# =====================================
# DATABASE SCHEMA
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
    total_amount REAL
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
    subtotal REAL
);
"""


# =====================================
# USER QUESTION
# =====================================

question = """
Show the top 5 customers by total purchase amount
"""


# =====================================
# LOAD COMPONENTS
# =====================================

generator = SQLGenerator()

executor = QueryExecutor()


# =====================================
# GENERATE SQL
# =====================================

sql_query = generator.generate_sql(
    schema=schema,
    question=question
)

print("\n" + "=" * 60)
print("GENERATED SQL")
print("=" * 60)
print(sql_query)


# =====================================
# EXECUTE SQL
# =====================================

response = executor.execute_query(sql_query)

print("\n" + "=" * 60)
print("QUERY RESULTS")
print("=" * 60)

if response["success"]:

    for row in response["results"]:
        print(row)

else:

    print("ERROR:")
    print(response["error"])


executor.close()