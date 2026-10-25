import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { LandingPage } from './features/landing/LandingPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { NewInvestigationPage } from './features/investigations/NewInvestigationPage';
import { InvestigationDetailPage } from './features/investigations/InvestigationDetailPage';
import { ThreatIntelPage } from './features/intelligence/ThreatIntelPage';
import { ReportArchivePage } from './features/reports/ReportArchivePage';
import { SettingsPage } from './features/settings/SettingsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-sleuth-950 text-slate-100 flex flex-col font-sans">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/investigations/new" element={<NewInvestigationPage />} />
              <Route path="/investigations/:id" element={<InvestigationDetailPage />} />
              <Route path="/intelligence" element={<ThreatIntelPage />} />
              <Route path="/reports" element={<ReportArchivePage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;
