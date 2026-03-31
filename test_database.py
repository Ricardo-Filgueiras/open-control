#!/usr/bin/env python
"""
Script de teste para validar persistência com SQLite
Execute com: python test_database.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Adiciona src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.database.repositories import SessionRepository, MessageRepository, MetadataRepository

def test_session_creation():
    """Testa criação de sessão"""
    print("\n" + "="*60)
    print("✍️  TESTE 1: Criação de Sessão")
    print("="*60)
    
    repo = SessionRepository()
    session = repo.create(
        title="Test Session 1",
        tags=["test", "debug"]
    )
    
    print(f"✅ Sessão criada:")
    print(f"   ID: {session.id}")
    print(f"   Título: {session.title}")
    print(f"   Criada em: {session.created_at}")
    
    return session.id

def test_message_operations(session_id):
    """Testa CRUD de mensagens"""
    print("\n" + "="*60)
    print("💬 TESTE 2: Operações com Mensagens")
    print("="*60)
    
    msg_repo = MessageRepository()
    
    # Criar mensagens
    print("\n➕ Adicionando mensagens...")
    msg1 = msg_repo.create(
        session_id=session_id,
        role="user",
        content="Olá, como você está?"
    )
    print(f"   ✅ Mensagem 1 criada (ID: {msg1.id})")
    
    msg2 = msg_repo.create(
        session_id=session_id,
        role="assistant",
        content="Estou bem, obrigado! Como posso ajudar?"
    )
    print(f"   ✅ Mensagem 2 criada (ID: {msg2.id})")
    
    msg3 = msg_repo.create(
        session_id=session_id,
        role="user",
        content="Qual é a data de hoje?"
    )
    print(f"   ✅ Mensagem 3 criada (ID: {msg3.id})")
    
    # Recuperar mensagens
    print("\n🔍 Recuperando mensagens da sessão...")
    messages = msg_repo.get_by_session(session_id)
    print(f"   ✅ {len(messages)} mensagem(ns) encontrada(s):")
    for i, msg in enumerate(messages, 1):
        print(f"      {i}. [{msg.role}] {msg.content[:50]}...")
    
    # Últimas N mensagens
    print("\n📌 Últimas 2 mensagens...")
    last_n = msg_repo.get_last_n(session_id, n=2)
    print(f"   ✅ {len(last_n)} mensagem(ns):")
    for msg in last_n:
        print(f"      • [{msg.role}] {msg.content[:60]}...")
    
    return len(messages) == 3

def test_session_retrieval(session_id):
    """Testa recuperação de sessão com histórico"""
    print("\n" + "="*60)
    print("📂 TESTE 3: Recuperação de Sessão com Histórico")
    print("="*60)
    
    repo = SessionRepository()
    session = repo.get_by_id(session_id)
    
    if session:
        print(f"\n✅ Sessão carregada:")
        print(f"   ID: {session.id}")
        print(f"   Título: {session.title}")
        print(f"   Mensagens: {session.message_count}")
        print(f"\n📋 Histórico:")
        for i, msg in enumerate(session.messages, 1):
            print(f"   {i}. [{msg.role}] {msg.content[:60]}...")
        return True
    return False

def test_list_sessions():
    """Testa listagem de sessões"""
    print("\n" + "="*60)
    print("📑 TESTE 4: Listagem de Sessões Recentes")
    print("="*60)
    
    repo = SessionRepository()
    sessions = repo.get_recent(limit=10)
    
    print(f"\n✅ {len(sessions)} sessão(ões) encontrada(s):")
    for i, session in enumerate(sessions, 1):
        duration_str = f"{session.duration_seconds//60}m" if session.duration_seconds else "N/A"
        print(f"   {i}. [{session.id}] {session.title}")
        print(f"      Mensagens: {session.message_count} | Duração: {duration_str}")
    
    return len(sessions) > 0

def test_metadata():
    """Testa gerenciamento de metadados"""
    print("\n" + "="*60)
    print("⚙️  TESTE 5: Metadados da Aplicação")
    print("="*60)
    
    meta_repo = MetadataRepository()
    
    # Definir metadados
    print("\n➕ Definindo metadados...")
    meta_repo.set("last_session_id", "123")
    meta_repo.set("version", "0.2.0")
    meta_repo.set("theme", "stark")
    print("   ✅ Metadados definidos")
    
    # Recuperar
    print("\n🔍 Recuperando metadados...")
    last_id = meta_repo.get("last_session_id")
    version = meta_repo.get("version")
    theme = meta_repo.get("theme")
    
    print(f"   • last_session_id: {last_id}")
    print(f"   • version: {version}")
    print(f"   • theme: {theme}")
    
    # Listar todos
    print("\n📋 Todos os metadados:")
    all_meta = meta_repo.get_all()
    for key, value in all_meta.items():
        print(f"   • {key}: {value}")
    
    return len(all_meta) >= 3

def main():
    print("\n" + "🗄️  "*30)
    print("TESTES DO SISTEMA DE PERSISTÊNCIA J.A.R.V.I.S.")
    print("🗄️  "*30)
    
    try:
        # Executar testes em sequência
        session_id = test_session_creation()
        msg_result = test_message_operations(session_id)
        session_result = test_session_retrieval(session_id)
        list_result = test_list_sessions()
        meta_result = test_metadata()
        
        results = {
            "Criação de Sessão": True,
            "Operações com Mensagens": msg_result,
            "Recuperação com Histórico": session_result,
            "Listagem de Sessões": list_result,
            "Metadados": meta_result,
        }
        
        print("\n" + "="*60)
        print("RESUMO DOS TESTES")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name:.<40} {status}")
        
        print(f"\nTotal: {passed}/{total} testes passaram")
        
        if passed == total:
            print("\n🎉 Sistema de persistência está funcionando!")
        else:
            print(f"\n⚠️  {total - passed} teste(s) falharam.")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ Erro geral durante testes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
