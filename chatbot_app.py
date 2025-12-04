import streamlit as st
import os
from google import genai

# --- Security Configuration (CRITICAL) ---
# Load API Key securely from the environment variable named 'GEMINI_API_KEY'
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("FATAL ERROR: GEMINI_API_KEY environment variable not set.")
        st.stop()
        
    # **FIX: Initialize the Client instead of using the deprecated configure()**
    client = genai.Client(api_key=api_key) 
    
except Exception as e:
    st.error(f"Error configuring API key: {e}")
    st.stop()
# ------------------------------------------

# **FIX: The model call uses the client object and the specific method**
# Note: For the Client model, the method is client.models.generate_content
def get_gemini_response(prompt):
    # This is how you call the model using the Client object
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Using the modern 'gemini-2.5-flash' model
        contents=[prompt]
    )
    return response.text

# Page title
st.title("🤖 AI Chatbot – Gemini + Streamlit")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Chat Display ---
st.subheader("Chat History")
for role, msg in st.session_state.messages:
    st.markdown(f"**{role}:** {msg}")

# --- User Input and Response Generation ---

user_input = st.text_input("Enter your message:")

if st.button("Send"):
    if user_input.strip():
        # 1. Save user message
        st.session_state.messages.append(("You", user_input))

        # 2. Build the prompt for the AI
        prompt = f"You are a friendly helpful chatbot. Reply briefly and concisely to the following user message.\nUser: {user_input}"

        try:
            # 3. Get response from Gemini
            with st.spinner('Thinking...'):
                # Call the updated function
                bot_reply = get_gemini_response(prompt) 
        except Exception as e:
            bot_reply = f"Error communicating with Gemini: {e}"

        # 4. Save bot response
        st.session_state.messages.append(("Bot", bot_reply))

        # 5. Force UI refresh
        st.rerun()

# --- Utility Buttons ---
if st.button("Clear Chat"):
    st.session_state.messages = []
