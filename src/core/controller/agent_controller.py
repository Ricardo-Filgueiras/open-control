import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from core.tools.router import ToolRouter
from core.tools.executor import ToolExecutor

load_dotenv()

class AgentController:
    """O Cérebro do JARVIS que gerencia o Loop de Raciocínio com suporte a Tools."""
    
    def __init__(self):
        self.system_prompt = """
        Você é o J.A.R.V.I.S. (Just A Rather Very Intelligent System).
        Atitude: Polido, leal, inteligente, levemente sarcástico.
        Regra: Chamar o usuário de 'senhor'. Formatar dados com clareza.
        """
        # Carregar configurações dinâmicas
        self.provider = os.getenv("ACTIVE_PROVIDER", "google").lower()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model_google = os.getenv("MODEL_GOOGLE", "gemini-1.5-flash")
        self.model_local = os.getenv("MODEL_LOCAL", "llama3.2:1b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.use_tools = os.getenv("USE_TOOLS", "true").lower() == "true"

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
        """
        Processa uma mensagem do usuário, opcionalmente roteando para tools.
        
        Args:
            message: Mensagem do usuário
            system_override: System prompt customizado (usado por tools)
        
        Returns:
            Resposta do agente
        """
        try:
            # Se um system prompt foi passado (por uma tool), usa ele
            if system_override:
                system_to_use = system_override
            else:
                system_to_use = self.system_prompt
            
            # Etapa 1: Tentar rotear para uma tool (se habilitado)
            if self.use_tools and not system_override:
                tool_id = ToolRouter.route(message, self._get_llm_handler())
                
                if tool_id:
                    # Etapa 2: Executar a tool com contexto injetado
                    response = ToolExecutor.execute(tool_id, message, self._get_llm_handler())
                    return response
            
            # Etapa 3: Fallback - Responder normalmente sem tool
            llm = self._get_llm()
            messages = [
                SystemMessage(content=system_to_use),
                HumanMessage(content=message)
            ]
            response = llm.invoke(messages)
            return response.content
            
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
