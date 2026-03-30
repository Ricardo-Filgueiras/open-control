# Arquitetura do Projeto: JARVIS

**Versão:** 0.1  
**Status:** Definição Arquitetural Atual  
**Stack Principal:** Python + LangChain  
**Paradigma:** Orientação a Objetos  
**Estilo:** Monolito Modular Orquestrado  
---

Agent Central — Contexto, Objetivos e Requisitos

Versão: 1.0
Status: Draft Adaptado ao Core Atual
Escopo: Sistema central local baseado em AgentLoop + Skill System + Memory + Multi-Interface (Telegram & Web Interface)

2. Contexto e Motivação
Problema

Soluções baseadas em agentes hospedados em nuvem:

Exigem exposição de dados privados.
Impõem custos recorrentes variáveis.
Limitam controle sobre extensões e “skills”.
Criam dependência estrutural (lock-in) de fornecedores.

Além disso, arquiteturas web-based adicionam:

Camadas desnecessárias de UI.
Complexidade de deploy.
Superfície ampliada de ataque.
Evidências
Experimentos prévios com arquiteturas externas funcionaram, porém:
Alto acoplamento com infra de terceiros.
Baixo controle sobre ciclo de vida das skills.
Dificuldade de manter governança arquitetural.

O modelo atual baseado em:

AgentLoop (ReAct)
Skill Management via FileSystem
Memory SQLite local
Execução via Terminal (uv run main.py)

resolve esses pontos mantendo simplicidade operacional.

Por que agora

A maturidade de:

LLMs eficientes (Gemini / DeepSeek)
API do Telegram via aiogram
SQLite assíncrono (aiosqlite)
Hot-reload de Skills via filesystem

permite consolidar um Agente Central Local, modular e sob controle total.

3. Goals (Objetivos)
G-01 — Experiência Multi-Interface Unificada

O JARVIS deve operar através de múltiplas camadas de entrada/saída, mantendo o mesmo cérebro e memória.

- Interface Web: HUD Futurista (Premium UI/UX) para interação local e visual.
- Interface Telegram: Bot persistente para suporte remoto e notificações.
- Dispatcher Central: Orquestrador que entrega a resposta no canal correto.

- Polling/Webhook via aiogram para Telegram.
- Websocket/REST para Interface Web.
- Sinalização de processamento em tempo real (typing... ou animando HUD).
G-02 — Engine de Raciocínio Determinístico (AgentLoop)

O núcleo deve:

Executar padrão ReAct (Thought → Action → Observation → Answer)
Respeitar MAX_ITERATIONS
Logar cada etapa do ciclo
Impedir loops infinitos e billing excessivo
G-03 — Provider Agnóstico

Permitir troca de LLM via ProviderFactory.

Critério:

Alterar config "provider": "gemini" | "deepseek" sem tocar no core.
Fallback automático em caso de erro 5xx.
G-04 — Persistência Conversacional Local
Armazenar histórico em SQLite.
Usar MemoryManager como fachada.
Aplicar truncamento por MEMORY_WINDOW_SIZE.
G-05 — Sistema de Skills Modular com Hot-Reload
Carregar .agents/skills/*/SKILL.md
Router leve para seleção da skill
Injeção de contexto somente em runtime
Zero reboot do core
G-06 — Controle Rígido de Acesso
Whitelist baseada em TELEGRAM_ALLOWED_USER_IDS
Nenhum processamento antes da validação
Nenhuma chamada a LLM para usuários inválidos
Métricas de Sucesso
Métrica	Baseline	Target	Prazo
Uptime do bot local	0%	99% estabilidade	30 dias
Hot-reload de skills	Reboot necessário	< 1s	10 dias
Loops encerrando antes do MAX	N/A	≥ 95%	Produção
Latência interna (sem LLM)	N/A	< 1000ms	Constante
4. Non-Goals (Fora do Escopo)
NG-02: Multiusuário público (não é SaaS corporativo).
NG-03: Bancos distribuídos (PostgreSQL complexo).
NG-04: Orquestração cloud ou containers (Kubernetes).
5. Usuário e Persona
Usuário Primário
Proprietário do sistema.
Opera via Telegram.
Acesso restrito por ID.
Jornada Atual (sem Agent Central)
Alterna entre múltiplas UIs web.
Copia/cola contexto manualmente.
Sem integração com filesystem local.
Jornada Futura (com Agent Central)
Envia mensagem via Telegram.
Bot intercepta localmente.
Validação de whitelist.
Skill Router identifica intenção.
AgentLoop executa ciclo ReAct.
Persistência automática.
Resposta no mesmo chat.
6. Requisitos Funcionais
6.1 Requisitos Principais
ID	Requisito	Prioridade	Critério de Aceite
RF-01	Loop persistente aiogram	Must	uv run main.py mantém polling ativo
RF-02	Validação de whitelist antes do core	Must	Usuário inválido não aciona AgentLoop
RF-03	AgentLoop com MAX_ITERATIONS	Must	Hard break seguro
RF-04	ProviderFactory intercambiável	Must	Troca de LLM via config
RF-05	Persistência via SQLite WAL	Must	Escrita concorrente sem lock perceptível
RF-06	SkillLoader FS-based	Must	Nova pasta é carregada sem reboot
RF-07	Log estruturado no terminal	Must	Thought/Action/Observation visíveis
6.2 Fluxo Principal (Happy Path)
Usuário envia texto no Telegram.
TelegramInputHandler valida whitelist.
AgentController coordena:
SkillLoader
SkillRouter
MemoryManager
AgentLoop inicia ciclo ReAct.
Tool executa se necessário.
Resultado retorna como Observation.
Resposta final é persistida.
TelegramOutputHandler envia resposta.
6.3 Fluxo Alternativo — Falha de LLM

Cenário: Provider retorna 503.

Comportamento:

ProviderFactory tenta fallback.
Se fallback falhar:
Loop encerra controladamente.
Mensagem enviada ao Telegram.
Log técnico no terminal.

Sem crash da engine principal.

7. Requisitos Não-Funcionais
ID	Requisito	Target
RNF-01	Latência interna (sem LLM)	< 1s
RNF-02	Timeout por chamada LLM	< 120s
RNF-03	SQLite WAL ativo	Sempre
RNF-04	Isolamento de secrets	Nunca persistir API keys
8. Design e Interface
Interface Externa
Telegram (única UI)
Terminal (observabilidade técnica)
Estados no Telegram
typing... durante processamento
Envio de:
Texto
Markdown como arquivo
Áudio (TTS)
Documentos
9. Modelo de Dados
conversations
id TEXT
user_id TEXT
provider TEXT
created_at DATETIME
messages
conversation_id TEXT
role TEXT   -- user | assistant | system | tool
content TEXT
created_at DATETIME

Sem foreign keys rígidas (performance > restrição estrutural).

10. Integrações e Dependências
Dependência	Tipo	Impacto se indisponível
Telegram API	Obrigatória	Sistema fica inoperante
Provider LLM	Obrigatória	Sem raciocínio
aiosqlite	Obrigatória	Falha na inicialização
Filesystem	Obrigatória	Skills não carregam
11. Edge Cases
Cenário	Trigger	Comportamento
Usuário falso	ID não whitelist	Ignorar no middleware
JSON malformado da IA	ToolCall inválido	Rejeita e solicita correção
DB lock	Escritas simultâneas	WAL + retry natural
MAX_ITERATIONS	Loop excedido	Break seguro
Arquivo grande demais	Excede threshold	Resposta de limite local
12. Segurança e Privacidade
Execução 100% local.
DB fora do Git.
Secrets via .env.
Tools não expõem paths sensíveis.
Nenhuma persistência de API keys.
13. Plano de Rollout
Estratégia
Deploy direto local via:
uv run main.py
Estrutura oficial:
/core
/data
/tmp
/.agents/skills
Monitoramento
Logs estruturados no STDOUT:
Iterações
Provider usado
Tool calls
Erros controlados
Considerações Estratégicas
Pontos Fortes
Total controle arquitetural.
Baixa superfície de ataque.
Modularidade real via Skills.
Sem dependência de UI web.
Riscos
Escalabilidade limitada ao hardware local.
Dependência forte da estabilidade do Telegram API.
Crescimento do SQLite sem política de arquivamento.
Oportunidades Futuras
Camada opcional de API REST interna.
Snapshot automático do SQLite.
Métricas estruturadas (Prometheus local).
Sandbox de execução para Tools mais sensíveis.