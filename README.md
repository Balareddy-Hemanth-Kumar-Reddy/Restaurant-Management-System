from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
import os

# ==================== Database Connection ====================
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("Connected to PostgreSQL database!")
except Exception as e:
    print("Error connecting to database:", e)
    exit()

# ==================== FastAPI App ====================
app = FastAPI(title="Restaurant Management API", version="1.0")

# ==================== Pydantic Models ====================
class MenuItem(BaseModel):
    name: str
    price: float
    stock: int

class OrderItem(BaseModel):
    item_id: int
    quantity: int

class Order(BaseModel):
    customer_name: str
    items: List[OrderItem]

# ==================== Menu Endpoints ====================
@app.get("/menu")
def view_menu():
    cursor.execute("SELECT item_id, name, price, stock FROM menu ORDER BY item_id")
    data = cursor.fetchall()
    return {"menu": [{"id": r[0], "name": r[1], "price": r[2], "stock": r[3]} for r in data]}

@app.post("/menu")
def add_menu_item(item: MenuItem):
    cursor.execute("INSERT INTO menu (name, price, stock) VALUES (%s, %s, %s)", (item.name, item.price, item.stock))
    conn.commit()
    return {"message": "Menu item added successfully."}

# ==================== Order Endpoints ====================
@app.post("/orders")
def place_order(order: Order):
    items = []
    total = 0
    for i in order.items:
        cursor.execute("SELECT price, stock FROM menu WHERE item_id=%s", (i.item_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Item ID {i.item_id} not found.")
        price, stock = result
        if i.quantity > stock:
            raise HTTPException(status_code=400, detail=f"Not enough stock for item ID {i.item_id}. Available: {stock}")
        total += i.quantity * price
        items.append((i.item_id, i.quantity, price))
    
    # Insert order
    cursor.execute("INSERT INTO orders (customer_name, total_price) VALUES (%s, %s) RETURNING order_id", (order.customer_name, total))
    order_id = cursor.fetchone()[0]
    
    for item_id, qty, price in items:
        cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, item_id, qty, price))
        cursor.execute("UPDATE menu SET stock = stock - %s WHERE item_id=%s", (qty, item_id))
    
    conn.commit()
    return {"message": f"Order placed successfully! Total: ₹{total:.2f}", "order_id": order_id}

@app.get("/orders")
def get_orders():
    cursor.execute("""
        SELECT o.order_id, o.customer_name, o.total_price, o.created_at, 
               STRING_AGG(m.name || ' x' || oi.quantity,  ', ') as items
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN menu m ON oi.item_id = m.item_id
        GROUP BY o.order_id
        ORDER BY o.order_id
    """)
    data = cursor.fetchall()
    return {"orders": [{"order_id": r[0], "customer_name": r[1], "total_price": r[2], "created_at": r[3], "items": r[4]} for r in data]}
