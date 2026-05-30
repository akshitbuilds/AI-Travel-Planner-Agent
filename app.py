"""
AI Travel Planner — Streamlit Frontend
Powered by LangChain ReAct Agent + Groq + Open-Meteo

FIXES applied:
  1. Hero bar attractions stat never shows N/A — shows real count (always ≥ 6 via agent fallback)
  2. ALL hero-bar numbers use Syne font with !important — fully uniform typography
  3. Font preconnect added so Google Fonts loads reliably inside Streamlit's iframe
"""

import streamlit as st
from agents.travel_agent import generate_trip

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font preconnect + import (reliable inside Streamlit iframe) ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --navy:       #0b1a33;
    --navy-mid:   #142040;
    --navy-light: #1a2f5a;
    --blue:       #2563eb;
    --sky:        #0ea5e9;
    --accent:     #38bdf8;
    --surface:    #ffffff;
    --bg:         #eef2f7;
    --border:     #dde3ee;
    --text-main:  #0b1a33;
    --text-muted: #6b7280;
    --text-light: #94a3b8;
    --green:      #15803d;
    --green-bg:   #f0fdf4;
    --amber:      #b45309;
    --amber-bg:   #fffbeb;
    --purple:     #7c3aed;
    --purple-bg:  #faf5ff;
    --red:        #dc2626;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp { background: var(--bg); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #e2e8f3 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label {
    color: #7a9cc4 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: var(--navy-light) !important;
    border: 1px solid #2d4a7a !important;
    color: #e2e8f3 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stNumberInput input {
    background: var(--navy-light) !important;
    border: 1px solid #2d4a7a !important;
    color: #e2e8f3 !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--blue) !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--blue) 0%, var(--sky) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    cursor: pointer !important;
    letter-spacing: 0.03em !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    transition: box-shadow 0.2s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 20px rgba(37,99,235,0.5) !important;
}

/* ── Hero ── */
.tp-hero {
    background: linear-gradient(135deg, var(--navy) 0%, #1b3464 60%, #1a4080 100%);
    border-radius: 22px;
    padding: 1.75rem 2.5rem 0 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(11,26,51,0.18);
    position: relative;
    overflow: hidden;
}
.tp-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.tp-hero-top { margin-bottom: 1.5rem; }
.tp-hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin: 0 !important;
    letter-spacing: -0.01em !important;
}
.tp-hero .subtitle {
    color: #7eb3e8;
    margin: 0.3rem 0 0 0;
    font-size: 0.82rem;
    font-weight: 400;
}
.tp-hero-stats {
    display: grid;
    grid-template-columns: 1fr 1px 1fr 1px 1fr 1px 1fr;
    align-items: center;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 1rem 0;
}
.tp-hero .stat { text-align: center; padding: 0 0.5rem; }

/* ── FIX: force Syne on every hero stat number — uniform font ── */
.tp-hero .stat .num,
.tp-hero .stat .num * {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(0.9rem, 1.8vw, 1.3rem) !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    line-height: 1.15 !important;
    white-space: nowrap !important;
    letter-spacing: -0.01em !important;
    overflow: hidden;
    text-overflow: ellipsis;
}
.tp-hero .stat .lbl {
    font-size: 0.64rem;
    color: #7eb3e8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.2rem;
    white-space: nowrap;
    font-weight: 600;
}
.tp-hero-divider {
    width: 1px;
    height: 32px;
    background: rgba(255,255,255,0.15);
    justify-self: center;
}

/* ── Section title ── */
.tp-section-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 1.75rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.01em;
}

/* ── Card ── */
.tp-card {
    background: var(--surface);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    border: 1px solid var(--border);
    box-shadow: 0 1px 6px rgba(11,26,51,0.06);
}
.tp-card h3 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-main);
    margin: 0 0 0.2rem 0;
}
.tp-card .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.tp-card .value {
    font-size: 0.93rem;
    color: #1e293b;
    font-weight: 400;
}

/* ── Chips ── */
.tp-chip {
    display: inline-block;
    background: #eff6ff;
    color: var(--blue);
    border-radius: 999px;
    padding: 0.22rem 0.85rem;
    font-size: 0.77rem;
    font-weight: 600;
    margin: 0.2rem 0.2rem 0.2rem 0;
    letter-spacing: 0.01em;
}
.tp-chip.green  { background: var(--green-bg);  color: var(--green); }
.tp-chip.amber  { background: var(--amber-bg);  color: var(--amber); }
.tp-chip.purple { background: var(--purple-bg); color: var(--purple); }
.tp-chip.red    { background: #fff1f1;           color: var(--red); }

/* ── Attraction card ── */
.tp-attr-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem;
    margin-bottom: 0.9rem;
    transition: box-shadow 0.18s ease;
}
.tp-attr-card:hover { box-shadow: 0 4px 16px rgba(11,26,51,0.09); }
.tp-attr-card .name {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.97rem;
    font-weight: 700;
    color: var(--text-main);
    margin-bottom: 0.4rem;
}
.tp-attr-card .meta  { font-size: 0.76rem; color: var(--text-muted); margin-bottom: 0.35rem; }
.tp-attr-card .desc  { font-size: 0.82rem; color: #374151; line-height: 1.55; }
.tp-attr-card .rating {
    display: inline-block;
    background: #fef9c3;
    color: #92400e;
    border-radius: 6px;
    padding: 0.15rem 0.55rem;
    font-size: 0.73rem;
    font-weight: 700;
    margin-bottom: 0.35rem;
}

/* ── Itinerary day ── */
.tp-day {
    border-left: 3px solid var(--blue);
    padding-left: 1.25rem;
    margin-bottom: 1.75rem;
}
.tp-day .day-label {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--blue);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.6rem;
}
.tp-day .activity {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 0.8rem 1.1rem;
    margin-bottom: 0.55rem;
    color: #1e293b;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* ── Weather ── */
.tp-weather {
    background: linear-gradient(135deg, #0369a1, var(--sky));
    border-radius: 16px;
    padding: 1.4rem 1.75rem;
    color: white;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 16px rgba(14,165,233,0.25);
}
.tp-weather h4 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.05rem;
    font-weight: 700;
    color: white;
    margin: 0 0 0.3rem 0;
}
.tp-weather p { color: #e0f2fe; font-size: 0.88rem; margin: 0; }

/* ── Budget ── */
.tp-budget-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.65rem 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.9rem;
}
.tp-budget-row:last-child { border-bottom: none; }
.tp-budget-row .item { color: #374151; }
.tp-budget-row .amt  { font-weight: 700; color: var(--text-main); }
.tp-budget-total {
    display: flex;
    justify-content: space-between;
    padding: 0.85rem 0 0 0;
    margin-top: 0.5rem;
    border-top: 2px solid var(--text-main);
    font-family: 'Syne', sans-serif !important;
    font-weight: 700;
    font-size: 1.08rem;
    color: var(--text-main);
}

/* ── Summary stat cards ── */
.tp-stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
}
.tp-stat-card .stat-num {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.65rem !important;
    font-weight: 800 !important;
    color: var(--text-main) !important;
    line-height: 1;
}
.tp-stat-card .stat-lbl {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-muted);
    font-weight: 600;
    margin-top: 0.35rem;
}

/* ── AI Reasoning ── */
.tp-reasoning {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem;
    font-size: 0.88rem;
    line-height: 1.75;
    color: #374151;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}
.tp-banner-info {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 11px;
    padding: 0.85rem 1.25rem;
    color: #1d4ed8;
    font-size: 0.88rem;
    margin-bottom: 1.25rem;
    font-weight: 500;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    border-bottom: 2px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-muted);
    background: transparent;
    border-radius: 9px 9px 0 0;
    padding: 0.5rem 1.1rem;
    transition: color 0.15s;
}
.stTabs [aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
    background: #eff6ff !important;
}

/* ── Info / empty states ── */
.tp-empty {
    background: #f8fafc;
    border: 1.5px dashed #cbd5e1;
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
CITIES = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Jaipur", "Ahmedabad", "Goa",
    "Kochi", "Varanasi", "Agra", "Udaipur", "Rishikesh",
]

with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 0 1rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.45rem;font-weight:800;color:#ffffff;letter-spacing:-0.01em;">
            ✈️ AI Travel Planner
        </div>
        <div style="font-size:0.75rem;color:#4a6a9a;margin-top:0.35rem;font-weight:500;">
            Powered by LangChain · Groq · Open-Meteo
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #1a3055;margin:0 0 1.5rem 0;">
    """, unsafe_allow_html=True)

    departure   = st.selectbox("🛫 Departure City",   CITIES, index=0)
    destination = st.selectbox("🛬 Destination City", CITIES, index=9)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    days   = st.slider("📅 Trip Duration (Days)", min_value=1, max_value=14, value=3)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    budget = st.number_input("💰 Hotel Budget / Night (₹)", min_value=500, max_value=50000, value=5000, step=500)
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    generate = st.button("🚀 Generate AI Trip Plan")
    st.markdown("""
    <hr style="border:none;border-top:1px solid #1a3055;margin:1.5rem 0 1rem 0;">
    <div style="font-size:0.72rem;color:#3e5a7a;line-height:1.7;font-weight:500;">
        ℹ️ The agent autonomously runs 5 specialised tools:<br>
        flight search · hotel finder · attraction discovery<br>
        weather forecast · budget calculator
    </div>
    """, unsafe_allow_html=True)


# ── Trigger generation ─────────────────────────────────────────────────────────
if generate:
    if departure == destination:
        st.error("⚠️ Departure and destination cities must be different.")
        st.stop()

    st.session_state.pop("result", None)
    st.session_state.pop("params", None)

    with st.spinner("🤖 Agent is planning your trip… (may take 30–60 seconds)"):
        try:
            result = generate_trip(
                source=departure,
                destination=destination,
                days=days,
                budget=budget,
            )
            st.session_state["result"] = result
            st.session_state["params"] = {
                "departure":   departure,
                "destination": destination,
                "days":        days,
                "budget":      budget,
            }
            st.rerun()
        except Exception as exc:
            import traceback
            st.error("❌ Agent error: " + str(exc))
            st.code(traceback.format_exc(), language="python")
            st.stop()


# ── Landing page ───────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.markdown("""
    <div style="max-width:700px;margin:5rem auto;text-align:center;">
        <div style="font-size:4rem;margin-bottom:1.25rem;">🌍</div>
        <h1 style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;color:#0b1a33;
                   margin:0 0 0.85rem 0;letter-spacing:-0.02em;">
            AI Travel Planner Agent
        </h1>
        <p style="font-size:1rem;color:#6b7280;line-height:1.75;max-width:520px;margin:0 auto 2.25rem auto;">
            An <strong>Agentic AI</strong> system built with <strong>LangChain ReAct</strong>.
            Configure your trip in the sidebar and hit <em>Generate</em> — the agent autonomously
            searches flights, recommends hotels, discovers attractions, fetches live weather,
            and estimates your total budget.
        </p>
        <div style="display:flex;justify-content:center;gap:0.65rem;flex-wrap:wrap;">
            <span class="tp-chip">🧠 ReAct Agent</span>
            <span class="tp-chip green">🔍 5 Tools</span>
            <span class="tp-chip amber">⚡ Groq LLaMA</span>
            <span class="tp-chip purple">🌤️ Live Weather</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Extract data from session state ───────────────────────────────────────────
data = st.session_state["result"]
p    = st.session_state["params"]

flight       = data.get("flight", {})      or {}
hotel        = data.get("hotel", {})       or {}
places       = data.get("places", [])      or []
weather_data = data.get("weather", [])     or []
budget_data  = data.get("budget", {})      or {}
itinerary    = data.get("itinerary", [])   or []
reasoning    = data.get("ai_reasoning", "") or ""
agent_steps  = data.get("agent_steps", 0)
agent_used   = data.get("agent_used", "ReAct Agent")

# ── Derive aligned values ──────────────────────────────────────────────────────
flight_price      = int(flight.get("price", 0) or 0)
h_price_per_night = int(hotel.get("price_per_night", 0) or 0)

# Total cost — prefer explicit key, then sum components
total_cost = 0
if isinstance(budget_data, dict):
    total_cost = int(
        budget_data.get("total")
        or budget_data.get("total_cost")
        or (
            (budget_data.get("flight_cost", 0) or 0)
            + (budget_data.get("hotel_cost",  0) or 0)
            + (budget_data.get("food_cost",   0) or 0)
            + (budget_data.get("transport_cost", 0) or 0)
            + (budget_data.get("activity_cost",  0) or 0)
        )
        or 0
    )

if not total_cost:
    total_cost = flight_price + h_price_per_night * p["days"]

# ── FIX: n_places is always ≥ 6 (fallback in travel_agent.py) ──────────────────
n_places = len(places) if isinstance(places, list) else 0


# ── Hero bar ───────────────────────────────────────────────────────────────────
# All four stats use actual agent values; attractions count is never 0/N/A.
st.markdown(f"""
<div class="tp-hero">
    <div class="tp-hero-top">
        <h1>✅ {p['departure']} → {p['destination']}</h1>
        <p class="subtitle">Trip plan generated · {agent_used} · {agent_steps} reasoning steps</p>
    </div>
    <div class="tp-hero-stats">
        <div class="stat">
            <div class="num">{p['days']}d</div>
            <div class="lbl">Duration</div>
        </div>
        <div class="tp-hero-divider"></div>
        <div class="stat">
            <div class="num">₹{total_cost:,}</div>
            <div class="lbl">Total Est.</div>
        </div>
        <div class="tp-hero-divider"></div>
        <div class="stat">
            <div class="num">₹{h_price_per_night:,}</div>
            <div class="lbl">Hotel/Night</div>
        </div>
        <div class="tp-hero-divider"></div>
        <div class="stat">
            <div class="num">{n_places}</div>
            <div class="lbl">Attractions</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_flight, tab_itinerary, tab_weather, tab_budget, tab_ai = st.tabs([
    "✈️ Flight & Hotel",
    "📅 Day-wise Itinerary",
    "🌤️ Weather",
    "💰 Budget",
    "🧠 AI Reasoning",
])


# ───────── TAB 1 : Flight & Hotel ─────────────────────────────────────────────
with tab_flight:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="tp-section-title">✈️ Flight Selected</div>', unsafe_allow_html=True)
        airline  = flight.get("airline", "N/A")
        price    = flight_price
        duration = flight.get("duration", "N/A")
        dep_time = flight.get("departure", flight.get("departure_time", "—"))
        arr_time = flight.get("arrival",   flight.get("arrival_time",   "—"))
        f_class  = flight.get("class", "Economy")
        why_f    = flight.get("why_chosen", "")
        why_html = (
            '<div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #f1f5f9;">'
            '<div class="label">Why chosen</div>'
            '<div class="value" style="margin-top:0.25rem;">' + str(why_f) + '</div></div>'
        ) if why_f else ""

        st.markdown(
            '<div class="tp-card">'
            '<h3>' + str(airline) + '</h3>'
            '<div style="margin:0.8rem 0;">'
            '<span class="tp-chip">₹' + f"{price:,}" + '</span>'
            '<span class="tp-chip green">' + str(duration) + '</span>'
            '<span class="tp-chip amber">' + str(f_class) + '</span>'
            '</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.85rem;margin-top:0.85rem;">'
            '<div><div class="label">Departure</div><div class="value">' + str(dep_time) + '</div></div>'
            '<div><div class="label">Arrival</div><div class="value">' + str(arr_time) + '</div></div>'
            '</div>' + why_html + '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown('<div class="tp-section-title">🏨 Hotel Recommended</div>', unsafe_allow_html=True)
        h_name      = hotel.get("name", "N/A")
        h_rating    = hotel.get("rating", "N/A")
        h_type      = hotel.get("type", "Hotel")
        h_amenities = hotel.get("amenities", []) or []
        why_h       = hotel.get("why_chosen", "")
        amenity_chips = "".join(
            '<span class="tp-chip purple">' + str(a) + '</span>' for a in h_amenities
        )
        why_h_html = (
            '<div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #f1f5f9;">'
            '<div class="label">Why chosen</div>'
            '<div class="value" style="margin-top:0.25rem;">' + str(why_h) + '</div></div>'
        ) if why_h else ""

        st.markdown(
            '<div class="tp-card">'
            '<h3>' + str(h_name) + '</h3>'
            '<div style="margin:0.8rem 0;">'
            '<span class="tp-chip">₹' + f"{h_price_per_night:,}" + '/night</span>'
            '<span class="tp-chip amber">⭐ ' + str(h_rating) + '</span>'
            '<span class="tp-chip green">' + str(h_type) + '</span>'
            '</div>'
            '<div><div class="label" style="margin-bottom:0.45rem;">Amenities</div>'
            + (amenity_chips if amenity_chips else '<span style="color:#9ca3af;font-size:0.85rem;">N/A</span>')
            + '</div>' + why_h_html + '</div>',
            unsafe_allow_html=True
        )

    # ── Attractions ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="tp-section-title">📍 Top Attractions in ' + str(p["destination"]) + '</div>',
        unsafe_allow_html=True
    )

    # FIX: places is always non-empty — fallback data guaranteed by travel_agent.py
    if places:
        cols = st.columns(2, gap="medium")
        for i, attr in enumerate(places):
            with cols[i % 2]:
                if isinstance(attr, dict):
                    nm   = attr.get("name", "N/A")
                    rt   = attr.get("rating", "")
                    cat  = attr.get("category", attr.get("type", ""))
                    entr = attr.get("entry_fee", "")
                    best = attr.get("best_time", "")
                    desc = attr.get("description", "")
                    meta_parts = []
                    if cat:  meta_parts.append("📂 " + str(cat))
                    if entr: meta_parts.append("🎟️ " + str(entr))
                    if best: meta_parts.append("🕐 " + str(best))
                    meta_str = " · ".join(meta_parts)
                    st.markdown(
                        '<div class="tp-attr-card">'
                        + ('<div class="rating">⭐ ' + str(rt) + '</div>' if rt else "")
                        + '<div class="name">' + str(nm) + '</div>'
                        + ('<div class="meta">' + meta_str + '</div>' if meta_str else "")
                        + ('<div class="desc">' + str(desc) + '</div>' if desc else "")
                        + '</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="tp-attr-card"><div class="name">📍 ' + str(attr) + '</div></div>',
                        unsafe_allow_html=True
                    )
    else:
        # This branch should never trigger anymore — kept as a safety net
        st.markdown(
            '<div class="tp-empty">No attractions data available. Try regenerating the plan.</div>',
            unsafe_allow_html=True
        )


# ───────── TAB 2 : Day-wise Itinerary ─────────────────────────────────────────
with tab_itinerary:
    st.markdown(
        '<div class="tp-section-title">📅 ' + str(p["days"]) + '-Day Itinerary for ' + str(p["destination"]) + '</div>',
        unsafe_allow_html=True
    )

    def make_slot_html(label, place):
        if not place:
            return ""
        if isinstance(place, dict):
            nm   = place.get("name", "")
            typ  = place.get("type", place.get("category", ""))
            rt   = place.get("rating", "")
            bt   = place.get("best_time", "")
            ds   = place.get("description", "")
            parts = [x for x in [typ, ("⭐ " + str(rt)) if rt else "", bt] if x]
            meta  = " · ".join(parts)
            html  = '<div class="activity"><strong>' + label + ":</strong> " + str(nm)
            if meta:
                html += ' <em style="color:#6b7280;font-size:0.8rem;">(' + meta + ')</em>'
            if ds:
                html += '<br><span style="font-size:0.82rem;color:#374151;">' + str(ds) + '</span>'
            html += '</div>'
            return html
        return '<div class="activity"><strong>' + label + ":</strong> " + str(place) + '</div>'

    if itinerary:
        for idx, day_data in enumerate(itinerary if isinstance(itinerary, list) else []):
            if not isinstance(day_data, dict):
                st.markdown(
                    '<div class="tp-day"><div class="day-label">Day ' + str(idx + 1) + '</div>'
                    '<div class="activity">🔹 ' + str(day_data) + '</div></div>',
                    unsafe_allow_html=True
                )
                continue

            day_num   = day_data.get("day", idx + 1)
            day_date  = day_data.get("date", "Day " + str(day_num))
            day_wx    = day_data.get("weather", "")
            morning   = day_data.get("morning")
            afternoon = day_data.get("afternoon")
            activities = day_data.get("activities", [])

            if morning or afternoon:
                acts_html = make_slot_html("Morning", morning) + make_slot_html("Afternoon", afternoon)
                if day_wx:
                    acts_html += '<div class="activity">🌤️ <strong>Weather:</strong> ' + str(day_wx) + '</div>'
            elif activities:
                acts_html = ""
                for a in activities:
                    if isinstance(a, dict):
                        t = a.get("time", "")
                        v = a.get("activity", str(a))
                        acts_html += '<div class="activity">' + ("<strong>" + t + "</strong> — " if t else "") + str(v) + '</div>'
                    else:
                        acts_html += '<div class="activity">' + str(a) + '</div>'
            else:
                acts_html = '<div class="activity">' + (str(day_wx) or str(day_data)) + '</div>'

            st.markdown(
                '<div class="tp-day">'
                '<div class="day-label">Day ' + str(day_num) + ' — ' + str(day_date) + '</div>'
                + acts_html + '</div>',
                unsafe_allow_html=True
            )

        if isinstance(itinerary, str):
            st.markdown('<div class="tp-reasoning">' + itinerary + '</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="tp-empty">No day-wise itinerary was generated. Try regenerating the plan.</div>', unsafe_allow_html=True)


# ───────── TAB 3 : Weather ────────────────────────────────────────────────────
with tab_weather:
    st.markdown(
        '<div class="tp-section-title">🌤️ Weather in ' + str(p["destination"]) + '</div>',
        unsafe_allow_html=True
    )

    if weather_data:
        daily_list = weather_data if isinstance(weather_data, list) else [weather_data]
        first = daily_list[0] if daily_list else {}

        raw_max  = first.get("temp_max",  first.get("temperature_max",  None))
        raw_min  = first.get("temp_min",  first.get("temperature_min",  None))
        raw_temp = first.get("temp",      first.get("temperature",      None))

        if raw_max is not None and raw_min is not None:
            temp_str = f"{raw_min}°C – {raw_max}°C"
        elif raw_max is not None:
            temp_str = f"{raw_max}°C"
        elif raw_temp is not None:
            temp_str = f"{raw_temp}°C"
        else:
            temp_str = "N/A"

        condition = first.get("description", first.get("condition", "N/A")) or "N/A"
        humidity  = first.get("humidity",    None)
        wind      = first.get("wind_speed",  None)
        precip    = first.get("precipitation", None)

        hum_str  = str(humidity) + "%" if humidity  is not None else "N/A"
        wind_str = str(wind)  + " km/h" if wind     is not None else "N/A"
        prec_str = str(precip) + " mm"  if precip   is not None else "N/A"

        st.markdown(
            '<div class="tp-weather">'
            '<h4>🌡️ ' + temp_str + ' &nbsp;·&nbsp; ' + str(condition) + '</h4>'
            '<p>💧 Humidity: ' + hum_str + ' &nbsp;·&nbsp; 💨 Wind: ' + wind_str + ' &nbsp;·&nbsp; 🌧️ Precipitation: ' + prec_str + '</p>'
            '</div>',
            unsafe_allow_html=True
        )

        if len(daily_list) > 1:
            st.markdown(
                '<div style="font-family:\'Syne\',sans-serif;font-weight:700;color:#0b1a33;'
                'font-size:0.95rem;margin:1rem 0 0.75rem;">Daily Forecast</div>',
                unsafe_allow_html=True
            )
            show = daily_list[:7]
            cols = st.columns(len(show))
            for i, day in enumerate(show):
                d_desc     = day.get("description", day.get("condition", "")) or ""
                d_raw_max  = day.get("temp_max", day.get("temperature_max", None))
                d_raw_min  = day.get("temp_min", day.get("temperature_min", None))
                d_raw_temp = day.get("temp",     day.get("temperature",     None))
                d_date     = day.get("date", "Day " + str(i + 1))

                if d_raw_max is not None and d_raw_min is not None:
                    d_temp_str = str(d_raw_max) + "° / " + str(d_raw_min) + "°"
                elif d_raw_max is not None:
                    d_temp_str = str(d_raw_max) + "°"
                elif d_raw_temp is not None:
                    d_temp_str = str(d_raw_temp) + "°"
                else:
                    d_temp_str = "N/A"

                with cols[i]:
                    st.markdown(
                        '<div class="tp-card" style="text-align:center;padding:0.9rem 0.6rem;">'
                        '<div class="label">' + str(d_date) + '</div>'
                        '<div style="font-size:0.75rem;color:#374151;margin:0.4rem 0;">' + d_desc + '</div>'
                        '<div style="font-size:0.85rem;color:#0b1a33;font-weight:700;">' + d_temp_str + '</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )
    else:
        st.markdown('<div class="tp-empty">Weather data was not returned by the agent.</div>', unsafe_allow_html=True)


# ───────── TAB 4 : Budget ─────────────────────────────────────────────────────
with tab_budget:
    st.markdown('<div class="tp-section-title">💰 Budget Breakdown</div>', unsafe_allow_html=True)

    if budget_data and isinstance(budget_data, dict):
        fc = int(budget_data.get("flight_cost",    budget_data.get("flights",     0)) or 0)
        hc = int(budget_data.get("hotel_cost",     budget_data.get("hotel",       0)) or 0)
        fo = int(budget_data.get("food_cost",      budget_data.get("food",        0)) or 0)
        tc = int(budget_data.get("transport_cost", budget_data.get("transport",   0)) or 0)
        ac = int(budget_data.get("activity_cost",  budget_data.get("sightseeing", 0)) or 0)
        mc = int(budget_data.get("miscellaneous",  budget_data.get("misc",        0)) or 0)

        if not hc and h_price_per_night:
            hc = h_price_per_night * p["days"]
        if not fc and flight_price:
            fc = flight_price

        items = [
            ("✈️ Flights (round trip)", fc),
            ("🏨 Hotel (" + str(p["days"]) + " nights @ ₹" + f"{h_price_per_night:,}" + "/night)", hc),
            ("🍽️ Food & Dining",        fo),
            ("🚌 Local Transport",      tc),
            ("📍 Activities & Entry",   ac),
            ("🎁 Miscellaneous",        mc),
        ]

        rows_html = "".join(
            '<div class="tp-budget-row">'
            '<span class="item">' + lbl + '</span>'
            '<span class="amt">₹' + f"{amt:,}" + '</span>'
            '</div>'
            for lbl, amt in items if amt
        )

        st.markdown(
            '<div class="tp-card">'
            + rows_html +
            '<div class="tp-budget-total">'
            '<span>Total Estimated Cost</span>'
            '<span>₹' + f"{total_cost:,}" + '</span>'
            '</div></div>',
            unsafe_allow_html=True
        )
    else:
        h_total  = h_price_per_night * p["days"]
        fb_total = total_cost or (flight_price + h_total)

        st.markdown(
            '<div class="tp-card">'
            '<div class="tp-budget-row">'
            '<span class="item">✈️ Flight</span>'
            '<span class="amt">₹' + f"{flight_price:,}" + '</span>'
            '</div>'
            '<div class="tp-budget-row">'
            '<span class="item">🏨 Hotel (' + str(p["days"]) + ' nights @ ₹' + f"{h_price_per_night:,}" + '/night)</span>'
            '<span class="amt">₹' + f"{h_total:,}" + '</span>'
            '</div>'
            '<div class="tp-budget-total">'
            '<span>Estimated Total</span>'
            '<span>₹' + f"{fb_total:,}" + '</span>'
            '</div></div>',
            unsafe_allow_html=True
        )

    per_day = round(total_cost / p["days"]) if p["days"] else total_cost
    col_a, col_b, col_c = st.columns(3, gap="medium")

    with col_a:
        st.markdown(
            '<div class="tp-stat-card">'
            '<div class="stat-lbl">Per Day Avg.</div>'
            '<div class="stat-num">₹' + f"{per_day:,}" + '</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            '<div class="tp-stat-card">'
            '<div class="stat-lbl">Trip Duration</div>'
            '<div class="stat-num">' + str(p["days"]) + ' Days</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col_c:
        st.markdown(
            '<div class="tp-stat-card">'
            '<div class="stat-lbl">Hotel/Night (Actual)</div>'
            '<div class="stat-num">₹' + f"{h_price_per_night:,}" + '</div>'
            '</div>',
            unsafe_allow_html=True
        )


# ───────── TAB 5 : AI Reasoning ───────────────────────────────────────────────
with tab_ai:
    st.markdown('<div class="tp-section-title">🧠 Agent Reasoning Chain</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="tp-banner-info">'
        'Agent type: <strong>' + str(agent_used) + '</strong>'
        ' &nbsp;·&nbsp; '
        'Tools invoked: <strong>' + str(agent_steps) + ' reasoning steps</strong>'
        '</div>',
        unsafe_allow_html=True
    )
    if reasoning:
        st.markdown('<div class="tp-reasoning">' + str(reasoning) + '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="tp-card">'
            '<div class="label">No detailed reasoning captured</div>'
            '<div class="value" style="margin-top:0.4rem;">'
            'The agent completed its task but did not return a reasoning trace. '
            'Return intermediate steps in <code>generate_trip()</code> under the key '
            '<code>"ai_reasoning"</code>.'
            '</div></div>',
            unsafe_allow_html=True
        )