// ============================================================
// Axiom AI — Fintech Diagnostics & Test Intelligence Page
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Brain, AlertCircle, TrendingDown, CheckCircle2, XCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import { getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult, FintechTestResult } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

function TestDiagnosticCard({ test }: { test: FintechTestResult }) {
  const severityColor = test.severity === 'CRITICAL' ? 'var(--critical)' :
                       test.severity === 'DEGRADED' ? 'var(--degraded)' :
                       test.severity === 'WATCH' ? 'var(--watch)' : 'var(--eligible)';

  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: `1px solid var(--border)`,
      borderLeft: `4px solid ${severityColor}`,
      borderRadius: 'var(--r-md)',
      padding: '16px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="font-mono" style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-primary)' }}>
              {test.test_id}
            </span>
            <span style={{
              fontSize: '9px',
              fontWeight: 700,
              padding: '2px 6px',
              borderRadius: '4px',
              background: 'var(--bg-sunken)',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
            }}>
              {test.domain}
            </span>
          </div>
          <h4 style={{ fontSize: '14px', fontWeight: 650, color: 'var(--text-primary)', marginBottom: '4px' }}>
            {test.name}
          </h4>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
            {test.description}
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {test.passed ? (
            <CheckCircle2 size={20} color="var(--eligible)" />
          ) : (
            <XCircle size={20} color="var(--critical)" />
          )}
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
        padding: '12px',
        background: 'var(--bg-card)',
        borderRadius: 'var(--r-sm)',
        marginBottom: '12px',
      }}>
        <div>
          <span className="font-label" style={{ fontSize: '9px' }}>ACCURACY</span>
          <div className="font-number" style={{
            fontSize: '16px',
            fontWeight: 800,
            color: test.accuracy < 80 ? 'var(--critical)' : 'var(--eligible)',
          }}>
            {test.accuracy.toFixed(1)}%
          </div>
        </div>
        <div>
          <span className="font-label" style={{ fontSize: '9px' }}>LATENCY</span>
          <div className="font-number" style={{ fontSize: '14px', fontWeight: 700 }}>
            {test.latency_ms.toFixed(0)}ms
          </div>
        </div>
        <div>
          <span className="font-label" style={{ fontSize: '9px' }}>SEVERITY</span>
          <div style={{ marginTop: '4px' }}>
            <StatusBadge status={test.severity} size="sm" />
          </div>
        </div>
      </div>

      {test.failure_reason && (
        <div style={{
          background: 'var(--critical-bg)',
          border: '1px solid var(--critical-border)',
          borderRadius: 'var(--r-sm)',
          padding: '10px 12px',
          marginBottom: '12px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '10px',
            fontWeight: 700,
            color: 'var(--critical)',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}>
            <AlertCircle size={12} /> Failure Diagnosis
          </div>
          <p style={{ fontSize: '11.5px', color: 'var(--critical)', lineHeight: 1.4, margin: 0 }}>
            {test.failure_reason}
          </p>
        </div>
      )}

      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>Connectivity:</span>
          <span className="font-mono" style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
            {test.conditions.connectivity}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span>Device:</span>
          <span className="font-mono" style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
            {test.conditions.device}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>Input Type:</span>
          <span className="font-mono" style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
            {test.conditions.input}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function DiagnosticsPage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'ALL' | 'FAILED' | 'CRITICAL' | 'PASSED'>('FAILED');

  useEffect(() => {
    async function load() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
      } catch (err: any) {
        setError(err?.message || 'Failed to load diagnostics');
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
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading diagnostics...</p>
        </div>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>
          {error || 'No diagnostic data available. Run an evaluation first.'}
        </p>
      </div>
    );
  }

  const filteredTests = evaluation.test_results.filter(test => {
    if (filter === 'FAILED') return !test.passed;
    if (filter === 'CRITICAL') return test.severity === 'CRITICAL';
    if (filter === 'PASSED') return test.passed;
    return true;
  });

  const failedTests = evaluation.test_results.filter(t => !t.passed);
  const criticalCount = evaluation.test_results.filter(t => t.severity === 'CRITICAL').length;

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>FORENSIC INTELLIGENCE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Brain size={28} color="var(--accent)" /> Test Diagnostics
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Deep analysis of test execution results and failure patterns
        </p>
      </motion.div>

      {/* Summary Cards */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <GlassCard hover={false}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--r-md)',
                background: 'var(--accent-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Brain size={20} color="var(--accent)" />
              </div>
              <div>
                <div className="font-label">TOTAL TESTS</div>
                <div className="font-number" style={{ fontSize: '22px', fontWeight: 800 }}>
                  {evaluation.total_tests}
                </div>
              </div>
            </div>
          </GlassCard>

          <GlassCard hover={false}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--r-md)',
                background: 'var(--critical-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <TrendingDown size={20} color="var(--critical)" />
              </div>
              <div>
                <div className="font-label">FAILURES</div>
                <div className="font-number" style={{ fontSize: '22px', fontWeight: 800, color: 'var(--critical)' }}>
                  {failedTests.length}
                </div>
              </div>
            </div>
          </GlassCard>

          <GlassCard hover={false}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--r-md)',
                background: 'var(--critical-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <AlertCircle size={20} color="var(--critical)" />
              </div>
              <div>
                <div className="font-label">CRITICAL</div>
                <div className="font-number" style={{ fontSize: '22px', fontWeight: 800, color: 'var(--critical)' }}>
                  {criticalCount}
                </div>
              </div>
            </div>
          </GlassCard>

          <GlassCard hover={false}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: 'var(--r-md)',
                background: 'var(--eligible-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <CheckCircle2 size={20} color="var(--eligible)" />
              </div>
              <div>
                <div className="font-label">PASS RATE</div>
                <div className="font-number" style={{ fontSize: '22px', fontWeight: 800, color: 'var(--eligible)' }}>
                  {evaluation.pass_rate.toFixed(1)}%
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div variants={item} style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setFilter('ALL')}
            className={`btn btn-sm ${filter === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All Tests ({evaluation.test_results.length})
          </button>
          <button
            onClick={() => setFilter('FAILED')}
            className={`btn btn-sm ${filter === 'FAILED' ? 'btn-danger' : 'btn-secondary'}`}
          >
            Failed ({failedTests.length})
          </button>
          <button
            onClick={() => setFilter('CRITICAL')}
            className={`btn btn-sm ${filter === 'CRITICAL' ? 'btn-danger' : 'btn-secondary'}`}
          >
            Critical ({criticalCount})
          </button>
          <button
            onClick={() => setFilter('PASSED')}
            className={`btn btn-sm ${filter === 'PASSED' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Passed ({evaluation.passed_tests})
          </button>
        </div>
      </motion.div>

      {/* Test Results Grid */}
      <motion.div variants={item}>
        {filteredTests.length === 0 ? (
          <GlassCard hover={false}>
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              No tests match the selected filter
            </div>
          </GlassCard>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '16px' }}>
            {filteredTests.map((test, idx) => (
              <motion.div
                key={test.test_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.03, duration: 0.3 }}
              >
                <TestDiagnosticCard test={test} />
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
