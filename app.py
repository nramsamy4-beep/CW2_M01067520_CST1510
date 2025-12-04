import streamlit as st

st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🔒",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("🔐 Multi-Domain Intelligence Platform")
    st.info("Please log in to access the platform.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/1_Login.py")
else:
    st.title("🏠 Welcome to the Intelligence Platform")
    
    # Role display mapping
    role_display = {
        "security_analyst": "🛡️ Security Analyst",
        "data_scientist": "📈 Data Scientist",
        "it_admin": "🖥️ IT Administrator",
        "admin": "👑 Admin"
    }
    role_name = role_display.get(st.session_state.role, st.session_state.role)
    st.success(f"Logged in as: **{st.session_state.username}** | Role: **{role_name}**")
    
    # Show only the dashboard that matches the user's role
    user_role = st.session_state.role
    
    # Admin has access to all dashboards
    if user_role == "admin":
        st.markdown("### 📊 All Dashboards (Admin Access):")
        st.info("As an **Admin**, you have full access to all domain dashboards.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🛡️ Cybersecurity")
            st.write("Analyze security incidents and threat trends")
            if st.button("Open Cybersecurity Dashboard", type="primary", use_container_width=True):
                st.switch_page("pages/2_Cybersecurity_Dashboard.py")
        
        with col2:
            st.subheader("📈 Data Science")
            st.write("Manage datasets and analyze resource usage")
            if st.button("Open Data Science Dashboard", type="primary", use_container_width=True):
                st.switch_page("pages/3_DataScience_Dashboard.py")
        
        with col3:
            st.subheader("🖥️ IT Operations")
            st.write("Monitor service desk performance")
            if st.button("Open IT Operations Dashboard", type="primary", use_container_width=True):
                st.switch_page("pages/4_IT_Operations_Dashboard.py")
    
    elif user_role == "security_analyst":
        st.markdown("### 📊 Your Dashboard:")
        st.subheader("🛡️ Cybersecurity Dashboard")
        st.write("Analyze security incidents, threat trends, and incident response bottlenecks.")
        st.info("As a **Security Analyst**, you have access to the Cybersecurity domain to monitor and manage security incidents.")
        if st.button("Open Cybersecurity Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/2_Cybersecurity_Dashboard.py")
    
    elif user_role == "data_scientist":
        st.markdown("### 📊 Your Dashboard:")
        st.subheader("📈 Data Science Dashboard")
        st.write("Manage datasets, analyze resource usage, and monitor data governance.")
        st.info("As a **Data Scientist**, you have access to the Data Science domain to manage and analyze datasets.")
        if st.button("Open Data Science Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/3_DataScience_Dashboard.py")
    
    elif user_role == "it_admin":
        st.markdown("### 📊 Your Dashboard:")
        st.subheader("🖥️ IT Operations Dashboard")
        st.write("Monitor service desk performance, track tickets, and identify bottlenecks.")
        st.info("As an **IT Administrator**, you have access to the IT Operations domain to manage support tickets.")
        if st.button("Open IT Operations Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/4_IT_Operations_Dashboard.py")
    
    else:
        st.warning("⚠️ Your role does not have access to any dashboard. Please contact an administrator.")
    
    st.divider()
    
    if st.button("🚪 Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()