#!/usr/bin/env bash
set -euo pipefail

echo "Creating virtual environment .venv..."
python3 -m venv .venv

echo "Activating venv..."
source .venv/bin/activate

echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir -r requirements/pip-packages.txt

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Running tests..."
python manage.py test -v2

echo "Done. To run the server: python manage.py runserver 127.0.0.1:8000"
