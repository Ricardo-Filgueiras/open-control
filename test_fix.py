import os
import sys
from unittest.mock import patch, MagicMock

# Adiciona o diretório 'src' ao sys.path
sys.path.insert(0, os.path.abspath("src"))

from core.controller.agent_controller import AgentController

def test_provider_ollama():
    print("Testando provedor 'ollama'...")
    with patch.dict(os.environ, {"ACTIVE_PROVIDER": "ollama", "MODEL_LOCAL": "llama3.2:1b"}):
        # Mock ChatOllama to avoid connection errors
        with patch("core.controller.agent_controller.ChatOllama") as mock_chat:
            controller = AgentController()
            try:
                llm = controller._get_llm()
                print("✅ Provedor 'ollama' aceito com sucesso!")
            except ValueError as e:
                print(f"❌ Erro: {e}")
            except Exception as e:
                print(f"⚠️ Outro erro (esperado se não houver Ollama): {e}")

def test_provider_local():
    print("Testando provedor 'local'...")
    with patch.dict(os.environ, {"ACTIVE_PROVIDER": "local", "MODEL_LOCAL": "llama3.2:1b"}):
        with patch("core.controller.agent_controller.ChatOllama") as mock_chat:
            controller = AgentController()
            try:
                llm = controller._get_llm()
                print("✅ Provedor 'local' aceito com sucesso!")
            except ValueError as e:
                print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_provider_ollama()
    test_provider_local()
