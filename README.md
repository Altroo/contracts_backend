# Contracts Backend

## Purpose

Contracts Backend is the Django API for contract document operations. It manages accounts, contracts, contract files, generated documents, notifications, and websocket events.

## Stack

- Python and Django
- Django REST Framework
- Simple JWT and dj-rest-auth
- django-filter
- Channels, Daphne, Redis, and Celery
- PostgreSQL
- ReportLab, WeasyPrint, OpenPyXL, and python-docx
- Pytest and pytest-django

## Features

- Contract creation and management APIs
- Contract document generation
- File and attachment handling
- User and permission management
- Notification and maintenance endpoints
- Real-time websocket integration

## Setup

Provide local-only variables for Django runtime settings, database, Redis, media storage, and allowed origins. Use localhost values for local development and do not commit local configuration files.

On macOS, make sure the native libraries used by WeasyPrint are available before starting the server.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

## Tests

```bash
python -m pytest
```

## Screenshot

![Contracts login](docs/screenshots/contracts-login.png)
