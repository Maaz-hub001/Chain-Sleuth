import React from 'react';

interface BadgeProps {
  variant?: 'critical' | 'high' | 'medium' | 'low' | 'verified' | 'warning' | 'neutral' | 'info';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'neutral', children, className = '' }) => {
  const variantStyles = {
    critical: 'bg-red-950/70 text-red-400 border-red-800/60 font-semibold',
    high: 'bg-orange-950/70 text-orange-400 border-orange-800/60 font-semibold',
    medium: 'bg-amber-950/60 text-amber-300 border-amber-800/50',
    low: 'bg-blue-950/60 text-blue-300 border-blue-800/50',
    verified: 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60',
    warning: 'bg-yellow-950/60 text-yellow-300 border-yellow-800/50',
    neutral: 'bg-slate-900 text-slate-300 border-slate-800',
    info: 'bg-cyan-950/60 text-cyan-300 border-cyan-800/50',
  }[variant];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs border tracking-wide uppercase font-mono ${variantStyles} ${className}`}>
      {children}
    </span>
  );
};
