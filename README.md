# ✈️ AI Travel Planner Agent

An **Agentic AI** travel planning assistant built with **LangChain ReAct Agent**, **Python**, and **Streamlit**.  
The system autonomously plans complete trips by calling 5 specialised AI tools — searching flights,
recommending hotels, discovering attractions, fetching live weather, and estimating the full budget.

---

## 🎯 Problem Statement

Planning a trip requires coordinating flights, hotels, attractions, weather, and budget across
multiple websites. Travellers switch between apps, compare inconsistent information, and manually
build itineraries that are often inefficient or incomplete.

This project solves that with a single intelligent agent that handles everything autonomously,
reasoning step-by-step like a human travel expert.

---

## 🚀 Live Demo

🔗 **[Click here to open the app](https://ai-travel-planner-agent.streamlit.app)**

> The app works even without a Groq key using the built-in **deterministic fallback agent**.

---

## 🤖 Architecture

```
User Query (Streamlit UI)
        │
        ▼
LangChain ReAct Agent  ←──  Groq LLaMA-3 70B (LLM)
        │
        ├── Tool 1: search_flights    →  flights.json  (cheapest flight)
        ├── Tool 2: recommend_hotel   →  hotels.json   (highest-rated in budget)
        ├── Tool 3: find_places       →  places.json   (top attractions)
        ├── Tool 4: get_weather       →  Open-Meteo API (live forecast, free)
        └── Tool 5: estimate_budget   →  Computed from all tool outputs
                │
                ▼
        Structured Trip Plan
        (Streamlit Tabbed UI)
```

The agent uses **ReAct (Reason + Act)** prompting — it thinks before every action and
justifies every recommendation.

---

## 🛠️ Tech Stack

| Component      | Technology                        |
|----------------|-----------------------------------|
| Language       | Python 3.10+                      |
| AI Framework   | LangChain (ReAct Agent)           |
| LLM            | Groq — LLaMA-3 70B (free tier)   |
| Weather API    | Open-Meteo (free, no key needed)  |
| Frontend       | Streamlit                         |
| Data           | JSON datasets (flights / hotels / places) |

---

## 📁 Project Structure

```
AI-Travel-Planner-Agent/
│
├── agents/
│   ├── __init__.py
│   └── travel_agent.py        # LangChain ReAct agent + deterministic fallback
│
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py         # @tool — search & rank flights by price
│   ├── hotel_tool.py          # @tool — recommend hotels by rating/budget
│   ├── places_tool.py         # @tool — discover top attractions
│   ├── weather_tool.py        # @tool — live forecast via Open-Meteo
│   └── budget_tool.py         # @tool — full cost breakdown
│
├── data/
│   ├── flights.json           # Flight dataset (routes across India)
│   ├── hotels.json            # Hotel dataset (multiple cities)
│   └── places.json            # Tourist places / POIs (multiple cities)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # JSON data loading helpers
│   └── weather_utils.py       # Open-Meteo API integration + city coordinates
│
├── app.py                     # Streamlit frontend (tabbed UI)
├── requirements.txt           # Python dependencies
├── .env.example               # API key template (copy → .env)
├── .gitignore                 # Keeps secrets and caches out of Git
└── README.md                  # This file
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/akshitbuilds/AI-Travel-Planner-Agent.git
cd AI-Travel-Planner-Agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your Groq API key
```bash
cp .env.example .env
# Open .env and paste your GROQ_API_KEY
```
> Get a **free** Groq key at [console.groq.com](https://console.groq.com) — no credit card needed.  
> The app works without a key too, using the built-in deterministic fallback.

### 4. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub (already done ✅)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect your repo: `akshitbuilds/AI-Travel-Planner-Agent`
4. Set **Main file**: `app.py`
5. Go to **Advanced settings → Secrets** and add:
```toml
GROQ_API_KEY = "your_actual_groq_key_here"
```
6. Click **Deploy** — your public URL will be ready in ~2 minutes.

---

## 🗺️ Supported Cities

| Role         | Cities                                                                 |
|--------------|------------------------------------------------------------------------|
| Departure    | Delhi, Mumbai, Bangalore, Chennai, Kolkata, Hyderabad, Pune, Jaipur   |
| Destination  | Goa, Jaipur, Agra, Udaipur, Varanasi, Rishikesh, Kochi, Ahmedabad + more |

> Attractions are available for all 15 cities with curated fallback data even when not in the local JSON.

---

## 🌟 Key Features

- **LangChain ReAct Agent** — multi-step autonomous reasoning
- **5 LangChain `@tool` functions** — each independently testable
- **Cheapest flight selection** — filtered and sorted from dataset
- **Best hotel ranking** — highest rating within user's budget
- **Live weather forecast** — real daily forecasts via Open-Meteo API (no key)
- **Day-wise itinerary** — morning + afternoon activity slots per day
- **AI reasoning output** — agent explains every decision it made
- **Tabbed Streamlit UI** — Flight & Hotel | Itinerary | Weather | Budget | AI Reasoning
- **Graceful fallback** — deterministic planner when Groq API unavailable
- **Full error handling** — try/except on all tool calls and API requests
- **No N/A** — curated attraction data for all 15 cities, always shows real count

---

## 📊 Sample Output

```
Your 3-Day Trip to Goa  (Delhi → Goa)

✈️  Flight Selected
    SpiceJet — ₹4,200 | 2h 50m | Dep: 14:00
    Reason: Lowest price among all available flights on this route

🏨  Hotel Recommended
    Sea View Resort — ₹3,200/night ⭐ 4.5 | Pool · Beach Access · Spa
    Reason: Highest rated hotel within your ₹5,000/night budget

📅  Itinerary
    Day 1: Baga Beach (Morning) + Fort Aguada (Afternoon)
    Day 2: Basilica of Bom Jesus (Morning) + Dudhsagar Falls (Afternoon)
    Day 3: Anjuna Flea Market (Morning) + Palolem Beach (Afternoon)

💰  Budget Breakdown
    Flight      ₹4,200
    Hotel       ₹9,600   (3 nights × ₹3,200)
    Food        ₹2,400
    Transport   ₹1,800
    Activities  ₹1,200
    ─────────────────────
    Total       ₹19,200
```

---

## 🔮 Future Improvements

- Real-time flight APIs (Skyscanner, Amadeus)
- Hotel booking integration (Booking.com API)
- Google Maps route planning
- PDF itinerary export
- Multi-city trip planning
- User preference memory across sessions

---

## 📜 Project Context

Built as part of an **Agentic AI Internship** — Travel/Tourism Domain.

**Skills demonstrated:** Python · LangChain · Prompt Engineering · Agentic AI ·
API Integration · Streamlit · JSON Data Handling · ReAct Reasoning

---

## 👨‍💻 Developer

**Akshit Agrawal**  
🔗 [github.com/akshitbuilds](https://github.com/akshitbuilds)