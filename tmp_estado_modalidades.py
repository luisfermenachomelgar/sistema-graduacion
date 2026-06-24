from django.db.models import Count
from modalidades.models import Modalidad
from postulantes.models import Postulacion

print('--- Modalidades y conteo de etapas ---')
for mod in Modalidad.objects.order_by('nombre'):
    etapas = list(mod.etapas.order_by('orden').values_list('orden', 'nombre'))
    print(f'Modalidad: {mod.id} - {mod.nombre} - etapas={len(etapas)}')
    for orden, nombre in etapas:
        print(f'  orden={orden} nombre={nombre}')

print('\n--- Estado general por modalidad ---')
for mod in Modalidad.objects.order_by('nombre'):
    counts = Postulacion.objects.filter(modalidad=mod).values('estado_general').order_by('estado_general').annotate(c=Count('id'))
    print(f'Modalidad: {mod.id} - {mod.nombre}')
    if counts:
        for item in counts:
            print(f"  {item['estado_general']}: {item['c']}")
    else:
        print('  (sin postulaciones)')

print('\n--- Postulaciones con estados específicos ---')
for state in ['PERFIL_APROBADO', 'PRIVADA_APROBADA', 'PUBLICA_APROBADA']:
    total = Postulacion.objects.filter(estado_general=state).count()
    print(f'{state}: {total}')

print('\n--- Modalidades con postulaciones en cada estado específico ---')
for state in ['PERFIL_APROBADO', 'PRIVADA_APROBADA', 'PUBLICA_APROBADA']:
    rows = Postulacion.objects.filter(estado_general=state).values('modalidad__nombre').annotate(c=Count('id')).order_by('modalidad__nombre')
    print(f'\n{state}:')
    if rows:
        for r in rows:
            print(f"  {r['modalidad__nombre']}: {r['c']}")
    else:
        print('  (ninguna)')
