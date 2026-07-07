# Script para asegurar que la modalidad EXAMEN DE GRADO tenga la etapa 'Registro' y el orden requerido.
# Ejecución recomendada desde el virtualenv del proyecto:
# .\.venv\Scripts\python.exe manage.py shell -c "exec(open('scripts/ensure_examen_registro.py').read())"

from django.db import transaction

Modalidad = None
Etapa = None

try:
    from modalidades.models import Modalidad as _Modalidad, Etapa as _Etapa
    Modalidad = _Modalidad
    Etapa = _Etapa
except Exception as e:
    print('Error importando modelos:', e)
    raise

ETAPAS_OBJETIVO = [
    (1, 'Registro'),
    (2, 'Examen 1 – Ciencias Básicas y Matemáticas'),
    (3, 'Examen 2 – Ciencias Sociales y Humanísticas'),
    (4, 'Examen 3 – Ciencias de la Ingeniería'),
    (5, 'Examen 4 – Ingeniería Aplicada'),
    (6, 'Acta de Calificación'),
    (7, 'Acta Final'),
]

with transaction.atomic():
    examen = Modalidad.objects.filter(nombre__iexact='EXAMEN DE GRADO').first()
    if not examen:
        print("Modalidad 'EXAMEN DE GRADO' no encontrada. Verifica nombres en la tabla Modalidad.")
        raise SystemExit(1)

    print('Modalidad encontrada:', examen.nombre, 'id=', examen.id)

    # Evitar conflictos de unique constraint (modalidad, orden) moviendo órdenes existentes fuera del rango.
    updated = 0
    for e in Etapa.objects.filter(modalidad=examen):
        e.orden = (e.orden or 0) + 1000
        e.save(update_fields=['orden'])
        updated += 1
    print(f'Mover órdenes existentes +1000 -> {updated} filas actualizadas')

    nombres_objetivo = []
    for orden, nombre in ETAPAS_OBJETIVO:
        etapa, created = Etapa.objects.update_or_create(
            modalidad=examen,
            nombre=nombre,
            defaults={
                'orden': orden,
                'activo': True,
            },
        )
        nombres_objetivo.append(nombre)
        print(('Creada' if created else 'Actualizada') + f": {etapa.nombre} (orden={etapa.orden})")

    # Desactivar etapas que no están en la lista objetivo
    q = Etapa.objects.filter(modalidad=examen).exclude(nombre__in=nombres_objetivo)
    count_desact = q.update(activo=False)
    print(f'Etapas no objetivo desactivadas: {count_desact}')

    # Verificación final
    etapas_final = list(Etapa.objects.filter(modalidad=examen).order_by('orden').values_list('orden', 'nombre', 'activo'))
    print('\nEtapas actuales para EXAMEN DE GRADO (orden, nombre, activo):')
    for ord_, name, act in etapas_final:
        print(ord_, name, act)

    if len([x for x in etapas_final if x[1] in nombres_objetivo]) >= 7:
        print('\nOK: Existen las 7 etapas requeridas (incluyendo Registro).')
    else:
        print('\nERROR: No se encontraron las 7 etapas objetivo. Verifica los logs anteriores.')
