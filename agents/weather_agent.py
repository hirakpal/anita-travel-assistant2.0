#agents/weather_agent.py
import requests
import os
import logging
from rag.youtube_rag import query_videos, summarize_results

logger = logging.getLogger(__name__)


class WeatherAgent:
    def __init__(self, name="WeatherAgent", mode="Online", provider="google"):
        """
        mode: "Online" or "Demo"
        provider: "google" or "open-meteo"
        """
        self.name = name
        self.mode = mode
        self.provider = provider

    def run(self, state):
        """
        Reads from `state` (read-only) and returns a fresh result dict.
        Does not mutate/return the shared `state` object.
        """
        if "destination" not in state or not state.get("destination"):
            return {"error": "Destination missing"}

        destination = state["destination"]

        # Demo mode → stubbed forecast only
        if self.mode == "Demo":
            return {
                "weather": {
                    "forecast": {"temperature": "28°C daytime, 20°C nighttime"},
                    "seasonal_notes": "Summer season, warm but pleasant evenings",
                    "advisories": "No major travel advisories",
                    "reviews": {"rating": 4.3, "highlights": ["July is warm but manageable"]},
                    "recommendation": "Carry light clothing and sunscreen."
                },
                "vlog_insights": ["🎬 Demo vlog: Weather tips for summer travel"]
            }

        # Online mode → choose provider
        if self.provider == "google":
            weather = self._fetch_google_weather(destination)
        else:
            weather = self._fetch_open_meteo(destination)

        # Append YouTube RAG insights
        try:
            rag_results = query_videos(destination, ["weather"], mode=self.mode)
            vlog_insights = summarize_results(rag_results, mode=self.mode)
        except Exception as e:
            logger.error(f"RAG lookup failed in WeatherAgent: {e!r}")
            vlog_insights = []

        return {"weather": weather, "vlog_insights": vlog_insights}

    def _fetch_google_weather(self, destination):
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return {"error": "GOOGLE_MAPS_API_KEY not configured"}
        try:
            resp = requests.get(
                "https://weather.googleapis.com/v1/weather",
                params={
                    "location": destination,
                    "languageCode": "en",
                    "units": "metric",
                    "key": api_key
                },
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            forecast = data.get("currentConditions", {})
            return {
                "forecast": {
                    "temperature": f"{forecast.get('temperature', 'N/A')}°C",
                    "precipitation": forecast.get("precipitation", "N/A"),
                    "wind": f"{forecast.get('windSpeed', 'N/A')} km/h"
                },
                "seasonal_notes": "Live data from Google Weather API",
                "advisories": data.get("alerts", "No major advisories"),
                "reviews": {"rating": 4.6, "highlights": ["Accurate hyperlocal forecasts"]},
                "recommendation": "Plan activities based on live forecast."
            }
        except requests.RequestException as e:
            logger.error(f"Google Weather API error: {e!r}")
            return {"error": "Unable to fetch live weather data"}

    def _fetch_open_meteo(self, destination):
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": destination},
                timeout=10
            ).json()
            lat = geo["results"][0]["latitude"]
            lon = geo["results"][0]["longitude"]
        except Exception as e:
            logger.warning(f"Open-Meteo geocoding failed, using fallback coords: {e!r}")
            lat, lon = 19.0760, 72.8777  # fallback: Mumbai

        try:
            data = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min",
                    "timezone": "auto"
                },
                timeout=10
            ).json()
            max_t = max(data["daily"]["temperature_2m_max"])
            min_t = min(data["daily"]["temperature_2m_min"])
            summary = f"Temperature ranges between {min_t:.1f}°C and {max_t:.1f}°C."
        except Exception as e:
            logger.error(f"Open-Meteo forecast fetch failed: {e!r}")
            summary = "Weather unavailable."

        return {
            "forecast": {"temperature": summary},
            "seasonal_notes": "Live data from Open-Meteo",
            "advisories": "Check local advisories for updates",
            "reviews": {"rating": 4.5, "highlights": ["Weather API data accurate"]},
            "recommendation": "Pack accordingly based on forecast."
        }
