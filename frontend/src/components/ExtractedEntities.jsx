import React from 'react';

export default function ExtractedEntities({ entities }) {
  if (!entities) return null;

  const entityColors = {
    ORG: 'bg-blue-100 text-blue-800 border-blue-200',
    LOC: 'bg-green-100 text-green-800 border-green-200',
    PAYMENT_ID: 'bg-purple-100 text-purple-800 border-purple-200',
    DOMAIN: 'bg-orange-100 text-orange-800 border-orange-200',
    CLAIM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    PHONE: 'bg-teal-100 text-teal-800 border-teal-200',
    BANK_INFO: 'bg-indigo-100 text-indigo-800 border-indigo-200'
  };

  const hasEntities = Object.values(entities).some(arr => arr.length > 0);

  return (
    <section className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Extracted Entities</h3>
      
      {!hasEntities ? (
        <p className="text-slate-500 italic text-sm">No entities extracted.</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {Object.entries(entities).map(([type, items]) => (
            items.map((item, idx) => (
              <span 
                key={`${type}-${idx}`} 
                className={`text-xs font-medium px-2.5 py-1 rounded-md border ${entityColors[type] || 'bg-slate-100 text-slate-800 border-slate-200'}`}
              >
                <span className="opacity-50 mr-1">{type}</span>
                {item}
              </span>
            ))
          ))}
        </div>
      )}
    </section>
  );
}
