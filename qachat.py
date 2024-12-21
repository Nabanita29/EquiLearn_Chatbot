import time
from dotenv import load_dotenv
from gtts import gTTS
import streamlit as st
import os
import google.generativeai as genai
import tempfile
import pygame
from threading import Thread

# Load Environment Variables
load_dotenv()

# Configure the Gemini Pro Model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Function to Get Response from Gemini API
def get_gemini_response_stream(question):
    response = chat.send_message(question, stream=True)
    for chunk in response:
        yield chunk.text

def play_response(text):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio_path = temp_audio.name
    tts.save(temp_audio_path)
    
    # Play the audio using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(temp_audio_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    
    # Unload the music to release the file
    pygame.mixer.music.unload()
    pygame.mixer.quit()
    
    # Clean up the temporary file
    os.remove(temp_audio_path)

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

# Initialize Chat History in Session State
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Input Bar Above Chat History
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input("Type your message here:", placeholder="Ask me anything...", key="input")
with col2:
    if st.button("Send", key="send-btn"):
        if user_input:
            # Add user message to chat history
            st.session_state["chat_history"].append(("You", user_input))
            
            # Generate and display response in real-time
            text_chunks = []
            complete_response = ""  # Initialize a variable to hold the full response
            
            def handle_audio():
                # Play the full response as audio after it's fully received
                play_response(complete_response)
            
            # Stream the bot's response
            for chunk in get_gemini_response_stream(user_input):
                complete_response += chunk  # Append chunks to form the complete response
                time.sleep(0.1)  # Simulate streaming delay
            
            # Add the complete bot response to the chat history
            st.session_state["chat_history"].append(("Bot", complete_response))
            
            # Start audio playback in a separate thread
            Thread(target=handle_audio).start()

# Chat History Display Container
chat_container = st.container()
with chat_container:
    for role, text in st.session_state["chat_history"]:
        if role == "You":
            st.markdown(f'<div class="chat-box user-msg">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box bot-msg">{text}</div>', unsafe_allow_html=True)
