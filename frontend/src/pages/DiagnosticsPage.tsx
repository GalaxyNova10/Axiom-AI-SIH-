import { useState } from 'react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { Brain, AlertCircle, ChevronDown, ChevronUp, ShieldAlert, Target } from 'lucide-react';
import type { HotspotDiagnosis, VendorChallenge, RetestRecommendation, DiagnosticReport, VendorFailureMap } from '../types/api';

function formatStratumId(stratumId: string) {
  if (!stratumId) return [];
  const parts = stratumId.split('_');
  const normalized: string[] = [];
  let i = 0;
  while (i < parts.length) {
    if (parts[i] === 'LOW' && parts[i+1] === 'END') { normalized.push('LOW-END'); i+=2; }
    else if (parts[i] === 'HIGH' && parts[i+1] === 'END') { normalized.push('HIGH-END'); i+=2; }
    else { normalized.push(parts[i]); i++; }
  }
  return normalized;
}

function StratumChips({ stratumId }: { stratumId: string }) {
  const parts = formatStratumId(stratumId);
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
      {parts.map((p, i) => (
        <span key={i} className="font-mono" style={{ background: 'var(--surface)', border: '1px solid var(--border-subtle)', borderRadius: '4px', padding: '3px 8px', fontSize: '11px', color: 'var(--text-secondary)' }}>
          {p}
        </span>
      ))}
    </div>
  );
}

function HotspotCard({ hs }: { hs: HotspotDiagnosis }) {
  const [expanded, setExpanded] = useState(false);
  
  const isCritical = (hs.accuracy != null && hs.accuracy < 0.5) || hs.operational_impact?.toLowerCase().includes('critical') || hs.failure_rate === 1.0;

  return (
    <div style={{ background: 'var(--surface)', border: `1px solid ${isCritical ? 'var(--critical-border)' : 'var(--border-strong)'}`, borderRadius: '8px', overflow: 'hidden' }}>
      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
           <StratumChips stratumId={hs.stratum_id} />
           <StatusBadge status={isCritical ? 'CRITICAL' : 'WATCH'} size="sm" />
        </div>
        
        <div style={{ display: 'flex', gap: '24px', fontSize: '13px' }}>
           {hs.accuracy != null && (
             <div style={{ display: 'flex', flexDirection: 'column' }}>
               <span style={{ color: 'var(--text-muted)' }}>Accuracy</span>
               <span style={{ fontWeight: 600 }}>{(hs.accuracy * 100).toFixed(1)}%</span>
             </div>
           )}
           {hs.failure_rate != null && (
             <div style={{ display: 'flex', flexDirection: 'column' }}>
               <span style={{ color: 'var(--text-muted)' }}>Failure Rate</span>
               <span style={{ fontWeight: 600 }}>{(hs.failure_rate * 100).toFixed(1)}%</span>
             </div>
           )}
           {hs.diagnostic_confidence != null && (
             <div style={{ display: 'flex', flexDirection: 'column' }}>
               <span style={{ color: 'var(--text-muted)' }}>Confidence</span>
               <span style={{ fontWeight: 600 }}>{typeof hs.diagnostic_confidence === 'number' ? `${(hs.diagnostic_confidence * 100).toFixed(1)}%` : hs.diagnostic_confidence}</span>
             </div>
           )}
        </div>
        
        {hs.operational_impact && (
          <p className="font-body" style={{ color: 'var(--text-secondary)' }}>
            {hs.operational_impact.length > 120 && !expanded ? `${hs.operational_impact.substring(0, 120)}...` : hs.operational_impact}
          </p>
        )}
      </div>
      
      {(hs.interaction_diagnosis || (hs.operational_impact && hs.operational_impact.length > 120)) && (
        <>
          {expanded && (
            <div style={{ padding: '0 16px 16px', borderTop: '1px solid var(--border-subtle)', marginTop: '8px', paddingTop: '16px' }}>
               {hs.interaction_diagnosis && (
                 <div style={{ marginBottom: '12px' }}>
                   <div className="font-label" style={{ marginBottom: '4px', color: 'var(--text)' }}>Interaction Diagnosis</div>
                   <p className="font-body" style={{ color: 'var(--text-secondary)' }}>{hs.interaction_diagnosis}</p>
                 </div>
               )}
            </div>
          )}
          <button 
            onClick={() => setExpanded(!expanded)} 
            style={{ width: '100%', padding: '8px', background: 'var(--surface-muted)', border: 'none', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {expanded ? 'Hide details' : 'View diagnostic details'}
          </button>
        </>
      )}
    </div>
  );
}

function ChallengeCard({ challenge }: { challenge: VendorChallenge }) {
  return (
    <div style={{ background: 'var(--surface)', border: '1px solid var(--border-strong)', borderRadius: '8px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text)' }}>{challenge.challenge_id}</span>
          <StatusBadge status={challenge.priority || 'HIGH'} size="sm" />
        </div>
      </div>
      
      <div>
        <div className="font-label" style={{ marginBottom: '6px' }}>Target Condition</div>
        <StratumChips stratumId={challenge.target_stratum_id} />
      </div>

      <div>
        <div className="font-label" style={{ marginBottom: '4px' }}>Vendor Question</div>
        <p className="font-body" style={{ color: 'var(--text-secondary)', fontStyle: 'italic', paddingLeft: '12px', borderLeft: '3px solid var(--border-subtle)' }}>
          "{challenge.question}"
        </p>
      </div>

      {challenge.rationale && (
        <div>
          <div className="font-label" style={{ marginBottom: '4px' }}>Rationale</div>
          <p className="font-body" style={{ color: 'var(--text-secondary)' }}>{challenge.rationale}</p>
        </div>
      )}

      {challenge.requested_evidence && challenge.requested_evidence.length > 0 && (
        <div>
          <div className="font-label" style={{ marginBottom: '8px' }}>Requested Evidence</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {challenge.requested_evidence.map((ev, i) => (
              <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', background: 'var(--surface-muted)', border: '1px solid var(--border-subtle)', borderRadius: '16px', fontSize: '12px', color: 'var(--text)', fontWeight: 500 }}>
                <Target size={12} color="var(--accent)" /> {ev}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function RetestRecommendationList({ retests }: { retests: RetestRecommendation[] }) {
  return (
    <div style={{ overflowX: 'auto', background: 'var(--surface)', border: '1px solid var(--border-strong)', borderRadius: '8px' }}>
      <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'collapse', fontSize: '13px' }}>
        <thead>
          <tr style={{ background: 'var(--surface-muted)', borderBottom: '1px solid var(--border-strong)', textAlign: 'left' }}>
             <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>RECOMMENDATION</th>
             <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>TARGET CONDITION</th>
             <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>REASON</th>
             <th style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>ACTION</th>
          </tr>
        </thead>
        <tbody>
          {retests.map((r, i) => (
            <tr key={i} style={{ borderBottom: i === retests.length - 1 ? 'none' : '1px solid var(--border-subtle)' }}>
              <td style={{ padding: '12px 16px', fontFamily: 'monospace', fontWeight: 600 }}>{r.recommendation_id}</td>
              <td style={{ padding: '12px 16px' }}><StratumChips stratumId={r.target_stratum_id} /></td>
              <td style={{ padding: '12px 16px', color: 'var(--text-secondary)' }}>{r.reason}</td>
              <td style={{ padding: '12px 16px' }}>
                 <span style={{ padding: '4px 8px', background: 'rgba(139, 92, 246, 0.1)', color: 'var(--advisory)', borderRadius: '4px', fontWeight: 600, fontSize: '11px' }}>
                   TARGETED REVALIDATION
                 </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function VendorDiagnosticSection({ diag, failureMap }: { diag: DiagnosticReport, failureMap?: VendorFailureMap }) {
  const hotspots = diag.compound_hotspot_diagnoses || [];
  const challenges = diag.recommended_vendor_challenges || [];
  const retests = diag.targeted_retest_recommendations || [];

  return (
    <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '32px', overflowWrap: 'anywhere' }}>
      {/* Vendor Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>{diag.display_name ?? diag.vendor_id}</h2>
          <div className="font-mono" style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '2px' }}>{diag.vendor_id}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="font-label">MODE</span>
          <StatusBadge status={diag.analysis_mode ?? 'DETERMINISTIC_FALLBACK'} />
        </div>
      </div>

      {/* Metrics */}
      {failureMap && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)', padding: '16px 0' }}>
          <div className="metric">
            <span className="metric-label">ACCURACY</span>
            <span style={{ fontSize: '18px', fontWeight: 700 }}>{failureMap.overall_accuracy != null ? `${(failureMap.overall_accuracy * 100).toFixed(1)}%` : 'N/A'}</span>
          </div>
          <div className="metric">
            <span className="metric-label">HOTSPOTS</span>
            <span style={{ fontSize: '18px', fontWeight: 700 }}>{failureMap.hotspots?.length || 0}</span>
          </div>
          <div className="metric">
            <span className="metric-label">CRITICAL</span>
            <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--critical)' }}>{failureMap.critical_hotspots_count || 0}</span>
          </div>
          <div className="metric">
            <span className="metric-label">RETESTS</span>
            <span style={{ fontSize: '18px', fontWeight: 700 }}>{retests.length}</span>
          </div>
        </div>
      )}

      {/* Assessment */}
      {diag.overall_verdict_explanation && (
        <div>
          <div className="font-label" style={{ marginBottom: '8px' }}>OVERALL ASSESSMENT</div>
          <p className="font-body" style={{ color: 'var(--text)', fontSize: '15px', lineHeight: 1.6 }}>
            {diag.overall_verdict_explanation}
          </p>
        </div>
      )}

      {/* Risk Summary */}
      {diag.operational_risk_summary && (
        <div style={{ background: 'var(--critical-bg)', borderLeft: '4px solid var(--critical)', padding: '16px', borderRadius: '4px 8px 8px 4px' }}>
          <div className="font-label" style={{ marginBottom: '8px', color: 'var(--critical)', display: 'flex', alignItems: 'center', gap: '6px' }}>
             <ShieldAlert size={14} /> OPERATIONAL RISK SUMMARY
          </div>
          <p className="font-body" style={{ color: 'var(--critical)', fontWeight: 500 }}>
            {diag.operational_risk_summary}
          </p>
        </div>
      )}

      {/* Hotspots */}
      {hotspots.length > 0 && (
        <div>
          <div className="font-label" style={{ marginBottom: '16px' }}>COMPOUND HOTSPOT DIAGNOSES</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
             {hotspots.map((hs, i) => <HotspotCard key={i} hs={hs} />)}
          </div>
        </div>
      )}

      {/* Challenges */}
      {challenges.length > 0 && (
        <div>
          <div className="font-label" style={{ marginBottom: '16px' }}>RECOMMENDED VENDOR CHALLENGES</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
             {challenges.map((c, i) => <ChallengeCard key={i} challenge={c} />)}
          </div>
        </div>
      )}

      {/* Retests */}
      {retests.length > 0 && (
        <div>
          <div className="font-label" style={{ marginBottom: '16px' }}>TARGETED RETEST RECOMMENDATIONS</div>
          <RetestRecommendationList retests={retests} />
        </div>
      )}

    </div>
  );
}

export default function DiagnosticsPage() {
  const { data } = useDemoContext();

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load diagnostic intelligence.</p>
      </div>
    );
  }

  const diagnostics = data.diagnostics ?? [];
  const failureMaps = data.failure_maps ?? [];

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '24px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>ADVISORY INTELLIGENCE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Brain size={28} color="var(--advisory)" /> Forensic Evaluation Intelligence
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px', maxWidth: '800px' }}>
          AI-assisted forensic analysis of failure interactions. Advisory only — does not affect procurement gates.
        </p>
      </div>

      <div className="alert alert-advisory" style={{ marginBottom: '32px' }}>
        <AlertCircle size={18} style={{ flexShrink: 0 }} />
        <div>
          <strong>Advisory Intelligence · Does not authorize procurement.</strong>{' '}
          All procurement decisions are produced by the deterministic governance engine. This analysis interprets measured results only.
        </div>
      </div>

      {diagnostics.length === 0 && (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)', background: 'var(--surface)', borderRadius: '8px', border: '1px dashed var(--border-strong)' }}>
          <Brain size={32} style={{ margin: '0 auto 12px', opacity: 0.4 }} />
          No diagnostic findings available.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {diagnostics.map(diag => {
           const fm = failureMaps.find(f => f.vendor_id === diag.vendor_id);
           return <VendorDiagnosticSection key={diag.vendor_id} diag={diag} failureMap={fm as VendorFailureMap | undefined} />;
        })}
      </div>
    </div>
  );
}
