import os
import sys
import subprocess
from pathlib import Path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from documentos.views import DocumentoPostulacionViewSet
from rest_framework import status

from modalidades.models import Modalidad, Etapa
from postulantes.models import Postulante, Postulacion
from documentos.models import TipoDocumento, DocumentoPostulacion


def ensure_admin():
    User = get_user_model()
    admin = User.objects.filter(username='e2e_admin').first()
    if not admin:
        admin = User.objects.create_superuser('e2e_admin', 'e2e_admin@example.com', 'e2e_pass')
    return admin


def ensure_entities():
    modalidad, _ = Modalidad.objects.get_or_create(nombre='E2E Modalidad')
    etapa, _ = Etapa.objects.get_or_create(modalidad=modalidad, orden=1, defaults={'nombre': 'Registro', 'activo': True})
    tipo, _ = TipoDocumento.objects.get_or_create(nombre='E2E Tipo Documento', etapa=etapa)
    postulante, _ = Postulante.objects.get_or_create(ci='E2E-CI-1', defaults={'nombre': 'E2E', 'apellido': 'User', 'telefono': '000', 'codigo_estudiante': 'E2E01'})
    postulacion, _ = Postulacion.objects.get_or_create(postulante=postulante, modalidad=modalidad, defaults={'titulo_trabajo': 'E2E test', 'gestion': 2026})
    return modalidad, etapa, tipo, postulante, postulacion


def make_text_file(path: Path, content: str = 'E2E Test'):
    path.write_text(content)
    return path


def convert_with_soffice(src: Path, target_ext: str) -> Path | None:
    outdir = src.parent
    cmd = ['soffice', '--headless', '--convert-to', target_ext, '--outdir', str(outdir), str(src)]
    try:
        env = os.environ.copy()
        env['HOME'] = '/tmp'
        subprocess.run(cmd, check=True, timeout=60, env=env)
        out = outdir / (src.stem + '.' + target_ext)
        if out.exists():
            return out
        # try common extension mapping
        candidates = list(outdir.glob(src.stem + '.*'))
        for c in candidates:
            if c.suffix.lower() == '.' + target_ext:
                return c
        return None
    except Exception as e:
        print('soffice conversion failed:', e)
        return None


def run_tests():
    admin = ensure_admin()
    modalidad, etapa, tipo, postulante, postulacion = ensure_entities()

    client = APIClient()
    client.force_authenticate(admin)
    factory = APIRequestFactory()

    tmp = Path('/tmp')
    tmp.mkdir(parents=True, exist_ok=True)

    base_txt = tmp / 'e2e_base.txt'
    make_text_file(base_txt, 'E2E conversion base file')

    tests = []

    # PDF (no conversion expected)
    pdf_path = tmp / 'e2e_test.pdf'
    make_text_file(pdf_path, '%PDF-1.4\n%EOF')
    tests.append(('pdf', pdf_path))

    # Create docx/xlsx/pptx using soffice from the text file
    docx = convert_with_soffice(base_txt, 'docx')
    xlsx = convert_with_soffice(base_txt, 'xlsx')
    pptx = convert_with_soffice(base_txt, 'pptx')

    if docx:
        tests.append(('docx', docx))
    else:
        print('DOCX not generated')
    if xlsx:
        tests.append(('xlsx', xlsx))
    else:
        print('XLSX not generated')
    if pptx:
        tests.append(('pptx', pptx))
    else:
        print('PPTX not generated')

    endpoint = '/api/documentos/'

    results = []
    for ext, path in tests:
        print('Uploading', path)
        with open(path, 'rb') as fh:
            # Build multipart request via RequestFactory and call view directly
            data = {'postulacion': str(postulacion.id), 'tipo_documento': str(tipo.id)}
            req = factory.post(endpoint, data, format='multipart', files={'archivo': fh})
            # attach authenticated user to request for DRF permission checks
            force_authenticate(req, user=admin)
            view = DocumentoPostulacionViewSet.as_view({'post': 'create'})
            resp = view(req)
            # If response is a DRF Response, access status_code and data
            if hasattr(resp, 'status_code'):
                status_code = resp.status_code
                resp_data = getattr(resp, 'data', None)
            else:
                status_code = None
                resp_data = None
        ok = status_code in (200, 201)
        print('Status', status_code)
        print('Response:', resp_data or getattr(resp, 'content', None))
        obj = None
        preview_url = None
        if ok:
            data = resp_data
            obj_id = data.get('id') if data else None
            if obj_id:
                obj = DocumentoPostulacion.objects.filter(id=obj_id).first()
                preview_url = data.get('preview_pdf_url') if data else None
        results.append({'ext': ext, 'path': str(path), 'status': resp.status_code, 'ok': ok, 'preview_url': preview_url, 'obj_exists': bool(obj)})

    print('\n=== E2E RESULTS ===')
    for r in results:
        print(r)


if __name__ == '__main__':
    run_tests()
