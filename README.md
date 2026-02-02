<div align="center">
	<h1>Travel Planner (Multi‑Agent) – with Google ADK & uv</h1>
	<p><em>An experimental multi‑agent travel concierge that researches destinations, surfaces events & nearby places, and inspires trip ideas using Google ADK + open geodata.</em></p>
</div>

## Overview

This project demonstrates a lightweight travel planning assistant built on the **Google Agent Development Kit (ADK)**. It composes several specialized agents (news, places, inspiration, search grounding) into a root planner that can:

* Suggest destinations & trip ideas
* Surface relevant travel news / events (web grounded)
* Find nearby places (hotels, cafes, landmarks) using OpenStreetMap (no API key required)
* Geocode and contextualize location information

The environment & dependency management use **[uv](https://github.com/astral-sh/uv)** for fast, reliable Python workflows.

## Key Features

* Multi‑agent orchestration via Google ADK `Agent` and `AgentTool`
* Web search grounding (Google ADK search tool wrapper)
* Free nearby place lookup powered by Overpass + Nominatim (OpenStreetMap)
* Composable inspiration agent that internally invokes `news_agent` + `places_agent`
* Python 3.11+, minimal dependencies (`geopy`, `google-adk`, `python-dotenv`)

## Architecture

```
root_agent (travel_planner_main)
		└─ travel_inspiration_agent
					├─ news_agent  (uses google_search_grounding tool)
					└─ places_agent (uses location_search_tool -> Overpass + Nominatim)

Tools:
	google_search_grounding -> wraps a search agent providing bullet-point grounded results
	location_search_tool    -> FunctionTool: find_nearby_places_open(query, location, radius, limit)
```

### Agents & Tools Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| `root_agent` | `travel_planner/agent.py` | Entry point orchestration agent (delegates to inspiration) |
| `travel_inspiration_agent` | `travel_planner/supporting_agents.py` | Guides destination discovery, calls news & places agents |
| `news_agent` | `travel_planner/supporting_agents.py` | Fetches events/news (search grounded) |
| `places_agent` | `travel_planner/supporting_agents.py` | Suggests specific places given a query |
| `google_search_grounding` | `travel_planner/tools.py` | AgentTool wrapping search agent for concise bullet results |
| `location_search_tool` | `travel_planner/tools.py` | Free OSM nearby place finder |

## Prerequisites

* Python 3.11+
* macOS / Linux / (Windows via WSL) recommended
* A Google API key (for ADK models/tools) – store it in `.env` as `GOOGLE_API_KEY=...`
* Homebrew (optional) for installing `uv`

## Setup (via uv)

Install `uv` (choose one):

```bash
brew install uv            # macOS (Homebrew)
curl -LsSf https://astral.sh/uv/install.sh | sh  # universal script
```

Create & activate a virtual environment:

```bash
uv venv .venv
source .venv/bin/activate  # zsh/bash
```

Sync dependencies from `pyproject.toml`:

```bash
uv sync
```

(If you later add dependencies: `uv add package_name` or edit `pyproject.toml` then run `uv sync` again.)

### Environment Variables

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

Load it automatically with `python-dotenv` (already listed as a dependency).

## Running the Project

Simple sanity check:

```bash
uv run python main.py
```

Using agents directly (interactive example in a Python REPL):

```python
from travel_planner.agent import root_agent

query = "Family-friendly summer trip in Europe near beaches"
response = root_agent.run(query)
print(response)
```

Calling the inspiration agent’s sub-tools explicitly:

```python
from travel_planner.supporting_agents import travel_inspiration_agent

travel_inspiration_agent.run("Find boutique hotels near the Eiffel Tower")
```

## Extending

* Add a budgeting tool – integrate currency conversion or cost estimation.
* Plug in itinerary serialization (export to JSON / Markdown).
* Add caching layer for repeated geocode / Overpass queries.
* Introduce rate limiting & graceful fallback when Overpass is slow.

## Error Handling & Edge Cases

* Missing geocode results – returns a helpful message instead of raising.
* Overpass API throttling – current code returns status error; consider retries/backoff.
* Empty search queries – ensure you validate user inputs before invoking agents.

## Project Structure

```
travel-planner-with-adk/
├── main.py
├── pyproject.toml
├── README.md
└── travel_planner/
		├── agent.py
		├── supporting_agents.py
		├── tools.py
		└── __pycache__/ (ignored)
```

## Development Workflow Cheatsheet

```bash
# Add a dependency
uv add rich

# Update existing lock & install
uv sync

# Run a module
uv run python -m travel_planner.agent

# Export pinned requirements (optional)
uv export --format requirements-txt > requirements.txt
```

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| `ModuleNotFoundError` | venv not activated | `source .venv/bin/activate` |
| Slow Overpass responses | Rate limiting | Implement retry/backoff; reduce radius |
| Empty search results | Query too specific | Broaden terms (e.g., use "hotel" instead of brand) |
| ADK auth failures | Missing/invalid API key | Check `.env` and environment export |

## License

No explicit license provided yet. Consider adding an OSS license (e.g., MIT) for clarity.

## Disclaimer

This is an experimental prototype; responses may contain inaccuracies. Always verify critical travel details (visa, safety advisories, etc.).

---


