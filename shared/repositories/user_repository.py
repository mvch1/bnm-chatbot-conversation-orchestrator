"""
FICHIER : shared/repositories/user_repository.py
RÔLE : Toutes les opérations de base de données sur la table users.

MÉTHODES :
  get_by_id(id: UUID) → User | None
  get_by_phone(phone: str) → User | None
    → Recherche par numéro WhatsApp (cas d'usage le plus fréquent)
  create(phone: str, name: str = None) → User
    → Crée un nouvel utilisateur avec normalisation du numéro (E.164)
  update_last_seen(user_id: UUID) → None
    → Met à jour last_seen_at à chaque message entrant
  block(user_id: UUID) → None
  is_blocked(phone: str) → bool
    → Vérifié avant tout traitement d'un message entrant

REQUÊTES OPTIMISÉES :
  get_by_phone utilise l'index idx_users_phone → O(log n)

CONSEILS TECHNIQUES :
  - Toutes les méthodes sont async (asyncpg)
  - Normaliser le numéro en E.164 dans create() avant insertion
  - Utiliser SELECT FOR UPDATE dans les opérations de mise à jour concurrentes

TECHNOLOGIE : SQLAlchemy 2.0 async, asyncpg, PostgreSQL
"""
