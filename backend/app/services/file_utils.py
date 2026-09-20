import os
import secrets
from datetime import datetime
import shutil


def is_safe_filename(filename: str) -> bool:
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    basename = os.path.basename(filename)
    return all(c in allowed for c in basename) and not basename.startswith(".")


def generate_safe_filename(original: str) -> str:
    ext = os.path.splitext(original)[1]
    return secrets.token_hex(16) + ext


def sanitize_filename(filename: str) -> str:
    return os.path.basename(filename).replace(" ", "_")


def validate_file_extension(filename: str, allowed: set) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed


def validate_file_size(file_path: str, max_bytes: int) -> bool:
    return os.path.getsize(file_path) <= max_bytes


def cleanup_uploads(directory: str):
    if os.path.exists(directory):
        for f in os.listdir(directory):
            filepath = os.path.join(directory, f)
            if os.path.isfile(filepath) and not f.startswith("."):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
