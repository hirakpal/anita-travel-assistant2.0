"""Tests for the event-parsing sub-agent logic (utils.parsers.parse_events_output)."""
from utils.parsers import parse_events_output


def test_parse_events_output_basic():
    raw = "Diwali Festival\nCelebration in the city center\n\nJazz Night\nLive music downtown"
    events = parse_events_output(raw)

    assert isinstance(events, list)
    assert len(events) == 2
    assert events[0]["name"] == "Diwali Festival"
    assert events[1]["name"] == "Jazz Night"
    # Regression: Event model previously had no default for Optional
    # fields, causing "Field required" validation errors that silently
    # dropped every event. Confirm these optional fields are present (as
    # None) rather than raising.
    assert events[0]["price_range"] is None
    assert events[0]["reviews"] is None


def test_parse_events_output_empty_string():
    events = parse_events_output("")
    assert events == []


def test_tour_agent_demo_includes_events():
    from agents.tour_agent import TourAgent

    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": "Jaipur"})
    assert "events" in result["tour_summary"]
    assert isinstance(result["tour_summary"]["events"], list)
