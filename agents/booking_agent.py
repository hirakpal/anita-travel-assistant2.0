#agents/booking_agent.py
import logging
from utils.parsers import parse_booking_output
from prompts.booking_prompt import BOOKING_PROMPT
from utils.gemini_client import call_gemini

logger = logging.getLogger(__name__)

class BookingAgent:
    def __init__(self, name="BookingAgent", mode="Online", provider="gemini"):
        self.name = name
        self.mode = mode
        self.provider = provider
        self.prompt = BOOKING_PROMPT

    def run(self, state):
        # DEMO MODE → stubbed booking only
        if self.mode == "Demo":
            return {
                "booking": [
                    {
                        "confirmation": "DEMO123",
                        "cancellation_policy": "Demo: Free cancellation until 72 hours",
                        "payment_options": ["Credit Card", "PayPal"],
                        "reviews": {
                            "rating": 4.5,
                            "highlights": ["Demo booking process smooth", "Refunds handled"]
                        },
                        "status": "Demo reservations confirmed for hotel, tours, flights."
                    }
                ]
            }

        # ONLINE MODE → Gemini API
        if self.provider == "gemini":
            try:
                output_text = call_gemini(f"{self.prompt}\nState: {state}")

                # Parse Gemini output into structured list of bookings
                parsed_bookings = parse_booking_output(output_text)
                return {"booking": parsed_bookings}

            except ValueError as e:
                return {"booking": [{"error": str(e)}]}
            except Exception as e:
                logger.error(f"Gemini API error in BookingAgent: {e!r}")
                return {"booking": [{"error": "Unable to fetch booking confirmation from Gemini"}]}
