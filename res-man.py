import psycopg2
from tabulate import tabulate

# ==================== Database Connection ====================
try:
    conn = psycopg2.connect(
        host="localhost",
        database="restaurant",
        user="postgres",
        password="postgres"
    )
    cursor = conn.cursor()
    print("Connected to PostgreSQL database!")
except Exception as e:
    print("Error connecting to database:", e)
    exit()

# ==================== User Authentication ====================
def login():
    username = input("Username: ")
    password = input("Password: ")
    cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    if result:
        print(f"Login successful! Role: {result[0]}")
        return result[0]
    else:
        print("Invalid credentials!")
        return None
 
# ==================== Menu Management ====================
def view_menu():
    cursor.execute("SELECT item_id, name, price, stock FROM menu ORDER BY item_id")
    data = cursor.fetchall()
    print("\n--- Menu ---")
    print(tabulate(data, headers=["ID", "Name", "Price", "Stock"], tablefmt="pretty"))

def add_menu_item():
    name = input("Item name: ")
    price = float(input("Price: "))
    stock = int(input("Stock quantity: "))
    cursor.execute("INSERT INTO menu (name, price, stock) VALUES (%s, %s, %s)", (name, price, stock))
    conn.commit()
    print("Menu item added!")

def update_menu_item():
    item_id = int(input("Enter item ID to update: "))
    name = input("New name: ")
    price = float(input("New price: "))
    stock = int(input("New stock: "))
    cursor.execute("UPDATE menu SET name=%s, price=%s, stock=%s WHERE item_id=%s", (name, price, stock, item_id))
    conn.commit()
    print("Menu item updated!")

def delete_menu_item():
    item_id = int(input("Enter item ID to delete: "))
    cursor.execute("DELETE FROM menu WHERE item_id=%s", (item_id,))
    conn.commit()
    print("Menu item deleted!")

# ==================== Order Management ====================
def place_order(): 
    customer_name = input("Customer Name: ")
    items = []
    while True:
        view_menu()
        item_id = int(input("Enter item ID to order (0 to finish): "))
        if item_id == 0:
            break
        qty = int(input("Quantity: "))
        cursor.execute("SELECT price, stock FROM menu WHERE item_id=%s", (item_id,))
        result = cursor.fetchone()
        if not result:
            print("Invalid item ID.")
            continue
        price, stock = result
        if qty > stock:
            print(f"Not enough stock for {item_id}, available: {stock}")
            continue
        items.append((item_id, qty, price))
    
    if not items:
        print("No items ordered.")
        return
    
    total = sum(qty * price for _, qty, price in items)
    
    # Insert order
    cursor.execute("INSERT INTO orders (customer_name, total_price) VALUES (%s, %s) RETURNING order_id", (customer_name, total))
    order_id = cursor.fetchone()[0]
    
    # Insert order items and update stock
    for item_id, qty, price in items:
        cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)",
                       (order_id, item_id, qty, price))
        cursor.execute("UPDATE menu SET stock = stock - %s WHERE item_id=%s", (qty, item_id))
    
    conn.commit()
    print(f"Order placed! Total: ₹{total:.2f}")

def view_orders():
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
    print("\n--- Orders ---")
    print(tabulate(data, headers=["Order ID", "Customer", "Total", "Created At", "Items"], tablefmt="pretty"))

# ==================== Inventory Check ====================
def check_inventory():
    cursor.execute("SELECT item_id, name, stock FROM menu ORDER BY item_id")
    data = cursor.fetchall()
    print("\n--- Inventory ---")
    print(tabulate(data, headers=["ID", "Item", "Stock"], tablefmt="pretty"))

# ==================== Reports ====================
def total_sales_report():
    cursor.execute("SELECT SUM(total_price) FROM orders")
    total = cursor.fetchone()[0] or 0
    print(f"\nTotal Sales: ₹{total:.2f}")
 
def popular_items_report():
    cursor.execute("""
        SELECT m.name, SUM(oi.quantity) as total_sold
        FROM order_items oi
        JOIN menu m ON oi.item_id = m.item_id
        GROUP BY m.name
        ORDER BY total_sold DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    print("\n--- Most Popular Items ---")
    print(tabulate(data, headers=["Item", "Quantity Sold"], tablefmt="pretty"))

# ==================== Main Program ====================
def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. View Menu\n2. Add Item\n3. Update Item\n4. Delete Item\n5. View Orders\n6. Inventory Check\n7. Total Sales\n8. Popular Items\n9. Place Order\n10. View Orders\n11. Logout")
        choice = input("Choice: ")
        if choice == "1": view_menu()
        elif choice == "2": add_menu_item()
        elif choice == "3": update_menu_item()
        elif choice == "4": delete_menu_item()
        elif choice == "5": view_orders()
        elif choice == "6": check_inventory()
        elif choice == "7": total_sales_report()
        elif choice == "8": popular_items_report()
        elif choice == "9": place_order()
        elif choice == "10": view_orders()
        elif choice == "11": break

        else: print("Invalid choice.")

def chef_menu():
    while True:
        print("\n--- Chef Menu ---")
        print("1. Inventory Check\n2. Logout")
        choice = input("Choice: ")
        if choice == "1": check_inventory()
        elif choice == "2": break
        else: print("Invalid choice.")

def waiter_menu():
    while True:
        print("\n--- Waiter Menu ---")
        print("1. Place Order\n2. View Orders\n3. Logout")
        choice = input("Choice: ")
        if choice == "1": place_order()
        elif choice == "2": view_orders()
        elif choice == "3": break
        else: print("Invalid choice.")

def main():
    print("\n=== Welcome to Restaurant Management System ===")
    role = login()
    if role == "Admin": admin_menu()
    elif role == "Chef": chef_menu()
    elif role == "Waiter": waiter_menu()
    else: print("Exiting program.")

if __name__ == "__main__":
    main()