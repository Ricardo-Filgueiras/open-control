import streamlit as st

def render_sidebar(session):
    with st.sidebar:
        st.title("J.A.R.V.I.S. Control")
        st.write("---")
        
        # TOGGLE DE PROVEDOR 🤖
        st.markdown("### Matrix Selection")
        provider = st.selectbox(
            "Matrix Ativa", 
            ["Google (Gemini)", "Local (Ollama)"], 
            index=0 if st.session_state.get('provider') == 'google' else 1
        )
        
        # Mapeamento para o Controller
        st.session_state.provider = "google" if "Google" in provider else "local"
        
        if st.button("Resetar Conversa", use_container_width=True):
            session.clear()
            st.rerun()

        st.divider()

        st.markdown("### Status do Sistema")
        st.write(f"Mensagens na sessão: {len(session.messages)}")
        st.write(f"Matrix: {provider}")
