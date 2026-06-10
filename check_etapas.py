#!/usr/bin/env python
"""Script para diagnosticar etapas y modalidades"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modalidades.models import Modalidad, Etapa

print("=" * 80)
print("MODALIDADES Y SUS ETAPAS")
print("=" * 80)

for modalidad in Modalidad.objects.prefetch_related('etapas'):
    print(f"\n📌 Modalidad: {modalidad.nombre} (ID: {modalidad.id}, Activa: {modalidad.activa})")
    etapas = modalidad.etapas.all()
    if etapas:
        for etapa in etapas:
            print(f"   • Orden {etapa.orden}: {etapa.nombre} (ID: {etapa.id}, Activo: {etapa.activo})")
    else:
        print("   (sin etapas)")

print("\n" + "=" * 80)
print("TODAS LAS ETAPAS (FORMATO TABLA)")
print("=" * 80)
print(f"{'ID':<4} {'Modalidad':<30} {'Etapa':<30} {'Orden':<5} {'Activo':<7}")
print("-" * 80)
for etapa in Etapa.objects.select_related('modalidad').order_by('modalidad__nombre', 'orden'):
    print(f"{etapa.id:<4} {etapa.modalidad.nombre:<30} {etapa.nombre:<30} {etapa.orden:<5} {str(etapa.activo):<7}")

print("\n" + "=" * 80)
