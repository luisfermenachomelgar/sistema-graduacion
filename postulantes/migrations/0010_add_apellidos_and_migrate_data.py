from django.db import migrations, models


def forward_split_apellido(apps, schema_editor):
    Postulante = apps.get_model('postulantes', 'Postulante')
    for p in Postulante.objects.all():
        # Try to read legacy 'apellido' value from the instance (database may still have column)
        apellido = None
        try:
            apellido = getattr(p, 'apellido')
        except Exception:
            apellido = None
        if not apellido:
            continue
        apellido = apellido.strip()
        if not apellido:
            continue
        parts = apellido.split()
        if len(parts) >= 2:
            paterno = parts[0]
            materno = ' '.join(parts[1:])
        else:
            paterno = apellido
            materno = ''
        # Use update to avoid calling model save hooks
        Postulante.objects.filter(pk=p.pk).update(apellido_paterno=paterno, apellido_materno=materno)


def reverse_join_apellido(apps, schema_editor):
    # On reverse, join paterno and materno into legacy 'apellido' if present
    Postulante = apps.get_model('postulantes', 'Postulante')
    for p in Postulante.objects.all():
        paterno = getattr(p, 'apellido_paterno', '') or ''
        materno = getattr(p, 'apellido_materno', '') or ''
        combined = (paterno + ' ' + materno).strip()
        # If legacy column exists, try to set it
        try:
            Postulante.objects.filter(pk=p.pk).update(apellido=combined)
        except Exception:
            # If the legacy column doesn't exist, skip
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('postulantes', '0009_historial_cambio_modalidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='postulante',
            name='apellido_paterno',
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.AddField(
            model_name='postulante',
            name='apellido_materno',
            field=models.CharField(max_length=150, blank=True),
        ),
        migrations.RunPython(forward_split_apellido, reverse_join_apellido),
    ]
