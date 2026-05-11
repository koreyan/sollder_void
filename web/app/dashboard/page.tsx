import fs from 'fs';
import path from 'path';
import { Activity } from 'lucide-react';
import MetricsChart from './MetricsChart';

export default function DashboardPage() {
  const dataPath = path.join(process.cwd(), 'public', 'data', 'metrics.json');
  const fileContents = fs.readFileSync(dataPath, 'utf8');
  const data = JSON.parse(fileContents);

  return (
    <div className="container">
      <div style={{ marginBottom: '3rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity color="var(--primary)" />
          Performance Metrics
        </h1>
        <p className="text-muted" style={{ fontSize: '1.125rem' }}>
          Quantitative comparison between Baseline and Proposed detection models on the independent test set.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '2rem',
        marginBottom: '3rem'
      }}>
        {/* Baseline Card */}
        <div className="card" style={{ borderTop: '4px solid var(--primary)' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--primary)' }}>Baseline Model</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', color: 'var(--foreground)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Training Data</span>
              <span>{data.baseline.data_count} imgs (Real Only)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Training Time</span>
              <span>{(data.baseline.training_time_sec / 60).toFixed(1)} mins</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--card-border)', paddingTop: '0.75rem', marginTop: '0.25rem' }}>
              <span className="text-muted">F1 Score</span>
              <span style={{ fontWeight: 'bold' }}>{data.baseline.F1.toFixed(3)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">mAP@50</span>
              <span style={{ fontWeight: 'bold' }}>{(data.baseline.mAP50 * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Proposed Card */}
        <div className="card" style={{ borderTop: '4px solid var(--accent)' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--accent)' }}>Proposed Model</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', color: 'var(--foreground)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Training Data</span>
              <span>{data.proposed.data_count} imgs (Real + Synthetic)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">Training Time</span>
              <span>{(data.proposed.training_time_sec / 60).toFixed(1)} mins</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--card-border)', paddingTop: '0.75rem', marginTop: '0.25rem' }}>
              <span className="text-muted">F1 Score</span>
              <span style={{ fontWeight: 'bold' }}>{data.proposed.F1.toFixed(3)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="text-muted">mAP@50</span>
              <span style={{ fontWeight: 'bold' }}>{(data.proposed.mAP50 * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Metrics Comparison Chart</h3>
        <MetricsChart data={data} />
      </div>
    </div>
  );
}
