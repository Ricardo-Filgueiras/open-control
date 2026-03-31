from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Message:
    """Representa uma mensagem na conversa"""
    id: Optional[int] = None
    session_id: Optional[int] = None
    role: Optional[str] = None  # "user" ou "assistant"
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    tokens_used: Optional[int] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "tokens_used": self.tokens_used
        }

@dataclass
class Session:
    """Representa uma sessão de conversa"""
    id: Optional[int] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    tags: Optional[str] = None  # JSON string de tags
    message_count: int = 0
    messages: Optional[List[Message]] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "duration_seconds": self.duration_seconds,
            "tags": self.tags,
            "message_count": self.message_count
        }

@dataclass
class AppMetadata:
    """Metadados da aplicação"""
    key: str
    value: str
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()
