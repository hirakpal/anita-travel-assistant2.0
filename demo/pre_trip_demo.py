"""
demo/pre_trip_demo.py

Standalone, offline demo script that walks through ANITA's pre-trip planning
flow: given an origin, destination, and dates, it fans out to the hotel,
food, tour, flight, transport, and weather agents, then runs an impact
assessment and prints a human-readable summary.

Runs entirely in Demo mode - no API keys or network access required.

Usage:
    python -m demo.pre_trip_demo
    python -m demo.pre_trip_demo --trip demo-002
"""
import argparse
import json
import os
import sys

# Allow running this file directly (`python demo/pre_trip_demo.py`) as well
# as as a module (`python -m demo.pre_trip_demo`).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.anita import ANITA  # noqa: E402

MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "mock_data.json")


def load_trip(trip_id: str) -> dict:
    with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for trip in data["trips"]:
        if trip["trip_id"] == trip_id:
            return trip
    raise ValueError(f"No trip found with id={trip_id!r} in {MOCK_DATA_PATH}")


def print_section(title: str):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def run_pre_trip_demo(trip_id: str = "demo-001"):
    trip = load_trip(trip_id)

    print_section(f"ANITA Pre-Trip Planning Demo: {trip['label']}")

    initial_state = {
        "origin": trip["origin"],
        "destination": trip["destination"],
        "arrival_time": trip["arrival_time"],
        "departure_time": trip["departure_time"],
        "budget": trip.get("budget"),
        "traveler_type": trip.get("traveler_type", "general"),
    }

    anita = ANITA(initial_state, mode="Demo")
    results = anita.orchestrate(traveler_type=initial_state["traveler_type"])

    print_section("✈️  Flights")
    for flight in results.get("flight", {}).get("flights", []):
        print(f"  - {flight.get('airline')}: {flight.get('route')} ({flight.get('price_range')})")

    print_section("🏨 Hotels")
    for hotel in results.get("hotel", {}).get("hotels", []):
        print(f"  - {hotel.get('name')} in {hotel.get('location')} ({hotel.get('price_range')})")

    print_section("🍽️  Restaurants")
    for restaurant in results.get("food", {}).get("restaurants", []):
        print(f"  - {restaurant.get('name')} ({restaurant.get('cuisine')}, {restaurant.get('price_range')})")

    print_section("🚖 Transport")
    for option in results.get("transport", {}).get("transport", []):
        print(f"  - {option.get('mode')}: {option.get('duration')} ({option.get('price_range')})")

    print_section("🎯 Tours & Activities")
    for tour in results.get("tour", {}).get("tour_summary", {}).get("tours", []):
        print(f"  - {tour.get('name') or tour.get('title')}")

    print_section("🌦️  Weather")
    weather = results.get("weather", {}).get("weather", {})
    print(f"  Forecast: {weather.get('forecast')}")
    print(f"  Recommendation: {weather.get('recommendation')}")

    print_section("📊 Impact Assessment")
    impact = results.get("impact_assessment", {})
    print(f"  Sustainability: {impact.get('sustainability', {}).get('carbon_score')}")
    print(f"  Risk level: {impact.get('risk', {}).get('risk_level')}")
    print(f"  Budget flag: {impact.get('budget', {}).get('flag')}")

    print_section("💬 ANITA says")
    print(f"  {results.get('impact_narrative')}")

    if results.get("alternate_options"):
        print_section("♻️  Alternate Options Triggered")
        for agent_name in results["alternate_options"]:
            print(f"  - Re-ran {agent_name} agent with a constraint")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ANITA's pre-trip planning demo (offline, Demo mode).")
    parser.add_argument("--trip", default="demo-001", help="Trip id from demo/mock_data.json to use")
    args = parser.parse_args()

    run_pre_trip_demo(args.trip)
