import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import DatabaseManager

def show_dashboard():
    st.title("📊 Dashboard")
    
    db = DatabaseManager()
    
    # Check if database is empty and suggest populating
    product_count = db.execute_query("SELECT COUNT(*) as count FROM products")
    if product_count and product_count[0]['count'] == 0:
        st.warning("⚠️ **Database is empty!** Run `python generate_dummy_data.py` to populate with sample data.")
        if st.button("📥 Generate Sample Data Now"):
            import subprocess
            import sys
            try:
                result = subprocess.run([sys.executable, "generate_dummy_data.py"], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    st.success("✅ Sample data generated successfully! Please refresh the page.")
                    st.rerun()
                else:
                    st.error(f"Error generating data: {result.stderr}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Get statistics
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Products
    total_products = db.execute_query("SELECT COUNT(*) as count FROM products")
    total_products_count = total_products[0]['count'] if total_products else 0
    
    with col1:
        st.metric(
            label="Total Products",
            value=total_products_count,
            delta=""
        )
    
    # Low Stock Products
    low_stock = db.execute_query("SELECT COUNT(*) as count FROM products WHERE quantity <= reorder_level")
    low_stock_count = low_stock[0]['count'] if low_stock else 0
    
    with col2:
        st.metric(
            label="Low Stock Products",
            value=low_stock_count,
            delta="",
            delta_color="inverse"
        )
    
    # Check user role for financial metrics
    user_role = st.session_state.get('role', 'staff')
    
    # Total Sales (only for admin)
    if user_role == 'admin':
        total_sales = db.execute_query("SELECT SUM(total_amount) as total FROM sales_orders WHERE status = 'completed'")
        total_sales_amount = total_sales[0]['total'] if total_sales and total_sales[0]['total'] else 0
        
        with col3:
            st.metric(
                label="Total Sales",
                value=f"₹{total_sales_amount:,.2f}",
                delta=""
            )
        
        # Total Purchases (only for admin)
        total_purchases = db.execute_query("SELECT SUM(total_amount) as total FROM purchase_orders WHERE status = 'completed'")
        total_purchases_amount = total_purchases[0]['total'] if total_purchases and total_purchases[0]['total'] else 0
        
        with col4:
            st.metric(
                label="Total Purchases",
                value=f"₹{total_purchases_amount:,.2f}",
                delta=""
            )
    else:
        # Staff sees different metrics
        with col3:
            total_customers = db.execute_query("SELECT COUNT(*) as count FROM customers")
            customers_count = total_customers[0]['count'] if total_customers else 0
            st.metric(
                label="Total Customers",
                value=customers_count,
                delta=""
            )
        
        with col4:
            total_suppliers = db.execute_query("SELECT COUNT(*) as count FROM suppliers")
            suppliers_count = total_suppliers[0]['count'] if total_suppliers else 0
            st.metric(
                label="Total Suppliers",
                value=suppliers_count,
                delta=""
            )
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    # Check user role for charts
    user_role = st.session_state.get('role', 'staff')
    
    with col1:
        if user_role == 'admin':
            st.subheader("📈 Monthly Revenue")
            
            # Get monthly sales data
            monthly_sales_query = """
                SELECT 
                    strftime('%Y-%m', order_date) as month,
                    SUM(total_amount) as revenue
                FROM sales_orders 
                WHERE status = 'completed'
                GROUP BY strftime('%Y-%m', order_date)
                ORDER BY month DESC
                LIMIT 12
            """
            
            monthly_sales_df = db.get_dataframe(monthly_sales_query)
            
            if not monthly_sales_df.empty:
                fig = px.line(
                    monthly_sales_df, 
                    x='month', 
                    y='revenue',
                    title="Monthly Sales Revenue",
                    labels={'month': 'Month', 'revenue': 'Revenue (₹)'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sales data available for charting.")
        else:
            st.subheader("📦 Products by Category")
            
            # Show products by category for staff
            category_products_query = """
                SELECT c.name as category, COUNT(p.id) as product_count
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                GROUP BY c.id, c.name
                ORDER BY product_count DESC
            """
            
            category_df = db.get_dataframe(category_products_query)
            
            if not category_df.empty:
                fig = px.pie(
                    category_df,
                    values='product_count',
                    names='category',
                    title="Product Distribution by Category"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available.")
    
    with col2:
        st.subheader("📦 Low Stock Alerts")
        
        # Get low stock products
        low_stock_query = """
            SELECT p.name, p.quantity, p.reorder_level, c.name as category
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.quantity <= p.reorder_level
            ORDER BY p.quantity ASC
        """
        
        low_stock_df = db.get_dataframe(low_stock_query)
        
        if not low_stock_df.empty:
            fig = px.bar(
                low_stock_df,
                x='name',
                y='quantity',
                color='category',
                title="Low Stock Products",
                labels={'name': 'Product', 'quantity': 'Current Stock', 'category': 'Category'}
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("All products are well stocked!")
    
    st.markdown("---")
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛒 Recent Sales Orders")
        recent_sales_query = """
            SELECT so.order_number, so.order_date, so.total_amount, so.status, c.name as customer
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.id
            ORDER BY so.created_at DESC
            LIMIT 10
        """
        
        recent_sales_df = db.get_dataframe(recent_sales_query)
        if not recent_sales_df.empty:
            st.dataframe(recent_sales_df, use_container_width=True)
        else:
            st.info("No sales orders found.")
    
    with col2:
        st.subheader("📦 Recent Purchase Orders")
        recent_purchases_query = """
            SELECT po.order_number, po.order_date, po.total_amount, po.status, s.name as supplier
            FROM purchase_orders po
            LEFT JOIN suppliers s ON po.supplier_id = s.id
            ORDER BY po.created_at DESC
            LIMIT 10
        """
        
        recent_purchases_df = db.get_dataframe(recent_purchases_query)
        if not recent_purchases_df.empty:
            st.dataframe(recent_purchases_df, use_container_width=True)
        else:
            st.info("No purchase orders found.")
    
    # Top Products by Sales (only for admin)
    if user_role == 'admin':
        st.markdown("---")
        st.subheader("🏆 Top Products by Sales")
        
        top_products_query = """
            SELECT 
                p.name as product_name,
                SUM(soi.quantity) as total_sold,
                SUM(soi.total_price) as total_revenue
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            JOIN sales_orders so ON soi.sales_order_id = so.id
            WHERE so.status = 'completed'
            GROUP BY p.id, p.name
            ORDER BY total_revenue DESC
            LIMIT 10
        """
        
        top_products_df = db.get_dataframe(top_products_query)
        if not top_products_df.empty:
            fig = px.bar(
                top_products_df,
                x='product_name',
                y='total_revenue',
                title="Top Products by Revenue",
                labels={'product_name': 'Product', 'total_revenue': 'Total Revenue (₹)'}
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data available for top products analysis.")
