# Development setup (Windows / Linux)

This README shows how to bootstrap the project for local development.

Prerequisites
- Python 3.10+ (3.11 recommended)
- Git
- On Windows: PowerShell
- On Linux/macOS: bash

Quick start (Windows, PowerShell)

1. Create a virtual environment and install dependencies:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
    .\.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements\pip-packages.txt

2. Apply migrations and run tests:

    .\.venv\Scripts\python.exe manage.py migrate --noinput
    .\.venv\Scripts\python.exe manage.py test -v2

3. Start development server:

    .\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

Quick start (Linux/macOS)

1. Create a virtual environment and install dependencies:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install --no-cache-dir -r requirements/pip-packages.txt

2. Apply migrations and run tests:

    python manage.py migrate --noinput
    python manage.py test -v2

3. Start development server:

    python manage.py runserver 127.0.0.1:8000

Useful helpers
- `scripts/boot.ps1` - PowerShell bootstrap helper (Windows)
- `scripts/boot.sh` - Bash bootstrap helper (Linux/macOS)
- `python manage.py statuscheck` - management command that checks DB/migrations availability

Notes
- `updatengine/settings_local.py` is ignored by git. Put local overrides there if needed.
- The project is configured to use SQLite for test/dev via `updatengine/settings_local.py` already added to the repo.
