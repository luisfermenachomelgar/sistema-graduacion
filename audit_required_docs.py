import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from postulantes.models import Postulacion
from postulantes.services import required_documents_missing
from modalidades.models import Etapa
from django.db.models import Min

IDS = [1,2,3,4,5,6,7,9]

print('id\testado_general\tetapa_id\tetapa_nombre\tetapa_orden\tmissing_count\tmissing_names\tcan_advance\tnext_stage_id\tnext_stage_nombre\tnext_stage_orden')
for id_ in IDS:
    try:
        p = Postulacion.objects.select_related('modalidad','etapa_actual').get(pk=id_)
    except Postulacion.DoesNotExist:
        print(f"{id_}\tMISSING\t-\t-\t-\t-\t-\tFalse\t-\t-\t-")
        continue
    etapa = p.etapa_actual
    etapa_id = etapa.id if etapa else None
    etapa_nombre = etapa.nombre if etapa else None
    etapa_orden = etapa.orden if etapa else None

    missing = required_documents_missing(p)
    missing_names = [d['nombre'] for d in missing]
    missing_count = len(missing)

    # compute next_stage
    next_stage = None
    if etapa:
        next_stage = Etapa.objects.filter(modalidad_id=p.modalidad_id, activo=True, orden__gt=etapa.orden).order_by('orden').first()

    can_advance = False
    if etapa and next_stage and missing_count == 0:
        can_advance = True

    ns_id = next_stage.id if next_stage else None
    ns_nombre = next_stage.nombre if next_stage else None
    ns_orden = next_stage.orden if next_stage else None

    print(f"{p.id}\t{p.estado_general}\t{etapa_id}\t{etapa_nombre}\t{etapa_orden}\t{missing_count}\t{missing_names}\t{can_advance}\t{ns_id}\t{ns_nombre}\t{ns_orden}")
