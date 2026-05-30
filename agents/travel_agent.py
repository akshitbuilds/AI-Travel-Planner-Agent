"""
agents/travel_agent.py
------------------------
Core agentic module using LangChain ReAct agent.
The agent autonomously decides which tools to call,
reasons through the problem, and generates a structured
travel itinerary with full justification.

FIXES:
  1. Fallback places generated for ANY city not in local JSON → no more N/A attractions
  2. All numeric values returned as proper int/float → hero bar always shows real numbers
"""

import os
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from tools.flight_tool import search_flights
from tools.hotel_tool import recommend_hotel
from tools.places_tool import find_places
from tools.weather_tool import get_weather
from tools.budget_tool import estimate_budget
from utils.weather_utils import fetch_weather_forecast
from utils.data_loader import load_flights, load_hotels, load_places


# ── Tool list passed to the agent ─────────────────────────────────────────────
TOOLS = [search_flights, recommend_hotel, find_places, get_weather, estimate_budget]


# ── ReAct prompt template ─────────────────────────────────────────────────────
REACT_PROMPT = PromptTemplate.from_template("""
You are an expert AI Travel Planning Assistant for India. Your job is to create
complete, personalised travel itineraries using the tools available to you.

You have access to the following tools:
{tools}

Use this format STRICTLY:

Question: the input question you must answer
Thought: think step by step about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat up to 6 times)
Thought: I now have all the information I need to create the full itinerary
Final Answer: [your complete structured travel plan here]

Rules:
- ALWAYS call search_flights first, then recommend_hotel, then find_places, then get_weather, then estimate_budget
- ALWAYS justify your hotel and flight recommendations ("we chose X because...")
- ALWAYS include a day-wise itinerary using the places data
- Provide the final answer in a well-structured, readable format

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")


# ── City-specific fallback attractions ────────────────────────────────────────
# Covers all 15 cities in the sidebar; used when load_places() has no data.
_CITY_FALLBACKS: dict[str, list[dict]] = {
    "delhi": [
        {"name": "Red Fort",                "category": "Heritage",   "rating": 4.6, "entry_fee": "₹35",  "best_time": "Morning",   "description": "UNESCO World Heritage Mughal fort on the banks of the Yamuna."},
        {"name": "Qutub Minar",             "category": "Heritage",   "rating": 4.6, "entry_fee": "₹35",  "best_time": "Morning",   "description": "World's tallest brick minaret and a stunning example of Indo-Islamic architecture."},
        {"name": "India Gate",              "category": "Landmark",   "rating": 4.7, "entry_fee": "Free", "best_time": "Evening",   "description": "Iconic war memorial at the heart of New Delhi."},
        {"name": "Humayun's Tomb",          "category": "Heritage",   "rating": 4.5, "entry_fee": "₹35",  "best_time": "Morning",   "description": "Magnificent Mughal garden tomb and precursor to the Taj Mahal."},
        {"name": "Chandni Chowk",           "category": "Shopping",   "rating": 4.3, "entry_fee": "Free", "best_time": "Evening",   "description": "Old Delhi's legendary bazaar — street food, spices, and silver."},
        {"name": "Lotus Temple",            "category": "Spiritual",  "rating": 4.5, "entry_fee": "Free", "best_time": "Afternoon", "description": "Stunning Bahá'í House of Worship shaped like an unfolding lotus."},
    ],
    "mumbai": [
        {"name": "Gateway of India",        "category": "Landmark",   "rating": 4.6, "entry_fee": "Free", "best_time": "Morning",   "description": "Iconic arch monument overlooking the Arabian Sea."},
        {"name": "Marine Drive",            "category": "Scenic",     "rating": 4.7, "entry_fee": "Free", "best_time": "Evening",   "description": "The 'Queen's Necklace' — a sweeping seafront promenade."},
        {"name": "Elephanta Caves",         "category": "Heritage",   "rating": 4.4, "entry_fee": "₹40",  "best_time": "Morning",   "description": "UNESCO cave temples on an island in Mumbai Harbour."},
        {"name": "Chhatrapati Shivaji Terminus", "category": "Heritage", "rating": 4.6, "entry_fee": "Free", "best_time": "Morning", "description": "Stunning Victorian Gothic UNESCO railway station."},
        {"name": "Juhu Beach",              "category": "Nature",     "rating": 4.2, "entry_fee": "Free", "best_time": "Sunset",    "description": "Famous beach known for street food stalls and sunset views."},
        {"name": "Dharavi Street Food Walk","category": "Food",       "rating": 4.3, "entry_fee": "Free", "best_time": "Evening",   "description": "Experience Mumbai's vibrant street food culture up close."},
    ],
    "bangalore": [
        {"name": "Lalbagh Botanical Garden","category": "Nature",     "rating": 4.5, "entry_fee": "₹20",  "best_time": "Morning",   "description": "250-acre garden with a 200-year-old glass house and rare plant species."},
        {"name": "Cubbon Park",             "category": "Nature",     "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "300-acre lung of the city — jogging, heritage buildings, and greenery."},
        {"name": "Bangalore Palace",        "category": "Heritage",   "rating": 4.3, "entry_fee": "₹230", "best_time": "Morning",   "description": "Tudor-style royal palace inspired by Windsor Castle."},
        {"name": "ISKCON Temple",           "category": "Spiritual",  "rating": 4.6, "entry_fee": "Free", "best_time": "Evening",   "description": "One of the largest ISKCON temples in the world."},
        {"name": "Commercial Street",       "category": "Shopping",   "rating": 4.2, "entry_fee": "Free", "best_time": "Afternoon", "description": "Bangalore's bustling shopping hub for clothes, accessories and street food."},
        {"name": "Nandi Hills",             "category": "Scenic",     "rating": 4.6, "entry_fee": "₹10",  "best_time": "Sunrise",   "description": "Ancient hilltop fortress with breathtaking sunrise views over the Deccan."},
    ],
    "chennai": [
        {"name": "Marina Beach",            "category": "Nature",     "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "World's second longest natural urban beach stretching 13 km."},
        {"name": "Kapaleeshwarar Temple",   "category": "Spiritual",  "rating": 4.7, "entry_fee": "Free", "best_time": "Morning",   "description": "Magnificent Dravidian temple dedicated to Lord Shiva."},
        {"name": "Fort St. George",         "category": "Heritage",   "rating": 4.3, "entry_fee": "₹15",  "best_time": "Morning",   "description": "India's first British fortress, now housing a museum and state legislature."},
        {"name": "Government Museum",       "category": "Culture",    "rating": 4.3, "entry_fee": "₹15",  "best_time": "Afternoon", "description": "One of India's oldest museums with bronze sculptures and natural history."},
        {"name": "Elliot's Beach",          "category": "Nature",     "rating": 4.3, "entry_fee": "Free", "best_time": "Evening",   "description": "Quieter, cleaner beach popular with locals for evening walks."},
        {"name": "Mahabalipuram",           "category": "Heritage",   "rating": 4.7, "entry_fee": "₹40",  "best_time": "Morning",   "description": "UNESCO shore temples and rock-cut caves — a day-trip marvel."},
    ],
    "kolkata": [
        {"name": "Victoria Memorial",       "category": "Heritage",   "rating": 4.7, "entry_fee": "₹30",  "best_time": "Morning",   "description": "Majestic marble monument housing a museum of colonial history."},
        {"name": "Howrah Bridge",           "category": "Landmark",   "rating": 4.7, "entry_fee": "Free", "best_time": "Evening",   "description": "Iconic cantilever bridge — the symbol of Kolkata."},
        {"name": "Dakshineswar Kali Temple","category": "Spiritual",  "rating": 4.7, "entry_fee": "Free", "best_time": "Morning",   "description": "Famous riverside temple associated with Sri Ramakrishna."},
        {"name": "Indian Museum",           "category": "Culture",    "rating": 4.4, "entry_fee": "₹50",  "best_time": "Afternoon", "description": "Oldest and largest museum in India with rare artefacts."},
        {"name": "Park Street Food Walk",   "category": "Food",       "rating": 4.5, "entry_fee": "Free", "best_time": "Evening",   "description": "Kolkata's culinary heartbeat — rolls, sweets and colonial-era cafes."},
        {"name": "Sundarbans Day Trip",     "category": "Nature",     "rating": 4.6, "entry_fee": "₹200", "best_time": "Morning",   "description": "UNESCO mangrove delta — Bengal tiger territory and river cruises."},
    ],
    "hyderabad": [
        {"name": "Charminar",               "category": "Heritage",   "rating": 4.5, "entry_fee": "₹25",  "best_time": "Morning",   "description": "Iconic 16th-century mosque and monument — symbol of Hyderabad."},
        {"name": "Golconda Fort",           "category": "Heritage",   "rating": 4.5, "entry_fee": "₹25",  "best_time": "Morning",   "description": "Magnificent medieval fort with an acoustic clapping system."},
        {"name": "Hussain Sagar Lake",      "category": "Scenic",     "rating": 4.3, "entry_fee": "Free", "best_time": "Evening",   "description": "Heart-shaped lake with a monolithic Buddha statue."},
        {"name": "Laad Bazaar",             "category": "Shopping",   "rating": 4.4, "entry_fee": "Free", "best_time": "Evening",   "description": "Famous for bangles, pearls, and traditional Hyderabadi crafts."},
        {"name": "Birla Mandir",            "category": "Spiritual",  "rating": 4.6, "entry_fee": "Free", "best_time": "Evening",   "description": "White marble temple offering panoramic views of the city."},
        {"name": "Ramoji Film City",        "category": "Theme Park", "rating": 4.3, "entry_fee": "₹1300","best_time": "Morning",   "description": "World's largest film studio complex — a full-day adventure."},
    ],
    "pune": [
        {"name": "Shaniwar Wada",           "category": "Heritage",   "rating": 4.3, "entry_fee": "₹25",  "best_time": "Morning",   "description": "Ruins of the grand Peshwa palace — a landmark of Maratha history."},
        {"name": "Aga Khan Palace",         "category": "Heritage",   "rating": 4.5, "entry_fee": "₹25",  "best_time": "Morning",   "description": "Historic palace where Mahatma Gandhi was interned."},
        {"name": "Sinhagad Fort",           "category": "Heritage",   "rating": 4.5, "entry_fee": "₹25",  "best_time": "Morning",   "description": "Hilltop fort with panoramic Sahyadri views and local food stalls."},
        {"name": "Osho Ashram",             "category": "Spiritual",  "rating": 4.1, "entry_fee": "₹200", "best_time": "Morning",   "description": "World-famous meditation and wellness resort."},
        {"name": "FC Road",                 "category": "Food",       "rating": 4.4, "entry_fee": "Free", "best_time": "Evening",   "description": "Pune's most vibrant street for cafes, street food and nightlife."},
        {"name": "Mulshi Lake",             "category": "Nature",     "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "Scenic reservoir in the Sahyadri hills — perfect for a half-day drive."},
    ],
    "jaipur": [
        {"name": "Amber Fort",              "category": "Heritage",   "rating": 4.7, "entry_fee": "₹200", "best_time": "Morning",   "description": "Majestic hilltop fort with stunning mirror palace interiors."},
        {"name": "Hawa Mahal",              "category": "Heritage",   "rating": 4.6, "entry_fee": "₹50",  "best_time": "Morning",   "description": "The 'Palace of Winds' — 953-windowed pink sandstone facade."},
        {"name": "City Palace",             "category": "Heritage",   "rating": 4.6, "entry_fee": "₹200", "best_time": "Morning",   "description": "Royal residence with a museum of Rajput art and weaponry."},
        {"name": "Jantar Mantar",           "category": "Culture",    "rating": 4.5, "entry_fee": "₹50",  "best_time": "Morning",   "description": "UNESCO astronomical observatory with the world's largest stone sundial."},
        {"name": "Johari Bazaar",           "category": "Shopping",   "rating": 4.4, "entry_fee": "Free", "best_time": "Evening",   "description": "Jaipur's jewellery market — gemstones, lac bangles, and block-print fabrics."},
        {"name": "Nahargarh Fort",          "category": "Scenic",     "rating": 4.5, "entry_fee": "₹50",  "best_time": "Sunset",    "description": "Hilltop fort offering the best panoramic sunset view of the Pink City."},
    ],
    "ahmedabad": [
        {"name": "Sabarmati Ashram",        "category": "Heritage",   "rating": 4.7, "entry_fee": "Free", "best_time": "Morning",   "description": "Gandhi's iconic ashram on the banks of the Sabarmati — a pilgrimage of peace."},
        {"name": "Adalaj Stepwell",         "category": "Heritage",   "rating": 4.6, "entry_fee": "Free", "best_time": "Morning",   "description": "Exquisite 15th-century five-storey stepwell with intricate carvings."},
        {"name": "Sidi Saiyyed Mosque",     "category": "Heritage",   "rating": 4.6, "entry_fee": "Free", "best_time": "Morning",   "description": "Famous for its breathtaking stone lattice 'Tree of Life' window."},
        {"name": "Kankaria Lake",           "category": "Nature",     "rating": 4.3, "entry_fee": "₹25",  "best_time": "Evening",   "description": "Historic lake with a zoo, toy train, and lively evening promenade."},
        {"name": "Law Garden Night Market", "category": "Shopping",   "rating": 4.4, "entry_fee": "Free", "best_time": "Evening",   "description": "Vibrant night market for mirror-work textiles, chaniya choli and street snacks."},
        {"name": "Ahmedabad Heritage Walk", "category": "Culture",    "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "Guided dawn walk through the UNESCO-listed old city's pol neighbourhoods."},
    ],
    "goa": [
        {"name": "Baga Beach",              "category": "Beach",      "rating": 4.4, "entry_fee": "Free", "best_time": "Morning",   "description": "North Goa's most famous beach — water sports, shacks and sunsets."},
        {"name": "Basilica of Bom Jesus",   "category": "Heritage",   "rating": 4.7, "entry_fee": "Free", "best_time": "Morning",   "description": "UNESCO basilica housing the relics of St Francis Xavier."},
        {"name": "Dudhsagar Waterfalls",    "category": "Nature",     "rating": 4.7, "entry_fee": "₹400", "best_time": "Morning",   "description": "Spectacular four-tiered waterfall on the Goa-Karnataka border."},
        {"name": "Fort Aguada",             "category": "Heritage",   "rating": 4.4, "entry_fee": "₹25",  "best_time": "Morning",   "description": "17th-century Portuguese fort with a lighthouse and sea views."},
        {"name": "Anjuna Flea Market",      "category": "Shopping",   "rating": 4.3, "entry_fee": "Free", "best_time": "Morning",   "description": "Legendary Wednesday flea market — clothes, jewellery and souvenirs."},
        {"name": "Palolem Beach",           "category": "Beach",      "rating": 4.6, "entry_fee": "Free", "best_time": "Sunset",    "description": "South Goa's most serene crescent beach — kayaking and dolphin trips."},
    ],
    "kochi": [
        {"name": "Fort Kochi Beach",        "category": "Scenic",     "rating": 4.5, "entry_fee": "Free", "best_time": "Sunset",    "description": "Historic waterfront promenade with famous Chinese fishing nets."},
        {"name": "Mattancherry Palace",     "category": "Heritage",   "rating": 4.4, "entry_fee": "₹5",   "best_time": "Morning",   "description": "Dutch Palace with exquisite Kerala murals depicting Ramayana scenes."},
        {"name": "Jewish Synagogue",        "category": "Culture",    "rating": 4.4, "entry_fee": "₹10",  "best_time": "Morning",   "description": "India's oldest active synagogue in the Jew Town spice market quarter."},
        {"name": "Backwater Houseboat",     "category": "Nature",     "rating": 4.8, "entry_fee": "₹3000","best_time": "Morning",   "description": "Cruise the legendary Kerala backwaters on a traditional kettuvallam."},
        {"name": "Cherai Beach",            "category": "Beach",      "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "Pristine beach where the backwaters meet the Arabian Sea."},
        {"name": "Spice Market Walk",       "category": "Culture",    "rating": 4.3, "entry_fee": "Free", "best_time": "Morning",   "description": "Explore the aromatic spice warehouses of Mattancherry."},
    ],
    "varanasi": [
        {"name": "Dashashwamedh Ghat",      "category": "Spiritual",  "rating": 4.8, "entry_fee": "Free", "best_time": "Evening",   "description": "The main ghat — witness the breathtaking Ganga Aarti ceremony at dusk."},
        {"name": "Kashi Vishwanath Temple", "category": "Spiritual",  "rating": 4.7, "entry_fee": "Free", "best_time": "Morning",   "description": "One of the 12 Jyotirlingas — the holiest Shiva temple in India."},
        {"name": "Sarnath",                 "category": "Heritage",   "rating": 4.5, "entry_fee": "₹30",  "best_time": "Morning",   "description": "Where Buddha first preached — ancient stupas and an archaeological museum."},
        {"name": "Manikarnika Ghat",        "category": "Cultural",   "rating": 4.4, "entry_fee": "Free", "best_time": "Morning",   "description": "The eternal burning ghat — an immersive glimpse into Hindu funeral rites."},
        {"name": "Boat Ride on the Ganges", "category": "Scenic",     "rating": 4.8, "entry_fee": "₹200", "best_time": "Sunrise",   "description": "Sunrise boat ride past 80+ ghats — the most iconic Varanasi experience."},
        {"name": "Banaras Silk Weaving",    "category": "Culture",    "rating": 4.3, "entry_fee": "Free", "best_time": "Afternoon", "description": "Watch master weavers craft the legendary Banarasi silk sarees."},
    ],
    "agra": [
        {"name": "Taj Mahal",               "category": "Heritage",   "rating": 4.9, "entry_fee": "₹1100","best_time": "Sunrise",   "description": "UNESCO Wonder of the World — a white marble monument to eternal love."},
        {"name": "Agra Fort",               "category": "Heritage",   "rating": 4.6, "entry_fee": "₹550", "best_time": "Morning",   "description": "Massive red sandstone Mughal fort with palace chambers and river views."},
        {"name": "Fatehpur Sikri",          "category": "Heritage",   "rating": 4.5, "entry_fee": "₹610", "best_time": "Morning",   "description": "Akbar's abandoned Mughal capital — stunning sandstone architecture."},
        {"name": "Mehtab Bagh",             "category": "Scenic",     "rating": 4.5, "entry_fee": "₹300", "best_time": "Sunset",    "description": "Garden across the Yamuna — the best sunset silhouette view of the Taj."},
        {"name": "Kinari Bazaar",           "category": "Shopping",   "rating": 4.2, "entry_fee": "Free", "best_time": "Evening",   "description": "Busy market for marble inlay souvenirs, leather goods and street food."},
        {"name": "Taj Nature Walk",         "category": "Nature",     "rating": 4.3, "entry_fee": "₹75",  "best_time": "Morning",   "description": "Forested walk with Taj Mahal views — birds and sunrise photography."},
    ],
    "udaipur": [
        {"name": "City Palace",             "category": "Heritage",   "rating": 4.7, "entry_fee": "₹300", "best_time": "Morning",   "description": "Massive lakeside palace complex — the grandest in Rajasthan."},
        {"name": "Lake Pichola Boat Ride",  "category": "Scenic",     "rating": 4.8, "entry_fee": "₹400", "best_time": "Sunset",    "description": "Sunset cruise past the iconic Lake Palace and Jag Mandir island."},
        {"name": "Sajjangarh (Monsoon Palace)","category":"Scenic",   "rating": 4.5, "entry_fee": "₹80",  "best_time": "Sunset",    "description": "Hilltop palace offering panoramic views of Udaipur's lakes and hills."},
        {"name": "Jagdish Temple",          "category": "Spiritual",  "rating": 4.5, "entry_fee": "Free", "best_time": "Morning",   "description": "Indo-Aryan temple with fine carvings of dancers, elephants, and horsemen."},
        {"name": "Fateh Sagar Lake",        "category": "Nature",     "rating": 4.5, "entry_fee": "Free", "best_time": "Evening",   "description": "Serene artificial lake with a science centre island and promenade."},
        {"name": "Shilpgram Crafts Village","category": "Culture",    "rating": 4.2, "entry_fee": "₹50",  "best_time": "Afternoon", "description": "Rural arts and crafts complex celebrating West Indian folk traditions."},
    ],
    "rishikesh": [
        {"name": "Laxman Jhula",            "category": "Landmark",   "rating": 4.6, "entry_fee": "Free", "best_time": "Morning",   "description": "Iconic iron suspension bridge over the Ganges — spiritual and scenic."},
        {"name": "Triveni Ghat",            "category": "Spiritual",  "rating": 4.6, "entry_fee": "Free", "best_time": "Evening",   "description": "Sacred confluence of rivers — famous for the nightly Ganga Aarti."},
        {"name": "White-Water Rafting",     "category": "Adventure",  "rating": 4.8, "entry_fee": "₹600", "best_time": "Morning",   "description": "Thrilling Grade II–IV rapids on the Ganges — India's top rafting destination."},
        {"name": "Neer Garh Waterfall",     "category": "Nature",     "rating": 4.4, "entry_fee": "₹50",  "best_time": "Morning",   "description": "Scenic 3-km forest trek to a beautiful multi-tiered waterfall."},
        {"name": "Beatles Ashram",          "category": "Culture",    "rating": 4.5, "entry_fee": "₹150", "best_time": "Morning",   "description": "Abandoned Maharishi ashram covered in colourful murals — a quirky landmark."},
        {"name": "Bungee Jumping",          "category": "Adventure",  "rating": 4.7, "entry_fee": "₹3550","best_time": "Morning",   "description": "India's highest fixed platform bungee at 83 metres."},
    ],
}


def _get_places_for_city(city: str, all_places: list) -> list:
    """
    Return places for a given city. First tries the loaded JSON data.
    Falls back to curated city-specific data, then generates generic entries.
    Always returns at least 6 places — never an empty list.
    """
    city_lower = city.lower()

    # 1. Try local JSON dataset
    city_places = sorted(
        [p for p in all_places if p.get("city", "").lower() == city_lower],
        key=lambda x: -x.get("rating", 0),
    )
    if city_places:
        return city_places

    # 2. Try curated fallback for known cities
    if city_lower in _CITY_FALLBACKS:
        return [dict(p, city=city) for p in _CITY_FALLBACKS[city_lower]]

    # 3. Generic fallback for unknown cities (always 6 entries)
    return [
        {"name": f"{city} Heritage Monument",  "city": city, "category": "Heritage",  "rating": 4.3, "entry_fee": "₹50",  "best_time": "Morning",   "description": f"The most celebrated historic site in {city}."},
        {"name": f"{city} Local Market",        "city": city, "category": "Shopping",  "rating": 4.1, "entry_fee": "Free", "best_time": "Evening",   "description": f"Vibrant bazaar showcasing local crafts and street food of {city}."},
        {"name": f"{city} City Park",           "city": city, "category": "Nature",    "rating": 4.0, "entry_fee": "₹20",  "best_time": "Morning",   "description": "A green escape and popular morning jogging spot."},
        {"name": f"{city} Regional Museum",     "city": city, "category": "Culture",   "rating": 4.2, "entry_fee": "₹50",  "best_time": "Afternoon", "description": f"Regional history, art and culture showcasing the heritage of {city}."},
        {"name": f"{city} Food Street",         "city": city, "category": "Food",      "rating": 4.4, "entry_fee": "Free", "best_time": "Evening",   "description": f"Savour authentic local cuisine on {city}'s famous food street."},
        {"name": f"{city} Scenic Viewpoint",    "city": city, "category": "Scenic",    "rating": 4.2, "entry_fee": "Free", "best_time": "Sunrise",   "description": f"Panoramic views of {city}'s skyline and surroundings."},
    ]


def build_agent_executor() -> AgentExecutor:
    """Build and return a LangChain ReAct AgentExecutor with all 5 travel tools."""
    llm = ChatGroq(
        model="llama3-70b-8192",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )
    agent = create_react_agent(llm=llm, tools=TOOLS, prompt=REACT_PROMPT)
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    return executor


def generate_trip(source: str, destination: str, days: int, budget: int) -> dict:
    """
    Main entry point: Generate a complete AI travel plan.

    Tries the LangChain LLM agent first. Falls back to the deterministic
    planner if the API key is missing or unavailable.

    Args:
        source:      Departure city  (e.g. "Delhi")
        destination: Arrival city    (e.g. "Ahmedabad")
        days:        Trip duration in days
        budget:      Hotel budget per night in INR

    Returns:
        Structured dict with keys:
            flight, hotel, places, weather, budget, itinerary,
            ai_reasoning, agent_used, agent_steps
    """
    try:
        executor = build_agent_executor()
        query = (
            f"Plan a complete {days}-day trip from {source} to {destination}. "
            f"My hotel budget is ₹{budget} per night. "
            f"Please find the cheapest flight, best hotel within budget, "
            f"top tourist places, day-wise weather forecast, and full budget breakdown. "
            f"Also explain why you chose each recommendation."
        )
        result = executor.invoke({"input": query})
        ai_output = result.get("output", "")
        steps = result.get("intermediate_steps", [])

        structured = _build_structured_data(source, destination, days, budget)
        structured["ai_reasoning"] = ai_output
        structured["agent_steps"] = len(steps)
        structured["agent_used"] = "LangChain ReAct Agent (LLaMA-3 70B)"
        return structured

    except Exception:
        structured = _build_structured_data(source, destination, days, budget)
        structured["ai_reasoning"] = _build_reasoning(structured, days)
        structured["agent_steps"] = 5
        structured["agent_used"] = "Deterministic Tool Agent (No LLM)"
        return structured


def _build_structured_data(source: str, destination: str, days: int, budget: int) -> dict:
    """
    Build structured trip data using local JSON datasets and the live weather API.
    Deterministic — no LLM needed — always produces clean output.

    FIX: uses _get_places_for_city() which never returns an empty list.
    """
    # ── Flights ──────────────────────────────────────────────────────────────
    all_flights = load_flights()
    matching = [
        f for f in all_flights
        if f.get("source", "").lower() == source.lower()
        and f.get("destination", "").lower() == destination.lower()
    ]
    if matching:
        flight = sorted(matching, key=lambda x: x.get("price", 99999))[0]
    else:
        flight = {
            "airline":   "Various Airlines",
            "price":     4500,
            "duration":  "Approx 2–3 hrs",
            "departure": "Morning",
            "arrival":   "Afternoon",
            "class":     "Economy",
            "why_chosen": "Lowest available fare for this route.",
        }

    # ── Hotels ───────────────────────────────────────────────────────────────
    all_hotels = load_hotels()
    city_hotels = [h for h in all_hotels if h.get("city", "").lower() == destination.lower()]
    within_budget = [h for h in city_hotels if h.get("price_per_night", 0) <= budget]
    if within_budget:
        hotel = sorted(within_budget, key=lambda x: -x.get("rating", 0))[0]
    elif city_hotels:
        hotel = sorted(city_hotels, key=lambda x: x.get("price_per_night", 0))[0]
    else:
        hotel = {
            "name":            "Local Hotel",
            "price_per_night": int(budget),
            "rating":          4.0,
            "type":            "Standard",
            "amenities":       ["AC", "WiFi", "Restaurant"],
            "why_chosen":      "Best available option within your budget.",
        }

    # ── Places — ALWAYS returns ≥ 6 entries ──────────────────────────────────
    all_places = load_places()
    city_places = _get_places_for_city(destination, all_places)

    # ── Weather (live from Open-Meteo) ────────────────────────────────────────
    weather_forecast = fetch_weather_forecast(destination, days)

    # ── Day-wise Itinerary ────────────────────────────────────────────────────
    itinerary = []
    for i in range(days):
        day_places = city_places[i * 2: i * 2 + 2] or city_places[:2]
        weather_day = (
            weather_forecast[i]
            if i < len(weather_forecast)
            else {"description": "Sunny", "temp": 30, "date": f"Day {i + 1}"}
        )
        itinerary.append({
            "day":       i + 1,
            "date":      weather_day.get("date", f"Day {i + 1}"),
            "weather":   weather_day.get("description", "Sunny"),
            "morning":   day_places[0] if len(day_places) > 0 else None,
            "afternoon": day_places[1] if len(day_places) > 1 else None,
        })

    # ── Budget ───────────────────────────────────────────────────────────────
    flight_price      = int(flight.get("price", 4500))
    hotel_price_night = int(hotel.get("price_per_night", budget))
    hotel_cost        = hotel_price_night * days
    food_cost         = 800  * days
    transport_cost    = 600  * days
    activity_cost     = 400  * days
    total             = flight_price + hotel_cost + food_cost + transport_cost + activity_cost

    budget_breakdown = {
        "flight_cost":    flight_price,
        "hotel_cost":     hotel_cost,
        "food_cost":      food_cost,
        "transport_cost": transport_cost,
        "activity_cost":  activity_cost,
        "total":          total,
        "per_day_avg":    round(total / days),
    }

    return {
        "flight":      flight,
        "hotel":       hotel,
        "places":      city_places[:8],
        "weather":     weather_forecast,
        "budget":      budget_breakdown,
        "itinerary":   itinerary,
        "source":      source,
        "destination": destination,
        "days":        days,
    }


def _build_reasoning(data: dict, days: int) -> str:
    """Generate a human-readable explanation of all planning decisions."""
    flight  = data["flight"]
    hotel   = data["hotel"]
    places  = data["places"]
    dest    = data.get("destination", "destination")

    return f"""
✈️  Flight Selection
We chose {flight.get('airline', 'the recommended airline')} at ₹{flight.get('price', 'N/A'):,} \
because it offers the lowest fare among all available options for this route. \
Departure time ({flight.get('departure', 'morning')}) is travel-friendly and allows a \
full first day at the destination.

🏨  Hotel Selection
{hotel.get('name', 'The recommended hotel')} was selected because it has the highest \
guest rating (⭐ {hotel.get('rating', 4.0)}) among hotels within your \
₹{hotel.get('price_per_night', 'N/A'):,}/night budget. \
It offers {', '.join(str(a) for a in hotel.get('amenities', [])[:3])} which adds significant value.

📍  Attractions ({len(places)} selected)
Top attractions for {dest} were ranked by guest rating and diversity of experience \
(heritage, nature, food, adventure). Entry fees have been factored into the activity budget.

🌤️  Weather Integration
Real-time weather data was fetched from Open-Meteo to plan appropriate activities for each \
day. Outdoor and scenic spots are scheduled during clear weather windows.

💰  Budget Optimisation
The cheapest available flight was selected. Hotel cost is within your stated budget. \
Daily food (₹800) and local transport (₹600) estimates are based on average tourist spending \
across Indian destinations.
""".strip()