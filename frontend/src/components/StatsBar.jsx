import React, { useEffect, useState } from 'react';
import { BarChart3, Shield, AlertTriangle } from 'lucide-react';

function Counter({ end, duration = 1000 }) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime = null;
    let animationFrame;

    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      setCount(Math.floor(progress * end));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration]);

  return <span>{count}</span>;
}

export default function StatsBar({ stats }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-blue-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
          <Shield size={24} />
        </div>
        <div>
          <p className="text-sm text-slate-500 font-medium">Appeals Verified</p>
          <p className="text-2xl font-bold text-blue-600">
            <Counter end={stats.total_appeals} />
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow-sm border border-green-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-green-50 text-green-600 flex items-center justify-center">
          <BarChart3 size={24} />
        </div>
        <div>
          <p className="text-sm text-slate-500 font-medium">Average Score</p>
          <p className="text-2xl font-bold text-green-600">
            <Counter end={stats.avg_score} />
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl p-4 shadow-sm border border-red-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center">
          <AlertTriangle size={24} />
        </div>
        <div>
          <p className="text-sm text-slate-500 font-medium">Flagged</p>
          <p className="text-2xl font-bold text-red-600">
            <Counter end={stats.flagged_count} />
          </p>
        </div>
      </div>
    </div>
  );
}
