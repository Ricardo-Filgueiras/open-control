import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Any
from langchain_core.tools import StructuredTool
from core.tools.schemas import CalculatorArgs, InfoArgs, WebSearchArgs
from core.tools.implementations import calculate, get_extended_info, web_search
from pydantic import BaseModel, Field


class ToolLoader(BaseModel):
    """Carrega tools dinamicamente do diretório .agents/tools"""
    
    # Campo definido como fixo, mas usando Pydantic para validação se necessário
    tools_dir: Path = Field(
        default=Path(__file__).parent.parent.parent.parent / ".agents" / "tools"
    )

    def load_all_tools(self) -> List[Dict]:
        """Carrega todas as ferramentas disponíveis no diretório .agents/tools"""
        tools = []
        
        if not self.tools_dir.exists():
            print(f"⚠️ Diretório de tools não encontrado: {self.tools_dir}")
            return tools
        
        for tool_dir in sorted(self.tools_dir.iterdir()):
            if not tool_dir.is_dir():
                continue
                
            tool_file = tool_dir / "tool.md"
            if not tool_file.exists():
                print(f"⚠️ tool.md não encontrado em {tool_dir.name}")
                continue
            
            try:
                tool_data = self._parse_tool_md(tool_file)
                if tool_data:
                    tools.append(tool_data)
                    print(f"✅ Tool carregada: {tool_data['name']}")
            except Exception as e:
                print(f"❌ Erro ao carregar {tool_dir.name}: {str(e)}")
        
        return tools
    
    def _parse_tool_md(self, file_path: Path) -> Optional[Dict]:
        """Parse YAML frontmatter + conteúdo do markdown"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair frontmatter YAML
        match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not match:
            return None
        
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2)
            
            return {
                "name": frontmatter.get("name"),
                "id": frontmatter.get("id", frontmatter.get("name", "").lower().replace(" ", "-")),
                "description": frontmatter.get("description"),
                "category": frontmatter.get("category", "general"),
                "version": frontmatter.get("version", "1.0"),
                "full_content": content,
                "instruction": body.strip()
            }
        except Exception as e:
            print(f"Erro ao fazer parse do frontmatter: {e}")
            return None
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict]:
        """Retorna uma tool específica pelo ID"""
        actual_tools = self.load_all_tools()

        for tool in actual_tools:
            if tool["id"] == tool_id:
                return tool
        return None
    
    def get_tool_summary(self) -> List[Dict]:
        """Retorna sumário leve para o router"""
        tools = self.load_all_tools()
        return [
            {
                "name": t["name"],
                "id": t["id"],
                "description": t["description"],
                "category": t["category"]
            }
            for t in tools
        ]

    def get_langchain_tools(self) -> List[Any]:
        """Retorna as ferramentas no formato StructuredTool do LangChain"""
        # Mapeia IDs para schemas e implementações
        mapping = {
            "calculator": {"schema": CalculatorArgs, "func": calculate},
            "info": {"schema": InfoArgs, "func": get_extended_info},
            "web-search": {"schema": WebSearchArgs, "func": web_search}
        }
        
        lc_tools = []
        for t_id, data in mapping.items():
            tool_info = self.get_tool_by_id(t_id)
            if tool_info:
                lc_tools.append(
                    StructuredTool.from_function(
                        func=data["func"],
                        name=tool_info["id"], # Usando ID como nome funcional
                        description=tool_info["description"],
                        args_schema=data["schema"]
                    )
                )
        return lc_tools
