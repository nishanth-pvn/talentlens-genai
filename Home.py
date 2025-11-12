import streamlit as st

st.set_page_config(page_title="TalentLens AI", page_icon="🏠", layout="wide")

st.markdown("""
<style>
    .main { background-color: white; }
    .stApp { background-color: white !important; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] { width: 250px !important; }
    .card-icon { font-size: 48px; margin-bottom: 15px; text-align: center; }
    .card-title { font-size: 24px; font-weight: bold; color: #1f2937; margin-bottom: 8px; text-align: center; }
    .card-description { font-size: 15px; color: #4b5563; line-height: 1.6; margin-bottom: 20px; text-align: center; min-height: 60px; }
    .ai-badge { display: inline-block; background: linear-gradient(135deg, #00E47C 0%, #08312A 100%); color: white; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: bold; margin-bottom: 10px; }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #00E47C 0%, #08312A 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(0, 228, 124, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.text(" ")
    st.image("BI-Logo.png", width=125)

st.markdown('<h1 style="text-align: center; font-size: 33px; font-weight: 600; color: #1f2937;">TalentLens AI - Recruitment Assistant</h1>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div style="text-align: center;"><span class="ai-badge">AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-icon">🔍</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Resume Screener</div>', unsafe_allow_html=True)
    st.text(' ')
    st.markdown('<div class="card-description">Analyze and evaluate candidates on technical fit and 5 BI Behaviors</div>', unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([0.5, 2, 0.5])
    with btn_col2:
        if st.button("Screen Candidates", key="resume_btn"):
            st.switch_page("pages/1_Resume_Screener.py")

with col2:
    st.markdown('<div style="text-align: center;"><span class="ai-badge">AI</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-icon">💼</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Interview Prep</div>', unsafe_allow_html=True)
    st.text(' ')
    st.markdown('<div class="card-description">Generate customized interview questions and case studies for shortlisted candidates</div>', unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([0.5, 2, 0.5])
    with btn_col2:
        if st.button("Prepare Interviews", key="interview_btn"):
            st.switch_page("pages/2_Interview_Prep.py")

with col3:
    st.markdown('<div style="text-align: center;"><span class="ai-badge">ANALYTICS</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-icon">🎯</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Behavioral Assessment</div>', unsafe_allow_html=True)
    st.text(' ')
    st.markdown('<div class="card-description">Compare candidates across 5 BI behavioral competencies with visual insights</div>', unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([0.5, 2, 0.5])
    with btn_col2:
        if st.button("View Analytics", key="behavioral_btn"):
            st.switch_page("pages/3_Behavioral_Assessment.py")
