import os
import json
import uuid
import datetime
from textblob import TextBlob
import streamlit as st
st.sidebar.info("Using JSON-based analytics_dashboard.py file")  # In your main file
class JSONAnalytics:
    """
    A simple analytics system that stores data in JSON files.
    Tracks user sessions, interactions, and provides basic analytics.
    """
    
    def __init__(self, data_dir="analytics_data"):
        """Initialize the analytics system with a directory for storing JSON files"""
        self.data_dir = data_dir
        self.session_id = None
        self.user_id = None
        self.session_start_time = None
        self.interaction_count = 0
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
        
    def _init_files(self):
        """Initialize the JSON files if they don't exist"""
        # Sessions file
        sessions_file = os.path.join(self.data_dir, "sessions.json")
        if not os.path.exists(sessions_file):
            with open(sessions_file, 'w') as f:
                json.dump([], f)
                
        # Interactions file
        interactions_file = os.path.join(self.data_dir, "interactions.json")
        if not os.path.exists(interactions_file):
            with open(interactions_file, 'w') as f:
                json.dump([], f)
                
        # Feedback file
        feedback_file = os.path.join(self.data_dir, "feedback.json")
        if not os.path.exists(feedback_file):
            with open(feedback_file, 'w') as f:
                json.dump([], f)
    
    def start_session(self):
        """Start tracking a new user session"""
        # Generate session ID
        self.session_id = str(uuid.uuid4())
        
        # Get or create persistent user ID
        if 'user_id' in st.session_state:
            self.user_id = st.session_state.user_id
            is_return_user = True
        else:
            self.user_id = str(uuid.uuid4())
            st.session_state.user_id = self.user_id
            is_return_user = False
        
        # Track session start time
        self.session_start_time = datetime.datetime.now()
        self.interaction_count = 0
        
        # Get device info
        device_type = "unknown"
        browser = "unknown"
        
        # Store session data
        session_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.session_start_time.isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "interaction_count": 0,
            "device_type": device_type,
            "browser": browser,
            "is_return_user": is_return_user
        }
        
        # Load existing sessions
        sessions_file = os.path.join(self.data_dir, "sessions.json")
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
            
        # Add new session
        sessions.append(session_data)
        
        # Save sessions
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f)
            
        return self.session_id
    
    def end_session(self):
        """End the current tracking session and update final metrics"""
        if not self.session_id:
            return
            
        # Calculate session duration
        end_time = datetime.datetime.now()
        duration_seconds = (end_time - self.session_start_time).total_seconds()
        
        # Load sessions
        sessions_file = os.path.join(self.data_dir, "sessions.json")
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
            
        # Update session data
        for session in sessions:
            if session["session_id"] == self.session_id:
                session["end_time"] = end_time.isoformat()
                session["duration_seconds"] = duration_seconds
                session["interaction_count"] = self.interaction_count
                break
                
        # Save sessions
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f)
            
        # Reset session tracking
        self.session_id = None
        self.session_start_time = None
        self.interaction_count = 0
        
    def track_interaction(self, query, response, start_time=None, end_time=None):
        """Track a single interaction between user and chatbot"""
        if not self.session_id:
            return None
            
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now()
        
        # Set defaults for optional parameters
        if not start_time:
            start_time = timestamp
        if not end_time:
            end_time = timestamp
            
        # Calculate response time
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Classify query type
        query_type = self._classify_query_type(query)
        
        # Sentiment analysis
        sentiment = TextBlob(query).sentiment.polarity
        
        # Extract topics
        topics = self._extract_topics(query)
        
        # Store interaction data
        interaction_data = {
            "interaction_id": interaction_id,
            "session_id": self.session_id,
            "timestamp": timestamp.isoformat(),
            "query": query,
            "query_type": query_type,
            "response": response,
            "response_time_ms": response_time_ms,
            "sentiment_score": sentiment,
            "topics": topics,
            "feedback_score": None
        }
        
        # Load interactions
        interactions_file = os.path.join(self.data_dir, "interactions.json")
        with open(interactions_file, 'r') as f:
            interactions = json.load(f)
            
        # Add new interaction
        interactions.append(interaction_data)
        
        # Save interactions
        with open(interactions_file, 'w') as f:
            json.dump(interactions, f)
            
        # Update interaction count
        self.interaction_count += 1
        
        return interaction_id
        
    def track_feedback(self, interaction_id, feedback_score):
        """Track user feedback for a specific interaction"""
        if not interaction_id:
            return
            
        # Load interactions
        interactions_file = os.path.join(self.data_dir, "interactions.json")
        with open(interactions_file, 'r') as f:
            interactions = json.load(f)
            
        # Update interaction with feedback
        for interaction in interactions:
            if interaction["interaction_id"] == interaction_id:
                interaction["feedback_score"] = feedback_score
                break
                
        # Save interactions
        with open(interactions_file, 'w') as f:
            json.dump(interactions, f)
            
        # Also store in feedback file for easier analysis
        feedback_data = {
            "interaction_id": interaction_id,
            "session_id": self.session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "feedback_score": feedback_score
        }
        
        # Load feedback
        feedback_file = os.path.join(self.data_dir, "feedback.json")
        with open(feedback_file, 'r') as f:
            feedback = json.load(f)
            
        # Add new feedback
        feedback.append(feedback_data)
        
        # Save feedback
        with open(feedback_file, 'w') as f:
            json.dump(feedback, f)
    
    def _classify_query_type(self, query):
        """Classify the type of query based on text analysis"""
        query = query.lower()
        
        if any(x in query for x in ["what", "who", "where", "when", "why", "how"]):
            if "when" in query or "what year" in query or "what date" in query:
                return "temporal_question"
            elif "who" in query:
                return "person_question"
            elif "where" in query:
                return "location_question"
            elif "why" in query or "explain" in query:
                return "explanation_question"
            else:
                return "factual_question"
        elif any(x in query for x in ["find", "search", "locate", "show me"]):
            return "search_request"
        elif any(x in query for x in ["compare", "difference", "similar"]):
            return "comparison_request"
        else:
            return "general_query"
    
    def _extract_topics(self, text):
        """Extract main topics from text"""
        words = text.lower().split()
        stopwords = {"the", "a", "an", "of", "and", "or", "but", "is", "are"}
        topics = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Return top 3 longest words as topics
        return sorted(topics, key=len, reverse=True)[:3]
