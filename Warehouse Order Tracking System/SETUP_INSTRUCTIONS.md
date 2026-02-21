# Quick Setup Instructions

## Step 1: Create .env File

Since the `.env` file is gitignored for security, you need to create it manually:

1. Copy `env_example.txt` to `.env`:
   - **Windows**: `copy env_example.txt .env`
   - **Linux/Mac**: `cp env_example.txt .env`

2. The `.env` file should contain:
   ```env
   DB_HOST=127.0.0.1
   DB_USER=root
   DB_PASSWORD=1234567890
   DB_NAME=warehouse_tracking
   DB_PORT=3306
   ENCRYPTION_KEY=warehouse-tracking-system-secret-key-change-in-production
   ```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Generate Dummy Data (Recommended)

Run the dummy data generator to populate the database with sample data:

```bash
python generate_dummy_data.py
```

This will create approximately 210 records including:
- 5 demo user accounts
- 10 categories
- 30 suppliers
- 40 customers
- 60 products
- 35 purchase orders
- 45 sales orders

## Step 4: Run the Application

```bash
streamlit run main.py
```

## Demo Login Credentials

Once you've generated the dummy data, you can login with:

**Admin Accounts:**
- Username: `admin` | Password: `admin123`
- Username: `manager` | Password: `manager123`

**Staff Accounts:**
- Username: `staff1` | Password: `staff123`
- Username: `staff2` | Password: `staff123`
- Username: `demo` | Password: `demo123`

## Troubleshooting

### Database Connection Issues

1. **No database server required**: SQLite uses a file-based database, no server installation needed
2. **Verify credentials**: Double-check the credentials in your `.env` file
3. **Check database exists**: The application will create the database automatically, but you can also create it manually:
   ```sql
   CREATE DATABASE IF NOT EXISTS warehouse_tracking;
   ```

### Password Encryption

The password in the `.env` file is stored in plain text by default. For enhanced security in production:
- Change the `ENCRYPTION_KEY` to a strong, random value
- Consider using environment-specific `.env` files (`.env.production`, `.env.development`)
- Never commit the `.env` file to version control

## Notes

- The `.env` file is automatically gitignored
- Database tables are created automatically on first run
- The dummy data script is idempotent - it won't create duplicates if run multiple times
