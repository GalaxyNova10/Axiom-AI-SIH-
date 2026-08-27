import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { ClipboardList, Shield, Lock, CheckCircle } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface AuditEvent {
  id: string;
  time: string;
  actor: string;
  action: string;
  icon: LucideIcon;
  done: boolean;
  detail: string;
  pending?: boolean;
}

export default function AuditPage() {
  const { data } = useDemoContext();

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load the audit trail.</p>
      </div>
    );
  }

  const audit = data.audit_summary ?? {};
  const vendors = data.vendors ?? [];
  const procurement = data.procurement ?? {};
  const humanAuth = data.human_authorization ?? {};

  // Build synthetic event ledger from available data
  const events: AuditEvent[] = [
    { id: 'e1', time: 'Stage 1', actor: 'System', action: 'CONTRACT_LOCKED', icon: Lock, done: !!(audit as Record<string, any>).contract_locked, detail: 'Outcome contract hashed and locked. KPI: Delivery Success Rate ≥ 80.0%.' },
    { id: 'e2', time: 'Stage 2', actor: 'System', action: 'PILOT_TWIN_LOCKED', icon: Shield, done: !!(audit as Record<string, any>).twin_locked, detail: 'Pilot Twin parameters captured and frozen for District Alpha.' },
    { id: 'e3', time: 'Stage 4', actor: 'System', action: 'GOLDEN_SUITE_AUTHORIZED', icon: CheckCircle, done: !!(audit as Record<string, any>).evaluator_authorized, detail: 'Evaluator passed Golden Reference Suite before vendor evaluation.' },
    ...vendors.map((v, i): AuditEvent => ({
      id: `e-vendor-${i}`,
      time: `Stage ${7 + i}`,
      actor: 'Decision Engine',
      action: `VENDOR_EVALUATED_${v.vendor_id.toUpperCase()}`,
      icon: Shield,
      done: true,
      detail: `${v.display_name ?? v.vendor_id}: ${procurement[v.vendor_id]?.decision ?? v.procurement_recommendation ?? 'PENDING'}. Accuracy: ${v.accuracy?.toFixed(1) ?? '—'}%`,
    })),
    { id: 'e-auth', time: 'Stage 13', actor: humanAuth.authorizing_officer_id ? String(humanAuth.authorizing_officer_id) : 'Pending Officer', action: 'HUMAN_AUTHORIZATION', icon: Lock, done: !!humanAuth.status, detail: humanAuth.status ? `Status: ${humanAuth.status}. Justification recorded.` : 'Awaiting officer authorization.', pending: !humanAuth.status },
  ];

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>IMMUTABLE LOG</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ClipboardList size={28} color="var(--accent)" /> Audit Trail
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Append-only governance audit history. Every decision is recorded and traceable.
        </p>
      </div>

      {/* Integrity Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '32px' }}>
        <div className="card" style={{ padding: '14px' }}>
          <div className="metric metric-sm">
            <span className="metric-label">Contract Lock</span>
            <div style={{ marginTop: '4px' }}>
              <StatusBadge status={audit.contract_locked ? 'LOCKED' : 'PENDING'} dot />
            </div>
          </div>
        </div>
        <div className="card" style={{ padding: '14px' }}>
          <div className="metric metric-sm">
            <span className="metric-label">Pilot Twin Lock</span>
            <div style={{ marginTop: '4px' }}>
              <StatusBadge status={audit.twin_locked ? 'LOCKED' : 'PENDING'} dot />
            </div>
          </div>
        </div>
        <div className="card" style={{ padding: '14px' }}>
          <div className="metric metric-sm">
            <span className="metric-label">Evaluator Auth</span>
            <div style={{ marginTop: '4px' }}>
              <StatusBadge status={audit.evaluator_authorized ? 'AUTHORIZED' : 'PENDING'} dot />
            </div>
          </div>
        </div>
        <div className="card" style={{ padding: '14px' }}>
          <div className="metric metric-sm">
            <span className="metric-label">Human Auth</span>
            <div style={{ marginTop: '4px' }}>
              <StatusBadge status={String(audit.human_authorization_status || humanAuth.status || 'PENDING')} dot />
            </div>
          </div>
        </div>
        {!!audit.scale_up_policy_case && (
          <div className="card" style={{ padding: '14px' }}>
            <div className="metric metric-sm">
              <span className="metric-label">Scale-Up Policy</span>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text)', marginTop: '4px' }}>{String(audit.scale_up_policy_case)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Event Timeline */}
      <h2 className="font-heading" style={{ marginBottom: '20px' }}>Event Ledger</h2>
      <div style={{ position: 'relative', paddingLeft: '32px' }}>
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '15px', width: '2px', background: 'var(--border-subtle)' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {events.map((evt, i) => {
            const Icon = evt.icon;
            const isPending = 'pending' in evt && evt.pending;
            return (
              <div key={evt.id} className="stagger" style={{ position: 'relative', animationDelay: `${i * 60}ms` }}>
                <div style={{
                  position: 'absolute', left: '-32px', top: '8px', width: '30px', height: '30px', marginLeft: '1px',
                  borderRadius: '50%',
                  background: evt.done ? 'var(--text)' : 'var(--surface)',
                  border: evt.done ? 'none' : '2px solid var(--border-strong)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1,
                  color: evt.done ? 'white' : 'var(--text-muted)'
                }}>
                  <Icon size={13} strokeWidth={2.5} />
                </div>
                <div className="card" style={{ padding: '12px 16px', opacity: isPending ? 0.65 : 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="font-label" style={{ color: 'var(--text-faint)' }}>{evt.time}</span>
                      <span style={{ fontSize: '14px', fontWeight: 700 }}>{evt.action.replace(/_/g, ' ')}</span>
                    </div>
                    <StatusBadge status={evt.done ? 'VERIFIED' : 'PENDING'} size="sm" />
                  </div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '13px' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 500, flexShrink: 0 }}>{evt.actor}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>{evt.detail}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Signature Strip */}
      <div style={{ marginTop: '32px', background: 'var(--surface-muted)', border: '1px solid var(--border)', borderRadius: '8px', padding: '14px 20px' }}>
        <div className="font-label" style={{ marginBottom: '4px' }}>Audit Chain Signature</div>
        <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)', wordBreak: 'break-all' }}>
          sha256:axiom-demo-001-{Date.now().toString(16)}
        </div>
      </div>
    </div>
  );
}
