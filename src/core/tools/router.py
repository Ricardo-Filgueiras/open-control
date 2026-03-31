import json
from typing import Optional
from core.tools.loader import ToolLoader
from pydantic import BaseModel, Field

class ToolRouter:
    """Roteia user intent para a tool apropriada"""
    
    @staticmethod
    def route(user_intent: str, llm_handler) -> Optional[str]:
        """
        Analisa a intenção do usuário e retorna o ID da tool apropriada.
        
        Args:
            user_intent: Intenção do usuário
            llm_handler: Função que chama o LLM (handle_message)
        
        Returns:
            tool_id se encontrada, None caso contrário
        """
        loader = ToolLoader()
        tools_summary = loader.get_tool_summary()
        
        if not tools_summary:
            return None
        
        # Construir prompt para o router
        system_prompt = """Você é um Router de Ferramentas. Analisando a intenção do usuário, escolha a ferramenta MAIS apropriada.
            Ferramentas disponíveis:
            """
        for tool in tools_summary:
            system_prompt += f"- {tool['name']} (id: {tool['id']}): {tool['description']}\n"
        
        system_prompt += """\nRESPONDA APENAS com um JSON válido neste formato exato:
                        {"toolId": "id_da_tool"}
                        ou
                        {"toolId": null}

                        Se a intenção não combina com nenhuma ferramenta, retorne null.
                        Não adicione explicação, apenas o JSON."""
        
        try:
            # Prepara o prompt completo para o LLM
            routing_prompt = f"{system_prompt}\nUser: {user_intent}"
            response = llm_handler(routing_prompt)
            
            # Extrai JSON da resposta
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                tool_id = data.get("toolId")
                
                if tool_id:
                    print(f"🔄 Router: '{user_intent}' → tool '{tool_id}'")
                    return tool_id
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao fazer parse JSON do router: {e}")
        except Exception as e:
            print(f"❌ Erro no router: {e}")
        
        return None