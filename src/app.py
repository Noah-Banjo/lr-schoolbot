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

# Add JavaScript for Enter key handling
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        const submitButton = document.querySelector('button[kind="primary"]');
        if (submitButton) {
            submitButton.click();
        }
        e.preventDefault();
    }
});
</script>
""", unsafe_allow_html=True)

# Custom CSS
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
    .source-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1E88E5;
    }
    .about-section {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextArea textarea {
        font-size: 16px !important;
    }
    button[kind="primary"] {
        background-color: #1E88E5;
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

def get_assistant_response(messages):
    """Get response from OpenAI API"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🎓 Navigation")
    st.markdown("---")
    page = st.radio(
        "",
        ["Home", "Chat with SchoolBot", "School Locations", "About", "Sources"]
    )

# Main content
if page == "Home":
    st.markdown('<p class="big-font">Welcome to LR SchoolBot! 🎉</p>', unsafe_allow_html=True)
    st.markdown("### Your friendly guide to Little Rock's amazing school history! 🌟")
    
    st.markdown("""
    Hey there! 👋 I'm your friendly neighborhood SchoolBot, and I'm super excited to take you 
    on an amazing journey through the history of two incredible schools!
    """)

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

    st.markdown("### 🌟 Let's Explore Together!")
    st.markdown("""
    Here's what you can do:
    1. 💬 **Chat with me** - Ask any questions about the schools
    2. 🗺️ **Find the schools** - See where these amazing places are
    3. 📚 **Learn cool facts** - Discover fascinating stories
    4. 🎨 **Share with friends** - Tell others what you learn
    """)

    st.markdown("### ✨ Fun Fact of the Day")
    st.info("Did you know? Central High School's building is so special, it's a National Historic Site! That means it's as important as the Statue of Liberty! 🗽")

elif page == "Chat with SchoolBot":
    st.markdown('<p class="big-font">Chat with LR SchoolBot! 🤖</p>', unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Show active topics
        if len(st.session_state['messages']) > 2:
            recent_topics = set()
            for msg in st.session_state['messages'][-3:]:
                if msg["role"] == "user":
                    recent_topics.add(msg["content"].lower())
            if recent_topics:
                st.markdown("#### 🎯 We've been talking about:")
                for topic in recent_topics:
                    st.markdown(f"- {topic}")
                st.markdown("---")

        # Chat interface
        with st.form(key='message_form', clear_on_submit=True):
            user_input = st.text_area("What would you like to know? 🤔", 
                                    key='input', 
                                    height=100,
                                    placeholder="Type your message here... (Press Enter to send)")
            submit_button = st.form_submit_button("Send Message", use_container_width=True)

            if submit_button and user_input:
                st.session_state['messages'].append({"role": "user", "content": user_input})
                response = get_assistant_response(st.session_state['messages'])
                if response:
                    st.session_state['messages'].append({"role": "assistant", "content": response})

        # Display chat history
        if len(st.session_state['messages']) > 1:
            st.markdown("### Our Conversation 📝")
            for message in reversed(st.session_state['messages'][1:]):
                if message["role"] == "user":
                    st.markdown(f"👤 **You:** {message['content']}")
                else:
                    st.markdown(f"🤖 **SchoolBot:** {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "School Locations":
    [Previous map code remains the same...]

elif page == "About":
    [Previous about code remains the same...]

elif page == "Sources":
    [Previous sources code remains the same...]

# Footer
st.markdown("---")
st.markdown("*LR SchoolBot - Exploring Little Rock's Educational Heritage* 📚")
