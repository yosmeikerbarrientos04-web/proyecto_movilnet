#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Crear superusuario si no existe
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='barrientos').exists() or User.objects.create_superuser('barrientos', 'yosmeikerbarrientos04@gmail.com', 'barriento12345.')"