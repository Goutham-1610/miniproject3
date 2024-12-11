import streamlit as st
from dotenv import load_dotenv
import os
import shelve
from openai import OpenAI

load_dotenv()

# Add custom CSS to control the container width
st.markdown(
    """
    <style>
    .main-container {
        width: 50%;
        margin: 0 auto;
    }
    .title-sg {
        color: #ff6347; /* Color for SG */
    }
    .title-medi-bot {
        color: #4682b4; /* Color for MEDI-BOT */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply the custom class to the main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown('<h1><span class="title-sg">SG</span> <span class="title-medi-bot">MEDI-BOT</span></h1>', unsafe_allow_html=True)

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Point the client to your local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "sdk/gouthamrepo"

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])

# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Sidebar with title, description, and delete chat history button
with st.sidebar:
    st.markdown('<h2><span class="title-sg">SG</span> <span class="title-medi-bot">MEDI-BOT</span></h2>', unsafe_allow_html=True)
    
    # Add the description
    st.write("""
    **Welcome to the AI-Powered Medical Assistant, an innovative chatbot designed to offer personalized healthcare advice across a range of medical fields. Currently, our focus is on skincare, where the chatbot provides accurate and reliable guidance on common skin conditions, helping you manage your skin health effectively.**
    """)
    
    delete_button_placeholder = st.empty()
    with delete_button_placeholder.container():
        if st.button("Delete Chat History"):
            st.session_state.messages = []
            save_chat_history([])

# Age, gender, and previous record input in the main section
col1, col2, col3 = st.columns(3)

with col1:
    age = st.selectbox("Age Group", ["1-10", "11-20", "21-50", "51-80", "81-100"])
    st.write(f"Selected age range: {age}")

with col2:
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    st.write(f"Selected gender: {gender}")

with col3:
    previous_record = st.text_input("Previous Record")
    st.write(f"Previous record: {previous_record}")

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)

# Close the main container div
st.markdown('</div>', unsafe_allow_html=True)
