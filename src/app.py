import streamlit as st
import openai
from datetime import datetime
import folium
from streamlit_folium import folium_static
from prompts import SYSTEM_PROMPT

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set page configuration
st.set_page_config(
    page_title="LR SchoolBot",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make it more attractive
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .school-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
    }
    .chat-container {
        border-radius: 15px;
        padding: 20px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#4CAF50,#2196F3);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Get assistant response function (same as before)
def get_assistant_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar with fun design
with st.sidebar:
    st.markdown("# 🎓 Navigation")
    st.markdown("---")
    page = st.radio(
        "",
        ["🏠 Home", "💬 Chat with LR SchoolBot", "🗺️ School Locations", 
         "ℹ️ About", "📚 Sources"],
        index=0
    )

# Main content
if page == "🏠 Home":
    # Hero section
    st.markdown('<p class="big-font">Welcome to LR SchoolBot! 🎉</p>', unsafe_allow_html=True)
    st.markdown("### Your friendly guide to Little Rock's amazing school history! 🌟")
    
    # Introduction with emojis
    st.markdown("""
    Hey there! 👋 I'm your friendly neighborhood SchoolBot, and I'm super excited to take you 
    on an amazing journey through the history of two incredible schools!
    """)

    # School cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="school-card">
        <h3>🏛️ Central High School</h3>
        <ul>
        <li>Historic landmark</li>
        <li>Symbol of civil rights</li>
        <li>Amazing architecture</li>
        <li>Incredible stories</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="school-card">
        <h3>🎓 Dunbar High School</h3>
        <ul>
        <li>Educational excellence</li>
        <li>Rich community heritage</li>
        <li>Inspiring legacy</li>
        <li>Remarkable achievements</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # Quick start guide
    st.markdown("### 🌟 Let's Explore Together!")
    st.markdown("""
    Here's what you can do:
    1. 💬 **Chat with me** - Ask any questions about the schools
    2. 🗺️ **Find the schools** - See where these amazing places are
    3. 📚 **Learn cool facts** - Discover fascinating stories
    4. 🎨 **Share with friends** - Tell others what you learn
    """)

    # Fun fact of the day
    st.markdown("### ✨ Fun Fact of the Day")
    st.info("Did you know? Central High School's building is so special, it's a National Historic Site! That means it's as important as the Statue of Liberty! 🗽")

elif page == "💬 Chat with LR SchoolBot":
    st.markdown('<p class="big-font">Chat with LR SchoolBot! 🤖</p>', unsafe_allow_html=True)
    
    # Chat interface in a container
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        with st.form(key='message_form', clear_on_submit=True):
            user_input = st.text_area("What would you like to know? 🤔", key='input', height=100)
            submit_button = st.form_submit_button("Ask Away! 🚀")

            if submit_button and user_input:
                st.session_state['messages'].append({"role": "user", "content": user_input})
                response = get_assistant_response(st.session_state['messages'])
                if response:
                    st.session_state['messages'].append({"role": "assistant", "content": response})

        # Display chat history with emoji markers
        if len(st.session_state['messages']) > 1:
            st.markdown("### Our Conversation 📝")
            for message in reversed(st.session_state['messages'][1:]):
                if message["role"] == "user":
                    st.markdown(f"👤 **You:** {message['content']}")
                else:
                    st.markdown(f"🤖 **SchoolBot:** {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

# Continue with other pages...
