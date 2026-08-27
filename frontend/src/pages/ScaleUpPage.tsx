// ============================================================
// Scale-Up Page
// ============================================================

import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { TrendingUp, AlertCircle } from 'lucide-react';

export default function ScaleUpPage() {
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to load scale-up evaluation." /></div>;

  const su = data.scale_up;

  if (!su) {
    return (
      <div style={{ padding: '28px' }}>
        <EmptyState title="No scale-up data" message="Scale-up evaluation is not available for this result." />
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '900px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <TrendingUp size={20} color="#3b82f6" />
          Regional Scale-Up Evaluation
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          Passing District A does not grant automatic scaling to District B. Each scale-up is independently re-evaluated.
        </p>
      </div>

      <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
        <AlertCircle size={14} />
        <span>
          The frontend never authorizes deployment. Scale-up decisions are made by the backend policy engine and presented here read-only.
        </span>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <span style={{ fontWeight: 600 }}>Scale-Up Decision</span>
          <StatusBadge status={su.status} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '16px' }}>
          <MetricBox label="Request ID" value={su.request_id} mono />
          <MetricBox label="Vendor" value={su.vendor_id} />
          <MetricBox label="Target District" value={su.target_district} />
          <MetricBox label="Policy Case" value={su.policy_case} />
          <MetricBox label="Scale Eligible" value={su.scale_eligible ? 'YES' : 'NO'} />
          <MetricBox label="Vendor Response Required" value={su.vendor_response_window_required ? 'YES' : 'NO'} />
        </div>

        {su.failure_map_status && (
          <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span className="section-title" style={{ margin: 0 }}>Failure Map Status:</span>
            <StatusBadge status={su.failure_map_status} />
          </div>
        )}

        {su.matched_failure_strata && su.matched_failure_strata.length > 0 && (
          <div style={{ marginBottom: '14px' }}>
            <div className="section-title">Matched Failure Strata (Risk Indicator)</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
              {su.matched_failure_strata.map((s, i) => (
                <span
                  key={i}
                  className="mono"
                  style={{
                    background: '#450a0a',
                    border: '1px solid #7f1d1d',
                    color: '#fca5a5',
                    borderRadius: '4px',
                    padding: '3px 8px',
                    fontSize: '11px',
                  }}
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {su.reasons?.length > 0 && (
          <div>
            <div className="section-title">Decision Reasons</div>
            <ul style={{ listStyle: 'disc', paddingLeft: '20px', marginTop: '6px' }}>
              {su.reasons.map((r, i) => (
                <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Status reference */}
      <div className="card">
        <div style={{ fontWeight: 600, marginBottom: '12px' }}>Scale-Up Decision States Reference</div>
        {[
          { status: 'SCALE_ELIGIBLE', desc: 'Vendor meets all requirements for regional scale-up.' },
          { status: 'SCALE_REVIEW_REQUIRED', desc: 'Further review is required before scale-up can proceed.' },
          { status: 'DO_NOT_SCALE_YET', desc: 'Scale-up is not permitted at this time due to unresolved failure strata.' },
          { status: 'REVALIDATION_REQUIRED', desc: 'Evidence or artifacts must be re-validated before scale-up.' },
        ].map(({ status, desc }) => (
          <div key={status} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0', borderBottom: '1px solid #1e293b' }}>
            <StatusBadge status={status} />
            <span style={{ fontSize: '12px', color: '#94a3b8' }}>{desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricBox({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="metric-box">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${mono ? 'mono' : ''}`} style={{ fontSize: '13px', fontWeight: 600, marginTop: '4px' }}>{value}</div>
    </div>
  );
}
