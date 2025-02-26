import os
import json
import uuid
import time
import datetime
import pandas as pd
import sqlite3
from pathlib import Path
import hashlib
import re
from textblob import TextBlob  # For sentiment analysis
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

class ArchivalChatbotAnalytics:
    """
    A comprehensive analytics tracking system for archival chatbots.
    This class handles session tracking, user interactions, query analysis,
    and generates reports on usage patterns and educational impact.
    
    Note: This analytics system does not collect or store any gender, sex, 
    or other demographic information about users.
    """
    
    def __init__(self, storage_type="sqlite", db_path="analytics.db", log_dir="analytics_logs"):
        """
        Initialize the analytics system.
        
        This system does not collect or store any gender or sex information.
        
        Args:
            storage_type (str): Type of storage ('sqlite' or 'csv')
            db_path (str): Path to the SQLite database
            log_dir (str): Directory for storing CSV logs
        """
        self.storage_type = storage_type
        self.db_path = db_path
        self.log_dir = log_dir
        self.session_id = None
        self.user_id = None
        self.session_start_time = None
        self.last_interaction_time = None
        self.interaction_count = 0
        self.current_topics = []
        self.historical_entities = set()
        
        # Initialize storage
        if self.storage_type == "sqlite":
            self._init_sqlite_db()
        else:
            self._init_csv_storage()
            
    def _init_sqlite_db(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        # Note: We do not collect any demographic data (gender, sex, age, etc.)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds INTEGER,
            interaction_count INTEGER,
            device_type TEXT,
            browser TEXT,
            is_mobile BOOLEAN,
            is_return_user BOOLEAN
        )
        ''')
        
        # Create interactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id TEXT PRIMARY KEY,
            session_id TEXT,
            timestamp TIMESTAMP,
            query TEXT,
            query_type TEXT,
            response TEXT,
            response_time_ms INTEGER,
            sentiment_score REAL,
            is_successful BOOLEAN,
            is_fallback BOOLEAN,
            topics TEXT,
            historical_entities TEXT,
            feedback_score INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        # Create query_analytics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_analytics (
            query_id TEXT PRIMARY KEY,
            session_id TEXT,
            query TEXT,
            query_length INTEGER,
            query_complexity REAL,
            is_reformulation BOOLEAN,
            previous_query_id TEXT,
            topic_cluster TEXT,
            has_followup BOOLEAN,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        # Create educational_metrics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS educational_metrics (
            session_id TEXT,
            topic TEXT,
            exploration_depth INTEGER,
            time_spent_seconds INTEGER,
            historical_figures TEXT,
            historical_events TEXT,
            complexity_progression REAL,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_csv_storage(self):
        """Initialize CSV storage with required directories"""
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Define CSV file paths
        self.sessions_csv = os.path.join(self.log_dir, "sessions.csv")
        self.interactions_csv = os.path.join(self.log_dir, "interactions.csv")
        self.query_analytics_csv = os.path.join(self.log_dir, "query_analytics.csv")
        self.educational_metrics_csv = os.path.join(self.log_dir, "educational_metrics.csv")
        
        # Initialize CSV files with headers if they don't exist
        if not os.path.exists(self.sessions_csv):
            pd.DataFrame(columns=[
                "session_id", "user_id", "start_time", "end_time", 
                "duration_seconds", "interaction_count", "device_type", 
                "browser", "is_mobile", "is_return_user"
            ]).to_csv(self.sessions_csv, index=False)
            
        if not os.path.exists(self.interactions_csv):
            pd.DataFrame(columns=[
                "interaction_id", "session_id", "timestamp", "query", 
                "query_type", "response", "response_time_ms", 
                "sentiment_score", "is_successful", "is_fallback", 
                "topics", "historical_entities", "feedback_score"
            ]).to_csv(self.interactions_csv, index=False)
            
        if not os.path.exists(self.query_analytics_csv):
            pd.DataFrame(columns=[
                "query_id", "session_id", "query", "query_length", 
                "query_complexity", "is_reformulation", "previous_query_id", 
                "topic_cluster", "has_followup"
            ]).to_csv(self.query_analytics_csv, index=False)
            
        if not os.path.exists(self.educational_metrics_csv):
            pd.DataFrame(columns=[
                "session_id", "topic", "exploration_depth", "time_spent_seconds", 
                "historical_figures", "historical_events", "complexity_progression"
            ]).to_csv(self.educational_metrics_csv, index=False)
    
    def start_session(self, request_headers=None):
        """
        Start tracking a new user session.
        
        Args:
            request_headers (dict): HTTP headers to extract device information
        
        Returns:
            str: The generated session ID
        """
        # Generate session ID
        self.session_id = str(uuid.uuid4())
        
        # Get or create persistent user ID using browser fingerprint or cookies
        if 'user_id' in st.session_state:
            self.user_id = st.session_state.user_id
            is_return_user = True
        else:
            self.user_id = str(uuid.uuid4())
            st.session_state.user_id = self.user_id
            is_return_user = False
        
        # Track session start time
        self.session_start_time = datetime.datetime.now()
        self.last_interaction_time = self.session_start_time
        self.interaction_count = 0
        
        # Extract device information
        device_type = "unknown"
        browser = "unknown"
        is_mobile = False
        
        if request_headers:
            user_agent = request_headers.get('User-Agent', '')
            if 'Mobile' in user_agent or 'Android' in user_agent:
                is_mobile = True
                device_type = "mobile"
            elif 'Tablet' in user_agent:
                device_type = "tablet"
            else:
                device_type = "desktop"
                
            # Extract browser info
            if 'Chrome' in user_agent:
                browser = "Chrome"
            elif 'Firefox' in user_agent:
                browser = "Firefox"
            elif 'Safari' in user_agent:
                browser = "Safari"
            elif 'Edge' in user_agent:
                browser = "Edge"
        
        # Store basic session info
        session_data = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.session_start_time,
            "end_time": None,
            "duration_seconds": 0,
            "interaction_count": 0,
            "device_type": device_type,
            "browser": browser,
            "is_mobile": is_mobile,
            "is_return_user": is_return_user
        }
        
        # Save initial session data
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    session_data["session_id"], session_data["user_id"], 
                    session_data["start_time"], session_data["end_time"],
                    session_data["duration_seconds"], session_data["interaction_count"],
                    session_data["device_type"], session_data["browser"],
                    session_data["is_mobile"], session_data["is_return_user"]
                )
            )
            conn.commit()
            conn.close()
        else:
            # CSV storage
            sessions_df = pd.read_csv(self.sessions_csv)
            sessions_df = pd.concat([sessions_df, pd.DataFrame([session_data])], ignore_index=True)
            sessions_df.to_csv(self.sessions_csv, index=False)
        
        return self.session_id
    
    def end_session(self):
        """
        End the current tracking session and update final metrics.
        """
        if not self.session_id:
            return
            
        # Calculate session duration
        end_time = datetime.datetime.now()
        duration_seconds = (end_time - self.session_start_time).total_seconds()
        
        # Update session data
        session_update = {
            "end_time": end_time,
            "duration_seconds": duration_seconds,
            "interaction_count": self.interaction_count
        }
        
        # Store updated session data
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE sessions SET end_time = ?, duration_seconds = ?, interaction_count = ? WHERE session_id = ?''',
                (session_update["end_time"], session_update["duration_seconds"], session_update["interaction_count"], self.session_id)
            )
            conn.commit()
            conn.close()
        else:
            # CSV storage
            sessions_df = pd.read_csv(self.sessions_csv)
            sessions_df.loc[sessions_df.session_id == self.session_id, "end_time"] = end_time
            sessions_df.loc[sessions_df.session_id == self.session_id, "duration_seconds"] = duration_seconds
            sessions_df.loc[sessions_df.session_id == self.session_id, "interaction_count"] = self.interaction_count
            sessions_df.to_csv(self.sessions_csv, index=False)
        
        # Reset session tracking
        self.session_id = None
        self.session_start_time = None
        self.interaction_count = 0
        
    def track_interaction(self, query, response, start_time=None, end_time=None, 
                         query_type=None, is_successful=None, is_fallback=None,
                         topics=None, historical_entities=None, feedback_score=None):
        """
        Track a single interaction between user and chatbot.
        
        Args:
            query (str): User's query text
            response (str): Chatbot's response text
            start_time (datetime): When query processing started
            end_time (datetime): When response was delivered
            query_type (str): Classification of query type
            is_successful (bool): Whether the response was helpful
            is_fallback (bool): Whether a fallback response was used
            topics (list): Topics identified in the conversation
            historical_entities (list): Historical entities mentioned
            feedback_score (int): User feedback score if provided
            
        Returns:
            str: The generated interaction ID
        """
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
        
        # Use NLP to analyze query if query_type not provided
        if not query_type:
            query_type = self._classify_query_type(query)
            
        # Perform sentiment analysis on the query
        sentiment = TextBlob(query).sentiment
        sentiment_score = sentiment.polarity
        
        # Extract topics if not provided
        if not topics:
            topics = self._extract_topics(query)
        
        # Extract historical entities if not provided
        if not historical_entities:
            historical_entities = self._extract_historical_entities(query)
            
        # Update current session topics and entities
        self.current_topics.extend(topics)
        self.historical_entities.update(historical_entities)
        
        # Store interaction data
        interaction_data = {
            "interaction_id": interaction_id,
            "session_id": self.session_id,
            "timestamp": timestamp,
            "query": query,
            "query_type": query_type,
            "response": response,
            "response_time_ms": response_time_ms,
            "sentiment_score": sentiment_score,
            "is_successful": is_successful if is_successful is not None else True,
            "is_fallback": is_fallback if is_fallback is not None else False,
            "topics": json.dumps(topics),
            "historical_entities": json.dumps(list(historical_entities)),
            "feedback_score": feedback_score
        }
        
        # Save interaction data
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    interaction_data["interaction_id"], interaction_data["session_id"], 
                    interaction_data["timestamp"], interaction_data["query"],
                    interaction_data["query_type"], interaction_data["response"],
                    interaction_data["response_time_ms"], interaction_data["sentiment_score"],
                    interaction_data["is_successful"], interaction_data["is_fallback"],
                    interaction_data["topics"], interaction_data["historical_entities"],
                    interaction_data["feedback_score"]
                )
            )
            conn.commit()
            conn.close()
        else:
            # CSV storage
            interactions_df = pd.read_csv(self.interactions_csv)
            interactions_df = pd.concat([interactions_df, pd.DataFrame([interaction_data])], ignore_index=True)
            interactions_df.to_csv(self.interactions_csv, index=False)
        
        # Track additional query analytics
        self._track_query_analytics(interaction_id, query)
        
        # Update session metrics
        self.interaction_count += 1
        self.last_interaction_time = timestamp
        
        # Update educational metrics if related to historical/educational content
        if historical_entities:
            self._track_educational_metrics(topics, historical_entities)
            
        return interaction_id
        
    def track_feedback(self, interaction_id, feedback_score, feedback_text=None):
        """
        Track explicit user feedback for a specific interaction.
        
        Args:
            interaction_id (str): ID of the interaction
            feedback_score (int): Numerical score (e.g., 1-5)
            feedback_text (str): Optional text feedback
        """
        if not interaction_id:
            return
            
        # Update the interaction record with feedback
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE interactions SET feedback_score = ? WHERE interaction_id = ?''',
                (feedback_score, interaction_id)
            )
            conn.commit()
            conn.close()
        else:
            # CSV storage
            interactions_df = pd.read_csv(self.interactions_csv)
            interactions_df.loc[interactions_df.interaction_id == interaction_id, "feedback_score"] = feedback_score
            interactions_df.to_csv(self.interactions_csv, index=False)
            
        # Store additional feedback text if provided
        if feedback_text:
            feedback_data = {
                "interaction_id": interaction_id,
                "session_id": self.session_id,
                "timestamp": datetime.datetime.now(),
                "feedback_score": feedback_score,
                "feedback_text": feedback_text
            }
            
            feedback_file = os.path.join(self.log_dir, "feedback.csv")
            if os.path.exists(feedback_file):
                feedback_df = pd.read_csv(feedback_file)
                feedback_df = pd.concat([feedback_df, pd.DataFrame([feedback_data])], ignore_index=True)
            else:
                feedback_df = pd.DataFrame([feedback_data])
                
            feedback_df.to_csv(feedback_file, index=False)
    
    def _track_query_analytics(self, interaction_id, query):
        """
        Track detailed analytics about a specific query.
        
        Args:
            interaction_id (str): ID of the interaction
            query (str): User's query text
        """
        # Generate query ID
        query_id = str(uuid.uuid4())
        
        # Calculate query complexity (based on length, structure, etc.)
        query_length = len(query)
        query_complexity = self._calculate_query_complexity(query)
        
        # Check if this is a reformulation of a previous query
        is_reformulation = False
        previous_query_id = None
        
        if self.interaction_count > 0:
            # Get the previous query
            if self.storage_type == "sqlite":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT interaction_id, query FROM interactions 
                    WHERE session_id = ? ORDER BY timestamp DESC LIMIT 1''',
                    (self.session_id,)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    prev_interaction_id, prev_query = result
                    is_reformulation = self._is_query_reformulation(prev_query, query)
                    if is_reformulation:
                        previous_query_id = prev_interaction_id
            else:
                # CSV storage
                interactions_df = pd.read_csv(self.interactions_csv)
                session_interactions = interactions_df[interactions_df.session_id == self.session_id]
                
                if not session_interactions.empty:
                    prev_interaction = session_interactions.iloc[-1]
                    prev_query = prev_interaction["query"]
                    is_reformulation = self._is_query_reformulation(prev_query, query)
                    if is_reformulation:
                        previous_query_id = prev_interaction["interaction_id"]
        
        # Determine topic cluster
        topic_cluster = self._determine_topic_cluster(query)
        
        # Prepare has_followup field (will be updated later)
        has_followup = False
        
        # Store query analytics data
        query_data = {
            "query_id": query_id,
            "session_id": self.session_id,
            "query": query,
            "query_length": query_length,
            "query_complexity": query_complexity,
            "is_reformulation": is_reformulation,
            "previous_query_id": previous_query_id,
            "topic_cluster": topic_cluster,
            "has_followup": has_followup
        }
        
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO query_analytics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    query_data["query_id"], query_data["session_id"], query_data["query"],
                    query_data["query_length"], query_data["query_complexity"],
                    query_data["is_reformulation"], query_data["previous_query_id"],
                    query_data["topic_cluster"], query_data["has_followup"]
                )
            )
            conn.commit()
            conn.close()
        else:
            # CSV storage
            query_df = pd.read_csv(self.query_analytics_csv)
            query_df = pd.concat([query_df, pd.DataFrame([query_data])], ignore_index=True)
            query_df.to_csv(self.query_analytics_csv, index=False)
            
        # Update has_followup field of previous query if this is a followup
        if self.interaction_count > 0 and not is_reformulation:
            if self.storage_type == "sqlite":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    '''UPDATE query_analytics SET has_followup = ? 
                    WHERE session_id = ? ORDER BY rowid DESC LIMIT 1''',
                    (True, self.session_id)
                )
                conn.commit()
                conn.close()
            else:
                # CSV storage
                query_df = pd.read_csv(self.query_analytics_csv)
                session_queries = query_df[query_df.session_id == self.session_id]
                
                if not session_queries.empty:
                    prev_query_id = session_queries.iloc[-1]["query_id"]
                    query_df.loc[query_df.query_id == prev_query_id, "has_followup"] = True
                    query_df.to_csv(self.query_analytics_csv, index=False)
    
    def _track_educational_metrics(self, topics, historical_entities):
        """
        Track metrics about educational impact and historical exploration.
        
        Args:
            topics (list): Topics identified in the conversation
            historical_entities (list): Historical entities mentioned
        """
        # Calculate exploration depth based on specificity of entities
        exploration_depth = self._calculate_exploration_depth(historical_entities)
        
        # Calculate time spent on current educational topic
        time_spent_seconds = 0
        if self.last_interaction_time:
            time_spent_seconds = (datetime.datetime.now() - self.last_interaction_time).total_seconds()
            
        # Categorize entities into figures and events
        historical_figures = []
        historical_events = []
        
        for entity in historical_entities:
            if self._is_person_entity(entity):
                historical_figures.append(entity)
            else:
                historical_events.append(entity)
                
        # Calculate complexity progression
        complexity_progression = self._calculate_complexity_progression()
        
        # Store educational metrics data
        for topic in topics:
            educational_data = {
                "session_id": self.session_id,
                "topic": topic,
                "exploration_depth": exploration_depth,
                "time_spent_seconds": time_spent_seconds,
                "historical_figures": json.dumps(historical_figures),
                "historical_events": json.dumps(historical_events),
                "complexity_progression": complexity_progression
            }
            
            if self.storage_type == "sqlite":
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO educational_metrics VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (
                        educational_data["session_id"], educational_data["topic"],
                        educational_data["exploration_depth"], educational_data["time_spent_seconds"],
                        educational_data["historical_figures"], educational_data["historical_events"],
                        educational_data["complexity_progression"]
                    )
                )
                conn.commit()
                conn.close()
            else:
                # CSV storage
                educational_df = pd.read_csv(self.educational_metrics_csv)
                educational_df = pd.concat([educational_df, pd.DataFrame([educational_data])], ignore_index=True)
                educational_df.to_csv(self.educational_metrics_csv, index=False)
    
    def _classify_query_type(self, query):
        """Classify the type of query based on text analysis"""
        # Simple rule-based classification - could be replaced with ML model
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
            elif "how" in query:
                return "process_question"
            else:
                return "factual_question"
        elif any(x in query for x in ["find", "search", "locate", "show me", "look for"]):
            return "search_request"
        elif any(x in query for x in ["compare", "difference", "similar", "versus", "vs"]):
            return "comparison_request"
        elif any(x in query for x in ["thank", "thanks", "good", "great", "excellent"]):
            return "feedback"
        elif len(query.split()) <= 3:
            return "short_query"
        else:
            return "exploratory_question"
    
    def _extract_topics(self, text):
        """Extract main topics from text using NLP techniques"""
        # This is a simplified version - ideally would use a topic model or NER
        # For now, just extract nouns and noun phrases as potential topics
        words = text.lower().split()
        stopwords = {"the", "a", "an", "of", "and", "or", "but", "is", "are", "was", "were"}
        topics = [word for word in words if word not in stopwords and len(word) > 3]
        
        # Return top 3 longest words as topics
        return sorted(topics, key=len, reverse=True)[:3]
    
    def _extract_historical_entities(self, text):
        """Extract historical entities from text"""
        # Simplified version - would use named entity recognition in production
        # Look for capitalized phrases, dates, etc.
        capitalized_pattern = r'\b[A-Z][a-zA-Z]+ (?:[A-Z][a-zA-Z]+ )*[A-Z][a-zA-Z]+\b'
        date_pattern = r'\b\d{4}s?\b|\b\d{1,2}th century\b'
        
        entities = set()
        
        # Find capitalized phrases
        capitalized_matches = re.findall(capitalized_pattern, text)
        entities.update(capitalized_matches)
        
        # Find dates
        date_matches = re.findall(date_pattern, text)
        entities.update(date_matches)
        
        return entities
    
    def _calculate_query_complexity(self, query):
        """Calculate query complexity based on length, structure, etc."""
        # Simple heuristic based on length and question words
        words = query.split()
        length_score = min(len(words) / 10, 1.0)  # Normalize to 0-1 range
        
        # Check for complex query indicators
        complex_indicators = ["compare", "relationship", "influence", "impact", "cause", "effect", 
                             "why", "how", "analysis", "interpret", "evaluate", "between"]
        
        indicator_score = sum(1 for word in words if word.lower() in complex_indicators) / len(complex_indicators)
        
        # Calculate final complexity score (0-1 range)
        complexity = (length_score + indicator_score) / 2
        return round(complexity, 2)
    
    def _is_query_reformulation(self, prev_query, curr_query):
        """Determine if current query is a reformulation of previous query"""
        # Simple check for similarity
        prev_words = set(prev_query.lower().split())
        curr_words = set(curr_query.lower().split())
        
        # Calculate Jaccard similarity
        intersection = prev_words.intersection(curr_words)
        union = prev_words.union(curr_words)
        
        similarity = len(intersection) / len(union) if union else 0
        
        # Check if query length difference is significant
        length_diff = abs(len(prev_query) - len(curr_query)) / max(len(prev_query), len(curr_query))
        
        # Consider it a reformulation if similar but not identical
        return 0.3 <= similarity <= 0.8 or length_diff < 0.3
    
    def _determine_topic_cluster(self, query):
        """Determine which topic cluster the query belongs to"""
        # Simplified clustering - could be replaced with more advanced techniques
        topic_keywords = {
            "document_preservation": ["preservation", "conserve", "protect", "storage", "condition"],
            "historical_research": ["research", "history", "historical", "sources", "evidence"],
            "digital_archives": ["digital", "scanned", "online", "electronic", "access"],
            "metadata": ["metadata", "catalog", "index", "finding aid", "description"],
            "specific_collection": ["collection", "papers", "records", "fonds", "series"],
            "time_period": ["century", "decade", "period", "era", "year"],
            "technical_help": ["help", "how to", "access", "find", "search"]
        }
        
        # Count matches for each topic
        query_lower = query.lower()
        topic_scores = {}
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            topic_scores[topic] = score
            
        # Return topic with highest score, or "general" if no matches
        if max(topic_scores.values(), default=0) > 0:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        else:
            return "general"
    
    def _is_person_entity(self, entity):
        """Determine if an entity is likely a person"""
        # Simple heuristic based on capitalization and common person indicators
        if not any(char.isupper() for char in entity):
            return False
            
        person_indicators = ["Dr.", "Professor", "Mr.", "Mrs.", "Ms.", "Sir", "Lady", "King", "Queen"]
        return any(indicator in entity for indicator in person_indicators)
    
    def _calculate_exploration_depth(self, entities):
        """Calculate depth of historical exploration based on specificity"""
        # Simple heuristic based on number of entities and length
        if not entities:
            return 0
            
        avg_length = sum(len(entity) for entity in entities) / len(entities)
        depth = min(len(entities) / 3, 1.0) + min(avg_length / 20, 1.0)
        
        return round(depth, 2)
    
    def _calculate_complexity_progression(self):
        """Calculate progression of query complexity over the session"""
        if self.interaction_count < 2:
            return 0.0
        
        # Get query complexity over time
        if self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT query_complexity FROM query_analytics 
                WHERE session_id = ? ORDER BY rowid''',
                (self.session_id,)
            )
            complexity_values = [row[0] for row in cursor.fetchall()]
            conn.close()
        else:
            # CSV storage
            query_df = pd.read_csv(self.query_analytics_csv)
            session_queries = query_df[query_df.session_id == self.session_id]
            complexity_values = session_queries["query_complexity"].tolist()
        
        # Calculate progression (simple linear trend)
        if len(complexity_values) >= 2:
            # Calculate slope of complexity values
            x = list(range(len(complexity_values)))
            y = complexity_values
            
            # Simple linear regression slope calculation
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
            sum_xx = sum(x_i * x_i for x_i in x)
            
            try:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
                return round(slope, 2)
            except ZeroDivisionError:
                return 0.0
        else:
            return 0.0
