import streamlit as st
import bcrypt
from database import DatabaseManager

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def login(self, username, password):
        """Authenticate user login"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            user = self.db.execute_query(query, (username,))
            
            if user and len(user) > 0:
                user = user[0]
                if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                    # Store user info in session state
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user['id']
                    st.session_state['username'] = user['username']
                    st.session_state['role'] = user['role']
                    return True
            return False
        except Exception as e:
            st.error(f"Login error: {e}")
            return False
    
    def logout(self):
        """Logout user and clear session"""
        for key in ['authenticated', 'user_id', 'username', 'role']:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def require_auth(self):
        """Require authentication for protected pages"""
        if not self.is_authenticated():
            st.error("Please login to access this page.")
            st.stop()
    
    def require_admin(self):
        """Require admin role for admin-only pages"""
        self.require_auth()
        if st.session_state.get('role') != 'admin':
            st.error("Admin access required.")
            st.stop()
    
    def create_user(self, username, password, role):
        """Create new user (admin only)"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
            return self.db.execute_update(query, (username, password_hash.decode('utf-8'), role))
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return False
    
    def change_password(self, user_id, new_password):
        """Change user password"""
        try:
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            query = "UPDATE users SET password_hash = %s WHERE id = %s"
            return self.db.execute_update(query, (password_hash.decode('utf-8'), user_id))
        except Exception as e:
            st.error(f"Error changing password: {e}")
            return False
