import React, { useState } from 'react';
import { Clock, ChevronDown, ChevronUp } from 'lucide-react';
import BreakdownCard from './BreakdownCard';

export default function ReportHistory({ history }) {
  const [expandedId, setExpandedId] = useState(null);

  if (!history || history.length === 0) {
    return (
      <div className="bg-white rounded-2xl p-6 text-center shadow-sm border border-slate-200">
        <Clock className="mx-auto text-slate-400 mb-2" size={24} />
        <p className="text-slate-500">No previous reports</p>
      </div>
    );
  }

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getScoreColor = (score) => {
    if (score < 40) return 'text-red-600';
    if (score <= 70) return 'text-amber-600';
    return 'text-green-600';
  };

  return (
    <section className="mt-8">
      <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
        <Clock size={20} className="text-slate-500" />
        Report History
      </h3>
      <div className="space-y-3">
        {history.map((report, idx) => (
          <div key={report.appeal_id || idx} className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
            <div 
              className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => setExpandedId(expandedId === report.appeal_id ? null : report.appeal_id)}
            >
              <div className="flex items-center gap-4">
                <div className={`font-bold text-lg ${getScoreColor(report.final_score)}`}>
                  {report.final_score}
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-800">
                    Appeal {report.appeal_id?.slice(0, 8) || `#${idx + 1}`}
                  </div>
                  <div className="text-xs text-slate-500">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
                {report.risk_level && (
                  <span className={`text-xs px-2 py-1 rounded-md border font-medium ${getRiskColor(report.risk_level)}`}>
                    {report.risk_level}
                  </span>
                )}
              </div>
              <div>
                {expandedId === report.appeal_id ? <ChevronUp size={20} className="text-slate-400" /> : <ChevronDown size={20} className="text-slate-400" />}
              </div>
            </div>
            {expandedId === report.appeal_id && (
              <div className="p-4 border-t border-slate-100 bg-slate-50">
                <div className="space-y-3">
                  {report.breakdown?.map((item, i) => (
                    <BreakdownCard key={i} {...item} />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
