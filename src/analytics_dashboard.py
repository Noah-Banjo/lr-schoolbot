import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
import json
import os

st.set_page_config(
    page_title="LR SchoolBot Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Check if database exists
db_path = "analytics.db"
if not os.path.exists(db_path):
    st.error(f"Database file {db_path} not found. No analytics data available yet.")
    st.stop()

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

try:
    conn = get_connection()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# Dashboard
st.markdown('<p class="header-font">SchoolBot Analytics Dashboard</p>', unsafe_allow_html=True)

# Date range filter
st.sidebar.header("Filters")

# Get the min and max dates from the database
try:
    date_range_df = pd.read_sql(
        "SELECT MIN(start_time) as min_date, MAX(start_time) as max_date FROM sessions", 
        conn
    )
    min_date = datetime.strptime(date_range_df['min_date'][0][:10], '%Y-%m-%d').date() if not pd.isna(date_range_df['min_date'][0]) else datetime.now().date() - timedelta(days=30)
    max_date = datetime.strptime(date_range_df['max_date'][0][:10], '%Y-%m-%d').date() if not pd.isna(date_range_df['max_date'][0]) else datetime.now().date()
except:
    min_date = datetime.now().date() - timedelta(days=30)
    max_date = datetime.now().date()

start_date = st.sidebar.date_input("Start Date", min_date)
end_date = st.sidebar.date_input("End Date", max_date)

if start_date > end_date:
    st.sidebar.error("End date must be after start date")
    st.stop()

date_filter = f"WHERE date(start_time) BETWEEN '{start_date}' AND '{end_date}'"
interaction_date_filter = f"WHERE date(timestamp) BETWEEN '{start_date}' AND '{end_date}'"

# Top metrics
st.markdown("## 📈 Key Metrics")

metrics_container = st.container()
with metrics_container:
    col1, col2, col3, col4 = st.columns(4)
    
    # Total users
    try:
        users_df = pd.read_sql(f"SELECT COUNT(DISTINCT user_id) as count FROM sessions {date_filter}", conn)
        col1.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{users_df['count'].iloc[0]}</div>
                <div class="metric-label">Unique Users</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading users metric: {e}")
        col1.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Unique Users</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Total sessions
    try:
        sessions_df = pd.read_sql(f"SELECT COUNT(*) as count FROM sessions {date_filter}", conn)
        col2.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{sessions_df['count'].iloc[0]}</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading sessions metric: {e}")
        col2.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Total Sessions</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Total interactions
    try:
        interactions_df = pd.read_sql(f"""
            SELECT COUNT(*) as count FROM interactions 
            WHERE session_id IN (SELECT session_id FROM sessions {date_filter})
        """, conn)
        col3.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{interactions_df['count'].iloc[0]}</div>
                <div class="metric-label">Total Interactions</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading interactions metric: {e}")
        col3.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Total Interactions</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Avg. session duration
    try:
        duration_df = pd.read_sql(f"""
            SELECT AVG(duration_seconds) as avg_duration FROM sessions 
            {date_filter} AND duration_seconds IS NOT NULL
        """, conn)
        avg_duration_min = round(duration_df['avg_duration'].iloc[0] / 60, 1) if not pd.isna(duration_df['avg_duration'].iloc[0]) else 0
        col4.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{avg_duration_min}</div>
                <div class="metric-label">Avg. Session (mins)</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error loading duration metric: {e}")
        col4.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">0</div>
                <div class="metric-label">Avg. Session (mins)</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Usage trends
st.markdown("## 🔍 Usage Analysis")

usage_container = st.container()
with usage_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily sessions chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Daily Sessions")
        
        try:
            sessions_by_day = pd.read_sql(f"""
                SELECT date(start_time) as date, COUNT(*) as count 
                FROM sessions {date_filter}
                GROUP BY date(start_time) 
                ORDER BY date(start_time)
            """, conn)
            
            if not sessions_by_day.empty:
                fig = px.line(sessions_by_day, x='date', y='count', 
                            title="Sessions per Day",
                            markers=True)
                fig.update_layout(xaxis_title="Date", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No session data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading sessions chart: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Interactions per session
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("User Engagement")
        
        try:
            session_interactions = pd.read_sql(f"""
                SELECT s.session_id, COUNT(i.interaction_id) as interaction_count
                FROM sessions s
                LEFT JOIN interactions i ON s.session_id = i.session_id
                {date_filter}
                GROUP BY s.session_id
            """, conn)
            
            if not session_interactions.empty:
                fig = px.histogram(session_interactions, x='interaction_count',
                                 title="Interactions per Session",
                                 labels={'interaction_count': 'Number of Interactions'})
                fig.update_layout(xaxis_title="Interactions per Session", yaxis_title="Number of Sessions")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No interaction data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading interactions chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Query Analysis
st.markdown("## 💬 Query Analysis")

query_container = st.container()
with query_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Query types distribution
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Query Types")
        
        try:
            query_types = pd.read_sql(f"""
                SELECT query_type, COUNT(*) as count
                FROM interactions
                WHERE session_id IN (SELECT session_id FROM sessions {date_filter})
                GROUP BY query_type
                ORDER BY count DESC
            """, conn)
            
            if not query_types.empty:
                fig = px.pie(query_types, values='count', names='query_type',
                            title="Query Types Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No query type data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading query types chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Most common topics
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Top Topics")
        
        try:
            # Extract topics from interactions (stored as JSON strings)
            topics_data = pd.read_sql(f"""
                SELECT topics
                FROM interactions
                WHERE session_id IN (SELECT session_id FROM sessions {date_filter})
            """, conn)
            
            # Process topics (stored as JSON strings)
            all_topics = []
            for topic_json in topics_data['topics']:
                try:
                    if topic_json:
                        topics = json.loads(topic_json)
                        all_topics.extend(topics)
                except:
                    continue
            
            # Count topic frequencies
            if all_topics:
                topic_counts = pd.DataFrame(
                    {"topic": list(set(all_topics)), "count": [all_topics.count(t) for t in set(all_topics)]}
                ).sort_values(by="count", ascending=False).head(10)
                
                fig = px.bar(topic_counts, x='topic', y='count',
                          title="Most Common Topics",
                          color='count',
                          color_continuous_scale='Blues')
                fig.update_layout(xaxis_title="Topic", yaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No topic data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading topics chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Response Quality
st.markdown("## ✅ Response Quality")

quality_container = st.container()
with quality_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Success rate
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Response Success Rate")
        
        try:
            success_data = pd.read_sql(f"""
                SELECT 
                    CASE WHEN is_successful=1 THEN 'Successful' ELSE 'Unsuccessful' END as status,
                    COUNT(*) as count
                FROM interactions
                WHERE session_id IN (SELECT session_id FROM sessions {date_filter})
                GROUP BY is_successful
            """, conn)
            
            if not success_data.empty:
                fig = px.pie(success_data, values='count', names='status',
                           title="Response Success Rate",
                           color_discrete_map={'Successful': '#4CAF50', 'Unsuccessful': '#F44336'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No response quality data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading success rate chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Feedback scores
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("User Feedback")
        
        try:
            feedback_data = pd.read_sql(f"""
                SELECT 
                    feedback_score,
                    COUNT(*) as count
                FROM interactions
                WHERE 
                    session_id IN (SELECT session_id FROM sessions {date_filter})
                    AND feedback_score IS NOT NULL
                GROUP BY feedback_score
            """, conn)
            
            if not feedback_data.empty:
                # Map scores to labels
                feedback_data['rating'] = feedback_data['feedback_score'].apply(
                    lambda x: "👍 Positive" if x > 3 else "👎 Negative"
                )
                
                fig = px.pie(feedback_data, values='count', names='rating',
                           title="User Feedback Distribution",
                           color_discrete_map={'👍 Positive': '#4CAF50', '👎 Negative': '#F44336'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feedback data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading feedback chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Educational Impact Analysis
st.markdown("## 🎓 Educational Impact")

education_container = st.container()
with education_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Historical entities mentioned
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Historical Topics Explored")
        
        try:
            # Extract historical entities
            entities_data = pd.read_sql(f"""
                SELECT historical_entities
                FROM interactions
                WHERE session_id IN (SELECT session_id FROM sessions {date_filter})
            """, conn)
            
            # Process entities (stored as JSON strings)
            all_entities = []
            for entity_json in entities_data['historical_entities']:
                try:
                    if entity_json:
                        entities = json.loads(entity_json)
                        all_entities.extend(entities)
                except:
                    continue
            
            # Count entity frequencies
            if all_entities:
                entity_counts = pd.DataFrame(
                    {"entity": list(set(all_entities)), "count": [all_entities.count(e) for e in set(all_entities)]}
                ).sort_values(by="count", ascending=False).head(10)
                
                fig = px.bar(entity_counts, x='count', y='entity',
                          title="Most Referenced Historical Topics",
                          orientation='h',
                          color='count',
                          color_continuous_scale='Viridis')
                fig.update_layout(yaxis_title="Historical Topic", xaxis_title="Frequency")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No historical topics data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading historical topics chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Exploration depth
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Learning Progression")
        
        try:
            depth_data = pd.read_sql(f"""
                SELECT 
                    s.session_id,
                    MAX(e.exploration_depth) as max_depth
                FROM 
                    sessions s
                LEFT JOIN educational_metrics e ON s.session_id = e.session_id
                {date_filter}
                GROUP BY s.session_id
                HAVING max_depth IS NOT NULL
            """, conn)
            
            if not depth_data.empty and len(depth_data) > 0:
                # Create depth categories
                depth_data['depth_category'] = pd.cut(
                    depth_data['max_depth'],
                    bins=[0, 0.5, 1.0, 1.5, 2.0],
                    labels=['Basic', 'Intermediate', 'Advanced', 'Expert']
                )
                
                depth_counts = depth_data['depth_category'].value_counts().reset_index()
                depth_counts.columns = ['category', 'count']
                
                fig = px.pie(depth_counts, values='count', names='category',
                           title="Exploration Depth Distribution",
                           color_discrete_sequence=px.colors.sequential.Blues_r)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No exploration depth data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading exploration depth chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Device Analytics
st.markdown("## 📱 Device Analytics")

device_container = st.container()
with device_container:
    col1, col2 = st.columns(2)
    
    with col1:
        # Device types
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("Device Types")
        
        try:
            device_data = pd.read_sql(f"""
                SELECT 
                    device_type,
                    COUNT(*) as count
                FROM sessions
                {date_filter}
                GROUP BY device_type
            """, conn)
            
            if not device_data.empty:
                fig = px.pie(device_data, values='count', names='device_type',
                           title="Device Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No device data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading device chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # New vs returning users
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("User Types")
        
        try:
            user_type_data = pd.read_sql(f"""
                SELECT 
                    CASE WHEN is_return_user=1 THEN 'Returning' ELSE 'New' END as user_type,
                    COUNT(*) as count
                FROM sessions
                {date_filter}
                GROUP BY is_return_user
            """, conn)
            
            if not user_type_data.empty:
                fig = px.pie(user_type_data, values='count', names='user_type',
                           title="New vs. Returning Users",
                           color_discrete_map={'Returning': '#1E88E5', 'New': '#FFC107'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No user type data available for the selected date range")
        except Exception as e:
            st.error(f"Error loading user type chart: {e}")
            
        st.markdown('</div>', unsafe_allow_html=True)

# Raw Data Exploration (Advanced)
st.markdown("## 🔬 Raw Data Exploration")
st.markdown("This section allows you to explore the raw data in your analytics database.")

tables = ["sessions", "interactions", "query_analytics", "educational_metrics"]
selected_table = st.selectbox("Select a table to explore", tables)

if selected_table:
    try:
        # Get column names
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Select which columns to display
        selected_columns = st.multiselect(
            "Select columns to display", 
            columns, 
            default=columns[:5]  # Default to first 5 columns
        )
        
        if selected_columns:
            # Query with limit
            limit = st.slider("Number of rows to display", 5, 100, 20)
            query = f"SELECT {', '.join(selected_columns)} FROM {selected_table} LIMIT {limit}"
            
            data = pd.read_sql(query, conn)
            st.dataframe(data)
            
            # Option to download as CSV
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name=f"{selected_table}.csv",
                mime="text/csv",
            )
    except Exception as e:
        st.error(f"Error exploring raw data: {e}")

# Footer
st.markdown("---")
st.markdown("*LR SchoolBot Analytics Dashboard* 📊")

# Close database connection
conn.close()
