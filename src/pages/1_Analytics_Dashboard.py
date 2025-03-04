import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import datetime
from datetime import timedelta

# This MUST be the first Streamlit command - nothing can come before this
st.set_page_config(
    page_title="SchoolBot Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Debug info and other commands can go after set_page_config
st.sidebar.info("Using JSON-based analytics_dashboard.py file")

# Custom CSS
st.markdown("""
    <style>
    .header-font {
        font-size:28px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Password Protection
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("DASHBOARD_PASSWORD", "admin"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.markdown('<p class="header-font">SchoolBot Analytics Dashboard</p>', unsafe_allow_html=True)
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.markdown('<p class="header-font">SchoolBot Analytics Dashboard</p>', unsafe_allow_html=True)
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Check if analytics data exists
data_dir = "analytics_data"
sessions_file = os.path.join(data_dir, "sessions.json")
interactions_file = os.path.join(data_dir, "interactions.json")
feedback_file = os.path.join(data_dir, "feedback.json")

# Display debugging info
st.sidebar.markdown("### Data Files")
st.sidebar.write(f"Sessions file exists: {os.path.exists(sessions_file)}")
st.sidebar.write(f"Interactions file exists: {os.path.exists(interactions_file)}")
st.sidebar.write(f"Feedback file exists: {os.path.exists(feedback_file)}")

# Initialize with empty data if files don't exist
if not os.path.exists(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    
if not os.path.exists(sessions_file):
    with open(sessions_file, 'w') as f:
        json.dump([], f)
        
if not os.path.exists(interactions_file):
    with open(interactions_file, 'w') as f:
        json.dump([], f)
        
if not os.path.exists(feedback_file):
    with open(feedback_file, 'w') as f:
        json.dump([], f)

# Load data
try:
    with open(sessions_file, 'r') as f:
        sessions = json.load(f)
    with open(interactions_file, 'r') as f:
        interactions = json.load(f)
    with open(feedback_file, 'r') as f:
        feedback = json.load(f)
except Exception as e:
    st.error(f"Error loading data: {e}")
    sessions = []
    interactions = []
    feedback = []

# Convert to pandas DataFrames
try:
    sessions_df = pd.DataFrame(sessions)
    interactions_df = pd.DataFrame(interactions)
    feedback_df = pd.DataFrame(feedback)
except Exception as e:
    st.error(f"Error converting to DataFrame: {e}")
    sessions_df = pd.DataFrame()
    interactions_df = pd.DataFrame()
    feedback_df = pd.DataFrame()

# Dashboard
st.markdown('<p class="header-font">SchoolBot Analytics Dashboard</p>', unsafe_allow_html=True)

# Date range filter
st.sidebar.header("Filters")

# Get the min and max dates from the sessions data
if not sessions_df.empty and 'start_time' in sessions_df.columns:
    sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time'])
    min_date = sessions_df['start_time'].min().date()
    max_date = sessions_df['start_time'].max().date()
else:
    min_date = datetime.datetime.now().date() - timedelta(days=30)
    max_date = datetime.datetime.now().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

if start_date > end_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

# Filter data by date
if not sessions_df.empty and 'start_time' in sessions_df.columns:
    sessions_df['start_time'] = pd.to_datetime(sessions_df['start_time'])
    filtered_sessions = sessions_df[
        (sessions_df['start_time'].dt.date >= start_date) & 
        (sessions_df['start_time'].dt.date <= end_date)
    ]
else:
    filtered_sessions = pd.DataFrame()

if not interactions_df.empty and 'timestamp' in interactions_df.columns:
    interactions_df['timestamp'] = pd.to_datetime(interactions_df['timestamp'])
    filtered_interactions = interactions_df[
        (interactions_df['timestamp'].dt.date >= start_date) & 
        (interactions_df['timestamp'].dt.date <= end_date)
    ]
else:
    filtered_interactions = pd.DataFrame()

# Top metrics
st.markdown("## 📈 Key Metrics")

metrics_container = st.container()
with metrics_container:
    col1, col2, col3, col4 = st.columns(4)
    
    # Total users
    if not filtered_sessions.empty and 'user_id' in filtered_sessions.columns:
        unique_users = filtered_sessions['user_id'].nunique()
    else:
        unique_users = 0
        
    col1.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{unique_users}</div>
            <div class="metric-label">Unique Users</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Total sessions
    if not filtered_sessions.empty:
        total_sessions = len(filtered_sessions)
    else:
        total_sessions = 0
        
    col2.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{total_sessions}</div>
            <div class="metric-label">Total Sessions</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Total interactions
    if not filtered_interactions.empty:
        total_interactions = len(filtered_interactions)
    else:
        total_interactions = 0
        
    col3.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{total_interactions}</div>
            <div class="metric-label">Total Interactions</div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Avg. session duration
    if not filtered_sessions.empty and 'duration_seconds' in filtered_sessions.columns:
        avg_duration = filtered_sessions['duration_seconds'].mean() / 60  # Convert to minutes
    else:
        avg_duration = 0
        
    col4.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{avg_duration:.1f}</div>
            <div class="metric-label">Avg. Session (mins)</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Query Analysis
st.markdown("## 💬 Query Analysis")

query_container = st.container()
with query_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Query types distribution
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Query Types")
        
        if not filtered_interactions.empty and 'query_type' in filtered_interactions.columns:
            query_types = filtered_interactions['query_type'].value_counts().reset_index()
            query_types.columns = ['query_type', 'count']
            
            if not query_types.empty:
                fig = px.pie(query_types, values='count', names='query_type',
                           title="Query Types Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No query type data available for the selected date range")
        else:
            st.info("No query data available")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Topics
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Top Topics")
        
        if not filtered_interactions.empty and 'topics' in filtered_interactions.columns:
            # Flatten the topics list
            all_topics = []
            for topics_list in filtered_interactions['topics']:
                if topics_list:
                    all_topics.extend(topics_list)
            
            if all_topics:
                topic_counts = pd.Series(all_topics).value_counts().reset_index()
                topic_counts.columns = ['topic', 'count']
                
                fig = px.bar(topic_counts.head(10), x='topic', y='count',
                          title="Most Common Topics")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No topic data available for the selected date range")
        else:
            st.info("No topic data available")
            
        st.markdown('</div>', unsafe_allow_html=True)

# User Feedback
st.markdown("## 👍 User Feedback")

feedback_container = st.container()
with feedback_container:
    # Feedback distribution
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("Feedback Ratings")
    
    if not filtered_interactions.empty and 'feedback_score' in filtered_interactions.columns:
        # Remove None values
        feedback_data = filtered_interactions[filtered_interactions['feedback_score'].notna()]
        
        if not feedback_data.empty:
            # Create categories
            feedback_data['rating'] = feedback_data['feedback_score'].apply(
                lambda x: "👍 Positive" if x > 3 else "👎 Negative"
            )
            
            feedback_counts = feedback_data['rating'].value_counts().reset_index()
            feedback_counts.columns = ['rating', 'count']
            
            fig = px.pie(feedback_counts, values='count', names='rating',
                      title="User Feedback Distribution",
                      color_discrete_map={'👍 Positive': '#4CAF50', '👎 Negative': '#F44336'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No feedback data available for the selected date range")
    else:
        st.info("No feedback data available")
        
    st.markdown('</div>', unsafe_allow_html=True)

# Raw Data Exploration
st.markdown("## 🔬 Raw Data")

# Sessions data
st.subheader("Sessions")
if not filtered_sessions.empty:
    st.dataframe(filtered_sessions)
else:
    st.info("No session data available")

# Interactions data
st.subheader("Interactions")
if not filtered_interactions.empty:
    st.dataframe(filtered_interactions)
else:
    st.info("No interaction data available")

# Footer
st.markdown("---")
st.markdown("*SchoolBot Analytics Dashboard* 📊")
