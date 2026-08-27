// ============================================================
// Axiom AI — Fintech Scale-Up Readiness Analysis
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { ArrowUpRight, Users, Building2, Globe, TrendingUp } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import { getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

export default function ScaleUpPage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
      } catch (err: any) {
        setError(err?.message || 'Failed to load scale-up analysis');
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
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading scale-up analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>
          {error || 'No scale-up data available. Run an evaluation first.'}
        </p>
      </div>
    );
  }

  const isEligible = evaluation.procurement_verdict === 'ELIGIBLE';
  const pilot = evaluation.pilot_twin_parameters;
  const demographics = pilot.demographics;
  const infrastructure = pilot.infrastructure;
  const language = pilot.language_coverage;

  // Calculate scale-up readiness based on evaluation results
  const scaleUpReadiness = {
    infrastructure_readiness: evaluation.pass_rate >= 80 ? 'READY' : 'NEEDS_IMPROVEMENT',
    language_coverage_score: (language.indic_dialects_tested / 12 * 100).toFixed(0),
    device_compatibility: infrastructure.low_end_device_pct >= 50 ? 'HIGH' : 'MEDIUM',
    network_resilience: evaluation.test_results.find(t => t.code === 'INTERMITTENT_2G_UPI_LATENCY')?.passed ? 'VERIFIED' : 'UNVERIFIED',
    rural_deployment_readiness: demographics.rural_borrower_pct >= 70 ? 'HIGH' : 'MEDIUM',
    overall_scale_recommendation: isEligible && evaluation.pass_rate >= 80 ? 'APPROVED_FOR_SCALE' : 'PILOT_ONLY',
  };

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>POST-PILOT ANALYSIS</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ArrowUpRight size={28} color="var(--accent)" /> Scale-Up Evaluation
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Multi-district and nationwide deployment readiness assessment
        </p>
      </motion.div>

      {/* Overall Recommendation */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <GlassCard hover={false} style={{
          borderColor: scaleUpReadiness.overall_scale_recommendation === 'APPROVED_FOR_SCALE' ? 'var(--eligible-border)' : 'var(--watch-border)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <div className="font-label" style={{ marginBottom: '8px' }}>SCALE-UP RECOMMENDATION</div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '4px' }}>
                {scaleUpReadiness.overall_scale_recommendation.replace(/_/g, ' ')}
              </h2>
              <p className="font-body" style={{ color: 'var(--text-secondary)' }}>
                {scaleUpReadiness.overall_scale_recommendation === 'APPROVED_FOR_SCALE'
                  ? 'Model meets all criteria for nationwide DFS deployment'
                  : 'Continue pilot monitoring before scale-up authorization'}
              </p>
            </div>
            <StatusBadge status={scaleUpReadiness.overall_scale_recommendation} size="lg" />
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '16px',
            paddingTop: '16px',
            borderTop: '1px solid var(--border)',
          }}>
            <div className="metric">
              <span className="metric-label">PASS RATE</span>
              <span style={{
                fontSize: '20px',
                fontWeight: 800,
                color: evaluation.pass_rate >= 80 ? 'var(--eligible)' : 'var(--critical)',
              }}>
                {evaluation.pass_rate.toFixed(1)}%
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">CRITICAL FAILURES</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--critical)' }}>
                {evaluation.critical_failures}
              </span>
            </div>
            <div className="metric">
              <span className="metric-label">EVIDENCE CONFIDENCE</span>
              <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--accent)' }}>
                {evaluation.evidence_confidence_score.toFixed(1)}%
              </span>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Readiness Dimensions */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Deployment Readiness Dimensions
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <GlassCard>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Building2 size={18} color="var(--accent)" />
              <span style={{ fontSize: '14px', fontWeight: 650 }}>Infrastructure Readiness</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="font-body">Deployment Status</span>
              <StatusBadge status={scaleUpReadiness.infrastructure_readiness} />
            </div>
          </GlassCard>

          <GlassCard>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Globe size={18} color="var(--accent)" />
              <span style={{ fontSize: '14px', fontWeight: 650 }}>Language Coverage</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="font-body">{language.indic_dialects_tested} Indic Dialects</span>
              <span className="font-number" style={{ fontSize: '18px', fontWeight: 800, color: 'var(--accent)' }}>
                {scaleUpReadiness.language_coverage_score}%
              </span>
            </div>
          </GlassCard>

          <GlassCard>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Users size={18} color="var(--accent)" />
              <span style={{ fontSize: '14px', fontWeight: 650 }}>Device Compatibility</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="font-body">Low-End Support</span>
              <StatusBadge status={scaleUpReadiness.device_compatibility} />
            </div>
          </GlassCard>

          <GlassCard>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <TrendingUp size={18} color="var(--accent)" />
              <span style={{ fontSize: '14px', fontWeight: 650 }}>Network Resilience</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="font-body">2G/3G Testing</span>
              <StatusBadge status={scaleUpReadiness.network_resilience} />
            </div>
          </GlassCard>
        </div>
      </motion.div>

      {/* Pilot Twin Demographics */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Pilot Twin Demographics
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
          <GlassCard hover={false}>
            <div className="metric">
              <span className="metric-label">RURAL BORROWERS</span>
              <span style={{ fontSize: '22px', fontWeight: 800, color: 'var(--accent)' }}>
                {demographics.rural_borrower_pct}%
              </span>
            </div>
          </GlassCard>
          <GlassCard hover={false}>
            <div className="metric">
              <span className="metric-label">THIN-FILE UNBANKED</span>
              <span style={{ fontSize: '22px', fontWeight: 800, color: 'var(--accent)' }}>
                {demographics.unbanked_thin_file_pct}%
              </span>
            </div>
          </GlassCard>
          <GlassCard hover={false}>
            <div className="metric">
              <span className="metric-label">FEMALE BORROWERS</span>
              <span style={{ fontSize: '22px', fontWeight: 800, color: 'var(--accent)' }}>
                {demographics.female_borrower_pct}%
              </span>
            </div>
          </GlassCard>
        </div>
      </motion.div>

      {/* Infrastructure Profile */}
      <motion.div variants={item}>
        <h3 style={{ fontSize: '16px', fontWeight: 650, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Infrastructure Profile
        </h3>
        <GlassCard hover={false}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '20px',
          }}>
            <div>
              <div className="font-label" style={{ marginBottom: '8px' }}>2G/3G CONNECTIVITY</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span className="font-number" style={{ fontSize: '28px', fontWeight: 800, color: 'var(--accent)' }}>
                  {infrastructure.connectivity_2g_3g_pct}
                </span>
                <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>%</span>
              </div>
              <p className="font-body" style={{ fontSize: '12px', marginTop: '4px' }}>
                of pilot deployment areas
              </p>
            </div>

            <div>
              <div className="font-label" style={{ marginBottom: '8px' }}>LOW-END DEVICES</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span className="font-number" style={{ fontSize: '28px', fontWeight: 800, color: 'var(--accent)' }}>
                  {infrastructure.low_end_device_pct}
                </span>
                <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>%</span>
              </div>
              <p className="font-body" style={{ fontSize: '12px', marginTop: '4px' }}>
                ≤2GB RAM Android devices
              </p>
            </div>

            <div>
              <div className="font-label" style={{ marginBottom: '8px' }}>OFFLINE KIOSKS</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span className="font-number" style={{ fontSize: '28px', fontWeight: 800, color: 'var(--accent)' }}>
                  {infrastructure.offline_kiosk_pct}
                </span>
                <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>%</span>
              </div>
              <p className="font-body" style={{ fontSize: '12px', marginTop: '4px' }}>
                CSC/BC offline origination
              </p>
            </div>
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}
