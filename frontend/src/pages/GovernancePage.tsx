import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { Database, ShieldCheck, Lock, Eye, AlertTriangle, ArrowRight } from 'lucide-react';

const SANITIZED_KEYS = ['private_parameters', 'raw_seed', 'seed', 'seed_hash', 'secret', 'private_key', 'api_key', 'openai_api_key', 'model_weights', 'source_code'];

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function GovernancePage() {
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading governance policies...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load data governance policies.</p></div>);

  const gov = data.data_governance ?? {};
  const scheduleRows = [
    { label: 'Evidence Integrity', status: 'VERIFIED', icon: ShieldCheck, desc: 'Cryptographic hash verification of evaluation artifacts.' },
    { label: 'Artifact Lineage', status: 'VERIFIED', icon: ShieldCheck, desc: 'Traceable provenance chain for all evaluation outputs.' },
    { label: 'Private Parameters', status: 'PROTECTED', icon: Lock, desc: 'Seeds, private keys, model weights are server-side only.' },
    { label: 'Public Deployment Conditions', status: 'VISIBLE', icon: Eye, desc: 'Strata dimensions and failure cartography are publicly auditable.' },
    { label: 'LLM Boundary', status: 'SANITIZED', icon: ShieldCheck, desc: 'Advisory analysis input is stripped of sensitive keys before LLM call.' },
  ];

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>DATA GOVERNANCE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><Database size={28} color="var(--accent)" /> Data Governance Policy</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>Evidence provenance, privacy boundaries, and sanitization guarantees.</p>
      </motion.div>

      <motion.div variants={item} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        <GlassCard hover={false}>
          <div className="card-header"><span style={{ fontWeight: 600 }}>Governance Schedule</span></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {scheduleRows.map(row => (
              <div key={row.label} style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'var(--bg-elevated)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid var(--border)' }}>
                  <row.icon size={15} color="var(--text-muted)" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px' }}>
                    <span style={{ fontSize: '14px', fontWeight: 600 }}>{row.label}</span>
                    <StatusBadge status={row.status} size="sm" />
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{row.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard hover={false}>
          <div className="card-header"><span style={{ fontWeight: 600 }}>Frontend Sanitization Boundary</span></div>
          <p className="font-body" style={{ marginBottom: '16px' }}>Defense-in-depth sanitization. These key patterns are scrubbed from all API responses:</p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
            {SANITIZED_KEYS.map(key => (
              <span key={key} className="font-mono" style={{ background: 'var(--critical-bg)', padding: '3px 8px', borderRadius: '4px', fontSize: '11px', color: 'var(--critical)', border: '1px solid var(--critical-border)' }}>{key}</span>
            ))}
          </div>
          <div className="alert alert-warning">
            <AlertTriangle size={16} style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '13px' }}><strong>Zero-Leak Guarantee:</strong> Raw seeds, private parameters, and model weights are never displayed in the UI.</div>
          </div>
          {Object.keys(gov).length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <div className="font-label" style={{ marginBottom: '10px' }}>Backend Governance Record</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {Object.entries(gov).filter(([k]) => !SANITIZED_KEYS.includes(k.toLowerCase())).map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', padding: '6px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                    <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>{k.replace(/_/g, ' ')}</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: '200px', textAlign: 'right' }}>{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </GlassCard>
      </motion.div>

      {/* Data Flow */}
      <motion.div variants={item}>
        <h2 className="font-heading" style={{ marginBottom: '20px' }}>Data Flow & LLM Boundary</h2>
        <GlassCard hover={false} style={{ padding: '32px', textAlign: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
            {[
              { label: 'Evaluation Output', sub: 'Public metrics + private internal state', color: 'var(--text-primary)', bg: 'var(--bg-sunken)', border: 'var(--border)' },
              null,
              { label: 'Sanitization Boundary', sub: 'Forbidden keys scrubbed recursively', color: 'var(--critical)', bg: 'var(--critical-bg)', border: 'var(--critical-border)' },
              null,
              { label: 'Advisory Diagnostics', sub: 'LLM analysis on safe public data only', color: 'var(--advisory)', bg: 'var(--advisory-bg)', border: 'var(--advisory-border)' },
            ].map((block, i) => {
              if (block === null) return <ArrowRight key={`arrow-${i}`} size={20} color="var(--text-faint)" />;
              return (
                <div key={i} style={{ background: block.bg, border: `1px solid ${block.border}`, padding: '16px 24px', borderRadius: '10px', width: '180px' }}>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: block.color, marginBottom: '6px' }}>{block.label}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.3 }}>{block.sub}</div>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}