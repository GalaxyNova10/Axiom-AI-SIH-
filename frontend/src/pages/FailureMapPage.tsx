import { useState } from 'react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { Map } from 'lucide-react';
import type { FailureHotspot } from '../types/api';

export default function FailureMapPage() {
  const { data } = useDemoContext();
  const [selectedVendor, setSelectedVendor] = useState<string>('');
  const [selectedHotspot, setSelectedHotspot] = useState<FailureHotspot | null>(null);

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load failure cartography.</p>
      </div>
    );
  }

  const vendors = data.vendors ?? [];
  const failureMaps = data.failure_maps ?? [];
  const activeVendorId = selectedVendor || vendors[0]?.vendor_id || '';
  const currentMap = failureMaps.find(f => f.vendor_id === activeVendorId);
  const hotspots = currentMap?.hotspots ?? [];

  const getSeverityBg = (sev: string) => {
    if (sev === 'CRITICAL') return 'var(--critical-bg)';
    if (sev === 'DEGRADED') return 'var(--degraded-bg)';
    if (sev === 'WATCH') return 'var(--watch-bg)';
    return 'var(--surface)';
  };
  const getSeverityBorder = (sev: string) => {
    if (sev === 'CRITICAL') return 'var(--critical-border)';
    if (sev === 'DEGRADED') return 'var(--degraded-border)';
    if (sev === 'WATCH') return 'var(--watch-border)';
    return 'var(--border-subtle)';
  };
  const getSeverityColor = (sev: string) => {
    if (sev === 'CRITICAL') return 'var(--critical)';
    if (sev === 'DEGRADED') return 'var(--degraded)';
    if (sev === 'WATCH') return 'var(--watch)';
    return 'var(--eligible)';
  };

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>CARTOGRAPHY</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Map size={28} color="var(--accent)" /> Failure Cartography
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Where does the system break? Performance heatmap across all 24 deployment strata.
        </p>
      </div>

      {/* Vendor Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {vendors.map(v => (
          <button
            key={v.vendor_id}
            className={`btn ${(activeVendorId === v.vendor_id) ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { setSelectedVendor(v.vendor_id); setSelectedHotspot(null); }}
          >
            {v.display_name ?? v.vendor_id}
          </button>
        ))}
      </div>

      {/* Summary Strip */}
      {currentMap && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '24px' }}>
          <div className="card" style={{ padding: '14px' }}>
            <div className="metric metric-sm">
              <span className="metric-label">Overall Accuracy</span>
              <span className="metric-value font-number">{currentMap.overall_accuracy?.toFixed(1) ?? '—'}%</span>
            </div>
          </div>
          <div className="card" style={{ padding: '14px', borderColor: 'var(--critical-border)' }}>
            <div className="metric metric-sm">
              <span className="metric-label" style={{ color: 'var(--critical)' }}>Critical</span>
              <span className="metric-value font-number" style={{ color: 'var(--critical)' }}>{currentMap.critical_hotspots_count ?? 0}</span>
            </div>
          </div>
          <div className="card" style={{ padding: '14px', borderColor: 'var(--degraded-border)' }}>
            <div className="metric metric-sm">
              <span className="metric-label" style={{ color: 'var(--degraded)' }}>Degraded</span>
              <span className="metric-value font-number" style={{ color: 'var(--degraded)' }}>{currentMap.degraded_hotspots_count ?? 0}</span>
            </div>
          </div>
          <div className="card" style={{ padding: '14px', borderColor: 'var(--watch-border)' }}>
            <div className="metric metric-sm">
              <span className="metric-label" style={{ color: 'var(--watch)' }}>Watch</span>
              <span className="metric-value font-number" style={{ color: 'var(--watch)' }}>{currentMap.watch_hotspots_count ?? 0}</span>
            </div>
          </div>
          <div className="card" style={{ padding: '14px' }}>
            <div className="metric metric-sm">
              <span className="metric-label">Status</span>
              <div style={{ marginTop: '4px' }}><StatusBadge status={currentMap.overall_status} /></div>
            </div>
          </div>
        </div>
      )}

      {/* Heatmap Grid */}
      {hotspots.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
          No failure hotspots found for this vendor.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '8px' }}>
          {hotspots.map((hs, i) => (
            <div
              key={i}
              className="stagger"
              style={{
                background: getSeverityBg(hs.severity),
                border: `1px solid ${getSeverityBorder(hs.severity)}`,
                borderLeft: `4px solid ${getSeverityColor(hs.severity)}`,
                borderRadius: '8px',
                padding: '10px 10px 10px 12px',
                cursor: 'pointer',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                animationDelay: `${i * 20}ms`,
              }}
              onClick={() => setSelectedHotspot(hs)}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'none'; }}
            >
              <div style={{ fontWeight: 800, fontSize: '18px', color: 'var(--text)', letterSpacing: '-0.02em', marginBottom: '2px' }}>
                {hs.accuracy.toFixed(1)}%
              </div>
              <div style={{ fontSize: '10px', fontWeight: 700, color: getSeverityColor(hs.severity), marginBottom: '6px', textTransform: 'uppercase' }}>
                {hs.severity}
              </div>
              <div style={{ fontSize: '9.5px', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                {hs.stratum_id.replace(/_/g, ' ').toLowerCase()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Hotspot Detail Drawer */}
      {selectedHotspot && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.2)', zIndex: 98, backdropFilter: 'blur(2px)' }}
            onClick={() => setSelectedHotspot(null)}
          />
          <div style={{
            position: 'fixed', top: 0, right: 0, bottom: 0, width: '380px', maxWidth: '100vw',
            background: 'var(--surface)', borderLeft: '1px solid var(--border)',
            boxShadow: 'var(--shadow-lg)', zIndex: 99, padding: '32px 24px',
            overflowY: 'auto', animation: 'fadeIn 0.2s ease'
          }}>
            <button className="btn btn-ghost btn-sm" style={{ position: 'absolute', top: '16px', right: '16px' }} onClick={() => setSelectedHotspot(null)}>
              ✕ Close
            </button>
            <div className="font-label" style={{ marginBottom: '8px' }}>DEPLOYMENT CONDITION</div>
            <h2 className="font-mono" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text)', marginBottom: '24px', lineHeight: 1.5, wordBreak: 'break-word' }}>
              {selectedHotspot.stratum_id.replace(/_/g, ' + ')}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
              <div className="metric">
                <span className="metric-label">Accuracy</span>
                <span className="metric-value font-number" style={{ color: selectedHotspot.severity === 'CRITICAL' ? 'var(--critical)' : 'var(--text)' }}>
                  {selectedHotspot.accuracy.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Severity</span>
                <div style={{ marginTop: '4px' }}><StatusBadge status={selectedHotspot.severity} /></div>
              </div>
              {selectedHotspot.failure_rate != null && (
                <div className="metric">
                  <span className="metric-label">Failure Rate</span>
                  <span className="metric-value font-number">{(selectedHotspot.failure_rate * 100).toFixed(1)}%</span>
                </div>
              )}
              {selectedHotspot.confidence != null && (
                <div className="metric">
                  <span className="metric-label">Confidence</span>
                  <span className="metric-value font-number">{selectedHotspot.confidence.toFixed(1)}%</span>
                </div>
              )}
            </div>
            {selectedHotspot.reason && (
              <div style={{ background: 'var(--surface-muted)', padding: '16px', borderRadius: '8px' }}>
                <div className="font-label" style={{ marginBottom: '6px' }}>Reason</div>
                <p className="font-body" style={{ color: 'var(--text-secondary)' }}>{selectedHotspot.reason}</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
