import streamlit as st
import sys
from pathlib import Path

# Add parent directory to import path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.user_service import login_user, register_user
from app.data.users import get_user_by_username

st.set_page_config(
    page_title="Login - Intelligence Platform",
    page_icon="🔑",
    layout="centered"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# If already logged in, redirect to home
if st.session_state.logged_in:
    st.success(f"Already logged in as **{st.session_state.username}**")
    if st.button("Go to Dashboard"):
        st.switch_page("app.py")
    st.stop()

# Login Page UI
st.title("🔐 Multi-Domain Intelligence Platform")
st.subheader("Secure Login")

# Create tabs for Login and Register
tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

# ----- LOGIN TAB -----
with tab_login:
    with st.form("login_form"):
        st.markdown("### Sign In")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if submit_login:
            if not login_username or not login_password:
                st.error("❌ Please enter both username and password")
            else:
                # Use your Week 8 login function
                success, message = login_user(login_username, login_password)
                
                if success:
                    # Get user info from database
                    user = get_user_by_username(login_username)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user[1]  # username column
                        st.session_state.role = user[3]      # role column
                        
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("Redirecting to your dashboard...")
                        
                        # Redirect based on role
                        role = user[3]
                        if role == "security_analyst":
                            st.switch_page("pages/2_Cybersecurity_Dashboard.py")
                        elif role == "data_scientist":
                            st.switch_page("pages/3_DataScience_Dashboard.py")
                        elif role == "it_admin":
                            st.switch_page("pages/4_IT_Operations_Dashboard.py")
                        elif role == "admin":
                            st.switch_page("app.py")  # Admin goes to home to choose dashboard
                        else:
                            st.switch_page("app.py")
                else:
                    st.error(f"❌ {message}")

# ----- REGISTER TAB -----
with tab_register:
    with st.form("register_form"):
        st.markdown("### Create New Account")
        
        reg_username = st.text_input("Choose Username", key="reg_user")
        reg_password = st.text_input("Choose Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        reg_role = st.selectbox(
            "Select Role",
            ["security_analyst", "data_scientist", "it_admin", "admin"],
            format_func=lambda x: {
                "security_analyst": "🛡️ Security Analyst (Cybersecurity)",
                "data_scientist": "📈 Data Scientist (Data Science)",
                "it_admin": "🖥️ IT Administrator (IT Operations)",
                "admin": "👑 Admin (All Domains)"
            }.get(x, x),
            key="reg_role"
        )
        
        submit_register = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submit_register:
            # Validation
            if not reg_username or not reg_password:
                st.error("❌ Please fill in all fields")
            elif len(reg_password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            elif reg_password != reg_confirm:
                st.error("❌ Passwords do not match")
            else:
                # Use your Week 8 register function
                success, message = register_user(reg_username, reg_password, reg_role)
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("👈 Please go to the Login tab to sign in")
                else:
                    st.error(f"❌ {message}")

st.divider()
st.caption("🔒 All passwords are securely hashed using bcrypt")