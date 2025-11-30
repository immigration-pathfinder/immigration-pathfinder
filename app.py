"""
Immigration Pathfinder - Streamlit Web Application
Simple and beautiful UI for the multi-agent system
"""

import streamlit as st
import sys
import json
from pathlib import Path
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Imports
from agents.orchestrator import Orchestrator
from memory.session_service import SessionService


# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Immigration Pathfinder",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .country-card {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .score-excellent {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .score-good {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .score-fair {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'orchestrator' not in st.session_state:
    with st.spinner("🔧 Initializing AI agents..."):
        session_service = SessionService()
        st.session_state.orchestrator = Orchestrator(session_service)
        st.session_state.results = None
        st.session_state.processing = False


# ============================================
# HEADER
# ============================================
st.markdown('<div class="main-header">🌍 Immigration Pathfinder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Find Your Perfect Immigration Destination with AI</div>', unsafe_allow_html=True)

st.divider()


# ============================================
# SIDEBAR - USER INPUT
# ============================================
# ============================================
# SIDEBAR - USER INPUT
# ============================================
with st.sidebar:

    # 🔥 تست اینکه Gemini key درست لود شده
    st.write("Gemini key loaded:", bool(os.getenv("GEMINI_API_KEY")))

    st.header("📋 Your Profile")
    st.markdown("Fill in your information below:")

    # فرم برای جلوگیری از reload
    with st.form("user_profile_form"):

        # Age
        age = st.number_input(
            "Age",
            min_value=18,
            max_value=100,
            value=30,
            help="Your current age"
        )

        # Citizenship
        citizenship = st.text_input(
            "Citizenship",
            value="Iran",
            placeholder="e.g., Iran, India, Pakistan",
            help="Your current nationality"
        )

        # Marital Status
        marital_status = st.selectbox(
            "Marital Status",
            options=["single", "married", "divorced", "widowed"],
            help="Your marital status"
        )

        # Education
        st.subheader("🎓 Education")
        education_level = st.selectbox(
            "Education Level",
            options=["high school", "bachelor", "master", "phd"],
            index=1,
            help="Your highest level of education"
        )

        field_of_study = st.text_input(
            "Field of Study",
            value="Computer Engineering",
            placeholder="e.g., Computer Science, Business",
            help="Your field of study"
        )

        # Work Experience
        st.subheader("💼 Work Experience")
        work_experience = st.number_input(
            "Years of Experience",
            min_value=0,
            max_value=50,
            value=2,
            help="Total years of work experience"
        )

        # English
        st.subheader("🗣️ Language")
        english_level = st.selectbox(
            "English Level",
            options=["A1", "A2", "B1", "B2", "C1", "C2"],
            index=2,
            help="Your English proficiency level (CEFR)"
        )

        english_score = st.number_input(
            "IELTS Score (optional)",
            min_value=0.0,
            max_value=9.0,
            value=0.0,
            step=0.5,
            help="Your IELTS score (leave 0 if not taken)"
        )

        # Funds
        st.subheader("💰 Financial")
        funds = st.number_input(
            "Available Funds (USD)",
            min_value=0,
            max_value=1000000,
            value=10000,
            step=1000,
            help="Your available liquid funds in USD"
        )

        # Goal
        st.subheader("🎯 Immigration Goal")
        goal = st.selectbox(
            "Primary Goal",
            options=["Work", "Study", "Family", "Business"],
            help="Your main reason for immigration"
        )

        # Target Countries
        target_countries = st.multiselect(
            "Preferred Countries (optional)",
            options=["Canada", "USA", "Germany", "Netherlands", "Ireland",
                     "Sweden", "Australia", "New Zealand", "UK"],
            default=["Germany", "Netherlands"],
            help="Countries you're interested in"
        )

        st.divider()

        # Analyze Button
        analyze_btn = st.form_submit_button(
            "🚀 Analyze My Options",
            use_container_width=True,
            type="primary"
        )



# ============================================
# MAIN CONTENT
# ============================================

# Process if button clicked
if analyze_btn:
    st.session_state.processing = True
    
    # Build user profile
    user_profile = {
        "age": age,
        "citizenship": citizenship,
        "marital_status": marital_status,
        "education_level": education_level,
        "field_of_study": field_of_study,
        "work_experience_years": work_experience,
        "english_level": english_level,
        "english_score": english_score if english_score > 0 else None,
        "funds_usd": funds,
        "goal": goal,
        "target_countries": target_countries
    }
    
    # Process
    with st.spinner("🔍 Analyzing your profile and matching countries..."):
        start_time = time.time()
        
        try:
            result = st.session_state.orchestrator.process(
                user_profile,
                f"What are my best immigration options for {goal.lower()}?"
            )
            
            elapsed_time = time.time() - start_time
            st.session_state.results = result
            st.session_state.processing_time = elapsed_time
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.processing = False


# Display results
if st.session_state.results:
    result = st.session_state.results
    
    # Success message
    st.success(f"✅ Analysis complete in {st.session_state.processing_time:.2f} seconds!")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Recommendation", "📊 Rankings", "💡 Details", "📥 Export"])
    
    # Tab 1: Recommendation
    with tab1:
        st.header("🎯 Your Immigration Recommendation")
        
        if "explanation" in result:
            st.markdown(result["explanation"])
        
        # Recommended Country Highlight
        if "recommended_country" in result:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 15px; color: white;">
                    <h2>🏆 Top Recommendation</h2>
                    <h1 style="font-size: 3rem; margin: 1rem 0;">{result['recommended_country']}</h1>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 2: Rankings
    with tab2:
        st.header("📊 Country Rankings")
        
        if "ranking" in result and "acceptable" in result["ranking"]:
            acceptable = result["ranking"]["acceptable"]
            
            # Display top 5 as cards
            for idx, country_info in enumerate(acceptable[:5], 1):
                country = country_info["country"]
                score = country_info["score"]
                reason = country_info.get("reason", "")
                
                # Determine color
                if score >= 75:
                    card_class = "score-excellent"
                    emoji = "🟢"
                    status = "Excellent"
                elif score >= 65:
                    card_class = "score-good"
                    emoji = "🟡"
                    status = "Good"
                else:
                    card_class = "score-fair"
                    emoji = "🔵"
                    status = "Fair"
                
                st.markdown(f"""
                <div class="country-card {card_class}">
                    <h3>{emoji} #{idx} {country}</h3>
                    <h2>Score: {score:.1f}/100</h2>
                    <p><strong>Status:</strong> {status}</p>
                    <p>{reason}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Full ranking table
            st.subheader("📋 Complete Rankings")
            
            import pandas as pd
            df_data = []
            for idx, country_info in enumerate(acceptable, 1):
                df_data.append({
                    "Rank": idx,
                    "Country": country_info["country"],
                    "Score": f"{country_info['score']:.2f}",
                    "Status": "✅ Excellent" if country_info['score'] >= 75 else 
                             "⚠️ Good" if country_info['score'] >= 65 else "❌ Fair"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Tab 3: Details
    with tab3:
        st.header("💡 Detailed Analysis")
        
        # Profile Summary
        with st.expander("👤 Your Profile Summary", expanded=True):
            if "profile" in result:
                profile = result["profile"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Age", profile.get("age", "N/A"))
                    st.metric("Citizenship", profile.get("citizenship", "N/A"))
                    st.metric("Education", profile.get("education_level", "N/A"))
                    st.metric("Work Experience", f"{profile.get('work_experience_years', 0)} years")
                
                with col2:
                    st.metric("English Level", profile.get("english_level", "N/A"))
                    st.metric("IELTS Score", profile.get("english_score", "Not provided"))
                    st.metric("Available Funds", f"${profile.get('funds_usd', 0):,.0f}")
                    st.metric("Goal", profile.get("goal", "N/A"))
        
        # Match Results
        with st.expander("🔍 Country Match Results"):
            if "match_results" in result:
                for match in result["match_results"][:5]:
                    st.markdown(f"""
                    **{match['country']}** - {match['pathway']} Pathway
                    - Status: {match['status']}
                    - Match Score: {match['raw_score']*100:.0f}%
                    - Missing: {', '.join(match['rule_gaps']['missing_requirements']) if match['rule_gaps']['missing_requirements'] else 'None'}
                    """)
                    st.divider()
    
    # Tab 4: Export
    with tab4:
        st.header("📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON Export
            json_data = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name="immigration_results.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Text Export (Explanation only)
            if "explanation" in result:
                st.download_button(
                    label="📝 Download Text Report",
                    data=result["explanation"],
                    file_name="immigration_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.info("💡 Tip: Save these results for your records and immigration planning!")

# If no results yet
else:
    # Welcome message
    st.info("👈 Fill in your profile in the sidebar and click **Analyze My Options** to get started!")
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered
        Advanced multi-agent system analyzes your profile against 8+ countries
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Smart Matching
        Intelligent scoring system considers eligibility, costs, and opportunities
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 Personalized
        Get tailored recommendations based on your unique situation
        """)


# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌍 Immigration Pathfinder v1.0 | Built with ❤️ using Streamlit</p>
    <p><small>Disclaimer: This is an AI-powered tool. Always consult with a licensed immigration consultant for official advice.</small></p>
</div>
""", unsafe_allow_html=True)
