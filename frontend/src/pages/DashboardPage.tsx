import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import { runDemoEvaluation } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { Play, AlertTriangle, ChevronRight, Activity, Shield, Users, Map } from 'lucide-react';

export default function DashboardPage() {
  const { data, loading, error, setDemoData, setLoading, setError } = useDemoContext();
  const navigate = useNavigate();
  const [running, setRunning] = useState(false);

  const handleRunDemo = async () => {
    setRunning(true);
    setLoading(true);
    setError(null);
    try {
      const res = await runDemoEvaluation();
      setDemoData(res);
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message ?? 'Failed to run demo evaluation. Is the backend running?';
      setError(msg);
    } finally {
      setRunning(false);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '70vh', gap: '20px' }}>
        <div style={{ width: '40px', height: '40px' }} className="spinner" />
        <p className="font-subheading">Executing 14-stage deterministic evaluation pipeline…</p>
      </div>
    );
  }

  if (!data && !error) {
    return <LandingScreen onRun={handleRunDemo} running={running} />;
  }

  if (error) {
    return (
      <div className="page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '70vh', gap: '24px' }}>
        <div className="card" style={{ maxWidth: '480px', width: '100%', borderColor: 'var(--critical-border)', textAlign: 'center' }}>
          <Shield size={32} color="var(--critical)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '12px', color: 'var(--text)' }}>Evaluation Failed</h2>
          <p className="font-body" style={{ color: 'var(--text-muted)', marginBottom: '20px' }}>{error}</p>
          <button className="btn btn-primary" onClick={handleRunDemo} disabled={running}>
            {running ? 'Retrying…' : 'Retry'}
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const vendors = data.vendors ?? [];
  const procurement = data.procurement ?? {};
  const failureMaps = data.failure_maps ?? [];
  const evalId = vendors[0]?.evaluation_id ?? 'demo';

  const eligibleCount = vendors.filter(v => (procurement[v.vendor_id]?.decision ?? v.procurement_recommendation) === 'ELIGIBLE').length;
  const rejectedCount = vendors.length - eligibleCount;
  const totalCritical = failureMaps.reduce((sum, fm) => sum + (fm.critical_hotspots_count ?? 0), 0);

  return (
    <div className="page animate-in">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div className="font-label" style={{ marginBottom: '6px' }}>AXIOM-DEMO-001 · EVIDENCE-GATED EVALUATION</div>
          <h1 className="font-display">Procurement Intelligence</h1>
          <p className="font-subheading" style={{ marginTop: '8px' }}>
            Rural Agricultural Logistics · Department of Agricultural Logistics
          </p>
        </div>
        <button className="btn btn-secondary" onClick={handleRunDemo} disabled={running}>
          <Play size={14} />
          {running ? 'Running…' : 'Re-run Demo'}
        </button>
      </div>

      {/* KPI Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '32px' }}>
        <KpiCard label="Vendors Evaluated" value={String(vendors.length)} icon={<Users size={16} />} />
        <KpiCard label="Eligible" value={String(eligibleCount)} icon={<Shield size={16} />} color="var(--eligible)" />
        <KpiCard label="Rejected" value={String(rejectedCount)} icon={<Shield size={16} />} color="var(--critical)" />
        <KpiCard label="Deployment Strata" value="24" icon={<Map size={16} />} />
        <KpiCard label="Critical Hotspots" value={String(totalCritical)} icon={<Activity size={16} />} color={totalCritical > 0 ? 'var(--critical)' : undefined} />
      </div>

      {/* Governance Principle Strip */}
      <div className="principle-strip" style={{ marginBottom: '32px' }}>
        AI assists · Evidence proves · Rules gate · Humans authorize
      </div>

      {/* Vendor Decision Cards */}
      <h2 className="font-heading" style={{ marginBottom: '20px' }}>Vendor Decision Landscape</h2>
      <div className="stagger" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        {vendors.map((v) => {
          const procDecision = procurement[v.vendor_id]?.decision ?? v.procurement_recommendation ?? 'PENDING';
          const fm = failureMaps.find(f => f.vendor_id === v.vendor_id);
          const isEligible = procDecision === 'ELIGIBLE';
          return (
            <article
              key={v.vendor_id}
              className="card card-hover"
              style={{ cursor: 'pointer', borderColor: isEligible ? 'var(--eligible-border)' : 'var(--border)' }}
              onClick={() => navigate(`/evaluation/${evalId}/vendors/${v.vendor_id}`)}
              tabIndex={0}
              onKeyDown={e => e.key === 'Enter' && navigate(`/evaluation/${evalId}/vendors/${v.vendor_id}`)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '15px', fontWeight: 700 }}>{v.display_name ?? v.vendor_id}</h3>
                  <div className="font-caption" style={{ marginTop: '2px' }}>{v.vendor_id}</div>
                </div>
                <StatusBadge status={procDecision} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div className="metric metric-sm">
                  <span className="metric-label">Accuracy</span>
                  <span className="metric-value font-number" style={{ color: (v.accuracy ?? 0) < 80 ? 'var(--critical)' : 'var(--text)' }}>
                    {v.accuracy != null ? `${v.accuracy.toFixed(1)}%` : '—'}
                  </span>
                </div>
                <div className="metric metric-sm">
                  <span className="metric-label">Evidence</span>
                  <span className="metric-value" style={{ fontSize: '13px' }}>{v.evidence_level ?? '—'}</span>
                </div>
                <div className="metric metric-sm">
                  <span className="metric-label">Critical Hotspots</span>
                  <span className="metric-value font-number" style={{ color: (fm?.critical_hotspots_count ?? 0) > 0 ? 'var(--critical)' : 'var(--text)' }}>
                    {fm?.critical_hotspots_count ?? 0}
                  </span>
                </div>
                <div className="metric metric-sm">
                  <span className="metric-label">Confidence</span>
                  <span className="metric-value font-number">
                    {v.evidence_confidence != null ? `${v.evidence_confidence.toFixed(1)}%` : '—'}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  View details <ChevronRight size={14} />
                </span>
              </div>
            </article>
          );
        })}
      </div>

      {/* Narrative Callout */}
      <div className="card animate-up" style={{ borderColor: 'var(--watch-border)', background: 'var(--watch-bg)' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
          <AlertTriangle size={24} color="var(--watch)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 700, marginBottom: '6px', color: 'var(--text)' }}>
              Aggregate performance is not deployment safety.
            </h3>
            <p className="font-body" style={{ color: 'var(--text-secondary)' }}>
              <strong>KrishiLink Technologies</strong> scores the highest overall accuracy yet receives a REJECTED 
              recommendation. The deterministic evidence-gate detected acute compound failure under 
              <code style={{ background: 'rgba(0,0,0,0.06)', padding: '1px 5px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '12px', margin: '0 4px' }}>NOISY + LOW_END + REGIONAL</code>
              conditions. High aggregate accuracy conceals localized catastrophic failure — which matters far more for rural deployment safety.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function LandingScreen({ onRun, running }: { onRun: () => void; running: boolean }) {
  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '80vh', textAlign: 'center' }}>
      <div style={{ maxWidth: '580px' }}>
        <div className="font-label" style={{ marginBottom: '12px', color: 'var(--accent)' }}>AXIOM-DEMO-001</div>
        <h1 className="font-display" style={{ fontSize: '36px', marginBottom: '16px' }}>
          Rural Agricultural Logistics
        </h1>
        <h2 style={{ fontSize: '18px', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '32px', lineHeight: 1.5 }}>
          Evidence-Gated Procurement & Deployment Governance
        </h2>
        <p className="font-body" style={{ color: 'var(--text-muted)', marginBottom: '40px', maxWidth: '460px', margin: '0 auto 40px' }}>
          Evaluates three AI vendors across 24 deployment strata — intermittent connectivity, low-end devices, 
          regional languages, and degraded inputs — then applies deterministic procurement gates and human authorization.
        </p>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '48px' }}>
          <button id="run-demo-btn" className="btn btn-primary btn-lg" onClick={onRun} disabled={running}>
            {running
              ? <><div style={{ width: '18px', height: '18px' }} className="spinner" /> Running Pipeline…</>
              : <><Play size={18} /> Run Canonical Demo</>
            }
          </button>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', maxWidth: '440px', margin: '0 auto' }}>
          {['AI assists', 'Evidence proves', 'Rules gate', 'Humans authorize'].map(p => (
            <div key={p} style={{ background: 'var(--surface-muted)', border: '1px solid var(--border)', borderRadius: '8px', padding: '10px 8px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textAlign: 'center' }}>
              {p}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color?: string }) {
  return (
    <div className="card" style={{ padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
        <span style={{ color: color ?? 'var(--text-muted)' }}>{icon}</span>
        <span className="font-label">{label}</span>
      </div>
      <div style={{ fontSize: '26px', fontWeight: 700, color: color ?? 'var(--text)', fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em' }}>
        {value}
      </div>
    </div>
  );
}
