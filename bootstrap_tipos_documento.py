#!/usr/bin/env python
"""
Script para crear datos iniciales de TipoDocumento
Ejecutar: python manage.py shell < bootstrap_tipos_documento.py
O dentro del contenedor: docker exec -i sistema_backend python bootstrap_tipos_documento.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from documentos.models import TipoDocumento

# Crear tipos básicos sin relacionar a etapas/modalidades
tipos = [
    {'nombre': 'Propuesta de Tesis', 'descripcion': 'Documento inicial de propuesta'},
    {'nombre': 'Certificado Académico', 'descripcion': 'Certificado de calificaciones'},
    {'nombre': 'CV del Estudiante', 'descripcion': 'Currículum vitae del postulante'},
    {'nombre': 'Carta de Aceptación', 'descripcion': 'Carta de aceptación del tutor'},
    {'nombre': 'Perfil de Tesis', 'descripcion': 'Perfil detallado del trabajo'},
    {'nombre': 'Documento de Avance', 'descripcion': 'Documento que muestra el avance del trabajo'},
    {'nombre': 'Documento Final', 'descripcion': 'Documento final/conclusión del trabajo'},
    {'nombre': 'Comprobante de Defensa', 'descripcion': 'Comprobante de defensa realizada'},
]

print("\n" + "="*70)
print("CREANDO TIPOS DE DOCUMENTO")
print("="*70)

for tipo_data in tipos:
    obj, created = TipoDocumento.objects.get_or_create(
        nombre=tipo_data['nombre'],
        defaults={
            'descripcion': tipo_data['descripcion'],
            'obligatorio': True,
            'activo': True,
            'etapa': None,
        }
    )
    status = '✓ Creado' if created else '✓ Existe'
    print(f"{status}: {obj.nombre}")

total = TipoDocumento.objects.count()
print(f"\n✅ Total tipos de documento: {total}\n")
