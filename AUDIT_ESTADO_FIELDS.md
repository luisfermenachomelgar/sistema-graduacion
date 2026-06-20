# Auditoría: Inconsistencia entre `estado` y `estado_general`

## Objetivo
Confirmar dónde se guardan realmente los estados RECHAZADO/APLAZADO en el modelo actual y unificar criterio antes de avanzar con validaciones.

## Preguntas de diagnóstico a responder en tu entorno local

### 1. Estructura actual del modelo
Ejecuta en Django shell:
```python
from postulantes.models import Postulacion

# Ver las opciones de choices actuales
print("ESTADO_CHOICES:")
for choice in Postulacion.ESTADO_CHOICES:
    print(f"  {choice}")

print("\nESTADO_GENERAL_CHOICES:")
for choice in Postulacion.ESTADO_GENERAL_CHOICES:
    print(f"  {choice}")
```

**Responder:**
- ¿Qué valores exactos están en cada uno?
- ¿Hay 'RECHAZADO' o 'APLAZADO' en `ESTADO_CHOICES`?
- ¿Hay 'RECHAZADO' o 'APLAZADO' en `ESTADO_GENERAL_CHOICES`?

### 2. Datos existentes en la base de datos
Ejecuta en Django shell:
```python
from postulantes.models import Postulacion
from django.db.models import Q

# Buscar postulaciones con "RECHAZADO" en algún campo
rechazadas_general = Postulacion.objects.filter(estado_general='RECHAZADO').count()
rechazadas_estado = Postulacion.objects.filter(estado='RECHAZADO').count()
rechazadas_estado_rechazada = Postulacion.objects.filter(estado='rechazada').count()

print(f"Postulaciones con estado_general='RECHAZADO': {rechazadas_general}")
print(f"Postulaciones con estado='RECHAZADO': {rechazadas_estado}")
print(f"Postulaciones con estado='rechazada': {rechazadas_estado_rechazada}")

# Buscar "APLAZADO"
aplazadas_general = Postulacion.objects.filter(estado_general='APLAZADO').count()
aplazadas_estado = Postulacion.objects.filter(estado='APLAZADO').count()
aplazadas_estado_aplazada = Postulacion.objects.filter(estado='aplazada').count()

print(f"\nPostulaciones con estado_general='APLAZADO': {aplazadas_general}")
print(f"Postulaciones con estado='APLAZADO': {aplazadas_estado}")
print(f"Postulaciones con estado='aplazada': {aplazadas_estado_aplazada}")

# Ver todos los valores únicos de estado_general
todos_general = Postulacion.objects.values('estado_general').distinct()
print(f"\nValores únicos en estado_general: {list(todos_general)}")

# Ver todos los valores únicos de estado
todos_estado = Postulacion.objects.values('estado').distinct()
print(f"Valores únicos en estado: {list(todos_estado)}")
```

**Responder:**
- ¿Cuántas postulaciones tienen estado_general='RECHAZADO'?
- ¿Cuántas postulaciones tienen estado='RECHAZADO' o estado='rechazada'?
- ¿Qué valores únicos hay realmente en la BD para cada campo?

### 3. Relación entre campos
Ejecuta en Django shell:
```python
from postulantes.models import Postulacion

# Ver ejemplos concretos
print("Primeras 10 postulaciones:")
for post in Postulacion.objects.all()[:10]:
    print(f"  ID {post.id}: estado='{post.estado}', estado_general='{post.estado_general}'")

# Buscar casos donde estado y estado_general tengan relación clara
print("\nPostulaciones con estado='rechazada':")
for post in Postulacion.objects.filter(estado='rechazada')[:5]:
    print(f"  ID {post.id}: estado='{post.estado}', estado_general='{post.estado_general}'")
```

**Responder:**
- Cuando `estado='rechazada'`, ¿qué valor tiene típicamente `estado_general`?
- ¿Existe una correspondencia clara entre `estado` y `estado_general`?

## Resumen esperado

Después de ejecutar lo anterior, proporciona un resumen:

```
ESTRUCTURA DEL MODELO:
- ESTADO_CHOICES tiene: [lista los valores]
- ESTADO_GENERAL_CHOICES tiene: [lista los valores]
- ¿Hay overlap o duplicación? Sí/No

DATOS EN BD:
- Postulaciones con estado_general='RECHAZADO': [número]
- Postulaciones con estado='RECHAZADO' o 'rechazada': [número]
- Postulaciones con estado_general='APLAZADO': [número]
- Postulaciones con estado='APLAZADO' o 'aplazada': [número]
- Valores únicos en estado_general: [lista]
- Valores únicos en estado: [lista]

RELACIÓN:
- ¿estado='rechazada' corresponde a estado_general='RECHAZADO'? Sí/No
- ¿Hay un mapeo claro? Describirlo

CONCLUSIÓN:
- ¿Cuál campo contiene realmente RECHAZADO/APLAZADO? estado / estado_general / ambos
- ¿Cuál debería usarse en las validaciones?
```

## Cambios pendientes

**PAUSADOS HASTA COMPLETAR AUDITORÍA:**
- Ajuste de la regla 2 del serializer
- Pruebas de API
- Ajustes a la lógica de validación

Una vez que confirmes la estructura real, procederemos con las correcciones.
