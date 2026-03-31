"""
FICHIER : test_session_manager.py
RÔLE : Tests unitaires du SessionManager.

TESTS :
  test_create_session() → Vérifier la création d'une nouvelle session
  test_get_existing_session() → Récupérer une session existante depuis Redis
  test_session_expiry() → Vérifier l'expiration TTL
  test_update_session_state() → Mettre à jour l'état et les données collectées
  test_session_serialization() → Sérialisation/désérialisation JSON correcte

TECHNOLOGIE : pytest-asyncio, fakeredis (mock Redis sans serveur réel)
"""
