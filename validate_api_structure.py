#!/usr/bin/env python
"""
Script para validar estructura de endpoints
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '.')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from postulantes.views import PostulacionViewSet
from documentos.views import DocumentoPostulacionViewSet

User = get_user_model()

print("\n" + "="*80)
print("VALIDACION DE ESTRUCTURA DE API - POSTULACIONES Y DOCUMENTOS")
print("="*80 + "\n")

user = User.objects.first()
if not user:
    print("No hay usuarios en la base de datos")
    exit(1)

print(f"Usando usuario: {user.username}\n")

# TEST 1: PostulacionViewSet
print("1. VALIDANDO /api/postulaciones/?page_size=5")
print("-" * 80)

factory = APIRequestFactory()
request = factory.get('/api/postulaciones/?page_size=5')
request = force_authenticate(request, user=user)

viewset = PostulacionViewSet.as_view({'get': 'list'})
response = viewset(request)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.data
    print(f"Estructura raiz: {list(data.keys())}")
    print(f"  - count: {data.get('count')} (total de registros)")
    print(f"  - next: {type(data.get('next')).__name__}")
    print(f"  - previous: {type(data.get('previous')).__name__}")
    print(f"  - results: tipo {type(data.get('results')).__name__} con {len(data.get('results', []))} items\n")
    
    if data.get('results'):
        print("Campos en primer registro de postulacion:")
        first_record = data['results'][0]
        for campo in sorted(first_record.keys()):
            valor = first_record[campo]
            print(f"  - {campo}: {type(valor).__name__}")

print("\n" + "="*80)
print("2. VALIDANDO /api/documentos/?page_size=5")
print("-" * 80)

request = factory.get('/api/documentos/?page_size=5')
request = force_authenticate(request, user=user)

viewset = DocumentoPostulacionViewSet.as_view({'get': 'list'})
response = viewset(request)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.data
    print(f"Estructura raiz: {list(data.keys())}")
    print(f"  - count: {data.get('count')} (total de registros)")
    print(f"  - next: {type(data.get('next')).__name__}")
    print(f"  - previous: {type(data.get('previous')).__name__}")
    print(f"  - results: tipo {type(data.get('results')).__name__} con {len(data.get('results', []))} items\n")
    
    if data.get('results'):
        print("Campos en primer registro de documento:")
        first_record = data['results'][0]
        for campo in sorted(first_record.keys()):
            valor = first_record[campo]
            print(f"  - {campo}: {type(valor).__name__}")

print("\n" + "="*80)
print("CONCLUSIONES:")
print("="*80 + "\n")
