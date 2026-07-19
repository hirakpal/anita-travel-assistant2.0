#agents/tour_agent.py
import logging
from utils.parsers import (
    parse_tours_output,
    parse_alerts_output,
    parse_events_output,
    parse_locations_output,
    parse_news_output
)
from prompts.tour_prompt import TOUR_PROMPT
from prompts.alerts_prompt import ALERTS_PROMPT
from prompts.events_prompt import EVENTS_PROMPT
from prompts.locations_prompt import LOCATIONS_PROMPT
from prompts.news_prompt import NEWS_PROMPT
from utils.gemini_client import call_gemini

logger = logging.getLogger(__name__)

class TourAgent:
    def __init__(self, name="TourAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt_tours = TOUR_PROMPT
        self.prompt_alerts = ALERTS_PROMPT
        self.prompt_events = EVENTS_PROMPT
        self.prompt_locations = LOCATIONS_PROMPT
        self.prompt_news = NEWS_PROMPT

    def _call_gemini(self, prompt, destination):
        return call_gemini(f"{prompt}\nDestination: {destination}")

    def run(self, state):
        if not state.get("destination"):
            return {"error": "Destination missing"}

        if self.mode == "Demo":
            return {
                "tour_summary": {
                    "tours": [{"name": "Demo Tour", "type": "Cultural"}],
                    "alerts": [{"type": "General", "message": "Demo alert"}],
                    "events": [{"name": "Demo Event"}],
                    "locations": [{"name": "Demo Location"}],
                    "news": [{"headline": "Demo News"}]
                }
            }

        try:
            # Tours
            tours_text = self._call_gemini(self.prompt_tours, state["destination"])
            tours = parse_tours_output(tours_text)

            # Alerts
            alerts_text = self._call_gemini(self.prompt_alerts, state["destination"])
            alerts = parse_alerts_output(alerts_text)

            # Events
            events_text = self._call_gemini(self.prompt_events, state["destination"])
            events = parse_events_output(events_text)

            # Locations
            locations_text = self._call_gemini(self.prompt_locations, state["destination"])
            locations = parse_locations_output(locations_text)

            # News
            news_text = self._call_gemini(self.prompt_news, state["destination"])
            news = parse_news_output(news_text)

            return {
                "tour_summary": {
                    "tours": tours,
                    "alerts": alerts,
                    "events": events,
                    "locations": locations,
                    "news": news
                }
            }

        except Exception as e:
            logger.error(f"Gemini API error in TourAgent: {e!r}")
            return {"tour_summary": {"error": "Unable to fetch tour data"}}
