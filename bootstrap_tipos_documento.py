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

OLD_ACTA_DEFENSA_NAME = 'Comprobante de Defensa'
NEW_ACTA_DEFENSA_NAME = 'Acta de Defensa de Tesis o de Modalidad de Graduación'

# Crear tipos básicos sin relacionar a etapas/modalidades
tipos = [
    {'nombre': 'Propuesta de Tesis', 'descripcion': 'Documento inicial de propuesta'},
    {'nombre': 'Certificado Académico', 'descripcion': 'Certificado de calificaciones'},
    {'nombre': 'CV del Estudiante', 'descripcion': 'Currículum vitae del postulante'},
    {'nombre': 'Carta de Aceptación', 'descripcion': 'Carta de aceptación del tutor'},
    {'nombre': 'Perfil de Tesis', 'descripcion': 'Perfil detallado del trabajo'},
    {'nombre': 'Documento de Avance', 'descripcion': 'Documento que muestra el avance del trabajo'},
    {'nombre': 'Documento Final', 'descripcion': 'Documento final/conclusión del trabajo'},
    {'nombre': NEW_ACTA_DEFENSA_NAME, 'descripcion': 'Comprobante de defensa realizada'},
]

print("\n" + "="*70)
print("CREANDO TIPOS DE DOCUMENTO")
print("="*70)

def rename_existing_acta_defensa():
    old = TipoDocumento.objects.filter(nombre=OLD_ACTA_DEFENSA_NAME).first()
    if not old:
        return

    existing_new = TipoDocumento.objects.filter(nombre=NEW_ACTA_DEFENSA_NAME).first()
    if existing_new and existing_new.id != old.id:
        print(
            f"Advertencia: existe '{OLD_ACTA_DEFENSA_NAME}' (id={old.id}) y "
            f"'{NEW_ACTA_DEFENSA_NAME}' (id={existing_new.id}); no se renombra automáticamente."
        )
        return

    old.nombre = NEW_ACTA_DEFENSA_NAME
    old.save(update_fields=['nombre'])
    print(f"Renombrado: '{OLD_ACTA_DEFENSA_NAME}' -> '{NEW_ACTA_DEFENSA_NAME}' (id={old.id})")


rename_existing_acta_defensa()

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
