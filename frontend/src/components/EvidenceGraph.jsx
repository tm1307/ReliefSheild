import React, { useRef, useEffect, useState } from 'react';
import { FileText, Building, CreditCard, Link2, Info } from 'lucide-react';

export default function EvidenceGraph({ graph }) {
  const containerRef = useRef(null);
  const nodeRefs = useRef({});
  const [positions, setPositions] = useState({});

  useEffect(() => {
    if (!containerRef.current || !graph || !graph.nodes) return;
    
    // Allow a small delay for DOM to settle
    const timer = setTimeout(() => {
      if (!containerRef.current) return;
      const containerRect = containerRef.current.getBoundingClientRect();
      const newPositions = {};
      Object.entries(nodeRefs.current).forEach(([id, el]) => {
        if (el) {
          const rect = el.getBoundingClientRect();
          newPositions[id] = {
            x: rect.left - containerRect.left + rect.width / 2,
            y: rect.top - containerRect.top + rect.height / 2,
          };
        }
      });
      setPositions(newPositions);
    }, 50);
    
    return () => clearTimeout(timer);
  }, [graph]);

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
    <div className="bg-slate-50 border border-slate-200 p-6 rounded-2xl overflow-x-auto relative flex flex-col items-center">
      <div 
        className="min-w-[600px] w-full flex flex-col items-center gap-16 relative py-8"
        ref={containerRef}
      >
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          {graph.edges.map((edge, idx) => {
            const sourcePos = positions[edge.source];
            const targetPos = positions[edge.target];
            
            if (!sourcePos || !targetPos) return null;

            const strokeColor = edge.status === 'flagged' ? '#ef4444' : edge.status === 'verified' ? '#22c55e' : '#9ca3af';
            
            // Quadratic bezier curve
            const midY = (sourcePos.y + targetPos.y) / 2;
            const path = `M ${sourcePos.x} ${sourcePos.y} Q ${(sourcePos.x + targetPos.x)/2} ${midY} ${targetPos.x} ${targetPos.y}`;

            const labelX = (sourcePos.x + targetPos.x) / 2;
            const labelY = (sourcePos.y + targetPos.y) / 2 - 10;

            return (
              <g key={idx}>
                <path 
                  d={path} 
                  fill="none"
                  stroke={strokeColor} 
                  strokeWidth="2" 
                  strokeDasharray={edge.status === 'unverifiable' ? '6 4' : '0'} 
                />
                <rect
                  x={labelX - edge.label.length * 3 - 10}
                  y={labelY - 10}
                  width={edge.label.length * 6 + 20}
                  height="20"
                  fill="white"
                  fillOpacity="0.8"
                  rx="4"
                />
                <text x={labelX} y={labelY + 4} textAnchor="middle" fill="#64748b" fontSize="11" className="font-medium">
                  {edge.label}
                </text>
              </g>
            );
          })}
        </svg>

        {rootNode && (
          <div 
            ref={el => nodeRefs.current[rootNode.id] = el}
            className={`relative z-10 graph-node flex items-center gap-2 px-4 py-2 border-2 rounded-full font-medium text-sm shadow-sm cursor-help ${getStatusColor(rootNode.status)}`}
          >
            {getIcon(rootNode.type)}
            {rootNode.label}
            <div className="graph-tooltip top-full mt-2 left-1/2 -translate-x-1/2">
              {rootNode.detail}
            </div>
          </div>
        )}

        <div className="relative z-10 flex flex-row gap-8 justify-center w-full">
          {childNodes.map(node => (
            <div 
              key={node.id} 
              ref={el => nodeRefs.current[node.id] = el}
              className={`graph-node relative flex items-center gap-2 px-4 py-2 border-2 rounded-full font-medium text-sm shadow-sm cursor-help ${getStatusColor(node.status)}`}
            >
              {getIcon(node.type)}
              {node.label}
              <div className="graph-tooltip bottom-full mb-2 left-1/2 -translate-x-1/2">
                {node.detail}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-6 flex items-center gap-6 text-sm text-slate-600 bg-white px-4 py-2 rounded-full border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div> Verified
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div> Flagged
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gray-400 border border-gray-400 border-dashed"></div> Unverifiable
        </div>
      </div>
    </div>
  );
}
