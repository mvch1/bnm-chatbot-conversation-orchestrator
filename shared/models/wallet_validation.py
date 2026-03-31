"""
FICHIER : shared/models/wallet_validation.py
RÔLE : Modèle SQLAlchemy pour la table wallet_validation_request.

Demandes de validation de compte Click Wallet :
  - phone_number   : numéro à valider (peut différer du numéro WhatsApp)
  - cin_number     : numéro CIN collecté à l'étape 1
  - document_path  : chemin MinIO de la photo CIN uploadée
  - document_type  : CIN / PASSEPORT / TITRE_SEJOUR
  - status         : PENDING → UNDER_REVIEW → APPROVED / REJECTED
  - reviewed_by    : agent examinateur (FK → agents)
  - reviewed_at    : date de décision (calcul SLA 24-48h)
  - rejection_reason : motif si REJECTED
  - attempt_number : compteur de tentatives (re-soumission après rejet)

CONTRAINTE : UNIQUE sur session_id (1 demande par session)

RELATIONS :
  user_id    → users.id
  session_id → sessions.id  [UNIQUE]
  ticket_id  → tickets.id
  reviewed_by → agents.id

USAGE :
  - Suivi du cycle de vie complet d'une validation wallet
  - Notification automatique au client à l'approbation/rejet
  - Tableau de bord superviseur (volume, délais, taux d'approbation)

TECHNOLOGIE : SQLAlchemy 2.0, PostgreSQL
"""
