import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Add parent directory to import path
sys.path.append(str(Path(__file__).parent.parent))

from app.data.datasets import get_all_datasets, insert_dataset, update_dataset_status, delete_dataset
from app.services.gemini_service import query_datascience_assistant, API_KEY_DATASCIENCE, list_available_models
import os

st.set_page_config(
    page_title="Data Science Dashboard",
    page_icon="📈",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("🚫 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# Check role-based access - Only data_scientist or admin can access this dashboard
if st.session_state.role not in ["data_scientist", "admin"]:
    st.error("🚫 Access Denied: This dashboard is only accessible to Data Scientists.")
    st.warning(f"Your current role: **{st.session_state.role}**")
    st.info("Please return to the home page to access your authorized dashboard.")
    if st.button("🏠 Go to Home"):
        st.switch_page("app.py")
    st.stop()

# Header
st.title("📈 Data Science Dashboard")
st.markdown(f"**Logged in as:** {st.session_state.username} | **Role:** {st.session_state.role}")

# Sidebar
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
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
    
    df_all = get_all_datasets()
    
    if not df_all.empty:
        categories = ["All"] + sorted(df_all['category'].unique().tolist())
        sources = ["All"] + sorted(df_all['source'].unique().tolist())
        
        selected_category = st.selectbox("Category", categories)
        selected_source = st.selectbox("Source", sources)
    else:
        selected_category = "All"
        selected_source = "All"

# =============================================
# ADD NEW DATASET - PROMINENT SECTION AT TOP
# =============================================
st.divider()

with st.expander("➕ **Register New Dataset**", expanded=False):
    st.markdown("### 📊 New Dataset Registration")
    
    with st.form("add_dataset_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("📁 Dataset Name")
            new_category = st.selectbox("🏷️ Category", ["General", "Threat Intelligence", "Network Logs", "Customer Data"])
            new_source = st.text_input("👤 Source/Uploaded By")
        
        with col2:
            new_date = st.date_input("📅 Last Updated")
            new_records = st.number_input("🔢 Record Count", min_value=1, value=1000)
            new_size = st.number_input("💾 File Size (MB)", min_value=0.1, value=1.0, step=0.1)
        
        submit_dataset = st.form_submit_button("🚀 Register Dataset", type="primary", use_container_width=True)
        
        if submit_dataset:
            if new_name and new_source:
                dataset_id = insert_dataset(
                    new_name,
                    new_category,
                    new_source,
                    str(new_date),
                    new_records,
                    new_size
                )
                st.success(f"✅ Dataset #{dataset_id} added!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill all required fields")

# Main Content
st.divider()

# Fetch and filter datasets
df = get_all_datasets()

if df.empty:
    st.warning("⚠️ No dataset data available. Add datasets using the sidebar.")
    st.stop()

# Apply filters
if selected_category != "All":
    df = df[df['category'] == selected_category]
if selected_source != "All":
    df = df[df['source'] == selected_source]

# Key Metrics
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_datasets = len(df)
    st.metric("Total Datasets", total_datasets)

with col2:
    total_records = df['record_count'].sum()
    st.metric("Total Records", f"{total_records:,}")

with col3:
    total_size = df['file_size_mb'].sum()
    st.metric("Total Size (MB)", f"{total_size:.2f}")

with col4:
    avg_size = df['file_size_mb'].mean()
    st.metric("Avg Size (MB)", f"{avg_size:.2f}")

st.divider()

# Visualizations
st.subheader("📈 Dataset Analysis")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Datasets by Category")
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig_category = px.bar(
        category_counts,
        x='Category',
        y='Count',
        color='Count',
        color_continuous_scale='Blues',
        title='Dataset Distribution by Category'
    )
    fig_category.update_layout(showlegend=False)
    st.plotly_chart(fig_category, use_container_width=True)

with col_right:
    st.markdown("#### Resource Consumption by Source")
    source_size = df.groupby('source')['file_size_mb'].sum().reset_index()
    source_size.columns = ['Source', 'Total Size (MB)']
    
    fig_source = px.pie(
        source_size,
        values='Total Size (MB)',
        names='Source',
        title='Storage Usage by Source',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig_source, use_container_width=True)

st.divider()

# Record Count Analysis
st.subheader("📊 Record Count Distribution")

fig_records = px.bar(
    df,
    x='dataset_name',
    y='record_count',
    color='record_count',
    color_continuous_scale='Viridis',
    title='Records per Dataset'
)
st.plotly_chart(fig_records, use_container_width=True)

st.divider()

# Dataset Table
st.subheader("📋 Dataset Catalog")

st.dataframe(
    df[['id', 'dataset_name', 'category', 'source', 'record_count', 'file_size_mb', 'last_updated']],
    use_container_width=True,
    hide_index=True
)

# Update/Delete Operations
st.markdown("#### ✏️ Update or Delete Dataset")

col_update, col_delete = st.columns(2)

with col_update:
    with st.form("update_form"):
        st.markdown("**Update Dataset Category**")
        update_id = st.number_input("Dataset ID", min_value=1, step=1, key="update_id")
        update_category = st.selectbox("New Category", ["General", "Threat Intelligence", "Network Logs", "Customer Data"], key="update_cat")
        
        submit_update = st.form_submit_button("Update Category")
        
        if submit_update:
            rows_affected = update_dataset_status(update_id, update_category)
            
            if rows_affected > 0:
                st.success(f"✅ Dataset #{update_id} updated!")
                st.rerun()
            else:
                st.error(f"❌ Dataset #{update_id} not found")

with col_delete:
    with st.form("delete_form"):
        st.markdown("**Delete Dataset**")
        delete_id = st.number_input("Dataset ID", min_value=1, step=1, key="delete_id")
        
        submit_delete = st.form_submit_button("Delete", type="secondary")
        
        if submit_delete:
            rows_affected = delete_dataset(delete_id)
            
            if rows_affected > 0:
                st.success(f"✅ Dataset #{delete_id} deleted!")
                st.rerun()
            else:
                st.error(f"❌ Dataset #{delete_id} not found")

# =============================================
# HIGH-VALUE INSIGHTS SECTION (Required for Top Grades)
# =============================================
st.divider()
st.subheader("🎯 High-Value Data Governance Insights")
st.caption("Addressing the core problem: Data Governance & Resource Management")

# Get full dataset for analysis
df_analysis = get_all_datasets()

if not df_analysis.empty:
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # INSIGHT 1: Resource Consumption Analysis
        st.markdown("#### 💾 Storage Consumption Analysis")
        
        # Top consumer
        source_storage = df_analysis.groupby('source')['file_size_mb'].sum().sort_values(ascending=False)
        total_storage = df_analysis['file_size_mb'].sum()
        
        if len(source_storage) > 0:
            top_source = source_storage.index[0]
            top_size = source_storage.iloc[0]
            top_percentage = (top_size / total_storage * 100) if total_storage > 0 else 0
            
            if top_percentage > 50:
                st.error(f"🚨 **Storage Imbalance Detected!**")
            elif top_percentage > 30:
                st.warning(f"⚠️ **High Concentration Risk**")
            else:
                st.success(f"✅ Storage well distributed")
            
            st.metric(f"Top Consumer: {top_source}", f"{top_size:.2f} MB", f"{top_percentage:.1f}% of total")
            st.info(f"📊 Total Storage: **{total_storage:.2f} MB** across **{len(df_analysis)}** datasets")
    
    with insight_col2:
        # INSIGHT 2: Data Source Dependency Analysis
        st.markdown("#### 🔗 Source Dependency Analysis")
        
        source_counts = df_analysis['source'].value_counts()
        total_datasets = len(df_analysis)
        
        if len(source_counts) > 0:
            primary_source = source_counts.index[0]
            primary_count = source_counts.iloc[0]
            dependency_ratio = (primary_count / total_datasets * 100) if total_datasets > 0 else 0
            
            if dependency_ratio > 60:
                st.error(f"🚨 **High Dependency Risk!**")
                st.metric(f"Primary Source: {primary_source}", f"{primary_count} datasets", f"{dependency_ratio:.1f}% dependency")
            elif dependency_ratio > 40:
                st.warning(f"⚠️ **Moderate Dependency**")
                st.metric(f"Primary Source: {primary_source}", f"{primary_count} datasets", f"{dependency_ratio:.1f}% dependency")
            else:
                st.success(f"✅ Healthy source diversity")
                st.metric(f"Sources", f"{len(source_counts)} different sources")
            
            # Record count analysis
            total_records = df_analysis['record_count'].sum()
            avg_records = df_analysis['record_count'].mean()
            st.info(f"📋 Total Records: **{total_records:,}** | Avg per dataset: **{avg_records:,.0f}**")
    
    st.divider()
    
    # ACTIONABLE RECOMMENDATIONS
    st.markdown("#### 📋 Data Governance Recommendations")
    
    recommendations = []
    
    # Based on storage analysis
    if len(source_storage) > 0:
        top_source = source_storage.index[0]
        top_percentage = (source_storage.iloc[0] / total_storage * 100) if total_storage > 0 else 0
        if top_percentage > 50:
            recommendations.append(f"🚨 **URGENT:** Review datasets from **{top_source}** - consuming {top_percentage:.1f}% of storage")
            recommendations.append(f"📦 Implement archiving policy for {top_source} datasets older than 6 months")
    
    # Large dataset warnings
    large_datasets = df_analysis[df_analysis['file_size_mb'] > 50]
    if len(large_datasets) > 0:
        recommendations.append(f"💾 **{len(large_datasets)} large datasets (>50MB)** - consider compression")
    
    # High record count warnings
    high_record_datasets = df_analysis[df_analysis['record_count'] > 50000]
    if len(high_record_datasets) > 0:
        recommendations.append(f"📊 **{len(high_record_datasets)} datasets with >50K records** - review for partitioning")
    
    # Category-specific recommendations
    customer_data = df_analysis[df_analysis['category'] == 'Customer Data']
    if len(customer_data) > 0:
        recommendations.append(f"🔒 **{len(customer_data)} Customer Data datasets** - ensure GDPR compliance")
    
    if not recommendations:
        recommendations.append("✅ Data governance posture is healthy - maintain regular audits")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

# =============================================
# AI ASSISTANT SECTION
# =============================================
st.divider()
st.subheader("🤖 Data Science AI Assistant")
st.caption("Ask questions about your datasets and data governance. This AI only answers data science-related questions.")

# Initialize chat history in session state
if "ds_chat_history" not in st.session_state:
    st.session_state.ds_chat_history = []

# API Key input
with st.expander("⚙️ API Configuration", expanded=False):
    ds_api_key = st.text_input(
        "Gemini API Key for Data Science",
        type="password",
        value=os.getenv(API_KEY_DATASCIENCE, ""),
        help="Enter your Gemini API key for the Data Science domain",
        key="ds_api_key_input"
    )
    if ds_api_key:
        os.environ[API_KEY_DATASCIENCE] = ds_api_key
        st.success("✅ API Key configured")
        
        # Show available models
        if st.button("🔍 List Available Models", key="list_models_ds"):
            with st.spinner("Fetching available models..."):
                models = list_available_models(ds_api_key)
                if models:
                    st.info("**Available Models:**")
                    for m in models:
                        st.code(m)

# Chat interface
with st.container():
    # Display chat history
    for message in st.session_state.ds_chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_question = st.chat_input("Ask about datasets and data governance...", key="ds_chat_input")
    
    if user_question:
        # Check if API key is configured
        api_key = os.getenv(API_KEY_DATASCIENCE, "")
        
        if not api_key:
            st.error("⚠️ Please configure your Gemini API key in the API Configuration section above.")
        else:
            # Add user message to history
            st.session_state.ds_chat_history.append({"role": "user", "content": user_question})
            st.chat_message("user").write(user_question)
            
            # Get AI response
            with st.spinner("🔍 Analyzing dataset information..."):
                # Get fresh data for context
                datasets_data = get_all_datasets()
                response = query_datascience_assistant(user_question, datasets_data, api_key)
            
            # Add response to history
            st.session_state.ds_chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

# Clear chat button
if st.session_state.ds_chat_history:
    if st.button("🗑️ Clear Chat History", key="clear_ds_chat"):
        st.session_state.ds_chat_history = []
        st.rerun()