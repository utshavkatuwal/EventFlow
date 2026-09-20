# EventFlow Backend

A comprehensive backend for the EventFlow event management platform.

## Features

- REST API with FastAPI
- User authentication (JWT)
- Event CRUD and search
- Registration and ticketing
- QR check-in
- Admin moderation
- Organizer dashboard

## Requirements

- Python 3.11+
- MySQL 8.0+

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload --port 8000
```
