"""
FICHIER : shared/repositories/base_repository.py
RÔLE : Classe abstraite de base pour tous les repositories.
       Implémente les opérations CRUD communes.

PATTERN : Repository Pattern — sépare la logique métier de l'accès aux données.
          Chaque service utilise les repositories au lieu d'écrire du SQL direct.

MÉTHODES ABSTRAITES :
  get_by_id(id: UUID) → Model | None
  create(data: dict)  → Model
  update(id: UUID, data: dict) → Model
  delete(id: UUID)    → bool
  list(filters: dict, page: int, per_page: int) → List[Model]

AVANTAGES :
  - Testabilité : on peut mocker le repository dans les tests unitaires
  - Cohérence : toutes les opérations DB passent par le même endroit
  - Évolutivité : changer PostgreSQL pour MongoDB = changer uniquement les repositories

TECHNOLOGIE : SQLAlchemy 2.0 async, Python ABC
"""
