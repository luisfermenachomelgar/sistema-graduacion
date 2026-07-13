const PROTECTED_MODALIDAD_NAMES = new Set([
  'PROYECTO DE GRADO',
  'EXAMEN DE GRADO',
  'EXCELENCIA ACADÉMICA',
]);

export function normalizeNombre(nombre) {
  if (!nombre) return '';
  return String(nombre).split(/\s+/).filter(Boolean).join(' ').toUpperCase();
}

export function isProtectedModalidadName(nombre) {
  return PROTECTED_MODALIDAD_NAMES.has(normalizeNombre(nombre));
}

export default isProtectedModalidadName;
