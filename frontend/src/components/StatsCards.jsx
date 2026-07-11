import React from 'react';
import { TrendingUp, TrendingDown, Users, FileText, CheckCircle, Zap } from 'lucide-react';

const StatsCards = ({ stats = {}, cards = [], gridClass = 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8' }) => {
  const defaultStats = {
    totalPostulantes: { value: 0, change: 0, icon: Users, color: 'blue' },
    modalidadesFinalizadas: { value: 0, change: 0, icon: CheckCircle, color: 'green' },
  };

  const titles = {
    totalPostulantes: 'Total Postulantes',
    modalidadesFinalizadas: 'Modalidades Finalizadas',
  };

  const getColorClasses = (color) => {
    const colors = {
      blue: 'from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700',
      yellow: 'from-yellow-500 to-orange-600 dark:from-yellow-600 dark:to-orange-700',
      green: 'from-green-500 to-emerald-600 dark:from-green-600 dark:to-emerald-700',
      purple: 'from-purple-500 to-pink-600 dark:from-purple-600 dark:to-pink-700',
      cyan: 'from-cyan-500 to-cyan-600 dark:from-cyan-600 dark:to-cyan-700',
      orange: 'from-orange-500 to-orange-600 dark:from-orange-600 dark:to-orange-700',
      indigo: 'from-indigo-500 to-indigo-600 dark:from-indigo-600 dark:to-indigo-700',
    };
    return colors[color] || colors.blue;
  };

  const getIconBgColor = (color) => {
    const colors = {
      blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
      yellow: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400',
      green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
      purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
      cyan: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400',
      orange: 'bg-orange-100 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
      indigo: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400',
    };
    return colors[color] || colors.blue;
  };

  const buildCard = ({ title, value = 0, change = 0, Icon = Users, color = 'blue', suffix = '' }) => ({
    title,
    value,
    change,
    Icon,
    suffix,
    colorClass: getColorClasses(color),
    bgColorClass: getIconBgColor(color),
  });

  const cardItems = cards.length > 0
    ? cards.map(buildCard)
    : Object.keys(stats).length > 0
      ? Object.keys(stats).map((key) => buildCard({
          title: titles[key] || key,
          ...defaultStats[key],
          ...(stats[key] || {}),
        }))
      : Object.keys(defaultStats).map((key) => buildCard({
          title: titles[key],
          ...defaultStats[key],
        }));

  const StatCard = ({ title, value, change, Icon, colorClass, bgColorClass, suffix }) => {
    const isPositive = typeof change === 'number' && change >= 0;
    const isNumericValue = typeof value === 'number';

    return (
      <div className="group overflow-hidden rounded-2xl border border-gray-200/80 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg dark:border-gray-700 dark:bg-gray-800">
        <div className={`h-1 bg-gradient-to-r ${colorClass}`} />

        <div className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="mb-2 text-sm font-medium text-gray-600 dark:text-gray-400">
                {title}
              </p>
              <h3 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
                {isNumericValue ? value : String(value)}
                {suffix}
              </h3>

              {/* Cambio */}
              {typeof change === 'number' ? (
                <div className="flex items-center gap-2">
                  {isPositive ? (
                    <TrendingUp className="w-4 h-4 text-green-500" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-500" />
                  )}
                  <span className={`text-sm font-semibold ${
                    isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  }`}>
                    {isPositive ? '+' : ''}{change}%
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">vs mes anterior</span>
                </div>
              ) : null}
            </div>

            {/* Icono */}
            <div className={`${bgColorClass} rounded-xl p-3 transition-transform group-hover:scale-110`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={gridClass}>
      {cardItems.map((card, index) => (
        <StatCard
          key={`${card.title}-${index}`}
          title={card.title}
          value={card.value}
          change={card.change}
          Icon={card.Icon}
          suffix={card.suffix}
          colorClass={card.colorClass}
          bgColorClass={card.bgColorClass}
        />
      ))}
    </div>
  );
};

export default StatsCards;
