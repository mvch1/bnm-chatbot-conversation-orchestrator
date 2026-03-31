import re
from decimal import Decimal, InvalidOperation
from typing import Optional


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format."""
    digits = re.sub(r'\D', '', phone)
    if not digits.startswith('222') and len(digits) == 8:
        digits = '222' + digits
    if not digits.startswith('+'):
        digits = '+' + digits
    return digits


def validate_cin(cin: str) -> bool:
    """Validate Mauritanian CIN format (10 digits)."""
    return bool(re.match(r'^\d{10}$', cin.strip()))


def parse_amount(text: str) -> Optional[Decimal]:
    """Parse amount from user text input."""
    cleaned = re.sub(r'[^\d.,]', '', text.replace(' ', ''))
    cleaned = cleaned.replace(',', '.')
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def validate_amount(text: str) -> bool:
    return parse_amount(text) is not None
