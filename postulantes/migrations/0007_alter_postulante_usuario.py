from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('postulantes', '0006_alter_postulante_options_alter_postulacion_tutor_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='postulante',
            name='usuario',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='perfil_postulante',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]