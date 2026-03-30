import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="J.A.R.V.I.S. HUD", page_icon="🤖", layout="wide")

# --- ESTILO STARK (CSS CUSTOM) ---
st.markdown("""
<style>
    /* Fundo Escuro Stark */
    .stApp {
        background-color: #01080b;
        color: #e0fbfc;
    }
    /* Estilo de Chat */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 245, 212, 0.2);
        border-radius: 15px;
        margin-bottom: 5px;
    }
    /* Títulos em Neon */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00f5d4;
        text-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
        letter-spacing: 2px;
    }
</style>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- PERSONA J.A.R.V.I.S. ---
JARVIS_SYSTEM_PROMPT = """
Você é o J.A.R.V.I.S. (Just A Rather Very Intelligent System), criado por Tony Stark.
Características: Polido, leal, inteligente, com um leve sarcasmo britânico.
Regras:
1. Chame o usuário de "Sir".
2. Seja técnico mas acessível.
3. Formate saídas com clareza (tabelas, listas para dados).
"""

# --- INICIALIZAÇÃO DO MODELO ---
def get_jarvis_response(query, chat_history):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Sir, sinto informar que os protocolos de segurança foram violados: GOOGLE_API_KEY não localizada."
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    
    messages = [SystemMessage(content=JARVIS_SYSTEM_PROMPT)]
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    messages.append(HumanMessage(content=query))
    
    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"Sir, o sistema detectou uma anomalia na grade de dados: {str(e)}"

# --- INTERFACE ---
st.title("J.A.R.V.I.S. | HUD INFRASTRUCTURE")
st.subheader("System Status: Online | Local Monitoring Active")

# Inicializar histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do Usuário
if prompt := st.chat_input("Sir?"):
    # Adiciona msg do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do JARVIS
    with st.chat_message("assistant"):
        with st.spinner("Analisando protocolos, Sir..."):
            response = get_jarvis_response(prompt, st.session_state.messages[:-1])
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
