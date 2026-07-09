from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0010_cleanup_examen_grado_documentos_per_stage'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentopostulacion',
            name='preview_pdf',
            field=models.FileField(blank=True, null=True, upload_to='documentos/previews/'),
        ),
    ]
