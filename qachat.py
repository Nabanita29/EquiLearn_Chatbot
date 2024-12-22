import time
from dotenv import load_dotenv
from gtts import gTTS
import streamlit as st
import os
import google.generativeai as genai
import tempfile
import pygame
from threading import Thread
from queue import Queue

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

def play_audio_from_queue(audio_queue):
    """Continuously plays audio files from the queue."""
    pygame.mixer.init()
    while True:
        temp_audio_path = audio_queue.get()  # Blocking call
        if temp_audio_path == "STOP":
            pygame.mixer.music.stop()  # Stop the music
            break
        try:
            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            os.remove(temp_audio_path)  # Clean up the temporary file after playing
        except Exception as e:
            print(f"Error during audio playback: {e}")
    pygame.mixer.quit()

def generate_audio_chunks(text_chunks, audio_queue):
    """Generate audio for text chunks and put them in the queue."""
    for text in text_chunks:
        try:
            tts = gTTS(text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio_path = temp_audio.name
            tts.save(temp_audio_path)
            audio_queue.put(temp_audio_path)
        except Exception as e:
            print(f"Error generating TTS audio: {e}")

# Streamlit App Configuration
st.set_page_config(page_title="EquiLearn", page_icon="🔮", layout="wide")

# Chat UI with Minimalist Colors and Spacing
st.markdown("""
    <style>
        .stButton>button {
            background-color: #FF69B4;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            padding: 15px;
            width: 150px;
        }
        .stTextInput input {
            font-size: 20px;
            border-radius: 10px;
            padding: 10px;
            width: 80%;
        }
        .chat-box {
            font-size: 16px;
            padding: 15px;
            margin: 10px 0; /* Add spacing between messages */
            border-radius: 10px;
            border: 1px solid #ddd; /* Add a subtle border */
        }
        .user-msg {
            background-color: #f9f9f9; /* Light gray for user messages */
            color: #333;
            text-align: left;
        }
        .bot-msg {
            background-color: #e6f7ff; /* Light blue for bot messages */
            color: #333;
            text-align: left;
        }
        .chat-container {
            max-width: 80%;
            margin: 0 auto; /* Center the chat container */
        }
    </style>
""", unsafe_allow_html=True)

st.header("Welcome to EquiLearn Chatbot! 🌟")
st.subheader("Ask anything, and I’ll help you! 🤖")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "audio_queue" not in st.session_state:
    st.session_state["audio_queue"] = Queue()
    Thread(target=play_audio_from_queue, args=(st.session_state["audio_queue"],), daemon=True).start()

# Input Bar with Minimalist Design
col1, col2 = st.columns([8, 1])
with col1:
    user_input = st.text_input(
        "Type your message here:",
        placeholder="Ask me anything...",
        key="input",
    )
with col2:
    if st.button("Send 🚀", key="send-btn"):
        if user_input:
            st.session_state["chat_history"].append(("You", user_input))
            
            text_chunks = []
            complete_response = ""

            for chunk in get_gemini_response_stream(user_input):
                complete_response += chunk
                text_chunks.append(chunk)  # Append chunks as they arrive
                time.sleep(0.1)

            # Once streaming is done, generate audio
            Thread(target=generate_audio_chunks, args=(text_chunks, st.session_state["audio_queue"])).start()

            st.session_state["chat_history"].append(("Bot", complete_response))

# Chat History Display with Minimalist Design
chat_container = st.container()
with chat_container:
    for role, text in st.session_state["chat_history"]:
        if role == "You":
            st.markdown(
                f'<div class="chat-box user-msg">{text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-box bot-msg">{text}</div>',
                unsafe_allow_html=True,
            )

# Play Again Button
if st.button("Play Again 🔁", key="play-again"):
    # Re-enqueue the last audio file
    if st.session_state["chat_history"]:
        last_response = st.session_state["chat_history"][-1][1]  # Get the last bot response
        text_chunks = [last_response]  # Make it ready for playback again
        Thread(target=generate_audio_chunks, args=(text_chunks, st.session_state["audio_queue"])).start()
