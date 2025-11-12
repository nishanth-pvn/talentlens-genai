import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Behavioral Assessment", page_icon="🎯", layout="wide")

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
    
    st.markdown("<h6 style='text-align: center;'>Behavioral Assessment</h6>", unsafe_allow_html=True)
    st.text(' ')
    
    if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
        st.warning("⚠️ Run Resume Screener first.")
        if st.button("Go to Resume Screener"):
            st.switch_page("pages/1_Resume_Screener.py")
        return
    
    results = [r for r in st.session_state.analysis_results if 'error' not in r]
    
    if not results:
        st.error("No valid results.")
        return
    
    st.markdown('<div class="section-header">📊 Behavioral Analysis</div>', unsafe_allow_html=True)
    
    behavior_labels = {
        'communicate_with_candor': 'Communicate with Candor',
        'decide_and_act_with_speed': 'Decide & Act with Speed',
        'innovate_and_drive_change': 'Innovate & Drive Change',
        'deliver_to_win': 'Deliver to Win',
        'collaborate_with_a_purpose': 'Collaborate with Purpose'
    }
    
    # Radar Chart
    st.markdown("### 🎯 Top Candidates - Behavioral Radar Chart")
    
    shortlisted = [r for r in results if r.get('overall_recommendation') == 'SHORTLIST'][:5]
    
    if shortlisted:
        fig = go.Figure()
        
        for candidate in shortlisted:
            behaviors = candidate.get('behavioral_scores', {})
            scores = [behaviors.get(key, {}).get('score', 0) for key in behavior_labels.keys()]
            
            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=list(behavior_labels.values()),
                fill='toself',
                name=candidate.get('candidate_name', 'Unknown')
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No shortlisted candidates for radar chart.")
    
    st.markdown("---")
    
    # Heatmap
    st.markdown("### 🔥 All Candidates - Behavioral Heatmap")
    
    heatmap_data = []
    candidate_names = []
    
    for r in results:
        candidate_names.append(r.get('candidate_name', 'Unknown'))
        behaviors = r.get('behavioral_scores', {})
        row = [behaviors.get(key, {}).get('score', 0) for key in behavior_labels.keys()]
        heatmap_data.append(row)
    
    if heatmap_data:
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=list(behavior_labels.values()),
            y=candidate_names,
            colorscale='RdYlGn',
            text=heatmap_data,
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Score (1-5)")
        ))
        
        fig.update_layout(
            height=max(400, len(candidate_names) * 40),
            xaxis_title="Behavioral Competencies",
            yaxis_title="Candidates"
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
