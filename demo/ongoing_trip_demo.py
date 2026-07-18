"""
demo/ongoing_trip_demo.py

Standalone, offline demo script that simulates ANITA reacting to a
mid-trip disruption: a solo traveler already has a confirmed itinerary, and
a political rally is reported near one of their planned locations. This
script shows how ImpactAssessmentAgent flags the elevated risk, how ANITA's
RouteManager proposes alternates, and how a human-in-the-loop decision
(via HumanAgentIntegration) applies - or rejects - those alternates.

Runs entirely in Demo mode - no API keys or network access required, and
does not block on real stdin input (the "human" choice is simulated so the
script can run non-interactively, e.g. in CI).

Usage:
    python -m demo.ongoing_trip_demo
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.anita import ANITA  # noqa: E402
from orchestrator.routes import RouteManager  # noqa: E402
from agents.impact_assessment_agent import ImpactAssessmentAgent  # noqa: E402
from agents.flight_agent import FlightAgent  # noqa: E402
from agents.tour_agent import TourAgent  # noqa: E402


def print_section(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def run_ongoing_trip_demo(simulate_human_choice: str = "approve"):
    """
    simulate_human_choice: "approve" or "keep" - stands in for what a human
    traveler would answer when ANITA asks whether to accept the safer
    alternate plan or keep the original itinerary.
    """
    initial_state = {
        "origin": "Delhi",
        "destination": "Rome",
        "arrival_time": "2026-09-05T20:00:00",
        "departure_time": "2026-09-01T04:30:00",
        "traveler_type": "solo",
    }

    print_section("🧳 ANITA Ongoing-Trip Disruption Demo (Solo Traveler, Delhi → Rome)")

    anita = ANITA(initial_state, mode="Demo")
    base_results = anita.orchestrate(traveler_type="solo")

    print("Original itinerary confirmed:")
    for flight in base_results.get("flight", {}).get("flights", []):
        print(f"  ✈️  {flight.get('airline')}: {flight.get('route')}")
    for tour in base_results.get("tour", {}).get("tour_summary", {}).get("tours", []):
        print(f"  🎯 {tour.get('name') or tour.get('title')}")

    # --- Simulate a live disruption report reaching ANITA mid-trip ---
    print_section("🚨 Disruption Report Received")
    disruption_note = "Political rally forming near Piazza Venezia this afternoon"
    print(f"  {disruption_note}")

    # Feed the disruption into a fresh impact assessment. The itinerary text
    # is stringified and scanned for risk keywords (see
    # ImpactAssessmentAgent.assess), so we fold the disruption note into the
    # itinerary payload to trigger the "solo + rally -> High risk" rule.
    impact_agent = ImpactAssessmentAgent(mode="Online")  # non-Demo path exercises real logic
    disrupted_itinerary = dict(base_results)
    disrupted_itinerary["live_disruption_note"] = disruption_note
    impact_report = impact_agent.assess(disrupted_itinerary, traveler_type="solo")

    print(f"  Risk level: {impact_report.risk['risk_level']}")
    print(f"  Political: {impact_report.risk['political']}")

    if impact_report.risk["risk_level"] != "High":
        print("  (Risk did not escalate to High in this run - nothing further to do.)")
        return base_results

    # --- ANITA proposes alternates via RouteManager ---
    print_section("♻️  ANITA Proposes an Alternate Plan")
    routes = RouteManager()
    alternates = routes.alternate_routes(impact_report.model_dump(), initial_state)
    print(f"  Agents flagged for re-routing: {list(alternates.keys())}")
    print("  Suggestion: switch to a safer daytime route and avoid the affected area.")

    # --- Human-in-the-loop decision (simulated, non-blocking) ---
    print_section("🙋 Human Decision")
    print(f"  Traveler choice (simulated): {simulate_human_choice.upper()}")

    if simulate_human_choice != "approve":
        print("  Original plan retained. Risk acknowledged by traveler.")
        return base_results

    # --- Re-run affected agents with the "safe" constraint ---
    print_section("✅ Realigned Itinerary")
    flight_agent = FlightAgent("FlightAgent", mode="Demo")
    tour_agent = TourAgent("TourAgent", mode="Demo")

    new_flight = flight_agent.run({**initial_state, "constraint": alternates.get("flight", "safe")})
    new_tour = tour_agent.run({**initial_state, "constraint": alternates.get("tour", "safe")})

    for flight in new_flight.get("flights", []):
        print(f"  ✈️  {flight.get('airline')}: {flight.get('route')} (constraint={flight.get('constraint_applied')})")
    for tour in new_tour.get("tour_summary", {}).get("tours", []):
        print(f"  🎯 {tour.get('name') or tour.get('title')}")

    print()
    print("  Itinerary realignment complete. Traveler notified.")

    return {"flight": new_flight, "tour": new_tour, "impact_assessment": impact_report.model_dump()}


if __name__ == "__main__":
    run_ongoing_trip_demo(simulate_human_choice="approve")
