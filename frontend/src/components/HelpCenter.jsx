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
    <div className="mb-6">
      <div className="flex items-center gap-3 mb-2">
        <div
          className="p-2 rounded-lg flex items-center justify-center"
          style={{ background: `linear-gradient(135deg, ${BRAND_MID}, ${BRAND_AZURE})` }}
        >
          <Icon className="w-5 h-5 text-white" />
        </div>
        <h3 style={{ color: TEXT_ON_DARK }} className="text-md font-semibold">{title}</h3>
      </div>
      <div style={{ color: MUTED }} className="text-sm leading-relaxed">
        {children}
      </div>
    </div>
  );

  return (
    <div style={{ background: BRAND_DEEP }} className="p-2 rounded-lg">
      <div className="px-2 py-1 mb-4">
        <h2 style={{ color: TEXT_ON_DARK }} className="text-lg font-bold">Centro de Ayuda</h2>
        <p style={{ color: MUTED }} className="text-sm mt-2">
          Este centro aporta guías rápidas y referencias para ayudarle a utilizar el sistema de gestión
          de graduación. Aquí encontrará instrucciones por temas, preguntas frecuentes e información
          técnica básica del sistema.
        </p>
      </div>

      <div className="mt-2">
        <Section Icon={BookOpen} title="Primeros pasos">
          Guía para comenzar: crear cuenta, navegar por el panel, y flujo básico de trabajo.
        </Section>

        <Section Icon={Users} title="Gestión de Usuarios">
          Cómo crear, editar y asignar roles a los usuarios. Políticas de permisos y buenas prácticas.
        </Section>

        <Section Icon={GraduationCap} title="Modalidades de Graduación">
          Explicación de las modalidades soportadas por el sistema y cómo gestionarlas desde la sección
          de Modalidades.
        </Section>

        <Section Icon={FileText} title="Documentos">
          Tipos de documentos, carga, validaciones y estado de revisión. Recomendaciones sobre formatos.
        </Section>

        <Section Icon={ClipboardList} title="Postulaciones">
          Flujo de postulaciones: crear, asignar etapa, revisar y cerrar postulaciones.
        </Section>

        <Section Icon={HelpCircle} title="Preguntas Frecuentes">
          Respuestas a las dudas comunes sobre uso, errores habituales y soluciones rápidas.
        </Section>

        <Section Icon={Info} title="Información del Sistema">
          Versión, datos de despliegue y enlaces de soporte técnico. Consulte con el equipo de TI para
          más detalles.
        </Section>
      </div>

      <div className="mt-4 pt-4 border-t" style={{ borderColor: '#6FD3FF14' }}>
        <p style={{ color: MUTED }} className="text-sm">Versión 1.0</p>
        <p style={{ color: MUTED }} className="text-sm">Carrera de Ingeniería de Sistemas</p>
        <p style={{ color: MUTED }} className="text-sm">Universidad Autónoma del Beni José Ballivián</p>
      </div>
    </div>
  );
};

export default HelpCenter;
