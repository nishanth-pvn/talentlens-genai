import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.apollo_api import ApolloAPIClient
from utils.resume_parser import extract_text_from_file, clean_resume_text

st.set_page_config(page_title="Resume Screener", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .main { background-color: white; }
    .stApp { background-color: white !important; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    .section-header { font-size: 22px; font-weight: bold; color: #08312A; margin: 30px 0 15px 0; padding: 10px 0; border-bottom: 3px solid #00E47C; }
    .status-box { padding: 15px; border-radius: 8px; margin: 15px 0; font-size: 14px; }
    .status-success { background-color: #d4edda; border-left: 4px solid #28a745; color: #155724; }
    .status-info { background-color: #d1ecf1; border-left: 4px solid #17a2b8; color: #0c5460; }
    .stButton > button {
        background: linear-gradient(135deg, #00E47C 0%, #08312A 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

if 'stage' not in st.session_state:
    st.session_state.stage = 1
if 'job_desc' not in st.session_state:
    st.session_state.job_desc = ""
if 'resume_files' not in st.session_state:
    st.session_state.resume_files = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

def main():
    with st.sidebar:
        st.text(' ')
        st.image("BI-Logo.png", width=125)
        st.text(' ')
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")
        st.markdown("---")
        st.markdown(f"""
        {'✅' if st.session_state.stage > 1 else '📝'} **Stage 1:** Upload  
        {'✅' if st.session_state.stage > 2 else '⏳'} **Stage 2:** AI Analysis  
        {'✅' if st.session_state.stage > 3 else '📊'} **Stage 3:** Results
        """)
    
    st.markdown("<h6 style='text-align: center;'>Resume Screener</h6>", unsafe_allow_html=True)
    st.text(' ')
    
    # STAGE 1: Upload
    st.markdown('<div class="section-header">📄 Stage 1: Upload Files</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**📋 Job Description**")
        uploaded_jd = st.file_uploader("Upload Job Description", type=['pdf', 'txt'], key="jd")
        if uploaded_jd:
            jd_bytes = uploaded_jd.read()
            jd_text = extract_text_from_file(jd_bytes, uploaded_jd.name)
            if jd_text:
                st.session_state.job_desc = clean_resume_text(jd_text)
                st.success(f"✅ {uploaded_jd.name}")
    
    with col2:
        st.markdown("**📁 Candidate Resumes**")
        uploaded_resumes = st.file_uploader("Upload Resumes", type=['pdf', 'txt'], accept_multiple_files=True, key="resumes")
        if uploaded_resumes:
            st.session_state.resume_files = {}
            for resume in uploaded_resumes:
                resume_bytes = resume.read()
                resume_text = extract_text_from_file(resume_bytes, resume.name)
                if resume_text:
                    st.session_state.resume_files[resume.name] = clean_resume_text(resume_text)
            if st.session_state.resume_files:
                st.success(f"✅ {len(st.session_state.resume_files)} resumes")
    
    if st.session_state.job_desc and st.session_state.resume_files:
        st.markdown(f'<div class="status-box status-success">✅ Ready | Resumes: {len(st.session_state.resume_files)}</div>', unsafe_allow_html=True)
        col_btn1, btn_col2, col_btn3 = st.columns([2, 1, 2])
        with btn_col2:
            if st.button("🔍 Analyze", use_container_width=True, type="primary"):
                st.session_state.stage = 2
                st.rerun()
    else:
        st.markdown('<div class="status-box status-info">ℹ️ Upload job description and resumes</div>', unsafe_allow_html=True)
    
    # STAGE 2: AI Analysis with parallel processing
    if st.session_state.stage >= 2 and not st.session_state.analysis_complete:
        st.markdown("---")
        st.markdown('<div class="section-header">🤖 Stage 2: AI Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-box status-info">🔄 Analyzing...</div>', unsafe_allow_html=True)
        
        api_client = ApolloAPIClient()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text(f"Processing {len(st.session_state.resume_files)} resumes, Please wait...")
        
        # Parallel analysis in batches of 2
        results = api_client.analyze_resumes_parallel(
            st.session_state.resume_files,
            st.session_state.job_desc,
            batch_size=2
        )
        
        progress_bar.progress(1.0)
        st.session_state.analysis_results = results
        st.session_state.analysis_complete = True
        st.session_state.stage = 3
        status_text.text("✅ Complete!")
        st.success("Analysis done!")
        st.rerun()
    
    # STAGE 3: Results
    if st.session_state.stage >= 3 and st.session_state.analysis_complete:
        st.markdown("---")
        st.markdown('<div class="section-header">✏️ Stage 3: Results</div>', unsafe_allow_html=True)
        
        results = st.session_state.analysis_results
        
        display_data = []
        for r in results:
            if 'error' not in r:
                behaviors = r.get('behavioral_scores', {})
                behavior_scores = [
                    behaviors.get('communicate_with_candor', {}).get('score', 0),
                    behaviors.get('decide_and_act_with_speed', {}).get('score', 0),
                    behaviors.get('innovate_and_drive_change', {}).get('score', 0),
                    behaviors.get('deliver_to_win', {}).get('score', 0),
                    behaviors.get('collaborate_with_a_purpose', {}).get('score', 0)
                ]
                avg_behavior = sum(behavior_scores) / len(behavior_scores) if behavior_scores else 0
                
                display_data.append({
                    'Candidate': r.get('candidate_name'),
                    'Experience': f"{r.get('years_experience', 0)} yrs",
                    'Tech Fit': r.get('technical_fit_score', 0),
                    'Communicate': behaviors.get('communicate_with_candor', {}).get('score', 0),
                    'Speed': behaviors.get('decide_and_act_with_speed', {}).get('score', 0),
                    'Innovate': behaviors.get('innovate_and_drive_change', {}).get('score', 0),
                    'Deliver': behaviors.get('deliver_to_win', {}).get('score', 0),
                    'Collaborate': behaviors.get('collaborate_with_a_purpose', {}).get('score', 0),
                    'Behavior Avg': round(avg_behavior),
                    'Recommendation': r.get('overall_recommendation'),
                    'File': r['resume_filename']
                })
        
        df = pd.DataFrame(display_data)
        
        col1, col2, col3, col4 = st.columns(4)
        shortlisted = df[df['Recommendation'] == 'SHORTLIST']
        maybe = df[df['Recommendation'] == 'MAYBE']
        rejected = df[df['Recommendation'] == 'REJECT']
        
        with col1:
            st.metric("Total", len(df))
        with col2:
            st.metric("SHORTLIST", len(shortlisted))
        with col3:
            st.metric("MAYBE", len(maybe))
        with col4:
            st.metric("REJECT", len(rejected))
        
        st.markdown("---")
        
        st.dataframe(
            df.style.apply(lambda x: ['background-color: #d4edda' if v == 'SHORTLIST' 
                                     else 'background-color: #fff3cd' if v == 'MAYBE'
                                     else 'background-color: #f8d7da' if v == 'REJECT'
                                     else '' for v in x], subset=['Recommendation']),
            height=300,
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("### 📋 Detailed Analysis")
        
        selected = st.selectbox("Select candidate:", [r.get('candidate_name') for r in results if 'error' not in r])
        
        if selected:
            candidate = next((r for r in results if r.get('candidate_name') == selected), None)
            
            if candidate:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Name:** {candidate.get('candidate_name')}")
                    st.markdown(f"**Email:** {candidate.get('email', 'N/A')}")
                    st.markdown(f"**Phone:** {candidate.get('phone', 'N/A')}")
                    st.markdown(f"**Experience:** {candidate.get('years_experience', 0)} years")
                    st.markdown(f"**Technical Fit:** {candidate.get('technical_fit_score')}/100")
                    st.markdown(f"**Recommendation:** **{candidate.get('overall_recommendation')}**")
                
                with col2:
                    st.markdown("**Behavioral Scores:**")
                    behaviors = candidate.get('behavioral_scores', {})
                    for key, label in [
                        ('communicate_with_candor', '💬 Communicate with Candor'),
                        ('decide_and_act_with_speed', '⚡ Decide & Act with Speed'),
                        ('innovate_and_drive_change', '💡 Innovate & Drive Change'),
                        ('deliver_to_win', '🏆 Deliver to Win'),
                        ('collaborate_with_a_purpose', '🤝 Collaborate with Purpose')
                    ]:
                        score = behaviors.get(key, {}).get('score', 0)
                        st.markdown(f"{label}: **{score}/5**")
                
                st.markdown("---")
                st.markdown("**📝 Technical Justification:**")
                st.info(candidate.get('technical_fit_justification'))
                
                st.markdown("**🎯 Recommendation Justification:**")
                st.info(candidate.get('recommendation_justification'))
                
                with st.expander("Behavioral Justifications"):
                    for key, label in [
                        ('communicate_with_candor', 'Communicate with Candor'),
                        ('decide_and_act_with_speed', 'Decide & Act with Speed'),
                        ('innovate_and_drive_change', 'Innovate & Drive Change'),
                        ('deliver_to_win', 'Deliver to Win'),
                        ('collaborate_with_a_purpose', 'Collaborate with Purpose')
                    ]:
                        just = behaviors.get(key, {}).get('justification', 'N/A')
                        st.markdown(f"**{label}:** {just}")
                
                with st.expander("Strengths & Concerns"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**✅ Strengths:**")
                        for s in candidate.get('key_strengths', []):
                            st.markdown(f"- {s}")
                    with col_b:
                        st.markdown("**⚠️ Concerns:**")
                        for c in candidate.get('key_concerns', []):
                            st.markdown(f"- {c}")
        
        st.markdown("---")
        
        if st.button("📥 Download Excel", use_container_width=True):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            st.download_button("📥 Download", output, "Analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
