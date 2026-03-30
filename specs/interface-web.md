# 1. Objetivo

Criar uma interface local em Streamlit para o projeto Jarvis, funcionando como alternativa ou complemento ao Telegram, integrando:

AgentController
AgentLoop (ReAct)
MemoryManager
SkillLoader / Router
ToolRegistry

A UI será apenas uma camada de apresentação, sem conter lógica de negócio.


## 2. Estrutura de Projeto (Interface Streamlit)

```
interface/
│
├── main.py                      # Entry point do core (já existente)
├── pyproject.toml
│
├── app/                         # Camada Streamlit
│   ├── streamlit_app.py         # Entry point da UI
│   ├── config.py
│   │
│   ├── components/              # Componentes reutilizáveis
│   │   ├── chat_window.py
│   │   ├── sidebar.py
│   │   ├── message_bubble.py
│   │   └── status_panel.py
│   │
│   ├── state/
│   │   └── session_manager.py   # Controle de st.session_state
│   │
│   ├── services/                # Adaptadores do core
│   │   └── agent_service.py     # Wrapper do AgentController
│   │
│   └── utils/
│       └── formatters.py
│
├── core/                        # (já existente)
│   ├── controller/
│   ├── agent_loop/
│   ├── memory/
│   ├── skills/
│   └── tools/
│
├── data/
│   └── db.sqlite
│
└── .agents/
    └── skills/
```

3. Arquitetura da Integração
3.1 Papel do Streamlit

O Streamlit:

Recebe input do usuário
Chama AgentController
Exibe resposta
Exibe status (iteração, tools usadas)
Permite reset de memória

Ele não executa lógica de ReAct.

3.2 Fluxo
User → Streamlit UI → AgentService → AgentController
      ← Response ← AgentLoop ← MemoryManager


4. Implementação Passo a Passo
PASSO 1 — Instalar Dependências

Se usar uv:

uv add streamlit

Testar:

uv run streamlit hello
PASSO 2 — Criar Entry Point da UI
app/streamlit_app.py
import streamlit as st
from app.services.agent_service import AgentService
from app.state.session_manager import SessionManager
from app.components.chat_window import render_chat
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Jarvis",
    layout="wide"
)

session = SessionManager()
agent = AgentService()

render_sidebar(session)

user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    response = agent.process_message(user_input)
    session.add_message("user", user_input)
    session.add_message("assistant", response)

render_chat(session.messages)
PASSO 3 — Criar Adapter para o Core
app/services/agent_service.py
from core.controller.agent_controller import AgentController

class AgentService:

    def __init__(self):
        self.controller = AgentController()

    def process_message(self, message: str) -> str:
        return self.controller.handle_message(message)

🔎 Estratégia correta:
A UI depende de uma fachada, não diretamente do Loop.

PASSO 4 — Gerenciar Estado da Sessão
app/state/session_manager.py
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
PASSO 5 — Criar Componente de Chat
app/components/chat_window.py
import streamlit as st

def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
PASSO 6 — Criar Sidebar Técnica
app/components/sidebar.py
import streamlit as st

def render_sidebar(session):
    with st.sidebar:
        st.title("Jarvis Control")

        if st.button("Resetar Conversa"):
            session.clear()
            st.rerun()

        st.divider()

        st.markdown("### Status")
        st.write(f"Mensagens na sessão: {len(session.messages)}")
5. Executar o Projeto
uv run streamlit run app/streamlit_app.py
6. Melhorias Técnicas Recomendadas
6.1 Exibir Logs do AgentLoop

Adicionar painel colapsável:

with st.expander("Agent Debug"):
    st.code(loop_logs)

Requer que o AgentLoop retorne metadata estruturada.

6.2 Streaming de Tokens

Para resposta progressiva:

Adaptar AgentController para yield incremental
Usar st.empty() como placeholder
6.3 Exibir Tools Usadas

Exemplo:

st.markdown("**Tools executadas:**")
for tool in response.tools_used:
    st.write(f"- {tool}")
6.4 Multi-Conversation (Produção)

Adicionar:

Selectbox com histórico de conversations
UUID por sessão
Carregamento via MemoryManager
7. Riscos Arquiteturais
Risco	Impacto	Mitigação
Misturar lógica de negócio na UI	Alto	Manter AgentService como única ponte
Travamento por chamada longa do LLM	Médio	Timeout + spinner
Estouro de memória no Streamlit	Médio	Limitar mensagens renderizadas
8. Extensão Futura
Upload de PDF → enviar para Tool
Upload de áudio → Whisper
Toggle de LLM Provider
Painel de Skills carregadas
Modo desenvolvedor (ver Thought/Action/Observation)
9. Resultado Esperado

Você terá:

Interface local elegante
Debug visual do ReAct
Controle manual de sessão
Independência do Telegram
Arquitetura limpa (UI desacoplada do core)