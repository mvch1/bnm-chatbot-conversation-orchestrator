"""
FICHIER : test_message_router.py
RÔLE : Tests unitaires du MessageRouter.

TESTS :
  test_route_faq_intent() → Intent INFO_PRODUIT → appel RAG Service
  test_route_complaint_intent() → Intent DEPOT_RECLAMATION → Workflow Service
  test_route_low_confidence() → confidence < 0.5 → Agent Service
  test_route_agent_request() → Intent DEMANDE_AGENT → Agent Service directement
  test_fallback_response() → Intent UNKNOWN → message de clarification

TECHNOLOGIE : pytest, pytest-mock (mocker les appels httpx)
"""
