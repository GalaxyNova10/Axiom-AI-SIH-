// ============================================================
// Axiom AI — Glassmorphic Sidebar with Theme Toggle
// ============================================================

import { Link, useLocation } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from './StatusBadge';
import ThemeToggle from './ThemeToggle';
import {
  LayoutDashboard, Users, Map, Brain, Gavel,
  ArrowUpRight, ShieldCheck, FileText, Database, Hexagon,
} from 'lucide-react';

const evalId = 'demo';

const navItems = [
  { name: 'Overview',        path: '/',                                          icon: LayoutDashboard },
  { name: 'Vendors',         path: `/evaluation/${evalId}/vendors`,              icon: Users },
  { name: 'Failure Map',     path: `/evaluation/${evalId}/failure-map`,          icon: Map },
  { name: 'Diagnostics',     path: `/evaluation/${evalId}/diagnostics`,          icon: Brain },
  { name: 'Decision',        path: `/evaluation/${evalId}/decision`,             icon: Gavel },
  { name: 'Scale-Up',        path: `/evaluation/${evalId}/scale-up`,             icon: ArrowUpRight },
  { name: 'Authorization',   path: `/evaluation/${evalId}/authorization`,        icon: ShieldCheck },
  { name: 'Audit Trail',     path: `/evaluation/${evalId}/audit`,                icon: FileText },
  { name: 'Data Governance', path: `/evaluation/${evalId}/governance`,           icon: Database },
];

export default function Sidebar() {
  const location = useLocation();
  const { data } = useDemoContext();

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <aside className="app-sidebar" role="navigation" aria-label="Main navigation">
      {/* Brand */}
      <div style={{ padding: '24px 20px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{
            width: '32px', height: '32px', borderRadius: 'var(--r-md)',
            background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: 'var(--accent-glow)',
          }}>
            <Hexagon size={16} color="white" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 750, color: 'var(--text-primary)', letterSpacing: '-0.03em', lineHeight: 1 }}>
              Axiom AI
            </div>
            <div style={{ fontSize: '10px', fontWeight: 500, color: 'var(--text-faint)', letterSpacing: '0.04em', marginTop: '2px' }}>
              GOVERNANCE ENGINE
            </div>
          </div>
        </Link>
        <ThemeToggle />
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '0 12px', overflowY: 'auto' }}>
        <div style={{ fontSize: '11px', fontWeight: 650, letterSpacing: '0.05em', color: 'var(--text-faint)', textTransform: 'uppercase', padding: '0 8px', marginBottom: '8px' }}>
          Evaluations
        </div>
        {navItems.map((item) => {
          const active = isActive(item.path);
          return (
            <Link
              key={item.name}
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 12px',
                borderRadius: 'var(--r-md)',
                color: active ? 'var(--accent-hover)' : 'var(--text-secondary)',
                background: active ? 'var(--accent-muted)' : 'transparent',
                fontWeight: active ? 600 : 500,
                fontSize: '13.5px',
                textDecoration: 'none',
                border: active ? '1px solid rgba(6, 182, 212, 0.2)' : '1px solid transparent',
                boxShadow: active ? '0 0 12px rgba(6, 182, 212, 0.08)' : 'none',
                transition: 'all 0.15s ease',
                marginBottom: '2px',
              }}
              onMouseEnter={(e) => {
                if (!active) {
                  e.currentTarget.style.background = 'var(--bg-elevated)';
                  e.currentTarget.style.color = 'var(--text-primary)';
                }
              }}
              onMouseLeave={(e) => {
                if (!active) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }
              }}
            >
              <item.icon size={16} strokeWidth={active ? 2.5 : 2} style={{ opacity: active ? 1 : 0.7 }} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div style={{ padding: '20px', borderTop: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>Environment</span>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', background: 'var(--bg-sunken)', padding: '2px 6px', borderRadius: '4px' }}>DEMO</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>API</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', fontWeight: 600, color: 'var(--eligible)' }}>
              <span className="dot dot-eligible dot-pulse" /> Connected
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>Evidence</span>
            <StatusBadge status="VERIFIED" size="sm" />
          </div>
          {data && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>Vendors</span>
              <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--accent)' }}>{data.vendors?.length ?? 0}</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
