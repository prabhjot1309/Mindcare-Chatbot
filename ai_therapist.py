import os
import streamlit as st
from groq import Groq


# API KEY
api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

def generate_reply(user_input, chat_history):

    messages = [
        {
            "role": "system",
            "content": "You are a friendly mental health therapist. Respond in the same language as the user. Be supportive and ask follow-up questions."
        }
    ]

    # chat history
    for role, msg in chat_history:
        if role == "user":
            messages.append({"role": "user", "content": msg})
        else:
            messages.append({"role": "assistant", "content": msg})

    # current message
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        return "Sorry, something went wrong. Please try again."
