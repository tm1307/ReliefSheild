import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function ShareReport({ score, breakdown }) {
  const [copied, setCopied] = useState(false);

  const handleShare = () => {
    let trustLevel = 'High Trust';
    if (score < 40) trustLevel = 'High Risk';
    else if (score <= 70) trustLevel = 'Moderate Concerns';

    let text = `🛡️ ReliefShield Trust Report\nScore: ${score}/100 — [${trustLevel}]\n\n`;
    
    breakdown.forEach(item => {
      const icon = item.status === 'Verified' ? '✅' : item.status === 'Flagged' ? '🚩' : '⚪';
      const points = item.points_deducted > 0 ? ` (-${item.points_deducted} pts)` : '';
      text += `${icon} ${item.check}: ${item.status} — ${item.details}${points}\n`;
    });

    text += `\nVerify appeals at: ${window.location.origin}`;

    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="flex justify-center">
      <button
        onClick={handleShare}
        className="flex items-center gap-2 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full font-medium text-sm transition-colors"
      >
        {copied ? <Check size={16} className="text-green-600" /> : <Copy size={16} />}
        {copied ? 'Copied to clipboard!' : 'Share Report'}
      </button>
    </div>
  );
}
