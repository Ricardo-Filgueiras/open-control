import streamlit as st

def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
