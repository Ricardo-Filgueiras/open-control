# Guia: Persistência com SQLite

## 📊 Visão Geral

O J.A.R.V.I.S. agora persiste automaticamente todas as conversas em um banco de dados SQLite local. Você pode:

- ✅ Recuperar conversas antigas
- ✅ Criar múltiplas sessões
- ✅ Manter metadados (duração, tags, etc)
- ✅ Pesquisar em histórico

---

## 🗄️ Estrutura do Banco

### Tabelas

| Tabela | Propósito | Campos |
|--------|-----------|--------|
| **sessions** | Conversas | id, title, created_at, updated_at, duration_seconds, tags |
| **messages** | Mensagens individuais | id, session_id, role, content, created_at, tokens_used |
| **app_metadata** | Config da app | key, value, updated_at |

### Arquivo
```
jarvis.db    ← Criado automaticamente na raiz do projeto
```

---

## 🚀 Como Usar

### Automático (Padrão)

Quando você rodar o Streamlit, o SessionManager carrega automaticamente:

```python
# src/app/state/session_manager.py
session = SessionManager()  # Carrega sessão recente automaticamente
```

**Fluxo:**
1. App inicia → Carrega sessão recente
2. User envia mensagem → Salvo em memória + BD
3. User fecha → Sessão fica guardada no BD

### Criar Nova Sessão

```python
session = SessionManager()
session.create_new_session(title="Análise de Projeto X")
```

### Recuperar Sessão Anterior

```python
session = SessionManager()
# Listar disponíveis
sessions = session.get_all_sessions()

# Carregar específica
session.get_session_by_id(session_id=123)
```

### Salvar com Metadados

```python
session = SessionManager()
session.save_session(title="Implementação de Tools")
# Automático: calcula duração, salva no BD
```

### Deletar Sessão

```python
session = SessionManager()
session.delete_session(session_id=123)
```

---

## 💾 Repositórios (Acesso Direto)

Se precisar acesso direto ao BD:

### SessionRepository

```python
from core.database.repositories import SessionRepository

repo = SessionRepository()

# Criar
session = repo.create(title="Minha Conversa", tags=["dev", "debug"])

# Buscar
session = repo.get_by_id(123)
sessions = repo.get_all(limit=50)
recent = repo.get_recent(limit=5)

# Atualizar
repo.update(session_id=123, title="Novo Título", duration=3600)

# Deletar
repo.delete(123)
```

### MessageRepository

```python
from core.database.repositories import MessageRepository

repo = MessageRepository()

# Criar
msg = repo.create(
    session_id=123,
    role="user",
    content="Qual é a data?",
    tokens=150
)

# Buscar
messages = repo.get_by_session(123)
last_10 = repo.get_last_n(session_id=123, n=10)

# Deletar (por sessão)
repo.delete_by_session(123)
```

### MetadataRepository

```python
from core.database.repositories import MetadataRepository

repo = MetadataRepository()

# Set/Get
repo.set("theme", "stark")
theme = repo.get("theme")

# Listar todos
all_meta = repo.get_all()
```

---

## 📝 Modelos de Dados

### Session

```python
from core.database.models import Session

session = Session(
    id=123,
    title="Conversa",
    created_at=datetime.now(),
    updated_at=datetime.now(),
    duration_seconds=3600,
    tags='["dev", "debug"]',
    message_count=15
)
```

### Message

```python
from core.database.models import Message

msg = Message(
    id=1,
    session_id=123,
    role="user",
    content="Olá!",
    created_at=datetime.now(),
    tokens_used=10
)
```

---

## 🧪 Testar

Execute o script de validação:

```bash
python test_database.py
```

Isso valida:
- ✅ Criação de sessões
- ✅ Operações com mensagens
- ✅ Recuperação de histórico
- ✅ Listagem de sessões
- ✅ Metadados

---

## 🔧 Configuração

No `.env`:

```env
# Padrão
DB_PATH=jarvis.db

# (Futuro) Suporte a múltiplos provedores
DB_PROVIDER=sqlite  # ou "postgres", "mysql"
```

---

## 📊 Queries SQL Úteis

### Listar todas as sessões com contagem de mensagens

```sql
SELECT 
    s.id, 
    s.title, 
    COUNT(m.id) as msg_count,
    s.duration_seconds,
    s.created_at
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
WHERE s.archived = 0
GROUP BY s.id
ORDER BY s.updated_at DESC;
```

### Buscar mensagens contendo texto

```sql
SELECT s.title, m.role, m.content, m.created_at
FROM messages m
JOIN sessions s ON m.session_id = s.id
WHERE m.content LIKE '%texto%'
ORDER BY m.created_at DESC;
```

### Tempo total gasto em conversas

```sql
SELECT 
    SUM(duration_seconds) / 3600.0 as horas_totais,
    COUNT(*) as total_sessoes
FROM sessions
WHERE archived = 0;
```

---

## 🐛 Troubleshooting

### Erro "database is locked"

SQLite tem limite de escrita. Se multi-thread:
```python
# Adicione timeout
conn = sqlite3.connect("jarvis.db", timeout=10)
```

### Recuperar histórico perdido

Sempre há backup em `jarvis.db`. Use SQL direto:

```bash
sqlite3 jarvis.db ".dump" > backup.sql
```

### Limpar banco (CUIDADO!)

```bash
rm jarvis.db
# Será recriado na próxima execução
```

---

## 🚀 Próximas Funcionalidades

- [ ] Busca full-text em mensagens
- [ ] Export de sessões em JSON/PDF
- [ ] Sincronização em nuvem (opcional)
- [ ] Backup automático
- [ ] Analytics de uso
