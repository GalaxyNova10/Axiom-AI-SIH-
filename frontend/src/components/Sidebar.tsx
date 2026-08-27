import { Link, useLocation } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import {
  LayoutDashboard, Users, Map, Brain,
  ShieldCheck, TrendingUp, UserCheck, ClipboardList, Database
} from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function Sidebar() {
  const { pathname } = useLocation();
  const { data } = useDemoContext();
  const evalId = data?.vendors?.[0]?.evaluation_id ?? 'demo';

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + '/');

  const navItems = [
    { name: 'Overview', path: '/', icon: LayoutDashboard },
    { name: 'Vendors', path: `/evaluation/${evalId}/vendors`, icon: Users },
    { name: 'Failure Cartography', path: `/evaluation/${evalId}/failure-map`, icon: Map },
    { name: 'Diagnostics', path: `/evaluation/${evalId}/diagnostics`, icon: Brain },
    { name: 'Procurement', path: `/evaluation/${evalId}/decision`, icon: ShieldCheck },
    { name: 'Scale-Up', path: `/evaluation/${evalId}/scale-up`, icon: TrendingUp },
    { name: 'Authorization', path: `/evaluation/${evalId}/authorization`, icon: UserCheck },
    { name: 'Audit Trail', path: `/evaluation/${evalId}/audit`, icon: ClipboardList },
    { name: 'Data Governance', path: `/evaluation/${evalId}/governance`, icon: Database },
  ];

  return (
    <aside style={{
      width: '260px',
      background: 'var(--surface-muted)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      flexShrink: 0
    }}>
      {/* Brand Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--text)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'white', fontWeight: 800, fontSize: '18px', letterSpacing: '-0.05em' }}>A</span>
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px', letterSpacing: '-0.01em', color: 'var(--text)' }}>AXIOM AI</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 500 }}>Evidence-Gated Procurement</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '20px 12px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '4px' }}>
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
                background: active ? 'var(--surface)' : 'transparent',
                fontWeight: active ? 600 : 500,
                fontSize: '13.5px',
                textDecoration: 'none',
                border: active ? '1px solid var(--border)' : '1px solid transparent',
                boxShadow: active ? 'var(--shadow-xs)' : 'none',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                if (!active) e.currentTarget.style.background = 'var(--surface)';
              }}
              onMouseLeave={(e) => {
                if (!active) e.currentTarget.style.background = 'transparent';
              }}
            >
              <item.icon size={16} strokeWidth={active ? 2.5 : 2} style={{ opacity: active ? 1 : 0.7 }} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div style={{ padding: '20px', borderTop: '1px solid var(--border)', background: 'var(--surface)' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>Environment</span>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text)', background: 'var(--surface-sunken)', padding: '2px 6px', borderRadius: '4px' }}>DEMO</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>API</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', fontWeight: 600, color: 'var(--eligible)' }}>
              <span className="dot dot-eligible" /> Connected
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11.5px', color: 'var(--text-muted)', fontWeight: 500 }}>Evidence</span>
            <StatusBadge status="VERIFIED" size="sm" />
          </div>
        </div>
      </div>
    </aside>
  );
}
