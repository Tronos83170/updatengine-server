<#
PowerShell bootstrap script for UpdatEngine development on Windows.
Usage: run from repository root (D:\UE)

.
#>
param()

Write-Output "Creating virtual environment .venv..."
python -m venv .venv

Write-Output "Activating venv and upgrading pip..."
. \.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel

Write-Output "Installing requirements..."
python -m pip install --no-cache-dir -r requirements\pip-packages.txt

Write-Output "Applying migrations..."
python manage.py migrate --noinput

Write-Output "Running tests..."
python manage.py test -v2

Write-Output "Done. To run the server: python manage.py runserver 127.0.0.1:8000"
