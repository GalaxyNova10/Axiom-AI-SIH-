import { ResponsiveContainer, Treemap, Tooltip } from 'recharts';
import type { FailureHotspot } from '../../types/api';

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'CRITICAL': return '#f87171';
    case 'DEGRADED': return '#fb923c';
    case 'WATCH': return '#fbbf24';
    default: return '#34d399';
  }
};

interface CustomContentProps {
  x?: number; y?: number; width?: number; height?: number;
  name?: string; severity?: string; accuracy?: number;
}

function CustomContent({ x = 0, y = 0, width = 0, height = 0, name, severity, accuracy }: CustomContentProps) {
  if (width < 40 || height < 30) return null;
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} rx={4} fill={getSeverityColor(severity ?? 'NORMAL')} fillOpacity={0.2} stroke={getSeverityColor(severity ?? 'NORMAL')} strokeWidth={1} strokeOpacity={0.4} />
      {width > 60 && height > 40 && (
        <>
          <text x={x + 6} y={y + 16} fill="var(--text-primary)" fontSize={11} fontWeight={700}>
            {accuracy != null ? `${accuracy.toFixed(1)}%` : ''}
          </text>
          {width > 80 && height > 50 && (
            <text x={x + 6} y={y + 30} fill="var(--text-muted)" fontSize={9}>
              {(name ?? '').replace(/_/g, ' ').slice(0, 20)}
            </text>
          )}
        </>
      )}
    </g>
  );
}

export default function HotspotTreemap({ hotspots }: { hotspots: FailureHotspot[] }) {
  const data = hotspots.map(hs => ({
    name: hs.stratum_id,
    size: Math.max(5, 100 - hs.accuracy),
    severity: hs.severity,
    accuracy: hs.accuracy,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <Treemap
        data={data}
        dataKey="size"
        stroke="var(--border)"
        content={<CustomContent />}
      >
        <Tooltip
          contentStyle={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'var(--text-primary)',
          }}
          formatter={(_: unknown, __: unknown, props: { payload?: { accuracy?: number; severity?: string } }) => {
            const p = props.payload;
            return [`${p?.accuracy?.toFixed(2)}% accuracy · ${p?.severity}`, 'Hotspot'];
          }}
        />
      </Treemap>
    </ResponsiveContainer>
  );
}
