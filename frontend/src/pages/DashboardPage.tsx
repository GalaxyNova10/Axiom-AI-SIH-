// ============================================================
// Dashboard / Home Page
// ============================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play, CheckCircle, ShieldCheck, Activity, Users,
  Map, Brain, TrendingUp, RefreshCw, AlertTriangle,
} from 'lucide-react';
import { runDemoEvaluation } from '../services/api';
import { useDemoContext } from '../context/DemoContext';
import type { ApiError } from '../types/api';
import StatusBadge from '../components/StatusBadge';

export default function DashboardPage() {
  const { data, loading, error, setData, setLoading, setError } = useDemoContext();
  const [runError, setRunError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleRunDemo() {
    setLoading(true);
    setRunError(null);
    setError(null);
    try {
      const result = await runDemoEvaluation();
      setData(result);
    } catch (e: unknown) {
      const apiErr = e as ApiError;
      setRunError(apiErr.message ?? 'Unknown error running demo.');
    } finally {
      setLoading(false);
    }
  }

  const evalId = data?.vendors?.[0]?.evaluation_id;

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1200px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h1 style={{ fontSize: '22px', fontWeight: 700, color: '#f1f5f9', marginBottom: '4px' }}>
              Axiom AI Governance Dashboard
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '13px' }}>
              Evidence-Gated Innovation Procurement Platform
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            {data && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={handleRunDemo}
                disabled={loading}
                aria-label="Re-run the canonical demo"
              >
                <RefreshCw size={13} />
                Re-run Demo
              </button>
            )}
            <button
              id="run-demo-btn"
              className="btn btn-primary btn-lg"
              onClick={handleRunDemo}
              disabled={loading}
              aria-label="Run canonical demo evaluation"
            >
              {loading ? (
                <>
                  <span className="spinner" style={{ width: '16px', height: '16px' }} aria-hidden="true" />
                  Running…
                </>
              ) : (
                <>
                  <Play size={16} aria-hidden="true" />
                  Run Canonical Demo
                </>
              )}
            </button>
          </div>
        </div>

        <div className="principle-banner" style={{ marginTop: '16px' }}>
          "AI assists. Evidence proves. Rules gate. Humans authorize."
        </div>
      </div>

      {/* Error */}
      {(runError || error) && (
        <div className="alert alert-error" style={{ marginBottom: '20px' }} role="alert">
          <AlertTriangle size={16} aria-hidden="true" />
          <div>
            <strong>Demo failed</strong>
            <p style={{ marginTop: '2px', fontSize: '12px' }}>{runError || error}</p>
            <p style={{ marginTop: '4px', fontSize: '12px', opacity: 0.8 }}>
              Make sure the Axiom backend is running: <code>python -m uvicorn app.main:app --reload</code>
            </p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0' }}>
            <span className="spinner" style={{ width: '24px', height: '24px' }} aria-hidden="true" />
            <div>
              <div style={{ fontWeight: 600, color: '#93c5fd' }}>Running 14-stage evaluation pipeline…</div>
              <div style={{ color: '#64748b', fontSize: '12px', marginTop: '2px' }}>
                Outcome Contract → Pilot Twin → Test Matrix → Golden Suite → Vendor Evaluation → Evidence → Failure Cartography → Diagnostics → Procurement → Scale-Up → Authorization
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Pre-demo info */}
      {!data && !loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <InfoCard
            title="Scenario"
            value="Rural Agricultural Logistics — Evidence-Gated Procurement"
            sub="AXIOM-DEMO-001"
            icon={<Activity size={18} color="#3b82f6" />}
          />
          <InfoCard
            title="Department"
            value="Department of Agricultural Logistics"
            sub="Government Client"
            icon={<ShieldCheck size={18} color="#7c3aed" />}
          />
          <InfoCard
            title="District"
            value="Rural Demonstration District"
            sub="Pilot Region"
            icon={<Map size={18} color="#16a34a" />}
          />
          <InfoCard
            title="Vendors Evaluated"
            value="3 Vendors"
            sub="AgriRoute · RuralFlow AI · KrishiLink"
            icon={<Users size={18} color="#d97706" />}
          />
        </div>
      )}

      {/* Post-demo summary */}
      {data && !loading && (
        <>
          {/* Scenario meta */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', marginBottom: '24px' }}>
            <MetricBox label="Scenario ID" value={data.scenario.scenario_id} mono />
            <MetricBox label="Department" value={data.scenario.department} />
            <MetricBox label="District" value={data.scenario.district} />
            <MetricBox label="Evaluation Status" value={<StatusBadge status="AUTHORIZED" dot />} />
          </div>

          {/* Audit summary */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <div className="card-header">
              <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={16} color="#16a34a" />
                Audit Summary
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              <AuditItem label="Contract Locked" value={data.audit_summary.contract_locked} />
              <AuditItem label="Pilot Twin Locked" value={data.audit_summary.twin_locked} />
              <AuditItem label="Evaluator Authorized" value={data.audit_summary.evaluator_authorized} />
              <AuditItem label="Human Auth Status" value={data.audit_summary.human_authorization_status} text />
              <AuditItem label="Scale-Up Policy" value={data.audit_summary.scale_up_policy_case} text />
            </div>
          </div>

          {/* Vendor overview */}
          <div className="card" style={{ marginBottom: '20px' }}>
            <div className="card-header">
              <span style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Users size={16} color="#3b82f6" />
                Vendor Evaluation Overview
              </span>
              {evalId && (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => navigate(`/evaluation/${evalId}/vendors`)}
                  aria-label="View all vendor details"
                >
                  View All →
                </button>
              )}
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table className="axiom-table" aria-label="Vendor evaluation results">
                <thead>
                  <tr>
                    <th>Vendor</th>
                    <th>Accuracy</th>
                    <th>Latency (ms)</th>
                    <th>Evidence Level</th>
                    <th>Confidence</th>
                    <th>Failure Status</th>
                    <th>Procurement</th>
                  </tr>
                </thead>
                <tbody>
                  {data.vendors.map((v) => (
                    <tr
                      key={v.vendor_id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => evalId && navigate(`/evaluation/${evalId}/vendors`)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => e.key === 'Enter' && evalId && navigate(`/evaluation/${evalId}/vendors`)}
                      aria-label={`View ${v.display_name ?? v.vendor_id} details`}
                    >
                      <td>
                        <div style={{ fontWeight: 600 }}>{v.display_name ?? v.vendor_id}</div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>{v.vendor_id}</div>
                      </td>
                      <td>
                        <AccuracyBar value={v.accuracy} />
                      </td>
                      <td className="mono" style={{ fontSize: '13px' }}>
                        {v.latency != null ? `${v.latency.toFixed(1)}` : '—'}
                      </td>
                      <td>
                        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                          {v.evidence_level ?? '—'}
                        </span>
                      </td>
                      <td>
                        {v.evidence_confidence != null ? (
                          <span style={{ fontWeight: 600, color: v.evidence_confidence >= 70 ? '#4ade80' : '#f87171' }}>
                            {v.evidence_confidence.toFixed(1)}%
                          </span>
                        ) : '—'}
                      </td>
                      <td>
                        <StatusBadge status={v.overall_status ?? 'NORMAL'} dot />
                      </td>
                      <td>
                        <StatusBadge status={v.procurement_recommendation} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quick nav */}
          {evalId && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px' }}>
              {[
                { label: 'Failure Cartography', icon: <Map size={18} />, segment: 'failure-map' },
                { label: 'Diagnostics', icon: <Brain size={18} />, segment: 'diagnostics' },
                { label: 'Procurement Decision', icon: <ShieldCheck size={18} />, segment: 'decision' },
                { label: 'Scale-Up', icon: <TrendingUp size={18} />, segment: 'scale-up' },
                { label: 'Human Authorization', icon: <Users size={18} />, segment: 'authorization' },
                { label: 'Audit Trail', icon: <Activity size={18} />, segment: 'audit' },
              ].map(({ label, icon, segment }) => (
                <button
                  key={segment}
                  className="btn btn-secondary"
                  style={{ flexDirection: 'column', height: '80px', justifyContent: 'center', gap: '8px' }}
                  onClick={() => navigate(`/evaluation/${evalId}/${segment}`)}
                  aria-label={`Navigate to ${label}`}
                >
                  {icon}
                  <span style={{ fontSize: '12px' }}>{label}</span>
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ---- Sub-components ----

function InfoCard({ title, value, sub, icon }: { title: string; value: string; sub: string; icon: React.ReactNode }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        {icon}
        <span className="section-title" style={{ margin: 0 }}>{title}</span>
      </div>
      <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: '14px' }}>{value}</div>
      <div style={{ color: '#64748b', fontSize: '11px', marginTop: '4px' }}>{sub}</div>
    </div>
  );
}

function MetricBox({ label, value, mono }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div className="metric-box">
      <div className="metric-label">{label}</div>
      <div className={`metric-value ${mono ? 'mono' : ''}`} style={{ fontSize: '13px', fontWeight: 600 }}>
        {value}
      </div>
    </div>
  );
}

function AuditItem({
  label, value, text,
}: { label: string; value: boolean | string; text?: boolean }) {
  return (
    <div className="metric-box">
      <div className="metric-label">{label}</div>
      <div style={{ marginTop: '6px' }}>
        {text ? (
          <StatusBadge status={String(value)} />
        ) : (
          <StatusBadge status={value ? 'ELIGIBLE' : 'REJECTED'} />
        )}
      </div>
    </div>
  );
}

function AccuracyBar({ value }: { value?: number }) {
  if (value == null) return <span style={{ color: '#64748b' }}>—</span>;
  const pct = Math.min(100, Math.max(0, value));
  const color = pct >= 80 ? '#16a34a' : pct >= 60 ? '#d97706' : '#dc2626';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div className="progress-bar" style={{ width: '60px' }} aria-hidden="true">
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span style={{ color, fontWeight: 600, fontSize: '13px' }} aria-label={`${pct.toFixed(1)} percent accuracy`}>
        {pct.toFixed(1)}%
      </span>
    </div>
  );
}
