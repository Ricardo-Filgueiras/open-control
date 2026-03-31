import os
import sys
from pathlib import Path

# Adiciona o diretório 'src' ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.tools.loader import ToolLoader
from core.tools.router import ToolRouter
from core.tools.executor import ToolExecutor

def test_loader():
    print("Testing ToolLoader...")
    loader = ToolLoader()
    tools = loader.load_all_tools()
    print(f"Total tools loaded: {len(tools)}")
    for t in tools:
        print(f"- {t['name']} (ID: {t['id']})")
    
    if len(tools) > 0:
        tool_id = tools[0]['id']
        t_info = loader.get_tool_by_id(tool_id)
        print(f"Found tool info for {tool_id}: {t_info['name']}")

def test_router():
    print("\nTesting ToolRouter...")
    def mock_llm_handler(prompt):
        # Mocking logical routing for "Calculadora" or "Web Search"
        if "calculadora" in prompt.lower():
            return '{"toolId": "calculadora"}'
        return '{"toolId": null}'
    
    tool_id = ToolRouter.route("Eu quero calcular 2+2", mock_llm_handler)
    print(f"Route result: {tool_id}")

if __name__ == "__main__":
    try:
        test_loader()
        test_router()
        print("\n✅ Verification SUCCESS!")
    except Exception as e:
        print(f"\n❌ Verification FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
