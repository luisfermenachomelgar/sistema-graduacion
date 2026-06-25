"""Bootstrap inicial para poblar ModalidadTipoDocumento.

Este script crea las asociaciones entre modalidad, tipo de documento y etapa.
"""

from documentos.models import ModalidadTipoDocumento, TipoDocumento
from modalidades.models import Modalidad, Etapa

OLD_ACTA_DEFENSA_NAME = 'Comprobante de Defensa'
ACTA_DEFENSA_NAME = 'Acta de Defensa de Tesis o de Modalidad de Graduación'

def get_modalidad(nombre):
    return Modalidad.objects.get(nombre=nombre)


def get_etapa(modalidad, nombre):
    return Etapa.objects.get(modalidad=modalidad, nombre=nombre)


def get_tipo_documento(nombre):
    try:
        return TipoDocumento.objects.get(nombre=nombre)
    except TipoDocumento.DoesNotExist:
        if nombre == ACTA_DEFENSA_NAME:
            return TipoDocumento.objects.get(nombre=OLD_ACTA_DEFENSA_NAME)
        raise


def main():
    mappings = [
        # Proyecto de Grado
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Propuesta/Perfil', 'tipo_documento': 'CV del Estudiante', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Propuesta/Perfil', 'tipo_documento': 'Certificado Académico', 'obligatorio': True, 'orden': 2},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Propuesta/Perfil', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': True, 'orden': 3},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Propuesta/Perfil', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': True, 'orden': 4},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Propuesta/Perfil', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': False, 'orden': 5},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 1},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': False, 'orden': 3},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': False, 'orden': 4},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': True, 'orden': 5},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Desarrollo del Proyecto', 'tipo_documento': 'Documento de Avance', 'obligatorio': True, 'orden': 6},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 1},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': False, 'orden': 3},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': False, 'orden': 4},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': False, 'orden': 5},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Documento de Avance', 'obligatorio': False, 'orden': 6},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': 'Documento Final', 'obligatorio': True, 'orden': 7},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Defensa de Proyecto', 'tipo_documento': ACTA_DEFENSA_NAME, 'obligatorio': True, 'orden': 8},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 1},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': False, 'orden': 3},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': False, 'orden': 4},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': False, 'orden': 5},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Documento de Avance', 'obligatorio': False, 'orden': 6},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': 'Documento Final', 'obligatorio': True, 'orden': 7},
        {'modalidad': 'Proyecto de Grado', 'etapa': 'Correcciones', 'tipo_documento': ACTA_DEFENSA_NAME, 'obligatorio': False, 'orden': 8},
        # Examen de Grado
        {'modalidad': 'Examen de Grado', 'etapa': 'Inscripción', 'tipo_documento': 'CV del Estudiante', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Examen de Grado', 'etapa': 'Inscripción', 'tipo_documento': 'Certificado Académico', 'obligatorio': True, 'orden': 2},
        {'modalidad': 'Examen de Grado', 'etapa': 'Evaluación', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 1},
        {'modalidad': 'Examen de Grado', 'etapa': 'Evaluación', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Examen de Grado', 'etapa': 'Evaluación', 'tipo_documento': ACTA_DEFENSA_NAME, 'obligatorio': True, 'orden': 3},
        {'modalidad': 'Examen de Grado', 'etapa': 'Resultado Final', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 1},
        {'modalidad': 'Examen de Grado', 'etapa': 'Resultado Final', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Examen de Grado', 'etapa': 'Resultado Final', 'tipo_documento': ACTA_DEFENSA_NAME, 'obligatorio': False, 'orden': 3},
        # Vía Diplomado
        {'modalidad': 'Vía Diplomado', 'etapa': 'Inscripción Diplomado', 'tipo_documento': 'CV del Estudiante', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Inscripción Diplomado', 'tipo_documento': 'Certificado Académico', 'obligatorio': True, 'orden': 2},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Inscripción Diplomado', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': True, 'orden': 3},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Desarrollo Diplomado', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Desarrollo Diplomado', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': True, 'orden': 2},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Desarrollo Diplomado', 'tipo_documento': 'Documento de Avance', 'obligatorio': True, 'orden': 3},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Defensa Monografía', 'tipo_documento': 'Documento Final', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Defensa Monografía', 'tipo_documento': ACTA_DEFENSA_NAME, 'obligatorio': True, 'orden': 2},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'Documento Final', 'obligatorio': True, 'orden': 1},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'CV del Estudiante', 'obligatorio': False, 'orden': 2},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'Certificado Académico', 'obligatorio': False, 'orden': 3},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'Carta de Aceptación', 'obligatorio': False, 'orden': 4},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'Propuesta de Tesis', 'obligatorio': False, 'orden': 5},
        {'modalidad': 'Vía Diplomado', 'etapa': 'Correcciones', 'tipo_documento': 'Perfil de Tesis', 'obligatorio': False, 'orden': 6},
      ]

    created = 0
    updated = 0

    for mapping in mappings:
        modalidad = get_modalidad(mapping['modalidad'])
        etapa = get_etapa(modalidad, mapping['etapa'])
        tipo_documento = get_tipo_documento(mapping['tipo_documento'])

        obj, created_flag = ModalidadTipoDocumento.objects.get_or_create(
            modalidad=modalidad,
            tipo_documento=tipo_documento,
            etapa=etapa,
            defaults={
                'obligatorio': mapping['obligatorio'],
                'orden': mapping['orden'],
                'activo': True,
                'descripcion_requerimiento': '',
            }
        )

        if created_flag:
            created += 1
        else:
            updated += 1
            obj.obligatorio = mapping['obligatorio']
            obj.orden = mapping['orden']
            obj.activo = True
            obj.descripcion_requerimiento = ''
            obj.save()

    print(f'Bootstrap ModalidadTipoDocumento finalizado: {created} creados, {updated} actualizados.')


if __name__ == '__main__':
    main()
