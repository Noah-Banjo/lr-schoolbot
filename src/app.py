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

elif page == "🗺️ School Locations":
    st.markdown('<p class="big-font">Find the Historic Schools! 🗺️</p>', unsafe_allow_html=True)
    
    # Introduction to the locations
    st.markdown("""
    ### 📍 Explore These Historic Locations
    Want to visit these amazing schools? Here's where you can find them! The map below shows both 
    Central High School and the historic Dunbar High School building.
    """)
    
    def create_school_map():
        # Create a map centered between the two schools
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
    
    # Display the map
    map_obj = create_school_map()
    folium_static(map_obj)
    
    # Additional information about visiting
    st.markdown("""
    ### 📸 Planning Your Visit
    
    #### Central High School National Historic Site
    - 🏛️ Still an active high school
    - 🎟️ Free admission to visitor center
    - 🚶‍♂️ Guided tours available (reservation required)
    - 📚 Museum exhibits and educational programs
    - 🖼️ Historic photographs and artifacts
    
    #### Historic Dunbar High School
    - 🏫 Now Dunbar Magnet Middle School
    - 🗺️ Part of the Little Rock African American Heritage Trail
    - 📝 Historical markers on site
    - 🎨 Cultural significance in the community
    - 🌟 Architectural landmark
    
    ### 🚗 Getting There
    - Both sites are easily accessible by car
    - Public parking available
    - Located in historic Little Rock neighborhoods
    - Can be visited in the same day
    
    ### 📸 Tips for Visitors
    1. Check visitor center hours before going
    2. Respect active school zones during school hours
    3. Photography allowed outside buildings
    4. Join guided tours when available
    5. Visit during good weather for best experience
    """)

elif page == "ℹ️ About":
    st.markdown('<p class="big-font">About LR SchoolBot 🤖</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="about-section">
    <h3>👋 Meet Your Educational Guide!</h3>
    
    I'm LR SchoolBot, your friendly guide to exploring the rich educational heritage of Little Rock! 
    I'm here to share stories, facts, and history about two incredible schools that have shaped 
    our community: Central High School and Dunbar High School.
    
    ### 🎯 My Purpose
    - Share the amazing history of these schools
    - Help people learn about civil rights and education
    - Connect you with historical resources
    - Make learning history fun and interactive!
    
    ### 🎓 My Knowledge
    I'm trained on carefully selected historical sources and scholarly works about both schools. 
    While I know a lot, I'm always happy to direct you to additional resources for deeper research!
    
    ### 💝 Special Thanks
    This project was created to help preserve and share Little Rock's educational heritage with 
    new generations. Special thanks to all the historians, educators, and community members who 
    have helped preserve these important stories.
    </div>
    """, unsafe_allow_html=True)

elif page == "📚 Sources":
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
