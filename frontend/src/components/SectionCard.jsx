/**
 * SectionCard Component
 * Shared surface for form sections and dashboard blocks
 */

import React from 'react';

const SectionCard = ({ title, description, children, className = '' }) => {
  return (
    <section className={`rounded-2xl border border-gray-200/80 bg-gray-50/60 p-5 sm:p-6 dark:border-gray-700 dark:bg-gray-800/60 shadow-sm ${className}`}>
      {(title || description) && (
        <div className="mb-3">
          {title && <h3 className="text-sm font-semibold tracking-wide text-gray-900 dark:text-gray-100">{title}</h3>}
          {description && <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">{description}</p>}
        </div>
      )}
      {children}
    </section>
  );
};

export default SectionCard;
