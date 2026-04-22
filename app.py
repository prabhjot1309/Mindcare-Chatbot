import streamlit as st
import os
from datetime import datetime
from typing import Dict, List
import time

# Local utils
from utils import (
    analyze_sentiment, detect_crisis_keywords, calculate_risk_score,
    generate_counseling_response, get_crisis_resources
)

# LLM Setup
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    st.error("❌ Install dependencies: `pip install -r requirements.txt`")

# Page config
st.set_page_config(
    page_title="🧠 MindWell AI - Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { 
        font-size: 3.2rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 10px;
    }
    .crisis-alert {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24) !important;
        animation: pulse 2s infinite;
        border: 3px solid #dc3545;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(220,53,69,0.7); }
        70% { box-shadow: 0 0 0 20px rgba(220,53,69,0); }
        100% { box-shadow: 0 0 0 0 rgba(220,53,69,0); }
    }
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        border: 2px solid #e9ecef !important;
        padding: 12px 20px !important;
    }
    .stButton > button {
        border-radius: 25px !important;
        height: 50px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize LLM
@st.cache_resource
def init_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    
    try:
        llm = ChatGroq(
            api_key=api_key,
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=400
        )
        
        prompt = ChatPromptTemplate.from_template("""
        You are MindWell AI, a compassionate mental health assistant with 10+ years counseling experience.
        
        CORE PRINCIPLES:
        1. VALIDATE feelings: "I hear you", "That sounds really tough"
        2. EMPATHY first: Acknowledge emotions before advice
        3. CBT techniques: Challenge negative thoughts gently
        4. NEVER diagnose or prescribe
        5. CRISIS DETECTION: If suicide/self-harm mentioned → EMERGENCY RESOURCES
        6. Always end positively with actionable steps
        
        User said: {input}
        
        Respond warmly and professionally (200-300 words):
        """)
        
        return prompt | llm | StrOutputParser()
    except:
        return None

# Sidebar - Crisis Resources
with st.sidebar:
    st.header("📞 **Emergency Help**")
    st.markdown("""
    **🌍 Global Crisis Lines:**
    - **USA**: 988 (Suicide & Crisis Lifeline)
    - **UK**: 116 123 (Samaritans)
    - **Australia**: 13 11 14 (Lifeline)
    - **Canada**: 1-833-456-4566
    - **India**: 9152987821 (iCall)
    
    **💙 This AI is NOT a crisis service**
    """)
    
    st.markdown("---")
    st.caption("*Always seek professional help when needed*")

# Main Header
st.markdown('<h1 class="main-header">🧠 MindWell AI</h1>', unsafe_allow_html=True)
st.markdown("*Your compassionate mental health companion* 🔮")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm" not in st.session_state:
    st.session_state.llm = init_llm()

# Check LLM
if not st.session_state.llm:
    st.error("❌ **GROQ_API_KEY required!**")
    st.info("`export GROQ_API_KEY=your_key_here`")
    st.stop()

# Chat Interface
st.subheader("💬 **How are you feeling today?**")

# Chat container
chat_container = st.container()

# Input
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input("", key="user_input", label_visibility="collapsed")
with col2:
    analyze_btn = st.button("✨ Send", use_container_width=True)

# Process input
if analyze_btn and user_input:
    with st.spinner("Analyzing your feelings..."):
        # NLP Analysis
        sentiment = analyze_sentiment(user_input)
        crisis_detected = detect_crisis_keywords(user_input)
        risk_score = calculate_risk_score(user_input)
        
        # LLM Response
        llm_response = generate_counseling_response(
            st.session_state.llm, user_input, sentiment, risk_score
        )
        
        # Store message
        msg = {
            "role": "user",
            "content": user_input,
            "sentiment": sentiment,
            "risk": risk_score,
            "timestamp": datetime.now().strftime("%H:%M"),
            "crisis": crisis_detected
        }
        st.session_state.messages.append(msg)
        
        ai_msg = {
            "role": "assistant",
            "content": llm_response,
            "risk": risk_score,
            "timestamp": datetime.now().strftime("%H:%M")
        }
        st.session_state.messages.append(ai_msg)

# Display chat history
with chat_container:
    for msg in st.session_state.messages[-10:]:  # Last 10 messages
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**You** ({msg['timestamp']}):")
                st.write(msg["content"])
                
                # Risk indicator
                risk_color = "🔴" if msg["risk"] > 0.7 else "🟡" if msg["risk"] > 0.4 else "🟢"
                st.caption(f"💭 Mood: {msg['sentiment']} | Risk: {risk_color} {msg['risk']:.1%}")
                
        else:  # assistant
            with st.chat_message("assistant"):
                st.write(f"**MindWell AI** ({msg['timestamp']}):")
                st.write(msg["content"])
                
                # Special crisis handling
                if msg["risk"] > 0.7:
                    st.error("🚨 **CRISIS DETECTED**")
                    st.markdown(get_crisis_resources())
                    st.balloons()  # Attention grabber

# Quick Assessment Form
st.markdown("---")
st.subheader("📊 **Quick Mood Check**")

col1, col2, col3 = st.columns(3)
with col1:
    mood = st.slider("😊 Current mood", 1, 10, 5)
with col2:
    anxiety = st.slider("😰 Anxiety level", 1, 10, 3)
with col3:
    sleep = st.slider("😴 Sleep quality", 1, 10, 6)

if st.button("🔍 **Assess My Risk**", use_container_width=True):
    quick_risk = (10-mood + anxiety + (10-sleep)) / 30
    risk_label = "HIGH" if quick_risk > 0.6 else "MEDIUM" if quick_risk > 0.3 else "LOW"
    
    col1, col2 = st.columns(2)
    with col1:
        if risk_label == "HIGH":
            st.error(f"🚨 **HIGH RISK** ({quick_risk:.0%})")
        elif risk_label == "MEDIUM":
            st.warning(f"⚠️ **MEDIUM RISK** ({quick_risk:.0%})")
        else:
            st.success(f"✅ **LOW RISK** ({quick_risk:.0%})")
    
    with col2:
        st.info("**Next Steps:**")
        if risk_label == "HIGH":
            st.markdown(get_crisis_resources())
        else:
            st.write("- 🧘 Practice deep breathing")
            st.write("- 📞 Talk to a trusted friend")
            st.write("- 💤 Prioritize sleep")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #6b7280;'>
    <h3>⚠️ **Important Disclaimer**</h3>
    <p><strong>This AI is NOT a substitute for professional mental health care.</strong></p>
    <p>For emergencies, call your local crisis hotline immediately.</p>
    <p>Made with ❤️ for mental wellness awareness</p>
</div>
""", unsafe_allow_html=True)

# Clear chat
if st.button("🗑️ **Clear Chat**", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
