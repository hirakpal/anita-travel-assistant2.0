"""
End-to-end and unit tests for the ANITA orchestrator and its agents.

All tests run in Demo mode so they require zero network access and zero API
keys - Demo mode is fully offline (see rag/*.py lazy-loading and each
agent's Demo branch).
"""
import pytest

from orchestrator.anita import ANITA
from agents.hotel_agent import HotelAgent
from agents.food_agent import FoodAgent
from agents.tour_agent import TourAgent
from agents.flight_agent import FlightAgent
from agents.transport_agent import TransportAgent
from agents.weather_agent import WeatherAgent
from agents.booking_agent import BookingAgent
from utils.cache import call_api, savings_percent, clear_cache
from utils.token_tracker import log_tokens, get_usage, get_all_usage

TRIP_STATE = {
    "origin": "Bengaluru",
    "destination": "Jaipur",
    "arrival_time": "2026-07-20T18:00:00",
    "departure_time": "2026-07-20T06:00:00",
}


# ----------------------------
# Agent Output Validation (Demo mode)
# ----------------------------

def test_hotel_agent_output():
    agent = HotelAgent("HotelAgent", mode="Demo")
    result = agent.run({"destination": "Rome"})
    assert "hotels" in result
    assert isinstance(result["hotels"], list)
    assert len(result["hotels"]) > 0


def test_food_agent_output():
    agent = FoodAgent("FoodAgent", mode="Demo")
    result = agent.run({"destination": "Rome"})
    assert "restaurants" in result
    assert isinstance(result["restaurants"], list)


def test_tour_agent_output():
    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": "Rome"})
    assert "tour_summary" in result
    assert isinstance(result["tour_summary"]["tours"], list)


def test_flight_agent_output():
    agent = FlightAgent("FlightAgent", mode="Demo")
    result = agent.run({
        "origin": "Delhi",
        "destination": "Rome",
        "arrival_time": "2026-08-01T00:00:00",
        "departure_time": "2026-07-30T00:00:00",
    })
    assert "flights" in result
    assert isinstance(result["flights"], list)


def test_transport_agent_output():
    agent = TransportAgent("TransportAgent", mode="Demo")
    result = agent.run({"origin": "Delhi", "destination": "Rome"})
    assert "transport" in result
    assert isinstance(result["transport"], list)


def test_weather_agent_output():
    agent = WeatherAgent("WeatherAgent", mode="Demo")
    result = agent.run({"destination": "Rome"})
    assert "weather" in result
    assert isinstance(result["weather"], dict)


def test_booking_agent_output():
    agent = BookingAgent("BookingAgent", mode="Demo")
    result = agent.run({"destination": "Rome"})
    assert "booking" in result
    assert isinstance(result["booking"], list)


# ----------------------------
# Agents do not mutate the shared state object
# ----------------------------

def test_agents_do_not_mutate_input_state():
    """
    Regression test: agents used to mutate-and-return the shared orchestrator
    state, which caused a self-referential cycle once the orchestrator stored
    the result back under state[agent_name]. Agents must instead return a
    fresh dict and leave the input state untouched.
    """
    state = dict(TRIP_STATE)
    original_keys = set(state.keys())

    HotelAgent("HotelAgent", mode="Demo").run(state)
    FoodAgent("FoodAgent", mode="Demo").run(state)
    WeatherAgent("WeatherAgent", mode="Demo").run(state)
    TransportAgent("TransportAgent", mode="Demo").run(state)
    FlightAgent("FlightAgent", mode="Demo").run(state)

    assert set(state.keys()) == original_keys, (
        "Agent run() must not add keys to the shared state dict it was given"
    )


# ----------------------------
# Orchestration Logic
# ----------------------------

def test_anita_orchestration():
    anita = ANITA(dict(TRIP_STATE), mode="Demo")
    results = anita.orchestrate(traveler_type="general")

    assert "hotel" in results
    assert "food" in results
    assert "tour" in results
    assert "flight" in results
    assert "transport" in results
    assert "weather" in results

    assert results["hotel"]["hotels"]
    assert results["food"]["restaurants"]
    assert results["flight"]["flights"]
    assert results["transport"]["transport"]
    assert results["weather"]["weather"]
    assert results["tour"]["tour_summary"]["tours"]


def test_anita_orchestration_no_self_reference():
    """The self-referential state cycle bug must not resurface."""
    import json
    anita = ANITA(dict(TRIP_STATE), mode="Demo")
    results = anita.orchestrate(traveler_type="general")
    # json.dumps will raise ValueError on circular references
    json.dumps(results, default=str)


def test_anita_impact_assessment_present():
    anita = ANITA(dict(TRIP_STATE), mode="Demo")
    results = anita.orchestrate(traveler_type="general")
    assert "impact_assessment" in results
    assert "error" not in results["impact_assessment"]
    assert "impact_narrative" in results
    assert isinstance(results["impact_narrative"], str)


def test_anita_routes_wired():
    """RouteManager must be active, not the old `self.routes = None` stub."""
    anita = ANITA(dict(TRIP_STATE), mode="Demo")
    assert anita.routes is not None
    assert anita.routes.route("hotel", anita.state_manager.state) is True


# ----------------------------
# Resilience & Error Handling
# ----------------------------

def test_missing_destination():
    agent = HotelAgent("HotelAgent", mode="Demo")
    result = agent.run({})
    assert "error" in result


def test_missing_origin_destination_flight():
    agent = FlightAgent("FlightAgent", mode="Demo")
    result = agent.run({"origin": "Delhi"})
    assert "error" in result


def test_orchestration_continues_if_agent_missing_state():
    """
    If some required state is missing for one agent, orchestrate() should
    still complete and simply skip that agent (via RouteManager), rather than
    crashing the whole run.
    """
    partial_state = {"destination": "Rome"}  # no origin -> flight/transport skipped
    anita = ANITA(partial_state, mode="Demo")
    results = anita.orchestrate(traveler_type="general")
    assert "hotel" in results
    assert "flight" not in results  # skipped: no origin
    assert "impact_assessment" in results


def test_api_fallback_cache():
    clear_cache()
    response = call_api("google_maps", {"origin": "Rome", "dest": "Vatican"})
    cached_response = call_api("google_maps", {"origin": "Rome", "dest": "Vatican"})  # cache hit
    assert response == cached_response


# ----------------------------
# RAG Pipeline (Demo mode - fully offline)
# ----------------------------

def test_youtube_rag_demo_mode():
    from rag.youtube_rag import query_videos, summarize_results
    result = query_videos("Rome", ["food"], mode="Demo")
    assert "insights" in result
    summary = summarize_results(result, mode="Demo")
    assert isinstance(summary, list)
    assert len(summary) > 0


def test_sim_currency_rag_demo_mode():
    from rag.sim_currency_rag import query_entries, summarize_results
    result = query_entries("Rome", mode="Demo")
    assert "insights" in result
    summary = summarize_results(result, mode="Demo")
    assert isinstance(summary, list)


def test_visa_rag_demo_mode():
    from rag.visa_rag import query_requirements, summarize_results
    result = query_requirements("Italy", mode="Demo")
    assert "insights" in result
    summary = summarize_results(result, mode="Demo")
    assert isinstance(summary, list)


# ----------------------------
# Efficiency Tracking
# ----------------------------

def test_token_logging():
    log_tokens("TestAgent", 100, 50)
    assert get_usage("TestAgent") >= 150
    assert "TestAgent" in get_all_usage()


def test_cache_savings():
    clear_cache()
    call_api("maps", {"origin": "Rome", "dest": "Vatican"})
    call_api("maps", {"origin": "Rome", "dest": "Vatican"})  # cache hit
    assert savings_percent() > 0
