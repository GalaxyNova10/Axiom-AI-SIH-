import { AlertCircle, Loader2 } from 'lucide-react';

export function LoadingState({ message = 'Loading evaluation data...' }: { message?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', gap: '16px' }}>
      <Loader2 size={32} className="spinner" style={{ color: 'var(--accent)', animation: 'spin 1s linear infinite' }} />
      <div style={{ color: 'var(--text-muted)', fontSize: '14px', fontWeight: 500 }}>{message}</div>
    </div>
  );
}

export function ErrorState({ title = 'Error', message, onRetry }: { title?: string; message: string; onRetry?: () => void }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
      <div className="card" style={{ maxWidth: '400px', width: '100%', borderColor: 'var(--critical-border)', textAlign: 'center', padding: 'var(--s8)' }}>
        <AlertCircle size={32} color="var(--critical)" style={{ margin: '0 auto var(--s4)' }} />
        <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', marginBottom: '8px' }}>{title}</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: 1.5, marginBottom: onRetry ? 'var(--s5)' : 0 }}>{message}</p>
        {onRetry && (
          <button className="btn btn-secondary" onClick={onRetry}>
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({ title = 'No data available', message = 'There is no evaluation data to display.' }: { title?: string; message?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', border: '1px dashed var(--border-strong)', borderRadius: 'var(--r-lg)', background: 'var(--surface-muted)' }}>
      <div style={{ textAlign: 'center', maxWidth: '300px' }}>
        <div style={{ color: 'var(--text-faint)', marginBottom: '12px' }}>
          <AlertCircle size={32} style={{ margin: '0 auto' }} />
        </div>
        <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text)', marginBottom: '6px' }}>{title}</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', lineHeight: 1.5 }}>{message}</p>
      </div>
    </div>
  );
}

