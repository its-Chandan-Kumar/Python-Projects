import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import base64

load_dotenv()

def get_encryption_key():
    """Get or generate encryption key"""
    key = os.getenv('ENCRYPTION_KEY', 'warehouse-tracking-system-secret-key-change-in-production')
    # Convert to 32 bytes and base64 encode for Fernet
    key_bytes = key.encode()[:32].ljust(32, b'0')
    return base64.urlsafe_b64encode(key_bytes)

def decrypt_password(encrypted_password):
    """Decrypt password from environment variable"""
    try:
        if not encrypted_password:
            return ''
        # Check if password is encrypted (Fernet tokens start with 'gAAAAAB')
        if encrypted_password.startswith('gAAAAAB'):
            f = Fernet(get_encryption_key())
            return f.decrypt(encrypted_password.encode()).decode()
        else:
            # Return plain password (for backward compatibility)
            return encrypted_password
    except Exception:
        # If decryption fails, assume it's plain text
        return encrypted_password

# Database Configuration - Using SQLite database file
DB_PATH = os.getenv('DB_PATH', 'warehouse_tracking.db')

# Application Settings
APP_TITLE = "Warehouse Order Tracking System"
APP_ICON = "📦"
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}