// EvidenceConfidenceGauge.tsx — Animated radial gauge for Evidence Confidence Score
import { motion } from 'motion/react';
import AnimatedNumber from './AnimatedNumber';
import type { EvidenceConfidenceBreakdown } from '../types/api';

interface Props {
  score: number;
  breakdown: EvidenceConfidenceBreakdown | Record<string, number>;
}

const WEIGHT_LABELS: Record<string, string> = {
  evaluator_integrity: 'Evaluator Integrity',
  contract_integrity: 'Contract Integrity',
  artifact_integrity: 'Artifact Integrity',
  test_coverage: '15-Test Coverage',
  pilot_twin_evidence: 'Pilot Twin Fidelity',
  measurement_quality: 'Measurement Quality',
};
const WEIGHTS: Record<string, number> = {
  evaluator_integrity: 0.20, contract_integrity: 0.20,
  artifact_integrity: 0.15, test_coverage: 0.15,
  pilot_twin_evidence: 0.15, measurement_quality: 0.15,
};

function ScoreGauge({ score }: { score: number }) {
  const r = 54;
  const circ = 2 * Math.PI * r;
  const color = score >= 80 ? 'var(--eligible)' : score >= 60 ? 'var(--watch)' : 'var(--critical)';
  return (
    <div style={{ position: 'relative', width: '140px', height: '140px', flexShrink: 0 }}>
      <svg width="140" height="140" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="70" cy="70" r={r} fill="none" stroke="var(--bg-elevated)" strokeWidth="10" />
        <motion.circle
          cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ * (1 - score / 100) }}
          transition={{ duration: 1.2, delay: 0.3 }}
        />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <AnimatedNumber value={score} decimals={1} suffix="%" style={{ fontSize: '22px', fontWeight: 800, color, letterSpacing: '-0.03em' }} />
        <span style={{ fontSize: '9px', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-faint)', marginTop: '2px' }}>Confidence</span>
      </div>
    </div>
  );
}

export default function EvidenceConfidenceGauge({ score, breakdown }: Props) {
  const bd = breakdown as Record<string, number>;
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <ScoreGauge score={score} />
        <div style={{ flex: 1, minWidth: '200px' }}>
          <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Multi-factor cryptographic confidence score measuring the trustworthiness of all evidence generated during the 15-point stress evaluation.
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {Object.keys(WEIGHT_LABELS).map(key => {
          const val = bd[key] ?? 0;
          const weight = WEIGHTS[key];
          const barColor = val >= 80 ? 'var(--eligible)' : val >= 60 ? 'var(--watch)' : 'var(--critical)';
          return (
            <div key={key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>{WEIGHT_LABELS[key]}</span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ fontSize: '10px', color: 'var(--text-faint)' }}>{(weight * 100).toFixed(0)}% weight</span>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: barColor, minWidth: '36px', textAlign: 'right' }}>{val.toFixed(1)}</span>
                </div>
              </div>
              <div style={{ height: '6px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${val}%` }}
                  transition={{ duration: 0.8, delay: 0.1 }}
                  style={{ height: '100%', background: barColor, borderRadius: '99px', opacity: 0.85 }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}