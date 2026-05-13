import React from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const mockBarChartData = [
  { semana: 'Sem 1', postulantes: 45, documentos: 38 },
  { semana: 'Sem 2', postulantes: 52, documentos: 48 },
  { semana: 'Sem 3', postulantes: 38, documentos: 35 },
  { semana: 'Sem 4', postulantes: 61, documentos: 55 },
  { semana: 'Sem 5', postulantes: 58, documentos: 52 },
  { semana: 'Sem 6', postulantes: 72, documentos: 68 },
];

const mockLineChartData = [
  { mes: 'Ene', graduados: 45, pendientes: 120, aprobados: 95 },
  { mes: 'Feb', graduados: 72, pendientes: 98, aprobados: 142 },
  { mes: 'Mar', graduados: 98, pendientes: 76, aprobados: 165 },
  { mes: 'Abr', graduados: 125, pendientes: 62, aprobados: 189 },
  { mes: 'May', graduados: 145, pendientes: 48, aprobados: 210 },
  { mes: 'Jun', graduados: 156, pendientes: 42, aprobados: 248 },
];

const mockPieChartData = [
  { name: 'Completado', value: 45, color: '#10b981' },
  { name: 'En Proceso', value: 30, color: '#f59e0b' },
  { name: 'Por Revisar', value: 15, color: '#3b82f6' },
  { name: 'Rechazado', value: 10, color: '#ef4444' },
];

const Charts = ({
  isDark = false,
  barChartData = mockBarChartData,
  lineChartData = mockLineChartData,
  pieChartData = mockPieChartData,
  metrics = {
    tasaAprobacion: 0,
    promedioProcesamiento: 0,
    satisfaccion: 'N/A',
    proyeccionMes: 0,
  },
}) => {
  // === ESTILO (sin cambios) ===
  const chartColors = {
    textColor: isDark ? '#e5e7eb' : '#374151',
    gridColor: isDark ? '#374151' : '#e5e7eb',
    barColor1: '#3b82f6',
    barColor2: '#8b5cf6',
    lineColor1: '#10b981',
    lineColor2: '#f59e0b',
    lineColor3: '#ef4444',
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-8">
      {/* Gráfico de Barras */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-slate-700/50 h-[320px] hover:-translate-y-1 hover:shadow-xl transition-all transition-shadow duration-300 transition-opacity duration-500 opacity-0 animate-[fadeIn_.5s_ease-in-out_forwards]">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Postulantes & Documentos por Semana
        </h3>
        {barChartData && barChartData.length > 0 && barChartData.some(d => d.postulantes > 0 || d.documentos > 0) ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.gridColor} />
            <XAxis dataKey="semana" stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <YAxis stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
              cursor={{ fill: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(59, 130, 246, 0.1)' }}
            />
            <Legend 
              wrapperStyle={{ 
                paddingTop: '16px',
                color: chartColors.textColor,
                fontSize: '14px',
                display: 'flex',
                gap: '16px',
                justifyContent: 'center',
              }}
              textColor={chartColors.textColor}
            />
            <Bar dataKey="postulantes" fill={chartColors.barColor1} radius={[8, 8, 0, 0]} name="Postulantes" />
            <Bar dataKey="documentos" fill={chartColors.barColor2} radius={[8, 8, 0, 0]} name="Documentos" />
          </BarChart>
        </ResponsiveContainer>
        ) : (
          <div className="flex flex-col items-center justify-center h-[300px] bg-gray-50 dark:bg-gray-700 rounded-lg">
            <svg className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Sin datos disponibles</p>
          </div>
        )}
      </div>

      {/* Gráfico de Línea */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-slate-700/50 h-[320px] hover:-translate-y-1 hover:shadow-xl transition-all transition-shadow duration-300 transition-opacity duration-500 opacity-0 animate-[fadeIn_.5s_ease-in-out_forwards]">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Progreso General (6 Meses)
        </h3>
        {lineChartData && lineChartData.length > 0 && lineChartData.some(d => d.graduados > 0 || d.pendientes > 0 || d.aprobados > 0) ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={lineChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={chartColors.gridColor} />
            <XAxis dataKey="mes" stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <YAxis stroke={chartColors.textColor} style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
              cursor={{ stroke: isDark ? 'rgba(59, 130, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)' }}
            />
            <Legend 
              wrapperStyle={{ 
                paddingTop: '16px',
                color: chartColors.textColor,
                fontSize: '14px',
                display: 'flex',
                gap: '16px',
                justifyContent: 'center',
              }}
              textColor={chartColors.textColor}
            />
            <Line
              type="monotone"
              dataKey="graduados"
              stroke={chartColors.lineColor1}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor1, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
              name="Graduados"
            />
            <Line
              type="monotone"
              dataKey="aprobados"
              stroke={chartColors.lineColor2}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor2, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
              name="Aprobados"
            />
            <Line
              type="monotone"
              dataKey="pendientes"
              stroke={chartColors.lineColor3}
              strokeWidth={3}
              dot={{ fill: chartColors.lineColor3, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
              name="Pendientes"
            />
          </LineChart>
        </ResponsiveContainer>
        ) : (
          <div className="flex flex-col items-center justify-center h-[300px] bg-gray-50 dark:bg-gray-700 rounded-lg">
            <svg className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Sin datos disponibles</p>
          </div>
        )}
      </div>

      {/* Gráfico Circular - Primera mitad (ancho completo en móvil, mitad en desktop) */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-slate-700/50 lg:col-span-1 hover:-translate-y-1 hover:shadow-xl transition-all transition-shadow duration-300 transition-opacity duration-500 opacity-0 animate-[fadeIn_.5s_ease-in-out_forwards]">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Distribución por Estado
        </h3>
        {pieChartData && pieChartData.length > 0 && pieChartData.some(d => d.name !== 'Sin datos') ? (
        <>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieChartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {pieChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1f2937' : '#ffffff',
                border: `1px solid ${isDark ? '#374151' : '#e5e7eb'}`,
                borderRadius: '8px',
                color: chartColors.textColor,
              }}
            />
          </PieChart>
        </ResponsiveContainer>

        {/* Leyenda personalizada */}
        <div className="mt-0 grid grid-cols-2 gap-0.5 text-xs">
          {pieChartData.map((item, idx) => (
            <div key={idx} className="flex items-center gap-1 px-0.5 py-0">
              <div
                className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: item.color }}
              ></div>
              <span className="text-gray-600 dark:text-gray-400">
                {item.name}: {item.value}%
              </span>
            </div>
          ))}
        </div>
        </>
        ) : (
          <div className="flex flex-col items-center justify-center h-[220px] bg-gray-50 dark:bg-gray-700 rounded-lg">
            <svg className="w-16 h-16 text-gray-300 dark:text-gray-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p className="text-gray-500 dark:text-gray-400 text-sm">Sin registros</p>
          </div>
        )}
      </div>

      {/* Resumen de Métricas Clave */}
      <div className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-900 p-6 rounded-xl shadow-lg border border-slate-700/50 h-[320px] hover:-translate-y-1 hover:shadow-xl transition-all transition-shadow duration-300 transition-opacity duration-500 opacity-0 animate-[fadeIn_.5s_ease-in-out_forwards]">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Resumen de Métricas
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Promedio Procesamiento</span>
            <span className="text-lg font-semibold text-blue-600 dark:text-blue-400">
              {metrics.promedioProcesamiento || 0} días
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Satisfacción</span>
            <span className="text-lg font-semibold text-purple-600 dark:text-purple-400">
              {metrics.satisfaccion === "N/A" ? "N/A" : `${metrics.satisfaccion || 0}/10`}
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">Proyección Mes</span>
            <span className={`text-lg font-semibold ${
              (metrics.proyeccionMes || 0) >= 0 
                ? 'text-orange-600 dark:text-orange-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              {(metrics.proyeccionMes || 0) > 0 ? '+' : ''}{metrics.proyeccionMes || 0}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Charts;
