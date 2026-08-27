// ============================================================
// Failure Cartography Page
// ============================================================

import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { Map, AlertTriangle } from 'lucide-react';
import type { VendorFailureMap, FailureHotspot } from '../types/api';

const SEVERITY_ORDER = ['CRITICAL', 'DEGRADED', 'WATCH', 'NORMAL'];
const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#dc2626',
  DEGRADED: '#ea580c',
  WATCH: '#d97706',
  NORMAL: '#16a34a',
};

function severityBg(sev: string): string {
  const c: Record<string, string> = {
    CRITICAL: '#450a0a',
    DEGRADED: '#431407',
    WATCH: '#451a03',
    NORMAL: '#14532d',
  };
  return c[sev] ?? '#1e293b';
}

function sortedHotspots(hotspots: FailureHotspot[]): FailureHotspot[] {
  return [...hotspots].sort(
    (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity),
  );
}

export default function FailureMapPage() {
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to load Failure Cartography." /></div>;

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1200px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Map size={20} color="#3b82f6" />
          Failure Cartography
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          Sanitized multi-stratum failure map. Shows deployment strata where vendors degrade or fail under realistic rural conditions.
          Private seeds and internal parameters are never exposed.
        </p>
      </div>

      <div className="alert alert-info" style={{ marginBottom: '20px' }}>
        <AlertTriangle size={14} />
        <span>
          Failure Cartography maps observable stratum-level performance. It uses only public/sanitized information — stratum ID, accuracy, severity, and failure reason.
          No private parameters, seeds, or internal evaluator details are shown.
        </span>
      </div>

      {/* Summary row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {data.failure_maps?.map((fm: VendorFailureMap) => (
          <SummaryCard key={fm.vendor_id} fm={fm} />
        ))}
      </div>

      {/* Heatmap per vendor */}
      {data.failure_maps?.map((fm: VendorFailureMap) => (
        <div key={fm.vendor_id} className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600 }}>
              {fm.display_name ?? fm.vendor_id} — Failure Heatmap
            </span>
            <div style={{ display: 'flex', gap: '8px' }}>
              <StatusBadge status={fm.overall_status} dot />
              {fm.overall_accuracy != null && (
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>Overall: {fm.overall_accuracy.toFixed(1)}%</span>
              )}
            </div>
          </div>

          {fm.hotspots.length === 0 ? (
            <p style={{ color: '#64748b', fontSize: '13px' }}>No failure hotspots detected.</p>
          ) : (
            <>
              {/* Grid heatmap */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
                {sortedHotspots(fm.hotspots).map((h) => (
                  <HotspotCell key={h.stratum_id} hotspot={h} />
                ))}
              </div>

              {/* Detail table */}
              <div style={{ overflowX: 'auto' }}>
                <table className="axiom-table" aria-label={`Failure hotspot details for ${fm.display_name ?? fm.vendor_id}`}>
                  <thead>
                    <tr>
                      <th>Stratum</th>
                      <th>Severity</th>
                      <th>Accuracy</th>
                      <th>Failure Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedHotspots(fm.hotspots).map((h) => (
                      <tr key={h.stratum_id}>
                        <td className="mono" style={{ fontSize: '11px', maxWidth: '200px', wordBreak: 'break-all' }}>{h.stratum_id}</td>
                        <td><StatusBadge status={h.severity} /></td>
                        <td>
                          <span style={{ fontWeight: 600, color: SEVERITY_COLORS[h.severity] ?? '#e2e8f0' }}>
                            {h.accuracy?.toFixed(1)}%
                          </span>
                        </td>
                        <td style={{ color: '#94a3b8', fontSize: '12px', maxWidth: '300px' }}>{h.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}

function SummaryCard({ fm }: { fm: VendorFailureMap }) {
  return (
    <div className="card">
      <div className="card-header" style={{ marginBottom: '12px', paddingBottom: '8px' }}>
        <span style={{ fontWeight: 600, fontSize: '14px' }}>{fm.display_name ?? fm.vendor_id}</span>
        <StatusBadge status={fm.overall_status} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <MiniMetric label="Total Strata" value={fm.total_strata?.toString() ?? '—'} />
        <MiniMetric label="Overall Accuracy" value={fm.overall_accuracy != null ? `${fm.overall_accuracy.toFixed(1)}%` : '—'} />
        <MiniMetric label="🔴 Critical" value={fm.critical_hotspots_count?.toString() ?? '0'} color="#f87171" />
        <MiniMetric label="🟠 Degraded" value={fm.degraded_hotspots_count?.toString() ?? '0'} color="#fb923c" />
        <MiniMetric label="🟡 Watch" value={fm.watch_hotspots_count?.toString() ?? '0'} color="#fbbf24" />
      </div>
    </div>
  );
}

function MiniMetric({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="metric-box" style={{ padding: '8px 10px' }}>
      <div className="metric-label" style={{ fontSize: '10px' }}>{label}</div>
      <div style={{ fontWeight: 700, color: color ?? '#e2e8f0', fontSize: '14px', marginTop: '2px' }}>{value}</div>
    </div>
  );
}

function HotspotCell({ hotspot }: { hotspot: FailureHotspot }) {
  const bg = severityBg(hotspot.severity);
  const col = SEVERITY_COLORS[hotspot.severity] ?? '#e2e8f0';
  const short = hotspot.stratum_id.replace(/_/g, '\n').slice(0, 30);

  return (
    <div
      title={`${hotspot.stratum_id}\nAccuracy: ${hotspot.accuracy?.toFixed(1)}%\n${hotspot.reason}`}
      aria-label={`${hotspot.stratum_id}: ${hotspot.severity}, ${hotspot.accuracy?.toFixed(1)}% accuracy`}
      style={{
        background: bg,
        border: `1px solid ${col}44`,
        borderRadius: '6px',
        padding: '6px 8px',
        fontSize: '10px',
        color: col,
        fontFamily: 'monospace',
        lineHeight: 1.3,
        whiteSpace: 'pre-wrap',
        minWidth: '100px',
        maxWidth: '140px',
        cursor: 'default',
      }}
    >
      {short}
      <div style={{ fontWeight: 700, marginTop: '4px' }}>{hotspot.accuracy?.toFixed(1)}%</div>
    </div>
  );
}
