import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { ArrowUpRight } from 'lucide-react';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function ScaleUpPage() {
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading scale-up evaluation...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load scale-up analysis.</p></div>);

  const scaleUp = data.scale_up ?? {};
  const entries = Object.entries(scaleUp);

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>SCALE ANALYSIS</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><ArrowUpRight size={28} color="var(--accent)" /> Scale-Up Evaluation</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>Post-pilot scaling readiness assessment.</p>
      </motion.div>

      {entries.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>No scale-up data available.</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
          {entries.map(([key, value], i) => (
            <motion.div key={key} variants={item}>
              <GlassCard delay={i * 0.05}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>{key.replace(/_/g, ' ')}</span>
                  {typeof value === 'string' && <StatusBadge status={value} />}
                </div>
                {typeof value === 'object' && value !== null ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {Object.entries(value as Record<string, unknown>).map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', padding: '4px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                        <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>{k.replace(/_/g, ' ')}</span>
                        <span style={{ color: 'var(--text-primary)', fontWeight: 500, maxWidth: '200px', textAlign: 'right' }}>{typeof v === 'string' ? v : JSON.stringify(v)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="font-body">{String(value)}</p>
                )}
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}