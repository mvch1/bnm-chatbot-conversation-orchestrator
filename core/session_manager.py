from typing import Optional, Dict, Any

from database.repository import (
    get_session_by_phone,
    create_session,
    update_session,
    delete_session,
)
from shared.constants import DialogState


class SessionManager:
    """
    Manages conversation sessions stored in PostgreSQL (via the Session entity).

    The session is represented as a plain dict with the following keys:
        session_id      : str  — UUID of the DB Session row
        user_phone      : str  — phone number of the user
        state           : str  — current DialogState value
        collected_data  : dict — arbitrary data collected during the conversation
        step_index      : int  — current step within a workflow
        created_at      : str  — ISO-8601 creation timestamp
        updated_at      : str  — ISO-8601 last-update timestamp
    """

    # No Redis connection needed — all state lives in PostgreSQL.

    async def get(self, phone: str) -> Optional[Dict[str, Any]]:
        return await get_session_by_phone(phone)

    async def create(self, phone: str, session_id: str) -> Dict[str, Any]:
        return await create_session(phone, session_id)

    async def save(self, phone: str, session: Dict[str, Any]) -> None:
        await update_session(phone, session)

    async def update_state(self, phone: str, state: DialogState) -> None:
        session = await self.get(phone)
        if session:
            session["state"] = state.value
            await self.save(phone, session)

    async def update_collected_data(self, phone: str, key: str, value: Any) -> None:
        session = await self.get(phone)
        if session:
            session["collected_data"][key] = value
            await self.save(phone, session)

    async def delete(self, phone: str) -> None:
        await delete_session(phone)
