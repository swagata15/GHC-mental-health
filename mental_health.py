import streamlit as st
from openai import OpenAI
import tiktoken
from PIL import Image
import pandas as pd
import base64

# Define a synthetic dataset for one user with enhanced attributes
data = {
    'age': [29],
    'gender': ['male'],
    'conversation_history': ["I've been experiencing work-related stress lately."],
    'emotional_state': ["anxious"],
    'preferred_support_style': ["insightful and data-driven"],
    'topics_of_interest': ["work-life balance, productivity, mental well-being"],
    'previous_advice_feedback': ["Finds value in data-backed insights and prefers actionable steps"]
}
df = pd.DataFrame(data)

# Set your OpenAI API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Function to count tokens using tiktoken
def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    return len(tokens)

# Function to generate AI response and explanation based on response type
def generate_ai_response(response_type, user_input):
    system_message = "You are a mental health coach assistant."
    
    # Check if response type is one that utilizes the dataset
    if response_type in ["With Data Science Only", "With Both Data Science and UX"]:
        user_info = df.iloc[0]  # Assuming only one user for simplicity
        customization_info = f"User is a {user_info['age']}-year-old {user_info['gender']} who is currently feeling {user_info['emotional_state']}. They previously mentioned: '{user_info['conversation_history']}' and prefer '{user_info['preferred_support_style']}'. They are interested in topics like '{user_info['topics_of_interest']}' and have given feedback that they '{user_info['previous_advice_feedback']}'."
    else:
        customization_info = ""  # No customization needed for other scenarios

    # Create prompt based on response type
    if response_type == "Without Data Science and UX":
        prompt = f"The user seeks support and here is their input: '{user_input}'. Provide a general recommendation."
        explanation = "This response is a general recommendation based on mental well-being principles."
    elif response_type == "With Data Science Only":
        prompt = f"{customization_info} Based on this input: '{user_input}', provide a data-driven response with quantitative analysis and external resource links."
        explanation = "This response leverages the user's work-related interests and conversation history, along with relevant resources."
    elif response_type == "With UX Only":
        prompt = f"The user seeks support and here is their input: '{user_input}'. Provide an empathetic response with visual and sensory elements."
        explanation = "This response focuses on empathetic language and aims to provide comfort with visual and audio aids."
    elif response_type == "With Both Data Science and UX":
        prompt = f"{customization_info} Based on this input: '{user_input}', provide a response that includes both data-driven insights and empathetic language, with links to external resources."
        explanation = "This response combines data-driven insights with empathetic language, considering user history and online resources."

    # Get response from OpenAI
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    ai_response = completion.choices[0].message.content.strip()
    return ai_response, explanation

# Streamlit UI
st.set_page_config(page_title="AI Mental Health Coach", page_icon=":brain:", layout="wide")

# Custom CSS for styling messages
background_css = """
<style>
.stApp {
    background: none;
}
.content {
    position: relative;
    z-index: 2;
    color: #ff69b4;
}
.title {
    color: #000000;
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}
.intro-text {
    color: #000000;
    text-align: center;
    margin-bottom: 20px;
}
.textbox, .dropdown {
    background-color: #ffffff;
    color: #ff69b4;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
}
.user-message, .ai-response {
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
}
.user-message {
    background-color: #d1e7ff;
    border: 1px solid #8ab6ff;
    color: #0a3d91;
}
.ai-response {
    background-color: #e8f5e9;
    border: 1px solid #a5d6a7;
    color: #1b5e20;
    text-align: right;
}
</style>
"""

st.markdown(background_css, unsafe_allow_html=True)
st.markdown('<div class="content">', unsafe_allow_html=True)
st.markdown('<div class="title">AI Mental Health Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="intro-text">Share your thoughts or experiences to receive personalized mental health advice.</div>', unsafe_allow_html=True)

# Initialize session state for chat history and previous response type
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'previous_response_type' not in st.session_state:
    st.session_state.previous_response_type = None

# User input and response type selection
user_input = st.text_area("Enter your thoughts here", height=150)
response_type = st.selectbox("Select AI Response Type", ["Without Data Science and UX", "With Data Science Only", "With UX Only", "With Both Data Science and UX"])

# Clear chat history if the response type changes
if response_type != st.session_state.previous_response_type:
    st.session_state.chat_history = []
    st.session_state.previous_response_type = response_type

# Handle user input and AI response
if user_input:
    if st.button("Send"):
        # Store user message
        st.session_state.chat_history.append(("user", user_input))
        # Generate and store AI response along with explanation
        ai_response, explanation = generate_ai_response(response_type, user_input)
        st.session_state.chat_history.append(("ai", ai_response, explanation))
        # Clear input box after sending
        st.session_state.user_text = ""

# Display chat history with alternating columns and explanations

for item in st.session_state.chat_history:
    role, text = item[0], item[1]
    cols = st.columns([2, 1, 2]) if role == "user" else st.columns([1, 2, 2])
    with cols[0] if role == "user" else cols[2]:
        st.markdown(f'<div class="{"user-message" if role == "user" else "ai-response"}">{text}</div>', unsafe_allow_html=True)
        # Show explanation with "Show More" option for AI responses
        if role == "ai" and len(item) > 2:
            with st.expander("Show More"):
                st.write(item[2])
            # Add visual and audio aids for UX scenarios with autoplay
            if response_type in ["With UX Only", "With Both Data Science and UX"]:
                st.image("example2.jpg", caption="Visual Aid", use_column_width=True)  # Replace with your own image path
                audio_html = """
                <audio autoplay controls>
                    <source src="example.mp3" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)



