import streamlit as st
from ai_therapist import generate_reply
import warnings

warnings.filterwarnings("ignore")

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Therapist", layout="centered")

# -------------------------------
# PREMIUM UI
# -------------------------------
st.markdown("""
<style>
.title {text-align:center;font-size:32px;font-weight:bold;}
.subtitle {text-align:center;color:gray;margin-bottom:20px;}
.chat-user {background:#1E1E1E;padding:10px;border-radius:10px;margin:5px;}
.chat-bot {background:#262730;padding:10px;border-radius:10px;margin:5px;}
.stButton button {border-radius:10px;background:linear-gradient(90deg,#4CAF50,#00C9A7);color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🧠 AI Mental Health Therapist</div>", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# -------------------------------
# 📝 ASSESSMENT SECTION
# -------------------------------
st.subheader("📝 Mental Health Assessment")

q1 = st.radio("Do you feel anxious frequently?", ["Never", "Sometimes", "Often"])
q2 = st.radio("Do you feel low or depressed?", ["Never", "Sometimes", "Often"])
q3 = st.radio("Do you have trouble sleeping?", ["No", "Sometimes", "Yes"])
q4 = st.radio("Do you feel motivated in daily life?", ["Yes", "Sometimes", "No"])

if st.button("Assess My Mental Health"):

    mapping = {
        "Never": 0,
        "No": 0,
        "Sometimes": 1,
        "Often": 2,
        "Yes": 2
    }

    score = mapping[q1] + mapping[q2] + mapping[q3] + mapping[q4]

    if score <= 2:
        result = "Healthy 😊"
        advice = "You're doing well! Maintain a balanced lifestyle 🌿"
    elif score <= 5:
        result = "Mild Stress 😐"
        advice = "Try meditation, exercise, and talking to friends 💙"
    else:
        result = "High Stress ⚠️"
        advice = "Consider talking to a professional or counselor 🤍"

    st.session_state.result = (result, advice)

# -------------------------------
# RESULT DISPLAY
# -------------------------------
if st.session_state.result:
    result, advice = st.session_state.result
    st.success(f"Your Mental Health Status: {result}")
    st.info(f"💡 Suggestion: {advice}")

# -------------------------------
# 💬 CHAT SECTION
# -------------------------------
st.subheader("💬 Talk to AI Therapist")

# show chat
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-user'>🧑 {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'>🤖 {msg}</div>", unsafe_allow_html=True)

# input
user_input = st.text_input("Talk in any language...", key="user_input")

col1, col2 = st.columns(2)

if col1.button("Send"):
    if st.session_state.user_input.strip() != "":
        user_msg = st.session_state.user_input

        st.session_state.chat_history.append(("user", user_msg))

        msg_lower = user_msg.lower()

        # 💊 SAFE MEDICAL SUGGESTIONS
        if "fever" in msg_lower or "bukhar" in msg_lower:
            reply = "It looks like you may have a fever 🤒. Take rest, stay hydrated, and use paracetamol if needed. If it continues, consult a doctor."
        
        elif "headache" in msg_lower:
            reply = "For headaches, try rest, hydration, and paracetamol if needed."
        
        elif "cold" in msg_lower or "cough" in msg_lower:
            reply = "For cold/cough, drink warm fluids, steam inhalation, and rest well."

        else:
            # 🔥 SAFE AI CALL (NO ERROR SHOWN)
            try:
                reply = generate_reply(user_msg, st.session_state.chat_history)
            except:
                reply = "I'm here for you 💙. Could you tell me more about how you're feeling?"

        st.session_state.chat_history.append(("assistant", reply))

        st.session_state.user_input = ""

if col2.button("Clear Chat"):
    st.session_state.chat_history = []
