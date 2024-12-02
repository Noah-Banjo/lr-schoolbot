import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="LR SchoolBot",
    page_icon="🏫",
    layout="wide"
)

# Basic title and welcome message
st.title("🏫 LR SchoolBot")
st.markdown("Welcome! I'm here to share the rich educational heritage of Little Rock.")

# Simple test button to verify everything works
if st.button("Click me to test!"):
    st.write("Everything is working correctly!")
