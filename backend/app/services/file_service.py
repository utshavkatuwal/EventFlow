import os
import secrets
from datetime import datetime
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.event import Event, EventCategory
from app.models.ticket import Ticket, TicketType, Registration
from app.models.other import EventReview, Favorite, Notification, AuditLog, Report, OrganizerProfile
from app.core.security import hash_password
from app.core.config import settings


def ensure_upload_dir():
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)


def save_uploaded_file(file, allowed_extensions=None, max_size=None):
    if allowed_extensions is None:
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    if max_size is None:
        max_size = settings.MAX_UPLOAD_SIZE

    import traceback
    try:
        file_content = file.read()
    except Exception:
        traceback.print_exc()

    if len(file_content) > max_size:
        raise ValueError(f"File size exceeds {max_size // (1024*1024)}MB limit")

    filename = file.filename
    if not filename:
        raise ValueError("No filename provided")

    _, ext = os.path.splitext(filename)
    if ext.lower() not in allowed_extensions:
        raise ValueError(f"File type {ext} not allowed")

    safe_name = secrets.token_hex(16) + ext
    filepath = os.path.join(settings.UPLOAD_DIRECTORY, safe_name)

    with open(filepath, 'wb') as f:
        f.write(file_content)

    return safe_name, filepath
