/**
 * PageHeader Component
 * Shared page header for consistent titles, descriptions, and primary actions
 */

import React from 'react';

const PageHeader = ({ title, description, action, className = '' }) => {
  return (
    <div className={`mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 ${className}`}>
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{title}</h1>
        {description && <p className="text-gray-600 dark:text-gray-400">{description}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};

export default PageHeader;
