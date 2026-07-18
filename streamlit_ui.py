"""
ANITA Travel Assistant - Professional Streamlit UI
Enhanced user interface with better styling and interactions
"""

import streamlit as st
from urllib.parse import quote
from datetime import datetime, timedelta
import json
from orchestrator.anita import ANITA

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="ANITA - AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00d4ff;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }

    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066cc;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    .card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }

    .rating-badge {
        display: inline-block;
        background: #fbbf24;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .price-badge {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
    }

    .status-success {
        background: #dcfce7;
        color: #166534;
    }

    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }

    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .info-item {
        padding: 1rem;
        background: #f3f4f6;
        border-radius: 8px;
        text-align: center;
    }

    .info-label {
        font-size: 0.875rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .info-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0066cc;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Trip Configuration")

    # Mode selection
    mode = st.radio(
        "Mode",
        ["Demo", "Online"],
        help="Demo shows simulated data, Online connects to real APIs"
    )

    st.markdown("---")

    # Trip details
    st.markdown("### 🌍 Trip Details")

    origin = st.text_input(
        "Origin City",
        value="Bengaluru",
        help="Starting city for your trip"
    )

    destination = st.text_input(
        "Destination City",
        value="Jaipur",
        help="Destination city for your trip"
    )

    # Date inputs
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() + timedelta(days=1),
            help="When does your trip start?"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now() + timedelta(days=4),
            help="When does your trip end?"
        )

    st.markdown("---")

    # Traveler preferences
    st.markdown("### 👤 Traveler Profile")

    traveler_type = st.selectbox(
        "Traveler Type",
        ["General", "Solo", "Family", "Adventure", "Senior"],
        help="Choose your travel profile for personalized recommendations"
    )

    budget_level = st.selectbox(
        "Budget Level",
        ["Economy", "Standard", "Premium", "Luxury"],
        help="Set your budget preferences"
    )

    st.markdown("---")

    # Action buttons
    st.markdown("### 🎯 Actions")

    if st.button("🔄 Refresh Itinerary", use_container_width=True):
        st.session_state.refresh = True

    if st.button("💾 Save Trip", use_container_width=True):
        st.success("✅ Trip saved successfully!")

    st.markdown("---")
    st.markdown(
        "**ANITA** - AI Travel Orchestrator & Planner\n\n"
        "Powered by Claude AI"
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-header">✈️ ANITA Travel Planner</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{origin} → {destination}</div>', unsafe_allow_html=True)

with col2:
    mode_badge = "🟢 Demo" if mode == "Demo" else "🔵 Online"
    st.markdown(f"<div style='text-align: right; padding: 1rem;'>{mode_badge}</div>", unsafe_allow_html=True)

st.markdown("---")

# Initialize ANITA with user inputs
initial_state = {
    "origin": origin,
    "destination": destination,
    "arrival_time": datetime.combine(start_date, datetime.min.time()).isoformat(),
    "departure_time": datetime.combine(end_date, datetime.max.time()).isoformat(),
    "budget": budget_level.lower(),
    "traveler_type": traveler_type.lower()
}

# Load results (with caching for performance)
@st.cache_data(show_spinner=True)
def get_itinerary(origin, destination, mode, traveler_type):
    try:
        anita = ANITA(initial_state, mode=mode)
        results = anita.orchestrate(traveler_type=traveler_type.lower())
        return results
    except Exception as e:
        st.error(f"Error generating itinerary: {str(e)}")
        return {}

results = get_itinerary(origin, destination, mode, traveler_type)

# ============================================================================
# TAB NAVIGATION
# ============================================================================

tabs = st.tabs([
    "🗺️ Overview",
    "✈️ Flights",
    "🏨 Hotels",
    "🚖 Transport",
    "🎯 Activities",
    "🍽️ Dining",
    "⚠️ Alerts",
    "📊 Impact Analysis"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================
with tabs[0]:
    st.markdown("### Trip Summary")

    # Trip duration
    trip_duration = (end_date - start_date).days

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Duration</div>
            <div class="info-value">{trip_duration} days</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Traveler Type</div>
            <div class="info-value">{traveler_type}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Budget</div>
            <div class="info-value">{budget_level}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="info-item">
            <div class="info-label">Distance</div>
            <div class="info-value">~</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Map section
    st.markdown("### 📍 Route Map")
    search_query = f"{quote(origin)} to {quote(destination)}"
    maps_url = f"https://www.google.com/maps/search/{search_query}"
    st.markdown(f"""
    <a href="{maps_url}" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: #0066cc; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
        📍 View on Google Maps
    </a>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Impact narrative
    narrative = results.get("impact_narrative", "Your itinerary is being prepared...")
    st.markdown(f"""
    <div class="card">
        <h4>✨ AI Recommendations</h4>
        <p>{narrative}</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 2: FLIGHTS
# ============================================================================
with tabs[1]:
    st.markdown("### Flight Options")

    flights = results.get("flight", {}).get("flights", [])

    if flights:
        for idx, flight in enumerate(flights):
            col1, col2 = st.columns([3, 1])

            with col1:
                airline = flight.get("airline", "Unknown Airline")
                price = flight.get("price_range", "N/A")
                rating = flight.get("reviews", {}).get("rating", "N/A")

                st.markdown(f"""
                <div class="card">
                    <h4>✈️ {airline}</h4>
                    <div style="margin: 1rem 0;">
                        <span class="price-badge">💰 {price}</span>
                        <span class="rating-badge">⭐ {rating}</span>
                    </div>
                    <p><strong>Route:</strong> {flight.get('route', 'N/A')}</p>
                    <p><strong>Duration:</strong> {flight.get('duration', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"✈️ Select", key=f"flight_{idx}", use_container_width=True):
                    st.success(f"✅ {airline} selected!")
    else:
        st.info("📌 No flights available. Please check your dates and cities.")

# ============================================================================
# TAB 3: HOTELS
# ============================================================================
with tabs[2]:
    st.markdown("### Hotel Recommendations")

    hotels = results.get("hotel", {}).get("hotels", [])

    if hotels:
        for idx, hotel in enumerate(hotels):
            col1, col2 = st.columns([3, 1])

            with col1:
                name = hotel.get("name", "Unknown Hotel")
                rating = hotel.get("rating", "N/A")
                price = hotel.get("price", "N/A")
                location = hotel.get("location", "City")

                st.markdown(f"""
                <div class="card">
                    <h4>🏨 {name}</h4>
                    <p>📍 {location}</p>
                    <div style="margin: 1rem 0;">
                        <span class="price-badge">💰 {price}</span>
                        <span class="rating-badge">⭐ {rating}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"🏨 Book", key=f"hotel_{idx}", use_container_width=True):
                    st.success(f"✅ {name} added to itinerary!")
    else:
        st.info("📌 No hotels available. Please check your destination.")

# ============================================================================
# TAB 4: TRANSPORT
# ============================================================================
with tabs[3]:
    st.markdown("### Local Transportation")

    transport = results.get("transport", {}).get("transport", [])

    if transport:
        # Create columns for transport options
        cols = st.columns(2)
        for idx, t in enumerate(transport):
            with cols[idx % 2]:
                mode = t.get("mode", "Unknown")
                duration = t.get("duration", "N/A")
                price = t.get("price_range") or t.get("price", "N/A")
                rating = t.get("reviews", {}).get("rating") or t.get("rating", "N/A")

                st.markdown(f"""
                <div class="card">
                    <h4>🚖 {mode}</h4>
                    <div style="margin: 1rem 0;">
                        <p><strong>⏱️ Duration:</strong> {duration}</p>
                        <p><strong>💰 Price:</strong> {price}</p>
                        <span class="rating-badge">⭐ {rating}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📌 Transport options not available.")

# ============================================================================
# TAB 5: ACTIVITIES
# ============================================================================
with tabs[4]:
    st.markdown("### Activities & Tours")

    tours = results.get("tour", {}).get("tour_summary", {}).get("tours", [])

    if tours:
        for idx, tour in enumerate(tours):
            col1, col2 = st.columns([3, 1])

            with col1:
                title = tour.get("title", "Activity")
                location = tour.get("location", "Location")
                price = tour.get("price", "N/A")
                rating = tour.get("rating", "N/A")
                description = tour.get("description", "")

                st.markdown(f"""
                <div class="card">
                    <h4>🎯 {title}</h4>
                    <p>📍 {location}</p>
                    <p>{description}</p>
                    <div style="margin: 1rem 0;">
                        <span class="price-badge">💰 {price}</span>
                        <span class="rating-badge">⭐ {rating}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"🎯 Add", key=f"tour_{idx}", use_container_width=True):
                    st.success(f"✅ {title} added!")
    else:
        st.info("📌 Activities not available.")

# ============================================================================
# TAB 6: DINING
# ============================================================================
with tabs[5]:
    st.markdown("### Dining Recommendations")

    # Cuisine filter
    cuisine_filter = st.multiselect(
        "Filter by Cuisine",
        ["Any", "Vegetarian", "Vegan", "Street Food", "Fine Dining", "Italian", "Indian", "Asian"],
        default=["Any"]
    )

    foods = results.get("food", {}).get("restaurants", [])

    if foods:
        cols = st.columns(2)
        for idx, food in enumerate(foods):
            with cols[idx % 2]:
                name = food.get("name", "Restaurant")
                cuisine = food.get("cuisine", "International")
                price = food.get("price", "N/A")
                rating = food.get("rating", "N/A")

                st.markdown(f"""
                <div class="card">
                    <h4>🍽️ {name}</h4>
                    <p>🍴 {cuisine}</p>
                    <div style="margin: 1rem 0;">
                        <span class="price-badge">💰 {price}</span>
                        <span class="rating-badge">⭐ {rating}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📌 No restaurants available.")

# ============================================================================
# TAB 7: ALERTS
# ============================================================================
with tabs[6]:
    st.markdown("### Travel Alerts")

    impact = results.get("impact_assessment", {})

    # Weather alerts
    weather = results.get("weather", {}).get("weather", {})
    if weather and not weather.get("error"):
        forecast = weather.get("forecast", {})
        temp = forecast.get("temperature", "N/A") if isinstance(forecast, dict) else forecast
        st.info(f"🌦️ Weather: {temp} — {weather.get('recommendation', '')}")
        advisories = weather.get("advisories")
        if advisories and advisories != "No major travel advisories":
            st.warning(f"⚠️ Advisory: {advisories}")
    elif weather.get("error"):
        st.info("🌦️ Weather data currently unavailable.")

    # Risk alerts
    risk = impact.get("risk", {})
    risk_level = risk.get("risk_level", "Low")

    if risk_level == "High":
        st.error(f"🚨 High Risk Alert: {risk.get('weather', 'No specific risks')}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve Alternate Plan"):
                st.success("Plan updated with safer alternatives!")
        with col2:
            if st.button("🛑 Keep Original Plan"):
                st.warning("Risk acknowledged. Original plan retained.")
    elif risk_level == "Medium":
        st.warning(f"⚠️ Medium Risk: Please review alternatives")
    else:
        st.success(f"✅ Low Risk - Your trip looks good!")

    st.markdown("---")

    # Accessibility alerts
    accessibility = impact.get("accessibility", {})
    if accessibility.get("wheelchair_friendly_hotels"):
        st.info("♿ Wheelchair-friendly options available")

    # Health alerts
    health = impact.get("health", {})
    if health.get("vaccination_advisories"):
        st.warning("💉 Vaccination recommended for this destination")

# ============================================================================
# TAB 8: IMPACT ANALYSIS
# ============================================================================
with tabs[7]:
    st.markdown("### Trip Impact Analysis")

    impact = results.get("impact_assessment", {})

    col1, col2 = st.columns(2)

    # Sustainability
    with col1:
        sustainability = impact.get("sustainability", {})
        carbon_score = sustainability.get("carbon_score", "N/A")

        st.markdown(f"""
        <div class="card">
            <h4>🌍 Sustainability</h4>
            <p><strong>Carbon Score:</strong> {carbon_score}</p>
            <p><strong>Eco-Alternatives:</strong></p>
            <ul>
                {''.join([f'<li>{alt}</li>' for alt in sustainability.get('eco_alternatives', [])])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Budget
    with col2:
        budget = impact.get("budget", {})
        flag = budget.get("flag", "N/A")

        badge_color = "status-success" if flag == "Affordable" else "status-warning"
        st.markdown(f"""
        <div class="card">
            <h4>💰 Budget Analysis</h4>
            <p><span class="status-badge {badge_color}">{flag}</span></p>
            <p><strong>Alternatives:</strong></p>
            <ul>
                {''.join([f'<li>{alt}</li>' for alt in budget.get('alternatives', [])])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Wellbeing
    wellbeing = impact.get("wellbeing", {})
    st.markdown(f"""
    <div class="card">
        <h4>😊 Wellbeing</h4>
        <p><strong>Activity Balance:</strong> {wellbeing.get('activity_balance', 'N/A')}</p>
        <p><strong>Recommendation:</strong> {wellbeing.get('recommendation', 'Looks good!')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Cultural Fit
    cultural = impact.get("cultural_fit", {})
    st.markdown(f"""
    <div class="card">
        <h4>🌏 Cultural Fit</h4>
        <p><strong>Local Customs:</strong> {cultural.get('sensitivity', 'N/A')}</p>
        <p><strong>Dining Options:</strong> {cultural.get('dietary', 'Various options available')}</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #999; padding: 2rem 0; font-size: 0.875rem;">
        <p>🤖 Powered by ANITA - AI Travel Orchestrator & Planner</p>
        <p>Built with Claude AI | Streamlit | Python</p>
    </div>
    """,
    unsafe_allow_html=True
)
