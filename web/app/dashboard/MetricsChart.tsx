'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface MetricsChartProps {
  data: {
    baseline: any;
    proposed: any;
  };
}

export default function MetricsChart({ data }: MetricsChartProps) {
  const chartData = [
    {
      name: 'F1 Score',
      Baseline: data.baseline.F1,
      Proposed: data.proposed.F1,
    },
    {
      name: 'mAP@50',
      Baseline: data.baseline.mAP50,
      Proposed: data.proposed.mAP50,
    },
    {
      name: 'mAP@50-95',
      Baseline: data.baseline["mAP50-95"],
      Proposed: data.proposed["mAP50-95"],
    },
  ];

  return (
    <div style={{ width: '100%', height: 400, marginTop: '2rem' }}>
      <ResponsiveContainer>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Bar dataKey="Baseline" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Proposed" fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
