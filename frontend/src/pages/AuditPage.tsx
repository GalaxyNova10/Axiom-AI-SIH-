// ============================================================
// Axiom AI — Immutable Audit Trail & Evidence Record
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { FileText, Hash, Clock, Shield } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import { getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult, FintechTestResult } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

export default function AuditPage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
      } catch (err: any) {
        setError(err?.message || 'Failed to load audit trail');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading audit records...</p>
        </div>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>
          {error || 'No audit data available. Run an evaluation first.'}
        </p>
      </div>
    );
  }

  const timestamp = new Date().toISOString();

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>IMMUTABLE GOVERNANCE RECORD</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <FileText size={28} color="var(--accent)" /> Audit Trail
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Complete cryptographic evidence log and procurement decision chain
        </p>
      </motion.div>

      {/* Evaluation Metadata */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={16} /> Evaluation Metadata
            </span>
            <StatusBadge status={evaluation.procurement_verdict} />
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
          }}>
            <div className="metric">
              <span className="metric-label">EVALUATION ID</span>
              <span className="font-mono" style={{ fontSize: '13px', fontWeight: 600 }}>
                {evaluation.evaluation_id}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">SCENARIO</span>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>
                {evaluation.scenario_id}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">STARTUP</span>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>
                {evaluation.startup_name}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">DEPARTMENT</span>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>
                {evaluation.department}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">DISTRICT</span>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>
                {evaluation.district}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">TIMESTAMP</span>
              <span className="font-mono" style={{ fontSize: '11px', fontWeight: 600 }}>
                {timestamp}
              </span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Test Results Summary */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650 }}>Test Execution Summary</span>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px',
          }}>
            <div className="metric">
              <span className="metric-label">TOTAL TESTS</span>
              <span style={{ fontSize: '20px', fontWeight: 800 }}>
                {evaluation.total_tests}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">PASSED</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--eligible)' }}>
                {evaluation.passed_tests}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">PASS RATE</span>
              <span style={{
                fontSize: '20px',
                fontWeight: 800,
                color: evaluation.pass_rate >= 80 ? 'var(--eligible)' : 'var(--critical)',
              }}>
                {evaluation.pass_rate.toFixed(1)}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">CRITICAL FAILURES</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--critical)' }}>
                {evaluation.critical_failures}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">DEGRADED</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--degraded)' }}>
                {evaluation.degraded_failures}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">WATCH</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--watch)' }}>
                {evaluation.watch_failures}
              </span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Evidence Confidence Record */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={16} /> Evidence Confidence Record
            </span>
            <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent)' }}>
              {evaluation.evidence_confidence_score.toFixed(1)}%
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(evaluation.evidence_confidence_breakdown).map(([dimension, score]) => (
              <div
                key={dimension}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  background: 'var(--bg-elevated)',
                  borderRadius: 'var(--r-md)',
                  border: '1px solid var(--border)',
                }}
              >
                <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                  {dimension.replace(/_/g, ' ')}
                </span>
                <span className="font-number" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent)' }}>
                  {score.toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* Evidence Distribution */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650 }}>Evidence Classification Distribution</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(evaluation.evidence_distribution).map(([tier, count]) => (
              <div
                key={tier}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  background: 'var(--bg-elevated)',
                  borderRadius: 'var(--r-md)',
                  border: '1px solid var(--border)',
                }}
              >
                <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)' }}>
                  {tier.replace(/_/g, ' ')}
                </span>
                <span className="font-number" style={{ fontSize: '14px', fontWeight: 700 }}>
                  {count} test{count !== 1 ? 's' : ''}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* Cryptographic Evidence Hashes */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Cryptographic Evidence Seals
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '12px' }}>
          {evaluation.test_results.map((test: FintechTestResult) => (
            <div
              key={test.test_id}
              style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--r-md)',
                padding: '12px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="font-mono" style={{ fontSize: '11px', fontWeight: 800 }}>
                  {test.test_id}
                </span>
                <span style={{
                  fontSize: '9px',
                  fontWeight: 700,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  background: test.passed ? 'var(--eligible-bg)' : 'var(--critical-bg)',
                  color: test.passed ? 'var(--eligible)' : 'var(--critical)',
                }}>
                  {test.passed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                <Hash size={10} color="var(--text-faint)" />
                <span style={{ fontSize: '9px', color: 'var(--text-faint)', textTransform: 'uppercase' }}>
                  Evidence Hash
                </span>
              </div>
              <div className="font-mono" style={{
                fontSize: '10px',
                color: 'var(--accent)',
                wordBreak: 'break-all',
                fontWeight: 600,
              }}>
                {test.evidence_hash}
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Audit Chain Signature */}
      <motion.div variants={item}>
        <div style={{
          background: 'var(--bg-elevated)',
          border: '2px solid var(--border-strong)',
          borderRadius: 'var(--r-lg)',
          padding: '20px 24px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '12px',
          }}>
            <Hash size={18} color="var(--accent)" />
            <span className="font-label" style={{ fontSize: '11px' }}>
              AUDIT CHAIN CRYPTOGRAPHIC SIGNATURE
            </span>
          </div>
          <div className="font-mono" style={{
            fontSize: '12px',
            color: 'var(--text-primary)',
            wordBreak: 'break-all',
            fontWeight: 600,
            padding: '12px',
            background: 'var(--bg-sunken)',
            borderRadius: 'var(--r-md)',
            marginBottom: '12px',
          }}>
            sha256:{evaluation.evaluation_id}::{timestamp}::fintech-15-test-battery::sealed
          </div>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.5, margin: 0 }}>
            This audit trail is cryptographically sealed and immutable. Any modification to the evaluation
            results, evidence records, or procurement decision will invalidate this signature.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
