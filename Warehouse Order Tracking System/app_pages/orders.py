import streamlit as st
import pandas as pd
from database import DatabaseManager
from datetime import datetime, date
import uuid

def show_orders():
    st.title("📋 Order Management")
    st.markdown("---")
    
    db = DatabaseManager()
    
    # Sidebar for order type selection
    with st.sidebar:
        st.header("Order Type")
        order_type = st.selectbox(
            "Choose Order Type",
            ["Sales Orders", "Purchase Orders"]
        )
        
        st.header("Actions")
        action = st.selectbox(
            "Choose Action",
            ["View Orders", "Create Order", "Update Order", "Delete Order"]
        )
    
    if order_type == "Sales Orders":
        if action == "View Orders":
            view_sales_orders(db)
        elif action == "Create Order":
            create_sales_order(db)
        elif action == "Update Order":
            update_sales_order(db)
        elif action == "Delete Order":
            delete_sales_order(db)
    else:
        if action == "View Orders":
            view_purchase_orders(db)
        elif action == "Create Order":
            create_purchase_order(db)
        elif action == "Update Order":
            update_purchase_order(db)
        elif action == "Delete Order":
            delete_purchase_order(db)

def view_sales_orders(db):
    st.subheader("🛒 Sales Orders")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("Search orders", placeholder="Order number or customer...")
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "completed", "cancelled"]
        )
    
    with col3:
        date_filter = st.date_input(
            "Filter by Date",
            value=date.today(),
            max_value=date.today()
        )
    
    # Check user role for audit trail
    user_role = st.session_state.get('role', 'staff')
    
    # Build query - include created_by for admin
    if user_role == 'admin':
        query = """
            SELECT 
                so.id, so.order_number, so.order_date, so.total_amount, so.status,
                c.name as customer, c.contact_person, c.email,
                u.username as created_by
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.id
            LEFT JOIN users u ON so.created_by = u.id
            WHERE 1=1
        """
    else:
        query = """
            SELECT 
                so.id, so.order_number, so.order_date, so.total_amount, so.status,
                c.name as customer, c.contact_person, c.email
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.id
            WHERE 1=1
        """
    params = []
    
    if search:
        query += " AND (so.order_number LIKE ? OR c.name LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    if status_filter != "All":
        query += " AND so.status = ?"
        params.append(status_filter)
    
    if date_filter:
        query += " AND so.order_date = ?"
        params.append(date_filter)
    
    query += " ORDER BY so.created_at DESC"
    
    sales_orders_df = db.get_dataframe(query, params)
    
    if not sales_orders_df.empty:
        # Select columns based on user role
        if user_role == 'admin':
            display_columns = ['order_number', 'order_date', 'customer', 'total_amount', 'status', 'created_by']
            column_config = {
                "order_number": "Order Number",
                "order_date": "Order Date",
                "customer": "Customer",
                "total_amount": st.column_config.NumberColumn("Total Amount (₹)", format="₹%.2f"),
                "status": "Status",
                "created_by": "Created By"
            }
        else:
            display_columns = ['order_number', 'order_date', 'customer', 'total_amount', 'status']
            column_config = {
                "order_number": "Order Number",
                "order_date": "Order Date",
                "customer": "Customer",
                "total_amount": st.column_config.NumberColumn("Total Amount (₹)", format="₹%.2f"),
                "status": "Status"
            }
        
        st.dataframe(
            sales_orders_df[display_columns],
            use_container_width=True,
            column_config=column_config
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = sales_orders_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"sales_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No sales orders found matching the criteria.")

def create_sales_order(db):
    st.subheader("➕ Create Sales Order")
    
    # Get available customers and products
    customers = db.execute_query("SELECT id, name FROM customers ORDER BY name")
    products = db.execute_query("SELECT id, name, quantity, unit_price FROM products WHERE quantity > 0 ORDER BY name")
    
    if not customers:
        st.error("No customers available. Please add customers first.")
        return
    
    if not products:
        st.error("No products available. Please add products first.")
        return
    
    with st.form("create_sales_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_id = st.selectbox(
                "Customer *",
                options=[c['id'] for c in customers],
                format_func=lambda x: [c['name'] for c in customers if c['id'] == x][0]
            )
            order_date = st.date_input("Order Date *", value=date.today())
        
        with col2:
            order_number = st.text_input("Order Number", value=f"SO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
            status = st.selectbox("Status", ["pending", "completed", "cancelled"])
        
        st.markdown("### Order Items")
        
        # Dynamic order items
        if 'order_items' not in st.session_state:
            st.session_state.order_items = []
        
        # Add item button (must use form submit inside st.form)
        add_item = st.form_submit_button("➕ Add Item")
        if add_item:
            st.session_state.order_items.append({
                'product_id': products[0]['id'] if products else None,
                'quantity': 1,
                'unit_price': 0.0
            })
            st.rerun()
        
        # Display and edit order items
        for i, item in enumerate(st.session_state.order_items):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    product_id = st.selectbox(
                        f"Product {i+1}",
                        options=[p['id'] for p in products],
                        index=[p['id'] for p in products].index(item['product_id']) if item['product_id'] else 0,
                        format_func=lambda x: [p['name'] for p in products if p['id'] == x][0] if x else "Select product",
                        key=f"product_{i}"
                    )
                
                with col2:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=item['quantity'],
                        key=f"quantity_{i}"
                    )
                
                with col3:
                    unit_price = st.number_input(
                        "Unit Price (₹)",
                        min_value=0.0,
                        value=float(item['unit_price']),
                        step=0.01,
                        key=f"unit_price_{i}"
                    )
                
                with col4:
                    remove_clicked = st.form_submit_button(f"❌ Remove {i+1}")
                    if remove_clicked:
                        st.session_state.order_items.pop(i)
                        st.rerun()
                
                # Update item
                st.session_state.order_items[i] = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                }
        
        # Calculate total
        total_amount = sum(item['quantity'] * item['unit_price'] for item in st.session_state.order_items)
        st.markdown(f"**Total Amount: ₹{total_amount:.2f}**")
        
        submitted = st.form_submit_button("Create Sales Order")
        
        if submitted:
            if not st.session_state.order_items:
                st.error("Please add at least one item to the order.")
                return
            
            # Validate stock availability
            for item in st.session_state.order_items:
                product = [p for p in products if p['id'] == item['product_id']][0]
                if item['quantity'] > product['quantity']:
                    st.error(f"Insufficient stock for {product['name']}. Available: {product['quantity']}")
                    return
            
            # Create sales order
            try:
                # Get current user ID
                user_id = st.session_state.get('user_id')
                
                # Insert sales order with user tracking
                order_query = """
                    INSERT INTO sales_orders (order_number, customer_id, order_date, total_amount, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                
                if db.execute_update(order_query, (order_number, customer_id, order_date, total_amount, status, user_id)):
                    # Get the created order ID
                    order_id = db.execute_query("SELECT id FROM sales_orders WHERE order_number = ?", (order_number,))[0]['id']
                    
                    # Insert order items
                    for item in st.session_state.order_items:
                        item_query = """
                            INSERT INTO sales_order_items (sales_order_id, product_id, quantity, unit_price, total_price)
                            VALUES (?, ?, ?, ?, ?)
                        """
                        item_total = item['quantity'] * item['unit_price']
                        
                        if not db.execute_update(item_query, (order_id, item['product_id'], item['quantity'], item['unit_price'], item_total)):
                            st.error("Failed to create order items.")
                            return
                        
                        # Update product quantity if order is completed
                        if status == 'completed':
                            update_query = """
                                UPDATE products 
                                SET quantity = quantity - ? 
                                WHERE id = ?
                            """
                            db.execute_update(update_query, (item['quantity'], item['product_id']))
                    
                    st.toast(f"Sales order '{order_number}' created successfully!", icon="✅")
                    st.session_state.order_items = []
                    st.rerun()
                else:
                    st.error("Failed to create sales order.")
            except Exception as e:
                st.error(f"Error creating sales order: {e}")

def update_sales_order(db):
    st.subheader("✏️ Update Sales Order")
    
    # Get all sales orders
    sales_orders = db.execute_query("SELECT id, order_number, status FROM sales_orders ORDER BY created_at DESC")
    
    if not sales_orders:
        st.info("No sales orders available to update.")
        return
    
    selected_order_id = st.selectbox(
        "Select Sales Order to Update",
        options=[o['id'] for o in sales_orders],
        format_func=lambda x: [o['order_number'] for o in sales_orders if o['id'] == x][0]
    )
    
    if selected_order_id:
        # Get current order data
        order = db.execute_query("SELECT * FROM sales_orders WHERE id = ?", (selected_order_id,))[0]
        
        with st.form("update_sales_order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                order_number = st.text_input("Order Number", value=order['order_number'])
                order_date = st.date_input("Order Date", value=order['order_date'])
            
            with col2:
                status = st.selectbox("Status", ["pending", "completed", "cancelled"], index=["pending", "completed", "cancelled"].index(order['status']))
            
            submitted = st.form_submit_button("Update Sales Order")
            
            if submitted:
                query = """
                    UPDATE sales_orders 
                    SET order_number = ?, order_date = ?, status = ?
                    WHERE id = ?
                """
                
                if db.execute_update(query, (order_number, order_date, status, selected_order_id)):
                    st.toast(f"Sales order '{order_number}' updated successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to update sales order.")

def delete_sales_order(db):
    st.subheader("🗑️ Delete Sales Order")
    
    # Get all sales orders
    sales_orders = db.execute_query("SELECT id, order_number, status FROM sales_orders ORDER BY created_at DESC")
    
    if not sales_orders:
        st.info("No sales orders available to delete.")
        return
    
    selected_order_id = st.selectbox(
        "Select Sales Order to Delete",
        options=[o['id'] for o in sales_orders],
        format_func=lambda x: [o['order_number'] for o in sales_orders if o['id'] == x][0]
    )
    
    if selected_order_id:
        # Get order details
        order = db.execute_query("SELECT * FROM sales_orders WHERE id = ?", (selected_order_id,))[0]
        
        st.warning(f"⚠️ You are about to delete: {order['order_number']}")
        st.info(f"Status: {order['status']}")
        
        if st.button("🗑️ Delete Sales Order", type="primary"):
            # Delete order items first
            if db.execute_update("DELETE FROM sales_order_items WHERE sales_order_id = ?", (selected_order_id,)):
                # Delete the order
                if db.execute_update("DELETE FROM sales_orders WHERE id = ?", (selected_order_id,)):
                    st.toast(f"Sales order '{order['order_number']}' deleted successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to delete sales order.")
            else:
                st.error("Failed to delete order items.")

def view_purchase_orders(db):
    st.subheader("📦 Purchase Orders")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("Search purchase orders", placeholder="Order number or supplier...")
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "pending", "completed", "cancelled"]
        )
    
    with col3:
        date_filter = st.date_input(
            "Filter by Date",
            value=date.today(),
            max_value=date.today()
        )
    
    # Check user role for audit trail
    user_role = st.session_state.get('role', 'staff')
    
    # Build query - include created_by for admin
    if user_role == 'admin':
        query = """
            SELECT 
                po.id, po.order_number, po.order_date, po.total_amount, po.status,
                s.name as supplier, s.contact_person, s.email,
                u.username as created_by
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users u ON po.created_by = u.id
            WHERE 1=1
        """
    else:
        query = """
            SELECT 
                po.id, po.order_number, po.order_date, po.total_amount, po.status,
                s.name as supplier, s.contact_person, s.email
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            WHERE 1=1
        """
    params = []
    
    if search:
        query += " AND (po.order_number LIKE ? OR s.name LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    if status_filter != "All":
        query += " AND po.status = ?"
        params.append(status_filter)
    
    if date_filter:
        query += " AND po.order_date = ?"
        params.append(date_filter)
    
    query += " ORDER BY po.created_at DESC"
    
    purchase_orders_df = db.get_dataframe(query, params)
    
    if not purchase_orders_df.empty:
        # Select columns based on user role
        if user_role == 'admin':
            display_columns = ['order_number', 'order_date', 'supplier', 'total_amount', 'status', 'created_by']
            column_config = {
                "order_number": "Order Number",
                "order_date": "Order Date",
                "supplier": "Supplier",
                "total_amount": st.column_config.NumberColumn("Total Amount (₹)", format="₹%.2f"),
                "status": "Status",
                "created_by": "Created By"
            }
        else:
            display_columns = ['order_number', 'order_date', 'supplier', 'total_amount', 'status']
            column_config = {
                "order_number": "Order Number",
                "order_date": "Order Date",
                "supplier": "Supplier",
                "total_amount": st.column_config.NumberColumn("Total Amount (₹)", format="₹%.2f"),
                "status": "Status"
            }
        
        st.dataframe(
            purchase_orders_df[display_columns],
            use_container_width=True,
            column_config=column_config
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = purchase_orders_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"purchase_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No purchase orders found matching the criteria.")

def create_purchase_order(db):
    st.subheader("➕ Create Purchase Order")
    
    # Get available suppliers and products
    suppliers = db.execute_query("SELECT id, name FROM suppliers ORDER BY name")
    products = db.execute_query("SELECT id, name, unit_price FROM products ORDER BY name")
    
    if not suppliers:
        st.error("No suppliers available. Please add suppliers first.")
        return
    
    if not products:
        st.error("No products available. Please add products first.")
        return
    
    with st.form("create_purchase_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            supplier_id = st.selectbox(
                "Supplier *",
                options=[s['id'] for s in suppliers],
                format_func=lambda x: [s['name'] for s in suppliers if s['id'] == x][0]
            )
            order_date = st.date_input("Order Date *", value=date.today())
        
        with col2:
            order_number = st.text_input("Order Number", value=f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
            status = st.selectbox("Status", ["pending", "completed", "cancelled"])
        
        st.markdown("### Order Items")
        
        # Dynamic order items
        if 'purchase_order_items' not in st.session_state:
            st.session_state.purchase_order_items = []
        
        # Add item button (must use form submit inside st.form)
        add_item = st.form_submit_button("➕ Add Item")
        if add_item:
            st.session_state.purchase_order_items.append({
                'product_id': products[0]['id'] if products else None,
                'quantity': 1,
                'unit_price': 0.0
            })
            st.rerun()
        
        # Display and edit order items
        for i, item in enumerate(st.session_state.purchase_order_items):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    product_id = st.selectbox(
                        f"Product {i+1}",
                        options=[p['id'] for p in products],
                        index=[p['id'] for p in products].index(item['product_id']) if item['product_id'] else 0,
                        format_func=lambda x: [p['name'] for p in products if p['id'] == x][0] if x else "Select product",
                        key=f"purchase_product_{i}"
                    )
                
                with col2:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        value=item['quantity'],
                        key=f"purchase_quantity_{i}"
                    )
                
                with col3:
                    unit_price = st.number_input(
                        "Unit Price (₹)",
                        min_value=0.0,
                        value=float(item['unit_price']),
                        step=0.01,
                        key=f"purchase_unit_price_{i}"
                    )
                
                with col4:
                    remove_clicked = st.form_submit_button(f"❌ Remove {i+1}")
                    if remove_clicked:
                        st.session_state.purchase_order_items.pop(i)
                        st.rerun()
                
                # Update item
                st.session_state.purchase_order_items[i] = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                }
        
        # Calculate total
        total_amount = sum(item['quantity'] * item['unit_price'] for item in st.session_state.purchase_order_items)
        st.markdown(f"**Total Amount: ₹{total_amount:.2f}**")
        
        submitted = st.form_submit_button("Create Purchase Order")
        
        if submitted:
            if not st.session_state.purchase_order_items:
                st.error("Please add at least one item to the order.")
                return
            
            # Create purchase order
            try:
                # Get current user ID
                user_id = st.session_state.get('user_id')
                
                # Insert purchase order with user tracking
                order_query = """
                    INSERT INTO purchase_orders (order_number, supplier_id, order_date, total_amount, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
                
                if db.execute_update(order_query, (order_number, supplier_id, order_date, total_amount, status, user_id)):
                    # Get the created order ID
                    order_id = db.execute_query("SELECT id FROM purchase_orders WHERE order_number = ?", (order_number,))[0]['id']
                    
                    # Insert order items
                    for item in st.session_state.purchase_order_items:
                        item_query = """
                            INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price, total_price)
                            VALUES (?, ?, ?, ?, ?)
                        """
                        item_total = item['quantity'] * item['unit_price']
                        
                        if not db.execute_update(item_query, (order_id, item['product_id'], item['quantity'], item['unit_price'], item_total)):
                            st.error("Failed to create order items.")
                            return
                        
                        # Update product quantity if order is completed
                        if status == 'completed':
                            update_query = """
                                UPDATE products 
                                SET quantity = quantity + ? 
                                WHERE id = ?
                            """
                            db.execute_update(update_query, (item['quantity'], item['product_id']))
                    
                    st.toast(f"Purchase order '{order_number}' created successfully!", icon="✅")
                    st.session_state.purchase_order_items = []
                    st.rerun()
                else:
                    st.error("Failed to create purchase order.")
            except Exception as e:
                st.error(f"Error creating purchase order: {e}")

def update_purchase_order(db):
    st.subheader("✏️ Update Purchase Order")
    
    # Get all purchase orders
    purchase_orders = db.execute_query("SELECT id, order_number, status FROM purchase_orders ORDER BY created_at DESC")
    
    if not purchase_orders:
        st.info("No purchase orders available to update.")
        return
    
    selected_order_id = st.selectbox(
        "Select Purchase Order to Update",
        options=[o['id'] for o in purchase_orders],
        format_func=lambda x: [o['order_number'] for o in purchase_orders if o['id'] == x][0]
    )
    
    if selected_order_id:
        # Get current order data
        order = db.execute_query("SELECT * FROM purchase_orders WHERE id = ?", (selected_order_id,))[0]
        
        with st.form("update_purchase_order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                order_number = st.text_input("Order Number", value=order['order_number'])
                order_date = st.date_input("Order Date", value=order['order_date'])
            
            with col2:
                status = st.selectbox("Status", ["pending", "completed", "cancelled"], index=["pending", "completed", "cancelled"].index(order['status']))
            
            submitted = st.form_submit_button("Update Purchase Order")
            
            if submitted:
                query = """
                    UPDATE purchase_orders 
                    SET order_number = ?, order_date = ?, status = ?
                    WHERE id = ?
                """
                
                if db.execute_update(query, (order_number, order_date, status, selected_order_id)):
                    st.toast(f"Purchase order '{order_number}' updated successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to update purchase order.")

def delete_purchase_order(db):
    st.subheader("🗑️ Delete Purchase Order")
    
    # Get all purchase orders
    purchase_orders = db.execute_query("SELECT id, order_number, status FROM purchase_orders ORDER BY created_at DESC")
    
    if not purchase_orders:
        st.info("No purchase orders available to delete.")
        return
    
    selected_order_id = st.selectbox(
        "Select Purchase Order to Delete",
        options=[o['id'] for o in purchase_orders],
        format_func=lambda x: [o['order_number'] for o in purchase_orders if o['id'] == x][0]
    )
    
    if selected_order_id:
        # Get order details
        order = db.execute_query("SELECT * FROM purchase_orders WHERE id = ?", (selected_order_id,))[0]
        
        st.warning(f"⚠️ You are about to delete: {order['order_number']}")
        st.info(f"Status: {order['status']}")
        
        if st.button("🗑️ Delete Purchase Order", type="primary"):
            # Delete order items first
            if db.execute_update("DELETE FROM purchase_order_items WHERE purchase_order_id = ?", (selected_order_id,)):
                # Delete the order
                if db.execute_update("DELETE FROM purchase_orders WHERE id = ?", (selected_order_id,)):
                    st.toast(f"Purchase order '{order['order_number']}' deleted successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to delete purchase order.")
            else:
                st.error("Failed to delete order items.")
