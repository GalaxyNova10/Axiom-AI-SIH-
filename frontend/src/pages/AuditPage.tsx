import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { FileText, Clock, Hash } from 'lucide-react';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function AuditPage() {
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading audit records...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load audit trail.</p></div>);

  const audit = data.audit_summary ?? {};
  const entries = Object.entries(audit);
  const auth = data.human_authorization;

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>IMMUTABLE RECORD</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><FileText size={28} color="var(--accent)" /> Audit Trail</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>Complete governance chain evidence log.</p>
      </motion.div>

      {/* Authorization Summary */}
      {auth && (
        <motion.div variants={item} style={{ marginBottom: '24px' }}>
          <GlassCard hover={false}>
            <div className="card-header"><span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}><Clock size={16} /> Authorization Record</span><StatusBadge status={auth.status ?? 'PENDING'} /></div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {Object.entries(auth).filter(([k]) => !['status'].includes(k) && typeof (auth as any)[k] !== 'object').map(([k, v]) => (
                <div key={k} className="metric"><span className="metric-label">{k.replace(/_/g, ' ')}</span><span style={{ fontSize: '14px', fontWeight: 500, marginTop: '4px', color: 'var(--text-primary)' }}>{typeof v === 'boolean' ? (v ? 'Yes' : 'No') : String(v ?? '\u2014')}</span></div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Audit Entries */}
      {entries.length > 0 && (
        <motion.div variants={item}>
          <GlassCard hover={false}>
            <div className="card-header"><span style={{ fontWeight: 600 }}>Audit Summary</span></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {entries.map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 'var(--r-md)', border: '1px solid var(--border)' }}>
                  <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)' }}>{k.replace(/_/g, ' ')}</span>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Signature */}
      <motion.div variants={item} style={{ marginTop: '32px' }}>
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '8px', padding: '14px 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}><Hash size={14} color="var(--text-faint)" /><span className="font-label">Audit Chain Signature</span></div>
          <div className="font-mono" style={{ fontSize: '11px', color: 'var(--text-muted)', wordBreak: 'break-all' }}>sha256:axiom-demo-001-audit-sealed</div>
        </div>
      </motion.div>
    </motion.div>
  );
}