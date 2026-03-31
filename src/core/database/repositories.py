import json
from datetime import datetime
from typing import List, Optional
from core.database.database import Database
from core.database.models import Session, Message, AppMetadata

class SessionRepository:
    """CRUD para sessions"""
    
    def __init__(self):
        self.db = Database()
    
    def create(self, title: str, tags: Optional[List[str]] = None) -> Session:
        """Cria uma nova sessão"""
        tags_json = json.dumps(tags) if tags else "[]"
        now = datetime.now()
        
        cursor = self.db.execute(
            """INSERT INTO sessions (title, created_at, updated_at, tags)
               VALUES (?, ?, ?, ?)""",
            (title, now, now, tags_json)
        )
        
        session = Session(
            id=cursor.lastrowid,
            title=title,
            created_at=now,
            updated_at=now,
            tags=tags_json
        )
        print(f"✅ Sessão criada: '{title}' (ID: {session.id})")
        return session
    
    def get_by_id(self, session_id: int) -> Optional[Session]:
        """Busca sessão por ID"""
        row = self.db.fetch_one(
            """SELECT id, title, created_at, updated_at, duration_seconds, tags
               FROM sessions WHERE id = ?""",
            (session_id,)
        )
        
        if not row:
            return None
        
        session = Session(
            id=row[0],
            title=row[1],
            created_at=row[2],
            updated_at=row[3],
            duration_seconds=row[4],
            tags=row[5]
        )
        
        # Carrega mensagens
        session.messages = MessageRepository().get_by_session(session_id)
        session.message_count = len(session.messages)
        
        return session
    
    def get_all(self, limit: int = 50, archived: bool = False) -> List[Session]:
        """Lista todas as sessões"""
        query = "SELECT id, title, created_at, updated_at, duration_seconds, tags FROM sessions"
        query += " WHERE archived = 0" if not archived else ""
        query += " ORDER BY updated_at DESC LIMIT ?"
        
        rows = self.db.fetch_all(query, (limit,))
        
        sessions = []
        for row in rows:
            session = Session(
                id=row[0],
                title=row[1],
                created_at=row[2],
                updated_at=row[3],
                duration_seconds=row[4],
                tags=row[5]
            )
            # Contar mensagens
            msg_count = self.db.fetch_one(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (session.id,)
            )
            session.message_count = msg_count[0] if msg_count else 0
            sessions.append(session)
        
        return sessions
    
    def update(self, session_id: int, title: Optional[str] = None, duration: Optional[int] = None):
        """Atualiza uma sessão"""
        now = datetime.now()
        
        if title:
            self.db.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, now, session_id)
            )
        
        if duration is not None:
            self.db.execute(
                "UPDATE sessions SET duration_seconds = ?, updated_at = ? WHERE id = ?",
                (duration, now, session_id)
            )
    
    def delete(self, session_id: int):
        """Deleta uma sessão (soft delete)"""
        self.db.execute(
            "UPDATE sessions SET archived = 1 WHERE id = ?",
            (session_id,)
        )
        print(f"✅ Sessão {session_id} arquivada")
    
    def get_recent(self, limit: int = 5) -> List[Session]:
        """Busca sessões recentes"""
        return self.get_all(limit=limit, archived=False)

class MessageRepository:
    """CRUD para messages"""
    
    def __init__(self):
        self.db = Database()
    
    def create(self, session_id: int, role: str, content: str, tokens: Optional[int] = None) -> Message:
        """Cria uma nova mensagem"""
        now = datetime.now()
        
        cursor = self.db.execute(
            """INSERT INTO messages (session_id, role, content, created_at, tokens_used)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, role, content, now, tokens)
        )
        
        message = Message(
            id=cursor.lastrowid,
            session_id=session_id,
            role=role,
            content=content,
            created_at=now,
            tokens_used=tokens
        )
        return message
    
    def get_by_session(self, session_id: int) -> List[Message]:
        """Busca todas as mensagens de uma sessão"""
        rows = self.db.fetch_all(
            """SELECT id, session_id, role, content, created_at, tokens_used
               FROM messages WHERE session_id = ? ORDER BY created_at ASC""",
            (session_id,)
        )
        
        messages = []
        for row in rows:
            msg = Message(
                id=row[0],
                session_id=row[1],
                role=row[2],
                content=row[3],
                created_at=row[4],
                tokens_used=row[5]
            )
            messages.append(msg)
        
        return messages
    
    def get_last_n(self, session_id: int, n: int = 10) -> List[Message]:
        """Busca últimas N mensagens"""
        rows = self.db.fetch_all(
            """SELECT id, session_id, role, content, created_at, tokens_used
               FROM messages WHERE session_id = ? 
               ORDER BY created_at DESC LIMIT ?""",
            (session_id, n)
        )
        
        messages = []
        for row in reversed(rows):  # Reverter para ordem cronológica
            msg = Message(
                id=row[0],
                session_id=row[1],
                role=row[2],
                content=row[3],
                created_at=row[4],
                tokens_used=row[5]
            )
            messages.append(msg)
        
        return messages
    
    def delete_by_session(self, session_id: int):
        """Deleta todas as mensagens de uma sessão"""
        self.db.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (session_id,)
        )

class MetadataRepository:
    """CRUD para app metadata"""
    
    def __init__(self):
        self.db = Database()
    
    def set(self, key: str, value: str):
        """Define um valor de metadado"""
        existing = self.db.fetch_one(
            "SELECT key FROM app_metadata WHERE key = ?",
            (key,)
        )
        
        now = datetime.now()
        if existing:
            self.db.execute(
                "UPDATE app_metadata SET value = ?, updated_at = ? WHERE key = ?",
                (value, now, key)
            )
        else:
            self.db.execute(
                "INSERT INTO app_metadata (key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, now)
            )
    
    def get(self, key: str) -> Optional[str]:
        """Busca um valor de metadado"""
        row = self.db.fetch_one(
            "SELECT value FROM app_metadata WHERE key = ?",
            (key,)
        )
        return row[0] if row else None
    
    def get_all(self) -> dict:
        """Busca todos os metadados"""
        rows = self.db.fetch_all("SELECT key, value FROM app_metadata")
        return {row[0]: row[1] for row in rows}
