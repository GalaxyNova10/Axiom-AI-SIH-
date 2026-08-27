import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import { Brain, AlertCircle, ShieldAlert, MessageSquare, RotateCcw } from 'lucide-react';
import type { DiagnosticReport, VendorFailureMap, HotspotDiagnosis, VendorChallenge, RetestRecommendation } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

function StratumChips({ stratumId }: { stratumId: string }) {
  const parts = (stratumId || '').split('_');
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
      {parts.map((p, i) => (
        <span key={i} style={{ padding: '2px 8px', background: 'var(--bg-elevated)', borderRadius: '4px', fontSize: '10px', fontWeight: 600, color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>{p}</span>
      ))}
    </div>
  );
}

function HotspotCard({ hs }: { hs: HotspotDiagnosis }) {
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <StratumChips stratumId={hs.stratum_id} />
        {hs.diagnostic_confidence != null && <span className="font-caption">{String(hs.diagnostic_confidence)}% conf.</span>}
      </div>
      {hs.interaction_diagnosis && <p className="font-body" style={{ marginBottom: '8px' }}>{hs.interaction_diagnosis}</p>}
      {hs.operational_impact && (
        <div style={{ background: 'var(--critical-bg)', borderLeft: '3px solid var(--critical)', padding: '8px 12px', borderRadius: '0 6px 6px 0', fontSize: '12px', color: 'var(--critical)' }}>
          <strong>Impact:</strong> {hs.operational_impact}
        </div>
      )}
    </div>
  );
}

function ChallengeCard({ challenge }: { challenge: VendorChallenge }) {
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)', padding: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={14} color="var(--advisory)" />
          <span className="font-mono" style={{ fontWeight: 600 }}>{challenge.challenge_id}</span>
        </div>
        <span style={{ padding: '2px 8px', background: challenge.priority === 'HIGH' ? 'var(--critical-bg)' : 'var(--watch-bg)', color: challenge.priority === 'HIGH' ? 'var(--critical)' : 'var(--watch)', borderRadius: '4px', fontSize: '10px', fontWeight: 700 }}>
          {challenge.priority}
        </span>
      </div>
      <p className="font-body" style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '6px' }}>{challenge.question}</p>
      <p className="font-body" style={{ fontSize: '12px' }}>{challenge.rationale}</p>
      <div style={{ marginTop: '8px' }}><StratumChips stratumId={challenge.target_stratum_id} /></div>
    </div>
  );
}

function RetestList({ retests }: { retests: RetestRecommendation[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {retests.map((r, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-md)' }}>
          <RotateCcw size={14} color="var(--advisory)" />
          <div style={{ flex: 1 }}>
            <span className="font-mono" style={{ fontSize: '11px', fontWeight: 600 }}>{r.recommendation_id}</span>
            <p className="font-body" style={{ fontSize: '12px', marginTop: '2px' }}>{r.reason}</p>
          </div>
          <StratumChips stratumId={r.target_stratum_id} />
        </div>
      ))}
    </div>
  );
}

function VendorDiagnosticSection({ diag, failureMap }: { diag: DiagnosticReport; failureMap?: VendorFailureMap }) {
  const hotspots: HotspotDiagnosis[] = Array.isArray(diag.compound_hotspot_diagnoses) ? diag.compound_hotspot_diagnoses : [];
  const challenges: VendorChallenge[] = Array.isArray(diag.recommended_vendor_challenges) ? diag.recommended_vendor_challenges : [];
  const retests: RetestRecommendation[] = Array.isArray(diag.targeted_retest_recommendations) ? diag.targeted_retest_recommendations : [];

  return (
    <GlassCard hover={false} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>{diag.display_name ?? diag.vendor_id}</h2>
          <div className="font-mono" style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>{diag.vendor_id}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="font-label">MODE</span>
          <StatusBadge status={diag.analysis_mode ?? 'DETERMINISTIC_FALLBACK'} />
        </div>
      </div>

      {failureMap && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)', padding: '16px 0' }}>
          <div className="metric"><span className="metric-label">ACCURACY</span><span style={{ fontSize: '18px', fontWeight: 700 }}>{failureMap.overall_accuracy != null ? `${(failureMap.overall_accuracy * (failureMap.overall_accuracy <= 1 ? 100 : 1)).toFixed(1)}%` : 'N/A'}</span></div>
          <div className="metric"><span className="metric-label">HOTSPOTS</span><span style={{ fontSize: '18px', fontWeight: 700 }}>{failureMap.hotspots?.length || 0}</span></div>
          <div className="metric"><span className="metric-label">CRITICAL</span><span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--critical)' }}>{failureMap.critical_hotspots_count || 0}</span></div>
          <div className="metric"><span className="metric-label">RETESTS</span><span style={{ fontSize: '18px', fontWeight: 700 }}>{retests.length}</span></div>
        </div>
      )}

      {diag.overall_verdict_explanation && (
        <div><div className="font-label" style={{ marginBottom: '8px' }}>OVERALL ASSESSMENT</div><p className="font-body" style={{ color: 'var(--text-primary)', fontSize: '15px', lineHeight: 1.6 }}>{diag.overall_verdict_explanation}</p></div>
      )}

      {diag.operational_risk_summary && (
        <div style={{ background: 'var(--critical-bg)', borderLeft: '4px solid var(--critical)', padding: '16px', borderRadius: '4px 8px 8px 4px' }}>
          <div className="font-label" style={{ marginBottom: '8px', color: 'var(--critical)', display: 'flex', alignItems: 'center', gap: '6px' }}><ShieldAlert size={14} /> OPERATIONAL RISK SUMMARY</div>
          <p className="font-body" style={{ color: 'var(--critical)', fontWeight: 500 }}>{diag.operational_risk_summary}</p>
        </div>
      )}

      {hotspots.length > 0 && (
        <div><div className="font-label" style={{ marginBottom: '16px' }}>COMPOUND HOTSPOT DIAGNOSES</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '12px' }}>{hotspots.map((hs, i) => <HotspotCard key={i} hs={hs} />)}</div></div>
      )}

      {challenges.length > 0 && (
        <div><div className="font-label" style={{ marginBottom: '16px' }}>RECOMMENDED VENDOR CHALLENGES</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>{challenges.map((c, i) => <ChallengeCard key={i} challenge={c} />)}</div></div>
      )}

      {retests.length > 0 && (
        <div><div className="font-label" style={{ marginBottom: '16px' }}>TARGETED RETEST RECOMMENDATIONS</div><RetestList retests={retests} /></div>
      )}
    </GlassCard>
  );
}

export default function DiagnosticsPage() {
  const { data, loading } = useDemoContext();

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading forensic diagnostics...</p>
        </div>
      </div>
    );
  }

  if (!data) return (<div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}><p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load diagnostic intelligence.</p></div>);

  const diagnosticsList: DiagnosticReport[] = data.diagnostics ?? [];
  const failureMapsList: VendorFailureMap[] = data.failure_maps ?? [];

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '24px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>ADVISORY INTELLIGENCE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}><Brain size={28} color="var(--advisory)" /> Forensic Evaluation Intelligence</h1>
        <p className="font-subheading" style={{ marginTop: '8px', maxWidth: '800px' }}>AI-assisted forensic analysis. Advisory only — does not affect procurement gates.</p>
      </motion.div>

      <motion.div variants={item}>
        <div className="alert alert-advisory" style={{ marginBottom: '32px' }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <div><strong>Advisory Intelligence — Does not authorize procurement.</strong> All procurement decisions are produced by the deterministic governance engine.</div>
        </div>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {diagnosticsList.map((diag) => {
          const fm = failureMapsList.find(f => f.vendor_id === diag.vendor_id);
          return <motion.div key={diag.vendor_id} variants={item}><VendorDiagnosticSection diag={diag} failureMap={fm} /></motion.div>;
        })}
      </div>
    </motion.div>
  );
}