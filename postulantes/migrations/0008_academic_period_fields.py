from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('postulantes', '0007_alter_postulante_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='postulacion',
            name='anio_academico',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='postulacion',
            name='semestre_academico',
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, 'Primer semestre'), (2, 'Segundo semestre')],
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='postulacion',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='postulacion',
            constraint=models.UniqueConstraint(
                fields=['postulante', 'anio_academico', 'semestre_academico'],
                condition=Q(anio_academico__isnull=False, semestre_academico__isnull=False),
                name='uniq_postulante_periodo_academico',
            ),
        ),
    ]
