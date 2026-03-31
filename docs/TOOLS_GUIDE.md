# Guia: Sistema de Tools do J.A.R.V.I.S.

## 📋 Visão Geral

O sistema de Tools permite que o J.A.R.V.I.S. rode automaticamente tarefas especializadas baseado na intenção do usuário, sem necessidade de reiniciar a aplicação.

### Componentes Principais

| Componente | Função |
|-----------|--------|
| **ToolLoader** | Carrega todas as tools do diretório `.agents/tools/` |
| **ToolRouter** | Analisa a intenção do usuário e escolhe a tool apropriada |
| **ToolExecutor** | Executa a tool com contexto especializado injetado |

---

## 🚀 Como Funciona (Fluxo)

```
User Input
    ↓
ToolRouter (Análise de Intenção)
    ↓
Tool Encontrada? 
    ├─ SIM → ToolExecutor (Com contexto especializado)
    └─ NÃO → Resposta Normal (AgentController padrão)
```

### Exemplo Prático

**User:** "Qual é a área de um triângulo com base 5 e altura 10?"

1. **Router** analisa → Identifica como `calculator`
2. **Executor** injeta contexto da tool `calculator`
3. **LLM** responde com instruções da tool ativa
4. **Resposta:** "Resultado: 25" (com formatação apropriada)

---

## 📁 Estrutura de Diretórios

```
.agents/tools/
├── calculator/
│   └── tool.md
├── info/
│   └── tool.md
├── web-search/
│   └── tool.md
└── [nova-tool]/
    └── tool.md
```

---

## 📝 Criar uma Nova Tool

### Passo 1: Criar Diretório

```bash
mkdir .agents/tools/minha-tool
```

### Passo 2: Criar `tool.md`

```markdown
---
name: Minha Ferramenta
id: minha-tool
description: Descrição breve da funcionalidade
category: categoria
version: 1.0
---

# Ferramenta: Minha Ferramenta

Instruções detalhadas sobre como essa tool funciona.

## Quando usar:
- Exemplo 1
- Exemplo 2

## Instruções:
1. Passo 1
2. Passo 2

## Formato de resposta:
[Especificar formato]
```

### Passo 3: Ativar

Mude o evento de aplicação. A tool será automaticamente carregada pela próxima requisição

---

## ✅ Verificar Tools Carregadas

### Via Script de Teste

```bash
python test_tools.py
```

Isso valida:
- ✅ Carregamento de todas as tools
- ✅ Parse correto de YAML frontmatter
- ✅ Recuperação de informações
- ✅ Listagem disponível

### Via Python

```python
from core.tools.loader import ToolLoader

# Carregar todas
tools = ToolLoader.load_all_tools()
print(f"Tools: {[t['name'] for t in tools]}")

# Sumário
summary = ToolLoader.get_tool_summary()

# Tool específica
calc = ToolLoader.get_tool_by_id("calculator")
```

---

## 🎯 Usar Tools na Aplicação

### Automático (Padrão)

O sistema roteia automaticamente durante `streamlit run`:

```bash
streamlit run src/app/streamlit_app.py
```

### Desabilitar Tools

No `.env`:

```env
USE_TOOLS=false
```

### Programático

```python
from core.tools.executor import ToolExecutor

# Executar uma tool
response = ToolExecutor.execute(
    tool_id="calculator",
    user_input="Quanto é 10 + 5?",
    llm_handler=controller._get_llm_handler()
)

# Listar todas
tools = ToolExecutor.list_all_tools()

# Info de uma tool
info = ToolExecutor.get_tool_info("info")
```

---

## 🔧 Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `USE_TOOLS` | `true` | Habilita/desabilita roteamento automático |
| `ACTIVE_PROVIDER` | `google` | `google` ou `local` |
| `GOOGLE_API_KEY` | (obrigatório) | Chave API Google |

---

## 🔍 Troubleshooting

### Tools não carregam

```bash
# Verificar estrutura
ls -la .agents/tools/

# Testar loader
python test_tools.py
```

### Erro de YAML Frontmatter

- Certifique-se que começa com `---`
- Use `name:` e `id:` sem aspas
- Não use `:` em valores sem aspas

### Router não roteia corretamente

Verifique que o `id` na tool.md é único e em minúsculas

---

## 📊 Tools Pré-instaladas

| Tool | ID | Descrição |
|-----|-----|-----------|
| **Calculadora** | `calculator` | Operações matemáticas |
| **Informação** | `info` | Explicações e conceitos |
| **Web Search** | `web-search` | Informações atualizadas |

---

## 🚦 Próximos Passos

- [ ] Criar tool de Git Management
- [ ] Criar tool de Code Analysis
- [ ] Integrar persistência de histórico de tools usadas
- [ ] Dashboard de uso de tools
