#agents/flight_agent.py
import os
import logging
import requests
from rag.youtube_rag import query_videos, summarize_results
from prompts.flight_prompt import FLIGHT_PROMPT
from utils.parsers import parse_flights_output

logger = logging.getLogger(__name__)

# Helper functions (can be moved to utils.py)
CITY_TO_IATA = {
    "Mumbai": "BOM",
    "Bengaluru": "BLR",
    "Tokyo": "HND",
    "Singapore": "SIN",
    "New York": "JFK"
}

def _city_to_iata(city: str) -> str:
    if not city:
        return ""
    return CITY_TO_IATA.get(city.strip(), city.strip().upper()[:3])

def _google_flights_url(origin: str, dest: str, start: str | None, end: str | None) -> str:
    from urllib.parse import quote_plus
    q = f"Flights from {origin} to {dest}"
    if start:
        q += f" on {start}"
    return f"https://www.google.com/travel/flights?q={quote_plus(q)}"

def _is_passenger_airline(name: str) -> bool:
    banned = ["cargo","freight","logistics","courier","express","blue dart","fedex","ups","dhl"]
    return not any(b in (name or "").lower() for b in banned)


class FlightAgent:
    def __init__(self, name="FlightAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt = FLIGHT_PROMPT

    def _call_gemini(self, prompt, origin, destination, constraint=None):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        text = f"{prompt}\nOrigin: {origin}\nDestination: {destination}"
        if constraint:
            text += f"\nConstraint: {constraint}"

        try:
            resp = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers={"x-goog-api-key": api_key},
                json={"contents": [{"parts": [{"text": text}]}]},
                timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except requests.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise

    def run(self, state):
        """
        Reads from `state` (read-only) and returns a fresh result dict.
        Does not mutate/return the shared `state` object.
        """
        if not all(k in state for k in ["origin", "destination", "arrival_time", "departure_time"]):
            return {"error": "Origin, destination, arrival, or departure time missing"}

        origin = state["origin"]
        destination = state["destination"]
        constraint = state.get("constraint")

        # Demo mode → stubbed flights only
        if self.mode == "Demo":
            return {
                "flights": [
                    {
                        "airline": "Demo Airlines",
                        "route": f"{origin} → {destination}",
                        "price_range": "$500",
                        "constraint_applied": constraint or "none"
                    }
                ],
                "vlog_insights": ["🎬 Demo vlog: Flight booking experience"]
            }

        try:
            # Online mode → Gemini call with prompt + constraint
            flights_text = self._call_gemini(
                self.prompt,
                origin,
                destination,
                constraint
            )

            # Parse Gemini output into structured flights
            flights = parse_flights_output(flights_text)

            # Enrich with AviationStack API
            flights = self._enrich_with_api(flights, origin, destination, state)

            # Append vlog insights via RAG
            rag_results = query_videos(destination, ["flights"], mode=self.mode)
            vlog_insights = summarize_results(rag_results, mode=self.mode)

            return {"flights": flights, "vlog_insights": vlog_insights}

        except requests.RequestException as e:
            logger.error(f"Network error fetching flights: {e}")
            return {
                "flights": [],
                "vlog_insights": [],
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.exception("Unexpected error fetching flights")
            return {
                "flights": [],
                "vlog_insights": [],
                "error": f"Unable to fetch flight data: {str(e)}"
            }

    def _enrich_with_api(self, flights, origin, destination, state):
        api_key = os.getenv("AVIATIONSTACK_API_KEY")
        if not api_key:
            return flights

        origin_iata = (origin or "").upper()
        dest_iata = _city_to_iata(destination)

        params = {"access_key": api_key, "dep_iata": origin_iata, "arr_iata": dest_iata, "limit": 20}
        try:
            resp = requests.get("http://api.aviationstack.com/v1/flights", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("data", []) or []

            api_url_map = {}
            for f in data:
                airline_name = (f.get("airline") or {}).get("name") or ""
                if not _is_passenger_airline(airline_name):
                    continue
                url = _google_flights_url(origin_iata, dest_iata, state.get("start_date"), state.get("end_date"))
                api_url_map[(airline_name.lower(), origin_iata, dest_iata)] = url

            enriched = []
            for f in flights:
                airline = (f.get("airline") or "").strip()
                key = (airline.lower(), origin_iata, dest_iata)
                if key in api_url_map:
                    f["url"] = api_url_map[key]
                enriched.append(f)
            return enriched

        except Exception as e:
            logger.warning(f"AviationStack enrichment failed: {e!r}")
            return flights
