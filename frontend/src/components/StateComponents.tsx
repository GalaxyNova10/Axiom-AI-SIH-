// ============================================================
// Loading / Error / Empty state components
// ============================================================

import { AlertCircle, RefreshCw, Inbox } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading…' }: LoadingStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '60px 20px', gap: '16px',
      }}
    >
      <div className="spinner" style={{ width: '36px', height: '36px' }} aria-hidden="true" />
      <p style={{ color: '#94a3b8', fontSize: '14px' }}>{message}</p>
    </div>
  );
}

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div
      role="alert"
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '60px 20px', gap: '16px',
      }}
    >
      <AlertCircle size={40} color="#dc2626" aria-hidden="true" />
      <p style={{ color: '#f87171', fontSize: '14px', maxWidth: '500px', textAlign: 'center' }}>
        {message}
      </p>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry} aria-label="Retry loading">
          <RefreshCw size={14} aria-hidden="true" />
          Retry
        </button>
      )}
    </div>
  );
}

interface EmptyStateProps {
  title?: string;
  message?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  title = 'No data yet',
  message = 'Run the canonical demo to populate this view.',
  action,
}: EmptyStateProps) {
  return (
    <div
      style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '60px 20px', gap: '12px',
      }}
    >
      <Inbox size={40} color="#334155" aria-hidden="true" />
      <p style={{ color: '#e2e8f0', fontWeight: 600 }}>{title}</p>
      <p style={{ color: '#64748b', fontSize: '13px', textAlign: 'center', maxWidth: '400px' }}>
        {message}
      </p>
      {action}
    </div>
  );
}
