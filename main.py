import streamlit as st
from urllib.parse import quote
from orchestrator.anita import ANITA

# Mode toggle (only Online and Demo)
mode = st.radio("Select Mode", ["Online", "Demo"])

# ---------------- Helper: Google Maps Embed ----------------
def show_map(origin, destination, waypoints=None):
    if mode == "Online":
        # Generate a safe Google Maps search URL (without API key - safer approach)
        if waypoints and len(waypoints) > 0:
            wp_str = "|".join([quote(w) for w in waypoints if w])
            search_query = f"{quote(origin)} to {quote(destination)} via {wp_str}"
        else:
            search_query = f"{quote(origin)} to {quote(destination)}"
        maps_url = f"https://www.google.com/maps/search/{search_query}"
        st.markdown(f"""
        📍 **Map**: [View on Google Maps]({maps_url})
        """)
    elif mode == "Demo":
        st.success(f"🎬 Demo Mode: Simulated route {origin} → {destination} with waypoints {waypoints}")

# ---------------- Helper: Suggestion Card ----------------
def suggestion_card(icon, title, price, rating, popularity, distance=None, duration=None, cuisine=None):
    st.markdown(f"""
    {icon} **{title}**  
    💰 Price: {price}  
    ⭐ Popularity: {popularity} (Rating: {rating})  
    {f"🚶 Distance: {distance} | ⏱️ Time: {duration}" if distance and duration else ""}  
    {f"🍴 Cuisine: {cuisine}" if cuisine else ""}
    """)

# ---------------- Initialize ANITA ----------------
initial_state = {
    "origin": "Bengaluru",
    "destination": "Jaipur",
    "arrival_time": "2026-07-20T18:00:00",
    "departure_time": "2026-07-20T06:00:00"
}

anita = ANITA(initial_state, mode=mode)
results = anita.orchestrate(traveler_type="general")

# ---------------- Tabs ----------------
tab_itinerary, tab_flights, tab_hotels, tab_transport, tab_activities, tab_culinary, tab_disruptions, tab_alerts = st.tabs(
    ["Itinerary", "Flights", "Hotels", "Transport", "Activities", "Culinary", "Disruptions", "Proactive Alerts"]
)

# ---------------- ITINERARY TAB ----------------
with tab_itinerary:
    st.header("Itinerary Overview")
    st.write(f"Mode: {mode}")
    show_map(initial_state["origin"], initial_state["destination"])

# ---------------- FLIGHTS TAB ----------------
with tab_flights:
    st.header("Flights")
    flights = results.get("flight", {}).get("flights", [])
    if flights:
        for f in flights:
            suggestion_card("✈️", f.get("airline", "Unknown"), f.get("price_range", "N/A"),
                            f.get("reviews", {}).get("rating", "N/A"),
                            f.get("constraint_applied", ""))
    show_map(initial_state["origin"], initial_state["destination"])

# ---------------- HOTELS TAB ----------------
with tab_hotels:
    st.header("Hotels")
    hotels = results.get("hotel", {}).get("hotels", [])
    if hotels:
        for h in hotels:
            suggestion_card("🏨", h.get("name", "Unknown"), h.get("price", "N/A"),
                            h.get("rating", "N/A"), h.get("popularity", ""))
    show_map(initial_state["destination"], hotels[0].get("name", "Jaipur Hotel") if hotels else "Jaipur Hotel")

# ---------------- TRANSPORT TAB ----------------
with tab_transport:
    st.header("Transport")
    transport = results.get("transport", {}).get("transport", [])
    if transport:
        for t in transport:
            suggestion_card("🚖", t.get("mode", "Transport"), t.get("price_range", "N/A"),
                            t.get("reviews", {}).get("rating", "N/A"), t.get("availability", ""),
                            distance=t.get("distance"), duration=t.get("duration"))
    show_map("ITC Rajputana Jaipur", "Amber Fort Jaipur")

# ---------------- ACTIVITIES TAB ----------------
with tab_activities:
    st.header("Activities")
    tours = results.get("tour", {}).get("tour_summary", {}).get("tours", [])
    if tours:
        for t in tours:
            suggestion_card("🎯", t.get("title", "Activity"), t.get("price", "N/A"),
                            t.get("rating", "N/A"), t.get("popularity", "🔥 Popular"))
    if tours:
        show_map(tours[0].get("location", "Amber Fort Jaipur"), tours[-1].get("location", "Hawa Mahal Jaipur"))

# ---------------- CULINARY TAB ----------------
with tab_culinary:
    st.header("Culinary")
    cuisine_filter = st.selectbox("Cuisine Preference", ["Any", "Vegetarian", "Vegan", "Street Food", "Fine Dining"])
    foods = results.get("food", {}).get("restaurants", [])
    if foods:
        for f in foods:
            suggestion_card("🍽️", f.get("name", "Restaurant"), f.get("price", "N/A"),
                            f.get("rating", "N/A"), f.get("popularity", ""),
                            distance=f.get("distance"), duration=f.get("duration"), cuisine=cuisine_filter)
    show_map("Amber Fort Jaipur", "Laxmi Misthan Bhandar Jaipur")

# ---------------- DISRUPTIONS TAB ----------------
with tab_disruptions:
    st.header("Disruption Alerts")
    alerts = results.get("impact_assessment", {}).get("risk", {})
    if mode == "Demo":
        st.error("🚨 Demo Disruption: Flight simulated delay")
        st.success("✅ Demo Alternative Approved")
    else:
        if alerts.get("risk_level") == "High":
            st.error("🚨 High risk detected in itinerary")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve Alternate Plan"):
                    st.success("✅ Approved. Itinerary updated.")
                    st.info("♻️ Realignment triggered.")
            with col2:
                if st.button("Keep Original Plan"):
                    st.warning("🛑 Original plan retained. Risks acknowledged.")

# ---------------- PROACTIVE ALERTS TAB ----------------
with tab_alerts:
    st.header("Proactive Alerts")
    if mode == "Demo":
        st.warning("🌦️ Demo Alert: Simulated rain forecast → Indoor activity suggested.")
    else:
        weather = results.get("weather", {}).get("weather", {})
        advisories = weather.get("advisories", "")
        if "rain" in str(advisories).lower() or "storm" in str(advisories).lower():
            st.warning("🌦️ Rain/storm advisory detected → Suggest indoor museum instead of outdoor walk.")
        st.warning("🚧 Road closure detected → Suggest alternate transport route.")
