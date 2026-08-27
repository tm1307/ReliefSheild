import React from 'react';
import { FileText, Building, CreditCard, Link2, Info, AlertTriangle } from 'lucide-react';

export default function EvidenceGraph({ graph }) {
  if (!graph || !graph.nodes) return null;

  const rootNode = graph.nodes.find(n => n.id === 0);
  const childNodes = graph.nodes.filter(n => n.id !== 0);

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return 'border-green-500 bg-green-50 text-green-800';
      case 'flagged': return 'border-red-500 bg-red-50 text-red-800';
      case 'unverifiable': return 'border-gray-400 bg-gray-50 text-gray-800';
      default: return 'border-blue-400 bg-blue-50 text-blue-800';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'appeal': return <FileText size={16} />;
      case 'organisation': return <Building size={16} />;
      case 'payment': return <CreditCard size={16} />;
      case 'source': return <Link2 size={16} />;
      default: return <Info size={16} />;
    }
  };

  return (
    <div className="bg-slate-50 border border-slate-200 p-6 rounded-2xl overflow-x-auto relative">
      <div className="min-w-[600px] flex flex-col items-center gap-12 relative py-4">
        
        {rootNode && (
          <div className={`relative z-10 graph-node flex items-center gap-2 px-4 py-2 border-2 rounded-full font-medium text-sm shadow-sm cursor-help ${getStatusColor(rootNode.status)}`}>
            {getIcon(rootNode.type)}
            {rootNode.label}
            <div className="graph-tooltip top-full mt-2 left-1/2 -translate-x-1/2">
              {rootNode.detail}
            </div>
          </div>
        )}

        <div className="relative z-10 flex flex-row gap-8 justify-center w-full mt-8">
          {childNodes.map(node => (
            <div key={node.id} className="flex flex-col items-center group">
              <div className={`graph-node relative flex items-center gap-2 px-4 py-2 border-2 rounded-full font-medium text-sm shadow-sm cursor-help ${getStatusColor(node.status)}`}>
                {getIcon(node.type)}
                {node.label}
                <div className="graph-tooltip bottom-full mb-2 left-1/2 -translate-x-1/2">
                  {node.detail}
                </div>
              </div>
            </div>
          ))}
        </div>

        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          {graph.edges.map((edge, idx) => {
            if (edge.source === 0) {
              const childIdx = childNodes.findIndex(n => n.id === edge.target);
              if (childIdx === -1) return null;
              
              const totalChildren = childNodes.length;
              const startX = '50%';
              const startY = '40px'; 
              const spacePerChild = 100 / totalChildren;
              const endX = `${(childIdx + 0.5) * spacePerChild}%`;
              const endY = '100px';

              const strokeColor = edge.status === 'flagged' ? '#ef4444' : edge.status === 'verified' ? '#22c55e' : '#9ca3af';

              return (
                <g key={idx}>
                  <line x1={startX} y1={startY} x2={endX} y2={endY} stroke={strokeColor} strokeWidth="2" strokeDasharray={edge.status === 'unverifiable' ? '4' : '0'} />
                  <text x={endX} y="70" textAnchor="middle" fill="#64748b" fontSize="10" className="opacity-70">
                    {edge.label}
                  </text>
                </g>
              );
            }
            return null;
          })}
        </svg>

      </div>
    </div>
  );
}
