import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import AnimatedNumber from '../components/AnimatedNumber';
import HotspotTreemap from '../components/charts/HotspotTreemap';
import { Map, X, Cpu, AlertTriangle } from 'lucide-react';
import type { VendorScorecard, VendorFailureMap, FailureHotspot } from '../types/api';

const getSeverityColor = (s: string) => s === 'CRITICAL' ? 'var(--critical)' : s === 'DEGRADED' ? 'var(--degraded)' : s === 'WATCH' ? 'var(--watch)' : 'var(--eligible)';
const getSeverityBg = (s: string) => s === 'CRITICAL' ? 'var(--critical-bg)' : s === 'DEGRADED' ? 'var(--degraded-bg)' : s === 'WATCH' ? 'var(--watch-bg)' : 'var(--eligible-bg)';
const getSeverityBorder = (s: string) => s === 'CRITICAL' ? 'var(--critical-border)' : s === 'DEGRADED' ? 'var(--degraded-border)' : s === 'WATCH' ? 'var(--watch-border)' : 'var(--eligible-border)';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.04 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

const MODEL_NAMES: Record<string, string> = {
  VendorA: 'FinScore Enterprise',
  VendorB: 'CredVeda AI (Selected)',
  VendorC: 'IndicPay Neural',
};

export default function FailureMapPage() {
  const { data, loading } = useDemoContext();
  const [selectedVendor, setSelectedVendor] = useState<string | null>(null);
  const [selectedHotspot, setSelectedHotspot] = useState<FailureHotspot | null>(null);

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading failure cartography...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load failure cartography.</p>
      </div>
    );
  }

  const vendorsList: VendorScorecard[] = data.vendors ?? [];
  const failureMapsList: VendorFailureMap[] = data.failure_maps ?? [];
  const activeVendorId = selectedVendor ?? (vendorsList.find(v => v.vendor_id === 'VendorB')?.vendor_id || vendorsList[0]?.vendor_id);
  const currentMap = failureMapsList.find(f => f.vendor_id === activeVendorId);
  const hotspots: FailureHotspot[] = Array.isArray(currentMap?.hotspots) ? currentMap.hotspots : [];

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>STRESS CARTOGRAPHY</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Map size={28} color="var(--accent)" /> Failure Cartography & Hotspot Mapping
            </h1>
            <p className="font-subheading" style={{ marginTop: '8px' }}>
              Forensic performance breakdown mapping exact failure points across orthogonal rural DPI deployment strata.
            </p>
          </div>
          <span style={{ fontSize: '11px', fontWeight: 650, color: 'var(--text-muted)' }}>
            Total Deployment Strata: <span className="font-number" style={{ color: 'var(--accent)' }}>24</span>
          </span>
        </div>
      </motion.div>

      {/* Model Selector Tabs */}
      <motion.div variants={item} style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {vendorsList.map(v => {
          const isSelected = activeVendorId === v.vendor_id;
          const label = MODEL_NAMES[v.vendor_id] || (v.display_name ?? v.vendor_id);
          return (
            <button
              key={v.vendor_id}
              className={`btn ${isSelected ? 'btn-accent' : 'btn-secondary'}`}
              onClick={() => { setSelectedVendor(v.vendor_id); setSelectedHotspot(null); }}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <Cpu size={14} /> {label}
            </button>
          );
        })}
      </motion.div>

      {/* Summary KPI Strip */}
      {currentMap && (
        <motion.div variants={item} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '24px' }}>
          <GlassCard style={{ padding: '14px' }} hover={false}>
            <div className="metric metric-sm">
              <span className="metric-label">Mean Stress Accuracy</span>
              <AnimatedNumber value={currentMap.overall_accuracy != null ? currentMap.overall_accuracy : 0} decimals={1} suffix="%" className="metric-value font-number" />
            </div>
          </GlassCard>
          <GlassCard style={{ padding: '14px', borderColor: 'var(--critical-border)' }} hover={false}>
            <div className="metric metric-sm">
              <span className="metric-label" style={{ color: 'var(--critical)' }}>Critical Failure Strata</span>
              <AnimatedNumber value={currentMap.critical_hotspots_count ?? 0} className="metric-value font-number" style={{ color: 'var(--critical)' }} />
            </div>
          </GlassCard>
          <GlassCard style={{ padding: '14px', borderColor: 'var(--degraded-border)' }} hover={false}>
            <div className="metric metric-sm">
              <span className="metric-label" style={{ color: 'var(--degraded)' }}>Degraded Strata</span>
              <AnimatedNumber value={currentMap.degraded_hotspots_count ?? 0} className="metric-value font-number" style={{ color: 'var(--degraded)' }} />
            </div>
          </GlassCard>
          <GlassCard style={{ padding: '14px' }} hover={false}>
            <div className="metric metric-sm">
              <span className="metric-label">DFS Gate Status</span>
              <div style={{ marginTop: '4px' }}><StatusBadge status={currentMap.overall_status} /></div>
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Treemap */}
      {hotspots.length > 0 && (
        <motion.div variants={item} style={{ marginBottom: '24px' }}>
          <GlassCard hover={false}>
            <div className="card-header">
              <span style={{ fontWeight: 700 }}>Compound Stress Impact Treemap</span>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Proportional severity weighting</span>
            </div>
            <HotspotTreemap hotspots={hotspots} />
          </GlassCard>
        </motion.div>
      )}

      {/* Grid of Strata */}
      {hotspots.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>No failure hotspots detected under current pilot constraints.</div>
      ) : (
        <motion.div variants={item} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '10px' }}>
          {hotspots.map((hs, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.02, duration: 0.3 }}
              whileHover={{ y: -2, boxShadow: 'var(--shadow-md)' }}
              onClick={() => setSelectedHotspot(hs)}
              style={{
                background: getSeverityBg(hs.severity),
                border: `1px solid ${getSeverityBorder(hs.severity)}`,
                borderLeft: `4px solid ${getSeverityColor(hs.severity)}`,
                borderRadius: '8px',
                padding: '12px 10px',
                cursor: 'pointer',
              }}
            >
              <div style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)', letterSpacing: '-0.02em', marginBottom: '2px' }}>
                {hs.accuracy.toFixed(1)}%
              </div>
              <div style={{ fontSize: '10px', fontWeight: 750, color: getSeverityColor(hs.severity), marginBottom: '6px', textTransform: 'uppercase' }}>
                {hs.severity}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: 1.35 }}>
                {hs.stratum_id.replace(/_/g, ' ').toLowerCase()}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* Forensic Detail Drawer */}
      <AnimatePresence>
        {selectedHotspot && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{ position: 'fixed', inset: 0, background: 'var(--bg-overlay)', zIndex: 98, backdropFilter: 'blur(4px)' }}
              onClick={() => setSelectedHotspot(null)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              style={{
                position: 'fixed',
                top: 0,
                right: 0,
                bottom: 0,
                width: '400px',
                maxWidth: '100vw',
                background: 'var(--bg-card)',
                borderLeft: '1px solid var(--border)',
                boxShadow: 'var(--shadow-xl)',
                zIndex: 99,
                padding: '32px 24px',
                overflowY: 'auto',
              }}
            >
              <button className="btn btn-ghost btn-sm" style={{ position: 'absolute', top: '16px', right: '16px' }} onClick={() => setSelectedHotspot(null)}>
                <X size={16} /> Close
              </button>
              <div className="font-label" style={{ marginBottom: '8px' }}>COMPOUND DEPLOYMENT CONDITION</div>
              <h2 className="font-mono" style={{ fontSize: '14px', fontWeight: 700, marginBottom: '24px', lineHeight: 1.5, wordBreak: 'break-word' }}>
                {selectedHotspot.stratum_id.replace(/_/g, ' + ')}
              </h2>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                <div className="metric">
                  <span className="metric-label">Observed Accuracy</span>
                  <span className="metric-value font-number" style={{ color: selectedHotspot.severity === 'CRITICAL' ? 'var(--critical)' : 'var(--text-primary)' }}>
                    {selectedHotspot.accuracy.toFixed(2)}%
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Severity Level</span>
                  <div style={{ marginTop: '4px' }}><StatusBadge status={selectedHotspot.severity} /></div>
                </div>
              </div>
              {selectedHotspot.reason && (
                <div style={{ background: 'var(--bg-elevated)', padding: '16px', borderRadius: '8px', marginBottom: '16px', border: '1px solid var(--border)' }}>
                  <div className="font-label" style={{ marginBottom: '6px' }}>Failure Root Cause Diagnosis</div>
                  <p className="font-body" style={{ fontSize: '13px', lineHeight: 1.5 }}>{selectedHotspot.reason}</p>
                </div>
              )}
              <div style={{ background: 'var(--bg-sunken)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div className="font-label" style={{ marginBottom: '4px' }}>DFS Policy Action</div>
                <p style={{ fontSize: '11.5px', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                  Deployment in pilot zones with matching condition combinations is blocked until structured remediation is certified.
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </motion.div>
  );
}