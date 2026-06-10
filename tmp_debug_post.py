import json, urllib.request, urllib.parse, sys, os
base='http://localhost:8000'
# login
login_data = json.dumps({'username':'estudiante_test','password':'test123'}).encode('utf-8')
req = urllib.request.Request(base + '/api/auth/login/', data=login_data, headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    print('LOGIN', resp.getcode(), body[:1000])
    token = json.loads(body).get('access')
except urllib.error.HTTPError as e:
    print('LOGIN_ERR', e.code, e.read().decode())
    sys.exit(0)
# get tipos
req = urllib.request.Request(base + '/api/tipos-documento/', headers={'Authorization': f'Bearer {token}'})
try:
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    print('TIPOS', resp.getcode(), body[:1000])
    tipos = json.loads(body)
    tipos_list = tipos if isinstance(tipos, list) else tipos.get('results', [])
except Exception as e:
    print('TIPOS_ERR', e)
    sys.exit(0)
# get postulaciones
req = urllib.request.Request(base + '/api/postulaciones/', headers={'Authorization': f'Bearer {token}'})
try:
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    print('POSTS', resp.getcode(), body[:1000])
    postul = json.loads(body)
    posts_list = postul if isinstance(postul, list) else postul.get('results', [])
except Exception as e:
    print('POSTS_ERR', e)
    sys.exit(0)
if not tipos_list or not posts_list:
    print('NO_TIPOS_OR_POSTS')
    sys.exit(0)
post_id = posts_list[0]['id']
tipo_id = tipos_list[1]['id'] if len(tipos_list)>1 else tipos_list[0]['id']
print('using', post_id, tipo_id)
# prepare multipart body
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
crlf='\r\n'
lines=[]
# fields
for name,value in [('postulacion', str(post_id)), ('tipo_documento', str(tipo_id)), ('estado','pendiente')]:
    lines.append('--' + boundary)
    lines.append(f'Content-Disposition: form-data; name="{name}"')
    lines.append('')
    lines.append(value)
# file
file_path='/tmp/test_doc.txt'
with open(file_path,'wb') as f:
    f.write(b'Hello world')
filename = os.path.basename(file_path)
lines.append('--' + boundary)
lines.append(f'Content-Disposition: form-data; name="archivo"; filename="{filename}"')
lines.append('Content-Type: application/octet-stream')
lines.append('')
body = '\r\n'.join(lines).encode('utf-8') + b'\r\n' + open(file_path,'rb').read() + b'\r\n' + ('--' + boundary + '--\r\n').encode('utf-8')
# send request WITH WRONG header Content-Type: application/json
req = urllib.request.Request(base + '/api/documentos/', data=body)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
req.add_header('Content-Length', str(len(body)))
try:
    resp = urllib.request.urlopen(req)
    resp_body = resp.read().decode()
    print('POST_OK', resp.getcode(), resp_body[:2000])
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print('POST_ERR', e.code, err_body[:2000])
