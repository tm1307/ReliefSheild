import React, { useEffect, useState } from 'react';

export default function TrustScore({ score, summary, risk_level, recommendations }) {
  const [offset, setOffset] = useState(100);
  
  let color = 'text-green-600';
  let strokeColor = '#16a34a';
  let label = 'High Trust';
  
  if (score < 40) {
    color = 'text-red-600';
    strokeColor = '#dc2626';
    label = 'High Risk';
  } else if (score <= 70) {
    color = 'text-amber-600';
    strokeColor = '#d97706';
    label = 'Moderate Concerns';
  }

  const getRiskBadge = (level) => {
    const lvl = level?.toLowerCase() || '';
    if (lvl.includes('critical')) return 'bg-red-100 text-red-800 border-red-200';
    if (lvl.includes('high')) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (lvl.includes('medium')) return 'bg-amber-100 text-amber-800 border-amber-200';
    if (lvl.includes('low')) return 'bg-green-100 text-green-800 border-green-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(100 - score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className={`bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 flex flex-col items-center ${score < 40 ? 'animate-pulse-slow' : ''}`}>
      <div className="relative w-40 h-40 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="3"
          />
          <circle
            cx="18"
            cy="18"
            r="16"
            fill="none"
            stroke={strokeColor}
            strokeWidth="3"
            strokeDasharray="100 100"
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="score-circle"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${color}`}>{score}</span>
          <span className="text-xs text-slate-400 font-medium uppercase tracking-wider mt-1">/ 100</span>
        </div>
      </div>
      
      <div className="text-center mt-4 flex flex-col items-center gap-2">
        <h3 className={`text-xl font-bold ${color}`}>{label}</h3>
        {risk_level && (
          <span className={`text-xs px-3 py-1 rounded-full border font-bold uppercase tracking-wider ${getRiskBadge(risk_level)}`}>
            {risk_level}
          </span>
        )}
      </div>

      <div className="mt-6 text-slate-600 max-w-2xl mx-auto w-full">
        <p className="text-sm sm:text-base leading-relaxed text-center mb-4">
          {summary}
        </p>
        
        {recommendations && recommendations.length > 0 && (
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 mt-4">
            <h4 className="font-semibold text-slate-800 mb-2 text-sm">Recommendations</h4>
            <ul className="list-disc list-inside text-sm space-y-1 text-slate-600">
              {recommendations.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
