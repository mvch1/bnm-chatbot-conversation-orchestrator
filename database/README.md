# Database

Modèles SQLAlchemy pour la plateforme banking chatbot.

## Entités

| Entité          | Description                                              |
|-----------------|----------------------------------------------------------|
| `User`          | Utilisateur/client identifié par son numéro de téléphone |
| `Session`       | Session de conversation liée à un User                   |
| `Message`       | Message individuel (entrant ou sortant) d'une Session    |
| `Intent`        | Catalogue de référence des intents connus                |
| `IntentMessage` | Résultat de classification d'un Message par l'intent service |
| `Agent`         | Agent humain pouvant prendre en charge une escalade      |
| `Ticket`        | Ticket de support lié à une Session et un Agent          |

## Relations

```
User ──< Session ──< Message ──── IntentMessage ──> Intent
                  └──< Ticket ──> Agent
```

## Installation

```bash
pip install -r database/requirements.txt
```

## Initialisation (développement)

```python
import asyncio
from database.db import init_db

asyncio.run(init_db())
```

## Utilisation

```python
from database import get_db, User, Session

async with get_db() as db:
    user = User(phone="22200000000", name="Alice")
    db.add(user)
    # commit is automatic at context exit
```

## Variables d'environnement

| Variable       | Défaut                                                                     |
|----------------|---------------------------------------------------------------------------|
| `DATABASE_URL` | `postgresql+asyncpg://chatbot_user:motdepasse@postgresql:5432/banking_chatbot` |
