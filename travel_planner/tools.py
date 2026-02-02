from google.adk.tools.google_search_tool import google_search
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

LLM="gemini-2.0-flash-001"

_search_agent = Agent(
    model=LLM,
    name="google_search_wrapped_agent",
    description="An agent providing Google-search grounding capability",
    instruction= """
        Answer the user's question directly using google_search grounding tool; Provide a brief but concise response. 
        Rather than a detail response, provide the immediate actionable item for a tourist or traveler, in a single sentence.
        Do not ask the user to check or look up information for themselves, that's your role; do your best to be informative.
        IMPORTANT: 
        - Always return your response in bullet points
        - Specify what matters to the user
    """,
    tools=[google_search]
)

google_search_grounding = AgentTool(agent=_search_agent)


from google.adk.tools import FunctionTool
from geopy.geocoders import Nominatim
import requests
import certifi

def find_nearby_places_open(query: str, location: str, radius: int = 3000, limit: int = 5) -> str:
    """
    Finds nearby places for any text query using ONLY free OpenStreetMap APIs (no API key needed).
    
    Args:
        query (str): What you’re looking for (e.g., "restaurant", "hospital", "gym", "bar").
        location (str): The city or area to search in.
        radius (int): Search radius in meters (default: 3000).
        limit (int): Number of results to show (default: 5).
    
    Returns:
        str: List of matching place names and addresses.
    """

    try:
        # Step 1: Geocode the location to get coordinates
        geolocator = Nominatim(user_agent="open_place_finder")
        try:
            loc = geolocator.geocode(location, timeout=10)
        except Exception:
            # Fallback: query Nominatim directly using requests with certifi for SSL
            try:
                resp = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": location, "format": "json", "limit": 1},
                    headers={"User-Agent": "open_place_finder"},
                    verify=certifi.where(),
                    timeout=10,
                )
                if resp.status_code != 200:
                    return f"Could not find location '{location}'."
                j = resp.json()
                if not j:
                    return f"Could not find location '{location}'."
                loc = type("L", (), {"latitude": float(j[0]["lat"]), "longitude": float(j[0]["lon"])})
            except Exception as e:
                return f"Could not find location '{location}': {e}"

        if not loc:
            return f"Could not find location '{location}'."

        lat, lon = loc.latitude, loc.longitude

        # Step 2: Query Overpass API for matching places. Try multiple endpoints with certifi verification.
        overpass_urls = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
        ]
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["name"~"{query}", i](around:{radius},{lat},{lon});
          node["amenity"~"{query}", i](around:{radius},{lat},{lon});
          node["shop"~"{query}", i](around:{radius},{lat},{lon});
        );
        out body {limit};
        """

        response = None
        data = None
        for overpass_url in overpass_urls:
            try:
                response = requests.get(overpass_url, params={"data": overpass_query}, timeout=30, verify=certifi.where())
                if response.status_code == 200:
                    data = response.json()
                    break
            except Exception:
                # try next endpoint
                continue

        if data is None:
            status = response.status_code if response is not None else 'no response'
            return f"Overpass API error: {status}"
        elements = data.get("elements", [])
        if not elements:
            return f"No results found for '{query}' near {location}."

        # Step 3: Format results
        output = [f"Top results for '{query}' near {location}:"]
        for el in elements[:limit]:
            name = el.get("tags", {}).get("name", "Unnamed place")
            street = el.get("tags", {}).get("addr:street", "")
            city = el.get("tags", {}).get("addr:city", "")
            full_addr = ", ".join(filter(None, [street, city]))
            output.append(f"- {name} | {full_addr if full_addr else 'Address not available'}")

        return "\n".join(output)

    except Exception as e:
        return f"Error searching for '{query}' near '{location}': {str(e)}"


location_search_tool = FunctionTool(func=find_nearby_places_open)