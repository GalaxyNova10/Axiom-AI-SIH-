// ============================================================
// Vendors Page — all scorecards
// ============================================================

import { useNavigate } from 'react-router-dom';
import { Users, ChevronRight, TrendingDown } from 'lucide-react';
import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import type { VendorScorecard, FailureHotspot } from '../types/api';

export default function VendorsPage() {
  const { data } = useDemoContext();
  const navigate = useNavigate();
  const evalId = data?.vendors?.[0]?.evaluation_id;

  if (!data) {
    return (
      <div style={{ padding: '28px' }}>
        <EmptyState message="Run the canonical demo from the Dashboard to load vendor scorecards." />
      </div>
    );
  }

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1200px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>Vendor Scorecards</h1>
        <p style={{ color: '#94a3b8', fontSize: '13px' }}>
          Evidence-validated performance metrics from independent evaluation. Backend is the source of truth.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {data.vendors.map((v) => (
          <VendorCard
            key={v.vendor_id}
            vendor={v}
            onInspect={() => evalId && navigate(`/evaluation/${evalId}/vendors/${v.vendor_id}`)}
          />
        ))}
      </div>

      {/* Advisory disclaimer */}
      <div className="alert alert-info" style={{ marginTop: '24px' }}>
        <Users size={14} />
        <span>
          Vendor scorecards reflect independently validated evidence. Diagnostic summaries are advisory intelligence only — they do not alter procurement decisions.
        </span>
      </div>
    </div>
  );
}

function VendorCard({ vendor, onInspect }: { vendor: VendorScorecard; onInspect: () => void }) {
  const isEligible = vendor.procurement_recommendation === 'ELIGIBLE';
  const borderColor = isEligible ? '#16a34a' : '#dc2626';

  return (
    <article
      className="card"
      style={{ borderColor, cursor: 'pointer', transition: 'all 0.2s ease' }}
      onClick={onInspect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onInspect()}
      aria-label={`Inspect ${vendor.display_name ?? vendor.vendor_id} scorecard`}
      onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)'; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.transform = 'translateY(0)'; }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: '16px', color: '#f1f5f9' }}>
            {vendor.display_name ?? vendor.vendor_id}
          </div>
          <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
            {vendor.vendor_id}
            {vendor.description && ` · ${vendor.description}`}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
          <StatusBadge status={vendor.procurement_recommendation} />
          <StatusBadge status={vendor.overall_status ?? 'NORMAL'} dot />
        </div>
      </div>

      {/* Metrics grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '14px' }}>
        <Metric label="Accuracy" value={vendor.accuracy != null ? `${vendor.accuracy.toFixed(2)}%` : '—'} highlight={vendor.accuracy != null && vendor.accuracy >= 80} />
        <Metric label="Latency (ms)" value={vendor.latency != null ? vendor.latency.toFixed(1) : '—'} />
        <Metric label="Error Count" value={vendor.error_count?.toString() ?? '—'} />
        <Metric label="Evidence Confidence" value={vendor.evidence_confidence != null ? `${vendor.evidence_confidence.toFixed(1)}%` : '—'} highlight={vendor.evidence_confidence != null && vendor.evidence_confidence >= 70} />
      </div>

      {/* Evidence level */}
      {vendor.evidence_level && (
        <div style={{ marginBottom: '12px', fontSize: '12px', color: '#94a3b8' }}>
          <span style={{ color: '#64748b' }}>Evidence Level: </span>
          <strong style={{ color: '#93c5fd' }}>{vendor.evidence_level}</strong>
        </div>
      )}

      {/* Top hotspot */}
      {(vendor.top_failure_hotspot ?? vendor.failure_hotspots?.[0]) && (
        <TopHotspot hotspot={vendor.top_failure_hotspot ?? vendor.failure_hotspots[0]} />
      )}

      {/* Diagnostic summary */}
      {vendor.diagnostic_summary && (
        <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '6px', padding: '10px', marginTop: '10px' }}>
          <div style={{ fontSize: '10px', color: '#7c3aed', fontWeight: 600, letterSpacing: '0.05em', marginBottom: '4px' }}>
            ADVISORY DIAGNOSTIC — does not authorize procurement
          </div>
          <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5 }}>
            {vendor.diagnostic_summary.slice(0, 200)}{vendor.diagnostic_summary.length > 200 ? '…' : ''}
          </p>
        </div>
      )}

      {/* Inspect button */}
      <div style={{ marginTop: '14px', display: 'flex', justifyContent: 'flex-end' }}>
        <button className="btn btn-ghost btn-sm" tabIndex={-1} aria-hidden="true">
          Inspect Detail <ChevronRight size={13} />
        </button>
      </div>
    </article>
  );
}

function Metric({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="metric-box">
      <div className="metric-label">{label}</div>
      <div style={{ fontWeight: 600, color: highlight ? '#4ade80' : '#e2e8f0', fontSize: '15px', marginTop: '2px' }}>
        {value}
      </div>
    </div>
  );
}

function TopHotspot({ hotspot }: { hotspot: FailureHotspot }) {
  return (
    <div
      style={{
        background: '#450a0a22',
        border: '1px solid #7f1d1d',
        borderRadius: '6px',
        padding: '8px 10px',
        marginTop: '8px',
      }}
    >
      <div style={{ fontSize: '10px', color: '#f87171', fontWeight: 600, letterSpacing: '0.05em', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
        <TrendingDown size={10} />
        TOP FAILURE HOTSPOT
      </div>
      <div style={{ fontSize: '11px', color: '#fca5a5', fontFamily: 'monospace' }}>{hotspot.stratum_id}</div>
      <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
        Accuracy: {hotspot.accuracy?.toFixed(1)}% · <StatusBadge status={hotspot.severity} />
      </div>
      {hotspot.reason && (
        <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{hotspot.reason}</div>
      )}
    </div>
  );
}
