import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, Activity, PlusCircle, FileText, Database, Settings, LayoutDashboard } from 'lucide-react';
import { api } from '../services/api';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [providerHealth, setProviderHealth] = useState<string>('checking');

  useEffect(() => {
    api.getProvidersHealth()
      .then((data) => {
        const hasError = data.providers?.some((p) => p.status === 'error');
        setProviderHealth(hasError ? 'degraded' : 'operational');
      })
      .catch(() => setProviderHealth('offline'));
  }, []);

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Threat Intel', path: '/intelligence', icon: Database },
    { label: 'Reports', path: '/reports', icon: FileText },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-sleuth-900/90 backdrop-blur-md border-b border-sleuth-700/60 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo and Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded bg-cyanAccent-500/10 border border-cyanAccent-500/40 flex items-center justify-center text-cyanAccent-400 group-hover:border-cyanAccent-400 transition-colors shadow-sm shadow-cyanAccent-500/20">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-white font-mono flex items-center gap-1.5">
              Chain<span className="text-cyanAccent-400">Sleuth</span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.2 bg-slate-800 text-slate-300 rounded border border-slate-700">MVP</span>
            </span>
            <p className="text-[10px] text-slate-400 font-sans tracking-wide">Blockchain Fraud & Evidence Intelligence</p>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1 bg-sleuth-850/80 border border-sleuth-700/50 rounded-lg p-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                  active
                    ? 'bg-sleuth-700/80 text-cyanAccent-400 shadow-sm border border-sleuth-600/50'
                    : 'text-slate-300 hover:text-white hover:bg-sleuth-800/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Right side: Provider Status and Action */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 bg-sleuth-850/90 rounded border border-sleuth-700/70 text-xs text-slate-300">
            <span
              className={`w-2 h-2 rounded-full animate-pulse ${
                providerHealth === 'operational'
                  ? 'bg-emerald-400'
                  : providerHealth === 'degraded'
                  ? 'bg-amber-400'
                  : 'bg-red-500'
              }`}
            />
            <span className="font-mono text-[11px] text-slate-300">
              RPC: {providerHealth === 'operational' ? 'Live' : providerHealth}
            </span>
          </div>

          <Link
            to="/investigations/new"
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-cyanAccent-600 hover:bg-cyanAccent-500 text-slate-950 font-semibold text-xs tracking-wide transition-all shadow-md shadow-cyanAccent-600/20 active:scale-95"
          >
            <PlusCircle className="w-4 h-4 text-slate-950" />
            <span>New Investigation</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
