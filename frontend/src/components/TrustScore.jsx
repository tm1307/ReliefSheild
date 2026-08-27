import React, { useEffect, useState } from 'react';

export default function TrustScore({ score, summary }) {
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

  useEffect(() => {
    const timer = setTimeout(() => {
      setOffset(100 - score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  return (
    <div className="bg-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-200 text-center flex flex-col items-center">
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
      <h3 className={`text-xl font-bold mt-4 ${color}`}>{label}</h3>
      <p className="mt-3 text-slate-600 max-w-lg mx-auto text-sm sm:text-base leading-relaxed">
        {summary}
      </p>
    </div>
  );
}
