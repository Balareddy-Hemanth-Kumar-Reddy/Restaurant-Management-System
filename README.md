
Swagger
https://restaurant-management-system-3-9sr5.onrender.com/docs

<img width="1024" height="1536" alt="Restaurant management system diagrams (1)" src="https://github.com/user-attachments/assets/d190d0fb-f1b9-4434-8112-d036115f97bb" />


# Restaurant Management API (FastAPI + PostgreSQL)

This FastAPI project implements a **restaurant menu and order management system**.

---

## Key Features

### 1️⃣ Menu Management
- **GET /menu** → Fetch all menu items.
- **POST /menu** → Add new menu items in bulk.

### 2️⃣ Order Management
- **POST /orders** → Place an order for multiple items.
  - Checks stock availability.
  - Calculates total (**quantity × price**).
  - Updates stock in the menu table.
- **GET /orders** → Retrieve all orders.
  - Aggregates ordered items per order.
  - Returns order details including total price and timestamp.

### 3️⃣ Database Design
- **menu** → Stores item details (`name`, `price`, `stock`).
- **orders** → Stores order details (`customer`, `total_price`, `timestamp`).
- **order_items** → Links orders and menu items (many-to-many), stores `quantity` and `price`.

### 4️⃣ Implementation Highlights
- Uses **Pydantic models** for request validation (`MenuItem`, `OrderItem`, `Order`).
- Uses **psycopg2** to connect and interact with PostgreSQL.
- Endpoints handle exceptions for:
  - Item not found
  - Insufficient stock
- Order total and stock update is handled **atomically per order**.

---

## Tech Stack
- **Backend:** FastAPI  
- **Database:** PostgreSQL  
- **Python packages:** `psycopg2`, `pydantic`, `uvicorn`

