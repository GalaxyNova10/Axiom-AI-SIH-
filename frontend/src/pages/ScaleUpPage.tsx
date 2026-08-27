import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { TrendingUp, MapPin, AlertOctagon, CheckCircle } from 'lucide-react';

export default function ScaleUpPage() {
  const { data } = useDemoContext();

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load scale-up evaluations.</p>
      </div>
    );
  }

  const scaleUp = data.scale_up ?? {};
  const entries = Object.entries(scaleUp);

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>SCALE-UP POLICY</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <TrendingUp size={28} color="var(--accent)" /> Evidence-Gated Scale-Up
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          A successful pilot does not automatically authorize deployment into another district.
        </p>
      </div>

      {entries.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
          <TrendingUp size={32} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          <p className="font-subheading">No scale-up evaluation data returned by backend.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {entries.map(([key, evaluation]) => {
            const ev = evaluation as Record<string, any>;
            const decision = String(ev.decision ?? ev.scale_up_decision ?? ev.status ?? 'UNKNOWN');
            return (
              <div key={key} className="card animate-up">
                <div className="card-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <MapPin size={16} color="var(--accent)" />
                    <div>
                      <h2 style={{ fontSize: '16px', fontWeight: 700 }}>{String(ev.vendor_id ?? key)}</h2>
                      {ev.target_district && (
                        <div className="font-caption" style={{ marginTop: '2px' }}>
                          Target: <strong>{String(ev.target_district)}</strong>
                        </div>
                      )}
                    </div>
                  </div>
                  <StatusBadge status={decision} />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '16px' }}>
                  {ev.policy_case && (
                    <div className="metric">
                      <span className="metric-label">Policy Case</span>
                      <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text)', marginTop: '4px' }}>{String(ev.policy_case)}</span>
                    </div>
                  )}
                  {ev.scale_eligible != null && (
                    <div className="metric">
                      <span className="metric-label">Scale Eligible</span>
                      <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        {ev.scale_eligible
                          ? <CheckCircle size={18} color="var(--eligible)" />
                          : <AlertOctagon size={18} color="var(--critical)" />}
                        <span style={{ fontWeight: 600, color: ev.scale_eligible ? 'var(--eligible)' : 'var(--critical)' }}>
                          {ev.scale_eligible ? 'Yes' : 'No'}
                        </span>
                      </div>
                    </div>
                  )}
                  {ev.failure_map_status && (
                    <div className="metric">
                      <span className="metric-label">Failure Map Status</span>
                      <div style={{ marginTop: '4px' }}><StatusBadge status={String(ev.failure_map_status)} /></div>
                    </div>
                  )}
                </div>

                {/* Target Environment */}
                {ev.target_environment && typeof ev.target_environment === 'object' && (
                  <div style={{ background: 'var(--surface-muted)', padding: '14px', borderRadius: '8px', marginBottom: '16px' }}>
                    <div className="font-label" style={{ marginBottom: '10px' }}>Target Environment Dimensions</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '8px' }}>
                      {Object.entries(ev.target_environment as Record<string, any>).map(([k, v]) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--surface)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                          <span style={{ fontSize: '12px', fontWeight: 600, textTransform: 'capitalize', color: 'var(--text-secondary)' }}>{k}</span>
                          <span className="font-mono" style={{ fontSize: '11px', color: 'var(--text)' }}>{String(v)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Historical matched strata */}
                {ev.matched_failure_strata && Array.isArray(ev.matched_failure_strata) && ev.matched_failure_strata.length > 0 && (
                  <div style={{ background: 'var(--critical-bg)', border: '1px solid var(--critical-border)', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                    <div className="font-label" style={{ marginBottom: '8px', color: 'var(--critical)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertOctagon size={14} /> Matching Historical Failure Strata
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {(ev.matched_failure_strata as string[]).map((s, i) => (
                        <span key={i} className="font-mono" style={{ background: 'var(--surface)', border: '1px solid var(--critical-border)', borderRadius: '4px', padding: '3px 8px', fontSize: '11px', color: 'var(--critical)' }}>
                          {String(s).replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Reasons */}
                {ev.reasons && Array.isArray(ev.reasons) && ev.reasons.length > 0 && (
                  <div>
                    <div className="font-label" style={{ marginBottom: '8px' }}>Decision Reasons</div>
                    <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {(ev.reasons as any[]).map((r, i) => (
                        <li key={i} className="font-body" style={{ color: 'var(--text-secondary)' }}>{String(r)}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
