import sqlite3
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

class Database:
    """Gerenciador de conexão e schema SQLite (Singleton Thread-Safe)"""
    
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    DB_PATH = Path(__file__).parent.parent.parent.parent / "jarvis.db"
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.connection = None
                    self.lock = threading.Lock()
                    self.init_db()
                    Database._initialized = True
    
    def get_connection(self):
        """Retorna conexão com o banco (thread-safe para Streamlit)"""
        with self.lock:
            if self.connection is None:
                self.connection = sqlite3.connect(
                    self.DB_PATH,
                    check_same_thread=False,
                    detect_types=sqlite3.PARSE_DECLTYPES
                )
                # Registrar conversor para datetime
                sqlite3.register_adapter(datetime, lambda val: val.isoformat())
                sqlite3.register_converter("timestamp", lambda val: datetime.fromisoformat(val.decode()))
            return self.connection
    
    def init_db(self):
        """Inicializa o banco de dados e cria schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de sessões
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds INTEGER,
            tags TEXT,
            archived INTEGER DEFAULT 0
        )
        """)
        
        # Tabela de mensagens
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tokens_used INTEGER,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """)
        
        # Tabela de metadados da app
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Criar índices para performance
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_session_id 
        ON messages(session_id)
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_created_at 
        ON sessions(created_at DESC)
        """)
        
        conn.commit()
        print(f"✅ Database inicializado: {self.DB_PATH}")
    
    def close(self):
        """Fecha a conexão"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Optional[Tuple] = None):
        """Executa uma query"""
        try:
            cursor = self.get_connection().cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.get_connection().commit()
            return cursor
        except sqlite3.Error as e:
            print(f"❌ Erro no banco: {e}")
            raise
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None):
        """Busca um registro"""
        cursor = self.get_connection().cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: Optional[Tuple] = None):
        """Busca múltiplos registros"""
        cursor = self.get_connection().cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
