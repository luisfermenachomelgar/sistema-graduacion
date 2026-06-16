#!/usr/bin/env python
"""
Diagnosticar la respuesta real del endpoint /api/documentos/
"""
import requests
import json

access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNjAwNjA4LCJpYXQiOjE3ODE1OTcwMDgsImp0aSI6IjY1ZTIxMzRjYzE2YTRhZTk5MWJkMjU1Zjc1NTEzZWJmIiwidXNlcl9pZCI6IjUwIiwicm9sZSI6ImFkbWluIiwidXNlcm5hbWUiOiJhZG1pbiIsImVtYWlsIjoiYWRtaW5AZXhhbXBsZS5jb20iLCJmaXJzdF9uYW1lIjoiQWRtaW4iLCJsYXN0X25hbWUiOiJVc2VyIn0.4ciIMqPewYSSBlezgZcLvxSWbyHXvALqF3jx6Z1l8U0'

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

try:
    response = requests.get('http://localhost/api/documentos/?limit=3', headers=headers)
    print(f'Status: {response.status_code}\n')
    
    data = response.json()
    
    print('=== ESTRUCTURA DE RESPUESTA ===')
    if 'results' in data:
        print(f'Total: {data.get("count", "N/A")}')
        print(f'Registros en page: {len(data.get("results", []))}')
        print()
        
        if data['results']:
            record = data['results'][0]
            print('=== PRIMER REGISTRO COMPLETO ===\n')
            print(json.dumps(record, indent=2, ensure_ascii=False))
            
            print('\n\n=== CAMPOS SOLICITADOS ===')
            print(f'postulante_nombre: {record.get("postulante_nombre", "⚠️ CAMPO NO EXISTE")}')
            print(f'modalidad_nombre: {record.get("modalidad_nombre", "⚠️ CAMPO NO EXISTE")}')
            
            print('\n\n=== CAMPOS DISPONIBLES ===')
            print(f'Campos en el registro: {list(record.keys())}')
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
