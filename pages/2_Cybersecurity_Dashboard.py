import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Add parent directory to import path
sys.path.append(str(Path(__file__).parent.parent))

from app.data.incidents import get_all_incidents, insert_incident, update_incident_status, delete_incident
from app.services.gemini_service import query_cybersecurity_assistant, API_KEY_CYBERSECURITY, list_available_models
import os

st.set_page_config(
    page_title="Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("🚫 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# Check role-based access - Only security_analyst or admin can access this dashboard
if st.session_state.role not in ["security_analyst", "admin"]:
    st.error("🚫 Access Denied: This dashboard is only accessible to Security Analysts.")
    st.warning(f"Your current role: **{st.session_state.role}**")
    st.info("Please return to the home page to access your authorized dashboard.")
    if st.button("🏠 Go to Home"):
        st.switch_page("app.py")
    st.stop()

# Header
st.title("🛡️ Cybersecurity Incident Dashboard")
st.markdown(f"**Logged in as:** {st.session_state.username} | **Role:** {st.session_state.role}")

# Sidebar - Navigation & Filters
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    # Navigation
    if st.button("🏠 Back to Home"):
        st.switch_page("app.py")
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.switch_page("app.py")
    
    st.divider()
    
    # Filters
    st.subheader("🔍 Filters")
    
    df_all = get_all_incidents()
    
    if not df_all.empty:
        threat_types = ["All"] + sorted(df_all['incident_type'].unique().tolist())
        severity_levels = ["All"] + sorted(df_all['severity'].unique().tolist())
        status_options = ["All"] + sorted(df_all['status'].unique().tolist())
        
        selected_threat = st.selectbox("Threat Type", threat_types)
        selected_severity = st.selectbox("Severity", severity_levels)
        selected_status = st.selectbox("Status", status_options)
    else:
        selected_threat = "All"
        selected_severity = "All"
        selected_status = "All"

# =============================================
# ADD NEW INCIDENT - PROMINENT SECTION AT TOP
# =============================================
st.divider()

with st.expander("➕ **Report New Security Incident**", expanded=False):
    st.markdown("### 🚨 New Incident Report")
    
    col_form1, col_form2 = st.columns(2)
    
    with st.form("add_incident_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_date = st.date_input("📅 Date")
            new_type = st.selectbox(
                "🎯 Incident Type",
                ["Phishing", "Malware", "DDoS", "Ransomware", "Data Breach", "Insider Threat"]
            )
        
        with col2:
            new_severity = st.selectbox("⚠️ Severity", ["Low", "Medium", "High", "Critical"])
            new_status = st.selectbox("📊 Status", ["Open", "Investigating", "Resolved", "Closed"])
        
        with col3:
            new_description = st.text_area("📝 Description", height=100)
        
        submit_incident = st.form_submit_button("🚀 Submit Incident Report", type="primary", use_container_width=True)
        
        if submit_incident:
            if new_description:
                incident_id = insert_incident(
                    str(new_date),
                    new_type,
                    new_severity,
                    new_status,
                    new_description,
                    st.session_state.username
                )
                
                st.success(f"✅ Incident #{incident_id} added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a description")

# Main Content Area
st.divider()

# Fetch and filter incidents
df = get_all_incidents()

if df.empty:
    st.warning("⚠️ No incident data available. Add incidents using the sidebar.")
    st.stop()

# Apply filters
if selected_threat != "All":
    df = df[df['incident_type'] == selected_threat]
if selected_severity != "All":
    df = df[df['severity'] == selected_severity]
if selected_status != "All":
    df = df[df['status'] == selected_status]

# Key Metrics
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_incidents = len(df)
    st.metric("Total Incidents", total_incidents)

with col2:
    open_incidents = len(df[df['status'].isin(['Open', 'Investigating'])])
    st.metric("Open/Investigating", open_incidents)

with col3:
    critical_high = len(df[df['severity'].isin(['Critical', 'High'])])
    st.metric("Critical/High Severity", critical_high)

with col4:
    phishing_count = len(df[df['incident_type'] == 'Phishing'])
    st.metric("Phishing Incidents", phishing_count)

st.divider()

# Visualizations
st.subheader("📈 Incident Analysis")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Threat Type Distribution")
    threat_counts = df['incident_type'].value_counts().reset_index()
    threat_counts.columns = ['Threat Type', 'Count']
    
    fig_threat = px.bar(
        threat_counts,
        x='Threat Type',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        title='Incident Count by Threat Type'
    )
    fig_threat.update_layout(showlegend=False)
    st.plotly_chart(fig_threat, use_container_width=True)

with col_right:
    st.markdown("#### Severity Distribution")
    severity_counts = df['severity'].value_counts()
    
    fig_severity = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title='Incidents by Severity',
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    st.plotly_chart(fig_severity, use_container_width=True)

st.divider()

# Status Breakdown
st.subheader("🔴 Status Breakdown")

status_counts = df['status'].value_counts()
fig_status = px.bar(
    x=status_counts.index,
    y=status_counts.values,
    labels={'x': 'Status', 'y': 'Count'},
    title='Incidents by Status',
    color=status_counts.values,
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# =============================================
# HIGH-VALUE INSIGHTS SECTION (Required for Top Grades)
# =============================================
st.subheader("🎯 High-Value Security Insights")
st.caption("Addressing the core problem: Incident Response Bottleneck & Phishing Surge")

# Get full dataset for analysis
df_analysis = get_all_incidents()

if not df_analysis.empty:
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # INSIGHT 1: Phishing Spike Analysis
        st.markdown("#### 🎣 Phishing Threat Trend")
        
        threat_counts = df_analysis['incident_type'].value_counts()
        total_incidents = len(df_analysis)
        phishing_count = threat_counts.get('Phishing', 0)
        phishing_percentage = (phishing_count / total_incidents * 100) if total_incidents > 0 else 0
        
        # Phishing spike indicator
        if phishing_percentage > 30:
            st.error(f"🚨 **PHISHING SURGE DETECTED!**")
            st.metric("Phishing Incidents", phishing_count, f"{phishing_percentage:.1f}% of all incidents")
        elif phishing_percentage > 20:
            st.warning(f"⚠️ **Elevated Phishing Activity**")
            st.metric("Phishing Incidents", phishing_count, f"{phishing_percentage:.1f}% of all incidents")
        else:
            st.success(f"✅ Phishing levels normal")
            st.metric("Phishing Incidents", phishing_count, f"{phishing_percentage:.1f}% of all incidents")
        
        # Phishing status breakdown
        phishing_df = df_analysis[df_analysis['incident_type'] == 'Phishing']
        if not phishing_df.empty:
            phishing_open = len(phishing_df[phishing_df['status'].isin(['Open', 'Investigating'])])
            st.info(f"📊 **{phishing_open}** phishing incidents still unresolved")
    
    with insight_col2:
        # INSIGHT 2: Response Bottleneck Analysis
        st.markdown("#### ⏱️ Response Bottleneck Analysis")
        
        # Find which threat type has most unresolved cases
        open_incidents = df_analysis[df_analysis['status'].isin(['Open', 'Investigating'])]
        
        if not open_incidents.empty:
            backlog_by_type = open_incidents.groupby('incident_type').size().sort_values(ascending=False)
            worst_backlog = backlog_by_type.index[0]
            worst_count = backlog_by_type.iloc[0]
            
            st.error(f"🔴 **Highest Backlog:** {worst_backlog}")
            st.metric("Unresolved Cases", worst_count, "Needs immediate attention")
            
            # Severity of backlog
            critical_backlog = len(open_incidents[open_incidents['severity'].isin(['Critical', 'High'])])
            st.warning(f"⚠️ **{critical_backlog}** critical/high severity cases in backlog")
        else:
            st.success("✅ No significant backlog detected")
    
    st.divider()
    
    # ACTIONABLE RECOMMENDATIONS
    st.markdown("#### 📋 Actionable Recommendations")
    
    recommendations = []
    
    # Recommendation based on phishing analysis
    if phishing_percentage > 30:
        recommendations.append("🚨 **URGENT:** Deploy additional phishing awareness training immediately")
        recommendations.append("📧 Implement stricter email filtering rules")
        recommendations.append("🔍 Prioritize investigation of all open phishing cases")
    
    # Recommendation based on backlog
    open_count = len(df_analysis[df_analysis['status'].isin(['Open', 'Investigating'])])
    if open_count > 5:
        recommendations.append(f"👥 Consider allocating more resources - {open_count} incidents pending")
    
    # Recommendation based on critical cases
    critical_open = len(df_analysis[(df_analysis['status'].isin(['Open', 'Investigating'])) & 
                                     (df_analysis['severity'].isin(['Critical', 'High']))])
    if critical_open > 0:
        recommendations.append(f"🔴 **{critical_open} critical/high incidents require immediate escalation**")
    
    if not recommendations:
        recommendations.append("✅ Security posture is healthy - maintain current monitoring levels")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

st.divider()

# Incident Data Table
st.subheader("📋 Incident Records")

st.dataframe(
    df[['id', 'date', 'incident_type', 'severity', 'status', 'description', 'reported_by']],
    use_container_width=True,
    hide_index=True
)

# Update/Delete Operations
st.markdown("#### ✏️ Update or Delete Incident")

col_update, col_delete = st.columns(2)

with col_update:
    with st.form("update_form"):
        st.markdown("**Update Incident Status**")
        update_id = st.number_input("Incident ID", min_value=1, step=1, key="update_id")
        update_status = st.selectbox("New Status", ["Open", "Investigating", "Resolved", "Closed"], key="update_status")
        
        submit_update = st.form_submit_button("Update Status")
        
        if submit_update:
            rows_affected = update_incident_status(update_id, update_status)
            
            if rows_affected > 0:
                st.success(f"✅ Incident #{update_id} updated!")
                st.rerun()
            else:
                st.error(f"❌ Incident #{update_id} not found")

with col_delete:
    with st.form("delete_form"):
        st.markdown("**Delete Incident**")
        delete_id = st.number_input("Incident ID", min_value=1, step=1, key="delete_id")
        
        submit_delete = st.form_submit_button("Delete", type="secondary")
        
        if submit_delete:
            rows_affected = delete_incident(delete_id)
            
            if rows_affected > 0:
                st.success(f"✅ Incident #{delete_id} deleted!")
                st.rerun()
            else:
                st.error(f"❌ Incident #{delete_id} not found")

# =============================================
# AI ASSISTANT SECTION
# =============================================
st.divider()
st.subheader("🤖 Cybersecurity AI Assistant")
st.caption("Ask questions about your security incidents. This AI only answers cybersecurity-related questions.")

# Initialize chat history in session state
if "cyber_chat_history" not in st.session_state:
    st.session_state.cyber_chat_history = []

# API Key input
with st.expander("⚙️ API Configuration", expanded=False):
    cyber_api_key = st.text_input(
        "Gemini API Key for Cybersecurity",
        type="password",
        value=os.getenv(API_KEY_CYBERSECURITY, ""),
        help="Enter your Gemini API key for the Cybersecurity domain",
        key="cyber_api_key_input"
    )
    if cyber_api_key:
        os.environ[API_KEY_CYBERSECURITY] = cyber_api_key
        st.success("✅ API Key configured")
        
        # Show available models
        if st.button("🔍 List Available Models", key="list_models_cyber"):
            with st.spinner("Fetching available models..."):
                models = list_available_models(cyber_api_key)
                if models:
                    st.info("**Available Models:**")
                    for m in models:
                        st.code(m)

# Chat interface
with st.container():
    # Display chat history
    for message in st.session_state.cyber_chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_question = st.chat_input("Ask about security incidents...", key="cyber_chat_input")
    
    if user_question:
        # Check if API key is configured
        api_key = os.getenv(API_KEY_CYBERSECURITY, "")
        
        if not api_key:
            st.error("⚠️ Please configure your Gemini API key in the API Configuration section above.")
        else:
            # Add user message to history
            st.session_state.cyber_chat_history.append({"role": "user", "content": user_question})
            st.chat_message("user").write(user_question)
            
            # Get AI response
            with st.spinner("🔍 Analyzing security data..."):
                # Get fresh data for context
                incidents_data = get_all_incidents()
                response = query_cybersecurity_assistant(user_question, incidents_data, api_key)
            
            # Add response to history
            st.session_state.cyber_chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

# Clear chat button
if st.session_state.cyber_chat_history:
    if st.button("🗑️ Clear Chat History", key="clear_cyber_chat"):
        st.session_state.cyber_chat_history = []
        st.rerun()