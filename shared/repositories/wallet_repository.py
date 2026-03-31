"""
FICHIER : shared/repositories/wallet_repository.py
RÔLE : Repository pour les opérations sur wallet_validation_request.

MÉTHODES :
  create_request(data: WalletRequestCreate) → WalletValidationRequest
    → INSERT + création du ticket associé
    → Vérifie si une demande existe déjà pour ce user (attempt_number++)

  get_by_session(session_id: UUID) → WalletValidationRequest | None
    → Récupère la demande active d'une session

  approve(id: UUID, agent_id: UUID) → WalletValidationRequest
    → UPDATE status='APPROVED', reviewed_by, reviewed_at
    → Déclenche la notification WhatsApp au client

  reject(id: UUID, agent_id: UUID, reason: str) → WalletValidationRequest
    → UPDATE status='REJECTED', rejection_reason
    → Déclenche la notification WhatsApp avec le motif

  list_pending(page: int, per_page: int) → List[WalletValidationRequest]
    → Pour le tableau de bord superviseur

TECHNOLOGIE : SQLAlchemy 2.0 async
"""
