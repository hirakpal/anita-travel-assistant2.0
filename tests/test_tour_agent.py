"""Tests for TourAgent (tours, alerts, events, locations, news bundled together)."""
import pytest

from agents.tour_agent import TourAgent


def test_tour_agent_demo_mode_shape():
    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": "Jaipur"})

    assert "tour_summary" in result
    summary = result["tour_summary"]
    for key in ["tours", "alerts", "events", "locations", "news"]:
        assert key in summary
        assert isinstance(summary[key], list)


def test_tour_agent_missing_destination():
    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({})
    assert "error" in result


def test_tour_agent_uses_all_five_prompts():
    """
    TourAgent bundles five distinct concerns (tours, alerts, events,
    locations, news) behind one agent. Verify all five prompt templates
    are wired up so Online mode would actually query each of them.
    """
    agent = TourAgent("TourAgent", mode="Demo")
    assert agent.prompt_tours
    assert agent.prompt_alerts
    assert agent.prompt_events
    assert agent.prompt_locations
    assert agent.prompt_news


@pytest.mark.parametrize("destination", ["Rome", "Jaipur", "Tokyo"])
def test_tour_agent_demo_mode_various_destinations(destination):
    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": destination})
    assert result["tour_summary"]["tours"]
