#!/usr/bin/env python
"""
Diagnóstico: Comparar flujos de Examen de Grado vs Proyecto de Grado.

Esto identifica por qué Proyecto de Grado permite avanzar sin validar documentos.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modalidades.models import Modalidad, Etapa
from documentos.models import ModalidadTipoDocumento, TipoDocumento
from postulantes.models import Postulacion


def compare_modalidades():
    print("="*80)
    print("DIAGNÓSTICO: COMPARACIÓN ENTRE EXAMEN DE GRADO Y PROYECTO DE GRADO")
    print("="*80)

    # 1. Obtener modalidades
    examen = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    proyecto = Modalidad.objects.filter(nombre__iexact='PROYECTO DE GRADO').first()

    if not examen:
        print("❌ Modalidad 'EXAMEN DE GRADO' no encontrada")
        return
    if not proyecto:
        print("❌ Modalidad 'PROYECTO DE GRADO' no encontrada")
        return

    print(f"\n✅ Examen de Grado (ID: {examen.id})")
    print(f"✅ Proyecto de Grado (ID: {proyecto.id})")

    # 2. Comparar etapas
    print("\n" + "="*80)
    print("ETAPAS")
    print("="*80)

    print("\nEXAMEN DE GRADO:")
    etapas_examen = Etapa.objects.filter(modalidad=examen, activo=True).order_by('orden')
    for etapa in etapas_examen:
        print(f"  Orden {etapa.orden}: {etapa.nombre}")

    print("\nPROYECTO DE GRADO:")
    etapas_proyecto = Etapa.objects.filter(modalidad=proyecto, activo=True).order_by('orden')
    for etapa in etapas_proyecto:
        print(f"  Orden {etapa.orden}: {etapa.nombre}")

    # 3. Comparar documentos obligatorios por etapa
    print("\n" + "="*80)
    print("DOCUMENTOS OBLIGATORIOS POR ETAPA")
    print("="*80)

    print("\nEXAMEN DE GRADO:")
    for etapa in etapas_examen:
        mtds = ModalidadTipoDocumento.objects.filter(
            modalidad=examen,
            etapa=etapa,
            obligatorio=True,
            activo=True
        ).order_by('orden')
        if mtds.exists():
            print(f"  [{etapa.nombre}]")
            for mtd in mtds:
                print(f"    - {mtd.tipo_documento.nombre} (activo={mtd.activo}, obligatorio={mtd.obligatorio})")
        else:
            print(f"  [{etapa.nombre}] ⚠️ SIN DOCUMENTOS OBLIGATORIOS")

    print("\nPROYECTO DE GRADO:")
    for etapa in etapas_proyecto:
        mtds = ModalidadTipoDocumento.objects.filter(
            modalidad=proyecto,
            etapa=etapa,
            obligatorio=True,
            activo=True
        ).order_by('orden')
        if mtds.exists():
            print(f"  [{etapa.nombre}]")
            for mtd in mtds:
                print(f"    - {mtd.tipo_documento.nombre} (activo={mtd.activo}, obligatorio={mtd.obligatorio})")
        else:
            print(f"  [{etapa.nombre}] ⚠️ SIN DOCUMENTOS OBLIGATORIOS")

    # 4. Documentos globales (etapa=None) para cada modalidad
    print("\n" + "="*80)
    print("DOCUMENTOS GLOBALES (aplican a todas las etapas)")
    print("="*80)

    print("\nEXAMEN DE GRADO:")
    mtds_global_examen = ModalidadTipoDocumento.objects.filter(
        modalidad=examen,
        etapa__isnull=True,
        obligatorio=True,
        activo=True
    )
    if mtds_global_examen.exists():
        for mtd in mtds_global_examen:
            print(f"  - {mtd.tipo_documento.nombre}")
    else:
        print("  (ninguno)")

    print("\nPROYECTO DE GRADO:")
    mtds_global_proyecto = ModalidadTipoDocumento.objects.filter(
        modalidad=proyecto,
        etapa__isnull=True,
        obligatorio=True,
        activo=True
    )
    if mtds_global_proyecto.exists():
        for mtd in mtds_global_proyecto:
            print(f"  - {mtd.tipo_documento.nombre}")
    else:
        print("  (ninguno)")

    # 5. Verificar si la configuración está activa
    print("\n" + "="*80)
    print("CONFIGURACIÓN GENERAL")
    print("="*80)

    print(f"\nEXAMEN DE GRADO:")
    print(f"  - Modalidad activa: {examen.activo}")
    print(f"  - Etapas activas: {etapas_examen.count()}")
    print(f"  - Total ModalidadTipoDocumento: {ModalidadTipoDocumento.objects.filter(modalidad=examen).count()}")
    print(f"  - ModalidadTipoDocumento obligatorios y activos: {ModalidadTipoDocumento.objects.filter(modalidad=examen, obligatorio=True, activo=True).count()}")

    print(f"\nPROYECTO DE GRADO:")
    print(f"  - Modalidad activa: {proyecto.activo}")
    print(f"  - Etapas activas: {etapas_proyecto.count()}")
    print(f"  - Total ModalidadTipoDocumento: {ModalidadTipoDocumento.objects.filter(modalidad=proyecto).count()}")
    print(f"  - ModalidadTipoDocumento obligatorios y activos: {ModalidadTipoDocumento.objects.filter(modalidad=proyecto, obligatorio=True, activo=True).count()}")

    # 6. Simulación de validación
    print("\n" + "="*80)
    print("SIMULACIÓN: ¿QUÉ DOCUMENTOS SE NECESITARÍAN EN CADA ETAPA?")
    print("="*80)

    from postulantes.services import required_documents_missing

    print("\nCreando postulaciones de prueba (sin guardar)...")

    # Para Examen de Grado, orden 1 (Inscripción)
    etapa_examen_1 = Etapa.objects.filter(modalidad=examen, orden=1, activo=True).first()
    if etapa_examen_1:
        print(f"\n✅ EXAMEN DE GRADO - Etapa '{etapa_examen_1.nombre}':")
        p_examen = Postulacion(modalidad=examen, etapa_actual=etapa_examen_1)
        missing_examen = required_documents_missing(p_examen)
        if missing_examen:
            print(f"   Documentos faltantes: {len(missing_examen)}")
            for doc in missing_examen:
                print(f"     - {doc['nombre']} ({doc['motivo']})")
        else:
            print("   ✓ Sin documentos faltantes (permite avanzar)")

    # Para Proyecto de Grado, orden 1 (Propuesta/Perfil)
    etapa_proyecto_1 = Etapa.objects.filter(modalidad=proyecto, orden=1, activo=True).first()
    if etapa_proyecto_1:
        print(f"\n✅ PROYECTO DE GRADO - Etapa '{etapa_proyecto_1.nombre}':")
        p_proyecto = Postulacion(modalidad=proyecto, etapa_actual=etapa_proyecto_1)
        missing_proyecto = required_documents_missing(p_proyecto)
        if missing_proyecto:
            print(f"   Documentos faltantes: {len(missing_proyecto)}")
            for doc in missing_proyecto:
                print(f"     - {doc['nombre']} ({doc['motivo']})")
        else:
            print("   ⚠️  Sin documentos faltantes (permite avanzar) - ESTE ES EL PROBLEMA")

    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)
    print("\nSi PROYECTO DE GRADO muestra '✓ Sin documentos faltantes', entonces:")
    print("→ La configuración de ModalidadTipoDocumento NO está completa en la BD")
    print("→ O los documentos están configurados pero con activo=False")
    print("→ Necesita ejecutarse el bootstrap o una migración para poblar los datos")


if __name__ == '__main__':
    compare_modalidades()
