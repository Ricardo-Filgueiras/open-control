#!/usr/bin/env python
"""
Script de teste para validar o sistema de Tools
Execute com: python test_tools.py
"""

import sys
from pathlib import Path

# Adiciona src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.tools.loader import ToolLoader
from core.tools.router import ToolRouter
from core.tools.executor import ToolExecutor

def test_loader():
    """Testa carregamento de tools"""
    print("\n" + "="*60)
    print("🔧 TESTE 1: Carregador de Tools")
    print("="*60)
    
    loader = ToolLoader()
    tools = loader.load_all_tools()
    print(f"\n✅ {len(tools)} tool(s) carregada(s):")
    for tool in tools:
        print(f"   • {tool['name']} (id: {tool['id']}) - {tool['description']}")
    
    summary = loader.get_tool_summary()
    print(f"\n📋 Sumário de tools:")
    for t in summary:
        print(f"   • {t['name']}: {t['description']}")
    
    return len(tools) > 0

def test_tool_retrieval():
    """Testa recuperação de tool específica"""
    print("\n" + "="*60)
    print("🔍 TESTE 2: Recuperação de Tool Específica")
    print("="*60)
    
    loader = ToolLoader()
    tool = loader.get_tool_by_id("calculator")
    if tool:
        print(f"\n✅ Tool 'calculator' encontrada:")
        print(f"   Nome: {tool['name']}")
        print(f"   Descrição: {tool['description']}")
        print(f"   Categoria: {tool['category']}")
        return True
    else:
        print("❌ Tool 'calculator' não encontrada")
        return False

def test_executor_info():
    """Testa obtenção de info da tool"""
    print("\n" + "="*60)
    print("ℹ️  TESTE 3: Informações da Tool (Executor)")
    print("="*60)
    
    info = ToolExecutor.get_tool_info("info")
    if info:
        print(f"\n✅ Info sobre tool 'info':")
        print(f"   Nome: {info['name']}")
        print(f"   ID: {info['id']}")
        print(f"   Instruções (primeiras 100 chars):")
        print(f"   {info['instruction'][:100]}...")
        return True
    else:
        print("❌ Tool 'info' não encontrada")
        return False

def test_list_tools():
    """Testa listagem de todas as tools"""
    print("\n" + "="*60)
    print("📑 TESTE 4: Listagem de Todas as Tools (Executor)")
    print("="*60)
    
    tools = ToolExecutor.list_all_tools()
    print(f"\n✅ {len(tools)} tool(s) disponível(is):")
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool['name']} ({tool['id']}) - Categoria: {tool['category']}")
    
    return len(tools) > 0

def main():
    print("\n" + "🤖 "*30)
    print("TESTES DO SISTEMA DE TOOLS J.A.R.V.I.S.")
    print("🤖 "*30)
    
    results = {
        "Loader": test_loader(),
        "Recuperação": test_tool_retrieval(),
        "Info da Tool": test_executor_info(),
        "Listagem": test_list_tools(),
    }
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! O sistema de tools está pronto.")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Verifique os logs acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
