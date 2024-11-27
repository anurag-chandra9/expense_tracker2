#!/bin/sh
set -e

echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Build completed successfully!"
