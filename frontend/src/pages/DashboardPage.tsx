// ============================================================
// Axiom AI — Fintech Model Evaluation Hub (DashboardPage)
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import {
  PlusCircle, Hexagon, Shield,
  Layers, RefreshCw, AlertTriangle,
  Landmark, Cpu, FileCheck,
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import AnimatedNumber from '../components/AnimatedNumber';
import StartupLifecycleStepper from '../components/StartupLifecycleStepper';
import StartupInputModal from '../components/StartupInputModal';
import Fintech15TestMatrix from '../components/Fintech15TestMatrix';
import GovernmentPilotTwinCard from '../components/GovernmentPilotTwinCard';
import EvidenceConfidenceGauge from '../components/EvidenceConfidenceGauge';
import EvidenceClassificationPanel from '../components/EvidenceClassificationPanel';
import { runFintechEvaluation, getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult, FintechStartupInput } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

export default function DashboardPage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeStage, setActiveStage] = useState(3);

  // Auto-load latest evaluation on mount if available, or load default preset
  useEffect(() => {
    async function init() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
      } catch {
        // Run canonical evaluation by default
        handleRunDefault();
      }
    }
    init();
  }, []);

  const handleRunDefault = async () => {
    setLoading(true);
    setError(null);
    try {
      const preset: FintechStartupInput = {
        startup_name: 'CredVeda AI',
        model_name: 'Vernacular MSME Underwriting & Credit Risk Engine',
        department: 'Department of Financial Services',
        district: 'DFS Digital Finance Pilot District (Tier-3/4)',
        claimed_accuracy: 94.5,
        seed: 42,
      };
      const res = await runFintechEvaluation(preset);
      setEvaluation(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to execute fintech evaluation.');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomSubmit = async (input: FintechStartupInput) => {
    setLoading(true);
    setError(null);
    try {
      const res = await runFintechEvaluation(input);
      setEvaluation(res);
    } catch (err: any) {
      setError(err?.message || 'Evaluation failed.');
    } finally {
      setLoading(false);
    }
  };

  const isEligible = evaluation?.procurement_verdict === 'ELIGIBLE';

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Top Hero Banner */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: 'var(--r-md)',
                background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'var(--accent-glow)',
              }}>
                <Hexagon size={18} color="white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="font-label" style={{ marginBottom: '1px' }}>EVIDENCE-GATED FINTECH GOVERNANCE</div>
                <h1 style={{
                  fontSize: '26px',
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  lineHeight: 1.15,
                  background: 'linear-gradient(135deg, var(--text-primary) 0%, var(--accent) 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>
                  Fintech Model Evaluation Sandbox
                </h1>
              </div>
            </div>
            <p className="font-subheading" style={{ maxWidth: '650px', fontSize: '13.5px', marginTop: '4px' }}>
              Government Pilot Twin stress-testing engine evaluating vernacular MSME credit underwriting across 15 real-world DPI conditions.
            </p>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => setIsModalOpen(true)}
              className="btn btn-secondary"
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <PlusCircle size={15} color="var(--accent)" /> Submit Startup Plan
            </button>
            <button
              onClick={handleRunDefault}
              disabled={loading}
              className="btn btn-accent"
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              {loading ? (
                <>
                  <span className="spinner" style={{ width: '14px', height: '14px' }} />
                  Running 15 Tests...
                </>
              ) : (
                <>
                  <RefreshCw size={14} /> Re-Run 15 Tests
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '20px' }}>
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* Startup Lifecycle Stepper */}
      <motion.div variants={item}>
        <StartupLifecycleStepper
          activeStage={activeStage}
          onStageClick={(id) => setActiveStage(id)}
          isEvaluated={!!evaluation}
        />
      </motion.div>

      {/* Main Content when Evaluation Available */}
      {evaluation && (
        <>
          {/* Active Model Summary Strip */}
          <motion.div variants={item} style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '14px 20px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--r-lg)',
            marginBottom: '24px',
            flexWrap: 'wrap',
            gap: '12px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--r-md)',
                background: 'var(--bg-sunken)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Cpu size={16} color="var(--accent)" />
              </div>
              <div>
                <div style={{ fontSize: '15px', fontWeight: 750, color: 'var(--text-primary)' }}>
                  {evaluation.startup_name} · <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{evaluation.model_name}</span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Target: {evaluation.department} · {evaluation.district}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ textAlign: 'right' }}>
                <span className="font-label">Verdict</span>
                <div style={{ marginTop: '2px' }}>
                  <StatusBadge status={evaluation.procurement_verdict} />
                </div>
              </div>
            </div>
          </motion.div>

          {/* Top KPI Bento Grid */}
          <motion.div variants={item} style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '14px',
            marginBottom: '28px',
          }}>
            {/* Accuracy */}
            <GlassCard delay={0} style={{ padding: '18px' }}>
              <div className="metric">
                <span className="metric-label">Tested Accuracy</span>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '4px' }}>
                  <AnimatedNumber
                    value={evaluation.overall_accuracy}
                    decimals={1}
                    suffix="%"
                    className="metric-value font-number"
                    style={{ color: evaluation.overall_accuracy >= 80 ? 'var(--eligible)' : 'var(--critical)' }}
                  />
                  <span style={{ fontSize: '11px', color: 'var(--text-faint)' }}>claimed 94.5%</span>
                </div>
                <span className="metric-sub">Mean across 15 stress conditions</span>
              </div>
            </GlassCard>

            {/* Evidence Confidence */}
            <GlassCard delay={0.04} style={{ padding: '18px' }}>
              <div className="metric">
                <span className="metric-label" style={{ color: 'var(--accent)' }}>Confidence Score</span>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', marginTop: '4px' }}>
                  <AnimatedNumber
                    value={evaluation.evidence_confidence_score}
                    decimals={1}
                    suffix="%"
                    className="metric-value font-number"
                    style={{ color: 'var(--accent)' }}
                  />
                </div>
                <span className="metric-sub">6-factor cryptographic index</span>
              </div>
            </GlassCard>

            {/* 15-Test Pass Rate */}
            <GlassCard delay={0.08} style={{ padding: '18px' }}>
              <div className="metric">
                <span className="metric-label">15-Test Pass Rate</span>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginTop: '4px' }}>
                  <span className="metric-value font-number">
                    {evaluation.passed_tests}/{evaluation.total_tests}
                  </span>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    ({evaluation.pass_rate.toFixed(0)}%)
                  </span>
                </div>
                <span className="metric-sub">SLA & Accuracy thresholds</span>
              </div>
            </GlassCard>

            {/* Critical Failures */}
            <GlassCard delay={0.12} style={{ padding: '18px', borderColor: evaluation.critical_failures > 0 ? 'var(--critical-border)' : undefined }}>
              <div className="metric">
                <span className="metric-label" style={{ color: evaluation.critical_failures > 0 ? 'var(--critical)' : 'var(--text-faint)' }}>
                  Critical Hotspots
                </span>
                <div style={{ marginTop: '4px' }}>
                  <span className="metric-value font-number" style={{ color: evaluation.critical_failures > 0 ? 'var(--critical)' : 'var(--eligible)' }}>
                    {evaluation.critical_failures}
                  </span>
                </div>
                <span className="metric-sub">Automatic gate blockers</span>
              </div>
            </GlassCard>

            {/* Gate Status */}
            <GlassCard delay={0.16} style={{ padding: '18px' }}>
              <div className="metric">
                <span className="metric-label">Procurement Gate</span>
                <div style={{ marginTop: '8px' }}>
                  <span style={{
                    fontSize: '13px',
                    fontWeight: 800,
                    padding: '4px 10px',
                    borderRadius: 'var(--r-full)',
                    background: isEligible ? 'var(--eligible-bg)' : 'var(--critical-bg)',
                    color: isEligible ? 'var(--eligible)' : 'var(--critical)',
                    border: `1px solid ${isEligible ? 'var(--eligible-border)' : 'var(--critical-border)'}`,
                  }}>
                    {evaluation.procurement_verdict}
                  </span>
                </div>
                <span className="metric-sub">Deterministic calculation</span>
              </div>
            </GlassCard>
          </motion.div>

          {/* Section 1: 15-Point Stress Test Grid */}
          <motion.div variants={item} style={{ marginBottom: '32px' }}>
            <GlassCard hover={false}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Layers size={16} color="var(--accent)" />
                  <span style={{ fontWeight: 700, fontSize: '15px' }}>15-Point Government Stress Test Matrix</span>
                </div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  Evaluator Seed: <span className="font-mono">42</span>
                </span>
              </div>
              <Fintech15TestMatrix tests={evaluation.test_results} />
            </GlassCard>
          </motion.div>

          {/* Section 2: Twin Sandbox + Confidence Gauge (Side by Side) */}
          <motion.div variants={item} style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
            gap: '20px',
            marginBottom: '32px',
          }}>
            {/* Government Pilot Twin Card */}
            <GlassCard hover={false}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Landmark size={16} color="var(--accent)" />
                  <span style={{ fontWeight: 700, fontSize: '15px' }}>Government Pilot Twin (DFS Sandbox)</span>
                </div>
              </div>
              <GovernmentPilotTwinCard pilotTwin={evaluation.pilot_twin_parameters} />
            </GlassCard>

            {/* Evidence Confidence Gauge */}
            <GlassCard hover={false}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Shield size={16} color="var(--eligible)" />
                  <span style={{ fontWeight: 700, fontSize: '15px' }}>Evidence Confidence Score Breakdown</span>
                </div>
              </div>
              <EvidenceConfidenceGauge
                score={evaluation.evidence_confidence_score}
                breakdown={evaluation.evidence_confidence_breakdown}
              />
            </GlassCard>
          </motion.div>

          {/* Section 3: Evidence Generation & Classification Protocol */}
          <motion.div variants={item} style={{ marginBottom: '32px' }}>
            <GlassCard hover={false}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <FileCheck size={16} color="var(--eligible)" />
                  <span style={{ fontWeight: 700, fontSize: '15px' }}>Evidence Generation & 5-Tier Classification Ledger</span>
                </div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AECP-5 Verified</span>
              </div>
              <EvidenceClassificationPanel
                distribution={evaluation.evidence_distribution}
                totalTests={evaluation.total_tests}
                evaluationId={evaluation.evaluation_id}
              />
            </GlassCard>
          </motion.div>
        </>
      )}

      {/* Startup Input Modal */}
      <StartupInputModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCustomSubmit}
        isLoading={loading}
      />
    </motion.div>
  );
}