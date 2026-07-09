import subprocess
import json

login_cmd = [
    'curl', '-s', '-X', 'POST',
    '-H', 'Content-Type: application/json',
    '-d', '{"username":"e2e_admin","password":"e2e_pass"}',
    'http://127.0.0.1:8000/api/auth/login/'
]
print('login_cmd', login_cmd)
proc = subprocess.run(login_cmd, capture_output=True, text=True)
print('login rc', proc.returncode)
print('login stdout', proc.stdout)
print('login stderr', proc.stderr)
if proc.returncode != 0:
    raise SystemExit('login curl failed')
access = json.loads(proc.stdout).get('access')
print('access', access)

for endpoint in ['http://127.0.0.1:8000/api/documentos/?debug_request=1', 'http://127.0.0.1:8000/api/documentos/']:
    print('\n=== DEBUG REQUEST to', endpoint)
    cmd = [
        'curl', '-v', '-X', 'POST',
        '-H', f'Authorization: Bearer {access}',
        '-F', 'postulacion=36',
        '-F', 'tipo_documento=9',
        '-F', 'archivo=@/tmp/e2e_base.docx',
        endpoint,
    ]
    proc2 = subprocess.run(cmd, capture_output=True, text=True)
    print('returncode', proc2.returncode)
    print('stdout:', proc2.stdout)
    print('stderr:', proc2.stderr)
