import sqlite3
import pandas as pd
from config import DB_PATH
import streamlit as st
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            # Ensure the directory exists
            db_dir = os.path.dirname(DB_PATH)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            self.connection = sqlite3.connect(DB_PATH)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self.create_tables()
            return True
        except sqlite3.Error as e:
            st.error(f"Error connecting to SQLite: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.connection.cursor()
            
            # Users table for authentication
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            """)
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    supplier_id INTEGER,
                    quantity INTEGER DEFAULT 0,
                    unit_price REAL DEFAULT 0.00,
                    reorder_level INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                )
            """)
            
            # Purchase Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    supplier_id INTEGER,
                    order_date DATE NOT NULL,
                    total_amount REAL DEFAULT 0.00,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'cancelled')),
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            
            # Purchase Order Items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS purchase_order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Sales Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    customer_id INTEGER,
                    order_date DATE NOT NULL,
                    total_amount REAL DEFAULT 0.00,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'cancelled')),
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """)
            
            # Sales Order Items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales_order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sales_order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            self.connection.commit()
            cursor.close()
            
            # Insert default admin user if not exists
            self.insert_default_admin()
            
            # Check if database is empty and suggest populating it
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM products")
            product_count = cursor.fetchone()[0]
            cursor.close()
            
            if product_count == 0:
                # Database is empty - will be handled by auto-population or user action
                pass
            
        except sqlite3.Error as e:
            st.error(f"Error creating tables: {e}")
    
    def add_user_tracking_columns(self):
        """SQLite doesn't need dynamic column addition as tables are created with all columns initially"""
        pass
    
    def insert_default_admin(self):
        """Insert default admin and demo users"""
        try:
            import bcrypt
            cursor = self.connection.cursor()
            
            # Demo users to create
            demo_users = [
                ("admin", "admin123", "admin"),
                ("manager", "manager123", "admin"),
                ("staff1", "staff123", "staff"),
                ("staff2", "staff123", "staff"),
                ("demo", "demo123", "staff")
            ]
            
            for username, password, role in demo_users:
                try:
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if not cursor.fetchone():
                        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, role) 
                            VALUES (?, ?, ?)
                        """, (username, password_hash.decode('utf-8'), role))
                except sqlite3.Error as e:
                    # Continue even if one user fails
                    pass
            
            self.connection.commit()
            cursor.close()
        except sqlite3.Error as e:
            st.error(f"Error inserting default users: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            # Convert MySQL-style %s placeholders to SQLite-style ? placeholders
            if params is not None:
                converted_query = query.replace("%s", "?")
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params)
            else:
                cursor = self.connection.cursor()
                cursor.execute(query)
            result = cursor.fetchall()
            # Convert to list of dictionaries to match MySQL behavior
            columns = [description[0] for description in cursor.description]
            result_dicts = []
            for row in result:
                result_dicts.append(dict(zip(columns, row)))
            cursor.close()
            return result_dicts
        except sqlite3.Error as e:
            st.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query, params=None):
        """Execute an update/insert/delete query"""
        try:
            # Convert MySQL-style %s placeholders to SQLite-style ? placeholders
            if params is not None:
                converted_query = query.replace("%s", "?")
                cursor = self.connection.cursor()
                cursor.execute(converted_query, params)
            else:
                cursor = self.connection.cursor()
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            st.error(f"Error executing update: {e}")
            return False
    
    def get_dataframe(self, query, params=None):
        """Get query results as pandas DataFrame"""
        try:
            # Convert MySQL-style %s placeholders to SQLite-style ? placeholders
            if params is not None:
                converted_query = query.replace("%s", "?")
                return pd.read_sql_query(converted_query, self.connection, params=params)
            else:
                return pd.read_sql_query(query, self.connection, params=params)
        except sqlite3.Error as e:
            st.error(f"Error getting DataFrame: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()