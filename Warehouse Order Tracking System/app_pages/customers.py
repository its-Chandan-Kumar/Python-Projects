import streamlit as st
import pandas as pd
from database import DatabaseManager
from datetime import datetime

def show_customers():
    st.title("👥 Customer Management")
    st.markdown("---")
    
    db = DatabaseManager()
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        action = st.selectbox(
            "Choose Action",
            ["View Customers", "Add Customer", "Update Customer", "Delete Customer"]
        )
    
    if action == "View Customers":
        view_customers(db)
    elif action == "Add Customer":
        add_customer(db)
    elif action == "Update Customer":
        update_customer(db)
    elif action == "Delete Customer":
        delete_customer(db)

def view_customers(db):
    st.subheader("📋 All Customers")
    
    # Search functionality
    search = st.text_input("Search customers", placeholder="Customer name, contact person, or email...")
    
    # Build query
    query = "SELECT * FROM customers WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR contact_person LIKE %s OR email LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY name"
    
    customers_df = db.get_dataframe(query, params)
    
    if not customers_df.empty:
        # Display with formatting
        st.dataframe(
            customers_df[['name', 'contact_person', 'email', 'phone', 'address']],
            use_container_width=True,
            column_config={
                "name": "Customer Name",
                "contact_person": "Contact Person",
                "email": "Email",
                "phone": "Phone",
                "address": "Address"
            }
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = customers_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No customers found matching the criteria.")

def add_customer(db):
    st.subheader("➕ Add New Customer")
    
    with st.form("add_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Customer Name *", placeholder="Enter customer name")
            contact_person = st.text_input("Contact Person", placeholder="Enter contact person name")
            email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            phone = st.text_input("Phone", placeholder="Enter phone number")
            address = st.text_area("Address", placeholder="Enter address")
        
        submitted = st.form_submit_button("Add Customer")
        
        if submitted:
            if name:
                query = """
                    INSERT INTO customers (name, contact_person, email, phone, address)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                if db.execute_update(query, (name, contact_person, email, phone, address)):
                    st.toast(f"Customer '{name}' added successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to add customer. Please try again.")
            else:
                st.error("Customer name is required.")

def update_customer(db):
    st.subheader("✏️ Update Customer")
    
    # Get all customers for selection
    customers = db.execute_query("SELECT id, name FROM customers ORDER BY name")
    
    if not customers:
        st.info("No customers available to update.")
        return
    
    selected_customer_id = st.selectbox(
        "Select Customer to Update",
        options=[c['id'] for c in customers],
        format_func=lambda x: [c['name'] for c in customers if c['id'] == x][0]
    )
    
    if selected_customer_id:
        # Get current customer data
        customer = db.execute_query("SELECT * FROM customers WHERE id = %s", (selected_customer_id,))[0]
        
        with st.form("update_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Customer Name", value=customer['name'])
                contact_person = st.text_input("Contact Person", value=customer['contact_person'] or "")
                email = st.text_input("Email", value=customer['email'] or "")
            
            with col2:
                phone = st.text_input("Phone", value=customer['phone'] or "")
                address = st.text_area("Address", value=customer['address'] or "")
            
            submitted = st.form_submit_button("Update Customer")
            
            if submitted:
                query = """
                    UPDATE customers 
                    SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s
                    WHERE id = %s
                """
                
                if db.execute_update(query, (name, contact_person, email, phone, address, selected_customer_id)):
                    st.toast(f"Customer '{name}' updated successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to update customer. Please try again.")

def delete_customer(db):
    st.subheader("🗑️ Delete Customer")
    
    # Get all customers for selection
    customers = db.execute_query("SELECT id, name FROM customers ORDER BY name")
    
    if not customers:
        st.info("No customers available to delete.")
        return
    
    selected_customer_id = st.selectbox(
        "Select Customer to Delete",
        options=[c['id'] for c in customers],
        format_func=lambda x: [c['name'] for c in customers if c['id'] == x][0]
    )
    
    if selected_customer_id:
        # Get customer details
        customer = db.execute_query("SELECT * FROM customers WHERE id = %s", (selected_customer_id,))[0]
        
        st.warning(f"⚠️ You are about to delete: {customer['name']}")
        
        # Check if customer is used in orders
        usage_check = db.execute_query("""
            SELECT COUNT(*) as orders_count
            FROM sales_orders 
            WHERE customer_id = %s
        """, (selected_customer_id,))
        
        if usage_check and usage_check[0]['orders_count'] > 0:
            st.error("⚠️ This customer cannot be deleted as it is associated with sales orders.")
            st.info(f"Associated with {usage_check[0]['orders_count']} sales orders")
            return
        
        if st.button("🗑️ Delete Customer", type="primary"):
            if db.execute_update("DELETE FROM customers WHERE id = %s", (selected_customer_id,)):
                st.toast(f"Customer '{customer['name']}' deleted successfully!", icon="✅")
                st.rerun()
            else:
                st.error("Failed to delete customer. Please try again.")
