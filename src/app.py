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
    layout="wide"
)

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
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message["content"]
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select:",
        ["Chat with LR SchoolBot", "School Locations", "About", "Sources"]
    )

# Main content
if page == "Chat with LR SchoolBot":
    st.title("🏫 LR SchoolBot")
    st.markdown("""
    Welcome! I'm here to share the rich educational heritage of Little Rock through the stories 
    of Central High School and Dunbar High. What would you like to learn about?
    
    You can ask about:
    - The schools' histories and significance
    - Integration and civil rights history
    - Community impact and voices
    - Notable alumni and achievements
    """)

    # Chat interface
    with st.form(key='message_form', clear_on_submit=True):
        user_input = st.text_area("Your question:", key='input', height=100)
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input:
            st.session_state['messages'].append({"role": "user", "content": user_input})
            response = get_assistant_response(st.session_state['messages'])
            if response:
                st.session_state['messages'].append({"role": "assistant", "content": response})

    # Display chat history
    if len(st.session_state['messages']) > 1:
        st.markdown("### Conversation History")
        for message in reversed(st.session_state['messages'][1:]):
            if message["role"] == "user":
                st.markdown(f"👤 **You:** {message['content']}")
            else:
                st.markdown(f"🏫 **LR SchoolBot:** {message['content']}")
