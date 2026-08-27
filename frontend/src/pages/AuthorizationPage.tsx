import { useState } from 'react';
import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import { submitAuthorization } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { ShieldCheck, AlertTriangle, Send } from 'lucide-react';
import type { VendorScorecard } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function AuthorizationPage() {
  const { data, loading } = useDemoContext();
  const [vendorId, setVendorId] = useState('');
  const [action, setAction] = useState('APPROVE');
  const [justification, setJustification] = useState('');
  const [officerId, setOfficerId] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading authorization record...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to access authorization.</p></div>);

  const vendorsList: VendorScorecard[] = data.vendors ?? [];
  const evalId = vendorsList[0]?.evaluation_id ?? 'demo';
  const auth = data.human_authorization;

  const handleSubmit = async () => {
    if (!vendorId || !justification || !officerId) { setError('All fields required.'); return; }
    setSubmitting(true); setError(null);
    try {
      const res = await submitAuthorization(evalId, { vendor_id: vendorId, action, officer_id: officerId, justification });
      setResult(res as unknown as Record<string, unknown>);
    } catch (err: unknown) { setError((err as { message?: string })?.message ?? 'Submission failed'); }
    finally { setSubmitting(false); }
  };

  const inputStyle: React.CSSProperties = { width: '100%', padding: '10px 14px', borderRadius: 'var(--r-md)', border: '1px solid var(--border-strong)', background: 'var(--bg-elevated)', color: 'var(--text-primary)', fontSize: '14px', fontFamily: 'inherit', outline: 'none', transition: 'border-color 0.15s' };

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>HUMAN-IN-THE-LOOP</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><ShieldCheck size={28} color="var(--accent)" /> Human Authorization</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>Final human oversight before any procurement action.</p>
      </motion.div>

      <motion.div variants={item}><div className="alert alert-advisory" style={{ marginBottom: '32px' }}><AlertTriangle size={16} style={{ flexShrink: 0 }} /><div><strong>No autonomous action.</strong> All procurement decisions require explicit human authorization. AI provides advisory intelligence only.</div></div></motion.div>

      {auth && (
        <motion.div variants={item} style={{ marginBottom: '32px' }}>
          <GlassCard hover={false}>
            <div className="card-header"><span style={{ fontWeight: 600 }}>Current Authorization State</span><StatusBadge status={auth.status ?? 'PENDING'} /></div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {auth.vendor_id && <div className="metric"><span className="metric-label">Vendor</span><span style={{ fontSize: '14px', fontWeight: 600, marginTop: '4px' }}>{auth.vendor_id}</span></div>}
              {auth.ai_recommendation && <div className="metric"><span className="metric-label">AI Recommendation</span><span style={{ fontSize: '14px', fontWeight: 600, marginTop: '4px' }}>{auth.ai_recommendation}</span></div>}
              {auth.human_decision && <div className="metric"><span className="metric-label">Human Decision</span><div style={{ marginTop: '4px' }}><StatusBadge status={auth.human_decision} /></div></div>}
            </div>
          </GlassCard>
        </motion.div>
      )}

      <motion.div variants={item}>
        <GlassCard hover={false}>
          <div className="card-header"><span style={{ fontWeight: 600 }}>Submit Authorization</span></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '500px' }}>
            <div><div className="font-label" style={{ marginBottom: '6px' }}>Vendor ID</div>
              <select value={vendorId} onChange={e => setVendorId(e.target.value)} style={inputStyle}>
                <option value="">Select vendor</option>
                {vendorsList.map(v => <option key={v.vendor_id} value={v.vendor_id}>{v.display_name ?? v.vendor_id}</option>)}
              </select>
            </div>
            <div><div className="font-label" style={{ marginBottom: '6px' }}>Action</div>
              <select value={action} onChange={e => setAction(e.target.value)} style={inputStyle}>
                <option value="APPROVE">APPROVE</option><option value="REJECT">REJECT</option><option value="OVERRIDE">OVERRIDE</option><option value="REQUEST_RETEST">REQUEST RETEST</option>
              </select>
            </div>
            <div><div className="font-label" style={{ marginBottom: '6px' }}>Officer ID</div><input value={officerId} onChange={e => setOfficerId(e.target.value)} placeholder="e.g. GOV-OFFICER-001" style={inputStyle} /></div>
            <div><div className="font-label" style={{ marginBottom: '6px' }}>Justification</div><textarea value={justification} onChange={e => setJustification(e.target.value)} placeholder="Provide written justification..." rows={3} style={{ ...inputStyle, resize: 'vertical' }} /></div>
            {error && <div className="alert alert-error"><AlertTriangle size={14} /> {error}</div>}
            <button className="btn btn-accent" onClick={handleSubmit} disabled={submitting}>{submitting ? 'Submitting...' : <><Send size={14} /> Submit Authorization</>}</button>
          </div>
        </GlassCard>
      </motion.div>

      {result && (
        <motion.div variants={item} style={{ marginTop: '24px' }}>
          <GlassCard hover={false} style={{ borderColor: 'var(--eligible-border)' }}>
            <div className="card-header"><span style={{ fontWeight: 600, color: 'var(--eligible)' }}>Authorization Recorded</span></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {Object.entries(result).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', padding: '4px 0', borderBottom: '1px solid var(--border-subtle)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{k.replace(/_/g, ' ')}</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{typeof v === 'boolean' ? (v ? 'Yes' : 'No') : String(v)}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}
    </motion.div>
  );
}