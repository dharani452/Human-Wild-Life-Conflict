import streamlit as st
import numpy as np
import pandas as pd
import joblib
import os

# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="Human-Wildlife Conflict Prediction",
    page_icon="🌿",
    layout="wide"
)

# =========================================
# DISTRICT CENSUS & GEOGRAPHIC LOOKUP DATA
# =========================================

DISTRICTS_DATA = {
    "ariyalur": {"Males": 346763, "Females": 348761, "Urban": 0, "Rural": 616539, "forest_area_sqkm": 392.32},
    "coimbatore": {"Males": 2176031, "Females": 2095825, "Urban": 0, "Rural": 1451653, "forest_area_sqkm": 1953.18},
    "cuddalore": {"Males": 1150908, "Females": 1134487, "Urban": 0, "Rural": 1531034, "forest_area_sqkm": 385.48},
    "dharmapuri": {"Males": 1473597, "Females": 1382703, "Urban": 0, "Rural": 2400354, "forest_area_sqkm": 1716.29},
    "dindigul": {"Males": 968137, "Females": 954877, "Urban": 0, "Rural": 1249762, "forest_area_sqkm": 1888.18},
    "erode": {"Males": 1309278, "Females": 1272222, "Urban": 0, "Rural": 1387537, "forest_area_sqkm": 2328.46},
    "karur": {"Males": 465538, "Females": 470148, "Urban": 0, "Rural": 624430, "forest_area_sqkm": 105.54},
    "madurai": {"Males": 1303363, "Females": 1274838, "Urban": 0, "Rural": 1134025, "forest_area_sqkm": 560.87},
    "nagapattinam": {"Males": 739074, "Females": 749765, "Urban": 0, "Rural": 1158557, "forest_area_sqkm": 98.57},
    "namakkal": {"Males": 759551, "Females": 733911, "Urban": 0, "Rural": 948230, "forest_area_sqkm": 590.24},
    "nilgiris": {"Males": 378351, "Females": 383790, "Urban": 0, "Rural": 307532, "forest_area_sqkm": 1706.89},
    "perambalur": {"Males": 246141, "Females": 247505, "Urban": 0, "Rural": 414426, "forest_area_sqkm": 143.01},
    "pudukkottai": {"Males": 724300, "Females": 735301, "Urban": 0, "Rural": 1211217, "forest_area_sqkm": 355.16},
    "ramanathapuram": {"Males": 583376, "Females": 604228, "Urban": 0, "Rural": 885210, "forest_area_sqkm": 242.34},
    "salem": {"Males": 1563633, "Females": 1452713, "Urban": 0, "Rural": 1626162, "forest_area_sqkm": 1490.52},
    "sivaganga": {"Males": 566947, "Females": 588409, "Urban": 0, "Rural": 829272, "forest_area_sqkm": 313.12},
    "thanjavur": {"Males": 1096638, "Females": 1119500, "Urban": 0, "Rural": 1467577, "forest_area_sqkm": 328.79},
    "theni": {"Males": 552986, "Females": 540964, "Urban": 0, "Rural": 502109, "forest_area_sqkm": 1217.11},
    "tirunelveli": {"Males": 1333939, "Females": 1390049, "Urban": 0, "Rural": 1415742, "forest_area_sqkm": 849.34},
    "tiruvannamalai": {"Males": 1095859, "Females": 1090266, "Urban": 0, "Rural": 1785364, "forest_area_sqkm": 1318.45},
    "vellore": {"Males": 1741083, "Females": 1736234, "Urban": 0, "Rural": 2169319, "forest_area_sqkm": 845.09},
    "virudhunagar": {"Males": 870376, "Females": 880925, "Urban": 0, "Rural": 973956, "forest_area_sqkm": 352.94}
}

# =========================================
# CUSTOM CSS DESIGN
# =========================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: linear-gradient(
        -45deg,
        #0b1622,
        #0f2b3e,
        #143e5c,
        #112f20,
        #0f2334
    );
    background-size: 400% 400%;
    animation: gradientAnimation 20s ease infinite;
    color: #f8f9fa !important;
}

@keyframes gradientAnimation {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Sidebar styling overrides */
section[data-testid="stSidebar"] {
    background: rgba(13, 27, 42, 0.9) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

section[data-testid="stSidebar"] * {
    color: #e0e1dd !important;
}

/* Glassmorphic Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 26px;
    backdrop-filter: blur(12px);
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.result-card {
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    color: white !important;
    font-weight: 700;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    margin-bottom: 15px;
}

.result-card.high {
    background: linear-gradient(135deg, #d00000, #ff4d4d);
}

.result-card.medium {
    background: linear-gradient(135deg, #f39c12, #f1c40f);
}

.result-card.low {
    background: linear-gradient(135deg, #27ae60, #2ecc71);
}

.result-card.animal {
    background: linear-gradient(135deg, #2980b9, #3498db);
}

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 12px;
}

/* Premium Button Styling */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #2ec4b6, #0f9f90) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(46, 196, 182, 0.4) !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(46, 196, 182, 0.6) !important;
}

/* Label styling */
h1, h2, h3, h4, h5, h6, p, label, span {
    color: #ffffff !important;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================
# LOAD MODELS & UTILS
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

@st.cache_resource
def load_ml_pipeline():
    risk_model = joblib.load(os.path.join(MODELS_DIR, "wildlife_model.pkl"))
    risk_scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    risk_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    
    animal_model = joblib.load(os.path.join(MODELS_DIR, "animal_model.pkl"))
    animal_scaler = joblib.load(os.path.join(MODELS_DIR, "animal_scaler.pkl"))
    animal_encoder = joblib.load(os.path.join(MODELS_DIR, "animal_encoder.pkl"))
    
    return risk_model, risk_scaler, risk_encoder, animal_model, animal_scaler, animal_encoder

try:
    risk_model, risk_scaler, risk_encoder, animal_model, animal_scaler, animal_encoder = load_ml_pipeline()
except Exception as e:
    st.error(f"Error loading models from {MODELS_DIR}: {e}")
    st.stop()

# =========================================
# HERO BANNER SECTION
# =========================================

hero_html = """
<div style="
    background-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 0.75),
        rgba(0, 0, 0, 0.45)
    ),
    url('https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=1600');
    background-size: cover;
    background-position: center 30%;
    border-radius: 20px;
    padding: 70px 40px;
    margin-bottom: 25px;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
">
    <h1 style="
        color: white !important;
        text-align: center;
        font-size: 52px;
        margin-bottom: 12px;
        font-weight: 800;
        letter-spacing: 1px;
        text-shadow: 0px 4px 10px rgba(0, 0, 0, 0.6);
    ">
        🌿 Human-Wildlife Conflict Prediction
    </h1>
    <p style="
        color: #e0e0e0 !important;
        text-align: center;
        font-size: 20px;
        max-width: 850px;
        margin: auto;
        line-height: 1.5;
        text-shadow: 0px 2px 6px rgba(0, 0, 0, 0.5);
    ">
        AI-Powered Environmental Risk Analysis and Wildlife Movement Prediction Dashboard for Tamil Nadu Districts.
    </p>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)

# =========================================
# SIDEBAR / PROJECT INFO
# =========================================

st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 15px;">
        <span style="font-size: 48px;">📌</span>
        <h3 style="margin-top: 5px; font-weight: 700;">Project Info</h3>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    This MCA machine learning system uses a Random Forest Classifier architecture to predict and map wildlife movements and conflicts.
    
    **Scope of System:**
    - 🛡️ **Conflict Risk Probability** (Low, Medium, High)
    - 🐾 **Target Wildlife Species Identification**
    - 📊 **Dynamic Environmental Parameter Scaling**
    
    **Frameworks & Tech:**
    - Python & Streamlit
    - Scikit-learn
    - Joblib & Pandas
    - Numpy & Custom CSS
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; font-size: 13px; opacity: 0.7;">
        Developed for MCA Machine Learning Project<br>
        © 2026 Tamil Nadu Environmental Risk Project
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================
# INPUT SECTIONS
# =========================================

col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📍 Geography & Demographics")
    
    # District selection
    selected_district = st.selectbox(
        "Select District of Tamil Nadu",
        options=sorted(list(DISTRICTS_DATA.keys())),
        format_func=lambda x: x.capitalize()
    )
    
    # Retrieve demographics
    demo = DISTRICTS_DATA[selected_district]
    
    # Display auto-filled parameters
    st.markdown("##### Automatically loaded census data:")
    st.info(
        f"👥 **Population**: {demo['Males'] + demo['Females']:,} | "
        f"👨 **Males**: {demo['Males']:,} | "
        f"👩 **Females**: {demo['Females']:,}\n\n"
        f"🌳 **Forest Area**: {demo['forest_area_sqkm']:,} sq. km"
    )
    
    # Dynamic agricultural & water options
    crop_production = st.number_input(
        "Crop Production (metric tons)",
        min_value=0.0,
        max_value=500000.0,
        value=20000.0,
        step=500.0
    )
    
    water_source_nearby = st.toggle(
        "Is there a water source nearby?",
        value=True
    )
    water_value = 1 if water_source_nearby else 0

with col_right:
    st.subheader("🌦 Environmental Parameters")
    
    rainfall = st.slider(
        "Rainfall (mm)",
        min_value=0.0,
        max_value=2500.0,
        value=600.0,
        step=10.0
    )
    
    humidity = st.slider(
        "Humidity (%)",
        min_value=0.0,
        max_value=100.0,
        value=70.0
    )
    
    precipitation = st.slider(
        "Precipitation Index",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.01
    )
    
    wind_speed = st.slider(
        "Wind Speed (km/h)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.5
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================
# PREDICTION LOGIC
# =========================================

st.markdown("<br>", unsafe_allow_html=True)
predict_clicked = st.button("🔍 Run Wildlife Conflict Risk Analysis")

if predict_clicked:
    # 1. Align features for Risk Prediction
    # Scaler expect order: ['Males', 'Females', 'Urban', 'Rural', 'forest_area_sqkm', 'water_source_nearby', 'crop_production', 'humidity', 'precipitation', 'wind_speed']
    risk_features = np.array([[
        demo["Males"],
        demo["Females"],
        demo["Urban"],
        demo["Rural"],
        demo["forest_area_sqkm"],
        water_value,
        crop_production,
        humidity,
        precipitation,
        wind_speed
    ]])
    
    try:
        risk_scaled = risk_scaler.transform(risk_features)
        risk_pred_encoded = risk_model.predict(risk_scaled)
        risk_result = risk_encoder.inverse_transform(risk_pred_encoded)[0]
    except Exception as e:
        st.error(f"Error during risk prediction: {e}")
        st.stop()
        
    # 2. Align features for Animal Prediction
    # Animal scaler expect order: ['forest_area_sqkm', 'rainfall_mm', 'humidity', 'precipitation', 'crop_production', 'wind_speed']
    animal_features = np.array([[
        demo["forest_area_sqkm"],
        rainfall,
        humidity,
        precipitation,
        crop_production,
        wind_speed
    ]])
    
    try:
        animal_scaled = animal_scaler.transform(animal_features)
        animal_pred_encoded = animal_model.predict(animal_scaled)
        animal_result = animal_encoder.inverse_transform(animal_pred_encoded)[0]
    except Exception as e:
        st.error(f"Error during animal type prediction: {e}")
        st.stop()

    # 3. High quality animal images lookup
    animal_images = {
        "Deer": "https://i.pinimg.com/736x/af/d2/df/afd2df1ccf6b168cdea05578d89c8f76.jpg",
        "Elephant": "https://i.pinimg.com/736x/8a/56/ff/8a56ff886bedd0367dfe34361fff91eb.jpg",
        "Leopard": "https://i.pinimg.com/736x/a9/1b/04/a91b040bc81a5ac2250ab4f6e3d661aa.jpg",
        "Monkey": "https://in.pinterest.com/pin/28147566419487002/",
        "Wild Boar": "https://i.pinimg.com/736x/fc/b1/d4/fcb1d47473f00718efb8323de31f993e.jpg"
    }
    
    animal_image_url = animal_images.get(
        animal_result,
        "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=800"
    )

    # =========================================
    # DISPLAY RESULTS
    # =========================================
    
    st.markdown("---")
    st.markdown(
        """
        <h3 style="text-align: center; font-weight: 700; margin-bottom: 25px;">
            📊 Predictive Analytics Output
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    col_res_left, col_res_right = st.columns([1, 1])
    
    with col_res_left:
        risk_class = risk_result.lower()
        st.markdown(
            f"""
            <div class="result-card {risk_class}">
                <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">
                    🛡️ Predicted Conflict Risk
                </div>
                <div style="font-size: 38px; margin-top: 10px; font-weight: 800;">
                    {risk_result}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Risk messages / advisories
        if risk_result == "High":
            st.error(
                "🚨 **Advisory**: Critical risk detected! Environmental and agricultural conditions highly favor human-wildlife encounters. Proactive patrolling and smart fencing activation are recommended."
            )
        elif risk_result == "Medium":
            st.warning(
                "⚠️ **Advisory**: Moderate risk detected. Regular monitoring of crop boundary areas is advised, especially during peak animal feeding hours."
            )
        else:
            st.success(
                "✅ **Advisory**: Low conflict risk detected. Standard conservation and agricultural monitoring practices are sufficient."
            )
            
        # Summary details card
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top: 15px;">
                <h5 style="margin-top: 0; font-weight: 700;">📊 Session Inputs Summary</h5>
                <p style="font-size: 14px; line-height: 1.6; margin-bottom: 0;">
                    • <b>District</b>: {selected_district.capitalize()}<br>
                    • <b>Rainfall</b>: {rainfall} mm<br>
                    • <b>Humidity</b>: {humidity}%<br>
                    • <b>Precipitation Index</b>: {precipitation}<br>
                    • <b>Wind Speed</b>: {wind_speed} km/h<br>
                    • <b>Crop Production</b>: {crop_production:,} tons<br>
                    • <b>Water Source Nearby</b>: {"Yes" if water_source_nearby else "No"}<br>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
            
    with col_res_right:
        st.markdown(
            f"""
            <div class="result-card animal">
                <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">
                    🐾 Predicted Target Species
                </div>
                <div style="font-size: 38px; margin-top: 10px; font-weight: 800;">
                    {animal_result}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.image(
            animal_image_url,
            caption=f"Primary Species: {animal_result} (Unsplash Dynamic Wildlife Library)",
            use_container_width=True
        )

# =========================================
# FOOTER
# =========================================

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; padding: 10px; opacity: 0.8; font-size: 15px;">
        <h4 style="margin: 0 0 5px 0; font-weight: 600;">🌿 Human-Wildlife Conflict Risk Prediction</h4>
        <p style="margin: 0; font-size: 14px; opacity: 0.7;">
            Leveraging Random Forest classifiers on regional meteorological & demographic data to safeguard local agriculture and biodiversity.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
