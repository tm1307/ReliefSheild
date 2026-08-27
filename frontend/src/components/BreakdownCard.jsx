import React from 'react';
import { Shield, CreditCard, Copy, FileCheck, Info } from 'lucide-react';

export default function BreakdownCard({ check, status, details, points_deducted }) {
  const getIcon = () => {
    switch (check) {
      case 'Identity': return <Shield size={20} />;
      case 'Payment': return <CreditCard size={20} />;
      case 'Similarity': return <Copy size={20} />;
      case 'Claim': return <FileCheck size={20} />;
      default: return <Info size={20} />;
    }
  };

  const statusStyles = {
    Verified: 'border-l-green-500 bg-green-50 text-green-700',
    Flagged: 'border-l-red-500 bg-red-50 text-red-700',
    Unverifiable: 'border-l-gray-400 bg-gray-50 text-gray-700'
  };

  const badgeStyles = {
    Verified: 'bg-green-100 text-green-700',
    Flagged: 'bg-red-100 text-red-700',
    Unverifiable: 'bg-gray-200 text-gray-700'
  };

  return (
    <div className={`border border-slate-200 border-l-4 rounded-xl p-4 sm:p-5 bg-white flex flex-col sm:flex-row gap-4 sm:items-center justify-between ${statusStyles[status] || 'border-l-slate-200'}`}>
      <div className="flex items-start gap-3">
        <div className={`mt-0.5 ${statusStyles[status] ? statusStyles[status].split(' ')[2] : 'text-slate-500'}`}>
          {getIcon()}
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-slate-800">{check}</h4>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeStyles[status] || 'bg-slate-100 text-slate-600'}`}>
              {status}
            </span>
          </div>
          <p className="text-sm text-slate-600">{details}</p>
        </div>
      </div>
      {points_deducted > 0 && (
        <div className="text-sm font-semibold text-red-600 bg-red-50 px-3 py-1 rounded-lg shrink-0 self-start sm:self-center">
          -{points_deducted} pts
        </div>
      )}
    </div>
  );
}
