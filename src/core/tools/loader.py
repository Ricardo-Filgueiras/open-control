import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional

class ToolLoader:
    """Carrega tools dinamicamente do diretório .agents/tools"""
    
    TOOLS_DIR = Path(__file__).parent.parent.parent.parent / ".agents" / "tools"
    
    @staticmethod
    def load_all_tools() -> List[Dict]:
        """Carrega todas as tools disponíveis"""
        tools = []
        
        if not ToolLoader.TOOLS_DIR.exists():
            print(f"⚠️ Diretório de tools não encontrado: {ToolLoader.TOOLS_DIR}")
            return tools
        
        for tool_dir in sorted(ToolLoader.TOOLS_DIR.iterdir()):
            if not tool_dir.is_dir():
                continue
                
            tool_file = tool_dir / "tool.md"
            if not tool_file.exists():
                print(f"⚠️ tool.md não encontrado em {tool_dir.name}")
                continue
            
            try:
                tool_data = ToolLoader._parse_tool_md(tool_file)
                if tool_data:
                    tools.append(tool_data)
                    print(f"✅ Tool carregada: {tool_data['name']}")
            except Exception as e:
                print(f"❌ Erro ao carregar {tool_dir.name}: {str(e)}")
        
        return tools
    
    @staticmethod
    def _parse_tool_md(file_path: Path) -> Optional[Dict]:
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
    
    @staticmethod
    def get_tool_by_id(tool_id: str) -> Optional[Dict]:
        """Retorna uma tool específica pelo ID"""
        tools = ToolLoader.load_all_tools()
        for tool in tools:
            if tool["id"] == tool_id:
                return tool
        return None
    
    @staticmethod
    def get_tool_summary() -> List[Dict]:
        """Retorna sumário leve para o router"""
        tools = ToolLoader.load_all_tools()
        return [
            {
                "name": t["name"],
                "id": t["id"],
                "description": t["description"],
                "category": t["category"]
            }
            for t in tools
        ]
