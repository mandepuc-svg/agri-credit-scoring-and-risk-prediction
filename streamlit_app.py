import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Agri-Finance Pro",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "Agri-Finance Pro v3.0 - Advanced Platform"}
)

# ============================================================================
# ADVANCED CSS STYLING
# ============================================================================
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Root colors */
    :root {
        --primary: #667eea;
        --primary-dark: #5568d3;
        --secondary: #764ba2;
        --success: #43e97b;
        --warning: #f5af19;
        --danger: #ff6b6b;
        --dark: #1a1a2e;
        --light: #f8f9fa;
        --glass: rgba(255, 255, 255, 0.25);
    }
    
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #16213e 100%);
        color: #fff;
    }
    
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* ===== HERO HEADER ===== */
    .hero-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        animation: slideDownFade 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(67, 233, 123, 0.05) 0%, rgba(255, 175, 25, 0.05) 100%);
        pointer-events: none;
    }
    
    .hero-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #43e97b 0%, #667eea 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-header p {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.7);
        margin: 0;
    }
    
    /* ===== NAVIGATION ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: linear-gradient(90deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        backdrop-filter: blur(10px);
        padding: 0.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        background: transparent;
        color: rgba(255, 255, 255, 0.6);
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #fff;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        color: #fff !important;
        border: 1px solid rgba(102, 126, 234, 0.5) !important;
    }
    
    /* ===== GLASS CARDS ===== */
    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        animation: slideUpFade 0.6s ease-out;
    }
    
    .glass-card:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.08) 100%);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 12px 48px 0 rgba(102, 126, 234, 0.4);
        transform: translateY(-5px);
    }
    
    /* ===== METRIC CARDS ===== */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        animation: popIn 0.5s ease-out;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
    }
    
    .metric-card.yield {
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%);
        border: 1px solid rgba(67, 233, 123, 0.3);
    }
    
    .metric-card.yield:hover {
        box-shadow: 0 12px 48px rgba(67, 233, 123, 0.4);
        border: 1px solid rgba(67, 233, 123, 0.6);
    }
    
    .metric-card.risk-low {
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.2) 0%, rgba(56, 249, 215, 0.2) 100%);
        border: 1px solid rgba(67, 233, 123, 0.3);
    }
    
    .metric-card.risk-low:hover {
        box-shadow: 0 12px 48px rgba(67, 233, 123, 0.4);
    }
    
    .metric-card.risk-medium {
        background: linear-gradient(135deg, rgba(245, 175, 25, 0.2) 0%, rgba(255, 135, 25, 0.2) 100%);
        border: 1px solid rgba(245, 175, 25, 0.3);
    }
    
    .metric-card.risk-medium:hover {
        box-shadow: 0 12px 48px rgba(245, 175, 25, 0.4);
    }
    
    .metric-card.risk-high {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 75, 75, 0.2) 100%);
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    .metric-card.risk-high:hover {
        box-shadow: 0 12px 48px rgba(255, 107, 107, 0.4);
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #fff;
        margin: 0.5rem 0;
    }
    
    .metric-unit {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* ===== SECTION TITLE ===== */
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.3);
        position: relative;
        display: inline-block;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        width: 0;
        animation: expandWidth 0.6s ease-out forwards;
    }
    
    /* ===== ALERT BOXES ===== */
    .alert-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        animation: slideInLeft 0.5s ease-out;
    }
    
    .alert-success {
        border-left-color: #43e97b;
        background: linear-gradient(135deg, rgba(67, 233, 123, 0.15) 0%, rgba(67, 233, 123, 0.05) 100%);
    }
    
    .alert-warning {
        border-left-color: #f5af19;
        background: linear-gradient(135deg, rgba(245, 175, 25, 0.15) 0%, rgba(245, 175, 25, 0.05) 100%);
    }
    
    .alert-danger {
        border-left-color: #ff6b6b;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15) 0%, rgba(255, 107, 107, 0.05) 100%);
    }
    
    .alert-info {
        border-left-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(102, 126, 234, 0.05) 100%);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.6);
    }
    
    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }
    
    /* ===== INPUT FIELDS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 0.8rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(102, 126, 234, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ===== SLIDERS ===== */
    .stSlider {
        padding: 1rem 0;
    }
    
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* ===== TABLE STYLING ===== */
    .stDataFrame {
        font-size: 0.9rem;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.15);
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes slideDownFade {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUpFade {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes popIn {
        0% {
            opacity: 0;
            transform: scale(0.8);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes shine {
        0% {
            transform: translateX(-100%) translateY(-100%) rotate(45deg);
        }
        100% {
            transform: translateX(100%) translateY(100%) rotate(45deg);
        }
    }
    
    @keyframes expandWidth {
        from {
            width: 0;
        }
        to {
            width: 100%;
        }
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 3rem 1rem;
        color: rgba(255, 255, 255, 0.5);
        margin-top: 5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.9rem;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD MODELS
# ============================================================================
@st.cache_resource
def load_credit_model():
    try:
        with open('farmer_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('encoder.pkl', 'rb') as f:
            encoder = pickle.load(f)
        return model, encoder, True
    except FileNotFoundError:
        return None, None, False

model, encoder, model_loaded = load_credit_model()

# ============================================================================
# YIELD MODEL
# ============================================================================
def predict_yield(rainfall, temperature, soil_ph, nitrogen, farm_size):
    rainfall_effect = -np.power(rainfall - 650, 2) / 50000
    temp_effect = -np.power(temperature - 22, 2) / 20
    ph_effect = -np.power(soil_ph - 6.5, 2) / 0.5
    nitrogen_effect = np.log(nitrogen + 1) * 0.8
    
    predicted = max(0.5,
        3.5 + rainfall_effect / 500 + temp_effect / 100 
        + ph_effect / 10 + nitrogen_effect / 100
    )
    
    return min(12, max(0.5, predicted))

# ============================================================================
# CREDIT SCORING
# ============================================================================
MODEL_FEATURES = [
    'region', 'coop_member', 'farm_size_hectares', 'primary_crop',
    'mobile_money_inflow', 'subsidy_status', 'loan_amount_requested'
]

def normalize_binary_fields(data):
    normalized = dict(data)
    
    coop_value = str(normalized.get('coop_member', '')).strip().lower()
    coop_mapping = {'yes': 1, 'no': 0, 'true': 1, 'false': 0, '1': 1, '0': 0}
    normalized['coop_member'] = coop_mapping.get(coop_value, 0)
    
    subsidy_value = str(normalized.get('subsidy_status', '')).strip().lower()
    subsidy_mapping = {
        'received': 1, 'pending': 1, 'not received': 0,
        'not_received': 0, 'not recieved': 0, '0': 0, '1': 1
    }
    normalized['subsidy_status'] = subsidy_mapping.get(subsidy_value, 0)
    
    return normalized

def score_farmer(farmer_data):
    try:
        normalized = normalize_binary_fields(farmer_data)
        df = pd.DataFrame([normalized]).reindex(columns=MODEL_FEATURES)
        encoded = encoder.transform(df)
        pd_score = model.predict_proba(encoded)[0, 1]
        
        lgd = 0.45
        expected_loss = pd_score * lgd * farmer_data['loan_amount_requested']
        
        pd_pct = pd_score * 100
        if pd_pct > 70:
            risk_cat = 'VERY_HIGH'
        elif pd_pct > 50:
            risk_cat = 'HIGH'
        elif pd_pct > 30:
            risk_cat = 'MEDIUM'
        else:
            risk_cat = 'LOW'
        
        return {
            'pd': pd_score,
            'pd_pct': pd_pct,
            'expected_loss': expected_loss,
            'risk_category': risk_cat
        }
    except Exception as e:
        return {'error': str(e)}

# ============================================================================
# HERO HEADER
# ============================================================================
st.markdown("""
<div class="hero-header">
    <h1>🌾 AGRI-FINANCE PRO</h1>
    <p>Advanced Agricultural Lending Intelligence Platform • Real-time Credit & Yield Analytics</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# NAVIGATION
# ============================================================================
selected = option_menu(
    menu_title=None,
    options=["⚡ Dashboard", "🌾 Yield Pro", "📊 Credit Pro", "📦 Batch Pro", "🔧 Settings"],
    icons=["lightning-fill", "sprout", "graph-up-arrow", "file-arrow-up", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "transparent"},
        "icon": {"color": "#667eea", "font-size": "22px"},
        "nav-link": {
            "font-size": "15px",
            "text-align": "center",
            "margin": "0 5px",
            "padding": "10px 20px",
            "--hover-color": "rgba(102, 126, 234, 0.1)",
            "border-radius": "10px",
            "transition": "all 0.3s ease",
        },
        "nav-link-selected": {"background-color": "rgba(102, 126, 234, 0.2)", "border": "1px solid rgba(102, 126, 234, 0.5)"},
    }
)

# ============================================================================
# TAB 1: DASHBOARD (INTEGRATED)
# ============================================================================
if selected == "⚡ Dashboard":
    st.markdown('<h2 class="section-title">Integrated Assessment Hub</h2>', unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown("""
        <div class="alert-box alert-danger">
            <strong>❌ Critical Error:</strong> Model files not loaded. Ensure farmer_model.pkl and encoder.pkl are in the directory.
        </div>
        """, unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="glass-card"><h3 style="color: #667eea; margin-bottom: 1rem;">📋 Farmer Profile</h3>', unsafe_allow_html=True)
            farmer_id = st.text_input("Farmer ID", value="FARMER_2024_001", key="dash_id")
            region = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'], key="dash_reg")
            coop_member = st.radio("Cooperative Member?", ["Yes", "No"], key="dash_coop", horizontal=True)
            farm_size = st.number_input("Farm Size (hectares)", 0.5, 20.0, 5.0, step=0.5, key="dash_size")
            primary_crop = st.selectbox("Primary Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'], key="dash_crop")
            mobile_money = st.number_input("Annual Mobile Money (TZS)", 0, value=500000, step=50000, key="dash_mobile")
            subsidy = st.radio("Subsidy Status", ['Received', 'Pending', 'Not Received'], key="dash_subsidy")
            loan_amount = st.number_input("Loan Amount Requested (TZS)", 100000, value=2000000, step=100000, key="dash_loan")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card"><h3 style="color: #43e97b; margin-bottom: 1rem;">🌱 Environmental Factors</h3>', unsafe_allow_html=True)
            
            col_rain, col_temp = st.columns(2)
            with col_rain:
                rainfall = st.slider("Rainfall (mm)", 200, 1500, 650, step=50, key="dash_rain")
                st.caption(f"📊 {rainfall}mm/season")
            with col_temp:
                temperature = st.slider("Temp (°C)", 5, 35, 22, step=1, key="dash_temp")
                st.caption(f"🌡️ {temperature}°C avg")
            
            col_ph, col_n = st.columns(2)
            with col_ph:
                soil_ph = st.slider("Soil pH", 4.5, 8.5, 6.5, step=0.1, key="dash_ph")
                st.caption(f"⚗️ pH {soil_ph}")
            with col_n:
                nitrogen = st.slider("Nitrogen (kg/ha)", 20, 250, 120, step=10, key="dash_n")
                st.caption(f"🥬 {nitrogen}kg/ha")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ANALYZE BUTTON
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("⚡ ANALYZE FARMER PROFILE", use_container_width=True, key="analyze"):
                farmer_data = {
                    'region': region,
                    'coop_member': coop_member,
                    'farm_size_hectares': farm_size,
                    'primary_crop': primary_crop,
                    'mobile_money_inflow': mobile_money,
                    'subsidy_status': subsidy,
                    'loan_amount_requested': loan_amount
                }
                
                credit_score = score_farmer(farmer_data)
                
                if 'error' not in credit_score:
                    # PREDICTIONS
                    predicted_yield = predict_yield(rainfall, temperature, soil_ph, nitrogen, farm_size)
                    annual_production = predicted_yield * farm_size
                    farm_income = annual_production * 300 * 1000
                    
                    dsr = 0.35
                    max_loan = farm_income * dsr
                    
                    pd_pct = credit_score['pd_pct']
                    risk_cat = credit_score['risk_category']
                    
                    collateral_factors = {'LOW': 1.2, 'MEDIUM': 1.5, 'HIGH': 2.0, 'VERY_HIGH': 2.5}
                    collateral_factor = collateral_factors.get(risk_cat, 1.5)
                    
                    recommended_loan = min(loan_amount, max_loan)
                    collateral_req = recommended_loan * collateral_factor
                    
                    # DECISION LOGIC
                    if pd_pct < 15 and recommended_loan >= loan_amount * 0.95:
                        decision = "✅ APPROVE"
                        decision_type = "approve"
                    elif pd_pct < 30 and recommended_loan >= loan_amount * 0.80:
                        decision = "⚠️ CONDITIONAL"
                        decision_type = "conditional"
                    else:
                        decision = "❌ RESTRUCTURE"
                        decision_type = "reject"
                    
                    st.success("✨ Analysis Complete!")
                    
                    # METRICS
                    st.markdown('<h3 class="section-title">📊 Key Metrics</h3>', unsafe_allow_html=True)
                    
                    m1, m2, m3, m4 = st.columns(4, gap="medium")
                    
                    with m1:
                        st.markdown(f"""
                        <div class="metric-card yield">
                            <div class="metric-label">🌾 Yield</div>
                            <div class="metric-value">{predicted_yield:.2f}</div>
                            <div class="metric-unit">tons/ha</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with m2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💰 Farm Income</div>
                            <div class="metric-value">{farm_income/1e6:.2f}M</div>
                            <div class="metric-unit">TZS</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with m3:
                        risk_color = 'risk-low' if risk_cat == 'LOW' else 'risk-medium' if risk_cat == 'MEDIUM' else 'risk-high'
                        st.markdown(f"""
                        <div class="metric-card {risk_color}">
                            <div class="metric-label">📈 Credit Risk</div>
                            <div class="metric-value">{pd_pct:.1f}%</div>
                            <div class="metric-unit">{risk_cat}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with m4:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💵 Loan</div>
                            <div class="metric-value">{recommended_loan/1e6:.2f}M</div>
                            <div class="metric-unit">Recommended</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # DECISION BOX
                    st.markdown('<h3 class="section-title">🎯 Recommendation</h3>', unsafe_allow_html=True)
                    
                    alert_class = "alert-success" if decision_type == "approve" else "alert-warning" if decision_type == "conditional" else "alert-danger"
                    
                    st.markdown(f"""
                    <div class="alert-box {alert_class}">
                        <h3 style="margin: 0 0 1rem 0; color: #fff;">{decision}</h3>
                        <p><strong>Recommended Loan:</strong> {recommended_loan/1e6:.2f}M TZS (requested: {loan_amount/1e6:.2f}M)</p>
                        <p><strong>Collateral Required:</strong> {collateral_req/1e6:.2f}M TZS</p>
                        <p><strong>Default Probability:</strong> {pd_pct:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # INTERACTIVE CHARTS
                    st.markdown('<h3 class="section-title">📈 Visualizations</h3>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2, gap="medium")
                    
                    with col1:
                        fig_loan = go.Figure(data=[
                            go.Bar(x=['Requested', 'Recommended', 'Max Available'],
                                   y=[loan_amount/1e6, recommended_loan/1e6, max_loan/1e6],
                                   marker=dict(color=['#ff6b6b', '#667eea', '#43e97b'],
                                             line=dict(color='rgba(255,255,255,0.3)', width=2)),
                                   hovertemplate='<b>%{x}</b><br>%{y:.2f}M TZS<extra></extra>')
                        ])
                        fig_loan.update_layout(
                            title="Loan Comparison",
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=400,
                            showlegend=False,
                            font=dict(color='rgba(255,255,255,0.8)'),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_loan, use_container_width=True)
                    
                    with col2:
                        fig_risk = go.Figure(data=[
                            go.Indicator(
                                mode="gauge+number+delta",
                                value=pd_pct,
                                title={'text': "Default Risk %"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': "#667eea"},
                                    'steps': [
                                        {'range': [0, 15], 'color': "rgba(67, 233, 123, 0.3)"},
                                        {'range': [15, 30], 'color': "rgba(245, 175, 25, 0.3)"},
                                        {'range': [30, 100], 'color': "rgba(255, 107, 107, 0.3)"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': 50
                                    }
                                }
                            )
                        ])
                        fig_risk.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=400,
                            font=dict(color='rgba(255,255,255,0.8)')
                        )
                        st.plotly_chart(fig_risk, use_container_width=True)
                    
                    # SUMMARY TABLE
                    st.markdown('<h3 class="section-title">📋 Full Assessment Report</h3>', unsafe_allow_html=True)
                    
                    summary_data = {
                        '📊 Metric': [
                            'Predicted Yield',
                            'Annual Production',
                            'Farm Income',
                            'Max Sustainable Loan',
                            'Requested Loan',
                            'Recommended Loan',
                            'Default Probability',
                            'Risk Category',
                            'Required Collateral'
                        ],
                        '✨ Value': [
                            f'{predicted_yield:.2f} t/ha',
                            f'{annual_production:.2f} tons',
                            f'{farm_income/1e6:.2f}M TZS',
                            f'{max_loan/1e6:.2f}M TZS',
                            f'{loan_amount/1e6:.2f}M TZS',
                            f'{recommended_loan/1e6:.2f}M TZS',
                            f'{pd_pct:.1f}%',
                            risk_cat,
                            f'{collateral_req/1e6:.2f}M TZS'
                        ]
                    }
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    # DOWNLOAD
                    csv = summary_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Report",
                        data=csv,
                        file_name=f"{farmer_id}_assessment_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

# ============================================================================
# TAB 2: YIELD PRO
# ============================================================================
elif selected == "🌾 Yield Pro":
    st.markdown('<h2 class="section-title">Advanced Yield Intelligence</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown('<div class="glass-card"><h3 style="color: #43e97b; margin-bottom: 1rem;">🌱 Environmental Inputs</h3>', unsafe_allow_html=True)
        y_rainfall = st.slider("Rainfall (mm/season)", 200, 1500, 650, 50, key="y_rain")
        y_temp = st.slider("Temperature (°C)", 5, 35, 22, 1, key="y_temp")
        y_ph = st.slider("Soil pH", 4.5, 8.5, 6.5, 0.1, key="y_ph")
        y_nitrogen = st.slider("Nitrogen (kg/ha)", 20, 250, 120, 10, key="y_n")
        y_size = st.number_input("Farm Size (ha)", 0.5, 20.0, 5.0, 0.5, key="y_size")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card"><h3 style="color: #667eea; margin-bottom: 1rem;">💡 Optimal Ranges</h3>', unsafe_allow_html=True)
        st.markdown("""
        **🌧️ Rainfall:** 650mm
        - <400mm = Drought
        - 400-800mm = ✅ Optimal
        - >1000mm = Waterlogging
        
        **🌡️ Temperature:** 22°C
        - <15°C = Cold
        - 15-28°C = ✅ Optimal
        - >30°C = Heat Stress
        
        **⚗️ Soil pH:** 6.5
        - <5.5 = Too Acidic
        - 5.5-7.5 = ✅ Optimal
        - >7.5 = Too Alkaline
        
        **🥬 Nitrogen:** 150kg/ha
        - Diminishing Returns Beyond
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🚀 RUN YIELD ANALYSIS", use_container_width=True):
        predicted = predict_yield(y_rainfall, y_temp, y_ph, y_nitrogen, y_size)
        production = predicted * y_size
        income = production * 300 * 1000
        
        st.markdown('<h3 class="section-title">🎯 Predictions</h3>', unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.markdown(f"""
            <div class="metric-card yield">
                <div class="metric-label">🌾 Yield</div>
                <div class="metric-value">{predicted:.2f}</div>
                <div class="metric-unit">t/ha</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📊 Production</div>
                <div class="metric-value">{production:.2f}</div>
                <div class="metric-unit">tons</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💰 Income</div>
                <div class="metric-value">{income/1e6:.2f}M</div>
                <div class="metric-unit">TZS</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            max_debt = income * 0.35
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📈 Max Loan</div>
                <div class="metric-value">{max_debt/1e6:.2f}M</div>
                <div class="metric-unit">(35% DSR)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # SENSITIVITY ANALYSIS
        st.markdown('<h3 class="section-title">📊 Sensitivity Analysis</h3>', unsafe_allow_html=True)
        
        rainfall_range = np.arange(200, 1501, 100)
        rainfall_yields = [predict_yield(r, y_temp, y_ph, y_nitrogen, y_size) for r in rainfall_range]
        
        temp_range = np.arange(5, 36, 2)
        temp_yields = [predict_yield(y_rainfall, t, y_ph, y_nitrogen, y_size) for t in temp_range]
        
        nitrogen_range = np.arange(20, 251, 20)
        nitrogen_yields = [predict_yield(y_rainfall, y_temp, y_ph, n, y_size) for n in nitrogen_range]
        
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=rainfall_range, y=rainfall_yields, mode='lines+markers',
                                      line=dict(color='#43e97b', width=3), marker=dict(size=8)))
            fig1.add_vline(x=650, line_dash="dash", line_color="rgba(255,255,255,0.5)")
            fig1.add_vline(x=y_rainfall, line_dash="dash", line_color="#667eea", annotation_text="Your")
            fig1.update_layout(title="Rainfall Effect", template="plotly_dark", height=400,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='rgba(255,255,255,0.8)'), hovermode='x')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=temp_range, y=temp_yields, mode='lines+markers',
                                      line=dict(color='#f5af19', width=3), marker=dict(size=8)))
            fig2.add_vline(x=22, line_dash="dash", line_color="rgba(255,255,255,0.5)")
            fig2.add_vline(x=y_temp, line_dash="dash", line_color="#667eea", annotation_text="Your")
            fig2.update_layout(title="Temperature Effect", template="plotly_dark", height=400,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='rgba(255,255,255,0.8)'), hovermode='x')
            st.plotly_chart(fig2, use_container_width=True)
        
        with col3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=nitrogen_range, y=nitrogen_yields, mode='lines+markers',
                                      line=dict(color='#ff6b6b', width=3), marker=dict(size=8)))
            fig3.add_vline(x=150, line_dash="dash", line_color="rgba(255,255,255,0.5)")
            fig3.add_vline(x=y_nitrogen, line_dash="dash", line_color="#667eea", annotation_text="Your")
            fig3.update_layout(title="Nitrogen Effect", template="plotly_dark", height=400,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='rgba(255,255,255,0.8)'), hovermode='x')
            st.plotly_chart(fig3, use_container_width=True)

# ============================================================================
# TAB 3: CREDIT PRO
# ============================================================================
elif selected == "📊 Credit Pro":
    st.markdown('<h2 class="section-title">Advanced Credit Assessment</h2>', unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown('<div class="alert-box alert-danger"><strong>❌ Error:</strong> Model not loaded</div>', unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown('<div class="glass-card"><h3 style="color: #667eea;">Credit Profile</h3>', unsafe_allow_html=True)
            region3 = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'], key='c3_region')
            coop3 = st.radio("Cooperative?", ["Yes", "No"], key='c3_coop', horizontal=True)
            size3 = st.number_input("Farm Size (ha)", 0.5, 20.0, 5.0, key='c3_size')
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="glass-card"><h3 style="color: #43e97b;">Financial Profile</h3>', unsafe_allow_html=True)
            crop3 = st.selectbox("Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'], key='c3_crop')
            mobile3 = st.number_input("Mobile Money (TZS)", 0, value=500000, key='c3_mobile')
            subsidy3 = st.radio("Subsidy", ['Received', 'Pending', 'Not Received'], key='c3_subsidy')
            st.markdown('</div>', unsafe_allow_html=True)
        
        loan3 = st.number_input("Loan Amount (TZS)", 100000, value=2000000, key='c3_loan')
        
        if st.button("🔍 SCORE FARMER", use_container_width=True):
            data = {
                'region': region3, 'coop_member': coop3, 'farm_size_hectares': size3,
                'primary_crop': crop3, 'mobile_money_inflow': mobile3,
                'subsidy_status': subsidy3, 'loan_amount_requested': loan3
            }
            
            result = score_farmer(data)
            if 'error' not in result:
                m1, m2, m3, m4 = st.columns(4, gap="medium")
                
                risk_class = 'risk-low' if result['risk_category'] == 'LOW' else 'risk-medium' if result['risk_category'] == 'MEDIUM' else 'risk-high'
                
                with m1:
                    st.markdown(f"""
                    <div class="metric-card {risk_class}">
                        <div class="metric-label">📈 PD %</div>
                        <div class="metric-value">{result['pd_pct']:.1f}%</div>
                        <div class="metric-unit">Default Risk</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📌 Category</div>
                        <div class="metric-value" style="font-size: 1.6rem;">{result['risk_category']}</div>
                        <div class="metric-unit">Risk Level</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">💸 Loss</div>
                        <div class="metric-value">{result['expected_loss']/1e6:.2f}M</div>
                        <div class="metric-unit">Expected</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">💰 Loan</div>
                        <div class="metric-value">{loan3/1e6:.2f}M</div>
                        <div class="metric-unit">Requested</div>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: BATCH PRO
# ============================================================================
elif selected == "📦 Batch Pro":
    st.markdown('<h2 class="section-title">Batch Processing Engine</h2>', unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown('<div class="alert-box alert-danger"><strong>❌ Error:</strong> Model not loaded</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card">
        <strong>📋 Required CSV Columns:</strong> region, coop_member (Yes/No), farm_size_hectares, primary_crop, mobile_money_inflow, subsidy_status, loan_amount_requested
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"📊 Loaded {len(df)} farmers")
            
            if st.button("⚡ SCORE ALL FARMERS", use_container_width=True):
                results = []
                progress = st.progress(0)
                
                for idx, row in df.iterrows():
                    score = score_farmer(row.to_dict())
                    combined = {**row.to_dict(), **score}
                    results.append(combined)
                    progress.progress((idx + 1) / len(df))
                
                results_df = pd.DataFrame(results)
                
                m1, m2, m3, m4 = st.columns(4, gap="medium")
                with m1:
                    st.markdown(f"""
                    <div class="metric-card risk-high">
                        <div class="metric-label">⚠️ Very High</div>
                        <div class="metric-value">{len(results_df[results_df['risk_category'] == 'VERY_HIGH'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="metric-card risk-high">
                        <div class="metric-label">🔴 High</div>
                        <div class="metric-value">{len(results_df[results_df['risk_category'] == 'HIGH'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="metric-card risk-medium">
                        <div class="metric-label">🟡 Medium</div>
                        <div class="metric-value">{len(results_df[results_df['risk_category'] == 'MEDIUM'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m4:
                    st.markdown(f"""
                    <div class="metric-card risk-low">
                        <div class="metric-label">🟢 Low</div>
                        <div class="metric-value">{len(results_df[results_df['risk_category'] == 'LOW'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.dataframe(results_df, use_container_width=True)
                
                csv = results_df.to_csv(index=False)
                st.download_button("📥 Download Results", csv, "batch_scores.csv", "text/csv")
                
                # PIE CHART
                risk_counts = results_df['risk_category'].value_counts()
                fig = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values,
                                             marker=dict(colors=['#43e97b', '#f5af19', '#ff6b6b', '#667eea']),
                                             hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>')])
                fig.update_layout(title="Risk Distribution", template="plotly_dark", height=400,
                                 paper_bgcolor='rgba(0,0,0,0)', font=dict(color='rgba(255,255,255,0.8)'))
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 5: SETTINGS
# ============================================================================
elif selected == "🔧 Settings":
    st.markdown('<h2 class="section-title">Platform Settings</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
    <h3 style="color: #667eea; margin-bottom: 1rem;">⚙️ Configuration</h3>
    
    **Debt Service Ratio (DSR):** 35%  
    **Loss Given Default (LGD):** 45%  
    **Market Price:** 300 TZS/ton  
    **Model Version:** 3.0 - Advanced  
    **Last Updated:** September 2024
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>🌾 AGRI-FINANCE PRO v3.0 | Advanced Agricultural Lending Intelligence | © 2024</p>
    <p style="color: rgba(255, 255, 255, 0.4); font-size: 0.8rem;">Powered by Machine Learning | Real-time Credit & Yield Analytics</p>
</div>
""", unsafe_allow_html=True)