from django.db import migrations


def create_etapas(apps, schema_editor):
    """Crea las etapas para la modalidad Excelencia Académica usando el mismo mecanismo de las migraciones previas."""
    Modalidad = apps.get_model('modalidades', 'Modalidad')
    Etapa = apps.get_model('modalidades', 'Etapa')

    modalidad = Modalidad.objects.filter(nombre='Excelencia Académica').first()
    if not modalidad:
        return

    etapas = [
        {'orden': 1, 'nombre': 'Presentación de documentos'},
        {'orden': 2, 'nombre': 'Cumplimiento de requisitos'},
        {'orden': 3, 'nombre': 'Graduación aprobada'},
    ]

    for etapa_data in etapas:
        Etapa.objects.get_or_create(
            modalidad=modalidad,
            orden=etapa_data['orden'],
            defaults={
                'nombre': etapa_data['nombre'],
                'activo': True,
            },
        )

    # ========================================================================
    # 2. TESIS DE GRADO - 5 etapas
    # ========================================================================
    print("\n📌 Inserta o actualiza etapas para Tesis de Grado...")
    tesis = Modalidad.objects.filter(nombre__iexact='Tesis de Grado').first()
    if tesis is None:
        print("⚠️ Modalidad 'Tesis de Grado' no encontrada, omitiendo etapas.")
    else:
        # Evita conflictos de unique constraint en orden cuando se crean nuevas etapas.
        for etapa in Etapa.objects.filter(modalidad=tesis):
            etapa.orden = etapa.orden + 1000
            etapa.save()

        etapas_tesis = [
            {'orden': 1, 'nombre': 'Perfil de Tesis'},
            {'orden': 2, 'nombre': 'Documento Final'},
            {'orden': 3, 'nombre': 'Defensa Privada'},
            {'orden': 4, 'nombre': 'Defensa Pública'},
            {'orden': 5, 'nombre': 'Acta Final'},
        ]

        for etapa_data in etapas_tesis:
            etapa, created = Etapa.objects.update_or_create(
                modalidad=tesis,
                nombre=etapa_data['nombre'],
                defaults={
                    'orden': etapa_data['orden'],
                    'activo': True,
                },
            )
            status = "✓ CREADA" if created else "✓ ACTUALIZADA"
            print(f"  {status}: Orden {etapa_data['orden']} - {etapa_data['nombre']}")

        Etapa.objects.filter(modalidad=tesis).exclude(nombre__in=[et['nombre'] for et in etapas_tesis]).update(activo=False)


def reverse_etapas(apps, schema_editor):
    """Elimina las etapas creadas para la modalidad Excelencia Académica."""
    Etapa = apps.get_model('modalidades', 'Etapa')
    Etapa.objects.filter(
        modalidad__nombre='Excelencia Académica',
        nombre__in=[
            'Presentación de documentos',
            'Cumplimiento de requisitos',
            'Graduación aprobada',
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('modalidades', '0007_historial_cambio_modalidad'),
    ]

    operations = [
        migrations.RunPython(create_etapas, reverse_etapas),
    ]
