# ✈️ AI Travel Planner Agent

An **Agentic AI** travel planning assistant built with **LangChain ReAct Agent**, **Python**, and **Streamlit**.
The system autonomously plans complete trips by calling 5 specialised AI tools — searching flights, recommending hotels,
discovering places, fetching live weather, and estimating budget.

---

## 🎯 Problem Statement

Planning a trip requires coordinating flights, hotels, attractions, weather, and budget across multiple websites.
This project solves that by building a single intelligent agent that handles all of it autonomously,
reasoning step-by-step like a human travel expert.

---

## 🚀 Live Demo

Deploy on [Streamlit Cloud](https://streamlit.io/cloud) — connect your GitHub repo and add your `OPENAI_API_KEY` in Secrets.

> **Note:** The app works even without an OpenAI key using the built-in deterministic fallback agent.

---

## 🤖 Architecture

```
LangChain ReAct Agent
  ├── Tool 1: search_flights      → flights.json (cheapest flight selection)
  ├── Tool 2: recommend_hotel     → hotels.json  (highest-rated within budget)
  ├── Tool 3: find_places         → places.json  (top-rated attractions)
  ├── Tool 4: get_weather         → Open-Meteo API (live day-by-day forecast)
  └── Tool 5: estimate_budget     → Computed from all tool outputs
```

The agent uses **ReAct (Reason + Act)** prompting — it thinks before each action and justifies every decision.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| AI Framework | LangChain (ReAct Agent) |
| LLM | OpenAI GPT-3.5-turbo |
| Weather API | Open-Meteo (free, no key) |
| Frontend | Streamlit |
| Data | JSON datasets (flights, hotels, places) |

---

## 📁 Project Structure

```
AI-Travel-Planner-Agent/
│
├── agents/
│   ├── __init__.py
│   └── travel_agent.py        # LangChain ReAct agent + fallback planner
│
├── tools/
│   ├── __init__.py
│   ├── flight_tool.py         # @tool — search & rank flights
│   ├── hotel_tool.py          # @tool — recommend hotels by rating/budget
│   ├── places_tool.py         # @tool — discover top attractions
│   ├── weather_tool.py        # @tool — live weather from Open-Meteo
│   └── budget_tool.py         # @tool — full cost breakdown
│
├── data/
│   ├── flights.json           # Flight dataset (20+ routes)
│   ├── hotels.json            # Hotel dataset (25+ hotels, 8 cities)
│   └── places.json            # Tourist places (30+ POIs, 8 cities)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py         # JSON data loading utilities
│   └── weather_utils.py       # Open-Meteo API integration + city coords
│
├── app.py                     # Streamlit frontend (tabbed UI)
├── requirements.txt           # Python dependencies
├── .env.example               # API key template
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

### 3. Set up API key (optional)
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```
> Get a free key at [platform.openai.com](https://platform.openai.com). The app works without it too.

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🗺️ Supported Cities

| Route | Destinations |
|-------|-------------|
| Sources | Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Kolkata |
| Destinations | Goa, Jaipur, Shimla, Mumbai, Bangalore, Hyderabad |

---

## 🌟 Key Features

- **LangChain ReAct Agent** — autonomous multi-step reasoning
- **5 LangChain @tool functions** — each independently testable
- **Cheapest flight selection** — filtered and ranked from dataset
- **Best hotel ranking** — highest rating within user's budget
- **Live weather forecast** — real daily forecasts via Open-Meteo API
- **Day-wise itinerary** — morning + afternoon activities per day
- **AI reasoning output** — agent explains every decision made
- **Tabbed Streamlit UI** — Flight/Hotel | Itinerary | Weather | Budget | Reasoning
- **Graceful fallback** — works without OpenAI key using deterministic agent
- **Full error handling** — try/except on all tool calls and API requests

---

## 📊 Sample Output

```
Your 3-Day Trip to Goa (Delhi → Goa)

Flight Selected:
  SpiceJet — ₹4,200 | Duration: 2h 50m | Dep: 14:00
  Reason: Lowest price among 4 available flights

Hotel Recommended:
  Sea View Resort — ₹3,200/night ⭐4.5 | Pool, Beach Access, Spa
  Reason: Highest rated within ₹5,000/night budget

Day 1: Baga Beach (Morning) + Fort Aguada (Afternoon)
Day 2: Basilica of Bom Jesus (Morning) + Dudhsagar Waterfall (Afternoon)
Day 3: Spice Plantation Tour (Morning) + Old Goa Heritage Walk (Afternoon)

Budget:  Flight ₹4,200 + Hotel ₹9,600 + Food ₹2,400 + Transport ₹1,800 + Activities ₹1,200
Total:   ₹19,200
```

---

## 🔮 Future Improvements

- Real-time flight APIs (Skyscanner, Aviasales)
- Hotel booking integration (Booking.com API)
- Google Maps route planning
- PDF itinerary export
- Multi-city trip planning
- User preference memory

---

## 👨‍💻 Developed By

**Akshit Agrawal**  
Agentic AI Internship Project — Travel/Tourism Domain  
Built with Python · LangChain · Streamlit · Open-Meteo API