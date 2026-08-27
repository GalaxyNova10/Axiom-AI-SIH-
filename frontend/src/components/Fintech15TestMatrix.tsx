// Fintech15TestMatrix.tsx — 15-Point Stress Test Interactive Grid & Forensic Drilldown
import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import StatusBadge from './StatusBadge';
import { AlertTriangle, X, Hash } from 'lucide-react';
import type { FintechTestResult } from '../types/api';

interface Props {
  tests: FintechTestResult[];
}

const getSeverityBorder = (s: string) => {
  if (s === 'CRITICAL') return 'var(--critical-border)';
  if (s === 'DEGRADED') return 'var(--degraded-border)';
  if (s === 'WATCH') return 'var(--watch-border)';
  return 'var(--eligible-border)';
};

const getSeverityBg = (s: string) => {
  if (s === 'CRITICAL') return 'var(--critical-bg)';
  if (s === 'DEGRADED') return 'var(--degraded-bg)';
  if (s === 'WATCH') return 'var(--watch-bg)';
  return 'var(--eligible-bg)';
};

const getSeverityColor = (s: string) => {
  if (s === 'CRITICAL') return 'var(--critical)';
  if (s === 'DEGRADED') return 'var(--degraded)';
  if (s === 'WATCH') return 'var(--watch)';
  return 'var(--eligible)';
};

export default function Fintech15TestMatrix({ tests }: Props) {
  const [filter, setFilter] = useState<'ALL' | 'CRITICAL' | 'DEGRADED' | 'PASSED'>('ALL');
  const [selectedTest, setSelectedTest] = useState<FintechTestResult | null>(null);

  const filteredTests = tests.filter((t) => {
    if (filter === 'CRITICAL') return t.severity === 'CRITICAL';
    if (filter === 'DEGRADED') return t.severity === 'DEGRADED';
    if (filter === 'PASSED') return t.passed;
    return true;
  });

  const passedCount = tests.filter((t) => t.passed).length;
  const criticalCount = tests.filter((t) => t.severity === 'CRITICAL').length;
  const degradedCount = tests.filter((t) => t.severity === 'DEGRADED').length;

  return (
    <div>
      {/* Filters & Summary Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            onClick={() => setFilter('ALL')}
            className={`btn btn-xs ${filter === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All 15 Tests ({tests.length})
          </button>
          <button
            onClick={() => setFilter('PASSED')}
            className={`btn btn-xs ${filter === 'PASSED' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ color: filter === 'PASSED' ? undefined : 'var(--eligible)' }}
          >
            Passed ({passedCount})
          </button>
          <button
            onClick={() => setFilter('CRITICAL')}
            className={`btn btn-xs ${filter === 'CRITICAL' ? 'btn-danger' : 'btn-secondary'}`}
            style={{ color: filter === 'CRITICAL' ? undefined : 'var(--critical)' }}
          >
            Critical ({criticalCount})
          </button>
          <button
            onClick={() => setFilter('DEGRADED')}
            className={`btn btn-xs ${filter === 'DEGRADED' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ color: filter === 'DEGRADED' ? undefined : 'var(--degraded)' }}
          >
            Degraded ({degradedCount})
          </button>
        </div>

        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          Click test card for forensic condition breakdown & evidence hash
        </div>
      </div>

      {/* 15-Test Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
        gap: '12px',
      }}>
        {filteredTests.map((test, idx) => {
          return (
            <motion.div
              key={test.test_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.02, duration: 0.25 }}
              whileHover={{ y: -2, boxShadow: 'var(--shadow-md)' }}
              onClick={() => setSelectedTest(test)}
              style={{
                background: 'var(--bg-card)',
                border: `1px solid ${getSeverityBorder(test.severity)}`,
                borderLeft: `4px solid ${getSeverityColor(test.severity)}`,
                borderRadius: 'var(--r-md)',
                padding: '14px 16px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'all 0.15s ease',
              }}
            >
              <div>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="font-mono" style={{
                      fontSize: '11px',
                      fontWeight: 800,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: 'var(--bg-elevated)',
                      color: 'var(--text-primary)',
                      border: '1px solid var(--border)',
                    }}>
                      {test.test_id}
                    </span>
                    <span style={{
                      fontSize: '9.5px',
                      fontWeight: 700,
                      padding: '2px 5px',
                      borderRadius: '4px',
                      background: 'var(--bg-sunken)',
                      color: 'var(--text-secondary)',
                      textTransform: 'uppercase',
                    }}>
                      {test.domain}
                    </span>
                  </div>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 750,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: getSeverityBg(test.severity),
                    color: getSeverityColor(test.severity),
                    textTransform: 'uppercase',
                  }}>
                    {test.severity}
                  </span>
                </div>

                {/* Name */}
                <h4 style={{ fontSize: '13px', fontWeight: 650, color: 'var(--text-primary)', marginBottom: '6px', lineHeight: 1.3 }}>
                  {test.name}
                </h4>
                <p style={{
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  lineHeight: 1.4,
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  marginBottom: '12px',
                }}>
                  {test.description}
                </p>
              </div>

              {/* Metrics Bottom */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '8px',
                borderTop: '1px solid var(--border-subtle)',
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                  <span style={{ fontSize: '10px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Acc:</span>
                  <span className="font-number" style={{
                    fontSize: '14px',
                    fontWeight: 800,
                    color: test.accuracy < 80 ? 'var(--critical)' : 'var(--text-primary)',
                  }}>
                    {test.accuracy.toFixed(1)}%
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
                  <span style={{ fontSize: '10px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>Lat:</span>
                  <span className="font-number" style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {test.latency_ms.toFixed(0)}ms
                  </span>
                </div>
                <span style={{
                  fontSize: '9px',
                  fontWeight: 600,
                  color: 'var(--eligible)',
                  background: 'var(--eligible-bg)',
                  padding: '1px 5px',
                  borderRadius: '3px',
                }}>
                  L5 Sealed
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Forensic Drilldown Drawer */}
      <AnimatePresence>
        {selectedTest && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedTest(null)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'var(--bg-overlay)',
                backdropFilter: 'blur(4px)',
                zIndex: 110,
              }}
            />

            {/* Slide-out Drawer */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 280 }}
              style={{
                position: 'fixed',
                top: 0,
                right: 0,
                bottom: 0,
                width: '440px',
                maxWidth: '100vw',
                background: 'var(--bg-card)',
                borderLeft: '1px solid var(--border-strong)',
                boxShadow: 'var(--shadow-xl)',
                zIndex: 111,
                padding: '32px 24px',
                overflowY: 'auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
              }}
            >
              {/* Header */}
              <div>
                <button
                  onClick={() => setSelectedTest(null)}
                  className="btn btn-ghost btn-sm"
                  style={{ position: 'absolute', top: '20px', right: '20px' }}
                >
                  <X size={16} /> Close
                </button>
                <div className="font-label" style={{ marginBottom: '6px' }}>
                  FORENSIC TEST INSPECTION · {selectedTest.domain}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span className="font-mono" style={{
                    fontSize: '13px',
                    fontWeight: 800,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                  }}>
                    {selectedTest.test_id}
                  </span>
                  <h3 style={{ fontSize: '16px', fontWeight: 750, color: 'var(--text-primary)' }}>
                    {selectedTest.name}
                  </h3>
                </div>
                <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {selectedTest.description}
                </p>
              </div>

              {/* Status & Scores */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                background: 'var(--bg-elevated)',
                padding: '16px',
                borderRadius: 'var(--r-md)',
                border: '1px solid var(--border)',
              }}>
                <div>
                  <span className="font-label">Accuracy Score</span>
                  <div className="font-number" style={{
                    fontSize: '22px',
                    fontWeight: 800,
                    color: selectedTest.accuracy < 80 ? 'var(--critical)' : 'var(--eligible)',
                    marginTop: '2px',
                  }}>
                    {selectedTest.accuracy.toFixed(2)}%
                  </div>
                </div>
                <div>
                  <span className="font-label">Test Severity</span>
                  <div style={{ marginTop: '6px' }}>
                    <StatusBadge status={selectedTest.severity} />
                  </div>
                </div>
                <div>
                  <span className="font-label">Execution Latency</span>
                  <div className="font-number" style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {selectedTest.latency_ms.toFixed(1)} ms
                  </div>
                </div>
                <div>
                  <span className="font-label">Evidence Tier</span>
                  <div style={{ marginTop: '6px' }}>
                    <StatusBadge status={selectedTest.evidence_level} size="sm" />
                  </div>
                </div>
              </div>

              {/* Failure Root Cause */}
              {selectedTest.failure_reason && (
                <div style={{
                  background: 'var(--critical-bg)',
                  border: '1px solid var(--critical-border)',
                  borderRadius: 'var(--r-md)',
                  padding: '14px 16px',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 700, color: 'var(--critical)', textTransform: 'uppercase', marginBottom: '4px' }}>
                    <AlertTriangle size={13} /> Threshold Breach Diagnosis
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--critical)', lineHeight: 1.45, margin: 0 }}>
                    {selectedTest.failure_reason}
                  </p>
                </div>
              )}

              {/* Condition Stacking */}
              <div style={{ background: 'var(--bg-elevated)', padding: '16px', borderRadius: 'var(--r-md)', border: '1px solid var(--border)' }}>
                <div className="font-label" style={{ marginBottom: '10px' }}>SIMULATED PILOT CONDITIONS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {Object.entries(selectedTest.conditions || {}).map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', paddingBottom: '6px', borderBottom: '1px solid var(--border-subtle)' }}>
                      <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{k}</span>
                      <span className="font-mono" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Feature Attribution (if available) */}
              {selectedTest.feature_attribution && (
                <div style={{ background: 'var(--bg-elevated)', padding: '16px', borderRadius: 'var(--r-md)', border: '1px solid var(--border)' }}>
                  <div className="font-label" style={{ marginBottom: '10px' }}>RBI ADVERSE ACTION ATTRIBUTION</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {Object.entries(selectedTest.feature_attribution).map(([feat, imp]) => (
                      <div key={feat}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '3px' }}>
                          <span style={{ color: 'var(--text-secondary)' }}>{feat.replace(/_/g, ' ')}</span>
                          <span className="font-number" style={{ fontWeight: 700, color: 'var(--accent)' }}>{(imp * 100).toFixed(1)}%</span>
                        </div>
                        <div style={{ height: '4px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${imp * 100}%`, background: 'var(--accent)', borderRadius: '99px' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Evidence Seal Hash */}
              <div style={{
                background: 'var(--bg-sunken)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--r-md)',
                padding: '12px 14px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '10.5px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '4px' }}>
                  <Hash size={12} /> Sealed Artifact Checksum
                </div>
                <div className="font-mono" style={{ fontSize: '11px', color: 'var(--accent)', wordBreak: 'break-all', fontWeight: 600 }}>
                  {selectedTest.evidence_hash}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}