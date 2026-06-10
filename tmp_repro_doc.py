import json, urllib.request, urllib.parse, sys, os
base='http://localhost:8000'
# Credentials
username='admin_test'
password='test123'
# Login
login_data = json.dumps({'username':username,'password':password}).encode('utf-8')
req = urllib.request.Request(base + '/api/auth/login/', data=login_data, headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    token = json.loads(body).get('access')
    print('LOGIN', resp.getcode())
except Exception as e:
    print('LOGIN_ERR', e)
    sys.exit(1)
# Get postulaciones
req = urllib.request.Request(base + '/api/postulaciones/', headers={'Authorization': f'Bearer {token}'})
try:
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    postul = json.loads(body)
    posts_list = postul if isinstance(postul, list) else postul.get('results', [])
    print('POSTS_COUNT', len(posts_list))
    if not posts_list:
        print('NO_POSTULACIONES_FOUND')
        sys.exit(2)
    post_id = posts_list[0]['id']
    print('USING_POSTULACION_ID', post_id)
except Exception as e:
    print('POSTS_ERR', e)
    sys.exit(1)
# Get tipos-documento to pick a tipo
req = urllib.request.Request(base + '/api/tipos-documento/', headers={'Authorization': f'Bearer {token}'})
try:
    resp = urllib.request.urlopen(req)
    tipos = json.loads(resp.read().decode())
    tipos_list = tipos if isinstance(tipos, list) else tipos.get('results', [])
    if not tipos_list:
        print('NO_TIPOS_FOUND')
        sys.exit(3)
    tipo_id = tipos_list[0]['id']
    print('USING_TIPO_ID', tipo_id)
except Exception as e:
    print('TIPOS_ERR', e)
    sys.exit(1)
# Prepare multipart body
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
crlf='\r\n'
lines=[]
for name,value in [('postulacion', str(post_id)), ('tipo_documento', str(tipo_id)), ('estado','pendiente')]:
    lines.append('--' + boundary)
    lines.append(f'Content-Disposition: form-data; name="{name}"')
    lines.append('')
    lines.append(value)
# File
file_path='/tmp/test_doc.pdf'
with open(file_path,'wb') as f:
    f.write(b'PDF DUMMY')
filename = os.path.basename(file_path)
lines.append('--' + boundary)
lines.append(f'Content-Disposition: form-data; name="archivo"; filename="{filename}"')
lines.append('Content-Type: application/pdf')
lines.append('')
body = '\r\n'.join(lines).encode('utf-8') + b'\r\n' + open(file_path,'rb').read() + b'\r\n' + ('--' + boundary + '--\r\n').encode('utf-8')
# Make request with WRONG Content-Type header (simulate axios bug)
url = base + '/api/documentos/'
req = urllib.request.Request(url, data=body)
req.add_header('Authorization', f'Bearer {token}')
req.add_header('Content-Type', 'application/json')
req.add_header('Content-Length', str(len(body)))
# Print request headers we set
print('REQUEST_HEADERS_SENT')
for k,v in req.header_items():
    print(f'{k}: {v}')
# Perform request
try:
    resp = urllib.request.urlopen(req)
    resp_body = resp.read().decode()
    print('POST_OK', resp.getcode())
    print(resp_body)
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print('POST_ERR_STATUS', e.code)
    print('RESPONSE_BODY')
    print(err_body)
    # print response headers
    print('RESPONSE_HEADERS')
    for k,v in e.headers.items():
        print(f'{k}: {v}')
    # Print final Content-Type observed (we set it; server will see this)
    print('FINAL_CONTENT_TYPE_SENT', req.get_header('Content-Type'))
    sys.exit(0)
except Exception as e:
    print('POST_EXCEPTION', e)
    sys.exit(1)
