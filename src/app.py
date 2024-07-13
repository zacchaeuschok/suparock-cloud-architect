import glob
import os
import re

import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler

from src.aws.main import search

st.title("👩🏻‍💻Suparock AWS Architect 🚀")

# Sidebar formatting with Markdown and emojis
st.sidebar.title("🛠️ About Suparock")
st.sidebar.markdown("""
Suparock is designed to assist users with AWS architecture queries. The agent is capable of:

- 🖥️ Running **AWS CLI commands** to fetch configuration and setup details.
- 📘 Referencing best practices from **AWS Well-Architected Framework**.
- 🐍 Generating **AWS cloud architecture diagrams**.

Users can input their queries and the AWS architect will process these using the appropriate tools, returning information and visual diagrams where applicable.
""")

# Add some spacing and visual appeal to sidebar options
st.sidebar.markdown("---")
st.sidebar.header("🔧 Utilities")
if st.sidebar.button('🔄 Reset Application'):
    for file_path in glob.glob('*.png'):
        os.remove(file_path)
    st.rerun()


# Initialize chat history if not already in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

avatars = {
    "user": "https://ps.w.org/user-avatar-reloaded/assets/icon-256x256.png?rev=2540745",
    "assistant": "https://partner.zoom.us/wp-content/uploads/2022/12/2022_Zoom-AWS_Lockup_RGB-1-e1672857797889-1024x760.png"
}

# Display chat messages from history
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar=avatars[role]):
        st.markdown(message["content"])
        if message.get("image"):  # Check if there's an image to display
            st.image(message["image"], caption="Here's what I found:")

# Handle user input
if prompt := st.chat_input("What is my AWS bill for July 2024?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=avatars["user"]):
        st.markdown(prompt)

    # Prepare the callback handler
    st_callback = StreamlitCallbackHandler(st.container())

    # Call the search function and handle the response
    response = search(prompt, callbacks=[st_callback])

    # Check if the response contains expected output and display it
    if response and "output" in response:
        message_data = {"role": "assistant", "content": response["output"]}

        # Attempt to extract an image path from the output
        image_path_match = re.search(r'"?([\w/\\]+\.png)"?', response["output"])
        if image_path_match:
            image_path = image_path_match.group(1)
            if os.path.exists(image_path):
                message_data["image"] = image_path

        st.session_state.messages.append(message_data)
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(response["output"])
            if "image" in message_data:
                st.image(message_data["image"])
    else:
        error_message = "Sorry, I could not process your request."
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(error_message)
