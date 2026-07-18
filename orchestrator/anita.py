#orchestrator/anita.py
import logging
from orchestrator.state_manager import StateManager
from orchestrator.routes import RouteManager
from agents.hotel_agent import HotelAgent
from agents.food_agent import FoodAgent
from agents.tour_agent import TourAgent
from agents.flight_agent import FlightAgent
from agents.transport_agent import TransportAgent
from agents.weather_agent import WeatherAgent
from agents.booking_agent import BookingAgent
from agents.impact_assessment_agent import ImpactAssessmentAgent
from prompts.anita_prompt import ANITA_PROMPT
from human_agent_integration import HumanAgentIntegration

logger = logging.getLogger(__name__)

# Agents run in Step 1 of orchestrate(). "booking" is intentionally excluded -
# it only runs after explicit user confirmation via finalize_booking().
CORE_AGENT_NAMES = ["hotel", "food", "tour", "flight", "transport", "weather"]


class ANITA:
    def __init__(self, initial_state, mode="Online"):
        self.prompt = ANITA_PROMPT
        self.state_manager = StateManager(initial_state)
        self.mode = mode

        # Initialize agents
        self.agents = {
            "hotel": HotelAgent("HotelAgent", mode=mode),
            "food": FoodAgent("FoodAgent", mode=mode),
            "tour": TourAgent("TourAgent", mode=mode),
            "flight": FlightAgent("FlightAgent", mode=mode),
            "transport": TransportAgent("TransportAgent", mode=mode),
            "weather": WeatherAgent("WeatherAgent", mode=mode),
            "impact": ImpactAssessmentAgent(mode=mode),
            "booking": BookingAgent("BookingAgent", mode=mode)
        }

        # RouteManager decides which agents should run based on state
        self.routes = RouteManager()

    def orchestrate(self, traveler_type="general", preferences=None):
        results = {}

        # Step 1: Run core agents with error handling
        for name in CORE_AGENT_NAMES:
            if self.state_manager.route(name, self.routes):
                try:
                    output = self.agents[name].run(self.state_manager.state)
                    self.state_manager.update(name, output)
                    results[name] = output
                except Exception as e:
                    logger.error(f"Agent {name} failed with error: {e}", exc_info=True)
                    results[name] = {
                        "error": f"Agent {name} failed: {str(e)}",
                        "status": "failed"
                    }
                    # Continue with other agents instead of crashing

        # Step 2: Assess impact
        impact_report = None
        try:
            impact_report = self.agents["impact"].assess(results, traveler_type, preferences)
            results["impact_assessment"] = impact_report.model_dump()
        except Exception as e:
            logger.error(f"Impact assessment failed: {e}", exc_info=True)
            results["impact_assessment"] = {"error": f"Impact assessment failed: {str(e)}"}

        # Step 3: Build narrative (guarded - impact_report may be None if Step 2 failed)
        narrative = []
        if impact_report is not None:
            if impact_report.budget.get("flag") == "Expensive":
                narrative.append("Your hotel choice looks expensive, so I’ve pulled budget alternatives.")
            if impact_report.accessibility.get("wheelchair_friendly_hotels"):
                narrative.append("Accessibility is flagged — I’ve added wheelchair‑friendly hotel and tour options.")
            if impact_report.risk.get("risk_level") == "High":
                narrative.append("Risk level is high — I suggest safer transport routes or daytime flights.")
            if impact_report.sustainability.get("carbon_score") == "High":
                narrative.append("This itinerary has a high carbon footprint — eco‑friendly hotels and metro transport are available.")

        results["impact_narrative"] = (
            " ".join(narrative) if narrative else "Your itinerary looks balanced and well‑suited."
        )

        # Step 4: Apply alternates into state (only when impact assessment succeeded)
        if self.routes and impact_report is not None:
            try:
                alternates = self.routes.alternate_routes(impact_report.model_dump(), self.state_manager.state)
                self.state_manager.apply_alternates(alternates)

                # Step 5: Re‑query agents with constraints
                alternate_outputs = {}
                for agent_name, constraint in alternates.items():
                    if agent_name not in self.agents:
                        continue
                    try:
                        alt_output = self.agents[agent_name].run(
                            {**self.state_manager.state, "constraint": constraint}
                        )
                        alternate_outputs[agent_name] = alt_output
                        self.state_manager.update(f"{agent_name}_alternates", alt_output)
                    except Exception as e:
                        logger.error(f"Alternate re-run for {agent_name} failed: {e}", exc_info=True)
                        alternate_outputs[agent_name] = {"error": str(e)}

                results["alternate_options"] = alternate_outputs
            except Exception as e:
                logger.error(f"Alternate routing failed: {e}", exc_info=True)

        return results

    def run_itinerary(self, state):
        flight_agent = FlightAgent(mode="Online")
        tour_agent = TourAgent(mode="Online")
        human_integration = HumanAgentIntegration()

        # Collect agent outputs
        state = flight_agent.run(state)
        tours = tour_agent.run(state)

        # Present to human
        human_integration.present_options({
            "Flights": state.get("flights", []),
            "Tours": tours.get("tour_summary", {}).get("tours", [])
        })

        # Collect feedback
        feedback = human_integration.collect_feedback()

        # Apply feedback and re‑run agents
        state = human_integration.apply_feedback(state, feedback)
        state = flight_agent.run(state)  # re‑run with constraint
        tours = tour_agent.run(state)

        return {"flights": state["flights"], "tours": tours["tour_summary"]["tours"]}

    def finalize_booking(self, itinerary, user_confirmation):
        if user_confirmation:
            return self.agents["booking"].run(itinerary)
        return {"status": "Booking not confirmed"}
