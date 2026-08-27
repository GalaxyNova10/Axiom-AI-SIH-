// ============================================================
// Axiom AI — Human Authorization & Procurement Approval
// ============================================================
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import { getLatestFintechEvaluation } from '../services/api';
import type { FintechEvaluationResult } from '../types/api';

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 14 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } };

export default function AuthorizationPage() {
  const [evaluation, setEvaluation] = useState<FintechEvaluationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [officerId, setOfficerId] = useState('DFS-OFFICER-001');
  const [humanDecision, setHumanDecision] = useState<'APPROVE' | 'REJECT' | 'REQUEST_RETEST'>('APPROVE');
  const [justification, setJustification] = useState('');
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const latest = await getLatestFintechEvaluation();
        setEvaluation(latest);
        // Pre-populate justification based on verdict
        if (latest.procurement_verdict === 'ELIGIBLE') {
          setJustification('All critical tests passed. Evidence confidence exceeds minimum threshold. Model meets DFS deployment requirements.');
          setHumanDecision('APPROVE');
        } else {
          setJustification('Critical test failures detected. Model does not meet minimum requirements for procurement at this time.');
          setHumanDecision('REJECT');
        }
      } catch (err: any) {
        setError(err?.message || 'Failed to load authorization data');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSubmit = () => {
    if (!justification.trim() || !officerId.trim()) {
      setError('Officer ID and justification are required');
      return;
    }
    setSubmitted(true);
    setError(null);
  };

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: '32px', height: '32px', marginBottom: '16px' }} />
          <p className="font-subheading" style={{ color: 'var(--text-secondary)' }}>Loading authorization...</p>
        </div>
      </div>
    );
  }

  if (error && !evaluation) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>
          {error || 'No authorization data available. Run an evaluation first.'}
        </p>
      </div>
    );
  }

  const isEligible = evaluation?.procurement_verdict === 'ELIGIBLE';

  return (
    <motion.div className="page" variants={container} initial="hidden" animate="visible">
      {/* Header */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>HUMAN-IN-THE-LOOP GOVERNANCE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ShieldCheck size={28} color="var(--accent)" /> Human Authorization
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Final human oversight and procurement approval decision
        </p>
      </motion.div>

      {/* Advisory Banner */}
      <motion.div variants={item} style={{ marginBottom: '28px' }}>
        <div className="alert alert-advisory">
          <AlertTriangle size={16} style={{ flexShrink: 0 }} />
          <div>
            <strong>No autonomous action.</strong> All procurement decisions require explicit human authorization
            with written justification. AI provides advisory intelligence only.
          </div>
        </div>
      </motion.div>

      {evaluation && (
        <>
          {/* AI Recommendation */}
          <motion.div variants={item} style={{ marginBottom: '28px' }}>
            <GlassCard hover={false} style={{
              borderColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div className="font-label" style={{ marginBottom: '8px' }}>AI PROCUREMENT RECOMMENDATION</div>
                  <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {isEligible ? (
                      <><CheckCircle2 size={24} color="var(--eligible)" /> ELIGIBLE FOR PROCUREMENT</>
                    ) : (
                      <><XCircle size={24} color="var(--critical)" /> REJECTED</>
                    )}
                  </h2>
                </div>
                <StatusBadge status={evaluation.procurement_verdict} size="lg" />
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '16px',
                paddingTop: '16px',
                borderTop: '1px solid var(--border)',
                marginBottom: '16px',
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

              <div>
                <div className="font-label" style={{ marginBottom: '8px' }}>VERDICT REASONING</div>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  {evaluation.verdict_reasons.map((reason, idx) => (
                    <li key={idx} className="font-body" style={{
                      marginBottom: '6px',
                      color: reason.includes('passed') || reason.includes('exceeds') ? 'var(--eligible)' : 'var(--critical)',
                    }}>
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            </GlassCard>
          </motion.div>

          {/* Human Decision Form */}
          {!submitted ? (
            <motion.div variants={item}>
              <GlassCard hover={false}>
                <div className="card-header">
                  <span style={{ fontWeight: 650 }}>Submit Human Authorization Decision</span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div>
                    <div className="font-label" style={{ marginBottom: '8px' }}>AUTHORIZING OFFICER ID</div>
                    <input
                      type="text"
                      value={officerId}
                      onChange={(e) => setOfficerId(e.target.value)}
                      placeholder="e.g., DFS-OFFICER-001"
                      style={{
                        width: '100%',
                        padding: '12px 14px',
                        borderRadius: 'var(--r-md)',
                        border: '1px solid var(--border-strong)',
                        background: 'var(--bg-elevated)',
                        color: 'var(--text-primary)',
                        fontSize: '14px',
                        fontFamily: 'inherit',
                        outline: 'none',
                      }}
                    />
                  </div>

                  <div>
                    <div className="font-label" style={{ marginBottom: '8px' }}>HUMAN DECISION</div>
                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                      <button
                        onClick={() => setHumanDecision('APPROVE')}
                        className={`btn ${humanDecision === 'APPROVE' ? 'btn-accent' : 'btn-secondary'}`}
                      >
                        <CheckCircle2 size={14} /> Approve
                      </button>
                      <button
                        onClick={() => setHumanDecision('REJECT')}
                        className={`btn ${humanDecision === 'REJECT' ? 'btn-danger' : 'btn-secondary'}`}
                      >
                        <XCircle size={14} /> Reject
                      </button>
                      <button
                        onClick={() => setHumanDecision('REQUEST_RETEST')}
                        className={`btn ${humanDecision === 'REQUEST_RETEST' ? 'btn-primary' : 'btn-secondary'}`}
                      >
                        Request Retest
                      </button>
                    </div>
                  </div>

                  <div>
                    <div className="font-label" style={{ marginBottom: '8px' }}>JUSTIFICATION (REQUIRED)</div>
                    <textarea
                      value={justification}
                      onChange={(e) => setJustification(e.target.value)}
                      placeholder="Provide written justification for this authorization decision..."
                      rows={4}
                      style={{
                        width: '100%',
                        padding: '12px 14px',
                        borderRadius: 'var(--r-md)',
                        border: '1px solid var(--border-strong)',
                        background: 'var(--bg-elevated)',
                        color: 'var(--text-primary)',
                        fontSize: '14px',
                        fontFamily: 'inherit',
                        outline: 'none',
                        resize: 'vertical',
                      }}
                    />
                  </div>

                  {error && (
                    <div className="alert alert-error">
                      <AlertTriangle size={14} /> {error}
                    </div>
                  )}

                  <button
                    onClick={handleSubmit}
                    className="btn btn-accent btn-lg"
                    style={{ width: 'fit-content' }}
                  >
                    <ShieldCheck size={16} /> Submit Authorization
                  </button>
                </div>
              </GlassCard>
            </motion.div>
          ) : (
            <motion.div variants={item}>
              <GlassCard hover={false} style={{ borderColor: 'var(--eligible-border)' }}>
                <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                  <div style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'var(--eligible-bg)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                  }}>
                    <CheckCircle2 size={32} color="var(--eligible)" />
                  </div>
                  <h3 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
                    Authorization Submitted
                  </h3>
                  <p className="font-body" style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                    Human decision <strong>{humanDecision}</strong> recorded by officer <strong>{officerId}</strong>
                  </p>
                  <div style={{
                    background: 'var(--bg-elevated)',
                    padding: '16px',
                    borderRadius: 'var(--r-md)',
                    border: '1px solid var(--border)',
                    textAlign: 'left',
                  }}>
                    <div className="font-label" style={{ marginBottom: '6px' }}>JUSTIFICATION</div>
                    <p className="font-body" style={{ fontSize: '13px', lineHeight: 1.5 }}>
                      {justification}
                    </p>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </>
      )}
    </motion.div>
  );
}
