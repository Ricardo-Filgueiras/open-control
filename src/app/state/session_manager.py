import streamlit as st
from datetime import datetime
from typing import Optional, List
from core.database.repositories import SessionRepository, MessageRepository

class SessionManager:
    """Gerencia sessões com persistência em SQLite"""
    
    def __init__(self, load_recent: bool = True):
        # Inicializar state do Streamlit
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_session_id" not in st.session_state:
            st.session_state.current_session_id = None
        
        if "session_start_time" not in st.session_state:
            st.session_state.session_start_time = datetime.now()
        
        # Repositórios
        self.session_repo = SessionRepository()
        self.message_repo = MessageRepository()
        
        # Carregar sessão recente se habilitado
        if load_recent and st.session_state.current_session_id is None:
            self._load_recent_session()
    
    def create_new_session(self, title: str = None) -> int:
        """Cria uma nova sessão"""
        if title is None:
            title = f"Conversa {datetime.now().strftime('%d/%m %H:%M')}"
        
        session = self.session_repo.create(title=title)
        st.session_state.current_session_id = session.id
        st.session_state.messages = []
        st.session_state.session_start_time = datetime.now()
        
        print(f"✅ Nova sessão criada: {session.id} - {title}")
        return session.id
    
    def _load_recent_session(self):
        """Carrega a sessão mais recente"""
        recent = self.session_repo.get_recent(limit=1)
        if recent:
            session = recent[0]
            st.session_state.current_session_id = session.id
            st.session_state.messages = [
                {"role": msg.role, "content": msg.content}
                for msg in session.messages
            ]
            print(f"✅ Sessão carregada: {session.id} - {session.title}")
    
    @property
    def messages(self):
        """Retorna mensagens da sessão atual"""
        return st.session_state.messages
    
    @property
    def current_session_id(self) -> Optional[int]:
        """Retorna ID da sessão atual"""
        return st.session_state.current_session_id
    
    def add_message(self, role: str, content: str):
        """Adiciona mensagem em memória e persiste no BD"""
        # Adicionar em memória
        st.session_state.messages.append({"role": role, "content": content})
        
        # Persistir no banco se temos uma sessão ativa
        if st.session_state.current_session_id:
            self.message_repo.create(
                session_id=st.session_state.current_session_id,
                role=role,
                content=content
            )
    
    def clear(self):
        """Limpa mensagens da sessão atual"""
        st.session_state.messages = []
        
        # Atualizar banco se temos sessão
        if st.session_state.current_session_id:
            self.message_repo.delete_by_session(st.session_state.current_session_id)
    
    def save_session(self, title: str = None):
        """Salva a sessão atual com título e duração"""
        if not st.session_state.current_session_id:
            return None
        
        duration = (datetime.now() - st.session_state.session_start_time).total_seconds()
        self.session_repo.update(
            session_id=st.session_state.current_session_id,
            title=title,
            duration=int(duration)
        )
        print(f"✅ Sessão salva: {st.session_state.current_session_id}")
        return st.session_state.current_session_id
    
    def get_all_sessions(self, limit: int = 50) -> List:
        """Retorna todas as sessões"""
        return self.session_repo.get_all(limit=limit)
    
    def get_session_by_id(self, session_id: int):
        """Carrega uma sessão específica"""
        session = self.session_repo.get_by_id(session_id)
        if session:
            st.session_state.current_session_id = session.id
            st.session_state.messages = [
                {"role": msg.role, "content": msg.content}
                for msg in session.messages
            ]
            print(f"✅ Sessão carregada: {session.id}")
        return session
    
    def delete_session(self, session_id: int):
        """Deleta uma sessão"""
        self.session_repo.delete(session_id)
        
        # Se era a sessão atual, limpar estado
        if st.session_state.current_session_id == session_id:
            st.session_state.current_session_id = None
            st.session_state.messages = []
