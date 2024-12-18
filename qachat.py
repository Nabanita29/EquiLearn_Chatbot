from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai

# Configure the Gemini Pro model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Streamlit App Configuration
st.set_page_config(page_title="EquiLearn", page_icon="🔮", layout="wide")

# Custom CSS for Styling
st.markdown("""
    <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 500px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 10px;
            background-color: #FFFFFF;
            margin-bottom: 10px;
        }
        .chat-box {
            padding: 10px;
            margin: 5px 0;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-msg {
            background-color: #DCF8C6;
            align-self: flex-end;
        }
        .bot-msg {
            background-color: #F1F0F0;
            align-self: flex-start;
        }
        .send-btn {
            background-color: #FF4B4B;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #ccc;
        }
    </style>
    """, unsafe_allow_html=True)

# Welcome Header
st.header("Welcome to EquiLearn Chatbot! 🌟")
st.subheader("Ask anything, and I’ll help you!")

# Input Bar Above Chat History
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input("Type your message here:", placeholder="Ask me anything...", key="input")
with col2:
    if st.button("Send", key="send-btn"):
        if user_input:
            st.session_state["chat_history"].append(("You", user_input))
            with st.spinner("Thinking..."):
                response = get_gemini_response(user_input)
                bot_response = "".join(chunk.text for chunk in response)
                st.session_state["chat_history"].append(("Bot", bot_response))
            st.rerun()

# Chat History Session State
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Chat History Display Container (NO BOX ABOVE)
chat_container = st.container()
with chat_container:
    for role, text in st.session_state["chat_history"]:
        if role == "You":
            st.markdown(f'<div class="chat-box user-msg">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box bot-msg">{text}</div>', unsafe_allow_html=True)


