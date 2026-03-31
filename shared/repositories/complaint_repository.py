"""
FICHIER : shared/repositories/complaint_repository.py
RÔLE : Repository dédié aux opérations sur la table complaints.

MÉTHODES :
  create_complaint(data: ComplaintCreate) → Complaint
    → INSERT avec génération du ticket_number (REC-YYYY-NNNNN)
    → Transaction : crée aussi le ticket correspondant

  get_by_ticket_number(ticket_number: str) → Complaint | None
    → SELECT avec JOIN sessions pour le contexte workflow

  update_status(id: UUID, status: str, agent_id: UUID, note: str) → Complaint
    → UPDATE + log dans complaint_status_history (V2)

  list_by_agent(agent_id: UUID, filters: dict) → List[Complaint]
    → Utilisé par le backoffice pour la file d'attente agent

  get_full_context(complaint_id: UUID) → dict
    → JOIN complaints + sessions + workflow_step_log + messages
    → Retourne tout le contexte pour l'agent backoffice

TECHNOLOGIE : SQLAlchemy 2.0 async, asyncpg
"""
