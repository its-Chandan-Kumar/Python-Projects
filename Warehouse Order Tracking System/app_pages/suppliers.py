import streamlit as st
import pandas as pd
from database import DatabaseManager
from datetime import datetime

def show_suppliers():
    st.title("🏭 Supplier Management")
    st.markdown("---")
    
    db = DatabaseManager()
    
    # Sidebar for actions
    with st.sidebar:
        st.header("Actions")
        action = st.selectbox(
            "Choose Action",
            ["View Suppliers", "Add Supplier", "Update Supplier", "Delete Supplier"]
        )
    
    if action == "View Suppliers":
        view_suppliers(db)
    elif action == "Add Supplier":
        add_supplier(db)
    elif action == "Update Supplier":
        update_supplier(db)
    elif action == "Delete Supplier":
        delete_supplier(db)

def view_suppliers(db):
    st.subheader("📋 All Suppliers")
    
    # Search functionality
    search = st.text_input("Search suppliers", placeholder="Supplier name, contact person, or email...")
    
    # Build query
    query = "SELECT * FROM suppliers WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE %s OR contact_person LIKE %s OR email LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += " ORDER BY name"
    
    suppliers_df = db.get_dataframe(query, params)
    
    if not suppliers_df.empty:
        # Display with formatting
        st.dataframe(
            suppliers_df[['name', 'contact_person', 'email', 'phone', 'address']],
            use_container_width=True,
            column_config={
                "name": "Supplier Name",
                "contact_person": "Contact Person",
                "email": "Email",
                "phone": "Phone",
                "address": "Address"
            }
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = suppliers_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"suppliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No suppliers found matching the criteria.")

def add_supplier(db):
    st.subheader("➕ Add New Supplier")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Supplier Name *", placeholder="Enter supplier name")
            contact_person = st.text_input("Contact Person", placeholder="Enter contact person name")
            email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            phone = st.text_input("Phone", placeholder="Enter phone number")
            address = st.text_area("Address", placeholder="Enter address")
        
        submitted = st.form_submit_button("Add Supplier")
        
        if submitted:
            if name:
                query = """
                    INSERT INTO suppliers (name, contact_person, email, phone, address)
                    VALUES (%s, %s, %s, %s, %s)
                """
                
                if db.execute_update(query, (name, contact_person, email, phone, address)):
                    st.toast(f"Supplier '{name}' added successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to add supplier. Please try again.")
            else:
                st.error("Supplier name is required.")

def update_supplier(db):
    st.subheader("✏️ Update Supplier")
    
    # Get all suppliers for selection
    suppliers = db.execute_query("SELECT id, name FROM suppliers ORDER BY name")
    
    if not suppliers:
        st.info("No suppliers available to update.")
        return
    
    selected_supplier_id = st.selectbox(
        "Select Supplier to Update",
        options=[s['id'] for s in suppliers],
        format_func=lambda x: [s['name'] for s in suppliers if s['id'] == x][0]
    )
    
    if selected_supplier_id:
        # Get current supplier data
        supplier = db.execute_query("SELECT * FROM suppliers WHERE id = %s", (selected_supplier_id,))[0]
        
        with st.form("update_supplier_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Supplier Name", value=supplier['name'])
                contact_person = st.text_input("Contact Person", value=supplier['contact_person'] or "")
                email = st.text_input("Email", value=supplier['email'] or "")
            
            with col2:
                phone = st.text_input("Phone", value=supplier['phone'] or "")
                address = st.text_area("Address", value=supplier['address'] or "")
            
            submitted = st.form_submit_button("Update Supplier")
            
            if submitted:
                query = """
                    UPDATE suppliers 
                    SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s
                    WHERE id = %s
                """
                
                if db.execute_update(query, (name, contact_person, email, phone, address, selected_supplier_id)):
                    st.toast(f"Supplier '{name}' updated successfully!", icon="✅")
                    st.rerun()
                else:
                    st.error("Failed to update supplier. Please try again.")

def delete_supplier(db):
    st.subheader("🗑️ Delete Supplier")
    
    # Get all suppliers for selection
    suppliers = db.execute_query("SELECT id, name FROM suppliers ORDER BY name")
    
    if not suppliers:
        st.info("No suppliers available to delete.")
        return
    
    selected_supplier_id = st.selectbox(
        "Select Supplier to Delete",
        options=[s['id'] for s in suppliers],
        format_func=lambda x: [s['name'] for s in suppliers if s['id'] == x][0]
    )
    
    if selected_supplier_id:
        # Get supplier details
        supplier = db.execute_query("SELECT * FROM suppliers WHERE id = %s", (selected_supplier_id,))[0]
        
        st.warning(f"⚠️ You are about to delete: {supplier['name']}")
        
        # Check if supplier is used in products or orders
        usage_check = db.execute_query("""
            SELECT 
                (SELECT COUNT(*) FROM products WHERE supplier_id = %s) as products_count,
                (SELECT COUNT(*) FROM purchase_orders WHERE supplier_id = %s) as orders_count
        """, (selected_supplier_id, selected_supplier_id))
        
        if usage_check and (usage_check[0]['products_count'] > 0 or usage_check[0]['orders_count'] > 0):
            st.error("⚠️ This supplier cannot be deleted as it is associated with products or orders.")
            if usage_check[0]['products_count'] > 0:
                st.info(f"Associated with {usage_check[0]['products_count']} products")
            if usage_check[0]['orders_count'] > 0:
                st.info(f"Associated with {usage_check[0]['orders_count']} purchase orders")
            return
        
        if st.button("🗑️ Delete Supplier", type="primary"):
            if db.execute_update("DELETE FROM suppliers WHERE id = %s", (selected_supplier_id,)):
                st.toast(f"Supplier '{supplier['name']}' deleted successfully!", icon="✅")
                st.rerun()
            else:
                st.error("Failed to delete supplier. Please try again.")
