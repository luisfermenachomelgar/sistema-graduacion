#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulante, Postulacion
from usuarios.models import CustomUser

# Verificar test_user
try:
    u = CustomUser.objects.get(username='test_user')
    print(f"✓ Usuario encontrado: {u.username}")
except CustomUser.DoesNotExist:
    print("✗ Usuario test_user no existe")
    exit(1)

# Buscar postulante relacionado
postulante = Postulante.objects.filter(usuario=u).first()
if postulante:
    print(f"✓ Postulante relacionado: {postulante}")
    posts = Postulacion.objects.filter(postulante=postulante)
    print(f"  → Postulaciones: {posts.count()}")
    if posts.exists():
        for p in posts:
            print(f"    - {p}")
else:
    print("✗ Sin postulante relacionado a test_user")
    print("\n✓ Postulaciones globales disponibles:")
    for p in Postulacion.objects.all()[:3]:
        print(f"  - {p} (postulante: {p.postulante.usuario})")
