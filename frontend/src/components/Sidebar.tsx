// ============================================================
// Sidebar Navigation
// ============================================================

import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, Map, Brain, ShieldCheck,
  TrendingUp, UserCheck, ClipboardList, Database, Activity,
} from 'lucide-react';
import { useDemoContext } from '../context/DemoContext';

const BASE_NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
];

const EVAL_NAV = [
  { icon: Users, label: 'Vendors', segment: 'vendors' },
  { icon: Map, label: 'Failure Cartography', segment: 'failure-map' },
  { icon: Brain, label: 'Diagnostics', segment: 'diagnostics' },
  { icon: ShieldCheck, label: 'Procurement Decision', segment: 'decision' },
  { icon: TrendingUp, label: 'Scale-Up', segment: 'scale-up' },
  { icon: UserCheck, label: 'Human Authorization', segment: 'authorization' },
  { icon: ClipboardList, label: 'Audit', segment: 'audit' },
  { icon: Database, label: 'Data Governance', segment: 'governance' },
];

export default function Sidebar() {
  const { data } = useDemoContext();
  const evalId = data?.vendors?.[0]?.evaluation_id;

  return (
    <aside
      className="flex flex-col"
      style={{
        width: '220px',
        minHeight: '100vh',
        background: '#0f172a',
        borderRight: '1px solid #1e293b',
        padding: '0',
        flexShrink: 0,
      }}
      aria-label="Main navigation"
    >
      {/* Logo */}
      <div style={{ padding: '20px 16px 16px', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '32px', height: '32px',
              background: 'linear-gradient(135deg, #1d4ed8, #7c3aed)',
              borderRadius: '8px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
            aria-hidden="true"
          >
            <Activity size={16} color="white" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '14px', color: '#f1f5f9' }}>Axiom AI</div>
            <div style={{ fontSize: '10px', color: '#64748b', letterSpacing: '0.05em' }}>GOVERNANCE PLATFORM</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto' }}>
        {BASE_NAV.map(({ to, icon: Icon, label }) => (
          <NavItem key={to} to={to} icon={<Icon size={16} />} label={label} exact />
        ))}

        {evalId && (
          <>
            <div className="section-title" style={{ padding: '16px 8px 4px' }}>
              Evaluation
            </div>
            {EVAL_NAV.map(({ icon: Icon, label, segment }) => (
              <NavItem
                key={segment}
                to={`/evaluation/${evalId}/${segment}`}
                icon={<Icon size={16} />}
                label={label}
              />
            ))}
          </>
        )}
      </nav>

      {/* Principle */}
      <div style={{ padding: '12px', borderTop: '1px solid #1e293b' }}>
        <div className="principle-banner" style={{ fontSize: '10px', padding: '8px 10px' }}>
          "AI assists. Evidence proves.<br />Rules gate. Humans authorize."
        </div>
      </div>
    </aside>
  );
}

function NavItem({
  to,
  icon,
  label,
  exact,
}: {
  to: string;
  icon: React.ReactNode;
  label: string;
  exact?: boolean;
}) {
  const location = useLocation();
  const isActive = exact ? location.pathname === to : location.pathname.startsWith(to);

  return (
    <NavLink
      to={to}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '8px 10px',
        borderRadius: '6px',
        marginBottom: '2px',
        color: isActive ? '#93c5fd' : '#94a3b8',
        background: isActive ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
        fontSize: '13px',
        fontWeight: isActive ? 600 : 400,
        transition: 'all 0.15s ease',
        textDecoration: 'none',
      }}
      onMouseEnter={(e) => {
        if (!isActive) {
          (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.04)';
          (e.currentTarget as HTMLElement).style.color = '#e2e8f0';
        }
      }}
      onMouseLeave={(e) => {
        if (!isActive) {
          (e.currentTarget as HTMLElement).style.background = 'transparent';
          (e.currentTarget as HTMLElement).style.color = '#94a3b8';
        }
      }}
      aria-current={isActive ? 'page' : undefined}
    >
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}
