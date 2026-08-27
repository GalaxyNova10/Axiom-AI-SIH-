import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ReferenceLine } from 'recharts';

interface VendorData {
  vendor_id: string;
  display_name?: string;
  accuracy?: number;
}

const getColor = (accuracy: number) => {
  if (accuracy >= 85) return '#34d399';
  if (accuracy >= 70) return '#fbbf24';
  return '#f87171';
};

export default function AccuracyBarChart({ vendors }: { vendors: VendorData[] }) {
  const data = vendors.map(v => ({
    name: v.display_name ?? v.vendor_id,
    accuracy: v.accuracy ?? 0,
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical" margin={{ top: 0, right: 20, bottom: 0, left: 10 }}>
        <XAxis type="number" domain={[0, 100]} tick={{ fill: 'var(--text-faint)', fontSize: 10 }} axisLine={{ stroke: 'var(--border)' }} tickLine={false} />
        <YAxis type="category" dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontWeight: 500 }} axisLine={false} tickLine={false} width={100} />
        <Tooltip
          contentStyle={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            fontSize: '12px',
            color: 'var(--text-primary)',
          }}
          formatter={(value: any) => [`${value.toFixed(2)}%`, 'Accuracy']}
        />
        <ReferenceLine x={80} stroke="var(--watch)" strokeDasharray="4 4" strokeWidth={1} />
        <Bar dataKey="accuracy" radius={[0, 6, 6, 0]} barSize={20}>
          {data.map((entry, i) => (
            <Cell key={i} fill={getColor(entry.accuracy)} fillOpacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
