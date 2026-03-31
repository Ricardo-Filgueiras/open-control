import streamlit as st
import sys
import os
from pathlib import Path

# Adiciona o diretório 'src' ao sys.path para permitir imports absolutos
root_path = Path(__file__).resolve().parent.parent.parent
src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from app.services.agent_service import AgentService
from app.state.session_manager import SessionManager
from app.components.chat_window import render_chat
from app.components.sidebar import render_sidebar

# --- CONFIGURAÇÃO DA UI ---
st.set_page_config(
    page_title="J.A.R.V.I.S. HUD v2.0",
    page_icon="🤖",
    layout="wide"
)

# --- ESTÉTICA STARK INDUSTRIES ---
st.markdown("""
<style>
    .stApp { background-color: #01080b; color: #e0fbfc; }
    .stChatMessage { 
        background: rgba(255, 255, 255, 0.05); 
        backdrop-filter: blur(10px); 
        border: 1px solid rgba(0, 245, 212, 0.2); 
        border-radius: 15px; 
    }
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif; 
        color: #00f5d4; 
        text-shadow: 0 0 10px rgba(0, 245, 212, 0.5); 
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- BOOT DO SISTEMA ---
if 'agent' not in st.session_state:
    st.session_state.agent = AgentService()
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()

agent = st.session_state.agent
session = st.session_state.session_manager

# Atualiza o provedor no controller se houver mudança na UI
if 'provider' in st.session_state:
    agent.controller.provider = st.session_state.provider

# --- RENDERIZAÇÃO ---
render_sidebar(session)

st.title("J.A.R.V.I.S.")
st.subheader("Central Command Alpha")

# Renderiza Janela de Chat
render_chat(session.messages)

# Input principal do usuário
if user_input := st.chat_input("Sir?"):
    # Adiciona msg do usuário
    session.add_message("user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    # Resposta do JARVIS
    with st.chat_message("assistant"):
        with st.spinner("Analisando protocolos, Sir..."):
            response = agent.process_message(user_input)
            st.markdown(response)
            session.add_message("assistant", response)
