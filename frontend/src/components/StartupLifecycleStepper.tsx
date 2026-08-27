// StartupLifecycleStepper.tsx — Interactive 8-Stage Startup Procurement Lifecycle Tracker
import { motion } from 'motion/react';
import {
  FileText, Landmark, PlayCircle, ShieldCheck,
  Award, Map, Gavel, CheckCircle,
} from 'lucide-react';

export const LIFECYCLE_STAGES = [
  { id: 1, key: 'INTAKE', label: '1. Plan Intake', icon: FileText, desc: 'Startup submits model specs, architecture, & claimed SLAs.' },
  { id: 2, key: 'TWIN', label: '2. Sandbox Twin', icon: Landmark, desc: 'DFS Pilot Twin calibrates real-world rural demographic stresses.' },
  { id: 3, key: 'TESTING', label: '3. 15-Test Matrix', icon: PlayCircle, desc: 'Automated 15-point stress battery execution.' },
  { id: 4, key: 'EVIDENCE', label: '4. Evidence Gen', icon: ShieldCheck, desc: 'Artifact generation and 5-tier cryptographic classification.' },
  { id: 5, key: 'CONFIDENCE', label: '5. Confidence Score', icon: Award, desc: 'Multi-factor mathematical reliability calculation.' },
  { id: 6, key: 'CARTOGRAPHY', label: '6. Failure Map', icon: Map, desc: 'Forensic failure hotspot and compound risk cartography.' },
  { id: 7, key: 'GATE', label: '7. Gate Verdict', icon: Gavel, desc: 'Deterministic procurement eligibility evaluation.' },
  { id: 8, key: 'SCALE', label: '8. Authorization', icon: CheckCircle, desc: 'Human maker-checker signoff and graduated scale-up policy.' },
];

interface Props {
  activeStage?: number;
  onStageClick?: (stageId: number) => void;
  isEvaluated?: boolean;
}

export default function StartupLifecycleStepper({ activeStage = 3, onStageClick, isEvaluated = false }: Props) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-lg)',
      padding: '16px 20px',
      marginBottom: '24px',
      overflowX: 'auto',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-faint)' }}>
            STARTUP PROCUREMENT LIFECYCLE
          </span>
          <span style={{
            fontSize: '10px',
            fontWeight: 700,
            padding: '2px 6px',
            borderRadius: '4px',
            background: isEvaluated ? 'var(--eligible-bg)' : 'var(--accent-muted)',
            color: isEvaluated ? 'var(--eligible)' : 'var(--accent)',
          }}>
            {isEvaluated ? 'EVALUATED' : 'READY TO RUN'}
          </span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          {isEvaluated ? 'All 8 governance checkpoints executed' : 'Click stage to inspect checkpoint'}
        </span>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        minWidth: '780px',
        position: 'relative',
      }}>
        {LIFECYCLE_STAGES.map((stage, idx) => {
          const isPassed = isEvaluated;
          const isActive = stage.id === activeStage;
          const Icon = stage.icon;

          return (
            <div key={stage.id} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              <motion.button
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => onStageClick?.(stage.id)}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '10px 8px',
                  borderRadius: 'var(--r-md)',
                  background: isActive ? 'var(--accent-muted)' : isPassed ? 'var(--bg-elevated)' : 'transparent',
                  border: isActive
                    ? '1px solid var(--accent)'
                    : isPassed
                    ? '1px solid var(--border-strong)'
                    : '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                  position: 'relative',
                }}
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: isPassed
                    ? 'var(--eligible-bg)'
                    : isActive
                    ? 'var(--accent)'
                    : 'var(--bg-sunken)',
                  border: isPassed
                    ? '1px solid var(--eligible-border)'
                    : isActive
                    ? 'none'
                    : '1px solid var(--border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '6px',
                }}>
                  <Icon
                    size={14}
                    color={
                      isPassed
                        ? 'var(--eligible)'
                        : isActive
                        ? 'var(--text-inverted)'
                        : 'var(--text-muted)'
                    }
                  />
                </div>
                <span style={{
                  fontSize: '11px',
                  fontWeight: isActive ? 750 : 600,
                  color: isActive
                    ? 'var(--accent-hover)'
                    : isPassed
                    ? 'var(--text-primary)'
                    : 'var(--text-muted)',
                  whiteSpace: 'nowrap',
                }}>
                  {stage.label}
                </span>
                <span style={{
                  fontSize: '9.5px',
                  color: 'var(--text-faint)',
                  lineHeight: 1.2,
                  marginTop: '3px',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  textAlign: 'center',
                }}>
                  {stage.desc}
                </span>
              </motion.button>

              {idx < LIFECYCLE_STAGES.length - 1 && (
                <div style={{
                  width: '12px',
                  height: '2px',
                  background: isPassed ? 'var(--eligible)' : 'var(--border)',
                  margin: '0 2px',
                  flexShrink: 0,
                  opacity: isPassed ? 0.6 : 0.3,
                }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}