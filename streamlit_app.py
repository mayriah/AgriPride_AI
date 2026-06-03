import streamlit as st
import re
from crew import build_crew
from llm_router import LLMRouter

# Page Configuration - Set tab title, emoji, and force wide layout
st.set_page_config(
    page_title="AgriPride AI - Market & Logistics Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom premium CSS styles for a stunning, high-contrast interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* General app override to a deep slate theme for maximum contrast */
    .stApp {
        background-color: #0A0F1D;
        color: #F1F5F9;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Ensure sidebar matches the deep theme */
    section[data-testid="stSidebar"] {
        background-color: #070B14 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    /* Title and Header Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    /* Top Banner Gradient */
    .banner-container {
        background: linear-gradient(135deg, #059669 0%, #1D4ED8 100%);
        border-radius: 16px;
        padding: 35px 25px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        position: relative;
    }
    .banner-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .banner-subtitle {
        font-size: 1.15rem;
        color: #F8FAFC;
        margin-top: 10px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Input Container Styling */
    .input-section {
        background-color: #111827;
        border-radius: 16px;
        padding: 30px;
        border: 1px solid #1F2937;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px;
    }
    
    /* High-contrast styles for Streamlit native inputs */
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 2px solid #334155 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 10px !important;
    }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 8px !important;
    }
    
    /* Styled action button - high contrast emerald green */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 14px 28px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6) !important;
        transform: translateY(-1px);
    }
    
    /* Metrics panel for high readability */
    div[data-testid="metric-container"] {
        background-color: #111827 !important;
        border: 2px solid #1F2937 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem !important;
        margin-bottom: 6px !important;
    }
    
    /* Custom CSS Cards for Results */
    .result-card {
        background-color: #111827;
        border-radius: 14px;
        padding: 25px;
        border: 1px solid #334155;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .result-header {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 15px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 2px solid #1F2937;
        padding-bottom: 12px;
    }
    
    /* Consistent Color Coding Borders */
    .border-advice { border-left: 6px solid #10B981 !important; } /* Green for advice/success */
    .border-risk { border-left: 6px solid #F59E0B !important; }    /* Orange for warning/risk */
    .border-planb { border-left: 6px solid #3B82F6 !important; }   /* Blue for plan B/info */
    .border-final { border-left: 6px solid #8B5CF6 !important; }   /* Purple for final plan */
    .border-safety { border-left: 6px solid #EF4444 !important; }  /* Red for critical/rejected */
    
    /* Sidebar Details Card */
    .sidebar-card {
        background-color: #111827;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #1F2937;
        margin-bottom: 12px;
    }
    
    /* High contrast status indicators */
    .indicator-pill {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .pill-active {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .pill-fallback {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    
    /* Streamlit custom tabs with high contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px 8px 0px 0px !important;
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        background-color: #1F2937 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1F2937 !important;
        color: #10B981 !important;
        border-top: 3px solid #10B981 !important;
        border-bottom: none !important;
    }
    
    /* High-contrast tables */
    .info-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        margin-top: 10px;
    }
    .info-table tr {
        border-bottom: 2px solid #1F2937;
    }
    .info-table td {
        padding: 14px 10px;
        font-size: 1rem;
    }
    .info-table td.label {
        color: #E2E8F0;
        font-weight: 600;
        width: 35%;
    }
    .info-table td.val {
        color: #FFFFFF;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------

def parse_scout_analysis(analysis_text):
    """
    Parses the scout's analysis report into three main structured sections:
    SELL ADVICE, RISK, and PLAN B.
    """
    sections = {"SELL ADVICE": "", "RISK": "", "PLAN B": ""}
    
    # Split text by matching headings
    pattern = r"(?mi)^\s*(SELL ADVICE|RISK|PLAN B)\s*:\s*"
    parts = re.split(pattern, analysis_text)
    
    current_key = None
    for part in parts:
        part_strip = part.strip()
        upper_part = part_strip.upper()
        if upper_part in ["SELL ADVICE", "RISK", "PLAN B"]:
            current_key = upper_part
        elif current_key:
            if sections[current_key]:
                sections[current_key] += "\n" + part_strip
            else:
                sections[current_key] = part_strip
                
    # Fallback if parsing fails to find sections
    if not any(sections.values()):
        sections["SELL ADVICE"] = analysis_text
        
    return sections

# ----------------- Sidebar Status Dashboard -----------------

router = LLMRouter()
active_providers = router.active_providers

with st.sidebar:
    st.markdown("### 🌾 AgriPride AI Panel")
    st.markdown("---")
    
    st.markdown("#### **Active LLM Fallback Stack**")
    
    # Show active providers with high-contrast status indicators
    for i, provider in enumerate(active_providers):
        is_primary = (i == 0)
        pill_class = "pill-active" if is_primary else "pill-fallback"
        pill_label = "Primary" if is_primary else f"Fallback #{i}"
        
        st.markdown(f"""
        <div class="sidebar-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: #FFFFFF; font-size: 1rem; text-transform: capitalize;">{provider}</strong>
                <span class="indicator-pill {pill_class}">{pill_label}</span>
            </div>
            <div style="font-size: 0.85rem; color: #E2E8F0; margin-top: 5px;">
                Ready to handle requests. Auto-route on rate-limit.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("#### **System Info**")
    st.info("The system automatically checks Gemini. If Gemini encounters rate limits or daily quota exhaustion, requests seamlessly routing to Cohere and Cerebras.")

# ----------------- Main App UI Header -----------------

st.markdown("""
<div class="banner-container">
    <h1 class="banner-title">🌾 AgriPride AI</h1>
    <div class="banner-subtitle">Intelligent Market Scouting, Compliance Guard & Transport Router</div>
</div>
""", unsafe_allow_html=True)

# ----------------- Input Panel -----------------

st.markdown("### **Enter Farmer Request Details**")
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        crop = st.text_input("Crop Type", "maize", help="Select or type the crop (e.g. maize, beans, coffee)")
        location = st.text_input("Location / Market Origin", "Masindi", help="District/Town where the crop is currently stored")
    
    with col2:
        qty = st.number_input("Stock Quantity (kg)", min_value=10, max_value=100000, value=800, step=10, help="Total weight of crop in kilograms")
        days = st.number_input("Days to Required Cash", min_value=1, max_value=365, value=14, help="Number of days the farmer can afford to wait before needing cash")
        
    run_btn = st.button("🚀 Execute Multi-Agent Routing", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- Processing & Output -----------------

if run_btn:
    input_data = {
        "crop": crop,
        "location": location,
        "quantity_kg": qty,
        "need_cash_in_days": days,
    }
    
    with st.spinner("Initiating agent workflow (Scout ➜ Guard ➜ Guardian ➜ Hunt)..."):
        try:
            crew = build_crew(input_data)
            result = crew.kickoff()
            
            status = result.get("status", "completed")
            
            # --- Status: Completed successfully ---
            if status == "completed":
                st.success("Workflow executed successfully! Agents completed evaluation and routing.")
                
                # Fetch data from agent responses
                scout_data = result.get("scout", {})
                guardian_data = result.get("guardian", {})
                guard_review = result.get("guard_review", {})
                final_data = result.get("final", {})
                
                market_prices = scout_data.get("prices", {})
                weather_info = scout_data.get("weather", {})
                logistics_route = guardian_data.get("route", {})
                
                # Header Metrics Row
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                
                price_val = market_prices.get("price_per_kg", 0)
                currency = market_prices.get("currency", "UGX")
                volatility = market_prices.get("volatility", 0.0)
                
                est_cost = logistics_route.get("estimated_cost", 0)
                distance = logistics_route.get("distance_km", 0)
                road_cond = logistics_route.get("road_condition", "N/A")
                
                rain_risk = weather_info.get("rain_risk", 0.0)
                weather_desc = weather_info.get("summary", "")
                
                with m_col1:
                    st.metric(
                        label="Market Price Estimate", 
                        value=f"{price_val:,} {currency}/kg", 
                        delta=f"Volatility: {volatility * 100:.0f}%"
                    )
                with m_col2:
                    st.metric(
                        label="Rain Risk (Next 5 Days)", 
                        value=f"{rain_risk * 100:.0f}%", 
                        delta=weather_desc,
                        delta_color="off"
                    )
                with m_col3:
                    st.metric(
                        label="Est. Transport Cost", 
                        value=f"{est_cost:,} {currency}", 
                        delta=f"Roads: {road_cond.capitalize()}"
                    )
                with m_col4:
                    st.metric(
                        label="Delivery Distance", 
                        value=f"{distance} km", 
                        delta=f"Route from {location}"
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display parsed sections inside modern tab component
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🎯 Final Action Plan", 
                    "📊 Market & Weather Analysis", 
                    "🚚 Logistics & Transport", 
                    "🛡️ Compliance & Safety Review",
                    "⚙️ Raw System Output"
                ])
                
                # Tab 1: Final Action Plan
                with tab1:
                    st.markdown(f"""
                    <div class="result-card border-final">
                        <div class="result-header">🎯 Hunt Agent Final Action Plan</div>
                        <div style="font-size: 1.1rem; line-height: 1.7; color: #F1F5F9;">
                            {final_data.get("summary", "No action plan generated.")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Tab 2: Market & Weather Analysis
                with tab2:
                    scout_sections = parse_scout_analysis(scout_data.get("analysis", ""))
                    
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        if scout_sections.get("SELL ADVICE"):
                            st.markdown(f"""
                            <div class="result-card border-advice">
                                <div class="result-header" style="color: #10B981;">💰 Sell Advice</div>
                                <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem;">{scout_sections["SELL ADVICE"]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        if scout_sections.get("PLAN B"):
                            st.markdown(f"""
                            <div class="result-card border-planb">
                                <div class="result-header" style="color: #3B82F6;">🛡️ Plan B Contingency</div>
                                <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem;">{scout_sections["PLAN B"]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                    with col_right:
                        if scout_sections.get("RISK"):
                            st.markdown(f"""
                            <div class="result-card border-risk">
                                <div class="result-header" style="color: #F59E0B;">⚠️ Identified Risks</div>
                                <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem;">{scout_sections["RISK"]}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        # Show raw details card
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="result-header">🔍 Raw Market Indicators</div>
                            <ul style="color: #F1F5F9; font-size: 1rem; line-height: 1.8;">
                                <li><b>Uncertainty Index:</b> {market_prices.get("uncertainty", 0.0) * 100:.0f}%</li>
                                <li><b>Data Latency:</b> Last updated on {market_prices.get("last_updated", "unknown")}</li>
                                <li><b>Weather Forecast Days:</b> {weather_info.get("forecast_days", 5)} days</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Tab 3: Logistics & Transport
                with tab3:
                    st.markdown(f"""
                    <div class="result-card border-planb">
                        <div class="result-header">🚚 Guardian Agent Logistics Plan</div>
                        <div style="font-size: 1.1rem; line-height: 1.7; color: #F1F5F9; margin-bottom: 20px;">
                            {guardian_data.get("plan", "No transport plan generated.")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display route specifications card
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="result-header">📍 Route Specification</div>
                        <table class="info-table">
                            <tr>
                                <td class="label">Route Origin:</td>
                                <td class="val">{logistics_route.get("origin", "Unknown")}</td>
                            </tr>
                            <tr>
                                <td class="label">Load Quantity:</td>
                                <td class="val">{logistics_route.get("quantity_kg", 0):,} kg</td>
                            </tr>
                            <tr>
                                <td class="label">Distance to Hub:</td>
                                <td class="val">{distance} km</td>
                            </tr>
                            <tr>
                                <td class="label">Transport Cost Ratio:</td>
                                <td class="val">{logistics_route.get("transport_cost_ratio", 0.0) * 100:.1f}% of total value</td>
                            </tr>
                            <tr>
                                <td class="label">Logistics Risk Index:</td>
                                <td class="val" style="text-transform: capitalize;">{logistics_route.get("risk", "Unknown")}</td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Tab 4: Safety & Review Guard
                with tab4:
                    is_approved = guard_review.get("status") == "approved"
                    status_color = "#10B981" if is_approved else "#EF4444"
                    status_text = "APPROVED" if is_approved else "REJECTED"
                    border_class = "border-advice" if is_approved else "border-safety"
                    
                    st.markdown(f"""
                    <div class="result-card {border_class}">
                        <div class="result-header">🛡️ Guard Agent Compliance Assessment</div>
                        <div style="margin-bottom: 20px;">
                            <span style="background-color: {status_color}22; color: {status_color}; border: 2px solid {status_color}; padding: 6px 18px; border-radius: 9999px; font-weight: 800; font-size: 0.95rem; text-transform: uppercase;">
                                STATUS: {status_text}
                            </span>
                        </div>
                        <div style="font-size: 1.1rem; line-height: 1.7; color: #F1F5F9;">
                            {guard_review.get("review", "No compliance review available.")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Tab 5: Raw Output (Collapsible Details)
                with tab5:
                    st.markdown("#### Full Pipeline JSON Response")
                    st.json(result)
                    
            # --- Status: Rejected by Guard ---
            elif status == "rejected":
                guard_review = result.get("guard_review", {})
                escalation = result.get("escalation", {})
                
                st.error("🚨 Ethics/Safety Guard Rejected the recommendation. Execution halted.")
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown(f"""
                    <div class="result-card border-safety">
                        <div class="result-header" style="color: #EF4444;">🛑 Safety Review Reason</div>
                        <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem;">{guard_review.get("review", "Safety review details not provided.")}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_right:
                    st.markdown(f"""
                    <div class="result-card border-safety">
                        <div class="result-header" style="color: #EF4444;">💼 Escalation Pathway</div>
                        <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem; margin-bottom: 15px;">{escalation.get("message", "Escalation details not provided.")}</div>
                        <div style="background-color: rgba(239, 68, 68, 0.15); border: 2px solid #EF4444; border-radius: 8px; padding: 14px; font-size: 0.9rem; color: #FFFFFF; font-weight: 600;">
                            This ticket has been logged for supervisor attention. Action plan generation was blocked.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Raw Details
                with st.expander("Show System Details"):
                    st.json(result)
                    
            # --- Status: Escalated ---
            elif status == "escalated":
                reason = result.get("reason", "unknown validation error")
                escalation = result.get("escalation", {})
                
                st.warning("⚠️ Market validation constraints triggered. Workflow escalated to human review.")
                
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown(f"""
                    <div class="result-card border-risk">
                        <div class="result-header" style="color: #F59E0B;">🔔 Validation Constraint Breached</div>
                        <div style="line-height: 1.6; font-size: 1.1rem; color: #F1F5F9;">
                            The engine flagged: <b style="color: #FFFFFF; background-color: rgba(245, 158, 11, 0.2); padding: 4px 8px; border-radius: 4px; border: 1px solid #F59E0B;">{reason}</b>
                        </div>
                        <p style="margin-top: 15px; font-size: 0.95rem; color: #CBD5E1; line-height: 1.6;">
                            This occurs when uncertainty thresholds or price volatility margins exceed limits, requiring supervisory authorization before proceeding.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_right:
                    st.markdown(f"""
                    <div class="result-card border-risk">
                        <div class="result-header" style="color: #F59E0B;">💼 Escalation Details</div>
                        <div style="line-height: 1.6; color: #F1F5F9; font-size: 1.05rem; margin-bottom: 15px;">{escalation.get("message", "No escalation details available.")}</div>
                        <div style="background-color: rgba(245, 158, 11, 0.15); border: 2px solid #F59E0B; border-radius: 8px; padding: 14px; font-size: 0.9rem; color: #FFFFFF; font-weight: 600;">
                            Workflow status escalated. Agent recommendations are held in pending state.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Raw Details
                with st.expander("Show System Details"):
                    st.json(result)
                    
        except Exception as exc:
            st.error(f"Error during system run: {exc}")
