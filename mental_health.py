import streamlit as st
import spacy
import subprocess
from openai import OpenAI
import tiktoken
from PIL import Image
import base64

# Ensure the language model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


# Initialize SpaCy model for NLP
nlp = spacy.load('en_core_web_sm')

# Set your OpenAI API key
#client = OpenAI(api_key='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')


client = OpenAI(api_key='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')

# Function to count tokens using tiktoken
def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    return len(tokens)

# Function to generate AI response based on response type
def generate_ai_response(response_type, user_input):
    system_message = "You are a mental health coach assistant."
    
    if response_type == "Without Data Science and UX":
        prompt = f"The user is seeking support and here is their input: '{user_input}'. Provide a response without data science and user experience considerations.Do not pose a question just a recommendation."
    elif response_type == "With Data Science Only":
        prompt = f"The user is seeking support and here is their input: '{user_input}'. Provide a response with data science considerations only, including quantitative data, examples, and numerical insights. Give links to external resources."
    elif response_type == "With UX Only":
        prompt = f"The user is seeking support and here is their input: '{user_input}'. Provide a response with user experience considerations only, including visual aids or empathetic language."
    elif response_type == "With Both Data Science and UX":
        prompt = f"The user is seeking support and here is their input: '{user_input}'. Provide a response with both data science and user experience considerations, including quantitative data, examples, numerical insights, visual aids, and empathetic language.Give links to external resources."

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
background_image = get_base64_of_bin_file("welcome2.jpg")  # Ensure you have a logo file named 'welcome_logo.png'
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
    color: #ff69b4; /* Bright pink color for better visibility */
}}
.title {{
    color: #000000; /* Pink color */
    font-size: 2.5em;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}}
.intro-text {{
    color: #000000; /* Black color for intro text */
    text-align: center;
    margin-bottom: 20px;
}}

.textbox {{
    background-color: #ffffff; /* Bright white background */
    color: #ff69b4; /* Text color for input */
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
}}
.dropdown {{
    background-color: #ffffff; /* Bright white background */
    color: #ff69b4; /* Text color for dropdown */
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 20px;
}}
.ai-response {{
    background-color: #ffffff; /* Bright white background */
    color: #ff69b4; /* Text color for AI response */
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
}}
</style>
"""

st.markdown(background_css, unsafe_allow_html=True)

st.markdown('<div class="content">', unsafe_allow_html=True)

st.markdown('<div class="title">AI Mental Health Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="intro-text">Share your thoughts or experiences to receive personalized mental health advice.</div>', unsafe_allow_html=True)

if 'user_text' not in st.session_state:
    st.session_state.user_text = ""

user_input = st.text_area("Enter your thoughts here", height=150)

# Dropdown to select the AI response type
response_type = st.selectbox("Select AI Response Type", ["Without Data Science and UX", "With Data Science Only", "With UX Only", "With Both Data Science and UX"])

if user_input:
    st.session_state.user_text = user_input

if st.session_state.user_text:
    if st.button("Get AI Response"):
        ai_response = generate_ai_response(response_type, st.session_state.user_text)
        st.markdown(f'<div class="ai-response">AI Response: {ai_response}</div>', unsafe_allow_html=True)
        if response_type == "With UX Only" or response_type == "With Both Data Science and UX":
            st.image("example2.jpg", caption="Visual Aid", use_column_width=True)  # Replace with an appropriate image path
            # Add music clip
            st.audio("example.mp3")  # Replace with your music file path

st.markdown('</div>', unsafe_allow_html=True)
