// ============================================================
// Axiom AI — Root App with React Router
// ============================================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DemoProvider } from './context/DemoContext';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import VendorsPage from './pages/VendorsPage';
import VendorDetailPage from './pages/VendorDetailPage';
import FailureMapPage from './pages/FailureMapPage';
import DiagnosticsPage from './pages/DiagnosticsPage';
import DecisionPage from './pages/DecisionPage';
import ScaleUpPage from './pages/ScaleUpPage';
import AuthorizationPage from './pages/AuthorizationPage';
import AuditPage from './pages/AuditPage';
import GovernancePage from './pages/GovernancePage';

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#0f172a' }}>
      <Sidebar />
      <main
        style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', minWidth: 0 }}
        id="main-content"
        tabIndex={-1}
        aria-label="Main content"
      >
        {children}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <DemoProvider>
      <BrowserRouter>
        <AppLayout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<Navigate to="/" replace />} />

            {/* Evaluation routes */}
            <Route path="/evaluation/:evaluationId/vendors" element={<VendorsPage />} />
            <Route path="/evaluation/:evaluationId/vendors/:vendorId" element={<VendorDetailPage />} />
            <Route path="/evaluation/:evaluationId/failure-map" element={<FailureMapPage />} />
            <Route path="/evaluation/:evaluationId/diagnostics" element={<DiagnosticsPage />} />
            <Route path="/evaluation/:evaluationId/decision" element={<DecisionPage />} />
            <Route path="/evaluation/:evaluationId/scale-up" element={<ScaleUpPage />} />
            <Route path="/evaluation/:evaluationId/authorization" element={<AuthorizationPage />} />
            <Route path="/evaluation/:evaluationId/audit" element={<AuditPage />} />
            <Route path="/evaluation/:evaluationId/governance" element={<GovernancePage />} />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </DemoProvider>
  );
}
