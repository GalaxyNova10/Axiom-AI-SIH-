import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { Gavel, CheckCircle, XCircle } from 'lucide-react';
import type { VendorScorecard } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

export default function DecisionPage() {
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading procurement decisions...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load procurement decisions.</p></div>);

  const vendorsList: VendorScorecard[] = data.vendors ?? [];
  const procurement = data.procurement ?? {};

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>PROCUREMENT GATES</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><Gavel size={28} color="var(--accent)" /> Procurement Decision</h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>Deterministic gate evaluation. No AI involvement in this decision path.</p>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {vendorsList.map((v) => {
          const pd = procurement[v.vendor_id];
          const decision = pd?.decision ?? v.procurement_recommendation ?? 'PENDING';
          const isEligible = decision === 'ELIGIBLE';
          const reasons: string[] = Array.isArray(pd?.reasons) ? pd.reasons : [];
          const gatesObj: Record<string, any> = (pd?.gates && typeof pd.gates === 'object' && !Array.isArray(pd.gates))
            ? pd.gates
            : {};

          return (
            <motion.div key={v.vendor_id} variants={item}>
              <GlassCard hover={false} style={{ borderColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: 700 }}>{v.display_name ?? v.vendor_id}</h3>
                    <span className="font-caption">{v.vendor_id}</span>
                  </div>
                  <StatusBadge status={decision} />
                </div>
                {reasons.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <div className="font-label" style={{ marginBottom: '8px' }}>DECISION REASONS</div>
                    <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {reasons.map((r: string, j: number) => (<li key={j} className="font-body">{String(r)}</li>))}
                    </ul>
                  </div>
                )}
                {Object.keys(gatesObj).length > 0 && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
                    {Object.entries(gatesObj).map(([gateName, gateStatus]) => {
                      const isPass = gateStatus === 'PASS' || gateStatus === true;
                      return (
                        <div key={gateName} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-elevated)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                          <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>{gateName.replace(/_/g, ' ')}</span>
                          {isPass ? <CheckCircle size={16} color="var(--eligible)" /> : <XCircle size={16} color="var(--critical)" />}
                        </div>
                      );
                    })}
                  </div>
                )}
              </GlassCard>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}