import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip, Legend } from 'recharts';

interface VendorData {
  vendor_id: string;
  display_name?: string;
  accuracy?: number;
  latency?: number;
  evidence_confidence?: number;
}

const COLORS = ['#06b6d4', '#a78bfa', '#34d399'];

export default function VendorRadarCompare({ vendors }: { vendors: VendorData[] }) {
  const metrics = ['Accuracy', 'Speed', 'Confidence'];
  const data = metrics.map(metric => {
    const point: Record<string, unknown> = { metric };
    vendors.forEach(v => {
      const name = v.display_name ?? v.vendor_id;
      if (metric === 'Accuracy') point[name] = v.accuracy ?? 0;
      else if (metric === 'Speed') point[name] = Math.max(0, 100 - (v.latency ?? 0) / 10);
      else if (metric === 'Confidence') point[name] = v.evidence_confidence ?? 0;
    });
    return point;
  });

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="70%">
        <PolarGrid stroke="var(--chart-grid)" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-muted)', fontSize: 11, fontWeight: 600 }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: 'var(--text-faint)', fontSize: 10 }} />
        {vendors.map((v, i) => (
          <Radar
            key={v.vendor_id}
            name={v.display_name ?? v.vendor_id}
            dataKey={v.display_name ?? v.vendor_id}
            stroke={COLORS[i % COLORS.length]}
            fill={COLORS[i % COLORS.length]}
            fillOpacity={0.15}
            strokeWidth={2}
          />
        ))}
        <Tooltip
          contentStyle={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'var(--text-primary)',
          }}
        />
        <Legend wrapperStyle={{ fontSize: '12px', color: 'var(--text-secondary)' }} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
