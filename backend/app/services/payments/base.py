"""Provider-independent payment interface (Phase 5)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class PaymentError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class InitiateResult:
    """What the frontend needs to redirect the buyer to the provider."""

    provider: str
    transaction_id: str
    amount: float
    action_url: str | None = None
    fields: dict[str, Any] | None = None  # form-post (eSewa) or redirect info
    payment_url: str | None = None  # full-redirect (Khalti)
    extra: dict[str, Any] | None = None


class PaymentProvider(ABC):
    name: str

    @abstractmethod
    def initiate(self, *, amount: float, transaction_id: str, registration_id: int,
                 event_title: str, return_urls: dict[str, str]) -> InitiateResult:
        """Create a pending provider-side transaction. No money moves yet."""

    @abstractmethod
    def verify(self, *, expected_amount: float, transaction_id: str,
               payload: dict[str, Any]) -> dict[str, Any]:
        """Server-side verification. Returns provider receipt dict.

        MUST raise PaymentError when the transaction is not genuinely complete.
        Never trust the browser — always check signatures / provider APIs here.
        """
