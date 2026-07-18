# ANITA — AI Travel Orchestrator & Planner

ANITA coordinates a set of specialized agents (hotel, food, tour, flight, transport, weather, impact assessment, booking) behind a single orchestrator to plan and adapt a trip end-to-end, with a Streamlit UI on top.

Runs fully offline in **Demo mode** — no API keys, no network access, no external services required. **Online mode** connects to Gemini, Google Maps/Weather, AviationStack, and Pinecone for live data.

## Architecture

```
streamlit_ui.py / main.py          UI layer (Streamlit)
        │
orchestrator/anita.py              ANITA orchestrator - fans out to agents,
        │                          runs impact assessment, applies alternates
        ├── orchestrator/state_manager.py   shared trip state + routing checks
        ├── orchestrator/routes.py          RouteManager: which agents can run,
        │                                   and alternate-routing on risk/budget/
        │                                   accessibility/sustainability flags
        │
        ├── agents/hotel_agent.py
        ├── agents/food_agent.py
        ├── agents/tour_agent.py            bundles tours + alerts + events +
        │                                   locations + news sub-outputs
        ├── agents/flight_agent.py          + AviationStack enrichment
        ├── agents/transport_agent.py
        ├── agents/weather_agent.py         Google Weather or Open-Meteo
        ├── agents/impact_assessment_agent.py  sustainability/risk/wellbeing/
        │                                   cultural fit/budget/accessibility/
        │                                   health/time/group-dynamics report
        └── agents/booking_agent.py         only runs after user confirmation
        │
        ├── prompts/*.py                    per-agent Gemini prompt templates
        ├── rag/*.py                        Pinecone-backed enrichment (YouTube
        │                                   vlogs, SIM/currency, visa info) -
        │                                   lazily initialized, Demo-safe
        └── utils/*.py                      parsers, pydantic models, cache,
                                             token tracking
```

### Design notes

- **Every agent's `run(state)` reads `state` but returns a fresh result dict** — it never mutates or returns the shared state object itself. (An earlier version did this, which created a self-referential cycle once the orchestrator stored an agent's output back under `state[agent_name]`.)
- **RAG modules (`rag/youtube_rag.py`, `rag/sim_currency_rag.py`, `rag/visa_rag.py`) lazily initialize Pinecone and the embedding model** on first Online-mode use only, so importing them — and any agent that imports them — never requires network access or a model download in Demo mode.
- **`RouteManager` (orchestrator/routes.py)** decides which agents can run given the current trip state, and proposes alternate agents to re-run when `ImpactAssessmentAgent` flags budget, accessibility, sustainability, or risk issues.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables (Online mode only)

Copy `.env.example` to `.env` and fill in the keys you have. Demo mode needs none of these.

| Variable | Used by |
|---|---|
| `GOOGLE_API_KEY` | Gemini calls in hotel/food/tour/flight/transport/booking agents |
| `GOOGLE_MAPS_API_KEY` | Weather agent (Google Weather provider) |
| `AVIATIONSTACK_API_KEY` | Flight agent enrichment |
| `PINECONE_API_KEY`, `PINECONE_HOST` | RAG modules (YouTube/SIM-currency/visa vector search) |

## Running

```bash
# Recommended: full UI
streamlit run streamlit_ui.py

# Minimal reference UI
streamlit run main.py
```

Or use the launcher scripts, which set up a venv and install dependencies automatically:

```bash
./run.sh        # Mac/Linux
run.bat         # Windows
```

Select **Demo** mode in the sidebar/radio to try it with zero configuration.

## Standalone demo scripts

Two offline, non-interactive scripts exercise the orchestrator directly (no Streamlit needed):

```bash
python -m demo.pre_trip_demo                 # pre-trip planning walkthrough
python -m demo.pre_trip_demo --trip demo-002 # a different trip from demo/mock_data.json

python -m demo.ongoing_trip_demo             # mid-trip disruption + alternate routing
```

## Tests

```bash
pip install pytest
pytest tests/ -v
```

All 38 tests run in Demo mode and require no network access or API keys. They cover: per-agent output shape, the state-mutation regression (agents must not leak keys into the shared state dict), full orchestration (including the alternate-routing path), routing/skip behavior when required state is missing, the RAG modules' Demo-mode paths, the in-memory API cache, token tracking, and the free-text parsers in `utils/parsers.py`.

## Modes

| Mode | Behavior |
|---|---|
| `Demo` | Every agent returns realistic stubbed data. Fully offline. No API keys needed. |
| `Online` | Agents call Gemini/Google/AviationStack/Pinecone for live data, with graceful fallback to an `{"error": ...}` result per agent on failure (the orchestrator logs the failure and continues with the remaining agents rather than crashing the whole run). |

## Known limitations

- `TourAgent` intentionally bundles five concerns (tours, alerts, events, locations, news) behind one agent rather than five separate agents — this keeps the Gemini call count and orchestration graph simpler at the cost of single-responsibility purity.
- Free-text parsing in `utils/parsers.py` uses regex heuristics against Gemini's raw text output for hotels/food/transport/booking; it is not guaranteed to parse every possible Gemini response shape. Flights, alerts, events, locations, news, and tours are parsed either from structured JSON or a more robust chunking strategy.
- `BookingAgent` is intentionally excluded from the main `orchestrate()` loop — it only runs via `ANITA.finalize_booking(itinerary, user_confirmation)` after explicit user approval.
