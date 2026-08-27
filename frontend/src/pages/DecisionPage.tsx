// ============================================================
// Procurement Decision Page
// ============================================================

import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { ShieldCheck, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import type { ProcurementDecisionDetail } from '../types/api';

export default function DecisionPage() {
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to load procurement decisions." /></div>;

  const procurement = data.procurement ?? {};
  const vendorMeta = Object.fromEntries((data.vendors ?? []).map((v) => [v.vendor_id, v.display_name ?? v.vendor_id]));

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1100px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldCheck size={20} color="#16a34a" />
          Procurement Decision
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          Deterministic procurement gate results from the backend decision engine. Read-only — the frontend does not calculate eligibility.
        </p>
      </div>

      <div className="alert alert-info" style={{ marginBottom: '20px' }}>
        <AlertCircle size={14} />
        <span>
          <strong>Deterministic procurement gate</strong> — Results are computed by strict rule-based logic in the backend.
          No LLM output can alter procurement eligibility.
          <strong> AI diagnostic advisory</strong> is shown separately on the Diagnostics page.
        </span>
      </div>

      {Object.entries(procurement).map(([vendorId, dec]) => (
        <ProcurementCard
          key={vendorId}
          vendorId={vendorId}
          displayName={vendorMeta[vendorId] ?? vendorId}
          decision={dec as ProcurementDecisionDetail}
        />
      ))}
    </div>
  );
}

function ProcurementCard({
  vendorId, displayName, decision,
}: { vendorId: string; displayName: string; decision: ProcurementDecisionDetail }) {
  const isEligible = decision.decision === 'ELIGIBLE';

  return (
    <div
      className="card"
      style={{
        marginBottom: '20px',
        borderColor: isEligible ? '#16a34a44' : '#dc262644',
      }}
    >
      <div className="card-header">
        <div>
          <span style={{ fontWeight: 700, fontSize: '15px' }}>{displayName}</span>
          <span style={{ marginLeft: '8px', fontSize: '11px', color: '#64748b' }}>({vendorId})</span>
        </div>
        <StatusBadge status={decision.decision} />
      </div>

      {/* Gate matrix */}
      {decision.gates?.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div className="section-title">Gate Results</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px', marginTop: '8px' }}>
            {decision.gates.map((g, i) => (
              <div
                key={i}
                className="metric-box"
                style={{ borderColor: g.passed ? '#16a34a44' : '#dc262644' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>{g.gate}</span>
                  {g.passed ? (
                    <CheckCircle2 size={14} color="#16a34a" aria-label="Gate passed" />
                  ) : (
                    <XCircle size={14} color="#dc2626" aria-label="Gate failed" />
                  )}
                </div>
                {g.value !== undefined && (
                  <div style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                    Value: <span style={{ color: '#94a3b8' }}>{String(g.value)}</span>
                    {g.required !== undefined && (
                      <> · Required: <span style={{ color: '#64748b' }}>{String(g.required)}</span></>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reasons */}
      {decision.reasons?.length > 0 && (
        <div>
          <div className="section-title">Decision Reasons</div>
          <ul style={{ listStyle: 'none', padding: 0, marginTop: '8px' }}>
            {decision.reasons.map((r, i) => (
              <li
                key={i}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '8px',
                  padding: '6px 0', borderBottom: '1px solid #1e293b', fontSize: '13px', color: '#94a3b8',
                }}
              >
                {isEligible ? (
                  <CheckCircle2 size={13} color="#16a34a" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
                ) : (
                  <XCircle size={13} color="#dc2626" style={{ flexShrink: 0, marginTop: '2px' }} aria-hidden="true" />
                )}
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
