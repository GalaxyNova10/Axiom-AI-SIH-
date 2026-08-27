import { useParams } from 'react-router-dom';
import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import AnimatedNumber from '../components/AnimatedNumber';
import { Target, ShieldAlert, AlertTriangle, CheckCircle, XCircle, Cpu, Landmark } from 'lucide-react';
import type { VendorScorecard, VendorFailureMap, DiagnosticReport, FailureHotspot } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

const PIPELINE_STAGES = [
  'Proposal Intake', 'DFS Pilot Twin', '15-Test Battery',
  'Failure Cartography', 'Forensic AI', 'DFS Gate Decision',
  'Scale-Up Policy', 'Human Authorization'
];

const FINTECH_METADATA: Record<string, { name: string; type: string; arch: string; desc: string }> = {
  VendorA: {
    name: 'FinScore Enterprise',
    type: 'Legacy Rule-Based + XGBoost Scorer',
    arch: 'Tabular XGBoost + Credit Bureau Rules',
    desc: 'High standard bureau accuracy, but acute degradation under thin-file rural & 2G network constraints.',
  },
  VendorB: {
    name: 'CredVeda AI (Selected Startup)',
    type: 'Multimodal LLM + GNN Risk Ensemble',
    arch: 'Transformer LLM (12 Indic Dialects) + GNN Transaction Graph Layer',
    desc: 'Offline-first resilient engine for vernacular MSME credit underwriting under PM SVANidhi & MUDRA schemes.',
  },
  VendorC: {
    name: 'IndicPay Neural',
    type: 'Speech & OCR Deep Learning Specialist',
    arch: 'Conformer Speech-to-Text + OCR Transformer',
    desc: 'High baseline speech benchmark, but suffers compound failure under low-end hardware + noisy input.',
  },
};

export default function VendorDetailPage() {
  const { vendorId } = useParams<{ vendorId: string }>();
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading model evaluation...</p>
        </div>
      </div>
    );
  }

  if (!data || !vendorId) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to view model details.</p>
      </div>
    );
  }

  const vendorsList: VendorScorecard[] = data.vendors ?? [];
  const failureMapsList: VendorFailureMap[] = data.failure_maps ?? [];
  const diagnosticsList: DiagnosticReport[] = data.diagnostics ?? [];

  const rawVendor = vendorsList.find(v => v.vendor_id === vendorId);
  if (!rawVendor) {
    return (
      <div className="page" style={{ textAlign: 'center', padding: '60px' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Model not found: {vendorId}</p>
      </div>
    );
  }

  const meta = FINTECH_METADATA[vendorId] || {
    name: rawVendor.display_name ?? rawVendor.vendor_id,
    type: 'Fintech Credit Risk Model',
    arch: 'Deep Learning Ensemble',
    desc: rawVendor.description ?? '',
  };

  const fm = failureMapsList.find(f => f.vendor_id === vendorId);
  const diag = diagnosticsList.find(d => d.vendor_id === vendorId);
  const procDecision = data.procurement?.[vendorId];
  const finalDecision = procDecision?.decision ?? rawVendor.procurement_recommendation ?? 'PENDING';
  const isEligible = finalDecision === 'ELIGIBLE';

  const reasons: string[] = Array.isArray(procDecision?.reasons) ? procDecision.reasons : [];
  const gatesObj: Record<string, any> = (procDecision?.gates && typeof procDecision.gates === 'object' && !Array.isArray(procDecision.gates))
    ? procDecision.gates
    : {};
  const hotspots: FailureHotspot[] = Array.isArray(fm?.hotspots) ? fm.hotspots : [];

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>FINTECH MODEL EVALUATION DOSSIER</div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Cpu size={28} color="var(--accent)" /> {meta.name}
            </h1>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginTop: '4px' }}>
              <span className="font-mono" style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{vendorId}</span>
              <span style={{ color: 'var(--text-faint)' }}>·</span>
              <span style={{ fontSize: '12.5px', color: 'var(--accent)', fontWeight: 600 }}>{meta.arch}</span>
            </div>
          </div>
          <StatusBadge status={finalDecision} />
        </div>
        <p className="font-subheading" style={{ marginTop: '8px', maxWidth: '750px' }}>{meta.desc}</p>
      </motion.div>

      {/* Pipeline Stage Tracker */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false} style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '4px', overflowX: 'auto' }}>
            {PIPELINE_STAGES.map((stage, i) => {
              const isAuth = stage.includes('Authorization');
              return (
                <div key={stage} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {i > 0 && <div style={{ width: '16px', height: '1px', background: 'var(--border-strong)' }} />}
                  <div style={{ textAlign: 'center' }}>
                    <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ delay: i * 0.04 }}
                      style={{
                        width: '26px', height: '26px', borderRadius: '50%', margin: '0 auto',
                        background: isAuth ? 'var(--accent-muted)' : 'var(--eligible-bg)',
                        border: `2px solid ${isAuth ? 'var(--accent)' : 'var(--eligible)'}`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px', fontWeight: 800,
                        color: isAuth ? 'var(--accent)' : 'var(--eligible)',
                      }}>
                      {isAuth ? '?' : '\u2713'}
                    </motion.div>
                    <div style={{ fontSize: '9px', fontWeight: 600, textAlign: 'center', marginTop: '6px', color: isAuth ? 'var(--text-muted)' : 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.03em', lineHeight: 1.2 }}>{stage}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>
      </motion.div>

      {/* Metrics Strip */}
      <motion.div variants={item} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        <GlassCard hover={false}>
          <div className="card-header"><span style={{ fontWeight: 700 }}>Government Stress Performance</span></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="metric">
              <span className="metric-label">Stress Accuracy</span>
              <AnimatedNumber value={rawVendor.accuracy ?? 0} decimals={1} suffix="%" className="metric-value font-number" style={{ color: (rawVendor.accuracy ?? 0) < 80 ? 'var(--critical)' : 'var(--eligible)' }} />
            </div>
            <div className="metric">
              <span className="metric-label">P99 Inference</span>
              <span className="metric-value font-number">{rawVendor.latency?.toFixed(0) ?? '\u2014'}<span style={{ fontSize: '13px', fontWeight: 400, color: 'var(--text-muted)' }}> ms</span></span>
            </div>
            <div className="metric">
              <span className="metric-label">Evidence Confidence</span>
              <AnimatedNumber value={rawVendor.evidence_confidence ?? 0} decimals={1} suffix="%" className="metric-value font-number" style={{ color: 'var(--accent)' }} />
            </div>
            <div className="metric">
              <span className="metric-label">Critical Breaches</span>
              <span className="metric-value font-number" style={{ color: (fm?.critical_hotspots_count ?? 0) > 0 ? 'var(--critical)' : 'var(--eligible)' }}>
                {fm?.critical_hotspots_count ?? 0}
              </span>
            </div>
          </div>
        </GlassCard>

        <GlassCard hover={false}>
          <div className="card-header"><span style={{ fontWeight: 700 }}>Statutory Regulatory Alignment</span></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="metric"><span className="metric-label">Evidence Standard</span><span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--eligible)', marginTop: '4px' }}>AECP-5 L5 Sealed</span></div>
            <div className="metric"><span className="metric-label">DPDP Act 2023</span><div style={{ marginTop: '4px' }}><StatusBadge status="VERIFIED" /></div></div>
            <div className="metric" style={{ gridColumn: 'span 2' }}>
              <span className="metric-label">RBI Digital Lending 2022</span>
              <div style={{ marginTop: '4px' }}><StatusBadge status={fm?.overall_status ?? 'NORMAL'} dot /></div>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Failure Hotspots */}
      {hotspots.length > 0 && (
        <motion.div variants={item} style={{ marginBottom: '24px' }}>
          <GlassCard hover={false}>
            <div className="card-header">
              <span style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={16} color="var(--critical)" /> Identified Stress Failure Hotspots
              </span>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>
                <span style={{ color: 'var(--critical)', fontWeight: 700 }}>{fm?.critical_hotspots_count ?? 0} critical</span>
                {'\u00B7'} {fm?.degraded_hotspots_count ?? 0} degraded {'\u00B7'} {fm?.watch_hotspots_count ?? 0} watch
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '10px' }}>
              {hotspots.slice(0, 12).map((hs, i) => (
                <motion.div key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.03 }}
                  style={{
                    background: hs.severity === 'CRITICAL' ? 'var(--critical-bg)' : hs.severity === 'DEGRADED' ? 'var(--degraded-bg)' : 'var(--watch-bg)',
                    border: `1px solid ${hs.severity === 'CRITICAL' ? 'var(--critical-border)' : hs.severity === 'DEGRADED' ? 'var(--degraded-border)' : 'var(--watch-border)'}`,
                    borderRadius: '8px', padding: '12px',
                  }}>
                  <div style={{ fontWeight: 800, fontSize: '16px', marginBottom: '2px' }}>{hs.accuracy.toFixed(1)}%</div>
                  <div style={{ fontSize: '10px', fontWeight: 750, color: hs.severity === 'CRITICAL' ? 'var(--critical)' : hs.severity === 'DEGRADED' ? 'var(--degraded)' : 'var(--watch)', marginBottom: '4px', textTransform: 'uppercase' }}>
                    {hs.severity}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.3 }}>{hs.stratum_id.replace(/_/g, ' ')}</div>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* DFS Procurement Gate */}
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <GlassCard hover={false} style={{ borderColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)' }}>
          <div className="card-header" style={{ borderBottomColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)' }}>
            <span style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', color: isEligible ? 'var(--eligible)' : 'var(--critical)' }}>
              <ShieldAlert size={16} /> Department of Financial Services (DFS) Procurement Gate
            </span>
            <StatusBadge status={finalDecision} />
          </div>
          {reasons.length > 0 && (
            <div>
              <div className="font-label" style={{ marginBottom: '8px' }}>Gate Evaluation Verdict Reasons</div>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {reasons.map((r: string, i: number) => (
                  <li key={i} className="font-body" style={{ color: 'var(--text-primary)' }}>{String(r)}</li>
                ))}
              </ul>
            </div>
          )}
          {Object.keys(gatesObj).length > 0 && (
            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
              {Object.entries(gatesObj).map(([gateName, gateStatus]) => {
                const isPass = gateStatus === 'PASS' || gateStatus === true;
                return (
                  <div key={gateName} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-elevated)', padding: '10px 14px', borderRadius: '8px', border: '1px solid var(--border)' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>{gateName.replace(/_/g, ' ')}</span>
                    {isPass ? <CheckCircle size={16} color="var(--eligible)" /> : <XCircle size={16} color="var(--critical)" />}
                  </div>
                );
              })}
            </div>
          )}
        </GlassCard>
      </motion.div>

      {/* Forensic Intelligence */}
      {diag?.overall_verdict_explanation && (
        <motion.div variants={item}>
          <GlassCard hover={false} style={{ borderColor: 'var(--advisory-border)' }}>
            <div className="card-header" style={{ borderBottomColor: 'var(--advisory-border)' }}>
              <span style={{ fontWeight: 700, color: 'var(--advisory)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertTriangle size={16} /> Forensic Evaluation Intelligence
              </span>
              <StatusBadge status={diag.analysis_mode} />
            </div>
            <div className="alert alert-advisory" style={{ marginBottom: '12px' }}>
              <AlertTriangle size={16} style={{ flexShrink: 0 }} />
              <strong>AI advisory intelligence only. Does not alter the deterministic DFS gate outcome.</strong>
            </div>
            <p className="font-body" style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{diag.overall_verdict_explanation}</p>
          </GlassCard>
        </motion.div>
      )}
    </motion.div>
  );
}