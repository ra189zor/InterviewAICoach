import os
import json
import time
from dotenv import load_dotenv, find_dotenv
import streamlit as st
from docore_ai import intelligence_profiler
import openai
import traceback
from functools import wraps
from datetime import datetime, timedelta

# Constants
DIFFICULTY_LEVELS = ["junior", "Mid", "senior"]
DEFAULT_DIFFICULTY = "Mid"
CACHE_TTL = 3600  # Cache time-to-live in seconds (1 hour)

# Load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path=dotenv_path, override=True)

# Validate required environment variables
required_env_vars = ["OPENAI_API_KEY", "MODEL_PROVIDER", "MODEL_NAME"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Implement a time-based cache decorator
def timed_lru_cache(seconds=CACHE_TTL, maxsize=128):
    """LRU Cache decorator with time expiration."""
    def decorator(func):
        # Using a dictionary to store function results with timestamps
        cache = {}
        timestamps = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            current_time = datetime.now()
            
            # Check if cached result exists and is still valid
            if key in cache and (current_time - timestamps[key]).total_seconds() < seconds:
                return cache[key]
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = current_time
            
            return result
        
        # Add a method to clear the cache
        wrapper.clear_cache = lambda: cache.clear() and timestamps.clear()
        
        return wrapper
    return decorator

def extract_optimized_prompt(intelligence_response):
    """Extract the optimized prompt from the intelligence_profiler response."""
    if not isinstance(intelligence_response, dict) or 'response' not in intelligence_response:
        return None
    
    response_value = intelligence_response.get('response')
    
    # Handle string response (attempt JSON parsing)
    if isinstance(response_value, str):
        try:
            parsed_response = json.loads(response_value)
            if isinstance(parsed_response, dict):
                response_data = parsed_response
            else:
                return None
        except json.JSONDecodeError:
            return None
    # Handle dict response
    elif isinstance(response_value, dict):
        response_data = response_value
    else:
        return None
    
    # Extract optimized prompt if available
    return response_data.get('optimized_response') if isinstance(response_data, dict) else None

@timed_lru_cache(seconds=CACHE_TTL, maxsize=100)
def get_intelligence_profile(raw_prompt, job_title):
    """Get intelligence profile with time-based caching to reduce API calls."""
    try:
        return intelligence_profiler(
            raw_prompt,
            job_title,
            os.getenv("MODEL_PROVIDER"),
            os.getenv("MODEL_NAME")
        )
    except Exception as e:
        print(f"Error in intelligence_profiler: {str(e)}")
        return None

def call_openai_api(system_message, user_message, max_tokens=100, temperature=0.7, response_format=None):
    """Centralized function for OpenAI API calls with optional JSON response format."""
    try:
        params = {
            "model": os.getenv("MODEL_NAME"),
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens,
            "n": 1,
            "temperature": temperature
        }
        
        # Add response_format if specified
        if response_format:
            params["response_format"] = response_format
        
        completion = openai.chat.completions.create(**params)
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        traceback.print_exc()
        return None

def generate_question(job_title, difficulty):
    """Generate an interview question based on job title and difficulty."""
    raw_prompt = f"Generate one interview question suitable to ask a candidate applying for a {difficulty}-level {job_title} position."
    
    try:
        # Get intelligence profile (cached)
        intelligence_response = get_intelligence_profile(raw_prompt, job_title)
        if not intelligence_response:
            return "Sorry, I couldn't connect to the intelligence profiler."
        
        # Extract optimized prompt
        optimized_prompt = extract_optimized_prompt(intelligence_response)
        
        if optimized_prompt:
            # Generate question using OpenAI
            system_message = f"You are an AI simulating an interview for a {job_title} role. Ask one relevant interview question based on the user prompt."
            question = call_openai_api(system_message, optimized_prompt, max_tokens=70)
            
            if question:
                # Clean up the response
                for prefix in ["Okay, here's a question:", "Here's one:", "Here's a question:"]:
                    if question.startswith(prefix):
                        question = question[len(prefix):].strip()
                return question
            else:
                return "Sorry, I couldn't generate a question at this time."
        else:
            error_message = f"Failed to extract optimized prompt from intelligence_profiler response."
            st.error(error_message)
            return "Sorry, I couldn't optimize the prompt via DoCoreAI."
            
    except Exception as e:
        st.error(f"Error generating question: {str(e)}")
        traceback.print_exc()
        return "Sorry, I couldn't generate a question at this time."

def generate_feedback(question, answer):
    """Generate feedback for a candidate's answer and recommend next difficulty level."""
    job_title = st.session_state.get('job_title', 'Unknown Job')
    
    raw_prompt = (
        f"Question asked: '{question}'. Candidate's answer: '{answer}'. "
        f"Provide feedback for the candidate's answer and recommend the next question difficulty."
        f"Respond in JSON format with two fields: 'feedback' (a one-sentence evaluation) and "
        f"'recommendation' (must be one of: easier, same, harder)."
    )
    
    try:
        # Get intelligence profile (cached)
        intelligence_response = get_intelligence_profile(raw_prompt, job_title)
        if not intelligence_response:
            return "Sorry, I couldn't connect to the intelligence profiler.", DEFAULT_DIFFICULTY
        
        # Extract optimized prompt
        optimized_prompt = extract_optimized_prompt(intelligence_response)
        
        if optimized_prompt:
            # Generate feedback using OpenAI with JSON response format
            system_message = (
                f"You are an AI providing feedback on a candidate's interview answer for a {job_title} role. "
                f"Respond with a JSON object containing two fields: 'feedback' (a concise sentence evaluating their answer) "
                f"and 'recommendation' (which must be exactly one of: 'easier', 'same', or 'harder')."
            )
            
            # Request JSON response
            json_response = call_openai_api(
                system_message, 
                optimized_prompt,
                response_format={"type": "json_object"}
            )
            
            if not json_response:
                return "Sorry, I couldn't generate feedback at this time.", DEFAULT_DIFFICULTY
            
            try:
                # Parse JSON response
                response_data = json.loads(json_response)
                
                # Extract feedback and recommendation
                feedback = response_data.get('feedback', "No feedback provided.")
                recommendation = response_data.get('recommendation', DEFAULT_DIFFICULTY).lower()
                
                # Validate recommendation
                if recommendation not in DIFFICULTY_LEVELS:
                    recommendation = DEFAULT_DIFFICULTY
                    st.warning(f"Invalid recommendation value: '{recommendation}'. Using '{DEFAULT_DIFFICULTY}' instead.")
                
                return feedback, recommendation
                
            except json.JSONDecodeError as e:
                st.warning(f"Failed to parse feedback JSON: {str(e)}. Feedback text: {json_response}")
                # Fall back to string parsing if JSON parsing fails
                feedback = json_response
                recommendation = DEFAULT_DIFFICULTY
                
                # Try to extract recommendation from text if JSON parsing failed
                for level in DIFFICULTY_LEVELS:
                    if level in json_response.lower():
                        recommendation = level
                        break
                        
                return feedback, recommendation
        else:
            error_message = "Failed to extract optimized prompt from intelligence_profiler response."
            st.error(error_message)
            return "Sorry, couldn't optimize feedback prompt via DoCoreAI.", DEFAULT_DIFFICULTY
            
    except Exception as e:
        st.error(f"Error generating feedback: {str(e)}")
        traceback.print_exc()
        return "Sorry, I couldn't generate feedback at this time.", DEFAULT_DIFFICULTY

# Function to get job title safely from session state
def get_job_title():
    """Safely get job title from session state or return a default value."""
    if 'job_title' not in st.session_state:
        st.session_state['job_title'] = "Software Developer"  
    return st.session_state['job_title']

# Clear cache function
def clear_cache():
    """Clear the time-based cache for the intelligence profiler."""
    get_intelligence_profile.clear_cache()
    st.success("Cache cleared successfully!")

# This comment triggers CodeRabbit to review the file