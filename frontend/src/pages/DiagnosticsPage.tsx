// ============================================================
// Diagnostics / Evaluation Intelligence Page
// ============================================================

import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { Brain, AlertCircle } from 'lucide-react';
import type { DiagnosticReport, HotspotDiagnosis } from '../types/api';

// Safe string coercer — never renders objects as children
function safeStr(v: unknown): string {
  if (v == null) return '—';
  if (typeof v === 'string') return v;
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  if (Array.isArray(v)) return v.map(safeStr).join(', ');
  if (typeof v === 'object') return JSON.stringify(v);
  return String(v);
}

function safeStrList(v: unknown): string[] {
  if (!Array.isArray(v)) return [];
  return v.map(safeStr);
}

export default function DiagnosticsPage() {
  const { data } = useDemoContext();

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to load diagnostic intelligence." /></div>;

  const diagnostics = data.diagnostics ?? [];

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '1100px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Brain size={20} color="#7c3aed" />
          Evaluation Intelligence — Forensic Diagnostics
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          AI-generated forensic analysis of multi-factor failure interactions. Advisory only — does not alter metrics, decisions, or procurement status.
        </p>
      </div>

      <div className="alert alert-advisory" style={{ marginBottom: '20px', background: '#2d1b6922', border: '1px solid #7c3aed', color: '#c4b5fd' }}>
        <AlertCircle size={14} />
        <span>
          <strong>Advisory Intelligence — does not authorize procurement.</strong>{' '}
          Diagnostic output is qualitative explanation only. All procurement decisions are made by the deterministic backend engine,
          not by LLM output. Analysis mode (LLM or DETERMINISTIC_FALLBACK) is shown per vendor.
        </span>
      </div>

      {diagnostics.map((diag: DiagnosticReport) => (
        <DiagnosticCard key={diag.vendor_id} diag={diag} />
      ))}

      {diagnostics.length === 0 && (
        <EmptyState title="No diagnostics available" message="Diagnostic data was not returned in the demo response." />
      )}
    </div>
  );
}

function DiagnosticCard({ diag }: { diag: DiagnosticReport }) {
  const challenges = safeStrList(diag.recommended_vendor_challenges);
  const retests = safeStrList(diag.targeted_retest_recommendations);
  const hotspots: HotspotDiagnosis[] = Array.isArray(diag.compound_hotspot_diagnoses)
    ? diag.compound_hotspot_diagnoses
    : [];

  return (
    <div className="card" style={{ marginBottom: '20px' }}>
      <div className="card-header">
        <div>
          <span style={{ fontWeight: 700, fontSize: '15px' }}>{safeStr(diag.display_name) !== '—' ? safeStr(diag.display_name) : diag.vendor_id}</span>
          <span style={{ marginLeft: '8px', fontSize: '11px', color: '#64748b' }}>{diag.vendor_id}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8' }}>Analysis Mode:</span>
          <StatusBadge status={safeStr(diag.analysis_mode)} />
        </div>
      </div>

      {/* Overall verdict */}
      <div className="metric-box" style={{ marginBottom: '16px' }}>
        <div className="section-title">Overall Verdict Explanation</div>
        <p style={{ color: '#94a3b8', fontSize: '13px', lineHeight: 1.7, marginTop: '6px' }}>
          {safeStr(diag.overall_verdict_explanation)}
        </p>
      </div>

      {/* Operational risk */}
      {diag.operational_risk_summary && (
        <div className="metric-box" style={{ marginBottom: '16px' }}>
          <div className="section-title">Operational Risk Summary</div>
          <p style={{ color: '#94a3b8', fontSize: '13px', lineHeight: 1.7, marginTop: '6px' }}>{safeStr(diag.operational_risk_summary)}</p>
        </div>
      )}

      {/* Hotspot diagnoses */}
      {hotspots.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div className="section-title">Compound Hotspot Diagnoses</div>
          {hotspots.map((d: HotspotDiagnosis, i: number) => (
            <HotspotDiagCard key={`${safeStr(d.stratum_id)}-${i}`} d={d} />
          ))}
        </div>
      )}

      {/* Vendor challenges */}
      {challenges.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div className="section-title">Recommended Vendor Challenges</div>
          <ul style={{ listStyle: 'disc', paddingLeft: '20px', marginTop: '6px' }}>
            {challenges.map((c, i) => (
              <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Retest */}
      {retests.length > 0 && (
        <div>
          <div className="section-title">Targeted Retest Recommendations</div>
          <ul style={{ listStyle: 'disc', paddingLeft: '20px', marginTop: '6px' }}>
            {retests.map((r, i) => (
              <li key={i} style={{ color: '#94a3b8', fontSize: '13px', marginBottom: '4px' }}>{r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function HotspotDiagCard({ d }: { d: HotspotDiagnosis }) {
  const conditions = safeStrList(d.observed_conditions);

  return (
    <div style={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', padding: '12px', marginBottom: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
        <span className="mono" style={{ fontSize: '11px', color: '#93c5fd' }}>{safeStr(d.stratum_id)}</span>
        {d.diagnostic_confidence && (
          <span style={{ fontSize: '11px', color: '#64748b' }}>Confidence: {safeStr(d.diagnostic_confidence)}</span>
        )}
      </div>
      {conditions.length > 0 && (
        <div style={{ marginBottom: '6px' }}>
          <span style={{ fontSize: '10px', color: '#64748b', fontWeight: 600 }}>OBSERVED CONDITIONS: </span>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>{conditions.join(', ')}</span>
        </div>
      )}
      {d.interaction_diagnosis && (
        <div style={{ marginBottom: '6px' }}>
          <span style={{ fontSize: '10px', color: '#7c3aed', fontWeight: 600 }}>INTERACTION DIAGNOSIS: </span>
          <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginTop: '2px' }}>{safeStr(d.interaction_diagnosis)}</p>
        </div>
      )}
      {d.operational_impact && (
        <div>
          <span style={{ fontSize: '10px', color: '#d97706', fontWeight: 600 }}>OPERATIONAL IMPACT: </span>
          <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginTop: '2px' }}>{safeStr(d.operational_impact)}</p>
        </div>
      )}
    </div>
  );
}
