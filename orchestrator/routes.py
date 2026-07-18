# orchestrator/routes.py
"""
Routing logic for Anita's orchestration layer.
Determines which agent(s) should be invoked based on state and user intent.
Also handles alternate routing when ImpactAssessmentAgent flags issues.
"""

class RouteManager:
    def __init__(self):
        # Define available routes and their conditions
        self.routes = {
            "hotel": self._hotel_route,
            "food": self._food_route,
            "flight": self._flight_route,
            "tour": self._tour_route,
            "transport": self._transport_route,
            "weather": self._weather_route,
            "impact": self._impact_route,
        }

    def route(self, agent_name: str, state: dict = None) -> bool:
        """
        Decide whether to run a given agent based on current state.
        Returns True if the agent should be invoked.
        """
        if agent_name not in self.routes:
            return False
        return self.routes[agent_name](state or {})

    # --- Individual route conditions ---
    # NOTE: conditions are intentionally aligned with the actual state schema
    # produced by main.py / streamlit_ui.py: origin, destination, arrival_time,
    # departure_time, budget (optional), traveler_type (optional). Dates are
    # represented as arrival_time/departure_time, not a generic "dates" key,
    # and food/tour preferences are optional rather than required so those
    # agents still run with sensible defaults.
    def _hotel_route(self, state: dict) -> bool:
        return bool(state.get("destination"))

    def _food_route(self, state: dict) -> bool:
        return bool(state.get("destination"))

    def _flight_route(self, state: dict) -> bool:
        return bool(state.get("origin") and state.get("destination"))

    def _tour_route(self, state: dict) -> bool:
        return bool(state.get("destination"))

    def _transport_route(self, state: dict) -> bool:
        return bool(state.get("origin") and state.get("destination"))

    def _weather_route(self, state: dict) -> bool:
        return bool(state.get("destination"))

    def _impact_route(self, state: dict) -> bool:
        # Always run impact assessment after itinerary is built
        return True

    # --- Alternate routing based on ImpactAssessmentAgent flags ---
    def alternate_routes(self, impact_report: dict, state: dict) -> dict:
        """
        Decide which agents to re-run with constraints based on impact flags.
        Returns a dict of agent_name -> constraint.
        """
        alternates = {}

        # Budget flagged → re-run hotel, food, flight with budget constraint
        if impact_report.get("budget", {}).get("flag") == "Expensive":
            alternates["hotel"] = "budget"
            alternates["food"] = "budget"
            alternates["flight"] = "budget"

        # Accessibility flagged → re-run hotel, tour, food with accessibility constraint
        if impact_report.get("accessibility", {}).get("wheelchair_friendly_hotels"):
            alternates["hotel"] = "accessible"
            alternates["tour"] = "accessible"
            alternates["food"] = "accessible"

        # Sustainability flagged → re-run hotel, flight, food with eco constraint
        if impact_report.get("sustainability", {}).get("carbon_score") == "High":
            alternates["hotel"] = "eco"
            alternates["flight"] = "eco"
            alternates["food"] = "eco"

        # Risk flagged → re-run flight, tour with safe constraint
        if impact_report.get("risk", {}).get("risk_level") == "High":
            alternates["flight"] = "safe"
            alternates["tour"] = "safe"

        return alternates
