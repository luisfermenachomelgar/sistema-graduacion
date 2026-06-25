import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db.models import Max
from postulantes.models import Postulacion
from postulantes.services import required_documents_missing
from modalidades.models import Etapa

print('POSTULACIONES_ACTUALES:')
for p in Postulacion.objects.select_related('modalidad', 'etapa_actual').order_by('id'):
    etapa = p.etapa_actual
    if etapa:
        etapa_info = f'id={etapa.id} nombre={etapa.nombre} orden={etapa.orden}'
    else:
        etapa_info = 'None'
    print(
        f'id={p.id} estado_general={p.estado_general} '
        f'modalidad={p.modalidad.nombre if p.modalidad else None} etapa_actual={etapa_info}'
    )

print('\nULTIMA_ETAPA_POR_MODALIDAD:')
modalidad_max = {}
for row in Etapa.objects.filter(activo=True).values('modalidad_id').annotate(max_orden=Max('orden')):
    modalidad_max[row['modalidad_id']] = row['max_orden']
    print(f"modalidad_id={row['modalidad_id']} max_orden={row['max_orden']}")

print('\nPOSTULACIONES_EN_ULTIMA_ETAPA:')
last_ids = []
for p in Postulacion.objects.select_related('modalidad', 'etapa_actual').order_by('id'):
    if p.etapa_actual and modalidad_max.get(p.modalidad_id) == p.etapa_actual.orden:
        print(
            f'id={p.id} estado_general={p.estado_general} modalidad={p.modalidad.nombre if p.modalidad else None} '
            f'etapa_actual={p.etapa_actual.nombre} orden={p.etapa_actual.orden}'
        )
        last_ids.append(p.id)
print(f'count_last={len(last_ids)}')

print('\nEVALUAR_POSIBLES_TITULADOS:')
for p in Postulacion.objects.select_related('modalidad', 'etapa_actual').order_by('id'):
    can_be_titulado = False
    missing = []
    if p.etapa_actual:
        max_orden = modalidad_max.get(p.modalidad_id)
        if max_orden is not None and p.etapa_actual.orden == max_orden:
            missing = required_documents_missing(p)
            if not missing:
                can_be_titulado = True
    print(
        f'id={p.id} estado_general={p.estado_general} etapa_orden={p.etapa_actual.orden if p.etapa_actual else None} '
        f'last={p.etapa_actual.orden == modalidad_max.get(p.modalidad_id) if p.etapa_actual else False} '
        f'missing_docs={len(missing)} can_be_titulado={can_be_titulado}'
    )
