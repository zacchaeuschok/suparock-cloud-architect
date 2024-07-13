from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
import streamlit as st

from src.doc_search.main import search

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = search(prompt, callbacks=[st_callback])
        st.write(response["output"])

