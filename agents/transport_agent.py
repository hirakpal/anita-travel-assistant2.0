#agents/transport_agent.py
import os
import logging
import requests
from rag.sim_currency_rag import query_entries, summarize_results
from prompts.transport_prompt import TRANSPORT_PROMPT
from utils.gemini_client import call_gemini

logger = logging.getLogger(__name__)


class TransportAgent:
    def __init__(self, name="TransportAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt = TRANSPORT_PROMPT

    def run(self, state):
        """
        Reads from `state` (read-only) and returns a fresh result dict.
        Does not mutate/return the shared `state` object.
        """
        if not state.get("origin") or not state.get("destination"):
            return {"error": "Origin or destination missing"}

        origin = state["origin"]
        destination = state["destination"]

        # DEMO MODE → stubbed transport only
        if self.mode == "Demo":
            return {
                "transport": [
                    {"mode": "Demo Cab", "duration": "15 min", "price_range": "$10"}
                ],
                "utility_insights": ["🎬 Demo SIM info: Prepaid SIM available at airport"]
            }

        # ONLINE MODE → Gemini API + RAG
        transport = []
        if self.provider == "gemini":
            try:
                output_text = call_gemini(f"{self.prompt}\nOrigin: {origin}\nDestination: {destination}")
                # For now, store raw Gemini output. Later, parse into structured JSON.
                transport = [{"raw_output": output_text}]
            except ValueError as e:
                transport = [{"error": str(e)}]
            except requests.RequestException as e:
                logger.error(f"Gemini API error in TransportAgent: {e!r}")
                transport = [{"error": "Unable to fetch transport options from Gemini"}]
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected Gemini response shape in TransportAgent: {e!r}")
                transport = [{"error": "Unexpected response from Gemini"}]

        # Append SIM/Currency RAG insights
        try:
            rag_results = query_entries(destination, ["transport"], mode=self.mode)
            utility_insights = summarize_results(rag_results, mode=self.mode)
        except Exception as e:
            logger.error(f"RAG lookup failed in TransportAgent: {e!r}")
            utility_insights = []

        return {"transport": transport, "utility_insights": utility_insights}
