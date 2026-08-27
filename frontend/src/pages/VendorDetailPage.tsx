import { Link, useParams } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { ArrowLeft, Target, CheckCircle, XCircle, Clock, ShieldAlert, AlertTriangle } from 'lucide-react';

export default function VendorDetailPage() {
  const { id: evalId, vendorId } = useParams<{ id: string; vendorId: string }>();
  const { data } = useDemoContext();

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load vendor details.</p>
      </div>
    );
  }

  const vendor = data.vendors?.find(v => v.vendor_id === vendorId);
  const procDecision = data.procurement?.[vendorId ?? ''] ?? null;
  const fm = data.failure_maps?.find(f => f.vendor_id === vendorId) ?? null;
  const diag = data.diagnostics?.find(d => d.vendor_id === vendorId) ?? null;

  if (!vendor) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Vendor "{vendorId}" not found in this evaluation.</p>
      </div>
    );
  }

  const finalDecision = procDecision?.decision ?? vendor.procurement_recommendation ?? 'PENDING';
  const isEligible = finalDecision === 'ELIGIBLE';

  const pipelineStages = [
    'Problem Statement', 'Outcome Contract', 'Pilot Twin', 'Test Matrix',
    'Golden Suite', 'Artifact Freeze', 'Vendor Evaluation', 'Evidence',
    'Confidence', 'Failure Cartography', 'Procurement Decision',
    'Vendor Response', 'Human Auth', 'Scale-Up Policy',
  ];

  return (
    <div className="page animate-in">
      <Link
        to={`/evaluation/${evalId}/vendors`}
        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '13px', fontWeight: 500, color: 'var(--text-muted)', marginBottom: '24px' }}
      >
        <ArrowLeft size={14} /> Back to Vendors
      </Link>

      {/* Hero Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div className="font-label" style={{ marginBottom: '6px' }}>VENDOR EVALUATION · {evalId}</div>
          <h1 className="font-display">{vendor.display_name ?? vendor.vendor_id}</h1>
          <div className="font-mono" style={{ marginTop: '6px', color: 'var(--text-secondary)' }}>{vendor.vendor_id}</div>
          {vendor.description && (
            <p className="font-body" style={{ marginTop: '8px', color: 'var(--text-muted)', maxWidth: '500px' }}>{vendor.description}</p>
          )}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
          <div className="font-label">PROCUREMENT DECISION</div>
          <StatusBadge status={finalDecision} />
        </div>
      </div>

      {/* 14-Stage Pipeline Progress */}
      <div className="card" style={{ marginBottom: '24px', overflowX: 'auto' }}>
        <div className="font-label" style={{ marginBottom: '16px' }}>14-Stage Governance Pipeline</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0', minWidth: 'max-content', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '13px', left: '14px', right: '14px', height: '2px', background: 'var(--border-subtle)' }} />
          {pipelineStages.map((stage, i) => {
            const isAuth = i === 12; // human auth pending
            return (
              <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '80px', flexShrink: 0, position: 'relative', zIndex: 1 }}>
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: isAuth ? 'var(--surface)' : 'var(--text)',
                  border: isAuth ? '2px solid var(--border-strong)' : 'none',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {isAuth
                    ? <Clock size={14} color="var(--text-muted)" />
                    : <CheckCircle size={14} color="white" />
                  }
                </div>
                <div style={{ fontSize: '9px', fontWeight: 600, textAlign: 'center', marginTop: '6px', color: isAuth ? 'var(--text-muted)' : 'var(--text)', textTransform: 'uppercase', letterSpacing: '0.03em', lineHeight: 1.2 }}>
                  {stage}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Performance Metrics */}
        <div className="card">
          <div className="card-header"><span style={{ fontWeight: 600 }}>Evaluation Metrics</span></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="metric">
              <span className="metric-label">Accuracy</span>
              <span className="metric-value font-number" style={{ color: (vendor.accuracy ?? 0) < 80 ? 'var(--critical)' : 'var(--eligible)' }}>
                {vendor.accuracy?.toFixed(2) ?? '—'}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">Latency</span>
              <span className="metric-value font-number">{vendor.latency?.toFixed(0) ?? '—'}<span style={{ fontSize: '14px', fontWeight: 400, color: 'var(--text-muted)' }}> ms</span></span>
            </div>
            <div className="metric">
              <span className="metric-label">Confidence</span>
              <span className="metric-value font-number">{vendor.evidence_confidence?.toFixed(1) ?? '—'}%</span>
            </div>
            <div className="metric">
              <span className="metric-label">Errors</span>
              <span className="metric-value font-number">{vendor.error_count ?? '—'}</span>
            </div>
          </div>
        </div>

        {/* Evidence Details */}
        <div className="card">
          <div className="card-header"><span style={{ fontWeight: 600 }}>Evidence</span></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="metric">
              <span className="metric-label">Level</span>
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text)', marginTop: '4px' }}>{vendor.evidence_level ?? '—'}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Validation</span>
              <div style={{ marginTop: '4px' }}><StatusBadge status="VERIFIED" /></div>
            </div>
            <div className="metric" style={{ gridColumn: 'span 2' }}>
              <span className="metric-label">Failure Cartography Status</span>
              <div style={{ marginTop: '4px' }}><StatusBadge status={fm?.overall_status ?? 'NORMAL'} dot /></div>
            </div>
          </div>
        </div>
      </div>

      {/* Failure Hotspots */}
      {fm && fm.hotspots.length > 0 && (
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Target size={16} /> Failure Hotspots
            </span>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>
              <span style={{ color: 'var(--critical)', fontWeight: 700 }}>{fm.critical_hotspots_count ?? 0} critical</span>
              · {fm.degraded_hotspots_count ?? 0} degraded · {fm.watch_hotspots_count ?? 0} watch
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '10px' }}>
            {fm.hotspots.slice(0, 12).map((hs, i) => (
              <div key={i} style={{
                background: hs.severity === 'CRITICAL' ? 'var(--critical-bg)' : hs.severity === 'DEGRADED' ? 'var(--degraded-bg)' : 'var(--watch-bg)',
                border: `1px solid ${hs.severity === 'CRITICAL' ? 'var(--critical-border)' : hs.severity === 'DEGRADED' ? 'var(--degraded-border)' : 'var(--watch-border)'}`,
                borderRadius: '8px',
                padding: '10px',
              }}>
                <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text)', marginBottom: '2px' }}>
                  {hs.accuracy.toFixed(1)}%
                </div>
                <div style={{ fontSize: '10px', fontWeight: 650, color: hs.severity === 'CRITICAL' ? 'var(--critical)' : hs.severity === 'DEGRADED' ? 'var(--degraded)' : 'var(--watch)', marginBottom: '4px' }}>
                  {hs.severity}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                  {hs.stratum_id.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Procurement Gate Summary */}
      <div className="card" style={{ borderColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)', background: isEligible ? 'var(--eligible-bg)' : 'var(--critical-bg)', marginBottom: '24px' }}>
        <div className="card-header" style={{ borderBottomColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)' }}>
          <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', color: isEligible ? 'var(--eligible)' : 'var(--critical)' }}>
            <ShieldAlert size={16} /> Procurement Gate
          </span>
          <StatusBadge status={finalDecision} />
        </div>
        {procDecision?.reasons && procDecision.reasons.length > 0 && (
          <div>
            <div className="font-label" style={{ marginBottom: '8px' }}>Decision Reasons</div>
            <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {procDecision.reasons.map((r, i) => (
                <li key={i} className="font-body" style={{ color: 'var(--text-secondary)' }}>{String(r)}</li>
              ))}
            </ul>
          </div>
        )}
        {procDecision?.gates && (
          <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
            {procDecision.gates.map((g, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--surface)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>{String(g.gate)}</span>
                {g.passed ? <CheckCircle size={16} color="var(--eligible)" /> : <XCircle size={16} color="var(--critical)" />}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Diagnostic Summary */}
      {diag?.overall_verdict_explanation && (
        <div className="card" style={{ borderColor: 'var(--advisory-border)', background: 'var(--advisory-bg)' }}>
          <div className="card-header" style={{ borderBottomColor: 'var(--advisory-border)' }}>
            <span style={{ fontWeight: 600, color: 'var(--advisory)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={16} /> Advisory Diagnostic Intelligence
            </span>
            <StatusBadge status={diag.analysis_mode} />
          </div>
          <div className="alert alert-advisory">
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <strong>AI advisory only. Does not affect the deterministic gate outcome.</strong>
          </div>
          <p className="font-body" style={{ color: 'var(--text-secondary)', marginTop: '12px' }}>
            {diag.overall_verdict_explanation}
          </p>
        </div>
      )}
    </div>
  );
}
