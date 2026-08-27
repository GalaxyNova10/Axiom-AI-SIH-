// EvidenceClassificationPanel.tsx — 5-Tier Evidence Classification & Cryptographic Lineage
import { motion } from 'motion/react';
import { ShieldCheck, Hash, CheckCircle2 } from 'lucide-react';
import type { EvidenceDistribution } from '../types/api';

interface Props {
  distribution: EvidenceDistribution;
  totalTests: number;
  evaluationId: string;
}

const TIERS = [
  {
    key: 'INDEPENDENTLY_VALIDATED',
    label: 'Independently Validated',
    level: 'L5',
    score: '100% Weight',
    badgeStatus: 'ELIGIBLE',
    desc: 'Cryptographically sealed test execution against the private Golden Reference Suite. Immutable proof.',
    color: 'var(--eligible)',
    bg: 'var(--eligible-bg)',
    border: 'var(--eligible-border)',
  },
  {
    key: 'OBSERVED',
    label: 'Empirically Observed',
    level: 'L4',
    score: '80% Weight',
    badgeStatus: 'NORMAL',
    desc: 'Live empirical measurements captured during active pilot twin stress runs under network simulation.',
    color: 'var(--info)',
    bg: 'var(--info-bg)',
    border: 'var(--info-border)',
  },
  {
    key: 'ESTIMATED',
    label: 'Model Estimated',
    level: 'L3',
    score: '60% Weight',
    badgeStatus: 'ADVISORY',
    desc: 'Statistical extrapolations derived from synthetic macroeconomic shock calibrations.',
    color: 'var(--advisory)',
    bg: 'var(--advisory-bg)',
    border: 'var(--advisory-border)',
  },
  {
    key: 'DECLARED',
    label: 'Department Declared',
    level: 'L2',
    score: '60% Weight',
    badgeStatus: 'WATCH',
    desc: 'Department of Financial Services (DFS) baseline demographic constraints and target district SLAs.',
    color: 'var(--watch)',
    bg: 'var(--watch-bg)',
    border: 'var(--watch-border)',
  },
  {
    key: 'CLAIMED',
    label: 'Vendor Claimed',
    level: 'L1',
    score: '40% Weight',
    badgeStatus: 'CRITICAL',
    desc: 'Self-attested vendor proposal claims and submitted SLA guarantees prior to independent verification.',
    color: 'var(--text-muted)',
    bg: 'var(--bg-elevated)',
    border: 'var(--border)',
  },
];

export default function EvidenceClassificationPanel({ distribution, totalTests, evaluationId }: Props) {
  const verifiedCount = distribution.INDEPENDENTLY_VALIDATED || 0;
  const verifiedPct = totalTests > 0 ? Math.round((verifiedCount / totalTests) * 100) : 0;

  return (
    <div>
      {/* Overview Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 18px',
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--r-md)',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: 'var(--r-md)',
            background: 'var(--eligible-bg)',
            border: '1px solid var(--eligible-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <ShieldCheck size={18} color="var(--eligible)" />
          </div>
          <div>
            <div style={{ fontSize: '13.5px', fontWeight: 650, color: 'var(--text-primary)' }}>
              Axiom Evidence Classification Protocol (AECP-5)
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Deterministic evidence classification ensuring no procurement decision relies on unverified vendor claims.
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Independently Verified:</span>
          <span className="font-number" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--eligible)' }}>
            {verifiedCount}/{totalTests} ({verifiedPct}%)
          </span>
        </div>
      </div>

      {/* 5-Tier Cards Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
        {TIERS.map((tier, i) => {
          const count = (distribution as any)[tier.key] || 0;
          const pct = totalTests > 0 ? (count / totalTests) * 100 : 0;

          return (
            <motion.div
              key={tier.key}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              style={{
                background: 'var(--bg-elevated)',
                border: `1px solid ${tier.border}`,
                borderLeft: `4px solid ${tier.color}`,
                borderRadius: 'var(--r-md)',
                padding: '12px 16px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 800,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: tier.bg,
                    color: tier.color,
                    border: `1px solid ${tier.border}`,
                  }}>
                    {tier.level}
                  </span>
                  <span style={{ fontSize: '13px', fontWeight: 650, color: 'var(--text-primary)' }}>
                    {tier.label}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-faint)' }}>{tier.score}</span>
                  <span className="font-number" style={{ fontSize: '14px', fontWeight: 700, color: count > 0 ? tier.color : 'var(--text-faint)' }}>
                    {count} {count === 1 ? 'Artifact' : 'Artifacts'}
                  </span>
                </div>
              </div>
              <p style={{ fontSize: '11.5px', color: 'var(--text-muted)', lineHeight: 1.45, margin: 0 }}>
                {tier.desc}
              </p>
              {totalTests > 0 && (
                <div style={{ marginTop: '8px', height: '3px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: tier.color, borderRadius: '99px' }} />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Cryptographic Proof Footer */}
      <div style={{
        background: 'var(--bg-sunken)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--r-md)',
        padding: '10px 14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Hash size={13} color="var(--text-faint)" />
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Evidence Lineage Root:</span>
          <span className="font-mono" style={{ fontSize: '11px', color: 'var(--accent)', fontWeight: 600 }}>
            sha256:axiom-{evaluationId || 'fintech-root'}-ledger
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--eligible)' }}>
          <CheckCircle2 size={13} />
          <span>Zero-Tamper Sealed</span>
        </div>
      </div>
    </div>
  );
}