import streamlit as st
import os
from utils import analyze_text, predict_from_form

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ================= API KEY =================

# 🔹 LOCAL TEST (use this)
groq_api_key = "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"

# 🔹 FOR DEPLOYMENT (uncomment this instead)
# groq_api_key = os.getenv("GROQ_API_KEY")

# ================= UI =================
st.set_page_config(page_title="Mental Health AI", page_icon="🧠")
st.title("🧠 AI Mental Health Assistant")

# Debug
st.write("API KEY FOUND:", bool(groq_api_key))

# ================= CHAT =================
user_input = st.text_input("Talk about how you're feeling:")

if user_input:

    llm_response = ""

    if groq_api_key:
        try:
            llm = ChatGroq(
                api_key=groq_api_key,
                model="llama3-8b-8192"
            )

            prompt = ChatPromptTemplate.from_template(
                "You are a calm, supportive mental health assistant. Respond empathetically.\nUser: {input}"
            )

            chain = prompt | llm
            llm_response = chain.invoke({"input": user_input}).content

        except Exception as e:
            llm_response = f"❌ LLM Error: {e}"
    else:
        llm_response = "❌ API key not found"

    # ---- Risk ----
    risk = analyze_text(user_input)

    # ---- Output ----
    st.subheader("💬 AI Response")
    st.write(llm_response)

    st.subheader("📊 Risk Analysis")
    if risk == "HIGH":
        st.error("🔴 High Risk")
    elif risk == "MEDIUM":
        st.warning("🟡 Moderate Risk")
    else:
        st.success("🟢 Low Risk")

# ================= FORM =================
st.subheader("📊 Mental Health Prediction")

age = st.slider("Age", 18, 60)
gender = st.selectbox("Gender", ["Male", "Female"])
family_history = st.selectbox("Family History", ["Yes", "No"])
work_interfere = st.selectbox(
    "Work Interference",
    ["Never", "Rarely", "Sometimes", "Often"]
)

if st.button("Predict Risk"):
    result = predict_from_form(age, gender, family_history, work_interfere)

    if result == "Needs Treatment":
        st.error("⚠️ High Risk Detected")
    elif result == "Model Not Loaded":
        st.warning("⚠️ Model not loaded properly")
    else:
        st.success("✅ Low Risk")
