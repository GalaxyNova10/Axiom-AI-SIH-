export function SkeletonCard({ height = 120 }: { height?: number }) {
  return <div className="skeleton" style={{ height: `${height}px`, width: '100%' }} />;
}

export function SkeletonText({ width = '100%', height = 14 }: { width?: string; height?: number }) {
  return <div className="skeleton" style={{ height: `${height}px`, width, borderRadius: '4px' }} />;
}

export function SkeletonMetric() {
  return (
    <div className="card" style={{ padding: '16px' }}>
      <SkeletonText width="60%" height={10} />
      <div style={{ marginTop: '8px' }}>
        <SkeletonText width="40%" height={28} />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 3 }: { rows?: number }) {
  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)' }}>
        <SkeletonText width="80%" height={10} />
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{ padding: '14px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: '16px', alignItems: 'center' }}>
          <SkeletonText width="25%" height={14} />
          <SkeletonText width="15%" height={14} />
          <SkeletonText width="20%" height={14} />
          <SkeletonText width="15%" height={14} />
        </div>
      ))}
    </div>
  );
}

