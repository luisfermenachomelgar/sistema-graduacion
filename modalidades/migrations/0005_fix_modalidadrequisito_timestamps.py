from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0004_repair_modalidadrequisito_schema'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'creada_en'
                    ) AND EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'created_at'
                    ) THEN
                        UPDATE modalidades_modalidadrequisito
                        SET created_at = creada_en
                        WHERE created_at IS NULL;

                        ALTER TABLE modalidades_modalidadrequisito
                        DROP COLUMN creada_en;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'actualizada_en'
                    ) AND EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'updated_at'
                    ) THEN
                        UPDATE modalidades_modalidadrequisito
                        SET updated_at = actualizada_en
                        WHERE updated_at IS NULL;

                        ALTER TABLE modalidades_modalidadrequisito
                        DROP COLUMN actualizada_en;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'created_at'
                    ) THEN
                        ALTER TABLE modalidades_modalidadrequisito
                        ALTER COLUMN created_at SET NOT NULL;
                    END IF;

                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'modalidades_modalidadrequisito'
                          AND column_name = 'updated_at'
                    ) THEN
                        ALTER TABLE modalidades_modalidadrequisito
                        ALTER COLUMN updated_at SET NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
