import { useNavigate } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { ChevronRight, BarChart2, AlertTriangle } from 'lucide-react';

export default function VendorsPage() {
  const { data } = useDemoContext();
  const navigate = useNavigate();
  const evalId = data?.vendors?.[0]?.evaluation_id ?? 'demo';

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <BarChart2 size={32} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          <p className="font-subheading">Run the canonical demo from Overview to load vendor scorecards.</p>
        </div>
      </div>
    );
  }

  const vendors = data.vendors ?? [];
  const procurement = data.procurement ?? {};
  const failureMaps = data.failure_maps ?? [];

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>COMPARISON VIEW</div>
        <h1 className="font-display">Vendor Scorecards</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Evidence-validated performance across all 24 deployment strata. Backend is source of truth.
        </p>
      </div>

      {/* Comparison Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: '32px' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="ax-table">
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Accuracy</th>
                <th>Latency (ms)</th>
                <th>Evidence Level</th>
                <th>Confidence</th>
                <th>Failure Status</th>
                <th>Critical Hotspots</th>
                <th>Decision</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {vendors.map(v => {
                const procDecision = procurement[v.vendor_id]?.decision ?? v.procurement_recommendation ?? 'PENDING';
                const fm = failureMaps.find(f => f.vendor_id === v.vendor_id);
                return (
                  <tr
                    key={v.vendor_id}
                    onClick={() => navigate(`/evaluation/${evalId}/vendors/${v.vendor_id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <div style={{ fontWeight: 600, fontSize: '14px' }}>{v.display_name ?? v.vendor_id}</div>
                      <div className="font-caption" style={{ marginTop: '2px' }}>{v.vendor_id}</div>
                    </td>
                    <td>
                      <span className="font-number" style={{ fontWeight: 700, color: (v.accuracy ?? 0) < 80 ? 'var(--critical)' : 'var(--text)' }}>
                        {v.accuracy != null ? `${v.accuracy.toFixed(2)}%` : '—'}
                      </span>
                    </td>
                    <td className="font-number">{v.latency != null ? v.latency.toFixed(1) : '—'}</td>
                    <td>
                      <span className="font-caption" style={{ fontWeight: 500 }}>{v.evidence_level ?? '—'}</span>
                    </td>
                    <td className="font-number">{v.evidence_confidence != null ? `${v.evidence_confidence.toFixed(1)}%` : '—'}</td>
                    <td><StatusBadge status={fm?.overall_status ?? v.overall_status ?? 'NORMAL'} dot /></td>
                    <td>
                      <span style={{ fontWeight: 700, color: (fm?.critical_hotspots_count ?? 0) > 0 ? 'var(--critical)' : 'var(--text)' }} className="font-number">
                        {fm?.critical_hotspots_count ?? 0}
                      </span>
                    </td>
                    <td><StatusBadge status={procDecision} /></td>
                    <td style={{ color: 'var(--text-faint)' }}><ChevronRight size={16} /></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual interpretation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={16} /> Accuracy vs. Deployment Risk
            </span>
          </div>
          {/* Conceptual scatter chart */}
          <div style={{ position: 'relative', height: '200px', borderLeft: '2px solid var(--border)', borderBottom: '2px solid var(--border)', margin: '16px 40px 32px 16px' }}>
            <div style={{ position: 'absolute', bottom: '-24px', left: '50%', transform: 'translateX(-50%)', fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>OVERALL ACCURACY →</div>
            <div style={{ position: 'absolute', left: '-40px', top: '50%', transform: 'translateY(-50%) rotate(-90deg)', fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, whiteSpace: 'nowrap' }}>DEPLOYMENT RISK ↑</div>
            {[
              { label: 'KrishiLink', x: 85, y: 20, color: 'var(--critical)' },
              { label: 'RuralFlow', x: 60, y: 75, color: 'var(--eligible)' },
              { label: 'AgriRoute', x: 20, y: 30, color: 'var(--critical)' },
            ].map(p => (
              <div key={p.label} style={{ position: 'absolute', left: `${p.x}%`, top: `${p.y}%`, transform: 'translate(-50%, -50%)' }}>
                <div style={{ width: '14px', height: '14px', borderRadius: '50%', background: p.color, border: '2px solid white', boxShadow: '0 1px 4px rgba(0,0,0,0.2)' }} />
                <div style={{ position: 'absolute', top: '16px', left: '50%', transform: 'translateX(-50%)', fontSize: '10px', fontWeight: 600, whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>{p.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card" style={{ background: 'var(--surface-muted)' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <AlertTriangle size={20} color="var(--watch)" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '8px' }}>Why accuracy alone is insufficient</h3>
              <p className="font-body" style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>
                KrishiLink Technologies achieves the highest aggregate score but is <strong>REJECTED</strong> by the deterministic procurement engine.
              </p>
              <p className="font-body" style={{ color: 'var(--text-secondary)' }}>
                The failure cartography reveals catastrophic localized breakdown under compound rural conditions — a risk that aggregate benchmarks completely conceal.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
