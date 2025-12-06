# home page - login and registration
import streamlit as st
from app.services.user_service import login_user, register_user
from app.data.users import get_user_by_username

# page config must be first
st.set_page_config(page_title="Intelligence Platform", layout="centered")

# initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# redirect if already logged in
if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py")

# page header
st.title("Intelligence Platform")
st.write("Welcome! Please login or create an account")
st.divider()

# create tabs
tab_login, tab_register = st.tabs(["Login", "Register"])

# login tab
with tab_login:
    st.subheader("Login")
    
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Log in"):
        if not login_username or not login_password:
            st.error("please fill in all fields")
        else:
            # authenticate user
            success, message = login_user(login_username, login_password)
            
            if success:
                # get user info
                user = get_user_by_username(login_username)
                
                # set session state
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.session_state.role = user[3]
                
                st.success(message)
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error(message)

# register tab
with tab_register:
    st.subheader("Register")
    
    new_username = st.text_input("Choose username", key="register_username")
    new_password = st.text_input("Choose password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")
    role = st.selectbox("Select role", ["user", "analyst", "admin"])
    
    if st.button("Create account"):
        # validation
        if not new_username or not new_password:
            st.warning("please fill in all fields")
        elif new_password != confirm_password:
            st.error("passwords do not match")
        else:
            # register user
            success, message = register_user(new_username, new_password, role)
            
            if success:
                st.success(message)
                st.info("go to login tab to sign in")
            else:
                st.error(message)