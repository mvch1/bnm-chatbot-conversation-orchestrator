"""
FICHIER : shared/repositories/escalation_repository.py
RÔLE : Repository pour les opérations sur la table escalation.

MÉTHODES :
  create_escalation(session_id, reason, confidence, last_step_id) → Escalation
    → INSERT + création du ticket ESCALATION
    → Sélectionne automatiquement l'agent disponible le plus approprié

  assign_agent(id: UUID, agent_id: UUID) → Escalation
    → UPDATE status='ASSIGNED', assigned_agent_id, assigned_at=NOW()

  get_context(escalation_id: UUID) → dict
    → JOIN escalation + workflow_step_log + sessions + users
    → Retourne le contexte complet pour l'agent

  get_pending() → List[Escalation]
    → SELECT WHERE status='PENDING' ORDER BY created_at
    → Utilisé pour la file d'attente d'assignation automatique

TECHNOLOGIE : SQLAlchemy 2.0 async
"""
