# Spec: tool Management System (Hot-Reload)

**Versão:** 1.0
**Status:** Aprovada
**Autor:** ten Agent
**Data:** 2026-03-10

---

## 1. Resumo

A arquitetura de injeção de habilidades (`tools`) possibilita que novas capacidades, prompts engessados ou guias instrucionais complexos se integrem dinamicamente ao agente sem requerer nenhuma reinicialização (deploy zero). Através deste sistema (Loader -> Router -> Executor), cada subpasta vira uma Action especializada reconhecida por um LLM.

---

## 2. Contexto e Motivação

**Problema:**
Adicionar habilidades num chatbot em nível de código causa quebras de estabilidade, misturas no "Core" Principal e requer reboot do backend Python a cada alteração pequena na string de inteligência.

**Evidências:**
Se o LLM receber instruções enormes fixas no seu Master Prompt, além de "queimar dinheiro" com a Context Window cheia em conversas bobas (ex: "Oi"), ele sofre de perda de atenção nas diretivas essenciais. 

**Por que agora:**
A separação num formato plugin (pasta .agents) modulariza tudo e deixa o Router LLM usar um prompt barato para dizer "Sim, devo focar a tool de Github" só quando o usuário pedir pra ver repósitorios.

---

## 3. Goals (Objetivos)

- [ ] G-01: Ler na raiz do projeto o diretório oculto/arquitetural `.agents/tools` mapeando seus `tool.md`. O agente deve, obrigatoriamente, carregar todas as tools desta pasta para formatar e responder adequadamente ao usuário via Telegram.
- [ ] G-02: Executar um Router inicial ("Passo Zero" na rede neural) apenas passando descritivos básicos das tools + Intenção do usuário, recebendo a string correspondente de qual plugin instanciar ou nulo.
- [ ] G-03: Inserir a documentação detalhada da tool no Master Context apenas durante a iteração daquele comando isolado (Runtime Injection).

**Métricas de sucesso:**
| Métrica | Baseline atual | Target | Prazo |
|---------|---------------|--------|-------|
| Tempos Re-escrita Hot Reload | Reboot forçado | 1ms por chamada (FS lendo síncrono subpastas) | Constante |
| Taxa de Sucesso Router LLM | < 50% sem Router | 99% precisão ao acionar o plugin certo | MVP |

---

## 4. Non-Goals (Fora do Escopo)

- NG-01: Chamar múltiplas tools distintas como resposta a uma única requisição. Uma requisição = Uma intenção master / tool principal repassada em pipeline. Multiplos acionamentos serão responsabilidade da abstração da LLM no passo 2 de ReAct e não no Router.

---

## 5. Usuários e Personas

**Usuario Primario:** Sandeco, através da pasta Filesystem para inserir diretórios customizados com `.md`, e o bot interno (Loader e Executor) para lidar nos backgrounds da arquitetura.

---

## 6. Requisitos Funcionais

### 6.1 Requisitos Principais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | `toolLoader` deve abrir síncrono FS nativo na inicial de todas requests Telegram, e carregar **todas** as tools presentes na pasta `.agents/tools` para o array. | Must | Retorna Array contendo objetos do YAML frontmatter de nome + desc de todas as pastas de tools instaladas em `.agents/tools`. |
| RF-02 | O Prompt de `toolRouter` deve conter o schema JSON forçado dizendo que ele apenas retorna `{"toolName": "xyz" | null}`. | Must | String parse error capturada e tratada igual a nulo (Fallback a chatbot casual). |
| RF-03 | A Observação "availabletools" com os resumos enxutos deve ir sempre pro loop subsequente. | Must | Se o AgentLoop do ReAct não souber das existencias de Ferramenta da própria tool, quebra por Prompt Injection de segurança reversa. |

### 6.2 Fluxo Principal (Happy Path)

1. Entrada: "Crie a spec de auth do projeto React".
2. Evento interceptado. Loader lê 3 tools (PrdManager, GitManager, CodeAnalyzer) de metadado.
3. toolRouter instancia request HTTP leve e barata pro Grog (ex) só validando com os metadados ("codeAnalyzer", "prdManager").
4. O `Router` retorna `{"toolName": "prd-manager"}`.
5. Inicia o Executor: lê 6KB de instrução profunda de `/prd-manager/tool.md`.
6. Repassa ela no AgentLoop via param `toolContent` (joga no System Role puro) associado à array de ferramentas ativas.
7. Bot devolve arquivo gerado baseando nos parâmetros intensivos estipulados no SDD local e descarta a string gigante. Limpo o ambiente pro proximo call não relacionado (como "Que horas são").

### 6.3 Fluxos Alternativos

**Nenhum Casamento (N/A Intent):** Se perguntou "Como tá a rua aí?" o router em passo zero dirá null; fallback cai pro agente raiz responder livre.

---

## 7. Requisitos Não-Funcionais

| ID | Requisito | Valor alvo | Observação |
|----|-----------|-----------|------------|
| RNF-01 | Velocidade de FS IO | Leitura local rápida | FS do Python deverá ler os arquivos rápido (sync ou async ok dada a escala). |

---

## 8. Design e Interface

Componente afeta `TelegramOutputHandler` pois a Saida da tool se for `.md` renderizado no OutputHandler gerará Files (`InputFile({path})`). O front-end invisível deve exportar um Document puro sem perda das sintaxes e indentações.

---

## 9. Modelo de Dados

Não gera tabela SQLite. Leitura via YAML Frontmatter.

---

## 10. Integrações e Dependências

| Dependência | Tipo | Impacto se indisponível |
|-------------|------|------------------------|
| Biblioteca `pyyaml` / regex | Obrigatória | Sem ela não separarei os params frontmatter do markdown e quebra indexação no dicionário/lista. |
| Filesystem nativo Python | Obrigatória | tool Loader System paralisa em exception de path inexistente `FileNotFoundError`. |

---

## 11. Edge Cases e Tratamento de Erros

| Cenário | Trigger | Comportamento esperado |
|---------|---------|----------------------|
| EC-01: tool Duplicada e Conflitante | O User salvou duas pastas com id "code-maker" iguais no YAML. | Puxar o First Match via `Object.keys()` overwrite (a ultima substitui a velha no Array de memory load e ignora warning limpo em console.log) |
| EC-02: `tool.md` Ausente na subpasta | User criou a pasta mas não colocou spec. | O Loader não quebra. Pula forEach nativa e silencia falha do plugin na pasta "ghost". |
| EC-03: Falha Estrutural do Frontmatter | Arquivo MD começa direto no # Header sem `---` tags e sem "name: x" | Rejeita load pontual por null exceptions geradas. Sem log fatal, prosseguir pros demais 10 plugins. |

---

## 12. Segurança e Privacidade

- Autenticação e Autorização estão em camada externa (Bot aiogram Handler), as tools operam blindly sem verificar Whitelist - assumindo permissão plena concedida globalmente ao AgentController via Telegram UserId check.

---

## 13. Plano de Rollout

A estrutura do diretório `.agents/tools` se tornará o padrão oficial na branch v2 MVP (sem dependência de banco de dados e só File IO de arquivos markdown normais compatíveis com LLMs de leitura de codebase puras e agentes IDE cursor-like).

---

## 14. Open Questions

N/A