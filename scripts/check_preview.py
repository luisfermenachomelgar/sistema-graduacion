import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from documentos.models import DocumentoPostulacion
from django.conf import settings

d = DocumentoPostulacion.objects.order_by('-id').first()
if not d:
    print('No DocumentoPostulacion found')
else:
    print('id', d.id)
    print('archivo_name', d.archivo.name if d.archivo else None)
    print('preview_name', d.preview_pdf.name if getattr(d, 'preview_pdf', None) else None)
    if getattr(d, 'preview_pdf', None):
        print('preview_path', d.preview_pdf.path)
        print('preview_exists', os.path.exists(d.preview_pdf.path))
    else:
        print('no preview file')
