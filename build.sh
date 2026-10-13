#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Crear o actualizar superusuario barrientos
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.filter(username='barrientos').first(); (u.set_password('barrientos.12345'), setattr(u, 'email', 'yosme@gmail.com'), u.save()) if u else User.objects.create_superuser('barrientos', 'yosme@gmail.com', 'barrientos.12345')"