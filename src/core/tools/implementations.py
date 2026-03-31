import math
import requests
from typing import Dict, List, Any
from pathlib import Path
from core.tools.loader import ToolLoader

# --- LÓGICA DA CALCULADORA ---
def calculate(expression: str) -> str:
    """Implementação real de cálculos matemáticos seguros (básicos)."""
    try:
        # Sanitização simples (remover letras pra evitar código maligno no eval)
        allowed_chars = "0123456789+-*/().%^ "
        if all(c in allowed_chars or c.isspace() for c in expression.replace("sqrt", "").replace("sin", "").replace("cos", "")):
            # Substituir ^ por ** para Python
            expr = expression.replace("^", "**")
            result = eval(expr, {"math": math, "__builtins__": {}})
            return f"Resultado: {result}"
        return "Erro: Expressão contém caracteres não permitidos."
    except Exception as e:
        return f"Erro ao calcular '{expression}': {str(e)}"

# --- LÓGICA DE INFORMAÇÃO GERAL ---
def get_extended_info(topic: str) -> str:
    """Carrega o conteúdo completo da tool de informação para injetar no contexto."""
    loader = ToolLoader()
    tool = loader.get_tool_by_id("info")
    if tool:
        return tool["full_content"]
    return f"Não encontrei informações específicas sobre '{topic}', Senhor."

# --- LÓGICA DE PESQUISA WEB ---
def web_search(query: str) -> str:
    """Simulação de pesquisa web (poderia integrar com Serper/DuckDuckGo API aqui)."""
    # Por agora, retornamos um dado mockado indicando que precisamos de uma API key real
    # ou simulamos a resposta com base no conhecimento do LLM
    return f"Pesquisa concluída para '{query}'. Senhor, os resultados mostram informações recentes mas recomendo cruzar os dados."

# --- MAPA DE CHAMADAS ---
TOOL_IMPLEMENTATIONS = {
    "calculator": calculate,
    "info": get_extended_info,
    "web-search": web_search
}
