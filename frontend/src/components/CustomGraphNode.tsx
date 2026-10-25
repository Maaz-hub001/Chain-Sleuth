import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Target, Wallet, FileCode, Shuffle, Landmark, AlertTriangle } from 'lucide-react';
import type { WalletNode } from '../types';

interface CustomNodeProps {
  data: WalletNode;
  selected?: boolean;
}

export const CustomGraphNode = memo(({ data, selected }: CustomNodeProps) => {
  const isTarget = data.is_target;
  const entityType = data.entity_type;

  // Determine styling and icon based on entity type
  let borderStyle = 'border-sleuth-600';
  let bgStyle = 'bg-sleuth-900';
  let badgeColor = 'bg-slate-800 text-slate-300';
  let Icon = Wallet;

  if (isTarget) {
    borderStyle = 'border-cyanAccent-400 ring-2 ring-cyanAccent-500/30 shadow-lg shadow-cyanAccent-500/20';
    bgStyle = 'bg-sleuth-850';
    badgeColor = 'bg-cyanAccent-950 text-cyanAccent-400 border border-cyanAccent-800';
    Icon = Target;
  } else if (entityType === 'mixer') {
    borderStyle = 'border-red-500 ring-1 ring-red-500/30';
    bgStyle = 'bg-red-950/40';
    badgeColor = 'bg-red-900/60 text-red-300 border border-red-700';
    Icon = Shuffle;
  } else if (entityType === 'sanctioned_entity') {
    borderStyle = 'border-red-600 ring-2 ring-red-600/40';
    bgStyle = 'bg-red-950/60';
    badgeColor = 'bg-red-950 text-red-400 border border-red-800';
    Icon = AlertTriangle;
  } else if (entityType === 'exchange') {
    borderStyle = 'border-amber-500';
    bgStyle = 'bg-amber-950/30';
    badgeColor = 'bg-amber-950 text-amber-300 border border-amber-700';
    Icon = Landmark;
  } else if (entityType === 'contract') {
    borderStyle = 'border-purple-500';
    bgStyle = 'bg-purple-950/30';
    badgeColor = 'bg-purple-950 text-purple-300 border border-purple-800';
    Icon = FileCode;
  }

  const shortAddr = `${data.address.slice(0, 6)}...${data.address.slice(-4)}`;

  return (
    <div
      className={`relative px-3 py-2.5 rounded-lg border text-left min-w-[170px] transition-all cursor-pointer ${bgStyle} ${borderStyle} ${
        selected ? 'ring-2 ring-white shadow-md' : 'hover:border-slate-400'
      }`}
    >
      {/* Top handles */}
      <Handle type="target" position={Position.Top} className="!bg-sleuth-500 !w-2.5 !h-2.5 !border-slate-800" />
      <Handle type="target" position={Position.Left} className="!bg-sleuth-500 !w-2.5 !h-2.5 !border-slate-800" />

      {/* Header */}
      <div className="flex items-center justify-between gap-1 mb-1.5">
        <div className="flex items-center gap-1.5 overflow-hidden">
          <Icon className={`w-3.5 h-3.5 shrink-0 ${isTarget ? 'text-cyanAccent-400' : 'text-slate-400'}`} />
          <span className="text-[11px] font-semibold text-white truncate max-w-[100px]">
            {data.label || (isTarget ? 'Target' : 'Wallet')}
          </span>
        </div>
        <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${badgeColor}`}>
          {entityType.replace('_', ' ')}
        </span>
      </div>

      {/* Address */}
      <div className="font-mono text-[11px] text-slate-300 tracking-wider mb-2">
        {shortAddr}
      </div>

      {/* Metrics Footer */}
      <div className="flex items-center justify-between text-[10px] text-slate-400 border-t border-sleuth-700/60 pt-1.5">
        <div>
          In: <span className="text-emerald-400 font-mono">{data.total_inflow_eth.toFixed(1)} ETH</span>
        </div>
        <div>
          Out: <span className="text-orange-400 font-mono">{data.total_outflow_eth.toFixed(1)} ETH</span>
        </div>
      </div>

      {/* Bottom handles */}
      <Handle type="source" position={Position.Bottom} className="!bg-cyanAccent-500 !w-2.5 !h-2.5 !border-slate-800" />
      <Handle type="source" position={Position.Right} className="!bg-cyanAccent-500 !w-2.5 !h-2.5 !border-slate-800" />
    </div>
  );
});

CustomGraphNode.displayName = 'CustomGraphNode';
