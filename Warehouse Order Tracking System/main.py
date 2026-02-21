import streamlit as st
from streamlit_option_menu import option_menu
from config import APP_TITLE, APP_ICON, PAGE_CONFIG
from auth import AuthManager
from app_pages.dashboard import show_dashboard
from app_pages.products import show_products
from app_pages.suppliers import show_suppliers
from app_pages.customers import show_customers
from app_pages.orders import show_orders
from app_pages.reports import show_reports
from app_pages.settings import show_settings

def main():
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    
    # Initialize authentication
    auth = AuthManager()
    
    # Check if user is authenticated
    if not auth.is_authenticated():
        show_login_page(auth)
    else:
        show_main_app(auth)

def show_login_page(auth):
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown("---")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    if auth.login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        # Show default credentials
        with st.expander("ℹ️ Demo Access Credentials", expanded=True):
            st.markdown("### 👤 Demo Accounts")
            st.markdown("""
            **Administrator Accounts:**
            - **Username:** `admin` | **Password:** `admin123`
            - **Username:** `manager` | **Password:** `manager123`
            
            **Staff Accounts:**
            - **Username:** `staff1` | **Password:** `staff123`
            - **Username:** `staff2` | **Password:** `staff123`
            - **Username:** `demo` | **Password:** `demo123`
            """)
            st.warning("⚠️ **Note:** These are demo credentials. Please change passwords after first login in a production environment.")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Warehouse Order Tracking System v1.0</p>
            <p>Built with Streamlit & SQLite</p>
        </div>
        """, unsafe_allow_html=True)

def show_main_app(auth):
    # Header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.title(f"{APP_ICON} {APP_TITLE}")
    
    with col2:
        st.info(f"👤 {st.session_state.get('username', 'User')}")
    
    with col3:
        if st.button("🚪 Logout", type="secondary"):
            auth.logout()
            st.rerun()
    
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        
        # Navigation menu
        selected = option_menu(
            menu_title=None,
            options=[
                "📊 Dashboard",
                "📦 Products", 
                "🏭 Suppliers",
                "👥 Customers",
                "📋 Orders",
                "📊 Reports",
                "⚙️ Settings"
            ],
            icons=[
                "speedometer2",
                "box-seam",
                "building",
                "people",
                "clipboard-data",
                "graph-up",
                "gear"
            ],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )
    
    # Main content area
    if selected == "📊 Dashboard":
        show_dashboard()
    elif selected == "📦 Products":
        show_products()
    elif selected == "🏭 Suppliers":
        show_suppliers()
    elif selected == "👥 Customers":
        show_customers()
    elif selected == "📋 Orders":
        show_orders()
    elif selected == "📊 Reports":
        show_reports()
    elif selected == "⚙️ Settings":
        show_settings()

if __name__ == "__main__":
    main()
