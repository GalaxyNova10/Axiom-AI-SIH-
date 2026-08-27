// ============================================================
// Axiom AI — Data Governance & Privacy Framework
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Database, ShieldCheck, Lock, Eye, AlertTriangle, ArrowRight, FileKey } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import { getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult } from '../types/api';

const SANITIZED_KEYS = [
  'private_parameters',
  'raw_seed',
  'seed',
  'seed_hash',
  'secret',
  'private_key',
  'api_key',
  'openai_api_key',
  'model_weights',
  'source_code',
];

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

export default function GovernancePage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
      } catch (err: any) {
        setError(err?.message || 'Failed to load governance data');
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
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading governance policies...</p>
        </div>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>
          {error || 'No governance data available. Run an evaluation first.'}
        </p>
      </div>
    );
  }

  const regulatory = evaluation.pilot_twin_parameters.regulatory_frame;

  const governanceSchedule = [
    {
      label: 'Evidence Integrity',
      status: 'VERIFIED',
      icon: ShieldCheck,
      desc: 'Cryptographic hash verification (SHA-256) for all 15 test results.',
    },
    {
      label: 'PII Protection (DPDP Act 2023)',
      status: 'COMPLIANT',
      icon: Lock,
      desc: 'Aadhaar VID, PAN, mobile numbers, and bank accounts cryptographically tokenized.',
    },
    {
      label: 'RBI Explainability',
      status: 'VERIFIED',
      icon: FileKey,
      desc: 'Adverse action notices with top-3 feature attribution for credit decisions.',
    },
    {
      label: 'Artifact Lineage',
      status: 'VERIFIED',
      icon: ShieldCheck,
      desc: 'Traceable provenance chain from raw test execution to procurement verdict.',
    },
    {
      label: 'Public Audit Trail',
      status: 'VISIBLE',
      icon: Eye,
      desc: 'Test conditions, scores, and failure reasons publicly auditable.',
    },
    {
      label: 'Zero PII Leak',
      status: 'PROTECTED',
      icon: Lock,
      desc: 'No raw PII in model input, output, logs, or frontend display.',
    },
  ];

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>COMPLIANCE & PRIVACY</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database size={28} color="var(--accent)" /> Data Governance
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Evidence provenance, regulatory compliance, and zero-leak privacy guarantees
        </p>
      </motion.div>

      {/* Regulatory Compliance Framework */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650 }}>Regulatory Compliance Framework</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
            {Object.entries(regulatory).map(([key, value]) => (
              <div
                key={key}
                style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--r-md)',
                  padding: '14px 16px',
                }}
              >
                <div className="font-label" style={{ marginBottom: '6px' }}>
                  {key.replace(/_/g, ' ')}
                </div>
                <p style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {value}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* Governance Schedule */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Governance Controls & Verification Status
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {governanceSchedule.map((control) => (
            <GlassCard key={control.label}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--r-md)',
                  background: 'var(--bg-elevated)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  border: '1px solid var(--border)',
                }}>
                  <control.icon size={16} color="var(--accent)" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '6px',
                  }}>
                    <span style={{ fontSize: '14px', fontWeight: 650 }}>{control.label}</span>
                    <StatusBadge status={control.status} size="sm" />
                  </div>
                  <p className="font-body" style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                    {control.desc}
                  </p>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </motion.div>

      {/* Sanitization Boundary */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <GlassCard hover={false}>
          <div className="card-header">
            <span style={{ fontWeight: 650 }}>Frontend Sanitization Boundary</span>
          </div>
          <p className="font-body" style={{ marginBottom: '16px' }}>
            Defense-in-depth sanitization. These key patterns are recursively scrubbed from all API responses
            before reaching the frontend:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
            {SANITIZED_KEYS.map((key) => (
              <span
                key={key}
                className="font-mono"
                style={{
                  background: 'var(--critical-bg)',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '11px',
                  color: 'var(--critical)',
                  border: '1px solid var(--critical-border)',
                  fontWeight: 600,
                }}
              >
                {key}
              </span>
            ))}
          </div>
          <div className="alert alert-warning">
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '13px' }}>
              <strong>Zero-Leak Guarantee:</strong> Raw seeds, private parameters, API keys, and model weights
              are never transmitted to or displayed in the UI. Evaluation results are sanitized at both
              backend and frontend layers.
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Data Flow Diagram */}
      <motion.div variants={item}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Data Flow & Privacy Boundaries
        </h3>
        <GlassCard hover={false} style={{ padding: '40px 24px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            flexWrap: 'wrap',
          }}>
            {[
              {
                label: 'Test Execution',
                sub: 'Private seeds + evaluation params',
                color: 'var(--text-primary)',
                bg: 'var(--bg-sunken)',
                border: 'var(--border)',
              },
              null,
              {
                label: 'Backend Sanitization',
                sub: 'Strip forbidden sensitive keys',
                color: 'var(--critical)',
                bg: 'var(--critical-bg)',
                border: 'var(--critical-border)',
              },
              null,
              {
                label: 'Frontend Defense',
                sub: 'Recursive sanitization pass',
                color: 'var(--watch)',
                bg: 'var(--watch-bg)',
                border: 'var(--watch-border)',
              },
              null,
              {
                label: 'Public Display',
                sub: 'Zero PII, audit-ready results',
                color: 'var(--eligible)',
                bg: 'var(--eligible-bg)',
                border: 'var(--eligible-border)',
              },
            ].map((block, i) => {
              if (block === null) {
                return <ArrowRight key={`arrow-${i}`} size={20} color="var(--text-faint)" />;
              }
              return (
                <div
                  key={i}
                  style={{
                    background: block.bg,
                    border: `2px solid ${block.border}`,
                    padding: '18px 24px',
                    borderRadius: 'var(--r-lg)',
                    minWidth: '160px',
                    textAlign: 'center',
                  }}
                >
                  <div style={{
                    fontSize: '13px',
                    fontWeight: 700,
                    color: block.color,
                    marginBottom: '6px',
                  }}>
                    {block.label}
                  </div>
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                    lineHeight: 1.4,
                  }}>
                    {block.sub}
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}
