"""Deprecated: event creation lives in `events_router.POST /events` (Phase 3).

Kept as an import-safe stub so old imports don't break. No routes registered
here to avoid duplicate OpenAPI entries / shadowing.
"""
from fastapi import APIRouter

api_router = APIRouter(tags=["Events (deprecated)"])
