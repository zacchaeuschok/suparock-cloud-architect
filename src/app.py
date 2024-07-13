import os
import streamlit as st
from src.aws_tool.main import search
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

st.title("AWS Architect")

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

        # Check if the image was generated and saved locally
        image_path = 'tmp.png'
        if os.path.exists(image_path):
            message_data["image"] = image_path

        st.session_state.messages.append(message_data)
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(response["output"])
            if os.path.exists(image_path):
                st.image(image_path)
    else:
        error_message = "Sorry, I could not process your request."
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(error_message)
