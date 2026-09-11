import streamlit as st
import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Agri-Credit & Yield Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# TITLE
# ============================================================================
st.markdown("# 🌾 Agri-Credit & Yield Prediction Platform")
st.markdown("""
**Integrated Loan Decision Support System**  
Combines credit risk assessment + crop yield prediction for better lending decisions
""")

# ============================================================================
# LOAD CREDIT MODEL
# ============================================================================
@st.cache_resource
def load_credit_model():
    """Load your trained agri-credit model"""
    try:
        with open('farmer_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('encoder.pkl', 'rb') as f:
            encoder = pickle.load(f)
        return model, encoder, True
    except FileNotFoundError as e:
        st.error(f"⚠️ Model files not found: {e}")
        return None, None, False

model, encoder, model_loaded = load_credit_model()

# ============================================================================
# YIELD MODEL (Embedded)
# ============================================================================
def predict_yield(rainfall, temperature, soil_ph, nitrogen, farm_size):
    """Predict crop yield based on farm conditions"""
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
# CREDIT MODEL SCORING
# ============================================================================
MODEL_FEATURES = [
    'region', 'coop_member', 'farm_size_hectares', 'primary_crop',
    'mobile_money_inflow', 'subsidy_status', 'loan_amount_requested'
]

def normalize_binary_fields(data):
    """Normalize binary fields"""
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
    """Score farmer using credit model"""
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
# TABS
# ============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔗 Integrated Analysis",
    "📊 Single Farmer Score",
    "📦 Batch Upload",
    "ℹ️ About"
])

# ============================================================================
# TAB 1: INTEGRATED ANALYSIS
# ============================================================================
with tab1:
    st.header("🔗 Integrated Farmer Assessment")
    
    st.info("""
    **How it works:**
    1. Enter farmer profile & credit details
    2. Enter farm conditions & environmental factors
    3. Get unified loan recommendation combining both factors
    """)
    
    if not model_loaded:
        st.error("❌ Credit model not loaded. Please place farmer_model.pkl and encoder.pkl in the same directory.")
    else:
        # TWO COLUMN LAYOUT
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👤 Farmer & Credit Profile")
            
            farmer_id = st.text_input("Farmer ID", value="FARMER_0001")
            region = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'])
            coop_member = st.radio("Cooperative Member?", ["Yes", "No"], index=0)
            farm_size = st.number_input("Farm Size (hectares)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
            primary_crop = st.selectbox("Primary Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'])
            mobile_money = st.number_input("Annual Mobile Money (TZS)", min_value=0, value=500000, step=50000)
            subsidy = st.radio("Subsidy Status", ['Received', 'Pending', 'Not Received'], index=1)
            loan_amount = st.number_input("Loan Amount Requested (TZS)", min_value=100000, value=2000000, step=100000)
        
        with col2:
            st.subheader("🌱 Farm Conditions")
            
            rainfall = st.slider("Rainfall (mm/season)", min_value=200, max_value=1500, value=650, step=50)
            temperature = st.slider("Avg Temperature (°C)", min_value=5, max_value=35, value=22, step=1)
            soil_ph = st.slider("Soil pH Level", min_value=4.5, max_value=8.5, value=6.5, step=0.1)
            nitrogen = st.slider("Nitrogen Applied (kg/ha)", min_value=20, max_value=250, value=120, step=10)
            
            # Info box with optimal conditions
            with st.expander("📖 Optimal Conditions Reference", expanded=False):
                st.markdown("""
                - **Rainfall:** ~650mm (too little = drought, too much = waterlogging)
                - **Temperature:** ~22°C (below 15°C or above 28°C = stress)
                - **Soil pH:** 6.5 (neutral - too acidic/alkaline reduces nutrients)
                - **Nitrogen:** ~150kg/ha (diminishing returns beyond this)
                """)
        
        # ANALYZE BUTTON
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
            
            # RUN MODELS
            credit_score = score_farmer(farmer_data)
            
            if 'error' not in credit_score:
                # CROP YIELD MODEL
                predicted_yield = predict_yield(rainfall, temperature, soil_ph, nitrogen, farm_size)
                annual_production = predicted_yield * farm_size
                farm_income = annual_production * 300 * 1000  # TZS at $300/ton
                
                # DEBT SERVICE CALCULATION
                dsr = 0.35
                max_loan = farm_income * dsr
                
                # RISK FACTORS
                pd_scr = credit_score['pd']
                pd_pct = credit_score['pd_pct']
                risk_cat = credit_score['risk_category']
                
                # COLLATERAL
                collateral_factors = {
                    'LOW': 1.2,
                    'MEDIUM': 1.5,
                    'HIGH': 2.0,
                    'VERY_HIGH': 2.5
                }
                collateral_factor = collateral_factors.get(risk_cat, 1.5)
                
                # RECOMMENDED LOAN
                recommended_loan = min(loan_amount, max_loan)
                collateral_req = recommended_loan * collateral_factor
                
                # INTEGRATED DECISION
                if pd_pct < 15 and recommended_loan >= loan_amount * 0.95:
                    decision = "✅ APPROVE"
                    decision_type = "approve"
                elif pd_pct < 30 and recommended_loan >= loan_amount * 0.80:
                    decision = "⚠️ CONDITIONAL APPROVAL"
                    decision_type = "conditional"
                else:
                    decision = "❌ REJECT / RESTRUCTURE"
                    decision_type = "reject"
                
                # DISPLAY RESULTS
                st.success("✓ Analysis Complete")
                
                # METRICS ROW 1
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Predicted Yield", f"{predicted_yield:.2f} t/ha")
                with m2:
                    st.metric("Annual Income", f"{farm_income/1e6:.2f}M TZS")
                with m3:
                    st.metric("Credit Risk (PD)", f"{pd_pct:.1f}%")
                with m4:
                    st.metric("Risk Category", risk_cat)
                
                # DECISION BOX
                st.markdown("---")
                
                if decision_type == "approve":
                    st.success(f"""
                    ### {decision}
                    
                    **Loan Approved:** {recommended_loan/1e6:.2f}M TZS (requested: {loan_amount/1e6:.2f}M)  
                    **Collateral Required:** {collateral_req/1e6:.2f}M TZS  
                    **Terms:** Standard 3-year loan with annual reviews
                    """)
                elif decision_type == "conditional":
                    st.warning(f"""
                    ### {decision}
                    
                    **Approved Loan:** {recommended_loan/1e6:.2f}M TZS (vs requested: {loan_amount/1e6:.2f}M)  
                    **Collateral Required:** {collateral_req/1e6:.2f}M TZS  
                    **Conditions:**
                    - Enhanced monitoring (quarterly reviews)
                    - Crop insurance required
                    - Cooperative membership recommended
                    """)
                else:
                    st.error(f"""
                    ### {decision}
                    
                    **Recommended Loan:** {recommended_loan/1e6:.2f}M TZS (vs requested: {loan_amount/1e6:.2f}M)  
                    **Collateral Required:** {collateral_req/1e6:.2f}M TZS  
                    **Options:**
                    - Reduce loan request to {recommended_loan/1e6:.2f}M TZS
                    - Increase collateral to {collateral_req/1e6:.2f}M TZS
                    - Improve farm conditions (irrigation, soil treatment)
                    """)
                
                # DECISION TABLE
                st.markdown("---")
                st.subheader("📋 Decision Summary")
                
                summary_data = {
                    'Metric': [
                        'Predicted Yield',
                        'Annual Production',
                        'Estimated Farm Income',
                        'Max Loan (from yield)',
                        'Requested Loan',
                        'Recommended Loan',
                        'Probability of Default',
                        'Risk Category',
                        'Collateral Required'
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
                
                # DOWNLOAD RESULTS
                results_csv = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results",
                    data=results_csv,
                    file_name=f"{farmer_id}_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"Error: {credit_score['error']}")

# ============================================================================
# TAB 2: SINGLE FARMER SCORE
# ============================================================================
with tab2:
    st.header("📊 Single Farmer Credit Score")
    st.markdown("*(Uses your trained credit risk model)*")
    
    if not model_loaded:
        st.error("❌ Model files not loaded")
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
                st.success("✓ Scored")
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("PD %", f"{result['pd_pct']:.1f}%")
                with m2:
                    st.metric("Risk Category", result['risk_category'])
                with m3:
                    st.metric("Expected Loss", f"{result['expected_loss']/1e6:.2f}M TZS")
                with m4:
                    st.metric("Loan Amount", f"{loan2/1e6:.2f}M TZS")
            else:
                st.error(f"Error: {result['error']}")

# ============================================================================
# TAB 3: BATCH UPLOAD
# ============================================================================
with tab3:
    st.header("📦 Batch Score From CSV")
    
    st.markdown("""
    **Required CSV columns:**
    - region
    - coop_member (Yes/No)
    - farm_size_hectares
    - primary_crop
    - mobile_money_inflow
    - subsidy_status (Received/Pending/Not Received)
    - loan_amount_requested
    """)
    
    if not model_loaded:
        st.error("❌ Model files not loaded")
    else:
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"Loaded {len(df)} farmers")
            
            required = MODEL_FEATURES
            missing = [c for c in required if c not in df.columns]
            
            if missing:
                st.error(f"Missing columns: {missing}")
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
                    st.success(f"✓ Scored {len(results_df)} farmers")
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # DOWNLOAD
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results",
                        data=csv,
                        file_name="batch_scores.csv",
                        mime="text/csv"
                    )
                    
                    # SUMMARY
                    st.subheader("Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Very High Risk", len(results_df[results_df['risk_category'] == 'VERY_HIGH']))
                    with col2:
                        st.metric("High Risk", len(results_df[results_df['risk_category'] == 'HIGH']))
                    with col3:
                        st.metric("Medium Risk", len(results_df[results_df['risk_category'] == 'MEDIUM']))
                    with col4:
                        st.metric("Low Risk", len(results_df[results_df['risk_category'] == 'LOW']))
                    
                    # CHART
                    fig, ax = plt.subplots(figsize=(10, 5))
                    risk_counts = results_df['risk_category'].value_counts()
                    colors = {'LOW': '#28a745', 'MEDIUM': '#ffc107', 'HIGH': '#fd7e14', 'VERY_HIGH': '#dc3545'}
                    color_list = [colors.get(x, '#999') for x in risk_counts.index]
                    risk_counts.plot(kind='bar', ax=ax, color=color_list)
                    ax.set_title('Risk Distribution', fontsize=14, fontweight='bold')
                    ax.set_xlabel('Risk Category')
                    ax.set_ylabel('Count')
                    plt.tight_layout()
                    st.pyplot(fig)

# ============================================================================
# TAB 4: ABOUT
# ============================================================================
with tab4:
    st.header("ℹ️ About This Platform")
    
    st.markdown("""
    ### Features
    
    **Tab 1: Integrated Analysis** 🔗
    - Combines credit risk + yield prediction
    - Single form for farmer profile + farm conditions
    - Unified loan recommendation
    - Decision summary with all metrics
    
    **Tab 2: Single Farmer Score** 📊
    - Credit risk assessment only
    - Probability of default calculation
    - Expected loss estimation
    
    **Tab 3: Batch Processing** 📦
    - Score multiple farmers from CSV
    - Download results
    - Risk distribution analysis
    
    ### Models
    
    **Credit Risk Model:**
    - Trained on agri-credit data
    - 7 features (region, co-op, farm size, crop, mobile money, subsidy, loan amount)
    - Predicts probability of default (0-100%)
    
    **Yield Prediction Model:**
    - Embedded non-linear model
    - 4 agronomic factors (rainfall, temp, pH, nitrogen)
    - Predicts tons/hectare
    - Calculates farm income
    
    ### Decision Logic
    
    | Condition | Decision |
    |-----------|----------|
    | PD < 15% & Loan ≤ Capacity | ✅ APPROVE |
    | PD < 30% & Loan ≤ 80% Capacity | ⚠️ CONDITIONAL |
    | Otherwise | ❌ REJECT |
    
    ### How to Use
    
    1. Gather farmer information + farm conditions
    2. Enter data in Tab 1 (or upload CSV in Tab 3)
    3. Click "Analyze" (or "Score All")
    4. Review recommendation
    5. Download results
    
    ---
    
    **Version:** 2.0 Integrated  
    **Status:** Production Ready  
    **Last Updated:** September 2024
    """)

st.markdown("---")
st.markdown("*Agri-Credit & Yield Prediction Platform | © 2026*")