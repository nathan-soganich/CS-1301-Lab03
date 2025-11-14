"""
CS 1301 - Web Development Lab 03
Weather Intelligence & Travel Planning System

This is the home page of our multi-page Streamlit web application.
Author: Team [Your Team Number]
"""

import streamlit as st

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Weather Intelligence Hub",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CUSTOM CSS FOR BETTER STYLING
# ==============================================================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .page-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .highlight-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #2196F3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MAIN HEADER
# ==============================================================================
st.markdown("""
<div class="main-header">
    <h1>🌤️ Weather Intelligence Hub</h1>
    <p style="font-size: 1.2rem;">Advanced Weather Analysis & AI-Powered Travel Planning</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# TEAM INFORMATION
# ==============================================================================
st.subheader("Team Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="highlight-box">
        <h3 style="margin-top: 0;"> Team Details</h3>
        <p><strong>Team Number:</strong> 80</p>
        <p><strong>Section:</strong> Section C</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="highlight-box">
        <h3 style="margin-top: 0;">Team Members</h3>
        <p>• Nathan Soganich</p>
        <p>• Kathy Tran Do</p>

    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="highlight-box">
        <h3 style="margin-top: 0;">Submission Info</h3>
        <p><strong>Lab:</strong> Web Dev Lab 03</p>
        <p><strong>Course:</strong> CS 1301</p>
        <p><strong>Semester:</strong> Fall 2025</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# PROJECT OVERVIEW
# ==============================================================================
st.markdown("Project Overview")

st.markdown("""
Welcome to our **Weather Intelligence Hub** - a comprehensive web application that combines 
real-time weather data with artificial intelligence to provide intelligent weather analysis 
and travel planning assistance.

This project demonstrates:
- **API Integration**: Real-time data from Open-Meteo Weather API
- **Data Visualization**: Interactive charts and dynamic graphs
- **AI Processing**: Google Gemini LLM for intelligent insights --> not yet working
- **Conversational AI**: Smart chatbot with context memory --> not yet working 
""")

st.markdown("---")

# ==============================================================================
# PAGE DESCRIPTIONS
# ==============================================================================
st.markdown("Application Pages")

st.markdown("""
Navigate through our application using the sidebar. Here's what each page offers:
""")

# Page 1 Description
st.markdown("""
<div class="page-card">
    <h3> Weather Analysis Dashboard</h3>
    <p><strong>Purpose:</strong> Comprehensive real-time weather data analysis and visualization</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Search weather data for any city worldwide</li>
        <li>View 5-day weather forecasts with hourly breakdowns</li>
        <li>Interactive temperature trend charts</li>
        <li>Weather condition distribution analysis</li>
        <li>Air quality index monitoring</li>
        <li>Dynamic weather icons and visual indicators</li>
    </ul>
    <p><strong>Technology:</strong> Open-Meteo Weather API, Plotly charts, Pandas data processing</p>
</div>
""", unsafe_allow_html=True)

# Page 2 Description
st.markdown("""
<div class="page-card">
    <h3>AI Weather Insights</h3>
    <p><strong>Purpose:</strong> AI-powered weather analysis and travel recommendations</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Compare weather conditions between multiple cities</li>
        <li>AI-generated travel advice based on forecast data</li>
        <li>Customized activity recommendations for weather conditions</li>
        <li>Intelligent weather comparison articles</li>
        <li>Packing list suggestions based on temperature and conditions</li>
    </ul>
    <p><strong>Technology:</strong> Google Gemini API, advanced prompt engineering, data synthesis</p>
</div>
""", unsafe_allow_html=True)

# Page 3 Description
st.markdown("""
<div class="page-card">
    <h3>Weather Assistant Chatbot</h3>
    <p><strong>Purpose:</strong> Conversational AI assistant for weather-related queries</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Natural language weather queries</li>
        <li>Context-aware conversation with memory</li>
        <li>Personalized travel planning assistance</li>
        <li>Weather-based activity suggestions</li>
        <li>Real-time data integration in responses</li>
        <li>Handles complex multi-city comparisons</li>
    </ul>
    <p><strong>Technology:</strong> Google Gemini API with conversation history, context management</p>
</div>
""", unsafe_allow_html=True)

# Home Page Description (implicit)
st.markdown("""
<div class="page-card">
    <h3>Home Page (Current)</h3>
    <p><strong>Purpose:</strong> Welcome page and navigation hub</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Team information and project overview</li>
        <li>Comprehensive page descriptions</li>
        <li>Quick start guide</li>
        <li>Project documentation</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #666;">
    <p>Built with Streamlit | CS 1301 Fall 2025</p>
    <p>Georgia Institute of Technology</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# SIDEBAR CONTENT
# ==============================================================================
with st.sidebar:
    st.markdown("Weather Intelligence Hub")
    st.markdown("---")
    st.markdown("Navigation")
    st.info("""
    Use the pages above to navigate through:
    - Weather Analysis
    - AI Insights
    - Chatbot
    """)
    
    st.markdown("---")
    st.markdown("Quick Tips")
    st.markdown("""
    - Start with Weather Analysis
    - Try comparing multiple cities
    - Ask the chatbot anything!
    """)
    

