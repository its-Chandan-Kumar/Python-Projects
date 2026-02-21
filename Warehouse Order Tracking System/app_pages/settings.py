import streamlit as st
import pandas as pd
from database import DatabaseManager
from auth import AuthManager
from datetime import datetime

def show_settings():
    st.title("⚙️ Settings")
    st.markdown("---")
    
    db = DatabaseManager()
    auth = AuthManager()
    
    # Sidebar for settings categories
    with st.sidebar:
        st.header("Settings")
        setting_type = st.selectbox(
            "Choose Setting",
            ["User Management", "Categories", "System Info"]
        )
    
    if setting_type == "User Management":
        show_user_management(auth, db)
    elif setting_type == "Categories":
        show_category_management(db)
    elif setting_type == "System Info":
        show_system_info(db)

def show_user_management(auth, db):
    st.subheader("👥 User Management")
    
    # Check if current user is admin
    if st.session_state.get('role') != 'admin':
        st.error("Only administrators can manage users.")
        return
    
    # Create new user
    with st.expander("➕ Create New User", expanded=False):
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username *", placeholder="Enter username")
                password = st.text_input("Password *", type="password", placeholder="Enter password")
            
            with col2:
                confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm password")
                role = st.selectbox("Role *", ["staff", "admin"])
            
            submitted = st.form_submit_button("Create User")
            
            if submitted:
                if not username or not password:
                    st.error("Username and password are required.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    if auth.create_user(username, password, role):
                        st.toast(f"User '{username}' created successfully!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Username might already exist.")
    
    st.markdown("---")
    
    # View and manage existing users
    st.subheader("📋 All Users")
    
    users_query = "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
    users_df = db.get_dataframe(users_query)
    
    if not users_df.empty:
        # Add actions column
        users_df['Actions'] = users_df['id'].apply(lambda x: f"User ID: {x}")
        
        st.dataframe(
            users_df[['username', 'role', 'created_at']],
            use_container_width=True,
            column_config={
                "username": "Username",
                "role": "Role",
                "created_at": "Created At"
            }
        )
        
        # Export option
        if st.button("📥 Export Users to CSV"):
            csv = users_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No users found.")
    
    # Change password section - DISABLED FOR DEMO PROJECT
    st.markdown("---")
    st.subheader("🔐 Change Password")
    st.info("ℹ️ Password change functionality is disabled for this demo project.")
    st.warning("⚠️ This is a demonstration system. Password changes are not available.")
    
    # Disabled form for visual consistency
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password", placeholder="Enter current password", disabled=True)
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password", disabled=True)
        confirm_new_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password", disabled=True)
        
        submitted = st.form_submit_button("Change Password", disabled=True)
        
        if submitted:
            st.info("Password change is disabled in this demo project.")

def show_category_management(db):
    st.subheader("📂 Category Management")
    
    # Create new category
    with st.expander("➕ Create New Category", expanded=False):
        with st.form("create_category_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Category Name *", placeholder="Enter category name")
            
            with col2:
                description = st.text_area("Description", placeholder="Enter category description")
            
            submitted = st.form_submit_button("Create Category")
            
            if submitted:
                if not name:
                    st.error("Category name is required.")
                else:
                    # Check if category already exists
                    existing = db.execute_query("SELECT id FROM categories WHERE name = %s", (name,))
                    if existing:
                        st.error("Category with this name already exists.")
                    else:
                        query = "INSERT INTO categories (name, description) VALUES (%s, %s)"
                        if db.execute_update(query, (name, description)):
                            st.toast(f"Category '{name}' created successfully!", icon="✅")
                            st.rerun()
                        else:
                            st.error("Failed to create category.")
    
    st.markdown("---")
    
    # View and manage existing categories
    st.subheader("📋 All Categories")
    
    categories_query = "SELECT * FROM categories ORDER BY name"
    categories_df = db.get_dataframe(categories_query)
    
    if not categories_df.empty:
        # Add actions column
        categories_df['Actions'] = categories_df['id'].apply(lambda x: f"Category ID: {x}")
        
        st.dataframe(
            categories_df[['name', 'description']],
            use_container_width=True,
            column_config={
                "name": "Category Name",
                "description": "Description"
            }
        )
        
        # Export option
        if st.button("📥 Export Categories to CSV"):
            csv = categories_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Delete category option
        st.markdown("---")
        st.subheader("🗑️ Delete Category")
        
        category_to_delete = st.selectbox(
            "Select Category to Delete",
            options=[c['id'] for c in categories_df.to_dict('records')],
            format_func=lambda x: [c['name'] for c in categories_df.to_dict('records') if c['id'] == x][0]
        )
        
        if category_to_delete:
            # Check if category is used in products
            usage_check = db.execute_query("""
                SELECT COUNT(*) as products_count
                FROM products 
                WHERE category_id = %s
            """, (category_to_delete,))
            
            if usage_check and usage_check[0]['products_count'] > 0:
                st.error("⚠️ This category cannot be deleted as it is associated with products.")
                st.info(f"Associated with {usage_check[0]['products_count']} products")
            else:
                category_name = [c['name'] for c in categories_df.to_dict('records') if c['id'] == category_to_delete][0]
                st.warning(f"⚠️ You are about to delete: {category_name}")
                
                if st.button("🗑️ Delete Category", type="primary"):
                    if db.execute_update("DELETE FROM categories WHERE id = %s", (category_to_delete,)):
                        st.toast(f"Category '{category_name}' deleted successfully!", icon="✅")
                        st.rerun()
                    else:
                        st.error("Failed to delete category.")
    else:
        st.info("No categories found.")
    
    # Update category
    if not categories_df.empty:
        st.markdown("---")
        st.subheader("✏️ Update Category")
        
        category_to_update = st.selectbox(
            "Select Category to Update",
            options=[c['id'] for c in categories_df.to_dict('records')],
            format_func=lambda x: [c['name'] for c in categories_df.to_dict('records') if c['id'] == x][0],
            key="update_category"
        )
        
        if category_to_update:
            # Get current category data
            category = [c for c in categories_df.to_dict('records') if c['id'] == category_to_update][0]
            
            with st.form("update_category_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Category Name", value=category['name'])
                
                with col2:
                    description = st.text_area("Description", value=category['description'] or "")
                
                submitted = st.form_submit_button("Update Category")
                
                if submitted:
                    if not name:
                        st.error("Category name is required.")
                    else:
                        # Check if name already exists (excluding current category)
                        existing = db.execute_query("SELECT id FROM categories WHERE name = %s AND id != %s", (name, category_to_update))
                        if existing:
                            st.error("Category with this name already exists.")
                        else:
                            query = "UPDATE categories SET name = %s, description = %s WHERE id = %s"
                            if db.execute_update(query, (name, description, category_to_update)):
                                st.toast(f"Category '{name}' updated successfully!", icon="✅")
                                st.rerun()
                            else:
                                st.error("Failed to update category.")

def show_system_info(db):
    st.subheader("ℹ️ System Information")
    
    # Database connection status
    st.markdown("### 🔌 Database Connection")
    
    try:
        if db.connection and db.connection.is_connected():
            st.success("✅ Database connected successfully")
            
            # Get database info
            cursor = db.connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Database Version:** {version[0] if version else 'Unknown'}")
                st.info(f"**Host:** {db.connection.server_host}")
                st.info(f"**Database:** {db.connection.database}")
            
            with col2:
                st.info(f"**Port:** {db.connection.server_port}")
                st.info(f"**User:** {db.connection.user}")
                st.info(f"**Connection ID:** {db.connection.connection_id}")
        else:
            st.error("❌ Database connection failed")
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
    
    st.markdown("---")
    
    # System Statistics
    st.markdown("### 📊 System Statistics")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        # Count records in each table
        tables = ['users', 'products', 'suppliers', 'customers', 'categories', 'sales_orders', 'purchase_orders']
        
        with col1:
            users_count = db.execute_query("SELECT COUNT(*) as count FROM users")
            st.metric("Users", users_count[0]['count'] if users_count else 0)
            
            products_count = db.execute_query("SELECT COUNT(*) as count FROM products")
            st.metric("Products", products_count[0]['count'] if products_count else 0)
        
        with col2:
            suppliers_count = db.execute_query("SELECT COUNT(*) as count FROM suppliers")
            st.metric("Suppliers", suppliers_count[0]['count'] if suppliers_count else 0)
            
            customers_count = db.execute_query("SELECT COUNT(*) as count FROM customers")
            st.metric("Customers", customers_count[0]['count'] if customers_count else 0)
        
        with col3:
            categories_count = db.execute_query("SELECT COUNT(*) as count FROM categories")
            st.metric("Categories", categories_count[0]['count'] if categories_count else 0)
            
            sales_orders_count = db.execute_query("SELECT COUNT(*) as count FROM sales_orders")
            st.metric("Sales Orders", sales_orders_count[0]['count'] if sales_orders_count else 0)
        
        with col4:
            purchase_orders_count = db.execute_query("SELECT COUNT(*) as count FROM purchase_orders")
            st.metric("Purchase Orders", purchase_orders_count[0]['count'] if purchase_orders_count else 0)
            
            # Total database size (approximate)
            total_records = sum([
                users_count[0]['count'] if users_count else 0,
                products_count[0]['count'] if products_count else 0,
                suppliers_count[0]['count'] if suppliers_count else 0,
                customers_count[0]['count'] if customers_count else 0,
                categories_count[0]['count'] if categories_count else 0,
                sales_orders_count[0]['count'] if sales_orders_count else 0,
                purchase_orders_count[0]['count'] if purchase_orders_count else 0
            ])
            st.metric("Total Records", total_records)
        
    except Exception as e:
        st.error(f"Error getting system statistics: {e}")
    
    st.markdown("---")
    
    # Current Session Info
    st.markdown("### 👤 Current Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Username:** {st.session_state.get('username', 'Not logged in')}")
        st.info(f"**Role:** {st.session_state.get('role', 'N/A')}")
    
    with col2:
        st.info(f"**User ID:** {st.session_state.get('user_id', 'N/A')}")
        st.info(f"**Authenticated:** {'Yes' if st.session_state.get('authenticated', False) else 'No'}")
    
    # Logout button
    if st.session_state.get('authenticated'):
        st.markdown("---")
        if st.button("🚪 Logout", type="primary"):
            auth = AuthManager()
            auth.logout()
            st.toast("Logged out successfully!", icon="✅")
            st.rerun()
