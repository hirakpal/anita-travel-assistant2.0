#agents/food_agent.py
import os
import logging
import requests
from rag.youtube_rag import query_videos, summarize_results
from prompts.food_prompt import FOOD_PROMPT
from utils.gemini_client import call_gemini

logger = logging.getLogger(__name__)


class FoodAgent:
    def __init__(self, name="FoodAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt = FOOD_PROMPT

    def run(self, state):
        """
        Reads from `state` (read-only) and returns a fresh result dict.
        Does not mutate/return the shared `state` object (avoids the
        self-referential cycle that would occur when the orchestrator
        stores this under state[name]).
        """
        if "destination" not in state or not state.get("destination"):
            return {"error": "Destination missing"}

        destination = state["destination"]

        # DEMO MODE → stubbed restaurants only
        if self.mode == "Demo":
            return {
                "restaurants": [
                    {"name": "Demo Eatery", "cuisine": "Street Food", "price_range": "$10–$20"}
                ],
                "vlog_insights": ["🎬 Demo vlog: Street food highlights"]
            }

        # ONLINE MODE → Gemini API
        restaurants = []
        if self.provider == "gemini":
            try:
                output_text = call_gemini(
                    f"{self.prompt}\nDestination: {destination}\nFood preferences: {state.get('preferences','General')}"
                )
                # For now, store raw Gemini output. Later, parse into structured JSON.
                restaurants = [{"raw_output": output_text}]
            except ValueError as e:
                restaurants = [{"error": str(e)}]
            except requests.RequestException as e:
                logger.error(f"Gemini API error in FoodAgent: {e!r}")
                restaurants = [{"error": "Unable to fetch restaurants from Gemini"}]
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected Gemini response shape in FoodAgent: {e!r}")
                restaurants = [{"error": "Unexpected response from Gemini"}]

        # Append YouTube RAG insights
        try:
            rag_results = query_videos(destination, ["food"], mode=self.mode)
            vlog_insights = summarize_results(rag_results, mode=self.mode)
        except Exception as e:
            logger.error(f"RAG lookup failed in FoodAgent: {e!r}")
            vlog_insights = []

        return {"restaurants": restaurants, "vlog_insights": vlog_insights}
