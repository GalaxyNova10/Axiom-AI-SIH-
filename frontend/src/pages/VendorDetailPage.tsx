// ============================================================
// Vendor Detail Page
// ============================================================

import { useParams } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { ShieldCheck, Brain, AlertCircle } from 'lucide-react';
import type { FailureHotspot } from '../types/api';

export default function VendorDetailPage() {
  const { vendorId } = useParams<{ vendorId: string }>();
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState /></div>;

  const vendor = data.vendors.find((v) => v.vendor_id === vendorId);
  const failureMap = data.failure_maps?.find((f) => f.vendor_id === vendorId);
  const diagnostic = data.diagnostics?.find((d) => d.vendor_id === vendorId);
  const procurement = data.procurement?.[vendorId ?? ''];

  if (!vendor) return <div style={{ padding: '28px' }}><EmptyState title="Vendor not found" /></div>;

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1100px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 700 }}>{vendor.display_name ?? vendorId}</h1>
            <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
              Vendor ID: <span className="mono">{vendorId}</span>
              {vendor.evaluation_id && <> · Evaluation: <span className="mono">{vendor.evaluation_id}</span></>}
            </div>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <StatusBadge status={vendor.procurement_recommendation} />
            <StatusBadge status={vendor.overall_status ?? 'NORMAL'} dot />
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '20px' }}>
        {[
          { label: 'Accuracy', value: vendor.accuracy != null ? `${vendor.accuracy.toFixed(2)}%` : '—' },
          { label: 'Avg Latency (ms)', value: vendor.latency != null ? vendor.latency.toFixed(1) : '—' },
          { label: 'Error Count', value: vendor.error_count?.toString() ?? '—' },
          { label: 'Evidence Confidence', value: vendor.evidence_confidence != null ? `${vendor.evidence_confidence.toFixed(1)}%` : '—' },
          { label: 'Evidence Level', value: vendor.evidence_level ?? '—' },
        ].map(({ label, value }) => (
          <div key={label} className="metric-box">
            <div className="metric-label">{label}</div>
            <div style={{ fontWeight: 700, fontSize: '16px', color: '#f1f5f9', marginTop: '4px' }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Evidence provenance */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-header">
          <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={16} color="#16a34a" />
            Evidence Provenance
          </span>
        </div>
        <div className="alert alert-info" style={{ marginBottom: '12px' }}>
          <AlertCircle size={14} />
          <span>
            <strong>INDEPENDENTLY_VALIDATED</strong> evidence is generated through independent black-box evaluation against the Government Pilot Twin, with cryptographic artifact integrity.
            Evidence labeled <strong>OBSERVED / DECLARED / ESTIMATED</strong> reflects Pilot Twin parameter sourcing only — not the evaluation outcome.
          </span>
        </div>
        {data.pilot_twin?.parameters?.map((p) => (
          <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #1e293b', fontSize: '13px' }}>
            <span style={{ color: '#94a3b8', textTransform: 'capitalize' }}>{p.name}</span>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span className="mono" style={{ color: '#f1f5f9' }}>{p.value}</span>
              <StatusBadge status={p.evidence_level} />
              <span style={{ color: '#64748b', fontSize: '11px' }}>Source: {p.source}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Failure hotspots */}
      {failureMap && failureMap.hotspots.length > 0 && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600 }}>Failure Hotspots ({failureMap.hotspots.length})</span>
            <span style={{ display: 'flex', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#f87171' }}>CRITICAL: {failureMap.critical_hotspots_count}</span>
              <span style={{ fontSize: '12px', color: '#fb923c' }}>DEGRADED: {failureMap.degraded_hotspots_count}</span>
              <span style={{ fontSize: '12px', color: '#fbbf24' }}>WATCH: {failureMap.watch_hotspots_count}</span>
            </span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="axiom-table" aria-label={`Failure hotspots for ${vendorId}`}>
              <thead>
                <tr>
                  <th>Stratum ID</th>
                  <th>Severity</th>
                  <th>Accuracy</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {failureMap.hotspots.map((h: FailureHotspot) => (
                  <tr key={h.stratum_id}>
                    <td className="mono" style={{ fontSize: '12px' }}>{h.stratum_id}</td>
                    <td><StatusBadge status={h.severity} /></td>
                    <td style={{ fontWeight: 600, color: h.accuracy < 50 ? '#f87171' : h.accuracy < 80 ? '#fbbf24' : '#4ade80' }}>
                      {h.accuracy?.toFixed(1)}%
                    </td>
                    <td style={{ color: '#94a3b8', fontSize: '12px' }}>{h.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Procurement detail */}
      {procurement && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={16} color="#3b82f6" />
              Deterministic Procurement Gate
            </span>
            <StatusBadge status={procurement.decision} />
          </div>
          <div className="alert alert-info" style={{ marginBottom: '12px' }}>
            <AlertCircle size={14} />
            <span>These results are produced by the deterministic backend decision engine. The frontend does not calculate eligibility.</span>
          </div>
          <div style={{ marginBottom: '12px' }}>
            <div className="section-title">Gate Results</div>
            {procurement.gates?.map((g, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: '1px solid #1e293b', fontSize: '13px' }}>
                <span style={{ color: '#94a3b8' }}>{g.gate}</span>
                <StatusBadge status={g.passed ? 'ELIGIBLE' : 'REJECTED'} />
              </div>
            ))}
          </div>
          {procurement.reasons?.length > 0 && (
            <div>
              <div className="section-title">Reasons</div>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px' }}>
                {procurement.reasons.map((r, i) => (
                  <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Diagnostics */}
      {diagnostic && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Brain size={16} color="#7c3aed" />
              Advisory Diagnostic Intelligence
            </span>
            <StatusBadge status={diagnostic.analysis_mode} />
          </div>
          <div className="alert alert-advisory" style={{ marginBottom: '12px', background: '#2d1b6922', border: '1px solid #7c3aed', color: '#c4b5fd' }}>
            <AlertCircle size={14} />
            <span>Advisory analysis — does not authorize procurement. Diagnostic output is qualitative interpretation only.</span>
          </div>

          <div style={{ marginBottom: '12px' }}>
            <div className="section-title">Overall Verdict</div>
            <p style={{ color: '#94a3b8', fontSize: '13px', lineHeight: 1.6 }}>{diagnostic.overall_verdict_explanation}</p>
          </div>

          {diagnostic.operational_risk_summary && (
            <div style={{ marginBottom: '12px' }}>
              <div className="section-title">Operational Risk</div>
              <p style={{ color: '#94a3b8', fontSize: '13px', lineHeight: 1.6 }}>{diagnostic.operational_risk_summary}</p>
            </div>
          )}

          {diagnostic.recommended_vendor_challenges?.length > 0 && (
            <div style={{ marginBottom: '12px' }}>
              <div className="section-title">Recommended Vendor Challenges</div>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px' }}>
                {diagnostic.recommended_vendor_challenges.map((c, i) => (
                  <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {diagnostic.targeted_retest_recommendations?.length > 0 && (
            <div>
              <div className="section-title">Targeted Retest Recommendations</div>
              <ul style={{ listStyle: 'disc', paddingLeft: '20px' }}>
                {diagnostic.targeted_retest_recommendations.map((r, i) => (
                  <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
