# Agent Loop (Reasoning Engine)

**Versão:** 0.2  
**Status:** Implementação Básica — Raciocínio sem Ação  
**Responsável:** `AgentController` em `src/core/controller/`  
**Stack Base:** Python + LangChain  

---

## 1.1 Visão Geral (Estado Atual)

O **Agent Loop** é o cérebro do JARVIS. Atualmente implementa:

- ✅ **Raciocínio:** Chat com LLM mantendo historico
- ✅ **Persona Stark:** Polida, leal, com sarcasmo britânico
- ✅ **Múltiplos Provedores:** Google Gemini + Ollama
- ✅ **Gestão de Contexto:** Via LangChain Messages
- ⏳ **ReAct Loop:** Estrutura planejada, ainda não implementada
- ⏳ **Execução de Tools:** Sistema de ferramentas em desenvolvimento
- ⏳ **ToolRegistry:** Não existe ainda

**Padrão Aspiracional (Next):** ReAct (Reasoning + Acting)
```
Thought → Action (Tool Call) → Observation → Thought → ... → Final Answer 
```

---

## 1.2 Papel na Arquitetura (Atual)

O Agent Loop:

- É invocado pelo `AgentController` (localização: [src/core/controller/agent_controller.py](../src/core/controller/agent_controller.py))
- Recebe mensagens do `SessionManager/AgentService`
- Retorna resposta final para renderização Streamlit
- Não acessa banco de dados diretamente
- Não conhece Telegram (interface agnóstica ✅)
- Usa LangChain para abstração de LLM

## 1.3 Implementação Atual (AgentController)

### Fluxo Simplificado (Hoje)

```
USER INPUT (Streamlit)
        ↓
AgentService.chat()
        ↓
AgentController._get_llm()  
        ↓
ChatGoogleGenerativeAI ou ChatOllama
        ↓
LLM Response (Direto, sem tools)
        ↓
Renderizar em Streamlit
```

### Classe: `AgentController`

**Localização:** [src/core/controller/agent_controller.py](../src/core/controller/agent_controller.py)

```python
class AgentController:
    """O cérebro de raciocínio (sem execução de tools por enquanto)."""
    
    def __init__(self):
        self.system_prompt = """Você é o J.A.R.V.I.S...."""
        self.provider = os.getenv("ACTIVE_PROVIDER", "google")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model_google = os.getenv("MODEL_GOOGLE", "gemini-1.5-flash")
        self.model_local = os.getenv("MODEL_LOCAL", "llama3.2:1b")
    
    def _get_llm(self):
        """Seleciona o provedor: Gemini ou Ollama."""
        if self.provider == "google":
            return ChatGoogleGenerativeAI(model=self.model_google)
        elif self.provider == "ollama":
            return ChatOllama(model=self.model_local)
    
    async def chat(self, messages: list[BaseMessage]) -> str:
        """Executa o raciocínio (sem tools ainda)."""
        llm = self._get_llm()
        
        system_message = SystemMessage(content=self.system_prompt)
        full_messages = [system_message] + messages
        
        response = await llm.ainvoke(full_messages)
        return response.content
```

### O Que Está Funcionando

| Feature | Status | Notas |
|---------|--------|-------|
| Seleção de Provider | ✅ | Google Gemini (padrão) + Ollama (alternativa) |
| System Prompt Injetado | ✅ | Persona JARVIS mantida |
| Histórico em Memória | ✅ | SessionManager armazena mensagens |
| Response Básica | ✅ | LLM responde, sem ferramentas |
| Async/Await | ✅ | Integrado com LangChain |

### O Que Falta (v0.3+)

| Feature | Status | Prioridade |
|---------|--------|-----------|
| ToolRegistry | ⏳ | Alta |
| ReAct Loop Explícito | ⏳ | Alta |
| Tool Execution | ⏳ | Alta |
| Max Iterations Control | ⏳ | Alta |
| Execution Logging | ⏳ | Média |
| Tool Validation | ⏳ | Média |
| Error Recovery | ⏳ | Média |

---

## 1.4 Modelo Conceitual (ReAct — Próxima Iteração)
``` 
Thought → Action (Tool Call) → Observation → Thought → ... → Final Answer 
```

### Estados possíveis por iteração:

| Estado | Origem | Próxima Ação |
|--------|--------|--------------|
| Final Answer | LLM | Encerrar loop |
| Tool Call | LLM | Executar Tool |
| Erro de Tool | Runtime | Retornar como Observation |
| JSON inválido | Parsing | Solicitar correção ao LLM |

---

## 1.4 Estrutura Base com LangChain

A implementação utilizará:

- `ChatModel` (LLM provider abstrato)
- `StructuredTool` (LangChain Tools)
- `AgentExecutor`
- `MessagesPlaceholder`
- `Tool Invocation Schema`

### Estratégia

Não usar agentes autônomos “black box” do LangChain.

Será utilizado:

- Agent customizado baseado em `Runnable`
- Controle explícito de iterações
- Controle manual de `max_iterations`
- Interceptação de Tool Calls

- Interceptação de Tool Calls

Isso evita comportamento imprevisível.

---

## 1.5 Interface Pública (v0.3+)

### Classe: `AgentLoop`

```python
class AgentLoop:
    """ReAct Loop completo com tool execution (Futuro)."""

    async def run(
        self,
        messages: list[BaseMessage],
        tools: list[BaseTool],
        skill_context: str | None = None,
    ) -> AgentResult:
        """Executa o loop ReAct com limite de iterações."""
        ...
```

### Parâmetros Esperados (v0.3+)

| Parâmetro     | Tipo | Descrição                               |
| ------------- | ---- | --------------------------------------- |
| messages      | list | Histórico filtrado pelo MemoryManager   |
| tools         | list | Tools registradas ativas                |
| skill_context | str  | Prompt injetado dinamicamente por Skill |

### Resultado Esperado (v0.3+)

```python
@dataclass
class AgentResult:
    final_answer: str
    iterations: int
    tool_calls: list[ToolExecutionLog]
    status: Literal["success", "max_iterations", "error"]

@dataclass
class ToolExecutionLog:
    iteration: int
    tool_name: str
    input_args: dict
    output: str
    execution_time_ms: int
```

Variável configurável:

```python
MAX_ITERATIONS = 5

# Proteção contra loops infinitos
if iteration_count > MAX_ITERATIONS:
    break
```

---

## 1.6 Ciclo ReAct Esperado (v0.3+)

```
[ITERATION 1]
Thought: O usuário quer saber a data de hoje. Preciso chamar uma tool.
Action: get_date_tool
Args: {}
Observation: 2026-03-30

[ITERATION 2]
Thought: Agora tenho a data. Posso formular a resposta final.
Final Answer: Sir, a data de hoje é 30 de março de 2026.

Status: success
Iterations: 2
```

---

## 1.7 Proteções & Riscos Técnicos

### Proteções Implementadas (v0.3+)

| Proteção | Descrição |
|----------|-----------|
| **Max Iterations** | Limite duro de 5 iterações previne loops infinitos |
| **Tool Validation** | Schema JSON validado antes da execução |
| **Error Encapsulation** | Erros de tool retornam como Observation, não quebram loop |
| **No Parallelism** | Tools executadas sequencialmente para determinismo |
| **LLM Timeout** | Limite de 120s na chamada ao LLM |

| Timeout LLM | 120s máximo | Evita bloqueio indefinido |

### Riscos Técnicos (Documento para Futuro)

| Risco | Impacto | Mitigação Planejada |
|-------|---------|-------------------|
| **Loops Infinitos** | Alto | Limite duro de MAX_ITERATIONS |
| **Recursão de Tools** | Alto | Whitelist + validação de schema |
| **Prompt Injection** | Alto | System boundary + tool whitelist |
| **Context Overflow** | Médio | Truncagem via SessionManager |
| **Bad Tool Impl** | Médio | Try/Except em cada tool |

---

## 1.8 Estratégia Anti-Alucinação (v0.3+)

Princípios que serão implementados:

1. **Nunca confiar em declarações sem execução real**
2. **Toda chamada deve executar a tool realmente**
3. **Erros retornam como Observation, não quebram o loop**
4. **LLM nunca pode anunciar execução sem tool**
5. **Logs estruturados para auditoria completa**

---

## 1.9 Próximas Etapas (Roadmap)

### v0.3 — ReAct Loop Básico

- [ ] Implementar `ToolRegistry`
- [ ] Criar estrutura `BaseTool` abstrata
- [ ] Adicionar primeiro Tool de teste (ex: `get_current_time`)
- [ ] Implementar AgentLoop com max_iterations
- [ ] Adicionar logging estruturado

### v0.4+ — Expansão de Capacidades

- [ ] Tools para web search
- [ ] Tools para file operations
- [ ] Tools para consultas SQL
- [ ] Sistema de Skills dinâmico
- [ ] Dashboard de observabilidade

---

## 1.10 Conclusão (Estado Atual)

O **Agent Loop** é uma estrutura em duas fases:

**Fase 1 (Atual - v0.2):** Raciocínio puro sem ferramentas
- LLM recebe histórico e context
- Responde diretamente
- Persona Stark mantida
- Foundation para próximas fases ✅

**Fase 2 (Próxima - v0.3):** ReAct Loop com Tool Execution
- Control explícito de iterações
- Execução real de ferramentas
- Logging estruturado
- Anti-alucinação garantida

A arquitetura está **pronta para expansão sem reescrita do núcleo**.

---

**Última Atualização:** Março 30, 2026  
**Responsável:** Core Team JARVIS