# Warehouse Order Tracking System

A comprehensive warehouse management system built with Python, Streamlit, and SQLite for tracking products, suppliers, customers, and orders with real-time inventory management.

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

## 📋 Prerequisites

Before running this application, ensure you have:

1. **Python 3.8+** installed on your system
2. **No database server required** - SQLite uses a file-based database
3. **Git** for cloning the repository

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd warehouse-order-tracking-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

#### Configure Database Connection

1. Copy the example environment file:
   ```bash
   copy env_example.txt .env
   ```
   (On Linux/Mac: `cp env_example.txt .env`)

2. Edit the `.env` file with your database configuration:
   ```env
   DB_HOST=****
   DB_USER=root
   DB_PASSWORD=****
   DB_NAME=warehouse_tracking
   DB_PORT=****
   ```

   **⚠️ Important**: The `.env` file contains sensitive information and is gitignored. Never commit it to version control.

The database will be created automatically when you first run the application.

### 4. Generate Dummy Data (Optional)

To populate the database with sample data for testing:

```bash
python generate_dummy_data.py
```

This will create:
- 5 demo user accounts
- 10 categories
- 30 suppliers
- 40 customers
- 60 products
- 35 purchase orders
- 45 sales orders

**Total: ~210 records**

### 5. Run the Application

```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🔐 Demo Login Credentials

The system includes several demo accounts for testing:

### Administrator Accounts:
- **Username**: `admin` | **Password**: `admin123`
- **Username**: `manager` | **Password**: `manager123`

### Staff Accounts:
- **Username**: `staff1` | **Password**: `staff123`
- **Username**: `staff2` | **Password**: `staff123`
- **Username**: `demo` | **Password**: `demo123`

**⚠️ Important**: These are demo credentials. Please change passwords after first login in a production environment.

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

## 🔧 Configuration Options

### Environment Variables
The application uses a `.env` file for secure configuration. See `env_example.txt` for the template.

**Password Encryption**: Database passwords are stored securely in the `.env` file and can be encrypted using the encryption key. The password is never hardcoded in the application files.

**Security Note**: 
- Never commit the `.env` file to version control
- Change the `ENCRYPTION_KEY` in production
- Use strong passwords for database access

### Customization
- Modify `config.py` for application settings
- Update database queries in individual page files
- Customize UI themes in Streamlit configuration

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - No database server required
   - Check connection credentials in `config.py`
   - Ensure database exists

2. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Port Already in Use**
   - Change port in Streamlit configuration
   - Kill existing processes using the port

### Logs and Debugging
- Check Streamlit console output for errors
- Verify database connection status in Settings page
- Use browser developer tools for frontend issues

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- Complete CRUD operations for all entities
- Real-time inventory tracking
- Comprehensive reporting system
- User authentication and authorization

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Database powered by [SQLite](https://www.sqlite.org/)
- Icons from [Bootstrap Icons](https://icons.getbootstrap.com/)
- Charts powered by [Plotly](https://plotly.com/)

---

**Note**: This is a production-ready warehouse management system. Always backup your data before making significant changes, and test thoroughly in a development environment before deploying to production.
