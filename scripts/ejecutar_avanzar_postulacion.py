import os
import sys
import django
from pathlib import Path

# Asegurar que la raíz del proyecto esté en sys.path (cuando se ejecuta desde scripts/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from postulantes.models import Postulacion
from postulantes.services import required_documents_missing, avanzar_postulacion
from modalidades.models import Etapa

qs = Postulacion.objects.select_related('etapa_actual','modalidad').all()
selected=None
for p in qs:
    missing = required_documents_missing(p)
    missing_count = len(missing)
    can_advance = (missing_count == 0) and (p.etapa_actual is not None)
    if can_advance:
        selected = p
        break

if not selected:
    print('NO_POSTULACION_FOUND')
else:
    p = selected
    print('ID|', p.id)
    print('ETAPA_BEFORE|', getattr(p.etapa_actual, 'id', None), getattr(p.etapa_actual, 'nombre', None))
    print('ESTADO_GENERAL_BEFORE|', p.estado_general)

    p2 = avanzar_postulacion(p.id, actor=None)
    print('ETAPA_AFTER|', getattr(p2.etapa_actual, 'id', None), getattr(p2.etapa_actual, 'nombre', None))
    print('ESTADO_GENERAL_AFTER|', p2.estado_general)

    next_stage_after = None
    if p2.etapa_actual:
        next_stage_after = Etapa.objects.filter(modalidad_id=p2.modalidad_id, activo=True, orden__gt=p2.etapa_actual.orden).order_by('orden').first()
    if next_stage_after is None and p2.estado_general != 'TITULADO':
        p3 = avanzar_postulacion(p2.id, actor=None)
        print('SECOND_CALL_ETAPA|', getattr(p3.etapa_actual, 'id', None), getattr(p3.etapa_actual, 'nombre', None))
        print('SECOND_CALL_ESTADO_GENERAL|', p3.estado_general)
