import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.apollo_api import ApolloAPIClient

st.set_page_config(page_title="Interview Prep", page_icon="💼", layout="wide")

st.markdown("""
<style>
    .main { background-color: white; }
    [data-testid="collapsedControl"] { display: none; }
    [data-testid="stSidebarNav"] { display: none; }
    .section-header { font-size: 22px; font-weight: bold; color: #08312A; margin: 30px 0 15px 0; border-bottom: 3px solid #00E47C; }
    .stButton > button {
        background: linear-gradient(135deg, #00E47C 0%, #08312A 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = None

def main():
    with st.sidebar:
        st.text(' ')
        st.image("BI-Logo.png", width=125)
        st.text(' ')
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")
        st.markdown("---")
        if st.button("🔍 Resume Screener", use_container_width=True):
            st.switch_page("pages/1_Resume_Screener.py")
    
    st.markdown("<h6 style='text-align: center;'>Interview Prep</h6>", unsafe_allow_html=True)
    st.text(' ')
    
    if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
        st.warning("⚠️ Run Resume Screener first.")
        if st.button("Go to Resume Screener"):
            st.switch_page("pages/1_Resume_Screener.py")
        return
    
    st.markdown('<div class="section-header">💼 Generate Questions</div>', unsafe_allow_html=True)
    
    shortlisted = [r for r in st.session_state.analysis_results 
                   if r.get('overall_recommendation') == 'SHORTLIST' and 'error' not in r]
    
    if not shortlisted:
        shortlisted = [r for r in st.session_state.analysis_results if 'error' not in r]
    
    candidate_names = [r.get('candidate_name') for r in shortlisted]
    selected_candidate = st.selectbox("Select candidate:", candidate_names)
    
    if st.button("🤖 Generate Questions", type="primary"):
        candidate_data = next((r for r in shortlisted if r.get('candidate_name') == selected_candidate), None)
        
        if candidate_data:
            with st.spinner("Generating..."):
                api_client = ApolloAPIClient()
                questions = api_client.generate_interview_questions(
                    candidate_data, 
                    st.session_state.get('job_desc', 'Senior Data Engineer')
                )
                
                if questions:
                    st.session_state.interview_questions = questions
                    st.session_state.selected_candidate = selected_candidate
                    st.success("✅ Generated!")
                    st.rerun()
                else:
                    st.error("Failed. Retry.")
    
    if st.session_state.interview_questions and st.session_state.get('selected_candidate') == selected_candidate:
        questions = st.session_state.interview_questions
        
        st.markdown("---")
        st.markdown(f"### 📋 Interview Guide: {selected_candidate}")
        
        st.markdown('<div class="section-header">🔧 Technical Questions</div>', unsafe_allow_html=True)
        
        for idx, q in enumerate(questions.get('technical_questions', []), 1):
            with st.expander(f"Q{idx}: {q.get('question', 'N/A')[:60]}..."):
                st.markdown(f"**Question:** {q.get('question')}")
                st.markdown(f"**Why:** {q.get('why_ask')}")
                st.markdown(f"**Good Answer:** {q.get('good_answer')}")
        
        st.markdown('<div class="section-header">🎯 Behavioral Questions</div>', unsafe_allow_html=True)
        
        for idx, q in enumerate(questions.get('behavioral_questions', []), 1):
            with st.expander(f"Q{idx}: {q.get('behavior', 'N/A')}"):
                st.markdown(f"**Behavior:** {q.get('behavior')}")
                st.markdown(f"**Question:** {q.get('question')}")
                st.markdown(f"**Why:** {q.get('why_ask')}")
                st.markdown(f"**Good Answer:** {q.get('good_answer')}")
        
        st.markdown('<div class="section-header">📝 Case Study</div>', unsafe_allow_html=True)
        
        case = questions.get('case_study', {})
        st.info(case.get('scenario', 'N/A'))
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Assess:**")
            for item in case.get('what_to_assess', []):
                st.markdown(f"- {item}")
        with col2:
            st.markdown("**Criteria:**")
            for item in case.get('evaluation_criteria', []):
                st.markdown(f"- {item}")
        
        st.markdown("---")
        
        if st.button("📥 Download Guide"):
            content = f"""INTERVIEW GUIDE
Candidate: {selected_candidate}

TECHNICAL QUESTIONS
"""
            for idx, q in enumerate(questions.get('technical_questions', []), 1):
                content += f"\n{idx}. {q.get('question')}\n   Why: {q.get('why_ask')}\n"
            
            content += "\nBEHAVIORAL QUESTIONS\n"
            for idx, q in enumerate(questions.get('behavioral_questions', []), 1):
                content += f"\n{idx}. {q.get('behavior')}\n   Q: {q.get('question')}\n"
            
            content += f"\nCASE STUDY\n{case.get('scenario')}\n"
            
            st.download_button("📥 Download", content, f"Interview_{selected_candidate.replace(' ', '_')}.txt", "text/plain")

if __name__ == "__main__":
    main()
