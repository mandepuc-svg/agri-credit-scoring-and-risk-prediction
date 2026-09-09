import streamlit as st
import pandas as pd
import pickle
import numpy as np

# Set page config
st.set_page_config(page_title="Farmer Credit Risk Scorer", layout="wide")

# Title
st.title("🌾 Farmer Credit Risk Scoring System")

# Load model and encoder
@st.cache_resource
def load_model():
    with open('farmer_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('encoder.pkl', 'rb') as f:
        encoder = pickle.load(f)
    return model, encoder

model, encoder = load_model()

MODEL_FEATURES = [
    'region',
    'coop_member',
    'farm_size_hectares',
    'primary_crop',
    'mobile_money_inflow',
    'subsidy_status',
    'loan_amount_requested'
]

# Convert human-readable binary values to the numeric values used during training.
def normalize_binary_fields(farmer_data_dict):
    normalized = dict(farmer_data_dict)

    coop_value = str(normalized.get('coop_member', '')).strip().lower()
    coop_mapping = {'yes': 1, 'no': 0, 'true': 1, 'false': 0, '1': 1, '0': 0}
    if coop_value not in coop_mapping:
        raise ValueError("coop_member must be Yes or No")
    normalized['coop_member'] = coop_mapping[coop_value]

    subsidy_value = str(normalized.get('subsidy_status', '')).strip().lower()
    subsidy_mapping = {
        'received': 1,
        'pending': 1,
        'not received': 0,
        'not_received': 0,
        'not recieved': 0,
        '0': 0,
        '1': 1
    }
    if subsidy_value not in subsidy_mapping:
        raise ValueError("subsidy_status must be Pending, Received, or Not received")
    normalized['subsidy_status'] = subsidy_mapping[subsidy_value]

    return normalized

# Scoring function
def score_farmer(farmer_data_dict, model=model, encoder=encoder):
    try:
        normalized_data = normalize_binary_fields(farmer_data_dict)
        temp_df = pd.DataFrame([normalized_data]).reindex(columns=MODEL_FEATURES)
        temp_encoded = encoder.transform(temp_df)
        
        pd_score = model.predict_proba(temp_encoded)[0, 1]
        
        lgd = 0.45
        ead = normalized_data['loan_amount_requested']
        el = pd_score * lgd * ead
        
        pd_pct = pd_score * 100
        if pd_pct > 70:
            risk_cat = 'VERY_HIGH'
        elif pd_pct > 50:
            risk_cat = 'HIGH'
        elif pd_pct > 30:
            risk_cat = 'MEDIUM'
        else:
            risk_cat = 'LOW'
        
        if risk_cat in ['HIGH', 'VERY_HIGH']:
            recommendation = '⛔ REJECT or require additional collateral'
        elif risk_cat == 'MEDIUM':
            recommendation = '⚠️ APPROVE with enhanced monitoring'
        else:
            recommendation = '✅ APPROVE - Low risk'
        
        return {
            'probability_of_default': round(pd_score, 4),
            'pd_percentage': round(pd_pct, 1),
            'expected_loss_tzs': round(el, 0),
            'risk_category': risk_cat,
            'recommendation': recommendation
        }
    except Exception as e:
        return {'error': str(e)}

# Create tabs
tab1, tab2 = st.tabs(["Score Single Farmer", "Batch Upload CSV"])

# ===== TAB 1: Single Farmer =====
with tab1:
    st.header("Score One Farmer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox("Region", ['Dodoma', 'Arusha', 'Mbeya', 'Morogoro', 'Mwanza'])
        coop_member = st.radio("Cooperative Member?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
        farm_size = st.number_input("Farm Size (hectares)", min_value=0.5, max_value=20.0, value=5.0)
        
    with col2:
        crop = st.selectbox("Primary Crop", ['Maize', 'Cashew', 'Coffee', 'Rice'])
        mobile_money = st.number_input("Annual Mobile Money Inflow (TZS)", min_value=0, value=500000)
        subsidy = st.radio("Subsidy Status", ['received', 'pending', 'not received'])
    
    loan_amount = st.number_input("Loan Amount Requested (TZS)", min_value=200000, value=2000000)
    
    # Score button
    if st.button("Score Farmer", key="single_score"):
        farmer_data = {
            'region': region,
            'coop_member': coop_member,
            'farm_size_hectares': farm_size,
            'primary_crop': crop,
            'mobile_money_inflow': mobile_money,
            'subsidy_status': subsidy,
            'loan_amount_requested': loan_amount
        }
        
        result = score_farmer(farmer_data)
        
        if 'error' not in result:
            st.success("✓ Farmer Scored")
            
            # Display results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Risk Category", result['risk_category'])
            with col2:
                st.metric("Default Probability", f"{result['pd_percentage']:.1f}%")
            with col3:
                st.metric("Expected Loss", f"{result['expected_loss_tzs']:,.0f} TZS")
            with col4:
                st.metric("Loan Amount", f"{loan_amount:,.0f} TZS")
            
            st.info(f"**Recommendation:** {result['recommendation']}")
        else:
            st.error(f"Error: {result['error']}")

# ===== TAB 2: Batch Upload =====
with tab2:
    st.header("Batch Score From CSV")
    
    st.write("Upload a CSV with columns: region, coop_member, farm_size_hectares, primary_crop, mobile_money_inflow, subsidy_status, loan_amount_requested")
    
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_columns = MODEL_FEATURES
        missing_columns = [column for column in required_columns if column not in df.columns]

        if missing_columns:
            st.error(
                "The uploaded CSV is missing required columns: "
                + ", ".join(missing_columns)
            )
            st.stop()

        # Keep only the features expected by the trained encoder. Extra columns
        # such as farmer_id and default_flag are allowed but not sent to the model.
        df = df[required_columns]
        st.write(f"Loaded {len(df)} farmers")
        
        if st.button("Score All Farmers", key="batch_score"):
            results = []
            
            with st.spinner("Scoring farmers..."):
                for idx, row in df.iterrows():
                    farmer_data = row.to_dict()
                    score = score_farmer(farmer_data)
                    
                    # Combine input + output
                    combined = {**row.to_dict(), **score}
                    results.append(combined)
            
            results_df = pd.DataFrame(results)
            st.success(f"✓ Scored {len(results_df)} farmers")
            
            # Display table
            st.dataframe(results_df, use_container_width=True)

            if 'risk_category' not in results_df.columns:
                error_details = results_df.get('error', pd.Series(dtype=str)).dropna().unique()
                st.error(
                    "No farmers could be scored. "
                    + (f"Details: {error_details[0]}" if len(error_details) else "Check the input values.")
                )
                st.stop()
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="farmer_scores.csv",
                mime="text/csv"
            )
            
            # Summary stats
            st.subheader("Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                very_high = len(results_df[results_df['risk_category'] == 'VERY_HIGH'])
                st.metric("Very High Risk", very_high)
            with col2:
                high = len(results_df[results_df['risk_category'] == 'HIGH'])
                st.metric("High Risk", high)
            with col3:
                medium = len(results_df[results_df['risk_category'] == 'MEDIUM'])
                st.metric("Medium Risk", medium)
            with col4:
                low = len(results_df[results_df['risk_category'] == 'LOW'])
                st.metric("Low Risk", low)
            
            total_loss = results_df['expected_loss_tzs'].sum()
            st.metric("Total Portfolio Expected Loss", f"{total_loss:,.0f} TZS")