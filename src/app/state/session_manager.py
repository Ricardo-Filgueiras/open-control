import streamlit as st

class SessionManager:

    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    @property
    def messages(self):
        return st.session_state.messages

    def add_message(self, role: str, content: str):
        st.session_state.messages.append({
            "role": role,
            "content": content
        })

    def clear(self):
        st.session_state.messages = []
