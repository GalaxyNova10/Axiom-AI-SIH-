// ============================================================
// Audit Trail Page
// ============================================================

import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { ClipboardList, Lock } from 'lucide-react';

export default function AuditPage() {
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to view the audit trail." /></div>;

  const audit = data.audit_summary;
  const auth = data.human_authorization;

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '900px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ClipboardList size={20} color="#3b82f6" />
          Audit Trail
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          Chronological, immutable record of governance events. All entries are append-only.
        </p>
      </div>

      <div className="alert alert-info" style={{ marginBottom: '20px' }}>
        <Lock size={14} />
        <span>Audit records are immutable and append-only. They cannot be modified by any actor including administrators.</span>
      </div>

      {/* Governance state summary */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <span style={{ fontWeight: 600 }}>Governance State Summary</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
          {audit && Object.entries(audit).map(([k, v]) => (
            <AuditRow
              key={k}
              label={k.replace(/_/g, ' ')}
              value={typeof v === 'boolean' ? (v ? 'TRUE' : 'FALSE') : String(v)}
              actor="SYSTEM"
              isBool={typeof v === 'boolean'}
              boolVal={typeof v === 'boolean' ? v : undefined}
            />
          ))}
        </div>
      </div>

      {/* Authorization events */}
      {auth && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600 }}>Authorization Events</span>
            <StatusBadge status={auth.status} />
          </div>
          <div>
            {[
              {
                event: 'Authorization Request Created',
                actor: auth.authorizing_officer_id ?? 'OFFICER',
                detail: `Vendor: ${auth.vendor_id} · Action: ${auth.requested_action}`,
                transition: `AI Recommendation: ${auth.ai_recommendation}`,
              },
              {
                event: 'Human Decision Recorded',
                actor: auth.authorizing_officer_id ?? 'OFFICER',
                detail: `Decision: ${auth.human_decision ?? 'PENDING'}`,
                transition: `Status → ${auth.status}`,
              },
              ...(auth.escalation_required ? [{
                event: 'Escalation Triggered',
                actor: 'SYSTEM',
                detail: `Override detected — sent to ${auth.escalation_destination ?? 'HIGHER_AUTHORITY'}`,
                transition: 'Maker-Checker Policy Applied',
              }] : []),
            ].map((entry, i) => (
              <div
                key={i}
                style={{
                  padding: '12px 0', borderBottom: '1px solid #1e293b',
                  display: 'grid', gridTemplateColumns: '24px 1fr', gap: '12px', alignItems: 'start',
                }}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6', marginTop: '5px', marginLeft: '8px' }} aria-hidden="true" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '13px', color: '#f1f5f9' }}>{entry.event}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>{entry.detail}</div>
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                    Actor: <span style={{ color: '#93c5fd' }}>{entry.actor}</span>
                    {' · '}
                    Transition: {entry.transition}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pipeline stages */}
      <div className="card">
        <div className="card-header">
          <span style={{ fontWeight: 600 }}>14-Stage Pipeline Completion</span>
          <StatusBadge status="AUTHORIZED" dot />
        </div>
        {[
          'Stage 1: Outcome Contract Generated & Locked',
          'Stage 2: Government Pilot Twin Created & Locked',
          'Stage 3: Stratified Test Suite Generated (24 strata)',
          'Stage 4: Golden Reference Suite Verification Passed',
          'Stage 5: Vendor Artifacts Registered & Frozen (SHA-256)',
          'Stage 6: Black-Box Vendor Evaluation Completed',
          'Stage 7: Evidence Records Generated with Cryptographic Provenance',
          'Stage 8: Evidence Confidence Calculated',
          'Stage 9: Failure Cartography Generated',
          'Stage 9.5: Advisory Forensic Diagnostics Generated',
          'Stage 10: Deterministic Procurement Decision Made',
          'Stage 11: Vendor Response Window Opened (VendorC)',
          'Stage 12: Human Authorization Recorded',
          'Stage 13: Scale-Up Policy Evaluated (District Beta)',
          'Stage 14: Data Governance Schedule Created',
        ].map((stage, i) => (
          <div
            key={i}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 0', borderBottom: '1px solid #1e293b' }}
          >
            <div style={{ width: '20px', height: '20px', borderRadius: '50%', background: '#14532d', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }} aria-hidden="true">
              <span style={{ fontSize: '9px', color: '#4ade80', fontWeight: 700 }}>✓</span>
            </div>
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>{stage}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function AuditRow({
  label, value, actor, isBool, boolVal,
}: {
  label: string; value: string; actor: string; isBool?: boolean; boolVal?: boolean;
}) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr auto', gap: '12px', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #1e293b' }}>
      <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'capitalize' }}>{label}</span>
      {isBool !== undefined ? (
        <StatusBadge status={boolVal ? 'ELIGIBLE' : 'REJECTED'} />
      ) : (
        <span style={{ fontSize: '12px', color: '#f1f5f9', fontWeight: 500 }}>{value}</span>
      )}
      <span style={{ fontSize: '10px', color: '#64748b' }}>Actor: {actor}</span>
    </div>
  );
}
