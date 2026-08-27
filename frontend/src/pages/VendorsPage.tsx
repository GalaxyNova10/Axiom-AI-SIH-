import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import GlassCard from '../components/GlassCard';
import VendorRadarCompare from '../components/charts/VendorRadarChart';
import AccuracyBarChart from '../components/charts/AccuracyBarChart';
import { ChevronRight, BarChart2, Cpu, ShieldCheck, Sparkles } from 'lucide-react';
import type { VendorScorecard, VendorFailureMap } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } };

// Friendly fintech vendor metadata overrides
const FINTECH_VENDOR_NAMES: Record<string, { name: string; type: string; desc: string }> = {
  VendorA: {
    name: 'FinScore Enterprise',
    type: 'Legacy Rule-Based + XGBoost Scorer',
    desc: 'High standard bureau accuracy, but acute degradation under thin-file rural & 2G network constraints.',
  },
  VendorB: {
    name: 'CredVeda AI (Selected Startup)',
    type: 'Multimodal LLM + GNN Risk Ensemble',
    desc: 'Offline-first resilient engine for vernacular MSME credit underwriting across 12 Indic regional dialects.',
  },
  VendorC: {
    name: 'IndicPay Neural',
    type: 'Deep Learning Speech & OCR Specialist',
    desc: 'High baseline speech benchmark, but suffers compound failure under low-end hardware + noisy input.',
  },
};

export default function VendorsPage() {
  const { data, loading } = useDemoContext();
  const navigate = useNavigate();
  const evalId = data?.vendors?.[0]?.evaluation_id ?? 'demo';

  if (loading && !data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading fintech model scorecards...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p className="font-subheading">Run the canonical demo to load model scorecards.</p>
        </div>
      </div>
    );
  }

  const vendorsList: VendorScorecard[] = data.vendors ?? [];
  const failureMapsList: VendorFailureMap[] = data.failure_maps ?? [];
  const procurement = data.procurement ?? {};

  // Augment display names for fintech presentation
  const enhancedVendors = vendorsList.map(v => {
    const meta = FINTECH_VENDOR_NAMES[v.vendor_id];
    return {
      ...v,
      display_name: meta ? meta.name : v.display_name,
      description: meta ? meta.desc : v.description,
    };
  });

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      <motion.div variants={item} style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>FINTECH MODEL BENCHMARKING</div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Cpu size={28} color="var(--accent)" /> Fintech Model Scorecards
            </h1>
            <p className="font-subheading" style={{ marginTop: '8px' }}>
              Comparative evaluation of MSME credit risk models under Department of Financial Services (DFS) sandbox conditions.
            </p>
          </div>
          <span style={{
            fontSize: '11px',
            fontWeight: 700,
            padding: '4px 10px',
            borderRadius: '4px',
            background: 'var(--accent-muted)',
            color: 'var(--accent)',
            border: '1px solid var(--accent)',
          }}>
            DFS SCHEME: PM SVANidhi & MUDRA
          </span>
        </div>
      </motion.div>

      {/* Charts Row */}
      <motion.div variants={item} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <GlassCard delay={0.05}>
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={16} color="var(--accent)" /> Multi-Axis Fintech Capability Radar
            </span>
          </div>
          <VendorRadarCompare vendors={enhancedVendors} />
        </GlassCard>
        <GlassCard delay={0.1}>
          <div className="card-header">
            <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BarChart2 size={16} color="var(--eligible)" /> 15-Test Stress Accuracy Ranking
            </span>
          </div>
          <AccuracyBarChart vendors={enhancedVendors} />
        </GlassCard>
      </motion.div>

      {/* Model Cards Table */}
      <motion.div variants={item}>
        <GlassCard hover={false} style={{ padding: 0, overflow: 'hidden' }}>
          <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
            <span style={{ fontWeight: 700, fontSize: '15px' }}>Government Sandbox Model Leaderboard</span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Target District: DFS Tier-3/4 Pilot Hub</span>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="ax-table">
              <thead>
                <tr>
                  <th>Model / Startup</th>
                  <th>Tested Accuracy</th>
                  <th>P99 Latency</th>
                  <th>Evidence Level</th>
                  <th>Confidence</th>
                  <th>Failure Status</th>
                  <th>Hotspots</th>
                  <th>DFS Eligibility</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {enhancedVendors.map(v => {
                  const procDecision = procurement[v.vendor_id]?.decision ?? v.procurement_recommendation ?? 'PENDING';
                  const fm = failureMapsList.find(f => f.vendor_id === v.vendor_id);
                  const isStartup = v.vendor_id === 'VendorB';

                  return (
                    <tr
                      key={v.vendor_id}
                      onClick={() => navigate(`/evaluation/${evalId}/vendors/${v.vendor_id}`)}
                      style={{
                        cursor: 'pointer',
                        background: isStartup ? 'rgba(6, 182, 212, 0.04)' : undefined,
                      }}
                    >
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '14px', color: isStartup ? 'var(--accent)' : 'var(--text-primary)' }}>
                              {v.display_name}
                            </div>
                            <div className="font-caption" style={{ marginTop: '2px', maxWidth: '280px', lineHeight: 1.3 }}>
                              {v.description}
                            </div>
                          </div>
                          {isStartup && (
                            <span style={{
                              fontSize: '9px',
                              fontWeight: 800,
                              background: 'var(--eligible-bg)',
                              color: 'var(--eligible)',
                              padding: '2px 6px',
                              borderRadius: '4px',
                              border: '1px solid var(--eligible-border)',
                              flexShrink: 0,
                            }}>
                              SELECTED
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className="font-number" style={{ fontWeight: 750, fontSize: '14px', color: (v.accuracy ?? 0) < 80 ? 'var(--critical)' : 'var(--eligible)' }}>
                          {v.accuracy != null ? `${v.accuracy.toFixed(1)}%` : '\u2014'}
                        </span>
                      </td>
                      <td className="font-number">{v.latency != null ? `${v.latency.toFixed(0)} ms` : '\u2014'}</td>
                      <td><span className="font-caption" style={{ fontWeight: 600, color: 'var(--eligible)' }}>L5 Sealed</span></td>
                      <td className="font-number" style={{ fontWeight: 700, color: 'var(--accent)' }}>
                        {v.evidence_confidence != null ? `${v.evidence_confidence.toFixed(1)}%` : '\u2014'}
                      </td>
                      <td><StatusBadge status={fm?.overall_status ?? v.overall_status ?? 'NORMAL'} dot /></td>
                      <td>
                        <span style={{ fontWeight: 700, color: (fm?.critical_hotspots_count ?? 0) > 0 ? 'var(--critical)' : 'var(--eligible)' }} className="font-number">
                          {fm?.critical_hotspots_count ?? 0}
                        </span>
                      </td>
                      <td><StatusBadge status={procDecision} /></td>
                      <td style={{ color: 'var(--text-faint)' }}><ChevronRight size={16} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}