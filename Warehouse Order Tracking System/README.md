# Warehouse Order Tracking System

A comprehensive warehouse management system built with Python, Streamlit, and SQLite for tracking products, suppliers, customers, and orders with real-time inventory management.

# Live Demo
https://warehouse-order-tracking-system.onrender.com

## 🚀 Features

### 🔐 Authentication & Security
- **User Management**: Admin and staff login with role-based access control
- **Password Security**: Bcrypt password hashing for secure authentication
- **Session Management**: Secure session handling with Streamlit

### 📦 Product Management
- **CRUD Operations**: Add, view, update, and delete products
- **Inventory Tracking**: Real-time stock monitoring with reorder level alerts
- **Category Management**: Organize products by categories
- **Supplier Integration**: Link products to suppliers

### 🏭 Supplier & Customer Management
- **Supplier CRUD**: Complete supplier information management
- **Customer CRUD**: Customer database with contact details
- **Relationship Tracking**: Link suppliers and customers to orders

### 📋 Order Management
- **Sales Orders**: Track outgoing orders with customer details
- **Purchase Orders**: Manage incoming inventory with supplier information
- **Order Status**: Track order progress (pending/completed/cancelled)
- **Auto Inventory**: Automatic stock updates on order completion

### 📊 Reports & Analytics
- **Dashboard**: Real-time statistics and key performance indicators
- **Sales Reports**: Revenue analysis and trend visualization
- **Purchase Reports**: Expense tracking and supplier analysis
- **Inventory Reports**: Stock levels and low-stock alerts
- **Financial Reports**: Profit/loss analysis and margin calculations
- **Interactive Charts**: Plotly-powered visualizations

### 📥 Export Functionality
- **CSV Export**: Download reports in CSV format
- **Excel Support**: Export data with proper formatting
- **Custom Date Ranges**: Flexible reporting periods

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **Database**: SQLite
- **Authentication**: Bcrypt for password hashing
- **Data Visualization**: Plotly and Altair
- **Data Processing**: Pandas for data manipulation

## 🔐 Demo Login Credentials

The system includes several demo accounts for testing:

### Administrator Accounts:
- **Username**: `admin` | **Password**: `admin123`
- **Username**: `manager` | **Password**: `manager123`

### Staff Accounts:
- **Username**: `staff1` | **Password**: `staff123`
- **Username**: `staff2` | **Password**: `staff123`
- **Username**: `demo` | **Password**: `demo123`

## 📱 Application Structure

```
warehouse-order-tracking-system/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings with encryption
├── database.py            # Database connection and management
├── auth.py                # Authentication and authorization
├── generate_dummy_data.py # Script to generate sample data
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in repo)
├── env_example.txt       # Example environment file
├── .gitignore           # Git ignore rules
├── README.md             # This file
└── app_pages/            # Application pages
    ├── dashboard.py      # Dashboard and analytics
    ├── products.py       # Product management
    ├── suppliers.py      # Supplier management
    ├── customers.py      # Customer management
    ├── orders.py         # Order management
    ├── reports.py        # Reports and analytics
    └── settings.py       # User and system settings
```

## 🗄️ Database Schema

The system automatically creates the following tables:

- **users**: User authentication and roles
- **categories**: Product categories
- **suppliers**: Supplier information
- **customers**: Customer information
- **products**: Product inventory
- **sales_orders**: Customer orders
- **sales_order_items**: Sales order details
- **purchase_orders**: Supplier orders
- **purchase_order_items**: Purchase order details

## 🎯 Key Features Explained

### Real-time Inventory Tracking
- Automatic stock updates when orders are completed
- Low-stock alerts based on reorder levels
- Stock status indicators (In Stock, Low Stock, Out of Stock)

### Comprehensive Reporting
- **Sales Analytics**: Revenue trends, top products, customer insights
- **Purchase Analytics**: Expense tracking, supplier performance
- **Inventory Analytics**: Stock levels, category distribution
- **Financial Analytics**: Profit/loss, margins, cash flow

### User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **Intuitive Navigation**: Sidebar navigation with clear icons
- **Search & Filter**: Advanced filtering for all data tables
- **Export Options**: Download data in multiple formats

## 📈 Performance Optimization

- **Database Indexing**: Ensure proper indexes on frequently queried columns
- **Query Optimization**: Use efficient SQL queries with proper JOINs
- **Caching**: Implement Streamlit caching for expensive operations
- **Connection Pooling**: Optimize database connection management

## 🔒 Security Considerations

- **Password Hashing**: All passwords are hashed using bcrypt
- **SQL Injection Prevention**: Parameterized queries throughout
- **Session Management**: Secure session handling
- **Role-based Access**: Admin and staff role separation

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Database powered by [SQLite](https://www.sqlite.org/)
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/)
- Charts powered by [Plotly](https://plotly.com/)

---

