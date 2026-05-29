import streamlit as st

from agents.travel_agent import generate_trip

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

.stMetric {
    background-color: #1E1E1E;
    padding: 15px;
    border-radius: 10px;
}

div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
}

div.stButton > button:hover {
    background-color: #ff2b2b;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("✈️ AI Travel Planner")

st.sidebar.markdown("---")

source = st.sidebar.text_input(
    "Source City",
    "Delhi"
)

destination = st.sidebar.text_input(
    "Destination City",
    "Goa"
)

days = st.sidebar.slider(
    "Trip Duration (Days)",
    1,
    10,
    3
)

budget = st.sidebar.number_input(
    "Hotel Budget/Night",
    min_value=1000,
    max_value=20000,
    value=5000
)

generate_button = st.sidebar.button(
    "🚀 Generate AI Trip"
)

st.sidebar.markdown("---")

st.sidebar.info(
    "AI-powered smart travel planning assistant."
)

# ---------------- MAIN TITLE ----------------

st.title("🌍 AI Travel Planner Agent")

st.markdown(
    """
Plan smarter trips using AI-powered recommendations,
weather intelligence, and budget optimization.
"""
)

st.markdown("---")
st.markdown(
    """
## 🌟 Smart AI-Based Travel Planning

Get intelligent recommendations for:

✅ Flights  
✅ Hotels  
✅ Tourist Places  
✅ Weather  
✅ Budget Planning  
"""
)

# ---------------- TOP METRICS ----------------

col1, col2, col3 = st.columns(3)

col1.metric(
    "Destination",
    destination
)

col2.metric(
    "Days",
    days
)

col3.metric(
    "Budget",
    f"₹{budget}"
)

st.markdown("---")

# ---------------- GENERATE BUTTON ----------------

if generate_button:

    with st.spinner("✈️ AI is planning your smart journey..."):

        result = generate_trip(
            source,
            destination,
            days,
            budget
        )

    st.success("✅ AI Trip Generated Successfully!")

    st.markdown("## ✈️ Trip Overview")

    # ---------------- FLIGHT CARD ----------------

    flight = result["flight"]

    st.markdown("## ✈ Flight Details")

    col4, col5 = st.columns(2)

    with col4:

        st.info(
            f"""
Airline: {flight['airline']}

Price: ₹{flight['price']}

Duration: {flight['duration']}
"""
        )

    # ---------------- HOTEL CARD ----------------

    hotel = result["hotel"]

    with col5:

        st.success(
            f"""
Hotel: {hotel['name']}

Price/Night: ₹{hotel['price_per_night']}

Rating: ⭐ {hotel['rating']}
"""
        )

    st.markdown("---")

    # ---------------- WEATHER ----------------

    st.markdown("## 🌤 Live Weather")

    st.warning(
        f"""
Current Temperature in {destination}:
{result['temperature']} °C
"""
    )

    st.markdown("---")

    # ---------------- PLACES ----------------

    st.markdown("## 📍 Recommended Places")

    for place in result["places"]:

        st.markdown(
            f"✅ {place['name']}"
        )

    st.markdown("---")

    # ---------------- BUDGET ----------------

    budget_data = result["budget"]

    st.markdown("## 💰 Budget Breakdown")

    col6, col7, col8, col9 = st.columns(4)

    col6.metric(
        "Flight",
        f"₹{budget_data['flight_cost']}"
    )

    col7.metric(
        "Hotel",
        f"₹{budget_data['hotel_cost']}"
    )

    col8.metric(
        "Food",
        f"₹{budget_data['food_cost']}"
    )

    col9.metric(
        "Transport",
        f"₹{budget_data['transport_cost']}"
    )

    st.markdown("---")

    st.success(
        f"""
### TOTAL ESTIMATED COST: ₹{budget_data['total']}
"""
    )

    # ---------------- AI REASONING ----------------

    st.markdown("---")

    st.markdown("## 🧠 AI Reasoning")

    st.info(
        """
Recommendations are generated based on:

✅ Budget optimization

✅ Hotel ratings

✅ Popular tourist attractions

✅ Smart travel planning

✅ Weather analysis
"""
    )

    # ---------------- SMART ITINERARY ----------------

    st.markdown("---")

    st.markdown("## 📅 Smart Itinerary")

    day = 1

    for place in result["places"]:

        st.markdown(
            f"""
### Day {day}

Visit: {place['name']}
"""
        )

        day += 1
st.markdown("---")

st.caption(
    "Developed using Python, Streamlit, Open-Meteo API, and AI-based travel planning logic."
)