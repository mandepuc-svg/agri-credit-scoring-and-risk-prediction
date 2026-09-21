import streamlit as st
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Agri-Credit & Yield Platform",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Agri-Credit & Yield Prediction Platform v2.1"
    }
)

# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================
st.markdown("""
<style>
    /* Main page styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    .metric-card.yield {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    .metric-card.risk-low {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card.risk-medium {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .metric-card.risk-high {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    /* Section styling */
    .section-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e0f7ff 0%, #f0e7ff 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #667eea;
        margin-bottom: 1.5rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #4caf50;
        margin: 1.5rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
        margin: 1.5rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #f44336;
        margin: 1.5rem 0;
    }
    
    /* Form styling */
    .form-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .form-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Slider styling */
    .stSlider {
        padding: 1rem 0;
    }
    
    /* Radio button styling */
    .stRadio {
        padding: 0.5rem 0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.8rem 1.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
        border-top: 1px solid #eee;
    }
    
    /* Animation */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-container h1 {
            font-size: 1.8rem;
        }
        
        .metric-card {
            margin-bottom: 1rem;
        }
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
# HEADER
# ============================================================================
st.markdown("""
<div class="header-container">
    <h1>🌾 Agri-Credit & Yield Prediction Platform</h1>
    <p>Integrated Loan Decision Support System • Credit Risk Assessment + Crop Yield Prediction</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# NAVIGATION MENU
# ============================================================================
selected = option_menu(
    menu_title="Navigation",
    options=["🔗 Integrated", "🌾 Crop Yield", "📊 Credit Score", "📦 Batch", "ℹ️ About"],
    icons=["link", "sprout", "graph-up", "file-earmark-arrow-up", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#f0f2f6"},
        "icon": {"color": "#667eea", "font-size": "25px"},
        "nav-link": {
            "font-size": "16px",
            "text-align": "center",
            "margin": "0px",
            "padding": "10px 20px",
            "--hover-color": "#eee",
        },
        "nav-link-selected": {"background-color": "#667eea", "color": "white"},
    }
)

# ============================================================================
# TAB 1: INTEGRATED ANALYSIS
# ============================================================================
if selected == "🔗 Integrated":
    st.markdown('<div class="section-title">Integrated Farmer Assessment</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>🔍 How it works:</strong><br>
        1. Enter farmer profile & credit details<br>
        2. Enter farm conditions & environmental factors<br>
        3. Get unified loan recommendation combining both factors
    </div>
    """, unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown('<div class="error-box"><strong>❌ Error:</strong> Model files not loaded. Please ensure farmer_model.pkl and encoder.pkl are in the same directory.</div>', unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="form-title">👤 Farmer & Credit Profile</div>', unsafe_allow_html=True)
            farmer_id = st.text_input("Farmer ID", value="FARMER_0001")
            region = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'])
            coop_member = st.radio("Cooperative Member?", ["Yes", "No"], index=0)
            farm_size = st.number_input("Farm Size (hectares)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
            primary_crop = st.selectbox("Primary Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'])
            mobile_money = st.number_input("Annual Mobile Money (TZS)", min_value=0, value=500000, step=50000)
            subsidy = st.radio("Subsidy Status", ['Received', 'Pending', 'Not Received'], index=1)
            loan_amount = st.number_input("Loan Amount Requested (TZS)", min_value=100000, value=2000000, step=100000)
        
        with col2:
            st.markdown('<div class="form-title">🌱 Farm Conditions</div>', unsafe_allow_html=True)
            rainfall = st.slider("Rainfall (mm/season)", min_value=200, max_value=1500, value=650, step=50)
            temperature = st.slider("Avg Temperature (°C)", min_value=5, max_value=35, value=22, step=1)
            soil_ph = st.slider("Soil pH Level", min_value=4.5, max_value=8.5, value=6.5, step=0.1)
            nitrogen = st.slider("Nitrogen Applied (kg/ha)", min_value=20, max_value=250, value=120, step=10)
            
            with st.expander("📖 Optimal Conditions Reference"):
                st.markdown("""
                - **Rainfall:** ~650mm (too little = drought, too much = waterlogging)
                - **Temperature:** ~22°C (below 15°C or above 28°C = stress)
                - **Soil pH:** 6.5 (neutral - too acidic/alkaline reduces nutrients)
                - **Nitrogen:** ~150kg/ha (diminishing returns beyond this)
                """)
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            analyze_btn = st.button("🎯 Analyze Farmer", key="analyze", use_container_width=True)
        with col2:
            reset_btn = st.button("↺ Reset", key="reset", use_container_width=True)
        
        if analyze_btn:
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
                predicted_yield = predict_yield(rainfall, temperature, soil_ph, nitrogen, farm_size)
                annual_production = predicted_yield * farm_size
                farm_income = annual_production * 300 * 1000
                
                dsr = 0.35
                max_loan = farm_income * dsr
                
                pd = credit_score['pd']
                pd_pct = credit_score['pd_pct']
                risk_cat = credit_score['risk_category']
                
                collateral_factors = {
                    'LOW': 1.2,
                    'MEDIUM': 1.5,
                    'HIGH': 2.0,
                    'VERY_HIGH': 2.5
                }
                collateral_factor = collateral_factors.get(risk_cat, 1.5)
                
                recommended_loan = min(loan_amount, max_loan)
                collateral_req = recommended_loan * collateral_factor
                
                if pd_pct < 15 and recommended_loan >= loan_amount * 0.95:
                    decision = "✅ APPROVE"
                    decision_type = "approve"
                elif pd_pct < 30 and recommended_loan >= loan_amount * 0.80:
                    decision = "⚠️ CONDITIONAL APPROVAL"
                    decision_type = "conditional"
                else:
                    decision = "❌ REJECT / RESTRUCTURE"
                    decision_type = "reject"
                
                st.markdown('<div class="success-box"><strong>✓ Analysis Complete</strong></div>', unsafe_allow_html=True)
                
                # METRICS WITH CUSTOM CARDS
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="metric-card yield">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Predicted Yield</div>
                        <div style="font-size: 2rem; font-weight: bold;">{predicted_yield:.2f}</div>
                        <div style="font-size: 0.85rem;">t/ha</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Annual Income</div>
                        <div style="font-size: 2rem; font-weight: bold;">{farm_income/1e6:.2f}M</div>
                        <div style="font-size: 0.85rem;">TZS</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m3:
                    st.markdown(f"""
                    <div class="metric-card {'risk-low' if risk_cat == 'LOW' else 'risk-medium' if risk_cat == 'MEDIUM' else 'risk-high'}">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Credit Risk</div>
                        <div style="font-size: 2rem; font-weight: bold;">{pd_pct:.1f}%</div>
                        <div style="font-size: 0.85rem;">{risk_cat}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Recommended Loan</div>
                        <div style="font-size: 2rem; font-weight: bold;">{recommended_loan/1e6:.2f}M</div>
                        <div style="font-size: 0.85rem;">TZS</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # DECISION BOXES
                if decision_type == "approve":
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>{decision}</strong><br>
                        <strong>Loan Approved:</strong> {recommended_loan/1e6:.2f}M TZS (requested: {loan_amount/1e6:.2f}M)<br>
                        <strong>Collateral Required:</strong> {collateral_req/1e6:.2f}M TZS<br>
                        <strong>Terms:</strong> Standard 3-year loan with annual reviews
                    </div>
                    """, unsafe_allow_html=True)
                elif decision_type == "conditional":
                    st.markdown(f"""
                    <div class="warning-box">
                        <strong>{decision}</strong><br>
                        <strong>Approved Loan:</strong> {recommended_loan/1e6:.2f}M TZS (vs requested: {loan_amount/1e6:.2f}M)<br>
                        <strong>Collateral Required:</strong> {collateral_req/1e6:.2f}M TZS<br>
                        <strong>Conditions:</strong> Enhanced monitoring (quarterly reviews), Crop insurance required
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="error-box">
                        <strong>{decision}</strong><br>
                        <strong>Recommended Loan:</strong> {recommended_loan/1e6:.2f}M TZS (vs requested: {loan_amount/1e6:.2f}M)<br>
                        <strong>Collateral Required:</strong> {collateral_req/1e6:.2f}M TZS
                    </div>
                    """, unsafe_allow_html=True)
                
                # SUMMARY TABLE
                st.markdown('<div class="section-title">📋 Decision Summary</div>', unsafe_allow_html=True)
                
                summary_data = {
                    'Metric': [
                        'Predicted Yield', 'Annual Production', 'Estimated Farm Income',
                        'Max Loan (from yield)', 'Requested Loan', 'Recommended Loan',
                        'Probability of Default', 'Risk Category', 'Collateral Required'
                    ],
                    'Value': [
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
                
                # INTERACTIVE CHART: Loan Breakdown
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Requested', 'Recommended', 'Max from Yield'],
                        y=[loan_amount/1e6, recommended_loan/1e6, max_loan/1e6],
                        marker=dict(
                            color=['#f44336', '#667eea', '#4caf50'],
                            line=dict(color='white', width=2)
                        ),
                        text=[f'{x:.2f}M' for x in [loan_amount/1e6, recommended_loan/1e6, max_loan/1e6]],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Amount: %{y:.2f}M TZS<extra></extra>'
                    )
                ])
                
                fig.update_layout(
                    title="Loan Amount Comparison",
                    yaxis_title="Amount (Million TZS)",
                    hovermode='x unified',
                    template='plotly_white',
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # DOWNLOAD
                results_csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results",
                    data=results_csv,
                    file_name=f"{farmer_id}_analysis.csv",
                    mime="text/csv"
                )

# ============================================================================
# TAB 2: CROP YIELD
# ============================================================================
elif selected == "🌾 Crop Yield":
    st.markdown('<div class="section-title">Crop Yield Prediction & Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>🌱 Predict crop yield based on farm conditions</strong><br>
        - Rainfall, temperature, soil pH, and fertilizer affect yield<br>
        - Model captures non-linear relationships (Goldilocks effects)<br>
        - Use this to estimate farming income and calculate sustainable loans
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-title">📊 Input Farm Conditions</div>', unsafe_allow_html=True)
        
        yield_rainfall = st.slider("Rainfall (mm/season)", min_value=200, max_value=1500, value=650, step=50, key='yield_rain')
        yield_temp = st.slider("Avg Temperature (°C)", min_value=5, max_value=35, value=22, step=1, key='yield_temp')
        yield_ph = st.slider("Soil pH Level", min_value=4.5, max_value=8.5, value=6.5, step=0.1, key='yield_ph')
        yield_nitrogen = st.slider("Nitrogen (kg/ha)", min_value=20, max_value=250, value=120, step=10, key='yield_n')
        yield_farm_size = st.number_input("Farm Size (hectares)", min_value=0.5, max_value=20.0, value=5.0, step=0.5, key='yield_size')
        yield_market_price = st.number_input("Market Price (TZS/ton)", min_value=100, max_value=1000, value=300, step=50, key='yield_price')
    
    with col2:
        st.markdown('<div class="form-title">📖 Optimal Conditions</div>', unsafe_allow_html=True)
        
        st.markdown("""
        **Rainfall:** 650mm
        - <400mm = Drought stress
        - 400-800mm = Optimal
        - >1000mm = Waterlogging
        
        **Temperature:** 22°C
        - <15°C = Cold stress
        - 15-28°C = Optimal
        - >30°C = Heat stress
        
        **Soil pH:** 6.5
        - <5.5 = Too acidic
        - 5.5-7.5 = Optimal
        - >7.5 = Too alkaline
        
        **Nitrogen:** 150 kg/ha
        - Diminishing returns beyond
        - Optimal sweet spot
        """)
    
    if st.button("🎯 Predict Yield", key="predict_yield", use_container_width=True):
        predicted = predict_yield(yield_rainfall, yield_temp, yield_ph, yield_nitrogen, yield_farm_size)
        production = predicted * yield_farm_size
        income = production * yield_market_price * 1000
        
        st.markdown('<div class="success-box"><strong>✓ Prediction Complete</strong></div>', unsafe_allow_html=True)
        
        # METRICS
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-card yield">
                <div style="font-size: 0.9rem; opacity: 0.9;">Predicted Yield</div>
                <div style="font-size: 2rem; font-weight: bold;">{predicted:.2f}</div>
                <div style="font-size: 0.85rem;">t/ha</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; opacity: 0.9;">Annual Production</div>
                <div style="font-size: 2rem; font-weight: bold;">{production:.2f}</div>
                <div style="font-size: 0.85rem;">tons</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; opacity: 0.9;">Farm Income</div>
                <div style="font-size: 2rem; font-weight: bold;">{income/1e6:.2f}M</div>
                <div style="font-size: 0.85rem;">TZS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with m4:
            max_annual_debt = income * 0.35
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; opacity: 0.9;">Max Annual Payment</div>
                <div style="font-size: 2rem; font-weight: bold;">{max_annual_debt/1e6:.2f}M</div>
                <div style="font-size: 0.85rem;">(35% DSR)</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # INTERACTIVE CHARTS WITH PLOTLY
        st.markdown('<div class="section-title">📈 Yield Sensitivity Analysis</div>', unsafe_allow_html=True)
        
        # Rainfall sensitivity
        rainfall_range = np.arange(200, 1501, 100)
        rainfall_yields = [predict_yield(r, yield_temp, yield_ph, yield_nitrogen, yield_farm_size) for r in rainfall_range]
        
        temp_range = np.arange(5, 36, 2)
        temp_yields = [predict_yield(yield_rainfall, t, yield_ph, yield_nitrogen, yield_farm_size) for t in temp_range]
        
        nitrogen_range = np.arange(20, 251, 20)
        nitrogen_yields = [predict_yield(yield_rainfall, yield_temp, yield_ph, n, yield_farm_size) for n in nitrogen_range]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=rainfall_range, y=rainfall_yields,
                mode='lines+markers',
                name='Yield',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=8)
            ))
            fig1.add_vline(x=650, line_dash="dash", line_color="green", annotation_text="Optimal (650mm)")
            fig1.add_vline(x=yield_rainfall, line_dash="dash", line_color="red", annotation_text=f"Your value ({yield_rainfall}mm)")
            fig1.update_layout(
                title="Rainfall Effect on Yield",
                xaxis_title="Rainfall (mm)",
                yaxis_title="Yield (t/ha)",
                template="plotly_white",
                height=400,
                hovermode='x'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=temp_range, y=temp_yields,
                mode='lines+markers',
                name='Yield',
                line=dict(color='#A23B72', width=3),
                marker=dict(size=8)
            ))
            fig2.add_vline(x=22, line_dash="dash", line_color="green", annotation_text="Optimal (22°C)")
            fig2.add_vline(x=yield_temp, line_dash="dash", line_color="red", annotation_text=f"Your value ({yield_temp}°C)")
            fig2.update_layout(
                title="Temperature Effect on Yield",
                xaxis_title="Temperature (°C)",
                yaxis_title="Yield (t/ha)",
                template="plotly_white",
                height=400,
                hovermode='x'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=nitrogen_range, y=nitrogen_yields,
                mode='lines+markers',
                name='Yield',
                line=dict(color='#F18F01', width=3),
                marker=dict(size=8)
            ))
            fig3.add_vline(x=150, line_dash="dash", line_color="green", annotation_text="Optimal (150kg/ha)")
            fig3.add_vline(x=yield_nitrogen, line_dash="dash", line_color="red", annotation_text=f"Your value ({yield_nitrogen}kg/ha)")
            fig3.update_layout(
                title="Nitrogen Effect on Yield",
                xaxis_title="Nitrogen (kg/ha)",
                yaxis_title="Yield (t/ha)",
                template="plotly_white",
                height=400,
                hovermode='x'
            )
            st.plotly_chart(fig3, use_container_width=True)

# ============================================================================
# TAB 3: CREDIT SCORE
# ============================================================================
elif selected == "📊 Credit Score":
    st.markdown('<div class="section-title">Farmer Credit Score</div>', unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown('<div class="error-box"><strong>❌ Error:</strong> Model files not loaded.</div>', unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            region2 = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'], key='s2_region')
            coop2 = st.radio("Cooperative Member?", ["Yes", "No"], index=0, key='s2_coop')
            farm_size2 = st.number_input("Farm Size (ha)", 0.5, 20.0, 5.0, key='s2_size')
        
        with col2:
            crop2 = st.selectbox("Primary Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'], key='s2_crop')
            mobile2 = st.number_input("Mobile Money (TZS)", 0, value=500000, key='s2_mobile')
            subsidy2 = st.radio("Subsidy Status", ['Received', 'Pending', 'Not Received'], index=1, key='s2_subsidy')
        
        loan2 = st.number_input("Loan Amount (TZS)", 100000, value=2000000, key='s2_loan')
        
        if st.button("Score Farmer", use_container_width=True):
            data = {
                'region': region2,
                'coop_member': coop2,
                'farm_size_hectares': farm_size2,
                'primary_crop': crop2,
                'mobile_money_inflow': mobile2,
                'subsidy_status': subsidy2,
                'loan_amount_requested': loan2
            }
            
            result = score_farmer(data)
            if 'error' not in result:
                st.markdown('<div class="success-box"><strong>✓ Scored</strong></div>', unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="metric-card {'risk-low' if result['risk_category'] == 'LOW' else 'risk-medium' if result['risk_category'] == 'MEDIUM' else 'risk-high'}">
                        <div style="font-size: 0.9rem; opacity: 0.9;">PD %</div>
                        <div style="font-size: 2rem; font-weight: bold;">{result['pd_pct']:.1f}%</div>
                        <div style="font-size: 0.85rem;">Default Risk</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Risk Category</div>
                        <div style="font-size: 2rem; font-weight: bold;">{result['risk_category']}</div>
                        <div style="font-size: 0.85rem;">Classification</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Expected Loss</div>
                        <div style="font-size: 2rem; font-weight: bold;">{result['expected_loss']/1e6:.2f}M</div>
                        <div style="font-size: 0.85rem;">TZS</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with m4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size: 0.9rem; opacity: 0.9;">Loan Amount</div>
                        <div style="font-size: 2rem; font-weight: bold;">{loan2/1e6:.2f}M</div>
                        <div style="font-size: 0.85rem;">TZS</div>
                    </div>
                    """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: BATCH
# ============================================================================
elif selected == "📦 Batch":
    st.markdown('<div class="section-title">Batch Score From CSV</div>', unsafe_allow_html=True)
    
    if not model_loaded:
        st.markdown('<div class="error-box"><strong>❌ Error:</strong> Model files not loaded.</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box">
        <strong>Required CSV columns:</strong><br>
        region, coop_member (Yes/No), farm_size_hectares, primary_crop, mobile_money_inflow, subsidy_status (Received/Pending/Not Received), loan_amount_requested
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"Loaded {len(df)} farmers")
            
            required = MODEL_FEATURES
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                st.markdown(f'<div class="error-box"><strong>Missing columns:</strong> {missing}</div>', unsafe_allow_html=True)
            else:
                if st.button("Score All Farmers", use_container_width=True):
                    results = []
                    progress = st.progress(0)
                    
                    for idx, row in df.iterrows():
                        score = score_farmer(row.to_dict())
                        combined = {**row.to_dict(), **score}
                        results.append(combined)
                        progress.progress((idx + 1) / len(df))
                    
                    results_df = pd.DataFrame(results)
                    st.markdown('<div class="success-box"><strong>✓ Scored</strong> all farmers</div>', unsafe_allow_html=True)
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name="batch_scores.csv",
                        mime="text/csv"
                    )
                    
                    st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card risk-high">
                            <div style="font-size: 0.9rem;">Very High Risk</div>
                            <div style="font-size: 2rem; font-weight: bold;">{len(results_df[results_df['risk_category'] == 'VERY_HIGH'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card risk-high">
                            <div style="font-size: 0.9rem;">High Risk</div>
                            <div style="font-size: 2rem; font-weight: bold;">{len(results_df[results_df['risk_category'] == 'HIGH'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card risk-medium">
                            <div style="font-size: 0.9rem;">Medium Risk</div>
                            <div style="font-size: 2rem; font-weight: bold;">{len(results_df[results_df['risk_category'] == 'MEDIUM'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""
                        <div class="metric-card risk-low">
                            <div style="font-size: 0.9rem;">Low Risk</div>
                            <div style="font-size: 2rem; font-weight: bold;">{len(results_df[results_df['risk_category'] == 'LOW'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Interactive pie chart
                    risk_counts = results_df['risk_category'].value_counts()
                    fig = go.Figure(data=[go.Pie(
                        labels=risk_counts.index,
                        values=risk_counts.values,
                        marker=dict(colors=['#28a745', '#ffc107', '#fd7e14', '#dc3545'][:len(risk_counts)]),
                        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
                    )])
                    fig.update_layout(title="Risk Distribution", height=400)
                    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 5: ABOUT
# ============================================================================
elif selected == "ℹ️ About":
    st.markdown('<div class="section-title">About This Platform</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>🌾 Agri-Credit & Yield Prediction Platform</strong><br>
    Integrated loan decision support system combining credit risk assessment with crop yield prediction.
    </div>
    
    ### Features
    
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
    <strong>🔗 Integrated Analysis</strong><br>
    Combines credit risk + yield prediction for unified loan recommendation<br><br>
    <strong>🌾 Crop Yield Prediction</strong><br>
    Interactive analysis with sensitivity charts showing how each factor affects yield<br><br>
    <strong>📊 Credit Scoring</strong><br>
    Probability of default calculation based on your trained model<br><br>
    <strong>📦 Batch Processing</strong><br>
    Score multiple farmers from CSV with automated analysis<br><br>
    <strong>📈 Interactive Charts</strong><br>
    Plotly-powered visualizations for better insights
    </div>
    
    ### Models Used
    
    **Credit Risk Model:** Trained machine learning model predicting probability of default  
    **Yield Prediction Model:** Non-linear model capturing optimal conditions for crop productivity
    
    ---
    
    **Version:** 2.2 With Enhanced UI  
    **Status:** Production Ready  
    **Last Updated:** September 2024
    """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div class="footer">
    <p>Agri-Credit & Yield Prediction Platform | Integrated Loan Decision Support | © 2024</p>
</div>
""", unsafe_allow_html=True)