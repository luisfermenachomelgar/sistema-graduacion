from django.db import migrations, models


def forward_split_apellido(apps, schema_editor):
    Postulante = apps.get_model('postulantes', 'Postulante')
    for postulante in Postulante.objects.all():
        apellido = getattr(postulante, 'apellido', None)
        if not apellido:
            continue
        parts = str(apellido).strip().split()
        if len(parts) >= 2:
            paterno = parts[0]
            materno = ' '.join(parts[1:])
        else:
            paterno = str(apellido).strip()
            materno = ''
        Postulante.objects.filter(pk=postulante.pk).update(
            apellido_paterno=paterno,
            apellido_materno=materno,
        )


def reverse_join_apellido(apps, schema_editor):
    Postulante = apps.get_model('postulantes', 'Postulante')
    for postulante in Postulante.objects.all():
        paterno = getattr(postulante, 'apellido_paterno', '') or ''
        materno = getattr(postulante, 'apellido_materno', '') or ''
        combined = (paterno + ' ' + materno).strip()
        Postulante.objects.filter(pk=postulante.pk).update(apellido=combined)


class Migration(migrations.Migration):

    dependencies = [
        ('postulantes', '0010_add_apellidos_and_migrate_data'),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop),
    ]
