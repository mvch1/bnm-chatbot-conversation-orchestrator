"""
FICHIER : shared/repositories/agent_repository.py
RÔLE : Opérations sur la table agents (authentification et assignation).

MÉTHODES :
  get_by_email(email: str) → Agent | None
    → Authentification backoffice (recherche par email)

  get_available_agents(role: str = None) → List[Agent]
    → Agents avec status=AVAILABLE, optionnellement filtrés par rôle
    → Utilisé pour l'assignation automatique des escalades

  get_least_loaded_agent() → Agent | None
    → Agent disponible avec le moins de tickets OPEN assignés
    → Load balancing pour l'assignation automatique

  update_status(agent_id: UUID, status: str) → Agent
  update_last_login(agent_id: UUID) → None
  list_all(include_inactive: bool = False) → List[Agent]
    → Liste pour le dashboard superviseur

CONSEILS TECHNIQUES :
  - get_least_loaded_agent() utilise une sous-requête COUNT sur tickets
  - Cacher la liste des agents disponibles dans Redis (TTL 30s)
  - Index sur (status, is_active) pour les requêtes d'assignation

TECHNOLOGIE : SQLAlchemy 2.0 async, PostgreSQL
"""
