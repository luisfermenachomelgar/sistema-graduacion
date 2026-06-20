import requests, json

r = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'username':'admin','password':'password'})
print('STATUS', r.status_code)
print('BODY', r.text)
