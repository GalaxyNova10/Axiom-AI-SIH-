// ============================================================
// StatusBadge — semantic governance state indicator.
// ALWAYS pair color with a text label for accessibility.
// ============================================================

interface Props {
  status: string;
  dot?: boolean;
  size?: 'sm' | 'md';
}

const MAP: Record<string, string> = {
  eligible: 'badge-eligible',
  approved: 'badge-approved',
  authorized: 'badge-authorized',
  normal: 'badge-normal',
  pass: 'badge-eligible',
  passed: 'badge-eligible',
  completed: 'badge-eligible',
  verified: 'badge-eligible',
  protected: 'badge-eligible',
  visible: 'badge-eligible',
  sanitized: 'badge-eligible',

  rejected: 'badge-rejected',
  critical: 'badge-critical',
  fail: 'badge-rejected',
  failed: 'badge-rejected',
  do_not_scale_yet: 'badge-rejected',
  case_c_critical_failure_match: 'badge-rejected',

  degraded: 'badge-degraded',

  watch: 'badge-watch',
  override: 'badge-override',
  scale_review_required: 'badge-watch',
  revalidation_required: 'badge-watch',

  pending: 'badge-pending',
  locked: 'badge-locked',
  independently_validated: 'badge-locked',
  observed: 'badge-locked',
  declared: 'badge-neutral',
  estimated: 'badge-neutral',
  unverified: 'badge-neutral',

  scale_eligible: 'badge-eligible',
  deterministic_fallback: 'badge-neutral',
  llm: 'badge-advisory',
};

const DOT_MAP: Record<string, string> = {
  eligible: 'dot-eligible', approved: 'dot-eligible', authorized: 'dot-eligible', normal: 'dot-eligible',
  pass: 'dot-eligible', passed: 'dot-eligible', completed: 'dot-eligible', verified: 'dot-eligible',
  protected: 'dot-eligible', scale_eligible: 'dot-eligible',
  rejected: 'dot-critical', critical: 'dot-critical', fail: 'dot-critical', failed: 'dot-critical',
  do_not_scale_yet: 'dot-critical', case_c_critical_failure_match: 'dot-critical',
  degraded: 'dot-degraded',
  watch: 'dot-watch', override: 'dot-watch', scale_review_required: 'dot-watch',
  revalidation_required: 'dot-watch', pending: 'dot-neutral',
};

export default function StatusBadge({ status, dot, size }: Props) {
  const key = (status ?? '').toLowerCase().replace(/\s+/g, '_');
  const cls = MAP[key] ?? 'badge-neutral';
  const dotCls = DOT_MAP[key] ?? 'dot-neutral';
  const label = (status ?? '').replace(/_/g, ' ');
  const sizeClass = size === 'sm' ? 'btn-xs' : '';

  return (
    <span className={`badge ${cls} ${sizeClass}`} role="status" aria-label={label}>
      {dot && <span className={`dot ${dotCls}`} aria-hidden="true" />}
      {label}
    </span>
  );
}
