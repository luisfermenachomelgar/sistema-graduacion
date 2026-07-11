from django.db import migrations


def migrate_administ_to_admin(apps, schema_editor):
    CustomUser = apps.get_model('usuarios', 'CustomUser')
    CustomUser.objects.filter(role='administ').update(role='admin')


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0002_alter_customuser_role'),
    ]

    operations = [
        migrations.RunPython(migrate_administ_to_admin, migrations.RunPython.noop),
    ]
