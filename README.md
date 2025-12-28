
Swagger
https://restaurant-management-system-yena.onrender.com/docs

DataBase
postgresql://postgres:HKXXHLQBaOBztZBapCeKQSKdtGJeMRJr@shinkansen.proxy.rlwy.net:43107/railway





1)ERD (Entity Relationship Diagram):
+------------+         +------------+        +----------------+
|   menu     |         |  orders    |        |  order_items   |
+------------+         +------------+        +----------------+
| item_id PK |<----+   | order_id PK|<----+  | order_item_id PK|
| name       |     |   | customer_name      | order_id FK     |
| price      |     +---| total_price        | item_id FK      |
| stock      |         | created_at         | quantity        |
+------------+         +-------------------+ | price           |
                                           +----------------+

2)Flowchart of the code:
Start
  |
  v
Connect to PostgreSQL
  |
  v
+-----------------------+
| FastAPI Server Start  |
+-----------------------+
  |
  +--> GET /menu --> Query menu table --> Return all menu items
  |
  +--> POST /menu --> Receive list of menu items
  |       |--> Insert each item into menu table
  |       --> Return success message
  |
  +--> POST /orders --> Receive order data
  |       |--> For each item in order
  |       |       --> Check stock and get price
  |       |       --> Calculate total price
  |       |--> Insert order into orders table
  |       |--> Insert items into order_items table
  |       |--> Update menu stock
  |       --> Return order confirmation
  |
  +--> GET /orders --> Join orders, order_items, menu
          --> Aggregate items per order

3)Database Schema Diagram:
menu
+---------+-----------+
| Column  | Type      |
+---------+-----------+
| item_id | SERIAL PK |
| name    | VARCHAR   |
| price   | NUMERIC   |
| stock   | INT       |
+---------+-----------+

orders
+-------------+-----------+
| Column      | Type      |
+-------------+-----------+
| order_id    | SERIAL PK |
| customer_name | VARCHAR |
| total_price | NUMERIC   |
| created_at  | TIMESTAMP |
+-------------+-----------+

order_items
+----------------+-----------+
| Column         | Type      |
+----------------+-----------+
| order_item_id  | SERIAL PK |
| order_id       | INT FK    |
| item_id        | INT FK    |
| quantity       | INT       |
| price          | NUMERIC   |
+----------------+-----------+

4)Code Explanation:
Restaurant Management API (FastAPI + PostgreSQL)
This FastAPI project implements a restaurant menu and order management system.

Key Features:
1)Menu Management
 GET /menu → Fetch all menu items.
 POST /menu → Add new menu items in bulk.
2)Order Management
 POST /orders → Place an order for multiple items.
   Checks stock availability.
   Calculates total (quantity × price).
   Updates stock in menu table.
 GET /orders → Retrieve all orders.
  Aggregates ordered items per order.
  Returns order details including total price and timestamp.
3)Database Design
 menu → Stores item details (name, price, stock).
 orders → Stores order details (customer, total price, timestamp).
 order_items → Links orders and menu items (many-to-many), stores quantity and item price.
4)Implementation Highlights
 Uses Pydantic models for request validation (MenuItem, OrderItem, Order).
 Uses psycopg2 to connect and interact with PostgreSQL.
 Endpoints handle exceptions for:
   Item not found
   Insufficient stock
 Order total and stock update is handled atomically per order.

Tech Stack:
 Backend: FastAPI
 Database: PostgreSQL
 Python packages: psycopg2, pydantic, uvicorn



<img width="1024" height="1536" alt="Entity-relationship and flowchart diagrams" src="https://github.com/user-attachments/assets/9064ed03-98fd-4a04-a55c-fedbf03eeff7" />

