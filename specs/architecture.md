# Arquitetura do Projeto: JARVIS

**Versão:** 0.2  
**Status:** Implementação Ativa — UI Streamlit  
**Stack Principal:** Python 3.12 + LangChain + Streamlit  
**Paradigma:** Orientação a Objetos  
**Estilo:** Monolito Modular com UI Reativa  

---

# 1. Propósito do Sistema

O JARVIS é um sistema de assistência inteligente baseado em agentes, atualmente operando com interface web interativa via **Streamlit**.

Seu objetivo é combinar:

- Controle determinístico e acionável do fluxo
- Integração com múltiplos provedores de LLM (Google Gemini, Ollama)
- Persistência local de contexto e histórico
- Interface reativa com estética Stark Industries
- Gerenciamento de sessão e estado de conversação

A arquitetura separa explicitamente:

> **Controle da Interface (Streamlit)** ≠ **Lógica de Agente (Controller)** ≠ **Serviços (Agent Service)**

---

## 2. Status Atual (Iteração Ativa)

Esta seção documenta o **estado real implementado** do projeto, não aspiracional.

### O Que Está Funcionando

- ✅ Interface Streamlit com tema Stark Industries
- ✅ Suporte a múltiplos provedores LLM (Gemini, Ollama)
- ✅ Gerenciamento de sessão e histórico de conversação
- ✅ Componentes modulares (chat window, sidebar, services)
- ✅ Mudança dinâmica de provedores via UI
- ✅ Persistência de estado em memória da sessão

### O Que Ainda Não Está Pronto

- ⏳ Persistência em banco de dados (SQLite preparado, não integrado)
- ⏳ Sistema de Tools/Skills
- ⏳ ReAct Loop com execução de ações
- ⏳ Integração com Telegram (aiogram depende de estrutura backend)
- ⏳ Autenticação e Segurança de Acesso
- ⏳ Backend FastAPI centralizado

---

### Tabela de Requisitos (Prioridade Real)

| Requisito | Status | Tipo | Prioridade | Notas |
|------------|--------|------|------------|-------|
| Interface Web Funcional | ✅ | Não-funcional | Crítica | Streamlit com renderização reativa completa. |
| Multi-Provider LLM | ✅ | Funcional | Crítica | Gemini + Ollama suportados, seleção dinâmica. |
| Gerenciamento de Sessão | ✅ | Funcional | Crítica | SessionManager mantém estado entre interações. |
| Persistência Local (SQLite) | ⏳ | Funcional | Alta | Estrutura pronta, não integrada. |
| Sistema de Componentes | ✅ | Não-funcional | Crítica | Modularização em chat_window, sidebar, services. |
| ReAct Loop Básico | ⏳ | Funcional | Alta | Raciocínio presente, execução de tools não. |
| Backend FastAPI | ⏳ | Não-funcional | Média | Planejado para multi-interface. |
| Telegram Bot | ⏳ | Funcional | Média | Depende de backend centralizado. |

---
## 3. Stack Técnico (Implementado)

Esta seção documenta as tecnologias **atualmente em uso** no projeto.

### Stack Oficial

| Componente | Tecnologia | Status | Notas |
|------------|------------|--------|-------|
| **Linguagem Principal** | **Python 3.12+** | ✅ | Tipagem moderna, async support, excelente para IA. |
| **Gerenciador de Dependências** | **uv** | ✅ | Especificado em `pyproject.toml`, ambientes reprodutíveis. |
| **Paradigma Arquitetural** | **Orientação a Objetos (POO)** | ✅ | AgentController, AgentService, SessionManager estruturados. |
| **Framework Web (Atual)** | **Streamlit** | ✅ | Interface reativa sem necessidade de JavaScript. |
| **Integração LLM Primária** | **LangChain + Google Gemini** | ✅ | Via `langchain-google-genai`, modelo padrão. |
| **Integração LLM Secundária** | **LangChain + Ollama** | ✅ | Via `langchain-ollama`, suporte local opcional. |
| **Backend (Futuro)** | **FastAPI** | ⏳ | Preparado nas dependências, não integrado. |
| **Interface Bot** | **aiogram** | ⏳ | Nas dependências, aguardando backend centralizado. |
| **Persistência** | **SQLite + aiosqlite** | ⏳ | Estrutura preparada, não integrada. |

### Estrutura de Componentes (Atual)

```
src/
├── app/                          # Interface e renderização
│   ├── streamlit_app.py         # Ponto de entrada Streamlit
│   ├── components/
│   │   ├── chat_window.py       # Renderização de conversa
│   │   └── sidebar.py           # Menu lateral dinâmico
│   ├── services/
│   │   └── agent_service.py     # Orquestração do agente
│   └── state/
│       └── session_manager.py   # Gerenciamento de sessão
│
└── core/                         # Núcleo da lógica
    ├── controller/
    │   └── agent_controller.py  # Cérebro (ReAct Loop)
    ├── subagents/              # Estrutura para futuros sub-agentes
    └── tools/                  # Estrutura para execução de tools
```

### Princípios de Arquitetura (Mantidos)

1. ✅ **Abstração de Provider** — AgentController independente de LLM específico.
2. ✅ **Separação de Responsabilidades** — Interface ≠ Lógica ≠ Persistência.
3. ✅ **Estado Centralizado** — SessionManager como fonte de verdade.
4. ✅ **Escalabilidade** — Estrutura preparada para Tools e SubAgents.
5. ⏳ **Logs Estruturados** — Ainda não implementado.

---

### Direção Evolutiva Prevista

A arquitetura deve permitir futura adição de:

- Sistema de Skills (Hot Reload).
- ReAct Loop completo com execução de Tools.
- Multimodalidade (STT/TTS).
- Multi-provider dinâmico.
- Execução paralela controlada.

Sem necessidade de reescrita do núcleo atual.

---
## 4. Infraestrutura e Deploy (Fase MVP do Agente Central)

Esta seção define o ambiente oficial de execução e o modelo de gerenciamento do processo na fase inicial do projeto.

O objetivo é manter simplicidade operacional, previsibilidade e facilidade de desenvolvimento local.

---

### Ambiente de Execução

| Item | Definição | Observações |
|------|-----------|-------------|
| **Sistema Operacional** | Windows (Host Local) | Execução direta na máquina do desenvolvedor/usuário. |
| **Execução do LLM** | Ollama (local) | Serviço rodando localmente, acessível via HTTP (`localhost`). |
| **Banco de Dados** | SQLite (arquivo local) | Persistido em diretório interno do projeto (`/data`). |
| **Modo de Execução** | Terminal (CLI) | Inicialização manual durante fase de desenvolvimento. |

---

### Process Management

| Item | Definição | Justificativa |
|------|-----------|---------------|
| **Gerenciamento de Ambiente** | `uv` | Garante isolamento de dependências e execução consistente. |
| **Comando Oficial de Execução** | `uv run main.py` | Executa dentro do ambiente virtual controlado. |
| **Hot Reload (Opcional)** | Watchdog ou equivalente | Pode ser utilizado durante desenvolvimento para reiniciar automaticamente o processo ao detectar mudanças no código. |
| **Gerenciamento de Processo** | Manual (MVP) | Nesta fase, não há necessidade de supervisores como systemd, PM2 ou Docker. |

---

### Estrutura de Diretórios Recomendada

```
/project-root
│
├── main.py
├── /core
├── /providers
├── /memory
├── /interface
├── /data
│ └── agent.db
└── pyproject.toml
```


---
## 4. Fluxo de Execução Atual (Diagrama Lógico)

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT APP (UI)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ render_sidebar() → Seleção de Provider e Configurações   │   │
│  │ render_chat()   → Exibição de histórico e input          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────┬────────────────────────────────────────────┘
                      │ session_state
                      ▼
        ┌─────────────────────────────┐
        │   AgentService              │
        │  (Orquestração)             │
        │  - usa SessionManager       │
        │  - chama Controller         │
        └────────┬────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │   AgentController           │
        │  (Lógica de Raciocínio)     │
        │  - seleciona provider       │
        │  - constrói prompts         │
        │  - chama LLM                │
        └────────┬────────────────────┘
                 │
        ┌────────┴──────────┐
        ▼                   ▼
   ┌─────────────┐   ┌──────────────┐
   │   Gemini    │   │   Ollama     │
   │  (Google)   │   │   (Local)    │
   └─────────────┘   └──────────────┘
        │                   │
        └────────┬──────────┘
                 ▼
        ┌─────────────────────────────┐
        │    Resposta do Modelo       │
        └─────────────────────────────┘
```

---

## 5. Ambiente de Execução (Atual)

| Item | Definição | Status |
|------|-----------|--------|
| **Sistema Operacional** | Windows (host local) | ✅ Testado |
| **Execução do LLM Primário** | API Google (Cloud) | ✅ Ativo |
| **Execução do LLM Secundário** | Ollama (local, opcional) | ✅ Suportado |
| **Banco de Dados** | SQLite (arquivo local) | ⏳ Preparado |
| **Framework Web** | Streamlit (CLI local) | ✅ Ativo |
| **Modo de Execução** | `uv run streamlit run src/app/streamlit_app.py` | ✅ Funcional |

### Comando de Execução

```bash
# Ativar ambiente virtual (Windows)
.\.venv\Scripts\Activate.ps1

# Executar aplicação
uv run streamlit run src/app/streamlit_app.py
```

A aplicação abrirá em `http://localhost:8501`.

---

## 6. Camada de Persistência (Em Desenvolvimento)

### Estado Atual

- **Persistência em Memória:** ✅ SessionManager mantém histórico na sessão Streamlit
- **Persistência em Arquivo (SQLite):** ⏳ Estrutura criada, não integrada
- **Limpeza de Contexto:** Automatic com limite de tokens via LangChain

### Estrutura Preparada para Futura Integração

```python
# Exemplo: Como será integrada (futuro)
async def save_message(session_id, role, content):
    async with aiosqlite.connect("data/agent.db") as db:
        await db.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        await db.commit()
```

---

## 7. Direção Evolutiva (Roadmap)

### Próxima Iteração (v0.3)

- [ ] Integrar SQLite como persistência primária
- [ ] Implementar ReAct Loop com Tool Execution
- [ ] Adicionar primeiro Tool (ex: web search)
- [ ] Logs estruturados com observabilidade

### Iterações Futuras (v0.4+)

- [ ] Backend FastAPI centralizado
- [ ] Integração com Telegram via aiogram
- [ ] Sistema dinâmico de Skills
- [ ] Suporte a múltiplos agentes
- [ ] Dashboard de monitoramento
- [ ] Containerização com Docker

---

## 8. Desvios do Plano Original (Documentados)

| Planejado | Implementado | Razão |
|-----------|--------------|-------|
| FastAPI Backend Central | Streamlit UI Direta | Prototipagem rápida, iteração ágil |
| Vanilla JS / React | Streamlit Components | Eliminação de overhead frontend |
| Ollama como Padrão | Google Gemini como Padrão | Performance + custo-benefício |
| Telegram + Web | Apenas Streamlit | Foco em core antes de multi-interface |
| SQLite Integrado | SQLite Preparado | Priorização de funcionalidade |

**Conclusão:** Estes desvios aceleram a validação do conceito sem comprometer a arquitetura.

---

## 9. Como Contribuir e Manter

### Convenções Gerais

1. **Nomes de Variáveis:** `snake_case` para Python
2. **Nomes de Classes:** `PascalCase`
3. **Métodos Privados:** Prefix `_`
4. **Docstrings:** Google-style, obrigatório para classes e métodos públicos
5. **Type Hints:** Obrigatório para todas as funções

### Estrutura de Pull Requests

Ao adicionar novas funcionalidades:

1. Atualize o documento de requisitos ([specs/PRD.md](specs/PRD.md))
2. Mantenha a separação entre Interface, Serviço e Lógica
3. Não acople código a provedores específicos (ex: Gemini hardcoded)
4. Teste localmente antes de fazer commit
5. Documente mudanças na arquitetura

---

## 10. Troubleshooting & Requisitos de Runtime

### Erro: "GOOGLE_API_KEY não localizada"

**Solução:**
```bash
# Criar arquivo .env na raiz do projeto
GOOGLE_API_KEY=sua_chave_aqui
ACTIVE_PROVIDER=google  # ou "ollama"
MODEL_GOOGLE=gemini-1.5-flash
MODEL_LOCAL=llama3.2:1b
```

### Erro: "Ollama não está respondendo"

**Solução:**
1. Certifique-se que Ollama está rodando: `ollama serve`
2. Teste a conexão: `curl http://localhost:11434`
3. Volte ao provedor Google no `.env`

### Performance em Streamlit

- Streamlit recarrega o script inteiro a cada mudança de input
- `@st.cache_resource` evita reinicializações desnecessárias (já usado)
- Para otimizações, veja [src/app/streamlit_app.py](src/app/streamlit_app.py#L35)

---

## 11. Dependências Críticas

```plaintext
Python 3.12+              # Linguagem base
langchain>=0.1.0          # Orquestração LLM
langchain-google-genai    # Integração Gemini
langchain-ollama          # Integração modelo local
streamlit>=1.55.0         # Interface web
fastapi>=0.135.2          # (Para futuro backend)
aiosqlite>=0.22.1         # (Para futura persistência)
python-dotenv             # Configuração via .env
```

Instalar com:
```bash
uv sync
```

---

## 12. Conclusão

Este documento reflete o **estado real da implementação em março de 2026**. A arquitetura é suficientemente flexível para suportar as evoluções planejadas sem reescrita do núcleo.

**Status:** 🟡 **Prototipagem Ativa** — UI funcional, core expandindo.  
**Próximo Marco:** Integração de persistência + Tools básicos.

---

**Última Atualização:** Março 30, 2026  
**Responsável:** Equipe de Desenvolvimento JARVIS