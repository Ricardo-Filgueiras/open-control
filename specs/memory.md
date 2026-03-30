# Sistema de Memória e Persistência

**Versão:** 0.2  
**Status:** Implementação Parcial — In-Memory apenas  
**Stack Principal:** Python + LangChain + SessionManager  
**Responsável:** `SessionManager` em `src/app/state/`  

---

## 1. Resumo Executivo

O módulo de memória gerencia tanto o **histórico conversacional de curto prazo** (sessão Streamlit) quanto será responsável por **persistência em banco de dados** (SQLite) e **gerenciamento de janela de contexto** para impedir estouro de tokens do LLM.

**Estado Atual:** Apenas memória em sessão (v0.2)  
**Estado Planejado:** Persistência SQLite + Window Management (v0.3+)

---

## 2. Contexto e Motivação

### Problema
- LLMs são stateless — esquecem tudo entre chamadas
- Sem persistência, o agente perde utilidade como "Assistente Pessoal"
- Contexto infinito esvazia tokens rapidamente

### Solução Adotada (Atual)
- `SessionManager` mantém histórico em memória durante sessão Streamlit
- Estrutura preparada para futura integração SQLite

### Solução Planejada (v0.3+)
- SQLite para persistência entre sessões
- WAL (Write-Ahead Logging) para concorrência
- `MemoryManager` com truncagem automática de contexto
- Repository Pattern para desacoplamento

---

## 3. Goals (Objetivos Reais)

### Fase Atual (v0.2)

- ✅ **G-01:** Manter histórico em memória durante sessão Streamlit
- ✅ **G-02:** Fornecer interface simples `SessionManager` para storage/retrieval
- ⏳ **G-03:** Estrutura preparada para futuro SQLite (não integrado)

### Fase Futura (v0.3+)

- ⏳ **G-04:** Persistência em SQLite sem perder histórico em memória
- ⏳ **G-05:** Window Management automático (últimas N mensagens)
- ⏳ **G-06:** Repository Pattern desacoplado

---

## 4. Arquitetura Atual (v0.2)

### Fluxo Real (Hoje)

```
USER INPUT (Streamlit)
        ↓
StreamlitApp → AgentService
        ↓
SessionManager.add_message(role, content)
        ↓
Histórico armazenado em st.session_state
        ↓
AgentController recebe mensagens
        ↓
LLM processa + responde
        ↓
SessionManager.add_message(role, response)
        ↓
Renderizar ChatMessages
```

### Classe `SessionManager` (Atual)

**Localização:** [src/app/state/session_manager.py](../src/app/state/session_manager.py)

```python
class SessionManager:
    """Gerencia histórico de conversa em memória."""
    
    def __init__(self):
        self.messages = []  # Histórico completo em memória
        self.conversation_id = str(uuid.uuid4())
    
    def add_message(self, role: str, content: str) -> None:
        """Adiciona mensagem ao histórico."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }
        self.messages.append(message)
    
    def get_messages(self) -> list[dict]:
        """Retorna todas as mensagens da sessão."""
        return self.messages
    
    def clear(self) -> None:
        """Limpa o histórico."""
        self.messages = []
```

### O Que Está Funcionando

| Feature | Status | Notas |
|---------|--------|-------|
| In-Memory Storage | ✅ | Lista Python simples, rápida |
| Add/Get Messages | ✅ | Interface básica funcional |
| Conversation ID | ✅ | UUID gerado por sessão |
| Timestamps | ✅ | Cada mensagem marcada |
| Session State | ✅ | Persiste enquanto Streamlit rodando |

### O Que Ainda Não Existe

| Feature | Status | Prioridade |
|---------|--------|-----------|
| SQLite Integration | ⏳ | Alta |
| MemoryManager Window | ⏳ | Alta |
| Repository Pattern | ⏳ | Média |
| WAL Mode | ⏳ | Média |
| Migration Scripts | ⏳ | Baixa |
| Cleanup/Vacuum | ⏳ | Baixa | 

---

## 5. Usuários e Stakeholders

### Módulos que Consomem SessionManager

| Módulo | Localização | Operação |
|--------|-------------|----------|
| **AgentService** | `src/app/services/agent_service.py` | Lê histórico + adiciona respostas |
| **ChatWindow** | `src/app/components/chat_window.py` | Renderiza histórico |
| **AgentController** | `src/core/controller/agent_controller.py` | Recebe mensagens formatadas |

---

## 6. Modelo de Dados (Atual in-Memory)

### Estrutura de Mensagem

```python
message = {
    "role": "user" | "assistant" | "tool",
    "content": str,  # Texto da mensagem
    "timestamp": datetime
}
```

### Estrutura Esperada (SQLite - v0.3+)

```sql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT,  -- "streamlit", "telegram", etc
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- "user", "assistant", "tool"
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

CREATE INDEX idx_conversation_id ON messages(conversation_id);
CREATE INDEX idx_created_at ON messages(created_at);
```

---

## 7. Fluxo Principal (Happy Path - Atual)

1. Usuário escreve mensagem em Streamlit
2. `AgentService.chat()` captura input
3. `SessionManager.add_message(role="user", content=...)`
4. Histórico atualizado em `st.session_state`
5. `AgentController` recebe últimas mensagens
6. LLM processa e responde
7. `SessionManager.add_message(role="assistant", content=...)`
8. UI re-renderiza com nova mensagem
9. **Sessão encerra → Histórico perdido** ❌

### Fluxo Esperado (Com SQLite - v0.3+)

1-8. Idêntico ao acima
9. `MemoryManager.persist()` salva tudo em SQLite
10. Próxima sessão: `MemoryManager.load_conversation(id)`
11. Histórico restaurado automaticamente ✅

---

## 8. Componentes de Memória (v0.3+)

### Classes Planejadas

```python
class MemoryManager:
    """Facade central para memória."""
    
    async def add_message(self, msg: Message):
        """Salva em memória + SQLite."""
        
    async def get_context_window(self, limit: int = 10) -> list[Message]:
        """Retorna últimas N mensagens (truncadas)."""
        
    async def get_conversation_history(self, conv_id: str):
        """Restaura histórico completo do DB."""

class ConversationRepository:
    """Queries conversações do SQLite."""
    
    async def get_active_conversation(self, user_id: str):
        """Recupera conversa ativa ou cria nova."""

class MessageRepository:
    """Queries mensagens do SQLite."""
    
    async def save_message(self, message: Message):
        """Persiste mensagem."""
        
    async def get_recent_messages(self, conv_id: str, limit: int):
        """Retorna mensagens recentes."""
```

---

## 9. Window Management (Gerenciamento de Contexto - v0.3+)

### Problema
LLM tem limite de tokens (context window). Histórico infinito causa erros.

### Solução Planejada

```python
MEMORY_WINDOW_SIZE = 10  # Últimas 10 mensagens para LLM

#MemoryManager calcular tokens automaticamente
if total_tokens > context_limit:
    messages = truncate_to_window(messages, MEMORY_WINDOW_SIZE)
```

### Comportamento
- **In-Memory:** Todas as mensagens mantidas (histórico completo)
- **Para LLM:** Apenas últimas N mensagens (janela)
- **No DB:** Histórico completo sempre persistido

---

## 10. Configuração de Runtime (Atual)

### Variáveis de Ambiente

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `DB_PATH` | `data/agent.db` | Quando SQLite for integrado |
| `MEMORY_WINDOW_SIZE` | `10` | Mensagens para LLM receber |

### Estrutura de Diretórios

```
/interface
├── data/                    # (Futuro)
│   └── agent.db            # SQLite DB
├── src/
│   └── app/
│       └── state/
│           └── session_manager.py
```

---

## 11. Integração LangChain

### Hoje (v0.2)
```python
# SessionManager retorna dict simples
messages = session_manager.get_messages()

# AgentController converte para LangChain Messages
for msg in messages:
    if msg["role"] == "user":
        langchain_messages.append(HumanMessage(content=msg["content"]))
    elif msg["role"] == "assistant":
        langchain_messages.append(AIMessage(content=msg["content"]))
```

### Futuro (v0.3+)
```python
# MemoryManager retorna já formatado
messages = await memory_manager.get_context_window()
# Já vem como LangChain Message objects
```

---

## 12. Segurança e Privacidade

### Medidas Atuais

- ✅ **Sem senhas cruas:** Nunca logar `GOOGLE_API_KEY` em histórico
- ✅ **Tokens de sessão:** Cada sessão Streamlit é isolada
- ⏳ **Arquivo DB no .gitignore:** Quando SQLite for integrado

### Medidas Planejadas (v0.3+)

- ⏳ Criptografia de dados sensíveis no SQLite
- ⏳ Limpeza automática de chaves de API
- ⏳ Hash de sensitivos: emails, números

---

## 13. Edge Cases e Tratamento de Erros

### Cenários Atuais (v0.2)

| Cenário | Comportamento | Solução |
|---------|--------------|---------|
| Sessão encerra | Histórico perdido | Esperado (MVP) |
| Mensagem vazia | Ignorado | Validação em AgentService |
| Rolle inválido | Aceita qualquer string | Will validate in v0.3 |

### Cenários Futuros (v0.3+)

| Cenário | Comportamento | Solução |
|---------|--------------|---------|
| Corrupção SQLite | Erro ao abrir DB | Rollback automático via WAL |
| Null bytes em msg | Query falha | String sanitize antes de INSERT |
| DB muito grande | Lentidão | VACUUM automático + archiving |

---

## 14. Roadmap de Memória

### v0.2 (Atual - MVP)
- ✅ SessionManager in-memory
- ✅ Add/Get messages básico
- ✅ Integration com Streamlit

### v0.3 (Próxima)
- ⏳ SQLite integration
- ⏳ MemoryManager facade
- ⏳ Repository Pattern
- ⏳ Window Management
- ⏳ Persistência entre sessões

### v0.4+
- ⏳ WAL mode
- ⏳ Criptografia
- ⏳ Auto-cleanup/Vacuum
- ⏳ Search/Query avançado
- ⏳ Backup automático

---

## 15. Como Testar (Atualmente)

```python
# No Streamlit
import sys
sys.path.insert(0, "src")
from app.state.session_manager import SessionManager

manager = SessionManager()
manager.add_message("user", "Olá!")
manager.add_message("assistant", "Bem-vindo!")

messages = manager.get_messages()
print(f"Total de mensagens: {len(messages)}")
print(f"Conversation ID: {manager.conversation_id}")
```

---

## 16. Conclusão

O **Sistema de Memória** está em **duas fases**:

**Fase 1 (Atual - v0.2):** In-Memory puro
- SessionManager funcional
- Histórico durante sessão
- Foundation para expansão ✅

**Fase 2 (Próxima - v0.3):** Persistência + Window Management
- SQLite integrado
- Histórico entre sessões
- Context window automático

A arquitetura está **pronta para escalar sem reengenharia**.

---

**Última Atualização:** Março 30, 2026  
**Responsável:** Core Team JARVIS
