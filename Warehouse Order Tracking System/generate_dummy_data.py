"""
Script to generate dummy data for the Warehouse Order Tracking System
This will insert 100-200 dummy records across various tables
"""

import sqlite3
from config import DB_PATH
import random
from datetime import datetime, timedelta
import bcrypt

# Sample data for generation
COMPANY_NAMES = [
    "Global Supplies Co.", "Prime Distribution", "Elite Trading", "Premium Goods Inc.",
    "Master Logistics", "Swift Delivery", "Apex Merchants", "Noble Traders",
    "Royal Suppliers", "Crown Distributors", "Sterling Commerce", "Diamond Trading",
    "Platinum Partners", "Golden Enterprises", "Silver Solutions", "Bronze Brothers",
    "Titan Industries", "Vanguard Ventures", "Phoenix Trading", "Eagle Exporters"
]

FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "James", "Jessica",
    "Robert", "Amanda", "William", "Melissa", "Richard", "Michelle", "Joseph", "Lisa",
    "Thomas", "Jennifer", "Christopher", "Amy", "Daniel", "Angela", "Matthew", "Nicole",
    "Anthony", "Stephanie", "Mark", "Rebecca", "Donald", "Laura", "Steven", "Kimberly"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris", "Sanchez"
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "company.com",
    "business.com", "enterprise.com", "corp.com", "trading.com", "supplies.com"
]

PRODUCT_NAMES = [
    "Wireless Mouse", "USB Cable", "Keyboard Stand", "Monitor Stand", "Laptop Bag",
    "Webcam HD", "USB Hub", "HDMI Cable", "Power Adapter", "Phone Case",
    "Screen Protector", "Charging Dock", "Bluetooth Speaker", "Wireless Charger",
    "Tablet Stand", "Cable Organizer", "Portable Hard Drive", "Memory Card",
    "USB Flash Drive", "Headphone Stand", "Desk Mat", "Cable Clips",
    "Laptop Sleeve", "Phone Mount", "Keyboard Wrist Rest", "Mouse Pad",
    "Monitor Light Bar", "USB-C Adapter", "Ethernet Cable", "Surge Protector",
    "Standing Desk Converter", "Ergonomic Mouse", "Mechanical Keyboard", "Gaming Chair",
    "Desk Lamp", "Blue Light Glasses", "Noise Cancelling Headphones", "Smart Watch",
    "Fitness Tracker", "Action Camera", "Drone", "Tablet", "E-Reader",
    "Smart Home Hub", "Security Camera", "Doorbell Camera", "Smart Bulb", "Smart Plug"
]

CATEGORIES = [
    ("Electronics", "Electronic devices and components"),
    ("Computer Accessories", "Computer peripherals and accessories"),
    ("Mobile Accessories", "Smartphone and tablet accessories"),
    ("Office Supplies", "Office equipment and supplies"),
    ("Home & Garden", "Home improvement and garden supplies"),
    ("Health & Fitness", "Health and fitness equipment"),
    ("Smart Home", "Smart home automation devices"),
    ("Audio & Video", "Audio and video equipment"),
    ("Photography", "Cameras and photography equipment"),
    ("Gaming", "Gaming equipment and accessories")
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "San Francisco", "Indianapolis", "Columbus", "Fort Worth", "Charlotte", "Seattle",
    "Denver", "Washington", "Boston", "El Paso", "Detroit", "Nashville"
]

STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "WA", "CO", "MA"]

def get_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def get_random_email(name):
    username = name.lower().replace(' ', '.')
    return f"{username}@{random.choice(EMAIL_DOMAINS)}"

def get_random_phone():
    return f"{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

def get_random_address():
    street_num = random.randint(100, 9999)
    street_name = random.choice([
        "Main St", "Oak Ave", "Park Blvd", "Maple Dr", "Elm St", "Cedar Ln",
        "Pine Rd", "First St", "Second Ave", "Third Blvd", "Commerce Way", "Business Park"
    ])
    city = random.choice(CITIES)
    state = random.choice(STATES)
    zip_code = random.randint(10000, 99999)
    return f"{street_num} {street_name}, {city}, {state} {zip_code}"

def connect_to_database():
    """Establish database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def generate_suppliers(connection, count=30):
    """Generate dummy suppliers"""
    cursor = connection.cursor()
    suppliers = []
    used_names = set()  # Track used names to avoid duplicates
    
    company_suffixes = ['Inc.', 'Ltd.', 'LLC', 'Corp.', 'Co.', 'LLP', 'Group', 'Enterprises']
    company_types = ['Trading', 'Supplies', 'Distribution', 'Logistics', 'Services', 'Solutions']
    
    i = 0
    while len(suppliers) < count and i < count * 2:  # Safety limit
        # Create unique supplier name
        base_name = random.choice(COMPANY_NAMES)
        suffix = random.choice(company_suffixes)
        company_type = random.choice(company_types)
        
        # Try different name combinations
        name_variants = [
            f"{base_name} {suffix}",
            f"{base_name} {company_type} {suffix}",
            f"{base_name} {company_type}",
            f"{base_name} {suffix} {random.randint(1, 100)}"
        ]
        
        name = None
        for variant in name_variants:
            if variant not in used_names:
                name = variant
                used_names.add(name)
                break
        
        if not name:
            # If all variants used, add random number
            name = f"{base_name} {random.randint(1000, 9999)} {suffix}"
            used_names.add(name)
        
        contact_person = get_random_name()
        email = get_random_email(contact_person)
        phone = get_random_phone()
        address = get_random_address()
        
        try:
            # Check if supplier with this name already exists
            cursor.execute("SELECT id FROM suppliers WHERE name = ?", (name,))
            if cursor.fetchone():
                i += 1
                continue
            
            cursor.execute("""
                INSERT INTO suppliers (name, contact_person, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (name, contact_person, email, phone, address))
            suppliers.append(cursor.lastrowid)
        except sqlite3.Error as e:
            print(f"Error inserting supplier {name}: {e}")
            i += 1
            continue
        i += 1
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated {len(suppliers)} unique suppliers")
    return suppliers

def generate_customers(connection, count=40):
    """Generate dummy customers"""
    cursor = connection.cursor()
    customers = []
    
    for i in range(count):
        name = random.choice(COMPANY_NAMES) + f" {random.choice(['Store', 'Shop', 'Outlet', 'Retail', 'Market'])}"
        contact_person = get_random_name()
        email = get_random_email(contact_person)
        phone = get_random_phone()
        address = get_random_address()
        
        try:
            cursor.execute("""
                INSERT INTO customers (name, contact_person, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (name, contact_person, email, phone, address))
            customers.append(cursor.lastrowid)
        except sqlite3.Error as e:
            print(f"Error inserting customer {name}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated {len(customers)} customers")
    return customers

def generate_categories(connection):
    """Generate categories if they don't exist"""
    cursor = connection.cursor()
    
    for category_name, description in CATEGORIES:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description)
                VALUES (?, ?)
            """, (category_name, description))
        except sqlite3.Error as e:
            print(f"Error inserting category {category_name}: {e}")
    
    connection.commit()
    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()
    categories = {name: id for id, name in rows}
    cursor.close()
    print(f"✓ Generated {len(categories)} categories")
    return categories

def generate_products(connection, categories, suppliers, count=60):
    """Generate dummy products"""
    cursor = connection.cursor()
    products = []
    
    category_ids = list(categories.values())
    
    for i in range(count):
        name = random.choice(PRODUCT_NAMES) + f" {random.choice(['Pro', 'Premium', 'Deluxe', 'Standard', 'Basic', 'Plus'])}"
        category_id = random.choice(category_ids)
        supplier_id = random.choice(suppliers)
        quantity = random.randint(0, 500)
        unit_price = round(random.uniform(5.99, 999.99), 2)
        reorder_level = random.randint(10, 50)
        
        try:
            cursor.execute("""
                INSERT INTO products (name, category_id, supplier_id, quantity, unit_price, reorder_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, category_id, supplier_id, quantity, unit_price, reorder_level))
            products.append(cursor.lastrowid)
        except sqlite3.Error as e:
            print(f"Error inserting product {name}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated {len(products)} products")
    return products

def generate_purchase_orders(connection, suppliers, products, count=120):
    """Generate dummy purchase orders"""
    cursor = connection.cursor()
    purchase_orders = []
    used_order_numbers = set()
    
    statuses = ['pending', 'completed', 'cancelled']
    # Ensure we have orders spread across different dates for trends
    base_date = datetime.now()
    
    for i in range(count):
        # Ensure unique order numbers
        while True:
            order_number = f"PO-{base_date.year}-{str(random.randint(10000, 99999))}"
            if order_number not in used_order_numbers:
                used_order_numbers.add(order_number)
                break
        supplier_id = random.choice(suppliers)
        # Spread orders across last 365 days for better trends
        order_date = base_date - timedelta(days=random.randint(0, 365))
        status = random.choice(statuses)
        
        # Generate order items
        num_items = random.randint(1, 5)
        total_amount = 0
        
        try:
            # Get a random user for created_by (for demo data)
            cursor.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1")
            user_result = cursor.fetchone()
            created_by = user_result[0] if user_result else None
            
            cursor.execute("""
                INSERT INTO purchase_orders (order_number, supplier_id, order_date, status, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (order_number, supplier_id, order_date.date(), status, created_by))
            po_id = cursor.lastrowid
            
            # Generate items for this order
            selected_products = random.sample(products, min(num_items, len(products)))
            for product_id in selected_products:
                cursor.execute("SELECT unit_price FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if result:
                    unit_price = float(result[0])
                    quantity = random.randint(10, 100)
                    total_price = round(unit_price * quantity, 2)
                    total_amount += total_price
                    
                    cursor.execute("""
                        INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (po_id, product_id, quantity, unit_price, total_price))
            
            # Update total amount
            cursor.execute("""
                UPDATE purchase_orders SET total_amount = ? WHERE id = ?
            """, (round(total_amount, 2), po_id))
            
            purchase_orders.append(po_id)
        except sqlite3.Error as e:
            print(f"Error inserting purchase order {order_number}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated {len(purchase_orders)} purchase orders")
    return purchase_orders

def generate_sales_orders(connection, customers, products, count=150):
    """Generate dummy sales orders"""
    cursor = connection.cursor()
    sales_orders = []
    used_order_numbers = set()
    
    statuses = ['pending', 'completed', 'cancelled']
    # Ensure we have orders spread across different dates for trends
    base_date = datetime.now()
    
    for i in range(count):
        # Ensure unique order numbers
        while True:
            order_number = f"SO-{base_date.year}-{str(random.randint(10000, 99999))}"
            if order_number not in used_order_numbers:
                used_order_numbers.add(order_number)
                break
        customer_id = random.choice(customers)
        # Spread orders across last 365 days for better trends
        order_date = base_date - timedelta(days=random.randint(0, 365))
        # Make most orders completed for better sales trends
        status = 'completed' if random.random() > 0.2 else random.choice(['pending', 'cancelled'])
        
        # Generate order items
        num_items = random.randint(1, 5)
        total_amount = 0
        
        try:
            # Get a random user for created_by (for demo data)
            cursor.execute("SELECT id FROM users ORDER BY RANDOM() LIMIT 1")
            user_result = cursor.fetchone()
            created_by = user_result[0] if user_result else None
            
            cursor.execute("""
                INSERT INTO sales_orders (order_number, customer_id, order_date, status, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (order_number, customer_id, order_date.date(), status, created_by))
            so_id = cursor.lastrowid
            
            # Generate items for this order
            selected_products = random.sample(products, min(num_items, len(products)))
            for product_id in selected_products:
                cursor.execute("SELECT unit_price FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if result:
                    # Sales price might be higher than purchase price
                    base_price = float(result[0])
                    unit_price = round(base_price * random.uniform(1.1, 1.5), 2)
                    quantity = random.randint(1, 50)
                    total_price = round(unit_price * quantity, 2)
                    total_amount += total_price
                    
                    cursor.execute("""
                        INSERT INTO sales_order_items (sales_order_id, product_id, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (so_id, product_id, quantity, unit_price, total_price))
            
            # Update total amount
            cursor.execute("""
                UPDATE sales_orders SET total_amount = ? WHERE id = ?
            """, (round(total_amount, 2), so_id))
            
            sales_orders.append(so_id)
        except sqlite3.Error as e:
            print(f"Error inserting sales order {order_number}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated {len(sales_orders)} sales orders")
    return sales_orders

def generate_demo_users(connection):
    """Generate demo user accounts"""
    cursor = connection.cursor()
    
    demo_users = [
        ("admin", "admin123", "admin"),
        ("manager", "manager123", "admin"),
        ("staff1", "staff123", "staff"),
        ("staff2", "staff123", "staff"),
        ("demo", "demo123", "staff")
    ]
    
    for username, password, role in demo_users:
        try:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                continue
            
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash.decode('utf-8'), role))
        except sqlite3.Error as e:
            print(f"Error inserting user {username}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"✓ Generated demo user accounts")

def main():
    """Main function to generate all dummy data"""
    print("=" * 60)
    print("Generating Dummy Data for Warehouse Order Tracking System")
    print("=" * 60)
    
    connection = connect_to_database()
    if not connection:
        print("Failed to connect to database. Please check your configuration.")
        return
    
    try:
        # Generate in order (respecting foreign key constraints)
        print("\n1. Generating demo users...")
        generate_demo_users(connection)
        
        print("\n2. Generating categories...")
        categories = generate_categories(connection)
        
        print("\n3. Generating suppliers...")
        suppliers = generate_suppliers(connection, count=50)
        
        print("\n4. Generating customers...")
        customers = generate_customers(connection, count=60)
        
        print("\n5. Generating products...")
        products = generate_products(connection, categories, suppliers, count=100)
        
        print("\n6. Generating purchase orders...")
        purchase_orders = generate_purchase_orders(connection, suppliers, products, count=120)
        
        print("\n7. Generating sales orders...")
        sales_orders = generate_sales_orders(connection, customers, products, count=150)
        
        print("\n" + "=" * 60)
        print("✓ Dummy data generation completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Users: 5")
        print(f"  - Categories: {len(categories)}")
        print(f"  - Suppliers: {len(suppliers)}")
        print(f"  - Customers: {len(customers)}")
        print(f"  - Products: {len(products)}")
        print(f"  - Purchase Orders: {len(purchase_orders)}")
        print(f"  - Sales Orders: {len(sales_orders)}")
        total_records = len(suppliers) + len(customers) + len(products) + len(purchase_orders) + len(sales_orders) + 5 + len(categories)
        print(f"\n✅ Total records generated: {total_records}")
        print(f"\n📊 Orders are spread across the last 365 days for trend analysis.")
        print(f"\n🎉 Database is now populated with realistic sample data!")
        
    except Exception as e:
        print(f"\nError generating data: {e}")
    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()