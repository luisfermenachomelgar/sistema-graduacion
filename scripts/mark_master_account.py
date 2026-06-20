#!/usr/bin/env python
"""
Script para marcar la cuenta maestra existente.
Usa `is_superuser=True` por defecto.

Ejecutar desde el workspace con Django configurado:

python scripts/mark_master_account.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from usuarios.models import CustomUser

USERNAME = 'admin'

try:
    user = CustomUser.objects.get(username=USERNAME)
    changed = False
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    if changed:
        user.save()
        print(f"✅ Usuario '{USERNAME}' marcado como cuenta maestra (is_superuser).")
    else:
        print(f"ℹ️  Usuario '{USERNAME}' ya estaba marcado como maestro (is_superuser).")
except CustomUser.DoesNotExist:
    print(f"❌ Usuario '{USERNAME}' no existe. No se realizaron cambios.")
except Exception as e:
    print(f"❌ Error: {e}")
