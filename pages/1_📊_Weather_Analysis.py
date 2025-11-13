"""
Phase 2: Weather Analysis Dashboard
Uses Open-Meteo API (COMPLETELY FREE - NO API KEY NEEDED!)

Requirements Met:
✅ Uses external web API (Open-Meteo)
✅ At least 2 user inputs (city, temperature unit, forecast days)
✅ Data processing without LLM
✅ Dynamic charts and visualizations
✅ Error handling for API calls
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Weather Analysis",
    page_icon="📊",
    layout="wide"
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def fallback_city_lookup(city_name):
    """
    Fallback function to lookup cities from hardcoded database
    Returns: (latitude, longitude, formatted_name) or None
    """
    # Comprehensive city database
    city_database = {
        # US Cities
        "atlanta": (33.7490, -84.3880, "Atlanta, Georgia, USA"),
        "new york": (40.7128, -74.0060, "New York, New York, USA"),
        "los angeles": (34.0522, -118.2437, "Los Angeles, California, USA"),
        "chicago": (41.8781, -87.6298, "Chicago, Illinois, USA"),
        "houston": (29.7604, -95.3698, "Houston, Texas, USA"),
        "miami": (25.7617, -80.1918, "Miami, Florida, USA"),
        "boston": (42.3601, -71.0589, "Boston, Massachusetts, USA"),
        "seattle": (47.6062, -122.3321, "Seattle, Washington, USA"),
        "san francisco": (37.7749, -122.4194, "San Francisco, California, USA"),
        "denver": (39.7392, -104.9903, "Denver, Colorado, USA"),
        "washington": (38.9072, -77.0369, "Washington, D.C., USA"),
        "philadelphia": (39.9526, -75.1652, "Philadelphia, Pennsylvania, USA"),
        "phoenix": (33.4484, -112.0740, "Phoenix, Arizona, USA"),
        "las vegas": (36.1699, -115.1398, "Las Vegas, Nevada, USA"),
        "portland": (45.5152, -122.6784, "Portland, Oregon, USA"),
        "austin": (30.2672, -97.7431, "Austin, Texas, USA"),
        "nashville": (36.1627, -86.7816, "Nashville, Tennessee, USA"),
        
        # International Cities
        "london": (51.5074, -0.1278, "London, United Kingdom"),
        "paris": (48.8566, 2.3522, "Paris, France"),
        "tokyo": (35.6762, 139.6503, "Tokyo, Japan"),
        "sydney": (33.8688, 151.2093, "Sydney, Australia"),
        "toronto": (43.6532, -79.3832, "Toronto, Canada"),
        "berlin": (52.5200, 13.4050, "Berlin, Germany"),
        "rome": (41.9028, 12.4964, "Rome, Italy"),
        "madrid": (40.4168, -3.7038, "Madrid, Spain"),
        "amsterdam": (52.3676, 4.9041, "Amsterdam, Netherlands"),
        "dubai": (25.2048, 55.2708, "Dubai, UAE"),
        "singapore": (1.3521, 103.8198, "Singapore"),
        "hong kong": (22.3193, 114.1694, "Hong Kong"),
        "moscow": (55.7558, 37.6173, "Moscow, Russia"),
        "beijing": (39.9042, 116.4074, "Beijing, China"),
        "mumbai": (19.0760, 72.8777, "Mumbai, India"),
        "rio de janeiro": (-22.9068, -43.1729, "Rio de Janeiro, Brazil"),
        "barcelona": (41.3851, 2.1734, "Barcelona, Spain"),
        "melbourne": (-37.8136, 144.9631, "Melbourne, Australia"),
        "vancouver": (49.2827, -123.1207, "Vancouver, Canada"),
        "bangkok": (13.7563, 100.5018, "Bangkok, Thailand"),
    }
    
    # Normalize input
    city_lower = city_name.lower().strip()
    
    # Check if city exists in database
    if city_lower in city_database:
        lat, lon, formatted_name = city_database[city_lower]
        return lat, lon, formatted_name
    
    # City not found
    st.error(f"❌ City '{city_name}' not found in database.")
    st.info("""
    💡 **Try these cities that are guaranteed to work:**
    
    **US:** Atlanta, New York, Los Angeles, Chicago, Miami, Boston, Seattle, San Francisco, Denver, Austin
    
    **International:** London, Paris, Tokyo, Sydney, Toronto, Berlin, Rome, Madrid, Dubai, Singapore, Barcelona
    
    *Tip: Use simple city names (e.g., "Paris" instead of "Paris, France")*
    """)
    return None
def get_coordinates(city_name):
    """Use OpenCage API for geocoding"""
    # Get API key from secrets
    try:
        api_key = st.secrets.get("OPENCAGE_API_KEY", "")
    except:
        api_key = ""
    
    if api_key:
        try:
            url = "https://api.opencagedata.com/geocode/v1/json"
            params = {
                "q": city_name,
                "key": api_key,
                "limit": 1
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['results']:
                result = data['results'][0]
                lat = result['geometry']['lat']
                lon = result['geometry']['lng']
                formatted = result['formatted']
                return lat, lon, formatted
        except:
            pass
    
    # Fallback to city database
    return fallback_city_lookup(city_name)
def fetch_current_weather(lat, lon, temperature_unit="celsius"):
    """
    Fetch current weather data using Open-Meteo API 
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        temperature_unit (str): 'celsius' or 'fahrenheit'
        
    Returns:
        dict: Weather data or None if error
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m",
            "temperature_unit": temperature_unit,
            "wind_speed_unit": "mph" if temperature_unit == "fahrenheit" else "kmh",
            "timezone": "auto"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching weather data: {e}")
        return None

def fetch_forecast(lat, lon, temperature_unit="celsius", days=7):
    """ 
    Fetch forecast data using Open-Meteo API
    Args:
        lat (float): Latitude
        lon (float): Longitude
        temperature_unit (str): 'celsius' or 'fahrenheit'
        days (int): Number of forecast days
        
    Returns:
        dict: Forecast data or None if error
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weather_code,cloud_cover,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "temperature_unit": temperature_unit,
            "wind_speed_unit": "mph" if temperature_unit == "fahrenheit" else "kmh",
            "timezone": "auto",
            "forecast_days": days
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching forecast data: {e}")
        return None

def get_weather_description(weather_code):
    """Convert WMO weather code to description"""
    weather_codes = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"),
        48: ("Foggy", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Moderate drizzle", "🌦️"),
        55: ("Dense drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"),
        63: ("Moderate rain", "🌧️"),
        65: ("Heavy rain", "🌧️"),
        71: ("Slight snow", "🌨️"),
        73: ("Moderate snow", "🌨️"),
        75: ("Heavy snow", "❄️"),
        77: ("Snow grains", "❄️"),
        80: ("Slight rain showers", "🌦️"),
        81: ("Moderate rain showers", "🌧️"),
        82: ("Violent rain showers", "⛈️"),
        85: ("Slight snow showers", "🌨️"),
        86: ("Heavy snow showers", "❄️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with hail", "⛈️"),
        99: ("Thunderstorm with hail", "⛈️")
    }
    return weather_codes.get(weather_code, ("Unknown", "🌡️"))

def process_hourly_forecast(forecast_data, days=5):
    """Process hourly forecast data into DataFrame"""
    if not forecast_data or 'hourly' not in forecast_data:
        return None
    
    hourly = forecast_data['hourly']
    
    # Limit to requested days (24 hours per day)
    hours_to_show = days * 24
    
    data_list = []
    for i in range(min(hours_to_show, len(hourly['time']))):
        weather_desc, weather_emoji = get_weather_description(hourly['weather_code'][i])
        
        data_list.append({
            'datetime': pd.to_datetime(hourly['time'][i]),
            'date': pd.to_datetime(hourly['time'][i]).strftime('%Y-%m-%d'),
            'time': pd.to_datetime(hourly['time'][i]).strftime('%H:%M'),
            'temperature': hourly['temperature_2m'][i],
            'feels_like': hourly['apparent_temperature'][i],
            'humidity': hourly['relative_humidity_2m'][i],
            'precipitation_prob': hourly['precipitation_probability'][i],
            'wind_speed': hourly['wind_speed_10m'][i],
            'clouds': hourly['cloud_cover'][i],
            'weather_code': hourly['weather_code'][i],
            'weather_desc': weather_desc,
            'weather_emoji': weather_emoji
        })
    
    return pd.DataFrame(data_list)

# ==============================================================================
# MAIN APP
# ==============================================================================

st.title("📊 Weather Analysis Dashboard")
st.markdown("*Real-time weather data from **Open-Meteo** (Completely FREE - No API Key Required!)*")
st.markdown("---")

# ==============================================================================
# USER INPUTS (Requirement: At least 2 user inputs)
# ==============================================================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    city_input = st.text_input(
        "🌍 Enter City Name",
        value="Atlanta",
        help="Enter any city name worldwide"
    )

with col2:
    temp_unit_display = st.selectbox(
        "🌡️ Temperature Unit",
        options=["Celsius (°C)", "Fahrenheit (°F)"],
        help="Choose your preferred temperature unit"
    )
    temp_unit = "celsius" if "Celsius" in temp_unit_display else "fahrenheit"
    unit_symbol = "°C" if temp_unit == "celsius" else "°F"
    wind_unit = "km/h" if temp_unit == "celsius" else "mph"

with col3:
    forecast_days = st.slider(
        "📅 Forecast Days",
        min_value=1,
        max_value=7,
        value=3,
        help="Number of days to show in forecast (1-7)"
    )

# Fetch button
if st.button("🔍 Fetch Weather Data", type="primary"):
    with st.spinner(f"Finding {city_input}..."):
        
        # Get coordinates for city
        coords = get_coordinates(city_input)
        
        if coords:
            lat, lon, full_location = coords
            
            with st.spinner(f"Fetching weather data..."):
                # Fetch current weather
                current_weather = fetch_current_weather(lat, lon, temp_unit)
                
                # Fetch forecast
                forecast_data = fetch_forecast(lat, lon, temp_unit, forecast_days)
                
                if current_weather and forecast_data:
                    # Store in session state
                    st.session_state['current_weather'] = current_weather
                    st.session_state['forecast_data'] = forecast_data
                    st.session_state['location'] = full_location
                    st.session_state['city_name'] = city_input
                    st.session_state['unit_symbol'] = unit_symbol
                    st.session_state['wind_unit'] = wind_unit
                    st.session_state['forecast_days'] = forecast_days
                    st.success(f"✅ Successfully fetched weather data for {city_input}!")
        else:
            st.error(f"❌ City '{city_input}' not found. Please check the spelling and try again.")

# ==============================================================================
# DISPLAY RESULTS
# ==============================================================================

if 'current_weather' in st.session_state and 'forecast_data' in st.session_state:
    current = st.session_state['current_weather']
    forecast = st.session_state['forecast_data']
    location = st.session_state['location']
    city_name = st.session_state.get('city_name', city_input)
    unit_symbol = st.session_state['unit_symbol']
    wind_unit = st.session_state['wind_unit']
    forecast_days = st.session_state['forecast_days']
    
    st.markdown("---")
    
    # ==============================================================================
    # CURRENT WEATHER SECTION
    # ==============================================================================
    
    st.markdown(f"## 🌤️ Current Weather in {city_name}")
    st.caption(f"📍 {location}")
    
    # Main weather display
    current_data = current['current']
    weather_desc, weather_emoji = get_weather_description(current_data['weather_code'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🌡️ Temperature",
            value=f"{current_data['temperature_2m']:.1f}{unit_symbol}",
            delta=f"Feels like {current_data['apparent_temperature']:.1f}{unit_symbol}"
        )
    
    with col2:
        st.metric(
            label=f"{weather_emoji} Condition",
            value=weather_desc,
            delta=None
        )
    
    with col3:
        st.metric(
            label="💧 Humidity",
            value=f"{current_data['relative_humidity_2m']}%"
        )
    
    with col4:
        st.metric(
            label="🌬️ Wind Speed",
            value=f"{current_data['wind_speed_10m']:.1f} {wind_unit}"
        )
    
    # Additional details
    with st.expander("📋 Additional Weather Details"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Wind Direction:** {current_data['wind_direction_10m']}°")
            st.write(f"**Cloud Cover:** {current_data['cloud_cover']}%")
        
        with col2:
            st.write(f"**Precipitation:** {current_data['precipitation']} mm")
            st.write(f"**Latitude:** {current['latitude']:.4f}")
        
        with col3:
            st.write(f"**Longitude:** {current['longitude']:.4f}")
            st.write(f"**Timezone:** {current['timezone']}")
    
    st.markdown("---")
    
    # ==============================================================================
    # FORECAST SECTION WITH DATA PROCESSING
    # ==============================================================================
    
    st.markdown(f"## 📈 {forecast_days}-Day Weather Forecast")
    
    # Process hourly forecast data
    df_forecast = process_hourly_forecast(forecast, days=forecast_days)
    
    if df_forecast is not None and not df_forecast.empty:
        
        # ==============================================================================
        # DYNAMIC CHART 1: Temperature Trends (Line Chart)
        # ==============================================================================
        
        st.markdown("### 🌡️ Temperature Trends")
        
        fig_temp = go.Figure()
        
        # Add temperature line
        fig_temp.add_trace(go.Scatter(
            x=df_forecast['datetime'],
            y=df_forecast['temperature'],
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=6)
        ))
        
        # Add feels like line
        fig_temp.add_trace(go.Scatter(
            x=df_forecast['datetime'],
            y=df_forecast['feels_like'],
            mode='lines',
            name='Feels Like',
            line=dict(color='#4ECDC4', width=2, dash='dash')
        ))
        
        fig_temp.update_layout(
            title=f"Temperature Forecast for {city_name}",
            xaxis_title="Date & Time",
            yaxis_title=f"Temperature ({unit_symbol})",
            hovermode='x unified',
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # ==============================================================================
        # DATA ANALYSIS: Temperature Statistics
        # ==============================================================================
        
        st.markdown("### 📊 Temperature Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_temp = df_forecast['temperature'].mean()
            st.metric("Average Temp", f"{avg_temp:.1f}{unit_symbol}")
        
        with col2:
            max_temp = df_forecast['temperature'].max()
            st.metric("Highest Temp", f"{max_temp:.1f}{unit_symbol}")
        
        with col3:
            min_temp = df_forecast['temperature'].min()
            st.metric("Lowest Temp", f"{min_temp:.1f}{unit_symbol}")
        
        with col4:
            temp_range = max_temp - min_temp
            st.metric("Temperature Range", f"{temp_range:.1f}{unit_symbol}")
        
        # ==============================================================================
        # DYNAMIC CHART 2: Weather Conditions Distribution (Bar Chart)
        # ==============================================================================
        
        st.markdown("### ☁️ Weather Conditions Distribution")
        
        # Count weather conditions
        weather_counts = df_forecast['weather_desc'].value_counts().reset_index()
        weather_counts.columns = ['Condition', 'Count']
        
        # Add emojis
        weather_counts['Emoji'] = df_forecast.groupby('weather_desc')['weather_emoji'].first().values
        weather_counts['Display'] = weather_counts['Emoji'] + ' ' + weather_counts['Condition']
        
        # Create bar chart
        fig_conditions = px.bar(
            weather_counts,
            x='Display',
            y='Count',
            title=f"Weather Conditions Over {forecast_days} Days",
            labels={'Display': 'Weather Condition', 'Count': 'Number of Hours'},
            color='Count',
            color_continuous_scale='Blues'
        )
        
        fig_conditions.update_layout(
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_conditions, use_container_width=True)
        
        # ==============================================================================
        # DYNAMIC CHART 3: Humidity & Wind Analysis (Multi-line Chart)
        # ==============================================================================
        
        st.markdown("### 💨 Humidity & Wind Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Humidity chart
            fig_humidity = go.Figure()
            fig_humidity.add_trace(go.Scatter(
                x=df_forecast['datetime'],
                y=df_forecast['humidity'],
                mode='lines+markers',
                name='Humidity',
                fill='tozeroy',
                line=dict(color='#45B7D1', width=2)
            ))
            
            fig_humidity.update_layout(
                title="Humidity Levels",
                xaxis_title="Date & Time",
                yaxis_title="Humidity (%)",
                height=300,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        with col2:
            # Wind speed chart
            fig_wind = go.Figure()
            fig_wind.add_trace(go.Scatter(
                x=df_forecast['datetime'],
                y=df_forecast['wind_speed'],
                mode='lines+markers',
                name='Wind Speed',
                fill='tozeroy',
                line=dict(color='#96CEB4', width=2)
            ))
            
            fig_wind.update_layout(
                title="Wind Speed",
                xaxis_title="Date & Time",
                yaxis_title=f"Wind Speed ({wind_unit})",
                height=300,
                template="plotly_white"
            )
            
            st.plotly_chart(fig_wind, use_container_width=True)
        
        # ==============================================================================
        # DYNAMIC CHART 4: Precipitation Probability
        # ==============================================================================
        
        st.markdown("### 🌧️ Precipitation Probability")
        
        fig_precip = go.Figure()
        fig_precip.add_trace(go.Scatter(
            x=df_forecast['datetime'],
            y=df_forecast['precipitation_prob'],
            mode='lines',
            name='Precipitation Chance',
            fill='tozeroy',
            line=dict(color='#6C5CE7', width=2)
        ))
        
        fig_precip.update_layout(
            title="Chance of Precipitation",
            xaxis_title="Date & Time",
            yaxis_title="Probability (%)",
            height=300,
            template="plotly_white"
        )
        
        st.plotly_chart(fig_precip, use_container_width=True)
        
        # ==============================================================================
        # DETAILED FORECAST TABLE
        # ==============================================================================
        
        st.markdown("### 📅 Daily Summary")
        
        # Get daily data from forecast
        if 'daily' in forecast:
            daily_data = forecast['daily']
            daily_df = pd.DataFrame({
                'Date': [datetime.fromisoformat(d).strftime('%A, %b %d') for d in daily_data['time']],
                'Max Temp': [f"{t:.1f}{unit_symbol}" for t in daily_data['temperature_2m_max']],
                'Min Temp': [f"{t:.1f}{unit_symbol}" for t in daily_data['temperature_2m_min']],
                'Precipitation': [f"{p:.1f} mm" for p in daily_data['precipitation_sum']],
                'Max Wind': [f"{w:.1f} {wind_unit}" for w in daily_data['wind_speed_10m_max']],
                'Condition': [get_weather_description(wc)[0] for wc in daily_data['weather_code']],
                '': [get_weather_description(wc)[1] for wc in daily_data['weather_code']]
            })
            
            st.dataframe(daily_df, use_container_width=True, hide_index=True)
        
        # ==============================================================================
        # WEATHER INSIGHTS (Data Analysis without LLM)
        # ==============================================================================
        
        st.markdown("### 💡 Weather Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Temperature Analysis:**
            - Temperature range: {min_temp:.1f}{unit_symbol} to {max_temp:.1f}{unit_symbol}
            - Average temperature: {avg_temp:.1f}{unit_symbol}
            - {"Expect warm conditions ☀️" if avg_temp > 25 else "Expect mild conditions 🌤️" if avg_temp > 15 else "Expect cool conditions 🌡️"}
            """)
        
        with col2:
            most_common_weather = df_forecast['weather_desc'].mode()[0]
            weather_percentage = (df_forecast['weather_desc'] == most_common_weather).sum() / len(df_forecast) * 100
            avg_precip_prob = df_forecast['precipitation_prob'].mean()
            
            st.info(f"""
            **Condition Analysis:**
            - Most frequent: {most_common_weather}
            - Occurs {weather_percentage:.0f}% of the time
            - Avg precipitation chance: {avg_precip_prob:.0f}%
            - {"Bring an umbrella! ☔" if avg_precip_prob > 50 else "Likely to stay dry ✨"}
            """)
    
    else:
        st.error("Unable to process forecast data. Please try again.")

else:
    st.info("👆 Enter a city name and click 'Fetch Weather Data' to get started!")
    
    # Show example cities
    st.markdown("### 🌍 Try these popular cities:")
    example_cities = ["Atlanta", "New York", "Los Angeles", "London", "Tokyo", "Paris", "Sydney"]
    cols = st.columns(len(example_cities))
    for idx, city in enumerate(example_cities):
        with cols[idx]:
            if st.button(city, key=f"example_{city}"):
                st.session_state['example_city'] = city
                st.rerun()

# ==============================================================================
# SIDEBAR
# ==============================================================================

with st.sidebar:
    st.markdown("### 📊 Weather Analysis")
    st.markdown("---")
    
    
    st.markdown("### 🎯 Features")
    st.markdown("""
    - 🌍 Global city search
    - 🌡️ Temperature units
    - 📅 1-7 day forecasts
    - 📊 5 chart types
    - 💡 Auto insights
    """)
    
    st.markdown("---")
    
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Enter city name
    2. Choose temp unit
    3. Select forecast days
    4. Click 'Fetch Data'
    5. Explore charts!
    """)
