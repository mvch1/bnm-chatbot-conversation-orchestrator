from enum import Enum


class DialogState(str, Enum):
    GREETING = "GREETING"
    INTENT_DETECTION = "INTENT_DETECTION"
    FAQ_RESPONSE = "FAQ_RESPONSE"
    COMPLAINT_COLLECTION = "COMPLAINT_COLLECTION"
    COMPLAINT_CONFIRMATION = "COMPLAINT_CONFIRMATION"
    WALLET_VALIDATION = "WALLET_VALIDATION"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    CLOSED = "CLOSED"


TRANSITIONS = {
    DialogState.GREETING: [DialogState.INTENT_DETECTION],
    DialogState.INTENT_DETECTION: [
        DialogState.FAQ_RESPONSE,
        DialogState.COMPLAINT_COLLECTION,
        DialogState.WALLET_VALIDATION,
        DialogState.HUMAN_ESCALATION,
    ],
    DialogState.FAQ_RESPONSE: [DialogState.INTENT_DETECTION, DialogState.CLOSED],
    DialogState.COMPLAINT_COLLECTION: [DialogState.COMPLAINT_CONFIRMATION, DialogState.HUMAN_ESCALATION],
    DialogState.COMPLAINT_CONFIRMATION: [DialogState.CLOSED, DialogState.COMPLAINT_COLLECTION],
    DialogState.WALLET_VALIDATION: [DialogState.CLOSED, DialogState.HUMAN_ESCALATION],
    DialogState.HUMAN_ESCALATION: [DialogState.CLOSED],
    DialogState.CLOSED: [],
}


def can_transition(current: str, next_state: str) -> bool:
    try:
        return DialogState(next_state) in TRANSITIONS.get(DialogState(current), [])
    except ValueError:
        return False
