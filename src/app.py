import streamlit as st
from src.doc_search.main import search
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
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        st.session_state.messages.append({"role": "assistant", "content": response["output"]})
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(response["output"])
    else:
        error_message = "Sorry, I could not process your request."
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant", avatar=avatars["assistant"]):
            st.markdown(error_message)
