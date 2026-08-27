// ============================================================
// Status Badge Component
// ============================================================

import type { Severity, ProcurementDecision } from '../types/api';

type BadgeVariant =
  | ProcurementDecision
  | Severity
  | 'APPROVED'
  | 'OVERRIDE'
  | 'AUTHORIZED'
  | 'PENDING'
  | 'LOCKED'
  | 'ADVISORY'
  | 'LLM'
  | 'DETERMINISTIC_FALLBACK'
  | string;

function getClass(variant: string): string {
  const v = variant.toUpperCase();
  if (v === 'ELIGIBLE' || v === 'NORMAL' || v === 'APPROVED' || v === 'AUTHORIZED') return 'badge-eligible';
  if (v === 'REJECTED') return 'badge-rejected';
  if (v === 'CRITICAL') return 'badge-critical';
  if (v === 'DEGRADED') return 'badge-degraded';
  if (v === 'WATCH') return 'badge-watch';
  if (v === 'PENDING') return 'badge-pending';
  if (v === 'ADVISORY' || v === 'DETERMINISTIC_FALLBACK') return 'badge-advisory';
  if (v === 'LLM') return 'badge-pending';
  if (v === 'OVERRIDE') return 'badge-override';
  if (v === 'LOCKED') return 'badge-locked';
  return 'badge-pending';
}

function getLabel(variant: string): string {
  const v = variant.toUpperCase();
  if (v === 'DETERMINISTIC_FALLBACK') return 'DETERMINISTIC';
  return v;
}

interface StatusBadgeProps {
  status: BadgeVariant;
  dot?: boolean;
}

export default function StatusBadge({ status, dot = false }: StatusBadgeProps) {
  return (
    <span className={`badge ${getClass(status)}`} aria-label={`Status: ${status}`}>
      {dot && (
        <span
          style={{
            width: '6px', height: '6px',
            borderRadius: '50%',
            background: 'currentColor',
            display: 'inline-block',
          }}
          aria-hidden="true"
        />
      )}
      {getLabel(status)}
    </span>
  );
}
