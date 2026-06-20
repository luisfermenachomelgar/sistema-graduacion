from postulantes.serializers import PostulacionDetailSerializer
from postulantes.models import Postulacion, Postulante
from modalidades.models import Modalidad
from django.contrib.auth import get_user_model

User = get_user_model()

# Crear o recuperar objetos de prueba
postulante, _ = Postulante.objects.get_or_create(ci='TESTCI123', defaults={'nombre':'Test','apellido':'User','codigo_estudiante':'CODE123','telefono':'000'})
modalidad, _ = Modalidad.objects.get_or_create(nombre='MOD_TEST', defaults={'activa': True})

# Limpiar postulaciones de prueba previas que interfieran
Postulacion.objects.filter(postulante=postulante, modalidad=modalidad, titulo_trabajo__startswith='TEST_SERIAL').delete()

# Crear una postulación previa con estado_general RECHAZADO para 2026/1
prev = Postulacion.objects.create(
    postulante=postulante,
    modalidad=modalidad,
    titulo_trabajo='TEST_SERIAL_PREV',
    anio_academico=2026,
    semestre_academico=1,
    gestion=2026,
    estado='rechazada',
    estado_general='RECHAZADO'
)
print('Prev created id=', prev.id, 'estado_general=', prev.estado_general)

# Intentar crear nueva postulación misma modalidad y mismo periodo - debe fallar
data_fail = {
    'postulante_id': postulante.id,
    'modalidad': modalidad.id,
    'titulo_trabajo': 'TEST_SERIAL_NEW_FAIL',
    'anio_academico': 2026,
    'semestre_academico': 1,
    'estado': 'borrador',
}
serializer_fail = PostulacionDetailSerializer(data=data_fail)
valid = serializer_fail.is_valid()
print('Is valid (should be False):', valid)
print('Errors:', serializer_fail.errors)

# Intentar crear nueva postulación misma modalidad pero distinto periodo - debe pasar
data_ok = data_fail.copy()
data_ok['titulo_trabajo'] = 'TEST_SERIAL_NEW_OK'
data_ok['anio_academico'] = 2027
serializer_ok = PostulacionDetailSerializer(data=data_ok)
valid_ok = serializer_ok.is_valid()
print('Is valid for different year (should be True):', valid_ok)
print('Errors:', serializer_ok.errors)

# Limpieza opcional
#Postulacion.objects.filter(titulo_trabajo__startswith='TEST_SERIAL').delete()
print('Test completed')
