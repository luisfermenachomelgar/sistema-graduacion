from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0003_modalidadrequisito'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE modalidades_modalidadrequisito
                    ADD COLUMN IF NOT EXISTS obligatorio boolean NOT NULL DEFAULT true,
                    ADD COLUMN IF NOT EXISTS version varchar(50) NOT NULL DEFAULT '1.0',
                    ADD COLUMN IF NOT EXISTS observaciones text NOT NULL DEFAULT '',
                    ADD COLUMN IF NOT EXISTS created_at timestamp with time zone,
                    ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone;

                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'creada_en'
                    ) AND EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'created_at'
                    ) THEN
                        EXECUTE 'UPDATE modalidades_modalidadrequisito SET created_at = creada_en WHERE created_at IS NULL';
                    END IF;

                    IF EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'actualizada_en'
                    ) AND EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'updated_at'
                    ) THEN
                        EXECUTE 'UPDATE modalidades_modalidadrequisito SET updated_at = actualizada_en WHERE updated_at IS NULL';
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]