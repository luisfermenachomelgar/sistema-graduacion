import React from 'react';
import { BookOpen, Users, GraduationCap, FileText, ClipboardList, HelpCircle, Info } from 'lucide-react';

const HelpCenter = () => {
  // Paleta corporativa (coincide exactamente con Header/Sidebar)
  const BRAND_DEEP = '#071740';
  const BRAND_MID = '#1E66B8';
  const BRAND_AZURE = '#6FD3FF';
  const TEXT_ON_DARK = '#EAF4FF';
  const MUTED = '#DCEBFF';

  const Section = ({ Icon, title, children }) => (
    <div className="mb-6 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        <div
          className="p-2 rounded-2xl flex items-center justify-center"
          style={{ background: `linear-gradient(135deg, ${BRAND_MID}, ${BRAND_AZURE})` }}
        >
          <Icon className="w-5 h-5 text-white" />
        </div>
        <h3 style={{ color: TEXT_ON_DARK }} className="text-md font-semibold">{title}</h3>
      </div>
      <div style={{ color: MUTED }} className="text-sm leading-6">
        {children}
      </div>
    </div>
  );

  return (
    <div style={{ background: BRAND_DEEP }} className="p-4 rounded-3xl text-white">
      <div className="px-2 py-1 mb-6">
        <h2 style={{ color: TEXT_ON_DARK }} className="text-xl font-bold">Centro de Ayuda</h2>
        <p style={{ color: MUTED }} className="text-sm mt-2 max-w-2xl">
          Guía rápida para usar el sistema paso a paso. Aquí encontrarás explicaciones claras de cada opción del menú lateral.
        </p>
      </div>

      <div className="grid gap-4">
        <Section Icon={BookOpen} title="Inicio">
          Muestra el resumen general del sistema, las estadísticas clave y accesos rápidos a las funciones principales.
        </Section>

        <Section Icon={Users} title="Postulantes">
          Aquí se registran, editan y consultan los estudiantes que iniciarán su proceso de graduación.
        </Section>

        <Section Icon={ClipboardList} title="Postulaciones">
          En esta sección se crea la postulación de un estudiante, eligiendo modalidad, tutor y período académico.
        </Section>

        <Section Icon={FileText} title="Documentos">
          <ul className="list-disc list-inside space-y-2">
            <li>Se administran los documentos requeridos por cada postulación.</li>
            <li>El estudiante puede subir sus archivos desde su postulación.</li>
            <li>Los administradores pueden aprobar o rechazar cada documento.</li>
            <li>Si un documento es rechazado, puede volver a enviar uno nuevo reemplazando el archivo.</li>
          </ul>
        </Section>

        <Section Icon={GraduationCap} title="Modalidades">
          <ul className="list-disc list-inside space-y-2">
            <li>Aquí se crean las modalidades de graduación disponibles.</li>
            <li>Dentro de cada modalidad se configuran etapas, requisitos y tipos de documento.</li>
          </ul>
        </Section>

        <Section Icon={Users} title="Usuarios">
          En esta área se administran las cuentas del sistema y los roles de cada usuario.
        </Section>

        <Section Icon={HelpCircle} title="Reportes">
          Aquí se generan estadísticas y reportes para conocer el avance del proceso y el estado de cada área.
        </Section>

        <Section Icon={Info} title="Flujo del Sistema">
          <ol className="list-decimal list-inside space-y-2">
            <li>Registrar postulante.</li>
            <li>Crear postulación.</li>
            <li>Subir documentos.</li>
            <li>Revisar documentos.</li>
            <li>Aprobar requisitos.</li>
            <li>Finalizar el proceso de graduación.</li>
          </ol>
        </Section>
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-md font-semibold text-white mb-3">🟢 Consejos rápidos</h3>
        <ul className="list-disc list-inside space-y-2 text-sm text-slate-200">
          <li>Complete primero el registro del postulante.</li>
          <li>Cree la postulación antes de subir documentos.</li>
          <li>Revise los documentos rechazados y vuelva a subirlos cuando sea necesario.</li>
          <li>Los documentos aprobados ya no pueden modificarse.</li>
          <li>Consulte los reportes para conocer el avance del proceso.</li>
        </ul>
      </div>
    </div>
  );
};

export default HelpCenter;
