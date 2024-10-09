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

# Function to generate AI response based on response type
def generate_ai_response(response_type, user_input):
    system_message = "You are a mental health coach assistant."
    
    # Check if response type is one that utilizes the dataset
    if response_type in ["With Data Science Only", "With Both Data Science and UX"]:
        # Extract user-specific details for data science scenarios
        user_info = df.iloc[0]  # Assuming only one user for simplicity
        customization_info = f"User is a {user_info['age']}-year-old {user_info['gender']} who is currently feeling {user_info['emotional_state']}. They previously mentioned: '{user_info['conversation_history']}' and prefer '{user_info['preferred_support_style']}'. They are interested in topics like '{user_info['topics_of_interest']}' and have given feedback that they '{user_info['previous_advice_feedback']}'."
    else:
        customization_info = ""  # No customization needed for other scenarios

    # Create prompt based on response type
    if response_type == "Without Data Science and UX":
        prompt = f"The user seeks support and here is their input: '{user_input}'. Provide a general recommendation."
    elif response_type == "With Data Science Only":
        prompt = f"{customization_info} Based on this input: '{user_input}', provide a data-driven response with quantitative analysis and external resource links."
    elif response_type == "With UX Only":
        prompt = f"The user seeks support and here is their input: '{user_input}'. Provide an empathetic response with visual and sensory elements."
    elif response_type == "With Both Data Science and UX":
        prompt = f"{customization_info} Based on this input: '{user_input}', provide a response that includes both data-driven insights and empathetic language, with links to external resources."

    # Get response from OpenAI
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )
    ai_response = completion.choices[0].message.content.strip()
    return ai_response

# Function to encode image to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Streamlit UI
st.set_page_config(page_title="AI Mental Health Coach", page_icon=":brain:", layout="wide")

# Custom CSS for background image and other styling
background_image = get_base64_of_bin_file("welcome2.jpg")
background_css = f"""
<style>
.stApp {{
    background: url(data:image/png;base64,{background_image});
    background-size: cover;
    background-position: center;
}}
.content {{
    position: relative;
    z-index: 2;
    color: #ff69b4;
}}
.title {{
    color: #000000;
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}}
.intro-text {{
    color: #000000;
    text-align: center;
    margin-bottom: 20px;
}}
.textbox, .dropdown, .ai-response {{
    background-color: #ffffff;
    color: #ff69b4;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
}}
.user-message {{
    text-align: left;
    color: #ff69b4;
}}
.ai-response {{
    text-align: right;
    color: #000000;
}}
</style>
"""

st.markdown(background_css, unsafe_allow_html=True)
st.markdown('<div class="content">', unsafe_allow_html=True)
st.markdown('<div class="title">AI Mental Health Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="intro-text">Share your thoughts or experiences to receive personalized mental health advice.</div>', unsafe_allow_html=True)

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_area("Enter your thoughts here", height=150)
response_type = st.selectbox("Select AI Response Type", ["Without Data Science and UX", "With Data Science Only", "With UX Only", "With Both Data Science and UX"])

# Handle user input and AI response
if user_input:
    if st.button("Send"):
        # Store user message
        st.session_state.chat_history.append(("user", user_input))
        # Generate and store AI response
        ai_response = generate_ai_response(response_type, user_input)
        st.session_state.chat_history.append(("ai", ai_response))
        # Clear input box after sending
        st.session_state.user_text = ""

# Display chat history in alternating columns
for role, text in st.session_state.chat_history:
    cols = st.columns([2, 1, 2]) if role == "user" else st.columns([1, 2, 2])
    with cols[0] if role == "user" else cols[2]:
        st.markdown(f'<div class="{"user-message" if role == "user" else "ai-response"}">{text}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
