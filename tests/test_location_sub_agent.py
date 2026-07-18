"""Tests for the location-parsing sub-agent logic (utils.parsers.parse_locations_output)."""
from utils.parsers import parse_locations_output


def test_parse_locations_output_basic():
    raw = "Amber Fort\nHistoric hilltop fort with stunning architecture"
    locations = parse_locations_output(raw)

    assert isinstance(locations, list)
    assert len(locations) == 1
    assert locations[0]["name"] == "Amber Fort"
    assert locations[0]["type"] == "Landmark"
    # Regression: Location model previously had no default for the
    # Optional "reviews" field, causing "Field required" validation
    # errors that silently dropped every location.
    assert locations[0]["reviews"] is None


def test_parse_locations_output_multiple():
    raw = "Hawa Mahal\nPalace of Winds\n\nCity Palace\nRoyal residence"
    locations = parse_locations_output(raw)
    assert len(locations) == 2


def test_parse_locations_output_empty_string():
    locations = parse_locations_output("")
    assert locations == []


def test_tour_agent_demo_includes_locations():
    from agents.tour_agent import TourAgent

    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": "Jaipur"})
    assert "locations" in result["tour_summary"]
    assert isinstance(result["tour_summary"]["locations"], list)
