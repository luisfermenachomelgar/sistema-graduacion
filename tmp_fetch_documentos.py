import json
import urllib.request

base = 'http://127.0.0.1:80'

login_req = urllib.request.Request(
    base + '/api/auth/login/',
    data=json.dumps({'username': 'admin', 'password': 'password'}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(login_req, timeout=20) as r:
    login_body = json.loads(r.read().decode())
    token = login_body['access']

req = urllib.request.Request(base + '/api/documentos/', headers={'Authorization': 'Bearer ' + token})
with urllib.request.urlopen(req, timeout=20) as r:
    body = json.loads(r.read().decode())
    print('DOCS_STATUS', r.status)
    print(json.dumps(body, ensure_ascii=False)[:20000])
