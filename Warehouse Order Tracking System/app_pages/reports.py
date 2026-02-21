import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from database import DatabaseManager

def show_reports():
    st.title("📊 Reports & Analytics")
    st.markdown("---")
    
    # Check user role
    user_role = st.session_state.get('role', 'staff')
    
    db = DatabaseManager()
    
    # Sidebar for report type selection
    with st.sidebar:
        st.header("Report Type")
        
        # Staff can only see Inventory Reports
        if user_role == 'staff':
            report_type = "Inventory Reports"
            st.info("ℹ️ Staff can only view Inventory Reports")
        else:
            report_type = st.selectbox(
                "Choose Report",
                ["Sales Reports", "Purchase Reports", "Inventory Reports", "Financial Reports"]
            )
        
        st.header("Date Range")
        date_range = st.selectbox(
            "Select Date Range",
            ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "Last Year", "Custom Range"]
        )
        
        if date_range == "Custom Range":
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
            end_date = st.date_input("End Date", value=date.today())
        else:
            # Calculate date range
            end_date = date.today()
            if date_range == "Last 7 Days":
                start_date = end_date - timedelta(days=7)
            elif date_range == "Last 30 Days":
                start_date = end_date - timedelta(days=30)
            elif date_range == "Last 3 Months":
                start_date = end_date - timedelta(days=90)
            elif date_range == "Last 6 Months":
                start_date = end_date - timedelta(days=180)
            elif date_range == "Last Year":
                start_date = end_date - timedelta(days=365)
    
    if report_type == "Sales Reports":
        show_sales_reports(db, start_date, end_date)
    elif report_type == "Purchase Reports":
        show_purchase_reports(db, start_date, end_date)
    elif report_type == "Inventory Reports":
        show_inventory_reports(db)
    elif report_type == "Financial Reports":
        show_financial_reports(db, start_date, end_date)

def show_sales_reports(db, start_date, end_date):
    # Check if user is admin
    user_role = st.session_state.get('role', 'staff')
    if user_role == 'staff':
        st.error("❌ Access Denied: Staff members cannot view sales reports.")
        return
    
    st.subheader("🛒 Sales Reports")
    
    # Sales Summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Sales
    total_sales_query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_order_value
        FROM sales_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
    """
    
    sales_summary = db.execute_query(total_sales_query, (start_date, end_date))
    if sales_summary and sales_summary[0]['total_orders']:
        total_orders = sales_summary[0]['total_orders']
        total_revenue = sales_summary[0]['total_revenue'] or 0
        avg_order_value = sales_summary[0]['avg_order_value'] or 0
    else:
        total_orders = 0
        total_revenue = 0
        avg_order_value = 0
    
    with col1:
        st.metric("Total Orders", total_orders)
    
    with col2:
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
    with col3:
        st.metric("Average Order Value", f"₹{avg_order_value:,.2f}")
    
    with col4:
        # Top selling product
        top_product_query = """
            SELECT p.name, SUM(soi.quantity) as total_sold
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            JOIN sales_orders so ON soi.sales_order_id = so.id
            WHERE so.order_date BETWEEN ? AND ? AND so.status = 'completed'
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT 1
        """
        top_product = db.execute_query(top_product_query, (start_date, end_date))
        if top_product:
            st.metric("Top Product", top_product[0]['name'])
        else:
            st.metric("Top Product", "N/A")
    
    st.markdown("---")
    
    # Sales Trend Chart
    st.subheader("📈 Sales Trend")
    
    sales_trend_query = """
        SELECT 
            date(order_date) as date,
            COUNT(*) as orders,
            SUM(total_amount) as revenue
        FROM sales_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
        GROUP BY date(order_date)
        ORDER BY date
    """
    
    sales_trend_df = db.get_dataframe(sales_trend_query, (start_date, end_date))
    
    if not sales_trend_df.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sales_trend_df['date'],
            y=sales_trend_df['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig.add_trace(go.Bar(
            x=sales_trend_df['date'],
            y=sales_trend_df['orders'],
            name='Orders',
            yaxis='y2',
            opacity=0.3
        ))
        
        fig.update_layout(
            title="Daily Sales Trend",
            xaxis_title="Date",
            yaxis=dict(title="Revenue (₹)", side="left"),
            yaxis2=dict(title="Number of Orders", side="right", overlaying="y"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available for the selected date range.")
    
    # Top Products by Sales
    st.subheader("🏆 Top Products by Sales")
    
    top_products_query = """
        SELECT 
            p.name as product_name,
            SUM(soi.quantity) as total_sold,
            SUM(soi.total_price) as total_revenue,
            AVG(soi.unit_price) as avg_price
        FROM sales_order_items soi
        JOIN products p ON soi.product_id = p.id
        JOIN sales_orders so ON soi.sales_order_id = so.id
        WHERE so.order_date BETWEEN ? AND ? AND so.status = 'completed'
        GROUP BY p.id, p.name
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    
    top_products_df = db.get_dataframe(top_products_query, (start_date, end_date))
    
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
        
        # Display table
        st.dataframe(
            top_products_df,
            use_container_width=True,
            column_config={
                "product_name": "Product Name",
                "total_sold": "Total Sold",
                "total_revenue": st.column_config.NumberColumn("Total Revenue (₹)", format="₹%.2f"),
                "avg_price": st.column_config.NumberColumn("Average Price (₹)", format="₹%.2f")
            }
        )
        
        # Export option
        if st.button("📥 Export Sales Report to CSV"):
            csv = top_products_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"sales_report_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No product sales data available for the selected date range.")

def show_purchase_reports(db, start_date, end_date):
    # Check if user is admin
    user_role = st.session_state.get('role', 'staff')
    if user_role == 'staff':
        st.error("❌ Access Denied: Staff members cannot view purchase reports.")
        return
    
    st.subheader("📦 Purchase Reports")
    
    # Purchase Summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Purchases
    total_purchases_query = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_amount) as total_spent,
            AVG(total_amount) as avg_order_value
        FROM purchase_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
    """
    
    purchase_summary = db.execute_query(total_purchases_query, (start_date, end_date))
    if purchase_summary and purchase_summary[0]['total_orders']:
        total_orders = purchase_summary[0]['total_orders']
        total_spent = purchase_summary[0]['total_spent'] or 0
        avg_order_value = purchase_summary[0]['avg_order_value'] or 0
    else:
        total_orders = 0
        total_spent = 0
        avg_order_value = 0
    
    with col1:
        st.metric("Total Orders", total_orders)
    
    with col2:
        st.metric("Total Spent", f"₹{total_spent:,.2f}")
    
    with col3:
        st.metric("Average Order Value", f"₹{avg_order_value:,.2f}")
    
    with col4:
        # Top supplier
        top_supplier_query = """
            SELECT s.name, SUM(po.total_amount) as total_spent
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.order_date BETWEEN ? AND ? AND po.status = 'completed'
            GROUP BY s.id, s.name
            ORDER BY total_spent DESC
            LIMIT 1
        """
        top_supplier = db.execute_query(top_supplier_query, (start_date, end_date))
        if top_supplier:
            st.metric("Top Supplier", top_supplier[0]['name'])
        else:
            st.metric("Top Supplier", "N/A")
    
    st.markdown("---")
    
    # Purchase Trend Chart
    st.subheader("📈 Purchase Trend")
    
    purchase_trend_query = """
        SELECT 
            date(order_date) as date,
            COUNT(*) as orders,
            SUM(total_amount) as spent
        FROM purchase_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
        GROUP BY date(order_date)
        ORDER BY date
    """
    
    purchase_trend_df = db.get_dataframe(purchase_trend_query, (start_date, end_date))
    
    if not purchase_trend_df.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=purchase_trend_df['date'],
            y=purchase_trend_df['spent'],
            mode='lines+markers',
            name='Amount Spent',
            line=dict(color='#ff7f0e', width=3)
        ))
        
        fig.add_trace(go.Bar(
            x=purchase_trend_df['date'],
            y=purchase_trend_df['orders'],
            name='Orders',
            yaxis='y2',
            opacity=0.3
        ))
        
        fig.update_layout(
            title="Daily Purchase Trend",
            xaxis_title="Date",
            yaxis=dict(title="Amount Spent (₹)", side="left"),
            yaxis2=dict(title="Number of Orders", side="right", overlaying="y"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No purchase data available for the selected date range.")
    
    # Top Products by Purchase
    st.subheader("🏆 Top Products by Purchase")
    
    top_purchase_products_query = """
        SELECT 
            p.name as product_name,
            SUM(poi.quantity) as total_purchased,
            SUM(poi.total_price) as total_spent,
            AVG(poi.unit_price) as avg_price
        FROM purchase_order_items poi
        JOIN products p ON poi.product_id = p.id
        JOIN purchase_orders po ON poi.purchase_order_id = po.id
        WHERE po.order_date BETWEEN ? AND ? AND po.status = 'completed'
        GROUP BY p.id, p.name
        ORDER BY total_spent DESC
        LIMIT 10
    """
    
    top_purchase_products_df = db.get_dataframe(top_purchase_products_query, (start_date, end_date))
    
    if not top_purchase_products_df.empty:
        fig = px.bar(
            top_purchase_products_df,
            x='product_name',
            y='total_spent',
            title="Top Products by Purchase Amount",
            labels={'product_name': 'Product', 'total_spent': 'Total Spent (₹)'}
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display table
        st.dataframe(
            top_purchase_products_df,
            use_container_width=True,
            column_config={
                "product_name": "Product Name",
                "total_purchased": "Total Purchased",
                "total_spent": st.column_config.NumberColumn("Total Spent (₹)", format="₹%.2f"),
                "avg_price": st.column_config.NumberColumn("Average Price (₹)", format="₹%.2f")
            }
        )
        
        # Export option
        if st.button("📥 Export Purchase Report to CSV"):
            csv = top_purchase_products_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"purchase_report_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No product purchase data available for the selected date range.")

def show_inventory_reports(db):
    st.subheader("📦 Inventory Reports")
    
    # Inventory Summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Products
    total_products = db.execute_query("SELECT COUNT(*) as count FROM products")
    total_products_count = total_products[0]['count'] if total_products else 0
    
    with col1:
        st.metric("Total Products", total_products_count)
    
    # Low Stock Products
    low_stock = db.execute_query("SELECT COUNT(*) as count FROM products WHERE quantity <= reorder_level")
    low_stock_count = low_stock[0]['count'] if low_stock else 0
    
    with col2:
        st.metric("Low Stock Products", low_stock_count, delta_color="inverse")
    
    # Out of Stock Products
    out_of_stock = db.execute_query("SELECT COUNT(*) as count FROM products WHERE quantity = 0")
    out_of_stock_count = out_of_stock[0]['count'] if out_of_stock else 0
    
    with col3:
        st.metric("Out of Stock", out_of_stock_count, delta_color="inverse")
    
    # Total Inventory Value
    total_value = db.execute_query("SELECT SUM(quantity * unit_price) as value FROM products")
    total_inventory_value = total_value[0]['value'] if total_value and total_value[0]['value'] else 0
    
    with col4:
        st.metric("Total Inventory Value", f"₹{total_inventory_value:,.2f}")
    
    st.markdown("---")
    
    # Low Stock Alerts
    st.subheader("⚠️ Low Stock Alerts")
    
    low_stock_query = """
        SELECT 
            p.name, p.quantity, p.reorder_level, p.unit_price,
            c.name as category, s.name as supplier
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.quantity <= p.reorder_level
        ORDER BY p.quantity ASC
    """
    
    low_stock_df = db.get_dataframe(low_stock_query)
    
    if not low_stock_df.empty:
        # Add stock status column
        def get_stock_status(row):
            if row['quantity'] == 0:
                return "🟠 Out of Stock"
            elif row['quantity'] <= row['reorder_level']:
                return "🟡 Low Stock"
            else:
                return "🟢 In Stock"
        
        low_stock_df['Stock Status'] = low_stock_df.apply(get_stock_status, axis=1)
        
        st.dataframe(
            low_stock_df[['name', 'category', 'supplier', 'quantity', 'reorder_level', 'unit_price', 'Stock Status']],
            use_container_width=True,
            column_config={
                "name": "Product Name",
                "category": "Category",
                "supplier": "Supplier",
                "quantity": "Current Stock",
                "reorder_level": "Reorder Level",
                "unit_price": st.column_config.NumberColumn("Unit Price (₹)", format="₹%.2f"),
                "Stock Status": "Stock Status"
            }
        )
        
        # Export option
        if st.button("📥 Export Low Stock Report to CSV"):
            csv = low_stock_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"low_stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("All products are well stocked!")
    
    # Inventory by Category
    st.subheader("📊 Inventory by Category")
    
    category_inventory_query = """
        SELECT 
            c.name as category,
            COUNT(p.id) as product_count,
            SUM(p.quantity) as total_quantity,
            SUM(p.quantity * p.unit_price) as total_value
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY total_value DESC
    """
    
    category_inventory_df = db.get_dataframe(category_inventory_query)
    
    if not category_inventory_df.empty:
        fig = px.pie(
            category_inventory_df,
            values='total_value',
            names='category',
            title="Inventory Value by Category"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display table
        st.dataframe(
            category_inventory_df,
            use_container_width=True,
            column_config={
                "category": "Category",
                "product_count": "Product Count",
                "total_quantity": "Total Quantity",
                "total_value": st.column_config.NumberColumn("Total Value (₹)", format="₹%.2f")
            }
        )

def show_financial_reports(db, start_date, end_date):
    # Check if user is admin
    user_role = st.session_state.get('role', 'staff')
    if user_role == 'staff':
        st.error("❌ Access Denied: Staff members cannot view financial reports.")
        return
    
    st.subheader("💰 Financial Reports")
    
    # Financial Summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Revenue
    total_revenue_query = """
        SELECT SUM(total_amount) as revenue
        FROM sales_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
    """
    
    total_revenue = db.execute_query(total_revenue_query, (start_date, end_date))
    total_revenue_amount = total_revenue[0]['revenue'] if total_revenue and total_revenue[0]['revenue'] else 0
    
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue_amount:,.2f}")
    
    # Total Expenses
    total_expenses_query = """
        SELECT SUM(total_amount) as expenses
        FROM purchase_orders 
        WHERE order_date BETWEEN ? AND ? AND status = 'completed'
    """
    
    total_expenses = db.execute_query(total_expenses_query, (start_date, end_date))
    total_expenses_amount = total_expenses[0]['expenses'] if total_expenses and total_expenses[0]['expenses'] else 0
    
    with col2:
        st.metric("Total Expenses", f"₹{total_expenses_amount:,.2f}")
    
    # Net Profit
    net_profit = total_revenue_amount - total_expenses_amount
    
    with col3:
        st.metric("Net Profit", f"₹{net_profit:,.2f}", delta=f"₹{net_profit:,.2f}")
    
    # Profit Margin
    profit_margin = (net_profit / total_revenue_amount * 100) if total_revenue_amount > 0 else 0
    
    with col4:
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    st.markdown("---")
    
    # Profit vs Loss Chart
    st.subheader("📈 Profit vs Loss Analysis")
    
    # Monthly breakdown
    monthly_financial_query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type = 'revenue' THEN amount ELSE 0 END) as revenue,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expenses
        FROM (
            SELECT order_date as date, total_amount as amount, 'revenue' as type
            FROM sales_orders 
            WHERE order_date BETWEEN ? AND ? AND status = 'completed'
            UNION ALL
            SELECT order_date as date, total_amount as amount, 'expense' as type
            FROM purchase_orders 
            WHERE order_date BETWEEN ? AND ? AND status = 'completed'
        ) combined
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """
    
    monthly_financial_df = db.get_dataframe(monthly_financial_query, (start_date, end_date, start_date, end_date))
    
    if not monthly_financial_df.empty:
        monthly_financial_df['profit'] = monthly_financial_df['revenue'] - monthly_financial_df['expenses']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_financial_df['month'],
            y=monthly_financial_df['revenue'],
            name='Revenue',
            marker_color='#2ecc71'
        ))
        
        fig.add_trace(go.Bar(
            x=monthly_financial_df['month'],
            y=monthly_financial_df['expenses'],
            name='Expenses',
            marker_color='#e74c3c'
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_financial_df['month'],
            y=monthly_financial_df['profit'],
            mode='lines+markers',
            name='Net Profit',
            line=dict(color='#3498db', width=3)
        ))
        
        fig.update_layout(
            title="Monthly Financial Overview",
            xaxis_title="Month",
            yaxis_title="Amount (₹)",
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display table
        st.dataframe(
            monthly_financial_df,
            use_container_width=True,
            column_config={
                "month": "Month",
                "revenue": st.column_config.NumberColumn("Revenue (₹)", format="₹%.2f"),
                "expenses": st.column_config.NumberColumn("Expenses (₹)", format="₹%.2f"),
                "profit": st.column_config.NumberColumn("Net Profit (₹)", format="₹%.2f")
            }
        )
        
        # Export option
        if st.button("📥 Export Financial Report to CSV"):
            csv = monthly_financial_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"financial_report_{start_date}_{end_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No financial data available for the selected date range.")
