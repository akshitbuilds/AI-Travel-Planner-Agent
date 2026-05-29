"""
app.py
-------
AI Travel Planner Agent — Streamlit Frontend
Built with LangChain ReAct Agent + 5 AI Tools + Open-Meteo Weather API
"""

import streamlit as st
from agents.travel_agent import generate_trip

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner Agent",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .card {
        background: linear-gradient(135deg, #1a1f2e, #0d1117);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .highlight-card {
        background: linear-gradient(135deg, #0d2137, #0e1117);
        border: 1px solid #1f6feb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .metric-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .tag {
        display: inline-block;
        background: #1f6feb22;
        color: #58a6ff;
        border: 1px solid #1f6feb55;
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 12px;
        margin: 2px;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #1f6feb, #388bfd);
        color: white;
        border: none;
        border-radius: 8px;
        height: 3.2em;
        width: 100%;
        font-size: 16px;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    div.stButton > button:hover { opacity: 0.85; }
    .stMetric { background: #161b22; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✈️ AI Travel Planner")
    st.markdown("*Powered by LangChain + Open-Meteo*")
    st.divider()

    source = st.selectbox(
        "🛫 Departure City",
        ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Kolkata"],
        index=0,
    )

    destination = st.selectbox(
        "🛬 Destination City",
        ["Goa", "Jaipur", "Shimla", "Mumbai", "Bangalore", "Goa", "Hyderabad"],
        index=0,
    )

    days = st.slider("📅 Trip Duration (Days)", min_value=1, max_value=7, value=3)

    budget = st.number_input(
        "💰 Hotel Budget / Night (₹)",
        min_value=1000,
        max_value=25000,
        value=5000,
        step=500,
    )

    st.divider()
    generate_button = st.button("🚀 Generate AI Trip Plan", use_container_width=True)
    st.divider()

    st.markdown("**🤖 AI Tools Used:**")
    st.markdown("""
    - ✈ Flight Search Tool  
    - 🏨 Hotel Recommendation Tool  
    - 📍 Places Discovery Tool  
    - 🌤 Weather Lookup Tool  
    - 💰 Budget Estimation Tool  
    """)

    st.info("Uses free Open-Meteo API for live weather — no API key needed for weather data.")


# ── Main Header ────────────────────────────────────────────────────────────────
st.title("🌍 AI Travel Planner Agent")
st.markdown(
    "An **Agentic AI** system using **LangChain ReAct Agent** with 5 specialised tools. "
    "It autonomously searches flights, recommends hotels, discovers attractions, "
    "fetches real-time weather, and estimates your total budget."
)
st.divider()


# ── Landing Cards (before generation) ─────────────────────────────────────────
if not generate_button:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='card'>
        <h4>🤖 Agentic AI</h4>
        <p>LangChain ReAct agent that reasons step-by-step and decides which tools to call automatically</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='card'>
        <h4>🌤 Live Weather</h4>
        <p>Real-time daily forecasts from Open-Meteo API — accurate weather for every day of your trip</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='card'>
        <h4>💡 Smart Picks</h4>
        <p>Cheapest flights, highest-rated hotels within budget, top-rated attractions — all justified</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 📌 How it works")
    st.markdown("""
    1. **Enter** your source, destination, days, and budget  
    2. **Agent** calls 5 tools in sequence: Flights → Hotels → Places → Weather → Budget  
    3. **Reasoning** is shown explaining why each choice was made  
    4. **Itinerary** is generated day-by-day with live weather for each day  
    """)
    st.stop()


# ── Trip Generation ────────────────────────────────────────────────────────────
with st.spinner(f"🤖 AI Agent is planning your {days}-day trip to {destination}..."):
    try:
        result = generate_trip(source, destination, days, budget)
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
        st.stop()

st.success(f"✅ AI Trip Plan Generated — {source} → {destination} ({days} Days)")

# ── Agent Info Banner ──────────────────────────────────────────────────────────
agent_used = result.get("agent_used", "Tool Agent")
steps = result.get("agent_steps", 5)
st.info(f"🧠 **Agent:** {agent_used} | **Tools invoked:** {steps} reasoning steps completed")


# ── Top Summary Metrics ────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🛫 From", source)
col2.metric("🛬 To", destination)
col3.metric("📅 Duration", f"{days} Days")
col4.metric("💰 Total Est.", f"₹{result['budget']['total']:,}")
st.divider()


# ── TABS Layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✈ Flight & Hotel", "📅 Day-wise Itinerary", "🌤 Weather", "💰 Budget", "🧠 AI Reasoning"
])


# ── TAB 1: Flight & Hotel ──────────────────────────────────────────────────────
with tab1:
    flight = result["flight"]
    hotel = result["hotel"]

    col_f, col_h = st.columns(2)

    with col_f:
        st.markdown("### ✈ Flight Selected")
        st.markdown(f"""
        <div class='highlight-card'>
        <h4 style='color:#58a6ff'>{flight.get('airline', 'N/A')}</h4>
        <p>💰 <b>Price:</b> ₹{flight.get('price', 0):,}</p>
        <p>⏱ <b>Duration:</b> {flight.get('duration', 'N/A')}</p>
        <p>🕐 <b>Departure:</b> {flight.get('departure', 'N/A')} → <b>Arrival:</b> {flight.get('arrival', 'N/A')}</p>
        <p>🪑 <b>Class:</b> {flight.get('class', 'Economy')}</p>
        <p>✅ <b>Why chosen:</b> Lowest price among all available flights on this route.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_h:
        st.markdown("### 🏨 Hotel Recommended")
        amenities_tags = "".join([f"<span class='tag'>{a}</span>" for a in hotel.get("amenities", [])])
        st.markdown(f"""
        <div class='highlight-card'>
        <h4 style='color:#58a6ff'>{hotel.get('name', 'N/A')}</h4>
        <p>💰 <b>Price:</b> ₹{hotel.get('price_per_night', 0):,}/night</p>
        <p>⭐ <b>Rating:</b> {hotel.get('rating', 'N/A')}/5</p>
        <p>🏷 <b>Type:</b> {hotel.get('type', 'N/A')}</p>
        <p>🛎 <b>Amenities:</b> {amenities_tags}</p>
        <p>✅ <b>Why chosen:</b> Highest rated within your ₹{budget:,}/night budget.</p>
        </div>
        """, unsafe_allow_html=True)

    # All available places
    st.markdown("### 📍 Top Attractions in " + destination)
    places = result.get("places", [])
    cols = st.columns(2)
    for i, place in enumerate(places):
        fee = f"₹{place['entry_fee']}" if place.get("entry_fee", 0) > 0 else "Free"
        with cols[i % 2]:
            st.markdown(f"""
            <div class='card'>
            <b>⭐ {place['rating']} &nbsp; {place['name']}</b><br>
            <small>📂 {place['type']} | 🎟 Entry: {fee} | 🕐 Best: {place['best_time']}</small><br>
            <small>{place['description']}</small>
            </div>
            """, unsafe_allow_html=True)


# ── TAB 2: Day-wise Itinerary ─────────────────────────────────────────────────
with tab2:
    st.markdown("### 📅 Day-by-Day Itinerary")
    itinerary = result.get("itinerary", [])

    for day_plan in itinerary:
        with st.expander(
            f"Day {day_plan['day']} — {day_plan.get('date', '')}  |  🌤 {day_plan['weather']}",
            expanded=True,
        ):
            col_m, col_a = st.columns(2)

            morning = day_plan.get("morning")
            afternoon = day_plan.get("afternoon")

            with col_m:
                if morning:
                    fee = f"₹{morning['entry_fee']}" if morning.get("entry_fee", 0) > 0 else "Free"
                    st.markdown(f"""
                    **🌅 Morning Visit**  
                    📍 **{morning['name']}**  
                    📂 {morning['type']} | 🎟 {fee}  
                    _{morning['description']}_
                    """)

            with col_a:
                if afternoon:
                    fee = f"₹{afternoon['entry_fee']}" if afternoon.get("entry_fee", 0) > 0 else "Free"
                    st.markdown(f"""
                    **🌇 Afternoon Visit**  
                    📍 **{afternoon['name']}**  
                    📂 {afternoon['type']} | 🎟 {fee}  
                    _{afternoon['description']}_
                    """)

            if not morning and not afternoon:
                st.info("Free day — rest, explore local markets, or revisit favourite spots.")


# ── TAB 3: Weather ────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f"### 🌤 Live Weather Forecast — {destination}")
    st.caption("Data sourced from Open-Meteo API (free, no API key required)")

    weather = result.get("weather", [])
    weather_cols = st.columns(len(weather)) if weather else [st]

    for i, day in enumerate(weather):
        with weather_cols[i]:
            temp = day.get("temp", 30)
            desc = day.get("description", "Sunny")
            emoji = "☀️" if temp > 30 else ("🌤" if temp > 22 else ("🌥" if temp > 15 else "❄️"))
            st.markdown(f"""
            <div class='metric-box'>
            <div style='font-size:32px'>{emoji}</div>
            <div style='font-weight:600'>Day {day['day']}</div>
            <div style='font-size:12px;color:#8b949e'>{day.get('date', '')}</div>
            <div style='font-size:18px;font-weight:700;color:#58a6ff'>{temp}°C</div>
            <div style='font-size:12px'>{desc.split('(')[0].strip()}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**🌡 Packing Tips Based on Forecast:**")
    all_temps = [d.get("temp", 30) for d in weather]
    avg_temp = sum(all_temps) / len(all_temps) if all_temps else 30
    if avg_temp > 30:
        st.markdown("🌞 Hot weather expected — pack light cotton clothes, sunscreen, and stay hydrated.")
    elif avg_temp > 20:
        st.markdown("🌤 Pleasant weather — light layers are ideal. Carry a light jacket for evenings.")
    else:
        st.markdown("❄ Cool weather expected — pack warm clothes, woolens, and a windproof jacket.")


# ── TAB 4: Budget ─────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 💰 Complete Budget Breakdown")
    budget_data = result["budget"]

    col1, col2, col3 = st.columns(3)
    col1.metric("✈ Flight", f"₹{budget_data['flight_cost']:,}")
    col2.metric("🏨 Hotel Total", f"₹{budget_data['hotel_cost']:,}", f"₹{budget_data['hotel_cost']//days:,}/night")
    col3.metric("🍽 Food", f"₹{budget_data['food_cost']:,}", f"₹{budget_data['food_cost']//days:,}/day")

    col4, col5, col6 = st.columns(3)
    col4.metric("🚕 Transport", f"₹{budget_data['transport_cost']:,}", f"₹{budget_data['transport_cost']//days:,}/day")
    col5.metric("🎟 Activities", f"₹{budget_data['activity_cost']:,}", f"₹{budget_data['activity_cost']//days:,}/day")
    col6.metric("📊 Per Day Avg", f"₹{budget_data['per_day_avg']:,}")

    st.divider()
    st.markdown(f"""
    <div class='highlight-card' style='text-align:center'>
    <h2 style='color:#58a6ff'>💰 Total Estimated Cost</h2>
    <h1 style='color:white'>₹{budget_data['total']:,}</h1>
    <p style='color:#8b949e'>For a {days}-day trip from {source} to {destination}</p>
    </div>
    """, unsafe_allow_html=True)

    # Budget chart using st.bar_chart
    st.markdown("**📊 Spend Distribution**")
    chart_data = {
        "Category": ["Flight", "Hotel", "Food", "Transport", "Activities"],
        "Amount (₹)": [
            budget_data["flight_cost"], budget_data["hotel_cost"],
            budget_data["food_cost"], budget_data["transport_cost"],
            budget_data["activity_cost"],
        ],
    }
    import pandas as pd
    df = pd.DataFrame(chart_data).set_index("Category")
    st.bar_chart(df)


# ── TAB 5: AI Reasoning ───────────────────────────────────────────────────────
with tab5:
    st.markdown("### 🧠 AI Reasoning & Decision Justification")
    st.caption("The agent explains every recommendation made during trip planning.")

    reasoning = result.get("ai_reasoning", "")
    if reasoning:
        st.markdown(reasoning)
    else:
        st.info("No reasoning available for this run.")

    st.divider()
    st.markdown("**🔧 Tools Invoked by the Agent:**")
    tool_data = {
        "Tool": ["search_flights", "recommend_hotel", "find_places", "get_weather", "estimate_budget"],
        "Purpose": [
            "Find cheapest direct flight on route",
            "Find highest-rated hotel within budget",
            "Discover top-rated tourist attractions",
            "Fetch real-time daily weather forecast",
            "Calculate complete trip cost breakdown",
        ],
        "Data Source": [
            "flights.json (local dataset)",
            "hotels.json (local dataset)",
            "places.json (local dataset)",
            "Open-Meteo API (live)",
            "Computed from all tool outputs",
        ],
    }
    import pandas as pd
    st.dataframe(pd.DataFrame(tool_data), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("**📐 Agent Architecture:**")
    st.code("""
LangChain ReAct Agent
  ├── LLM: GPT-3.5-turbo (fallback: Deterministic)
  ├── Tool 1: search_flights      → flights.json
  ├── Tool 2: recommend_hotel     → hotels.json
  ├── Tool 3: find_places         → places.json
  ├── Tool 4: get_weather         → Open-Meteo API
  └── Tool 5: estimate_budget     → Computed output
""", language="text")


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Built with Python · LangChain · Streamlit · Open-Meteo API | "
    "Developed for Agentic AI Internship Project Submission"
)