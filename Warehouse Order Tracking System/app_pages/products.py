import streamlit as st
import pandas as pd
from database import DatabaseManager
from datetime import datetime

def show_products():
    st.title("📦 Product Management")
    st.markdown("---")
    
    db = DatabaseManager()
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        action = st.selectbox(
            "Choose Action",
            ["View Products", "Add Product", "Update Product", "Delete Product"]
        )
    
    if action == "View Products":
        view_products(db)
    elif action == "Add Product":
        add_product(db)
    elif action == "Update Product":
        update_product(db)
    elif action == "Delete Product":
        delete_product(db)

def view_products(db):
    st.subheader("📋 All Products")
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("Search products", placeholder="Product name...")
    
    with col2:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + [cat['name'] for cat in db.execute_query("SELECT name FROM categories")]
        )
    
    with col3:
        stock_filter = st.selectbox(
            "Filter by Stock",
            ["All", "In Stock", "Low Stock", "Out of Stock"]
        )
    
    # Build query based on filters
    query = """
        SELECT 
            p.id, p.name, p.quantity, p.unit_price, p.reorder_level,
            c.name as category, s.name as supplier
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE 1=1
    """
    params = []
    
    if search:
        query += " AND p.name LIKE %s"
        params.append(f"%{search}%")
    
    if category_filter != "All":
        query += " AND c.name = %s"
        params.append(category_filter)
    
    if stock_filter == "Low Stock":
        query += " AND p.quantity <= p.reorder_level"
    elif stock_filter == "Out of Stock":
        query += " AND p.quantity = 0"
    elif stock_filter == "In Stock":
        query += " AND p.quantity > p.reorder_level"
    
    query += " ORDER BY p.name"
    
    products_df = db.get_dataframe(query, params)
    
    if not products_df.empty:
        # Add stock status column
        def get_stock_status(row):
            if row['quantity'] == 0:
                return "🟠 Out of Stock"
            elif row['quantity'] <= row['reorder_level']:
                return "🟡 Low Stock"
            else:
                return "🟢 In Stock"
        
        products_df['Stock Status'] = products_df.apply(get_stock_status, axis=1)
        
        # Display with formatting
        st.dataframe(
            products_df[['name', 'category', 'supplier', 'quantity', 'unit_price', 'reorder_level', 'Stock Status']],
            use_container_width=True,
            column_config={
                "name": "Product Name",
                "category": "Category",
                "supplier": "Supplier",
                "quantity": "Quantity",
                "unit_price": st.column_config.NumberColumn("Unit Price (₹)", format="₹%.2f"),
                "reorder_level": "Reorder Level",
                "Stock Status": "Stock Status"
            }
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = products_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No products found matching the criteria.")

def add_product(db):
    st.subheader("➕ Add New Product")
    
    # Get categories and suppliers first
    categories = db.execute_query("SELECT id, name FROM categories ORDER BY name")
    suppliers = db.execute_query("SELECT id, name FROM suppliers ORDER BY name")
    
    if not categories:
        st.error("⚠️ No categories available. Please create categories first in Settings → Categories.")
        return
    
    if not suppliers:
        st.error("⚠️ No suppliers available. Please create suppliers first.")
        return
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Product Name *", placeholder="Enter product name")
            
            # Create category mapping
            category_options = {cat['id']: cat['name'] for cat in categories}
            category_id = st.selectbox(
                "Category *",
                options=list(category_options.keys()),
                format_func=lambda x: category_options[x]
            )
            
            # Create supplier mapping
            supplier_options = {sup['id']: sup['name'] for sup in suppliers}
            supplier_id = st.selectbox(
                "Supplier *",
                options=list(supplier_options.keys()),
                format_func=lambda x: supplier_options[x]
            )
        
        with col2:
            quantity = st.number_input("Initial Quantity *", min_value=0, value=0)
            unit_price = st.number_input("Unit Price (₹) *", min_value=0.0, value=0.0, step=0.01)
            reorder_level = st.number_input("Reorder Level *", min_value=0, value=10)
        
        submitted = st.form_submit_button("✅ Add Product", type="primary")
        
        if submitted:
            if not name or not name.strip():
                st.error("❌ Product name is required.")
            elif not category_id:
                st.error("❌ Category is required.")
            elif not supplier_id:
                st.error("❌ Supplier is required.")
            else:
                query = """
                    INSERT INTO products (name, category_id, supplier_id, quantity, unit_price, reorder_level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                if db.execute_update(query, (name.strip(), category_id, supplier_id, quantity, unit_price, reorder_level)):
                    st.success(f"✅ Product '{name}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add product. Please try again.")

def update_product(db):
    st.subheader("✏️ Update Product")
    
    # Get all products for selection
    products = db.execute_query("SELECT id, name FROM products ORDER BY name")
    
    if not products:
        st.info("ℹ️ No products available to update.")
        return
    
    # Create product mapping
    product_options = {p['id']: p['name'] for p in products}
    selected_product_id = st.selectbox(
        "Select Product to Update",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x]
    )
    
    if selected_product_id:
        # Get current product data
        product = db.execute_query("SELECT * FROM products WHERE id = %s", (selected_product_id,))[0]
        
        # Get categories and suppliers
        categories = db.execute_query("SELECT id, name FROM categories ORDER BY name")
        suppliers = db.execute_query("SELECT id, name FROM suppliers ORDER BY name")
        
        if not categories or not suppliers:
            st.error("⚠️ Categories or suppliers are missing. Please add them first.")
            return
        
        category_options = {cat['id']: cat['name'] for cat in categories}
        supplier_options = {sup['id']: sup['name'] for sup in suppliers}
        
        with st.form("update_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name *", value=product['name'])
                
                # Find current category index
                category_index = 0
                if product['category_id']:
                    category_list = list(category_options.keys())
                    if product['category_id'] in category_list:
                        category_index = category_list.index(product['category_id'])
                
                category_id = st.selectbox(
                    "Category *",
                    options=list(category_options.keys()),
                    index=category_index,
                    format_func=lambda x: category_options[x]
                )
                
                # Find current supplier index
                supplier_index = 0
                if product['supplier_id']:
                    supplier_list = list(supplier_options.keys())
                    if product['supplier_id'] in supplier_list:
                        supplier_index = supplier_list.index(product['supplier_id'])
                
                supplier_id = st.selectbox(
                    "Supplier *",
                    options=list(supplier_options.keys()),
                    index=supplier_index,
                    format_func=lambda x: supplier_options[x]
                )
            
            with col2:
                quantity = st.number_input("Quantity *", min_value=0, value=product['quantity'])
                unit_price = st.number_input("Unit Price (₹) *", min_value=0.0, value=float(product['unit_price']), step=0.01)
                reorder_level = st.number_input("Reorder Level *", min_value=0, value=product['reorder_level'])
            
            submitted = st.form_submit_button("✅ Update Product", type="primary")
            
            if submitted:
                if not name or not name.strip():
                    st.error("❌ Product name is required.")
                else:
                    query = """
                        UPDATE products 
                        SET name = %s, category_id = %s, supplier_id = %s, quantity = %s, unit_price = %s, reorder_level = %s
                        WHERE id = %s
                    """
                    
                    if db.execute_update(query, (name.strip(), category_id, supplier_id, quantity, unit_price, reorder_level, selected_product_id)):
                        st.success(f"✅ Product '{name}' updated successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update product. Please try again.")

def delete_product(db):
    st.subheader("🗑️ Delete Product")
    
    # Get all products for selection
    products = db.execute_query("SELECT id, name FROM products ORDER BY name")
    
    if not products:
        st.info("No products available to delete.")
        return
    
    selected_product_id = st.selectbox(
        "Select Product to Delete",
        options=[p['id'] for p in products],
        format_func=lambda x: [p['name'] for p in products if p['id'] == x][0]
    )
    
    if selected_product_id:
        # Get product details
        product = db.execute_query("SELECT * FROM products WHERE id = %s", (selected_product_id,))[0]
        
        st.warning(f"⚠️ You are about to delete: {product['name']}")
        st.info(f"Current stock: {product['quantity']}")
        
        # Check if product is used in orders
        order_usage = db.execute_query("""
            SELECT 
                (SELECT COUNT(*) FROM sales_order_items WHERE product_id = %s) as sales_count,
                (SELECT COUNT(*) FROM purchase_order_items WHERE product_id = %s) as purchase_count
        """, (selected_product_id, selected_product_id))
        
        if order_usage and (order_usage[0]['sales_count'] > 0 or order_usage[0]['purchase_count'] > 0):
            st.error("⚠️ This product cannot be deleted as it is used in existing orders.")
            return
        
        if st.button("🗑️ Delete Product", type="primary"):
            if db.execute_update("DELETE FROM products WHERE id = %s", (selected_product_id,)):
                st.toast(f"Product '{product['name']}' deleted successfully!", icon="✅")
                st.rerun()
            else:
                st.error("Failed to delete product. Please try again.")
