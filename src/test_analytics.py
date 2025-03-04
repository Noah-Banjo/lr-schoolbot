import streamlit as st
import os
import json

st.title("Analytics Files Test")

# Check if analytics data exists
data_dir = "analytics_data"
sessions_file = os.path.join(data_dir, "sessions.json")
interactions_file = os.path.join(data_dir, "interactions.json")
feedback_file = os.path.join(data_dir, "feedback.json")

# Display file existence
st.write(f"Looking for analytics files in: {os.getcwd()}")
st.write(f"Data directory exists: {os.path.exists(data_dir)}")
st.write(f"Sessions file exists: {os.path.exists(sessions_file)}")
st.write(f"Interactions file exists: {os.path.exists(interactions_file)}")
st.write(f"Feedback file exists: {os.path.exists(feedback_file)}")

# Try to list all files in current directory
st.write("All files in current directory:")
st.write(os.listdir())

# If data directory exists, list files there
if os.path.exists(data_dir):
    st.write(f"Files in {data_dir}:")
    st.write(os.listdir(data_dir))
    
    # Try to read a file if it exists
    if os.path.exists(sessions_file):
        st.write("Reading sessions file:")
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
        st.write(f"Number of sessions: {len(sessions)}")
