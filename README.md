# J.A.R.V.I.S. — Just A Rather Very Intelligent System

Uma aplicação inteligente de assistência baseada em agentes, com interface web reativa (Streamlit) e suporte a múltiplos provedores de LLM.

## 🚀 Quick Start

### Pré-requisitos

- **Python 3.12+**
- **uv** (gerenciador de ambientes)
- **Google API Key** (para Gemini) ou **Ollama** (local)

### Instalação

```bash
# 1. Clone o repositório
git clone <repository>
cd interface

# 2. Instale as dependências
uv sync

# 3. Configure as variáveis de ambiente
# Criar .env na raiz do projeto:
# GOOGLE_API_KEY=sua_chave_aqui
# ACTIVE_PROVIDER=google  # ou "ollama"
# MODEL_GOOGLE=gemini-1.5-flash
# MODEL_LOCAL=llama3.2:1b
```

### Executar a Aplicação

```bash
# Ativar ambiente virtual (Windows)
.\.venv\Scripts\Activate.ps1

# Executar Streamlit
uv run streamlit run src/app/streamlit_app.py
```

A aplicação abrirá em `http://localhost:8501`

---

## 📋 Estrutura do Projeto

```
interface/
├── main.py                          # Ponto de entrada (legado)
├── README.md                        # Este arquivo
├── pyproject.toml                   # Dependências (uv)
├── requirements.txt                 # Fallback de dependências
│
├── specs/                           # Documentação
│   ├── architecture.md             # Arquitetura detalhada
│   ├── agent-loop.md               # Fluxo do agente (ReAct)
│   ├── interface-web.md            # Especificações da UI
│   ├── memory.md                   # Sistema de memória
│   └── PRD.md                      # Product Requirements
│
└── src/
    ├── app/                         # Interface Streamlit
    │   ├── streamlit_app.py        # Ponto de entrada Streamlit
    │   ├── components/
    │   │   ├── chat_window.py      # Renderização de conversa
    │   │   └── sidebar.py          # Menu lateral
    │   ├── services/
    │   │   └── agent_service.py    # Orquestração do agente
    │   └── state/
    │       └── session_manager.py  # Gerenciamento de sessão
    │
    └── core/                        # Núcleo da lógica
        ├── controller/
        │   └── agent_controller.py # O "cérebro" (ReAct Loop)
        ├── subagents/              # (Em desenvolvimento)
        └── tools/                  # (Em desenvolvimento)
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (`.env`)

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `ACTIVE_PROVIDER` | `google` | Provedor LLM ativo: `google` ou `ollama` |
| `GOOGLE_API_KEY` | *obrigatório* | Sua chave da API Google Generative AI |
| `MODEL_GOOGLE` | `gemini-1.5-flash` | Modelo Google a usar |
| `MODEL_LOCAL` | `llama3.2:1b` | Modelo Ollama a usar |

### Usando Ollama (Modo Local)

1. **Instale Ollama:** https://ollama.com
2. **Execute:** `ollama serve`
3. **Configure `.env`:**
   ```
   ACTIVE_PROVIDER=ollama
   ```

---

## 🎯 Funcionalidades Atuais

### ✅ Implementadas

- Interface web moderna com Streamlit
- Chat interativo com histórico
- Suporte a Google Gemini
- Suporte a modelos locais (Ollama)
- Troca dinâmica de provedores
- Tema visual Stark Industries (futurista)
- Componentes modulares reutilizáveis
- Gerenciamento de sessão

### ⏳ Em Desenvolvimento

- Persistência em banco de dados (SQLite)
- ReAct Loop completo com execução de Tools
- Sistema de Skills dinâmico
- Integração com Telegram
- Autenticação e controle de acesso

---

## 🔧 Desenvolvimento

### Executar em Modo Debug

```bash
# Com recarga automática
uv run streamlit run src/app/streamlit_app.py --logger.level=debug
```

### Adicionar Novas Dependências

```bash
# Adicionar pacote
uv add <nome-do-pacote>

# Sincronizar
uv sync
```

### Estrutura de Código

- **snake_case** para variáveis e funções
- **PascalCase** para classes
- **Type hints** obrigatório
- **Docstrings** em português

---

## 📚 Documentação Detalhada

- **[Architecture](specs/architecture.md)** — Stack técnico, decisões, diagrama de fluxo
- **[Agent Loop](specs/agent-loop.md)** — ReAct Loop (Raciocínio + Ação)
- **[Interface Web](specs/interface-web.md)** — Design e componentes Streamlit
- **[Memory System](specs/memory.md)** — Persistência e janela de contexto
- **[PRD](specs/PRD.md)** — Requisitos de produto

---

## 🐛 Troubleshooting

### "GOOGLE_API_KEY não localizada"

Crie um arquivo `.env` na raiz do projeto:
```
GOOGLE_API_KEY=sua_chave_aqui
```

### "Port 8501 already in use"

```bash
# Use uma porta diferente
uv run streamlit run src/app/streamlit_app.py --server.port=8502
```

### Interface lenta

- Streamlit recarrega a cada input
- Use `@st.cache_resource` para evitar reinicializações
- Considere usar FastAPI para próxima iteração

---

## 🚦 Status do Projeto

- **Versão:** 0.2.0
- **Status:** 🟡 Prototipagem Ativa
- **Última Atualização:** Março 2026
- **Próximo Milestone:** v0.3 com persistência integrada

---

## 📝 Licença

[Especificar licença aqui]

---

## 👥 Contribuição

Ao contribuir:

1. Mantenha a separação entre componentes
2. Adicione type hints
3. Documente mudanças na arquitetura
4. Teste localmente antes de commit

---

**Desenvolvido com ❤️ por JARVIS**
