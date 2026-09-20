@echo off
cd C:\Projects\EventFlow\backend
python -m hypercorn app.main:app --bind 127.0.0.1:8000 --log-level info