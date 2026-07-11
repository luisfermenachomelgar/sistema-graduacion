import React from 'react';
import {
  PieChart, Pie, Cell,
  Tooltip, ResponsiveContainer
} from 'recharts';

const mockPieChartData = [
  { name: 'Completado', value: 45, color: '#10b981' },
  { name: 'En Proceso', value: 30, color: '#f59e0b' },
  { name: 'Por Revisar', value: 15, color: '#3b82f6' },
  { name: 'Rechazado', value: 10, color: '#ef4444' },
];

const Charts = ({
  isDark = false,
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
    <div className="grid grid-cols-1 gap-6 mb-8">

      {/* Gráfico Circular */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-slate-700/50 hover:-translate-y-1 hover:shadow-xl transition-all transition-shadow duration-300 transition-opacity duration-500 opacity-0 animate-[fadeIn_.5s_ease-in-out_forwards]">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Postulaciones por Etapa Actual
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
    </div>
  );
};

export default Charts;
