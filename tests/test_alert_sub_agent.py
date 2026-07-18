"""Tests for the alert-parsing sub-agent logic (utils.parsers.parse_alerts_output)."""
from utils.parsers import parse_alerts_output


def test_parse_alerts_output_basic():
    raw = "Heatwave advisory in effect\nRoad closure near Amber Fort"
    alerts = parse_alerts_output(raw)

    assert isinstance(alerts, list)
    assert len(alerts) == 2
    for alert in alerts:
        assert alert["type"] == "General"
        assert "message" in alert
        assert alert["message"]


def test_parse_alerts_output_ignores_blank_lines():
    raw = "Flight delayed\n\n\nStrike planned tomorrow"
    alerts = parse_alerts_output(raw)
    assert len(alerts) == 2


def test_parse_alerts_output_empty_string():
    alerts = parse_alerts_output("")
    assert alerts == []


def test_tour_agent_demo_includes_alerts():
    """TourAgent aggregates alerts alongside tours/events/locations/news."""
    from agents.tour_agent import TourAgent

    agent = TourAgent("TourAgent", mode="Demo")
    result = agent.run({"destination": "Jaipur"})
    assert "alerts" in result["tour_summary"]
    assert isinstance(result["tour_summary"]["alerts"], list)
