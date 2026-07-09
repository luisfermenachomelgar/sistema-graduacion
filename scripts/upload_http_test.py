#!/usr/bin/env python3
import subprocess, json, os, sys

def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

print('Login...')
rc,out,err = sh("curl -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"e2e_admin\",\"password\":\"e2e_pass\"}' http://127.0.0.1:8000/api/auth/login/")
if rc != 0:
    print('curl login error', err)
    sys.exit(1)
try:
    token = json.loads(out).get('access')
except Exception as e:
    print('login parse failed', e, out)
    sys.exit(1)
print('token:', bool(token))

rc,out,err = sh(f"curl -s -H \"Authorization: Bearer {token}\" http://127.0.0.1:8000/api/postulaciones/")
print('postulaciones raw:', out, err)
postulaciones_data = json.loads(out)
postulaciones = postulaciones_data.get('results', postulaciones_data)
rc,out,err = sh(f"curl -s -H \"Authorization: Bearer {token}\" http://127.0.0.1:8000/api/tipos-documento/")
print('tipos raw:', out, err)
tipos_data = json.loads(out)
tipos = tipos_data.get('results', tipos_data)
if not postulaciones or not tipos:
    print('No postulaciones or tipos found')
    print('postulaciones_data=', postulaciones_data)
    print('tipos_data=', tipos_data)
    sys.exit(1)
post_id = postulaciones[0]['id']
tipo_id = tipos[0]['id']
print('using post', post_id, 'tipo', tipo_id)

# ensure docx exists
if not os.path.exists('/tmp/e2e_base.docx'):
    print('creating /tmp/e2e_base.docx')
    open('/tmp/e2e_base.txt','w').write('E2E')
    sh('soffice --headless --convert-to docx --outdir /tmp /tmp/e2e_base.txt || true')

print('Uploading file...')
cmd = f"curl -s -X POST -H \"Authorization: Bearer {token}\" -F 'postulacion={post_id}' -F 'tipo_documento={tipo_id}' -F 'archivo=@/tmp/e2e_base.docx' http://127.0.0.1:8000/api/documentos/"
rc,out,err = sh(cmd)
print('upload rc', rc)
try:
    print('upload resp:', json.dumps(json.loads(out), indent=2))
except Exception:
    print('upload resp raw:', out)

# Verify preview URL and file exists via HTTP
print('\nVerifying preview URL...')
created = json.loads(out)
preview_url = created.get('preview_pdf_url')
if not preview_url:
    print('No preview_pdf_url returned')
    sys.exit(1)
full_preview_url = f'http://127.0.0.1:8000{preview_url}' if preview_url.startswith('/') else preview_url
print('preview_url:', full_preview_url)
rc2,out2,err2 = sh(f"curl -s -I -L -H \"Authorization: Bearer {token}\" {full_preview_url}")
print('preview HEAD response:', out2, err2)
if rc2 != 0:
    print('Failed to fetch preview URL')
    sys.exit(1)
