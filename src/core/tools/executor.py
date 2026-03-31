from typing import Optional, Dict, Any
from core.tools.loader import ToolLoader

class ToolExecutor:
    """Executa a tool selecionada com seu contexto completo"""
    
    @staticmethod
    def execute(tool_id: str, user_input: str, llm_handler) -> Optional[str]:
        """
        Executa uma tool específica injetando seu contexto
        
        Args:
            tool_id: ID da tool a executar
            user_input: Input do usuário
            llm_handler: Função para chamar o LLM
        
        Returns:
            Resposta da tool ou mensagem de erro
        """
        tool = ToolLoader.get_tool_by_id(tool_id)
        
        if not tool:
            return f"❌ Tool '{tool_id}' não encontrada."
        
        # Injeta o contexto completo da tool
        enhanced_system_prompt = f"""Você está operando com a ferramenta: **{tool['name']}**

{tool['instruction']}

---

Responda baseado nas instruções dessa ferramenta."""
        
        try:
            response = llm_handler(user_input, enhanced_system_prompt)
            print(f"✅ Tool '{tool_id}' executada com sucesso")
            return response
        except Exception as e:
            print(f"❌ Erro ao executar tool '{tool_id}': {str(e)}")
            return f"❌ Erro ao executar tool '{tool_id}': {str(e)}"
    
    @staticmethod
    def get_tool_info(tool_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações completas de uma tool"""
        return ToolLoader.get_tool_by_id(tool_id)
    
    @staticmethod
    def list_all_tools() -> list:
        """Lista todas as tools disponíveis"""
        return ToolLoader.get_tool_summary()
