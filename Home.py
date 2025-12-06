import streamlit as st

# Page configuration 
st.set_page_config(
    page_title="My App",
    layout="wide"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "username" not in st.session_state:
    st.session_state.username = ""
    
if "role" not in st.session_state:
    st.session_state.role = ""
    
if "users" not in st.session_state:
    # For demo only - in real app use database
    st.session_state.users = {}

st.title("🔐 Multi-Domain Intelligence Platform")


tab_login, tab_register = st.tabs(["Login", "Register"])

with tab_login:
    st.header("Login")
    
    # Login form
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        # Simple validation
        if login_username in st.session_state.users and \
           st.session_state.users[login_username] == login_password:
            
            # Set session state (Page 11 in PDF)
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.role = "user"  # Default role
            
            # Navigate to dashboard 
            st.success("Login successful!")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Invalid credentials")

with tab_register:
    st.header("Register")
    
    # Registration form 
    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Choose a password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    
    # Create account button 
    if st.button("Create account"):
        # Three-step validation 
        # 1. Empty field check
        if not new_username or not new_password:
            st.warning("Please fill in all fields")
        # 2. Password match
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        # 3. Uniqueness check
        elif new_username in st.session_state.users:
            st.error("Username already exists")
        else:
            # Store user 
            st.session_state.users[new_username] = new_password
            st.success("Account created! ✅")
            st.info("Go to login tab to sign in")

st.markdown("---")
st.warning("⚠️ **SECURITY NOTE:** This implementation stores passwords in plain text for learning purposes only. For real applications, use bcrypt for password hashing and store hashed passwords in a database.")