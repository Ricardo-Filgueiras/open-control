import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.tools.loader import ToolLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.agents import AgentFinish
from langchain_core.utils.function_calling import convert_to_openai_function

load_dotenv()

class AgentController:
    """O Cérebro do JARVIS que gerencia o Loop de Raciocínio com suporte a Tools."""
    
    def __init__(self):
        # Configurações dinâmicas
        self.provider = os.getenv("ACTIVE_PROVIDER", "google").lower()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model_google = os.getenv("MODEL_GOOGLE", "gemini-1.5-flash")
        self.model_local = os.getenv("MODEL_LOCAL", "llama3.2:1b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.use_tools = os.getenv("USE_TOOLS", "true").lower() == "true"
        
        # Carregar tools
        self.loader = ToolLoader()
        self.tools = self.loader.get_langchain_tools()
        self.tool_run = {t.name: t for t in self.tools}
        
        # Lista para o prompt (amigável)
        tools_summary = self.loader.get_tool_summary()
        tools_list = "\n".join([f"- {t['name']} ({t['id']}): {t['description']}" for t in tools_summary])

        self.system_prompt = f"""
        Você é o J.A.R.V.I.S. (Just A Rather Very Intelligent System).
        Atitude: Polido, leal, inteligente, levemente sarcástico.
        Regra: Chamar o usuário de 'senhor'. Formatar dados com clareza.
        
        Protocolos (Ferramentas) Ativos:
        {tools_list if tools_list else "Nenhum protocolo extra carregado no momento."}
        
        Sempre que o senhor perguntar sobre suas capacidades ou ferramentas, você deve listar os protocolos acima.
        """

    def _get_llm(self):
        """Seleciona o provedor com base no .env"""
        if self.provider == "google":
            if not self.google_api_key:
                raise ValueError("senhor, GOOGLE_API_KEY não localizada.")
            return ChatGoogleGenerativeAI(
                model=self.model_google, 
                google_api_key=self.google_api_key
            )
        elif self.provider in ["local", "ollama"]:
            return ChatOllama(model=self.model_local, base_url=self.ollama_host)
        else:
            raise ValueError(f"Sir, o provedor '{self.provider}' é desconhecido.")

    def handle_message(self, message: str, system_override: str = None) -> str:
        """Processa mensagem via Function Calling Chain"""
        try:
            llm = self._get_llm()
            system_to_use = system_override or self.system_prompt
            
            # 1. Definir Prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_to_use),
                ("user", "{input}")
            ])
            
            # 2. Bind das ferramentas (convertendo para schema OpenAI)
            if self.use_tools and self.tools:
                # Nota: Alguns provedores preferem bind_tools direto
                chat_with_tools = llm.bind_tools(self.tools)
            else:
                chat_with_tools = llm

            # 3. Criar Chain
            chain = prompt | chat_with_tools
            
            # 4. Executar e Processar
            result = chain.invoke({"input": message})
            
            # 5. Roteamento (Lógica simplificada do parser)
            if hasattr(result, 'tool_calls') and result.tool_calls:
                # Executar a primeira tool call encontrada
                tool_call = result.tool_calls[0]
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                if tool_name in self.tool_run:
                    print(f"⚙️ Executando tool: {tool_name} com {tool_args}")
                    # A execução real da ferramenta
                    observation = self.tool_run[tool_name].invoke(tool_args)
                    
                    # Opcional: Chamar o LLM novamente com o resultado para uma resposta fluida
                    # Para simplificar e seguir o checklist, retornamos o resultado ou chamamos de novo
                    print(f"✅ Resultado da tool: {observation}")
                    
                    # Segunda chamada para o J.A.R.V.I.S. consolidar a resposta
                    final_prompt = ChatPromptTemplate.from_messages([
                        ("system", system_to_use),
                        ("user", message),
                        ("assistant", f"Executarei o protocolo {tool_name}."),
                        ("user", f"Resultado da ferramenta: {observation}. Agora finalize sua resposta para mim.")
                    ])
                    return (final_prompt | llm).invoke({}).content
            
            return result.content
            
        except Exception as e:
            return f"senhor, detectei uma instabilidade na matriz {self.provider.upper()}: {str(e)}"
    
    def _get_llm_handler(self):
        """Retorna uma função que pode ser usada pelo router/executor"""
        def handler(user_input: str, system_prompt: str = None) -> str:
            try:
                llm = self._get_llm()
                messages = [
                    SystemMessage(content=system_prompt or self.system_prompt),
                    HumanMessage(content=user_input)
                ]
                response = llm.invoke(messages)
                return response.content
            except Exception as e:
                return f"Erro: {str(e)}"
        return handler
