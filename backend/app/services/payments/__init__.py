"""Payment providers registry (Phase 5). Add new providers here."""
from app.services.payments.base import PaymentError, PaymentProvider
from app.services.payments.esewa import EsewaProvider
from app.services.payments.khalti import KhaltiProvider


def get_provider(name: str) -> PaymentProvider:
    key = (name or "").upper()
    if key == "ESEWA":
        return EsewaProvider()
    if key == "KHALTI":
        return KhaltiProvider()
    raise PaymentError(f"Unknown provider '{name}'. Choose eSewa or Khalti.", 400)


__all__ = ["PaymentError", "PaymentProvider", "get_provider"]
