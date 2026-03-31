import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

class AgentController:
    """O Cérebro do JARVIS que gerencia o Loop de Raciocínio."""
    
    def __init__(self):
        self.system_prompt = """
        Você é o J.A.R.V.I.S. (Just A Rather Very Intelligent System).
        Atitutde: Polido, leal, inteligente, levemente sarcástico.
        Regra: Chamar o usuário de 'Sir'. Formatar dados com clareza.
        """
        # Carregar configurações dinâmicas
        self.provider = os.getenv("ACTIVE_PROVIDER", "google").lower()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.model_google = os.getenv("MODEL_GOOGLE", "gemini-1.5-flash")
        self.model_local = os.getenv("MODEL_LOCAL", "llama3.2:1b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def _get_llm(self):
        """Seleciona o provedor com base no .env"""
        if self.provider == "google":
            if not self.google_api_key:
                raise ValueError("Sir, GOOGLE_API_KEY não localizada.")
            return ChatGoogleGenerativeAI(
                model=self.model_google, 
                google_api_key=self.google_api_key
            )
        elif self.provider == "local":
            return ChatOllama(model=self.model_local, base_url=self.ollama_host )
        else:
            raise ValueError(f"Sir, o provedor '{self.provider}' é desconhecido.")

    def handle_message(self, message: str) -> str:
        try:
            llm = self._get_llm()
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message)
            ]
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"Sir, detectei uma instabilidade na matriz {self.provider.upper()}: {str(e)}"
