"""
FICHIER : shared/repositories/workflow_repository.py
RÔLE : Opérations sur workflow_step_logs, escalations et wallet_validation_requests.

MÉTHODES — workflow_step_logs :
  log_step(session_id, workflow_type, step_index, step_name,
           user_input, bot_response, is_valid) → WorkflowStepLog
    → Insère une ligne de journal à chaque étape du workflow

  get_steps_for_session(session_id: UUID) → List[WorkflowStepLog]
    → Récupère toutes les étapes d'une session (pour reprise ou audit)

  get_last_valid_step(session_id: UUID) → WorkflowStepLog | None
    → Dernière étape avec is_valid=True (pour la reprise de session)

MÉTHODES — escalations :
  create_escalation(session_id, last_step_id, reason, confidence) → Escalation
  assign_escalation(escalation_id, agent_id) → Escalation
  get_context_for_agent(escalation_id) → EscalationContext
    → Jointure : escalation + dernière étape + données collectées session

MÉTHODES — wallet_validation_requests :
  create_wallet_request(user_id, session_id, phone, cin, doc_path) → WalletValidationRequest
  update_wallet_status(id, status, reviewed_by, rejection_reason) → WalletValidationRequest
  get_by_user(user_id) → List[WalletValidationRequest]
    → Historique des tentatives de validation d'un client

CONSEILS TECHNIQUES :
  - log_step() est appelé à haute fréquence → optimiser avec INSERT batch
  - get_context_for_agent() est une requête critique → pré-calculer avec une vue
  - Index sur (session_id, step_index) pour toutes les requêtes de reprise

TECHNOLOGIE : SQLAlchemy 2.0 async, PostgreSQL
"""
