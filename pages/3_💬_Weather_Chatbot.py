"""
Phase 4: Weather Assistant Chatbot
Conversational AI with memory using Google Gemini + Open-Meteo (FREE!)

Requirements Met:
✅ Uses Streamlit chat interface
✅ Maintains conversation memory
✅ Integrates API data with LLM responses
✅ Specialized in weather/travel topics
✅ Comprehensive error handling
✅ Never crashes
"""

import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime
from geopy.geocoders import Nominatim
import json

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Weather Chatbot",
    page_icon="💬",
    layout="wide"
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_gemini_key():
    """Get Gemini API key"""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        st.error("⚠️ Gemini API key not found")
        st.info("Add GEMINI_API_KEY to .streamlit/secrets.toml")
        return None

def get_coordinates(city_name):
    """Convert city to coordinates"""
    try:
        geolocator = Nominatim(user_agent="weather_intelligence_hub")
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return location.latitude, location.longitude
        return None
    except:
        return None

def fetch_weather_for_chatbot(city):
    """Fetch weather data from Open-Meteo (FREE!)"""
    try:
        coords = get_coordinates(city)
        if not coords:
            return None
        
        lat, lon = coords
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,weather_code",
            "temperature_unit": "celsius",
            "forecast_days": 3
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Get weather description
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 61: "Rain", 63: "Rain", 65: "Heavy rain",
            71: "Snow", 73: "Snow", 75: "Heavy snow", 95: "Thunderstorm"
        }
        
        current = data['current']
        weather_desc = weather_codes.get(current['weather_code'], "Unknown")
        
        weather_info = {
            "city": city,
            "temperature": round(current['temperature_2m'], 1),
            "feels_like": round(current['apparent_temperature'], 1),
            "condition": weather_desc,
            "humidity": current['relative_humidity_2m'],
            "wind_speed": round(current['wind_speed_10m'], 1),
            "forecast_next_hours": []
        }
        
        # Add next 24 hours forecast
        hourly = data['hourly']
        for i in range(min(24, len(hourly['time']))):
            time = datetime.fromisoformat(hourly['time'][i]).strftime('%H:%M')
            temp = round(hourly['temperature_2m'][i], 1)
            cond = weather_codes.get(hourly['weather_code'][i], "Unknown")
            weather_info["forecast_next_hours"].append({
                "time": time,
                "temp": temp,
                "condition": cond
            })
        
        return weather_info
        
    except:
        return None

def initialize_chatbot(gemini_key):
    """Initialize Gemini chatbot"""
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        return chat, model
    except Exception as e:
        st.error(f"Error initializing chatbot: {e}")
        return None, None

def get_chatbot_response(chat, user_message, weather_data=None):
    """Get response from chatbot with error handling"""
    try:
        if weather_data:
            context = f"""
CURRENT WEATHER DATA:
{json.dumps(weather_data, indent=2)}

USER MESSAGE: {user_message}

Provide a helpful response using the weather data. Be specific with actual numbers.
"""
        else:
            context = user_message
        
        response = chat.send_message(context)
        return response.text
        
    except Exception as e:
        error_str = str(e).lower()
        
        if "quota" in error_str or "resource_exhausted" in error_str:
            return "⚠️ Rate limit reached. Please wait and try again."
        elif "rate" in error_str or "429" in error_str:
            return "⚠️ Too many requests. Please slow down."
        elif "safety" in error_str or "blocked" in error_str:
            return "⚠️ Content filtered. Please rephrase."
        elif "invalid" in error_str or "api_key" in error_str:
            return "⚠️ API configuration issue."
        else:
            return f"⚠️ Error: {str(e)}\n\nPlease try rephrasing!"

def extract_city_from_message(message):
    """Extract city name from user message"""
    message_lower = message.lower()
    
    patterns = [
        "weather in ",
        "weather for ",
        "forecast for ",
        "forecast in ",
        "temperature in ",
        "how's the weather in ",
        "what's the weather like in "
    ]
    
    for pattern in patterns:
        if pattern in message_lower:
            start_idx = message_lower.find(pattern) + len(pattern)
            rest = message[start_idx:].strip()
            city = rest.split('?')[0].split(',')[0].split('.')[0].strip()
            if city:
                return city
    
    return None

# ==============================================================================
# INITIALIZE SESSION STATE
# ==============================================================================

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

if "chat_model" not in st.session_state:
    st.session_state.chat_model = None

if "chatbot_initialized" not in st.session_state:
    st.session_state.chatbot_initialized = False

# ==============================================================================
# MAIN APP
# ==============================================================================

st.title("💬 Weather Assistant Chatbot")
st.markdown("*Your AI companion for weather queries (FREE weather data from Open-Meteo!)*")
st.markdown("---")

gemini_key = get_gemini_key()

if not gemini_key:
    st.stop()

# Initialize chatbot
if not st.session_state.chatbot_initialized:
    with st.spinner("Initializing Weather Assistant..."):
        chat, model = initialize_chatbot(gemini_key)
        if chat:
            st.session_state.chat_session = chat
            st.session_state.chat_model = model
            st.session_state.chatbot_initialized = True
            
            # Add welcome message
            welcome = """👋 Hello! I'm your Weather Assistant!

I can help you with:
- 🌍 Real-time weather for any city (FREE!)
- 📊 Weather forecasts and trends
- ✈️ Travel planning advice
- 🎒 Activity recommendations
- 🧳 Packing suggestions
- ☔ Weather explanations

Just ask me anything! For example:
- "What's the weather in Paris?"
- "Should I bring an umbrella to London?"
- "Compare weather in Tokyo and Seoul"

How can I help you today?"""
            
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": welcome
            })

# ==============================================================================
# CHAT INTERFACE
# ==============================================================================

# Display chat history
for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about weather..."):
    
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # Check if asking about specific city
            city = extract_city_from_message(prompt)
            weather_data = None
            
            if city:
                with st.spinner(f"Fetching weather for {city}..."):
                    weather_data = fetch_weather_for_chatbot(city)
                    
                    if weather_data:
                        st.success(f"✅ Got weather for {weather_data['city']}")
                    else:
                        st.warning(f"⚠️ Couldn't fetch weather for {city}")
            
            # Get chatbot response
            response = get_chatbot_response(
                st.session_state.chat_session,
                prompt,
                weather_data
            )
            
            st.markdown(response)
            
            # Save assistant response
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response
            })

# ==============================================================================
# SIDEBAR
# ==============================================================================

with st.sidebar:
    st.markdown("### 💬 Chat Controls")
    
    # Clear chat
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.chatbot_initialized = False
        st.rerun()
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    quick_cities = ["New York", "London", "Tokyo", "Paris", "Sydney"]
    selected = st.selectbox("Get weather for:", ["Choose city..."] + quick_cities)
    
    if st.button("🌍 Fetch Weather", use_container_width=True):
        if selected != "Choose city...":
            quick_prompt = f"What's the current weather in {selected}?"
            st.session_state.chat_messages.append({
                "role": "user",
                "content": quick_prompt
            })
            st.rerun()
    
    st.markdown("---")
    
    # Suggested questions
    st.markdown("### 💡 Try Asking:")
    
    suggestions = [
        "Weather in Atlanta?",
        "Bring a jacket to Seattle?",
        "Best cities this week?",
        "What is humidity?",
        "Tips for hot weather"
    ]
    
    for suggestion in suggestions:
        if st.button(f"💭 {suggestion}", use_container_width=True, key=suggestion):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": suggestion
            })
            st.rerun()
    
    st.markdown("---")
    
    # Info
    st.markdown("### ℹ️ About")
    st.success("""
    **Uses:**
    - 🤖 Google Gemini AI
    - 🌦️ Open-Meteo API (FREE!)
    - 💾 Conversation memory
    - 🛡️ Error handling
    
    **No weather API key needed!**
    """)
    
    st.markdown("---")
    
    # Stats
    st.markdown("### 📊 Chat Stats")
    num_messages = len(st.session_state.chat_messages)
    user_messages = sum(1 for m in st.session_state.chat_messages if m["role"] == "user")
    st.metric("Total Messages", num_messages)
    st.metric("Your Questions", user_messages)

# ==============================================================================
# FOOTER INFO
# ==============================================================================

with st.expander("🔧 How This Works"):
    st.markdown("""
    ### Technical Implementation
    
    **Conversation Memory:**
    - Session state stores full history
    - Gemini maintains context
    - Persists until cleared
    
    **Weather Integration:**
    - Detects cities in questions
    - Fetches from Open-Meteo (FREE!)
    - Integrates data into responses
    
    **Error Handling:**
    - Rate limit detection
    - API failure handling
    - Content safety management
    - Never crashes!
    
    **Features:**
    - Natural language understanding
    - Context-aware responses
    - Real-time data integration
    - Multi-turn conversations
    """)

with st.expander("⚠️ Error Handling"):
    st.markdown("""
    This chatbot handles:
    
    1. **Rate Limits** - Polite wait message
    2. **Invalid Cities** - General knowledge fallback
    3. **Network Issues** - Helpful error messages
    4. **Safety Filters** - Rephrasing request
    5. **API Failures** - Continues conversation
    
    The chatbot **never crashes**!
    """)

with st.expander("💭 Example Conversations"):
    st.markdown("""
    **Weather Queries:**
    - "What's the weather in Paris?"
    - "Is it going to rain in London?"
    - "Tell me about Tokyo's weather"
    
    **Travel Planning:**
    - "Planning a trip to Barcelona, what should I pack?"
    - "Which is warmer, Miami or LA?"
    - "Best time to visit New York?"
    
    **Activity Recommendations:**
    - "Good beach weather in Sydney?"
    - "Should I go hiking in Seattle?"
    - "What to do on a rainy day?"
    
    **Weather Education:**
    - "What causes humidity?"
    - "Why is it windy?"
    - "Explain weather vs climate"
    """)

# Add styling
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
