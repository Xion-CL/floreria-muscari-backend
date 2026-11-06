#!/usr/bin/env bash
# Script de build para Render (también sirve para desplegar manualmente).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Datos de demostración (catálogo, usuarios demo, pedidos). Es idempotente.
if [ "${SEED_DEMO:-true}" = "true" ]; then
  python manage.py seed_demo
fi

# Administrador del sitio (solo si ADMIN_PASSWORD está definida)
python manage.py crear_usuarios
