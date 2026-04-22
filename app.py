import streamlit as st
import os
from datetime import datetime

# Local utils
from utils import (
    analyze_sentiment, detect_crisis_keywords, calculate_risk_score,
    generate_counseling_response
)

# LLM Setup
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MindWell AI – Mental Health Companion",
    page_icon="🧠",
    layout="centered"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu, footer, header { visibility: hidden; }

    /* Page background */
    .stApp { background-color: #0d1117; }

    /* Header */
    .main-header {
        font-size: 2.6rem;
        background: linear-gradient(135deg, #6ee7b7 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        margin-bottom: 4px;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 14px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessageContent"] p {
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* User bubble */
    [data-testid="stChatMessage-user"] {
        background-color: #1e3a5f !important;
        border-bottom-right-radius: 4px !important;
    }

    /* Bot bubble */
    [data-testid="stChatMessage-assistant"] {
        background-color: #1a2e1f !important;
        border-bottom-left-radius: 4px !important;
    }

    /* Crisis banner */
    .crisis-banner {
        background: linear-gradient(135deg, #7f1d1d, #991b1b);
        color: #fecaca;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 5px solid #f87171;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    /* Input */
    .stTextInput > div > div > input {
        background-color: #161b22 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 25px !important;
        color: #e2e8f0 !important;
        padding: 12px 20px !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6ee7b7 !important;
        box-shadow: none !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #6b7280 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #6ee7b7 !important;
        color: #0d1117 !important;
        border: none !important;
        border-radius: 25px !important;
        height: 50px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.85 !important;
        transform: translateY(-1px) !important;
    }

    /* Risk caption */
    .risk-caption {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Divider */
    hr { border-color: #2d3748 !important; }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #4b5563;
        font-size: 0.82rem;
        border-top: 1px solid #2d3748;
        margin-top: 1.5rem;
    }

    /* Info box */
    .stAlert {
        background-color: #161b22 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 12px !important;
        color: #9ca3af !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INIT LLM (cached)
# ─────────────────────────────────────────────
@st.cache_resource
def init_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, FileNotFoundError):
            st.error("❌ GROQ_API_KEY not found. Add it to Streamlit secrets.")
            return None

    try:
        llm = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=400
        )
        prompt = ChatPromptTemplate.from_template("""
You are MindWell AI, a compassionate and professionally trained mental health support companion.

CORE PRINCIPLES:
- Validate the user's feelings before offering any advice ("I hear you", "That sounds really hard")
- Use empathy-first language; never minimize emotions
- Apply CBT techniques gently — challenge negative thoughts, not the person
- NEVER diagnose, prescribe, or claim to replace therapy
- If the user mentions suicide, self-harm, or is in danger → immediately urge them to call a helpline
- End every response with one small, actionable step the user can take right now

User message: {input}

Respond with warmth and care (150–250 words):
""")
        return prompt | llm | StrOutputParser()
    except Exception as e:
        st.error(f"❌ LLM init failed: {str(e)}")
        return None


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm" not in st.session_state:
    st.session_state.llm = init_llm()
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False


# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────
if not LLM_AVAILABLE:
    st.error("❌ Missing dependencies. Run: `pip install -r requirements.txt`")
    st.stop()

if not st.session_state.llm:
    st.error("❌ **GROQ_API_KEY not found.**")
    st.info("Get a free key at https://console.groq.com and add it to Streamlit secrets.")
    st.stop()

st.markdown('<h1 class="main-header">🧠 MindWell AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">A compassionate space to share how you\'re feeling</p>', unsafe_allow_html=True)

st.markdown("---")

# ── Chat history ──
chat_area = st.container()
with chat_area:
    if not st.session_state.messages:
        st.info("👋 Hi! I'm MindWell AI. Feel free to share what's on your mind — I'm here to listen.")
    else:
        for msg in st.session_state.messages[-20:]:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
                    risk = msg.get("risk", 0)
                    risk_icon = "🔴" if risk > 0.7 else "🟡" if risk > 0.4 else "🟢"
                    st.markdown(
                        f'<p class="risk-caption">💭 {msg.get("sentiment","—")} &nbsp;|&nbsp; '
                        f'{risk_icon} {risk:.0%} &nbsp;|&nbsp; {msg["timestamp"]}</p>',
                        unsafe_allow_html=True
                    )
            else:
                with st.chat_message("assistant"):
                    if msg.get("crisis"):
                        st.markdown(
                            '<div class="crisis-banner">🚨 I noticed some concerning language. '
                            'Please reach out to a crisis helpline — you are not alone.</div>',
                            unsafe_allow_html=True
                        )
                    st.write(msg["content"])
                    st.caption(msg["timestamp"])

# ── Input ──
st.markdown("---")
col1, col2 = st.columns([5, 1])
with col1:
    input_key = "user_input_0" if not st.session_state.clear_input else "user_input_1"
    user_input = st.text_input(
        "Your message",
        key=input_key,
        placeholder="Share how you're feeling...",
        label_visibility="collapsed"
    )
with col2:
    send_btn = st.button("💬 Send", use_container_width=True)

# ── Process ──
if send_btn and user_input.strip():
    text = user_input.strip()

    with st.spinner("MindWell is listening..."):
        sentiment    = analyze_sentiment(text)
        crisis_flag  = detect_crisis_keywords(text)
        risk_score   = calculate_risk_score(text)
        llm_response = generate_counseling_response(
            st.session_state.llm, text, sentiment, risk_score
        )

    st.session_state.messages.append({
        "role":      "user",
        "content":   text,
        "sentiment": sentiment,
        "risk":      risk_score,
        "crisis":    crisis_flag,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })
    st.session_state.messages.append({
        "role":      "assistant",
        "content":   llm_response,
        "crisis":    crisis_flag,
        "risk":      risk_score,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })

    st.session_state.clear_input = not st.session_state.clear_input
    st.rerun()

# ── Clear chat ──
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ⚠️ <strong>Disclaimer:</strong> MindWell AI is not a substitute for professional mental health care.<br>
    For emergencies, please call your local crisis hotline immediately.<br><br>
    Made with ❤️ for mental wellness awareness
</div>
""", unsafe_allow_html=True)
