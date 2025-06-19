import streamlit as st
import os
from datetime import datetime
import folium
from streamlit_folium import folium_static
from prompts import SYSTEM_PROMPT
from analytics import JSONAnalytics
import datetime

# Initialize OpenAI client with fallback for both Railway and Streamlit
try:
    from openai import OpenAI
    
    # Try multiple sources for API key
    api_key = None
    
    # First try environment variable (Railway)
    if os.environ.get("OPENAI_API_KEY"):
        api_key = os.environ.get("OPENAI_API_KEY")
    
    # Then try Streamlit secrets (Streamlit Cloud)
    elif hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        st.error("⚠️ OpenAI API key not found! Please add OPENAI_API_KEY to environment variables or Streamlit secrets.")
        st.stop()
        
except ImportError:
    st.error("OpenAI library not found. Please install: pip install openai")
    st.stop()
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

# Set page configuration with light theme default
st.set_page_config(
    page_title="LR SchoolBot",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme by default
st.markdown("""
    <style>
    .stApp {
        background-color: white;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

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
    body {
        background-color: white !important;
        color: #262730 !important;
    }

    .stApp {
        background-color: white !important;
    }

    .st-emotion-cache-ue6h4q {
        background-color: white !important;
    }

    .st-emotion-cache-ffhzg2 {
        background-color: white !important;
    }

    .st-emotion-cache-1avcm0n {
        background-color: white !important;
    }

    .css-18e3th9, .css-1d391kg {
        background-color: white !important;
    }
    
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
    .map-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .visitor-info {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Initialize analytics tracking
if 'analytics' not in st.session_state:
    st.session_state.analytics = JSONAnalytics()
    # Start a new session
    st.session_state.analytics.start_session()
    st.session_state.last_interaction_id = None

def get_assistant_response(messages, user_input):
    """Get response from OpenAI API"""
    start_time = datetime.datetime.now()
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        response_text = response.choices[0].message.content
        
        # Record when processing finished
        end_time = datetime.datetime.now()
        
        # Track this interaction
        if 'analytics' in st.session_state:
            interaction_id = st.session_state.analytics.track_interaction(
                query=user_input,
                response=response_text,
                start_time=start_time,
                end_time=end_time
            )
            # Store for potential feedback
            st.session_state.last_interaction_id = interaction_id
            
        return response_text
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def create_school_map():
    """Create a map with both schools marked"""
    m = folium.Map(location=[34.7370, -92.2986], zoom_start=13)
    
    # Add Central High School marker
    central_popup = """
    <b>Little Rock Central High School</b><br>
    1500 S Park St, Little Rock, AR 72202<br>
    <br>
    🏛️ National Historic Site<br>
    🕒 Visitor Center Hours: 9 AM - 4:30 PM<br>
    📞 Phone: (501) 374-1957<br>
    <br>
    <a href="https://www.nps.gov/chsc/" target="_blank">Visit Website</a>
    """
    
    folium.Marker(
        [34.7367, -92.2980],
        popup=central_popup,
        tooltip="Central High School",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Add Dunbar High School marker
    dunbar_popup = """
    <b>Historic Dunbar High School</b><br>
    (Now Dunbar Magnet Middle School)<br>
    1100 Wright Ave, Little Rock, AR 72202<br>
    <br>
    🏫 Historic Site<br>
    📚 Part of Little Rock's African American Heritage Trail<br>
    🎓 Historic Landmark
    """
    
    folium.Marker(
        [34.7399, -92.2867],
        popup=dunbar_popup,
        tooltip="Historic Dunbar High School",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)
    
    return m

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🎓 Navigation")
    st.markdown("---")
    page = st.radio(
        "",
        ["Home", "Chat with SchoolBot", "School Locations", "About", "Sources"]
    )
    
    st.markdown("---")

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
    st.markdown("""
    <div style="background-color: #FFF4DE; color: #664500; padding: 20px; border-radius: 10px; border-left: 5px solid #FFA500;">
    <strong>Did you know?</strong> Central High School's building is so special, it's a National Historic Site! That means it's as important as the Statue of Liberty! 🗽
    </div>
    """, unsafe_allow_html=True)

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
                response = get_assistant_response(st.session_state['messages'], user_input)
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
            
            # Add feedback buttons if we have a last interaction
            if 'last_interaction_id' in st.session_state and st.session_state.last_interaction_id:
                st.markdown("### Was this helpful?")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👍 Yes, thanks!"):
                        st.session_state.analytics.track_feedback(
                            st.session_state.last_interaction_id, 
                            feedback_score=5
                        )
                        st.success("Thanks for your feedback!")
                with col3:
                    if st.button("👎 Not really"):
                        st.session_state.analytics.track_feedback(
                            st.session_state.last_interaction_id, 
                            feedback_score=1
                        )
                        st.success("Thanks for your feedback!")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "School Locations":
    st.markdown('<p class="big-font">Find the Historic Schools! 🗺️</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📍 Explore These Historic Locations
    Want to visit these amazing schools? Here's where you can find them! The map below shows both 
    Central High School and the historic Dunbar High School building.
    """)
    
    # Display map in container
    with st.container():
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        map_obj = create_school_map()
        folium_static(map_obj)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visitor information
    st.markdown("""
    <div class="visitor-info">
    <h3>📸 Planning Your Visit</h3>
    
    <h4>Central High School National Historic Site</h4>
    <ul>
    <li>🏛️ Still an active high school</li>
    <li>🎟️ Free admission to visitor center</li>
    <li>🚶‍♂️ Guided tours available (reservation required)</li>
    <li>📚 Museum exhibits and educational programs</li>
    <li>🖼️ Historic photographs and artifacts</li>
    </ul>
    
    <h4>Historic Dunbar High School</h4>
    <ul>
    <li>🏫 Now Dunbar Magnet Middle School</li>
    <li>🗺️ Part of the Little Rock African American Heritage Trail</li>
    <li>📝 Historical markers on site</li>
    <li>🎨 Cultural significance in the community</li>
    <li>🌟 Architectural landmark</li>
    </ul>
    
    <h3>🚗 Getting There</h3>
    <ul>
    <li>Both sites are easily accessible by car</li>
    <li>Public parking available</li>
    <li>Located in historic Little Rock neighborhoods</li>
    <li>Can be visited in the same day</li>
    </ul>
    
    <h3>📸 Tips for Visitors</h3>
    <ol>
    <li>Check visitor center hours before going</li>
    <li>Respect active school zones during school hours</li>
    <li>Photography allowed outside buildings</li>
    <li>Join guided tours when available</li>
    <li>Visit during good weather for best experience</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

elif page == "About":
    st.markdown('<p class="big-font">About LR SchoolBot 🤖</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="about-section">
    <h3>👋 Meet Your Educational Guide!</h3>
    
    I'm LR SchoolBot, your friendly guide to exploring the rich educational heritage of Little Rock! 
    I'm here to share stories, facts, and history about two incredible schools that have shaped 
    our community: Central High School and Dunbar High School.
    
    <h3>🎯 My Purpose</h3>
    <ul>
    <li>Share the amazing history of these schools</li>
    <li>Help people learn about civil rights and education</li>
    <li>Connect you with historical resources</li>
    <li>Make learning history fun and interactive!</li>
    </ul>
    
    <h3>🎓 My Knowledge</h3>
    I'm trained on carefully selected historical sources and scholarly works about both schools. 
    While I know a lot, I'm always happy to direct you to additional resources for deeper research!
    
    <h3>💝 Special Thanks</h3>
    This project was created to help preserve and share Little Rock's educational heritage with 
    new generations. Special thanks to all the historians, educators, and community members who 
    have helped preserve these important stories.
    </div>
    """, unsafe_allow_html=True)

elif page == "Sources":
    st.markdown('<p class="big-font">Our Historical Sources 📚</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📖 Building Knowledge from Trusted Sources
    
    My knowledge comes from these carefully selected scholarly works and historical documents:
    """)
    
    st.markdown("""
    <div class="source-card">
    <h4>1. Jones-Wilson's "A Traditional Model of Educational Excellence: Dunbar High School"</h4>
    Published: 1981<br>
    Focus: Dunbar's educational legacy and community impact<br>
    Key aspects: Teaching methods, academic achievements, community influence
    </div>
    
    <div class="source-card">
    <h4>2. Gordy's "Finding the Lost Year"</h4>
    Published: 2009<br>
    Focus: School closure period and its impact<br>
    Key aspects: Community testimonies, historical documentation, social impact
    </div>
    
    <div class="source-card">
    <h4>3. Ross and Fulk's "Grand Central"</h4>
    Published: 1983<br>
    Focus: Central High School history (1927-1983)<br>
    Key aspects: Architectural significance, institutional development, key events
    </div>
    
    <div class="source-card">
    <h4>4. Stewart's "First Class: Legacy of Dunbar"</h4>
    Published: 2013<br>
    Focus: Dunbar's significance in African American education<br>
    Key aspects: Cultural impact, community perspectives, long-term influence
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📍 Additional Resources
    
    For more information, visit:
    - Central High National Historic Site Visitor Center
    - Little Rock Central High School National Historic Site Library
    - Butler Center for Arkansas Studies
    - UALR Center for Arkansas History and Culture
    """)

# Footer
st.markdown("---")
st.markdown("*LR SchoolBot - Exploring Little Rock's Educational Heritage* 📚")

# Handle session end
def on_session_end():
    if 'analytics' in st.session_state:
        st.session_state.analytics.end_session()

# Register session end handler
import atexit
atexit.register(on_session_end)
