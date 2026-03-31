# Shared — Bibliothèque partagée entre les microservices

## Rôle
Centralise le code commun à tous les microservices pour éviter la duplication.
Inclut les modèles de données, les utilitaires et les constantes.

## Contenu
- models/ : Classes SQLAlchemy communes (User, Message, Session)
- utils/ : Logger, validateurs, formateurs
- constants/ : Énumérations partagées (intents, statuts)

## Utilisation
Chaque service installe ce package en dépendance locale :
  pip install -e ../../shared

## Règle importante
Ne jamais ajouter de logique métier spécifique à un service dans shared/.
Uniquement du code véritablement partagé par 2+ services.
