import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px

# Add parent directory to import path
sys.path.append(str(Path(__file__).parent.parent))

from app.data.tickets import get_all_tickets, insert_ticket, update_ticket_status, delete_ticket
from app.services.gemini_service import query_itoperations_assistant, API_KEY_ITOPERATIONS, list_available_models, get_api_key
import os

st.set_page_config(
    page_title="IT Operations Dashboard",
    page_icon="🖥️",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.error("🚫 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("pages/1_Login.py")
    st.stop()

# Check role-based access - Only it_admin or admin can access this dashboard
if st.session_state.role not in ["it_admin", "admin"]:
    st.error("🚫 Access Denied: This dashboard is only accessible to IT Administrators.")
    st.warning(f"Your current role: **{st.session_state.role}**")
    st.info("Please return to the home page to access your authorized dashboard.")
    if st.button("🏠 Go to Home"):
        st.switch_page("app.py")
    st.stop()

# Header
st.title("🖥️ IT Operations Dashboard")
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
    
    df_all = get_all_tickets()
    
    if not df_all.empty:
        priorities = ["All"] + sorted(df_all['priority'].unique().tolist())
        statuses = ["All"] + sorted(df_all['status'].unique().tolist())
        staff = ["All"] + sorted(df_all['assigned_to'].unique().tolist())
        
        selected_priority = st.selectbox("Priority", priorities)
        selected_status = st.selectbox("Status", statuses)
        selected_staff = st.selectbox("Assigned To", staff)
    else:
        selected_priority = "All"
        selected_status = "All"
        selected_staff = "All"
    
    st.divider()
    st.subheader("🤖 AI Settings")
    
    # API Key input (secure - from secrets or manual entry)
    api_key = get_api_key("itoperations")
    if not api_key:
        st.info("🔑 **API Key Required**\n\nTo use the AI assistant, please:\n1. Enter your key below, OR\n2. Create a `.env` file (see README)")
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get your FREE key from https://makersuite.google.com/app/apikey",
            placeholder="Enter your Gemini API key here...",
            key="it_api_key_input"
        )
        if api_key:
            st.success("✅ API Key entered (session only)")
    else:
        st.success("✅ API Key loaded from configuration")
    
    # Model selection (gemini-2.5-flash is the default)
    selected_model = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        index=0,
        help="Select the Gemini model. gemini-2.5-flash is the latest version.",
        key="it_model_select"
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Higher values = more creative, Lower = more focused",
        key="it_temperature"
    )
    
    # Message count
    msg_count = len([m for m in st.session_state.get("it_chat_history", []) if m["role"] == "user"])
    st.metric("💬 Messages", msg_count)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True, key="clear_it_chat_sidebar"):
        st.session_state.it_chat_history = []
        st.rerun()

# =============================================
# ADD NEW TICKET - PROMINENT SECTION AT TOP
# =============================================
st.divider()

with st.expander("➕ **Create New Support Ticket**", expanded=False):
    st.markdown("### 🎫 New Support Ticket")
    
    with st.form("add_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_ticket_id = st.text_input("🔖 Ticket ID", value=f"TKT{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}")
            new_priority = st.selectbox("⚠️ Priority", ["Low", "Medium", "High", "Critical"])
            new_status = st.selectbox("📊 Status", ["Open", "In Progress", "Waiting for User", "Resolved"])
            new_category = st.selectbox("🏷️ Category", ["Hardware", "Software", "Network", "Support"])
        
        with col2:
            new_subject = st.text_input("📋 Subject")
            new_assigned = st.text_input("👤 Assigned To", value="IT_Support_A")
            new_date = st.date_input("📅 Created Date")
        
        new_description = st.text_area("📝 Description", height=100)
        
        submit_ticket = st.form_submit_button("🚀 Submit Ticket", type="primary", use_container_width=True)
        
        if submit_ticket:
            if new_ticket_id and new_subject and new_description:
                ticket_id = insert_ticket(
                    new_ticket_id,
                    new_priority,
                    new_status,
                    new_category,
                    new_subject,
                    new_description,
                    new_assigned,
                    str(new_date)
                )
                st.success(f"✅ Ticket {new_ticket_id} added!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill all required fields")

# Main Content
st.divider()

# Fetch and filter tickets
df = get_all_tickets()

if df.empty:
    st.warning("⚠️ No ticket data available. Add tickets using the sidebar.")
    st.stop()

# Apply filters
if selected_priority != "All":
    df = df[df['priority'] == selected_priority]
if selected_status != "All":
    df = df[df['status'] == selected_status]
if selected_staff != "All":
    df = df[df['assigned_to'] == selected_staff]

# Key Metrics
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_tickets = len(df)
    st.metric("Total Tickets", total_tickets)

with col2:
    open_tickets = len(df[df['status'].isin(['Open', 'In Progress'])])
    st.metric("Open/In Progress", open_tickets)

with col3:
    critical_high = len(df[df['priority'].isin(['Critical', 'High'])])
    st.metric("Critical/High Priority", critical_high)

with col4:
    waiting = len(df[df['status'] == 'Waiting for User'])
    st.metric("Waiting for User", waiting)

st.divider()

# Visualizations
st.subheader("📈 Ticket Analysis")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Tickets by Priority")
    priority_counts = df['priority'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    fig_priority = px.bar(
        priority_counts,
        x='Priority',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        title='Ticket Distribution by Priority'
    )
    fig_priority.update_layout(showlegend=False)
    st.plotly_chart(fig_priority, use_container_width=True)

with col_right:
    st.markdown("#### Tickets by Status")
    status_counts = df['status'].value_counts()
    
    fig_status = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title='Tickets by Status',
        color_discrete_sequence=px.colors.sequential.Blues
    )
    st.plotly_chart(fig_status, use_container_width=True)

st.divider()

# Staff Performance Analysis
st.subheader("👥 Staff Performance")

staff_counts = df.groupby('assigned_to').agg({
    'ticket_id': 'count',
    'status': lambda x: (x == 'Resolved').sum()
}).reset_index()
staff_counts.columns = ['Staff', 'Total Tickets', 'Resolved Tickets']
staff_counts['Resolution Rate %'] = (staff_counts['Resolved Tickets'] / staff_counts['Total Tickets'] * 100).round(2)

fig_staff = px.bar(
    staff_counts,
    x='Staff',
    y=['Total Tickets', 'Resolved Tickets'],
    title='Staff Performance: Total vs Resolved Tickets',
    barmode='group',
    color_discrete_sequence=['#636EFA', '#00CC96']
)
st.plotly_chart(fig_staff, use_container_width=True)

st.divider()

# Ticket Table
st.subheader("📋 Ticket Records")

st.dataframe(
    df[['ticket_id', 'priority', 'status', 'category', 'subject', 'assigned_to', 'created_date']],
    use_container_width=True,
    hide_index=True
)

# Update/Delete Operations
st.markdown("#### ✏️ Update or Delete Ticket")

col_update, col_delete = st.columns(2)

with col_update:
    with st.form("update_form"):
        st.markdown("**Update Ticket Status**")
        update_ticket_id = st.text_input("Ticket ID", key="update_id")
        update_status = st.selectbox("New Status", ["Open", "In Progress", "Waiting for User", "Resolved"], key="update_status")
        
        submit_update = st.form_submit_button("Update Status")
        
        if submit_update:
            rows_affected = update_ticket_status(update_ticket_id, update_status)
            
            if rows_affected > 0:
                st.success(f"✅ Ticket {update_ticket_id} updated!")
                st.rerun()
            else:
                st.error(f"❌ Ticket {update_ticket_id} not found")

with col_delete:
    with st.form("delete_form"):
        st.markdown("**Delete Ticket**")
        delete_ticket_id = st.text_input("Ticket ID", key="delete_id")
        
        submit_delete = st.form_submit_button("Delete", type="secondary")
        
        if submit_delete:
            rows_affected = delete_ticket(delete_ticket_id)
            
            if rows_affected > 0:
                st.success(f"✅ Ticket {delete_ticket_id} deleted!")
                st.rerun()
            else:
                st.error(f"❌ Ticket {delete_ticket_id} not found")

# =============================================
# HIGH-VALUE INSIGHTS SECTION (Required for Top Grades)
# =============================================
st.divider()
st.subheader("🎯 High-Value Performance Insights")
st.caption("Addressing the core problem: Service Desk Performance & Staff Bottlenecks")

# Get full dataset for analysis
df_analysis = get_all_tickets()

if not df_analysis.empty:
    insight_col1, insight_col2 = st.columns(2)
    
    with insight_col1:
        # INSIGHT 1: Staff Performance Anomaly Detection
        st.markdown("#### 👤 Staff Performance Analysis")
        
        # Find worst performer
        worst_performer = staff_counts.loc[staff_counts['Resolution Rate %'].idxmin()]
        best_performer = staff_counts.loc[staff_counts['Resolution Rate %'].idxmax()]
        avg_resolution_rate = staff_counts['Resolution Rate %'].mean()
        
        # Performance anomaly detection
        if worst_performer['Resolution Rate %'] < (avg_resolution_rate - 20):
            st.error(f"🚨 **Performance Anomaly Detected!**")
        elif worst_performer['Resolution Rate %'] < (avg_resolution_rate - 10):
            st.warning(f"⚠️ **Below Average Performance**")
        else:
            st.success(f"✅ Team performance balanced")
        
        st.metric(
            f"Lowest: {worst_performer['Staff']}", 
            f"{worst_performer['Resolution Rate %']:.1f}%",
            f"{worst_performer['Resolution Rate %'] - avg_resolution_rate:.1f}% vs avg"
        )
        
        st.info(f"📊 Team Average: **{avg_resolution_rate:.1f}%** | Best: **{best_performer['Staff']}** ({best_performer['Resolution Rate %']:.1f}%)")
    
    with insight_col2:
        # INSIGHT 2: Process Bottleneck - Waiting for User
        st.markdown("#### ⏱️ Process Bottleneck Analysis")
        
        waiting_tickets = len(df_analysis[df_analysis['status'] == 'Waiting for User'])
        total_open = len(df_analysis[df_analysis['status'].isin(['Open', 'In Progress', 'Waiting for User'])])
        waiting_percentage = (waiting_tickets / total_open * 100) if total_open > 0 else 0
        
        if waiting_percentage > 30:
            st.error(f"🚨 **Critical Process Bottleneck!**")
        elif waiting_percentage > 20:
            st.warning(f"⚠️ **Significant Delays**")
        else:
            st.success(f"✅ Process flow healthy")
        
        st.metric(
            "Waiting for User", 
            f"{waiting_tickets} tickets",
            f"{waiting_percentage:.1f}% of open tickets"
        )
        
        # Priority breakdown of waiting tickets
        if waiting_tickets > 0:
            waiting_df = df_analysis[df_analysis['status'] == 'Waiting for User']
            critical_waiting = len(waiting_df[waiting_df['priority'].isin(['Critical', 'High'])])
            if critical_waiting > 0:
                st.error(f"🔴 **{critical_waiting} critical/high priority tickets stuck waiting!**")
    
    st.divider()
    
    # Detailed Performance Table
    st.markdown("#### 📊 Staff Performance Summary")
    
    # Add performance status
    staff_counts['Status'] = staff_counts['Resolution Rate %'].apply(
        lambda x: '🔴 Needs Attention' if x < avg_resolution_rate - 15 
        else ('🟡 Below Average' if x < avg_resolution_rate 
        else '🟢 Good')
    )
    
    st.dataframe(
        staff_counts[['Staff', 'Total Tickets', 'Resolved Tickets', 'Resolution Rate %', 'Status']],
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # ACTIONABLE RECOMMENDATIONS
    st.markdown("#### 📋 Actionable Recommendations")
    
    recommendations = []
    
    # Staff performance recommendations
    if worst_performer['Resolution Rate %'] < (avg_resolution_rate - 15):
        recommendations.append(f"🚨 **URGENT:** Provide immediate support/training to **{worst_performer['Staff']}**")
        recommendations.append(f"👥 Consider redistributing {worst_performer['Staff']}'s workload temporarily")
    
    # Waiting for User recommendations
    if waiting_percentage > 20:
        recommendations.append(f"⏰ Implement automated reminders for 'Waiting for User' tickets after 24 hours")
        recommendations.append(f"📧 Set up escalation process for tickets waiting >3 days")
    
    # Workload distribution
    max_workload = staff_counts['Total Tickets'].max()
    min_workload = staff_counts['Total Tickets'].min()
    if max_workload > min_workload * 2:
        overloaded = staff_counts.loc[staff_counts['Total Tickets'].idxmax(), 'Staff']
        recommendations.append(f"⚖️ Rebalance workload - **{overloaded}** has significantly more tickets")
    
    # Critical ticket recommendations
    critical_open = len(df_analysis[(df_analysis['status'].isin(['Open', 'In Progress'])) & 
                                     (df_analysis['priority'].isin(['Critical', 'High']))])
    if critical_open > 3:
        recommendations.append(f"🔴 **{critical_open} critical/high priority tickets open** - prioritize immediately")
    
    if not recommendations:
        recommendations.append("✅ Service desk performing well - maintain current processes")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")

# =============================================
# AI ASSISTANT SECTION (Week 10 Lab Style with Streaming)
# =============================================
st.divider()
st.subheader("🤖 IT Operations AI Assistant")
st.caption("Ask questions about IT tickets and service desk performance. Powered by Google Gemini.")

# Initialize chat history in session state
if "it_chat_history" not in st.session_state:
    st.session_state.it_chat_history = []

# Display chat history
for message in st.session_state.it_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input (at bottom of page)
user_question = st.chat_input("Ask about IT tickets and service desk...")

if user_question:
    if not api_key:
        st.error("⚠️ **API Key Required**")
        st.info("""
        **To use the AI assistant:**
        1. Enter your Gemini API key in the **AI Settings** section (sidebar)
        2. Or create a `.env` file with `GEMINI_API_KEY=your_key_here`
        
        **Get a FREE API key:** https://makersuite.google.com/app/apikey
        """)
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Add to history
        st.session_state.it_chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Get fresh data for context
        tickets_data = get_all_tickets()
        
        # Display streaming response (Week 10 Lab style)
        with st.chat_message("assistant"):
            container = st.empty()
            full_reply = ""
            
            # Stream the response
            try:
                from app.services.gemini_service import query_gemini_streaming, SYSTEM_PROMPTS, dataframe_to_context
                
                data_context = dataframe_to_context(tickets_data)
                
                for chunk in query_gemini_streaming(
                    question=user_question,
                    system_prompt=SYSTEM_PROMPTS["itoperations"],
                    data_context=data_context,
                    api_key=api_key,
                    model_name=selected_model,
                    temperature=temperature
                ):
                    full_reply += chunk
                    container.markdown(full_reply + "▌")  # Cursor effect
                
                # Remove cursor and show final
                container.markdown(full_reply)
                
            except Exception as e:
                error_msg = str(e)
                if "API_KEY" in error_msg or "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                    full_reply = f"""⚠️ **API Key Error**

**Issue:** {error_msg}

**Solution:**
1. Check that your API key is correct
2. Verify the key is active at https://makersuite.google.com/app/apikey
3. Try entering the key again in the sidebar

**Note:** API keys are session-only and not saved."""
                else:
                    full_reply = f"❌ **Error:** {error_msg}\n\nPlease try again or check your connection."
                container.markdown(full_reply)
        
        # Save to history
        st.session_state.it_chat_history.append({
            "role": "assistant",
            "content": full_reply
        })