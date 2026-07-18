#agents/hotel_agent.py
import os
import logging
import requests
from rag.youtube_rag import query_videos, summarize_results
from prompts.hotel_prompt import HOTEL_PROMPT

logger = logging.getLogger(__name__)


class HotelAgent:
    def __init__(self, name="HotelAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt = HOTEL_PROMPT

    def run(self, state):
        """
        Reads from `state` (read-only) and returns a fresh result dict with
        this agent's own output. It deliberately does NOT mutate or return
        the shared `state` object itself - doing so would let the orchestrator
        create a self-referential cycle when storing results under state[name].
        """
        if not state.get("destination"):
            return {"error": "Destination missing"}

        destination = state["destination"]

        # DEMO MODE → stubbed hotels only
        if self.mode == "Demo":
            return {
                "hotels": [
                    {"name": "Demo Hotel", "location": "City Center", "price_range": "$100"}
                ],
                "vlog_insights": ["🎬 Demo vlog: Hotel booking highlights"]
            }

        # ONLINE MODE → Gemini API
        hotels = []
        if self.provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                hotels = [{"error": "GOOGLE_API_KEY not configured"}]
            else:
                try:
                    resp = requests.post(
                        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                        headers={"x-goog-api-key": api_key},
                        json={
                            "contents": [{
                                "parts": [{
                                    "text": f"{self.prompt}\nDestination: {destination}\nTraveler profile: {state.get('profile','General')}"
                                }]
                            }]
                        },
                        timeout=15
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    output_text = data["candidates"][0]["content"]["parts"][0]["text"]

                    # For now, store raw Gemini output. Later, parse into structured JSON.
                    hotels = [{"raw_output": output_text}]
                except requests.RequestException as e:
                    logger.error(f"Gemini API error in HotelAgent: {e!r}")
                    hotels = [{"error": "Unable to fetch hotels from Gemini"}]
                except (KeyError, IndexError) as e:
                    logger.error(f"Unexpected Gemini response shape in HotelAgent: {e!r}")
                    hotels = [{"error": "Unexpected response from Gemini"}]

        # Append YouTube RAG insights
        try:
            rag_results = query_videos(destination, ["hotels"], mode=self.mode)
            vlog_insights = summarize_results(rag_results, mode=self.mode)
        except Exception as e:
            logger.error(f"RAG lookup failed in HotelAgent: {e!r}")
            vlog_insights = []

        return {"hotels": hotels, "vlog_insights": vlog_insights}
