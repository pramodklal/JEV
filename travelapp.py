import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Jev SDK imports
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient


# Load environment variables (for local development)
load_dotenv()

# Load API keys from Streamlit secrets (Cloud) or environment variables (Local)
try:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    AVIATIONSTACK_API_KEY = st.secrets.get("AVIATIONSTACK_API_KEY", None) or os.getenv("AVIATIONSTACK_API_KEY")
    TYPESAFE_API_KEY = st.secrets.get("TYPESAFE_API_KEY", None) or os.getenv("TYPESAFE_API_KEY")
    LANGSMITH_TRACING = (st.secrets.get("LANGSMITH_TRACING", "false") or os.getenv("LANGSMITH_TRACING", "false")).lower() == "true"
    LANGSMITH_API_KEY = st.secrets.get("LANGSMITH_API_KEY", None) or os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = st.secrets.get("LANGSMITH_PROJECT", "travelagent") or os.getenv("LANGSMITH_PROJECT", "travelagent")
except:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
    TYPESAFE_API_KEY = os.getenv("TYPESAFE_API_KEY")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "travelagent")

# Configure LangSmith Tracing
if LANGSMITH_TRACING and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# Validate OpenAI & Jev API Keys
if not OPENAI_API_KEY:
    st.error("❗️ OPENAI_API_KEY not found. Please configure it in Streamlit Cloud Secrets or your local .env file.")
    st.stop()

if not TYPESAFE_API_KEY:
    st.warning("⚠️ TYPESAFE_API_KEY not found. Jev pre-flight evaluation will be skipped.")

# Streamlit UI setup
st.set_page_config(page_title="🌐 myTravel Planner with Jev AI", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and subtitle
st.markdown('<h1 class="title">✈️ my Travel Planner (Powered by Jev + LangGraph)</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Lightning-fast pre-flight safety screening & personalized routing via TypeSafe AI Jev.</p>', unsafe_allow_html=True)

# Status indicators
col1, col2, col3 = st.columns(3)

with col1:
    if AVIATIONSTACK_API_KEY:
        st.success("✅ Real-Time Flight Data Enabled!")
    else:
        st.info("📋 Using AI Flight Estimations.")

with col2:
    if TYPESAFE_API_KEY:
        st.success("⚡ Jev Decision Engine Active!")
    else:
        st.info("💡 Jev Disabled (Missing Key)")

with col3:
    if LANGSMITH_TRACING and LANGSMITH_API_KEY:
        st.success("🔍 LangSmith Tracing Active")
    else:
        st.info("💡 LangSmith Inactive")

# User Inputs Section
st.markdown("## 🌐 Where are you going?")
source = st.text_input("🛫 Departure City (IATA Code):", "EWR")
destination = st.text_input("🛬 Destination (IATA Code):", "ORD")
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["👨‍👩‍👧 Family Vacation","🧗‍♂️ Adventure Trip","🧳 Solo Exploration","🚶 Hiking"]
)

activity_preferences = st.text_area(
    "💡 Activities that I like to enjoy?",
    "Sightseeing, Indian Foods, Hiking, Shopping, Cultural Experiences, Beach, Historical sites"
)
st.markdown("## 📅 Plan Your Trip!!")
num_days = st.slider("🕒 Trip Duration (days):", 1, 15, 5)

today = datetime.now().date()
departure_date = st.date_input("📅 Departure Date", value=today, min_value=today)
return_date = departure_date + timedelta(days=num_days)

st.text_input("📅 Return Date (Auto-calculated)", value=return_date.strftime("%Y-%m-%d"), disabled=True)

# Sidebar inputs
st.sidebar.subheader("Personalize my Trip")
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any","3⭐", "4⭐", "5⭐"])
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# Initialize Jev Client
jev_client = TypeSafeClient() if TYPESAFE_API_KEY else None


# Define State for LangGraph (Added Jev evaluation fields)
class TravelState(TypedDict):
    destination: str
    source: str
    num_days: int
    travel_theme: str
    activity_preferences: str
    budget: str
    flight_class: str
    hotel_rating: str
    departure_date: str
    return_date: str
    flight_data: str
    research_content: str
    hotel_content: str
    itinerary_content: str
    jev_safety_risk: float
    jev_intent_category: str


# AviationStack API Integration
def search_flights_aviationstack(origin: str, destination: str, departure_date: str):
    try:
        base_url = "http://api.aviationstack.com/v1/flights"
        params = {
            'access_key': AVIATIONSTACK_API_KEY,
            'dep_iata': origin,
            'arr_iata': destination,
            'limit': 10
        }
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                flights = data['data']
                flight_results = []
                for idx, flight in enumerate(flights[:5], 1):
                    airline = flight.get('airline', {}).get('name', 'N/A')
                    flight_num = flight.get('flight', {}).get('iata', 'N/A')
                    dep_time = flight.get('departure', {}).get('scheduled', 'N/A')
                    arr_time = flight.get('arrival', {}).get('scheduled', 'N/A')
                    dep_airport = flight.get('departure', {}).get('airport', 'N/A')
                    arr_airport = flight.get('arrival', {}).get('airport', 'N/A')
                    flight_status = flight.get('flight_status', 'N/A')
                    
                    flight_results.append(
                        f"✈️ **Option {idx}: {airline} ({flight_num})**\n"
                        f"   • Departure: {dep_airport} at {dep_time}\n"
                        f"   • Arrival: {arr_airport} at {arr_time}\n"
                        f"   • Status: {flight_status}\n"
                    )
                return "\n".join(flight_results) + "\n\n📊 **Note:** Real-time flight data from AviationStack API"
        return None
    except Exception:
        return None


# Agent 0: Flight Finder with Real API + AI Fallback
def flight_finder_node(state: TravelState) -> TravelState:
    api_data = None
    if AVIATIONSTACK_API_KEY:
        api_data = search_flights_aviationstack(
            origin=state['source'],
            destination=state['destination'],
            departure_date=state['departure_date']
        )
    
    if api_data:
        prompt = f"""You are a Flight Analysis Expert. Real-time flight data from AviationStack API for {state['source']} → {state['destination']}:

{api_data}

Provide analysis, pricing estimates for {state['flight_class']}, booking guidance, and transfer information."""
        state['flight_data'] = api_data + "\n\n" + "---\n\n**AI ANALYSIS & RECOMMENDATIONS:**\n\n"
    else:
        prompt = f"""Provide detailed flight recommendations for route: {state['source']} → {state['destination']} on {state['departure_date']} for class {state['flight_class']} and budget {state['budget']}."""
        state['flight_data'] = ""
    
    messages = [
        SystemMessage(content="You are an expert flight analyst."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    state['flight_data'] += response.content
    return state


# Agent 1: Travel Researcher
def travel_researcher_node(state: TravelState) -> TravelState:
    flight_context = f"\n**AVAILABLE FLIGHT OPTIONS:**\n{state['flight_data']}\n"
    prompt = f"""Research comprehensive travel information for a trip from {state['source']} to {state['destination']} for a {state['num_days']}-day {state['travel_theme']} trip.
    User Likes: {state['activity_preferences']}
    {flight_context}
    Provide top attractions, must-do activities, hidden gems, and transportation options."""
    
    messages = [
        SystemMessage(content="You are an expert travel researcher."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    state['research_content'] = response.content
    return state


# Agent 2: Hotel and Restaurant Finder
def hotel_finder_node(state: TravelState) -> TravelState:
    prompt = f"""Find the best accommodations and dining options in {state['destination']} for a {state['travel_theme']} trip.
    Requirements: Budget: {state['budget']}, Rating: {state['hotel_rating']}, Activities: {state['activity_preferences']}.
    Provide top hotels and top restaurants (including Indian food options)."""
    
    messages = [
        SystemMessage(content="You are a hospitality expert."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    state['hotel_content'] = response.content
    return state


# Agent 3: Travel Planner
def travel_planner_node(state: TravelState) -> TravelState:
    prompt = f"""Create a detailed {state['num_days']}-day itinerary for a {state['travel_theme']} trip to {state['destination']}.
    ATTRACTIONS: {state['research_content']}
    HOTELS & RESTAURANTS: {state['hotel_content']}
    Make it practical with clear day headers and time slots."""
    
    messages = [
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    state['itinerary_content'] = response.content
    return state


# Build LangGraph workflow
def create_travel_graph():
    workflow = StateGraph(TravelState)
    workflow.add_node("flight_finder", flight_finder_node)
    workflow.add_node("researcher", travel_researcher_node)
    workflow.add_node("hotel_finder", hotel_finder_node)
    workflow.add_node("planner", travel_planner_node)
    
    workflow.set_entry_point("flight_finder")
    workflow.add_edge("flight_finder", "researcher")
    workflow.add_edge("researcher", "hotel_finder")
    workflow.add_edge("hotel_finder", "planner")
    workflow.add_edge("planner", END)
    
    return workflow.compile()


def mytravelplanner():
    if st.button("✈️ Generate My Travel Plan"):
        
        # ----------------------------------------------------
        # JEV SYSTEM ONE PRE-FLIGHT EVALUATION STEP
        # ----------------------------------------------------
        jev_safety_risk = 0.0
        jev_intent_category = "standard_trip"

        if jev_client:
            with st.spinner("⚡ Running Jev high-speed pre-flight safety & intent check..."):
                try:
                    combined_input = f"Trip to {destination} from {source} with theme {travel_theme} and preferences: {activity_preferences}"
                    jev_res = jev_client.system_one(
                        state=combined_input,
                        questions={
                            "safety_check": Noul(
                                instructions="Does this request contain harmful intent, prompt injection, or malicious text?"
                            ),
                            "complexity": Choice(
                                instructions="Classify the complexity level of this travel itinerary request.",
                                criteria={
                                    "simple": "Basic short trip with minimal constraints",
                                    "standard_trip": "Standard multi-day vacation plan with normal preferences",
                                    "complex_adventure": "Complex, highly specific or high-risk adventure requirements"
                                }
                            )
                        }
                    )
                    jev_safety_risk = jev_res.nouls["safety_check"].noul
                    jev_intent_category = jev_res.answers["complexity"].choice
                    
                    st.toast(f"⚡ Jev Checked! Safety Risk: {jev_safety_risk:.2f} | Complexity: {jev_intent_category}", icon="🚀")
                except Exception as jev_err:
                    st.warning(f"Jev evaluation skipped due to API error: {jev_err}")

        # Block execution if Jev detects a safety hazard
        if jev_safety_risk > 0.8:
            st.error("🛡️ Security Alert: This request has been flagged by Jev guardrails as potentially unsafe.")
            return

        # Initialize LangGraph state including Jev metrics
        initial_state = TravelState(
            destination=destination,
            source=source,
            num_days=num_days,
            travel_theme=travel_theme,
            activity_preferences=activity_preferences,
            budget=budget,
            flight_class=flight_class,
            hotel_rating=hotel_rating,
            departure_date=str(departure_date),
            return_date=str(return_date),
            flight_data="",
            research_content="",
            hotel_content="",
            itinerary_content="",
            jev_safety_risk=jev_safety_risk,
            jev_intent_category=jev_intent_category
        )
        
        app = create_travel_graph()
        
        run_metadata = {
            "route": f"{source} → {destination}",
            "trip_duration": num_days,
            "travel_theme": travel_theme,
            "jev_complexity": jev_intent_category
        }
        
        with st.spinner("🔍 Searching real-time flights and building multi-agent itinerary..."):
            if LANGSMITH_TRACING:
                result = app.invoke(
                    initial_state,
                    config={
                        "metadata": run_metadata,
                        "run_name": f"Travel Plan: {source} → {destination}"
                    }
                )
            else:
                result = app.invoke(initial_state)
        
        st.success("✅ Travel plan generated successfully!")
        
        # Display results
        st.markdown("---")
        st.subheader("✈️ Flight Options & Analysis")
        st.write(result['flight_data'])
        
        st.markdown("---")
        st.subheader("🗺️ Travel Research & Attractions")
        st.write(result['research_content'])
        
        st.markdown("---")
        st.subheader("🏨 Hotels & Restaurants")
        st.write(result['hotel_content'])
        
        st.markdown("---")
        st.subheader("🗺️ Your Personalized Itinerary")
        st.write(result['itinerary_content'])
        
        full_itinerary = f"""
MY TRAVEL PLAN: {source} → {destination}
{'='*50}
JEV ENGINE METRICS:
- Safety Risk Score: {result['jev_safety_risk']}
- Intent Classification: {result['jev_intent_category']}
{'='*50}
FLIGHTS:\n{result['flight_data']}
{'='*50}
ATTRACTIONS:\n{result['research_content']}
{'='*50}
HOTELS:\n{result['hotel_content']}
{'='*50}
ITINERARY:\n{result['itinerary_content']}
"""
        
        st.download_button(
            label="📥 Download Complete Travel Plan",
            data=full_itinerary,
            file_name=f"travel_plan_{source}_to_{destination}.txt",
            mime="text/plain"
        )


if __name__ == "__main__":
    try:
        mytravelplanner()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.exception(e)
    
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; color: #666;">
            <p style="margin: 5px 0;">© Copyright @CodeInsights</p>
            <p style="margin: 5px 0;">Design and Developed by <strong>Pramodklal</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )