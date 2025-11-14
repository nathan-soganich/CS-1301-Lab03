"""
Phase 3: AI Weather Insights
Uses Google Gemini API + Open-Meteo API (FREE - NO API KEY!)

Requirements Met:
✅ Uses same API as Phase 2 (Open-Meteo)
✅ At least 2 new user inputs (different from Phase 2)
✅ Preprocesses data before LLM
✅ Generates creative, specialized text
✅ Full error handling
"""

import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import json

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AI Weather Insights",
    page_icon="🤖",
    layout="wide"
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_gemini_key():
    """Get Gemini API key from Streamlit secrets"""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except:
        st.error("⚠️ Gemini API key not found. Please add it to .streamlit/secrets.toml")
        st.info("""
        Add to .streamlit/secrets.toml:
```
        GEMINI_API_KEY = "your_gemini_key_here"
```
        
        Get your key at: https://ai.google.dev/
        """)
        return None

def get_coordinates(city_name):
    """Convert city name to coordinates"""
    try:
        geolocator = Nominatim(user_agent="weather_intelligence_hub")
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return location.latitude, location.longitude, location.address
        return None
    except Exception as e:
        st.error(f"❌ Error finding city: {e}")
        return None

def fetch_weather_data(lat, lon, temp_unit="celsius"):
    """Fetch weather data from Open-Meteo API (FREE!)"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "temperature_unit": temp_unit,
            "wind_speed_unit": "mph" if temp_unit == "fahrenheit" else "kmh",
            "timezone": "auto",
            "forecast_days": 7
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Error fetching weather: {e}")
        return None

def get_weather_description(weather_code):
    """Convert weather code to description"""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Foggy", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
        80: "Rain showers", 81: "Rain showers", 82: "Heavy rain showers",
        85: "Snow showers", 86: "Heavy snow showers", 95: "Thunderstorm",
        96: "Thunderstorm with hail", 99: "Heavy thunderstorm"
    }
    return codes.get(weather_code, "Unknown")

def process_weather_for_llm(weather_data, city_name):
    """Process weather data for LLM (data preprocessing requirement)"""
    current = weather_data['current']
    daily = weather_data['daily']
    
    processed = {
        "city": city_name,
        "current": {
            "temperature": round(current['temperature_2m'], 1),
            "feels_like": round(current['apparent_temperature'], 1),
            "humidity": current['relative_humidity_2m'],
            "wind_speed": round(current['wind_speed_10m'], 1),
            "condition": get_weather_description(current['weather_code'])
        },
        "forecast": []
    }
    
    # Process daily forecast
    for i in range(min(5, len(daily['time']))):
        processed["forecast"].append({
            "date": datetime.fromisoformat(daily['time'][i]).strftime('%A, %B %d'),
            "temp_max": round(daily['temperature_2m_max'][i], 1),
            "temp_min": round(daily['temperature_2m_min'][i], 1),
            "precipitation": round(daily['precipitation_sum'][i], 1),
            "wind_max": round(daily['wind_speed_10m_max'][i], 1),
            "condition": get_weather_description(daily['weather_code'][i])
        })
    
    return processed

def generate_ai_insights(prompt, context_data, gemini_key):
    """Use Google Gemini to generate insights"""
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = f"""You are a weather analysis expert and travel advisor.

WEATHER DATA:
{json.dumps(context_data, indent=2)}

USER REQUEST:
{prompt}

Provide a detailed, informative, and practical response. Be specific and use the actual data provided.
Make your response engaging and easy to read.
"""
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "rate" in error_msg:
            return "⚠️ API rate limit reached. Please wait a moment and try again."
        elif "safety" in error_msg:
            return "⚠️ Content filtered. Please rephrase your request."
        else:
            return f"⚠️ Error: {e}"

# ==============================================================================
# MAIN APP
# ==============================================================================

st.title("🤖 AI Weather Insights")
st.markdown("*Powered by Google Gemini LLM + Open-Meteo API (100% FREE!)*")
st.markdown("---")

gemini_key = get_gemini_key()

if not gemini_key:
    st.stop()

# ==============================================================================
# INSIGHT TYPE SELECTION
# ==============================================================================

st.markdown("## 🎯 Choose Your Analysis Type")

insight_type = st.radio(
    "What would you like to analyze?",
    options=[
        "🌍 City Comparison & Travel Advice",
        "🎒 Activity Recommendations",
        "📝 Weather Report Article",
        "🧳 Smart Packing List"
    ],
    horizontal=True
)

st.markdown("---")

# ==============================================================================
# MODE 1: CITY COMPARISON
# ==============================================================================

if "City Comparison" in insight_type:
    st.markdown("## 🌍 Multi-City Weather Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cities_input = st.text_area(
            "Enter cities to compare (one per line)",
            value="Atlanta\nNew York\nMiami",
            height=100,
            help="Enter 2-4 cities"
        )
        cities = [c.strip() for c in cities_input.split('\n') if c.strip()]
        
        if len(cities) < 2:
            st.warning("Enter at least 2 cities")
        elif len(cities) > 4:
            st.warning("Max 4 cities")
            cities = cities[:4]
    
    with col2:
        travel_purpose = st.selectbox(
            "Purpose of travel",
            options=[
                "🏖️ Beach vacation",
                "⛷️ Winter sports",
                "🏙️ City sightseeing",
                "🏕️ Outdoor activities",
                "💼 Business trip",
                "🎓 Academic conference"
            ]
        )
        
        travel_timeframe = st.selectbox(
            "When are you traveling?",
            options=[
                "This week",
                "Next week",
                "In 2 weeks",
                "This weekend",
                "Next weekend"
            ]
        )
    
    if st.button("🔍 Generate Comparison & Travel Advice", type="primary"):
        if len(cities) >= 2:
            with st.spinner("Fetching weather data and generating insights..."):
                all_city_data = {}
                
                for city in cities:
                    coords = get_coordinates(city)
                    if coords:
                        lat, lon, full_loc = coords
                        weather = fetch_weather_data(lat, lon)
                        if weather:
                            all_city_data[city] = process_weather_for_llm(weather, city)
                
                if len(all_city_data) >= 2:
                    prompt = f"""
Compare weather for these cities and provide travel advice:

Cities: {', '.join(all_city_data.keys())}
Travel Purpose: {travel_purpose}
Timeframe: {travel_timeframe}

Provide:
1. Detailed weather comparison
2. Pros and cons of each destination
3. Best city for {travel_purpose}
4. Specific recommendations
5. What to expect and prepare
"""
                    
                    insights = generate_ai_insights(prompt, all_city_data, gemini_key)
                    
                    st.markdown("---")
                    st.markdown("## 📊 AI-Generated Analysis")
                    
                    with st.expander("📋 Weather Data Summary"):
                        for city, data in all_city_data.items():
                            st.markdown(f"### {city}")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Current Temp", f"{data['current']['temperature']}°")
                            with col2:
                                st.metric("Condition", data['current']['condition'])
                            with col3:
                                st.metric("Humidity", f"{data['current']['humidity']}%")
                    
                    st.markdown("### 🤖 AI Analysis")
                    st.markdown(insights)
                else:
                    st.error("Couldn't fetch data for enough cities")

# ==============================================================================
# MODE 2: ACTIVITY RECOMMENDATIONS
# ==============================================================================

elif "Activity" in insight_type:
    st.markdown("## 🎒 Weather-Based Activity Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        activity_city = st.text_input(
            "🌍 Enter your city",
            value="Atlanta"
        )
    
    with col2:
        activity_pref = st.multiselect(
            "🎯 Activities that interest you",
            options=[
                "Outdoor sports",
                "Indoor activities",
                "Water activities",
                "Photography",
                "Dining & restaurants",
                "Shopping",
                "Cultural events",
                "Nature & hiking"
            ],
            default=["Outdoor sports", "Dining & restaurants"]
        )
    
    activity_days = st.slider(
        "📅 Planning for how many days?",
        min_value=1,
        max_value=7,
        value=3
    )
    
    if st.button("🎨 Generate Activity Plan", type="primary"):
        with st.spinner(f"Analyzing weather for {activity_city}..."):
            coords = get_coordinates(activity_city)
            if coords:
                lat, lon, _ = coords
                weather = fetch_weather_data(lat, lon)
                if weather:
                    weather_context = process_weather_for_llm(weather, activity_city)
                    
                    prompt = f"""
Create a detailed activity plan based on weather:

Location: {activity_city}
Interests: {', '.join(activity_pref)}
Duration: {activity_days} days

Provide:
1. Day-by-day activity recommendations
2. Best times for outdoor vs indoor
3. What to wear each day
4. Activities to avoid and alternatives
5. Pro tips for the weather
"""
                    
                    insights = generate_ai_insights(prompt, weather_context, gemini_key)
                    
                    st.markdown("---")
                    st.markdown("## 🎯 Your Personalized Activity Plan")
                    
                    with st.expander("☁️ Weather Overview"):
                        st.markdown(f"**Current in {activity_city}:**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Temp", f"{weather_context['current']['temperature']}°")
                        with col2:
                            st.metric("Condition", weather_context['current']['condition'])
                        with col3:
                            st.metric("Humidity", f"{weather_context['current']['humidity']}%")
                        with col4:
                            st.metric("Wind", f"{weather_context['current']['wind_speed']} km/h")
                    
                    st.markdown("### 🤖 AI-Generated Plan")
                    st.markdown(insights)

# ==============================================================================
# MODE 3: WEATHER REPORT
# ==============================================================================

elif "Article" in insight_type:
    st.markdown("## 📝 AI-Generated Weather Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_city = st.text_input(
            "🌍 City for weather report",
            value="Atlanta"
        )
    
    with col2:
        report_style = st.selectbox(
            "📰 Report style",
            options=[
                "Professional Weather Broadcast",
                "Casual Blog Post",
                "Scientific Analysis",
                "Travel Newsletter",
                "Social Media Update"
            ]
        )
    
    focus_areas = st.multiselect(
        "🎯 Report focus",
        options=[
            "Temperature trends",
            "Precipitation likelihood",
            "Wind conditions",
            "Travel impact",
            "Outdoor activities",
            "Health advisories"
        ],
        default=["Temperature trends", "Travel impact"]
    )
    
    if st.button("✍️ Generate Weather Report", type="primary"):
        with st.spinner("Writing report..."):
            coords = get_coordinates(report_city)
            if coords:
                lat, lon, _ = coords
                weather = fetch_weather_data(lat, lon)
                if weather:
                    weather_context = process_weather_for_llm(weather, report_city)
                    
                    prompt = f"""
Write a weather report in style: {report_style}

Location: {report_city}
Focus: {', '.join(focus_areas)}

Include:
1. Compelling headline
2. Current conditions overview
3. Detailed forecast breakdown
4. Key weather patterns
5. Practical advice
6. Concluding summary

Make it professional yet accessible.
"""
                    
                    insights = generate_ai_insights(prompt, weather_context, gemini_key)
                    
                    st.markdown("---")
                    st.markdown("## 📰 Your Weather Report")
                    
                    with st.expander("📊 Key Data"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Current", f"{weather_context['current']['temperature']}°")
                        with col2:
                            temps = [f['temp_max'] for f in weather_context['forecast']]
                            st.metric("Avg High", f"{sum(temps)/len(temps):.1f}°")
                        with col3:
                            st.metric("Condition", weather_context['forecast'][0]['condition'])
                    
                    st.markdown(insights)
                    
                    st.download_button(
                        label="📥 Download Report",
                        data=insights,
                        file_name=f"weather_report_{report_city}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

# ==============================================================================
# MODE 4: PACKING LIST
# ==============================================================================

elif "Packing" in insight_type:
    st.markdown("## 🧳 Smart Packing List Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        pack_city = st.text_input(
            "🌍 Destination",
            value="New York"
        )
        
        trip_duration = st.number_input(
            "📅 Trip duration (days)",
            min_value=1,
            max_value=14,
            value=5
        )
    
    with col2:
        trip_type = st.selectbox(
            "🎯 Trip type",
            options=[
                "Business",
                "Leisure/Vacation",
                "Adventure/Outdoor",
                "Beach",
                "Winter/Ski",
                "City exploration",
                "Family trip"
            ]
        )
        
        special_needs = st.multiselect(
            "⚙️ Special considerations",
            options=[
                "Formal events",
                "Athletic activities",
                "Swimming",
                "Hiking",
                "Photography",
                "Work from hotel"
            ]
        )
    
    if st.button("🎒 Generate Packing List", type="primary"):
        with st.spinner("Creating packing list..."):
            coords = get_coordinates(pack_city)
            if coords:
                lat, lon, _ = coords
                weather = fetch_weather_data(lat, lon)
                if weather:
                    weather_context = process_weather_for_llm(weather, pack_city)
                    
                    prompt = f"""
Create a comprehensive packing list:

Destination: {pack_city}
Duration: {trip_duration} days
Trip Type: {trip_type}
Special Needs: {', '.join(special_needs) if special_needs else 'None'}

Provide:
1. Clothing (specific quantities)
2. Footwear
3. Weather-specific items
4. Accessories
5. Special items for {trip_type}
6. Don't-forget essentials
7. Pro packing tips

Be practical and specific to the weather.
"""
                    
                    insights = generate_ai_insights(prompt, weather_context, gemini_key)
                    
                    st.markdown("---")
                    st.markdown("## 🧳 Your Packing List")
                    
                    with st.expander("🌤️ Weather During Trip"):
                        st.markdown(f"**Forecast for {pack_city}:**")
                        temps = [f['temp_max'] for f in weather_context['forecast']] + \
                               [f['temp_min'] for f in weather_context['forecast']]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Temp Range", f"{min(temps):.0f}° - {max(temps):.0f}°")
                        with col2:
                            conditions = [f['condition'] for f in weather_context['forecast']]
                            st.metric("Conditions", ", ".join(set(conditions)))
                        with col3:
                            st.metric("Humidity", f"{weather_context['current']['humidity']}%")
                    
                    st.markdown("### 🤖 AI-Generated List")
                    st.markdown(insights)
                    
                    st.download_button(
                        label="📥 Download List",
                        data=insights,
                        file_name=f"packing_{pack_city}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )

# ==============================================================================
# SIDEBAR
# ==============================================================================

with st.sidebar:
    st.markdown("### 🤖 AI Weather Insights")
    st.markdown("---")
    

    
    st.markdown("---")
    
    st.markdown("### ⚡ Features")
    st.markdown("""
    - 🌍 Multi-city comparison
    - 🎯 Personalized recommendations
    - 📝 Multiple formats
    - 🧠 AI-powered insights
    - 💾 Downloadable reports
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Be specific with inputs
    - Try different modes
    - Download useful reports
    - Compare cities
    """)
