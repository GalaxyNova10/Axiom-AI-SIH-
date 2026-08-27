// ============================================================
// Human Authorization Page — governance-critical
// ============================================================

import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useDemoContext } from '../context/DemoContext';
import { EmptyState } from '../components/StateComponents';
import StatusBadge from '../components/StatusBadge';
import { submitAuthorization } from '../services/api';
import type { HumanAction, AuthorizationActionRequest, ApiError } from '../types/api';
import { UserCheck, AlertTriangle, AlertCircle, ShieldAlert } from 'lucide-react';

const PLACEHOLDER_JUSTIFICATIONS = new Set(['', 'n/a', 'none', 'na', 'no', '-', '--']);

export default function AuthorizationPage() {
  const { evaluationId } = useParams<{ evaluationId: string }>();
  const { data } = useDemoContext();

  const [selectedVendor, setSelectedVendor] = useState('');
  const [action, setAction] = useState<HumanAction>('APPROVE');
  const [officerId, setOfficerId] = useState('');
  const [justification, setJustification] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitResult, setSubmitResult] = useState<Record<string, unknown> | null>(null);

  if (!data) return <div style={{ padding: '28px' }}><EmptyState message="Run the canonical demo to access the authorization form." /></div>;

  const demoAuth = data.human_authorization;
  const vendors = data.vendors ?? [];
  const aiRec = data.procurement?.[selectedVendor]?.decision ?? demoAuth?.ai_recommendation ?? '—';
  const isOverride = selectedVendor && (
    (action === 'APPROVE' && aiRec === 'REJECTED') ||
    (action === 'REJECT' && aiRec === 'ELIGIBLE') ||
    action === 'OVERRIDE'
  );

  function validateJustification(j: string): boolean {
    return j.trim().length >= 10 && !PLACEHOLDER_JUSTIFICATIONS.has(j.trim().toLowerCase());
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!evaluationId) { setSubmitError('No evaluation ID found.'); return; }
    if (!selectedVendor) { setSubmitError('Please select a vendor.'); return; }
    if (!officerId.trim()) { setSubmitError('Officer ID is required.'); return; }
    if (!validateJustification(justification)) {
      setSubmitError('Justification must be at least 10 characters and cannot be a placeholder (e.g., "N/A", "none").');
      return;
    }

    const req: AuthorizationActionRequest = {
      vendor_id: selectedVendor,
      action,
      officer_id: officerId.trim(),
      justification: justification.trim(),
      requested_action: 'PROCUREMENT',
    };

    setSubmitting(true);
    setSubmitError(null);
    setSubmitResult(null);

    try {
      const res = await submitAuthorization(evaluationId, req);
      setSubmitResult(res as unknown as Record<string, unknown>);
    } catch (e: unknown) {
      const err = e as ApiError;
      setSubmitError(err.message ?? 'Authorization submission failed.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fade-in" style={{ padding: '28px', maxWidth: '900px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <UserCheck size={20} color="#7c3aed" />
          Human Authorization
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>
          Governance-critical. Only a human officer can authorize procurement. AI recommendation is advisory.
        </p>
      </div>

      {/* Critical governance notice */}
      <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
        <ShieldAlert size={16} />
        <div>
          <strong>Governance Requirement</strong>
          <p style={{ marginTop: '4px', fontSize: '12px' }}>
            Overriding an AI rejection requires dual-officer concurrence or higher-authority escalation.
            The frontend submits the decision to the backend API which enforces maker-checker rules.
            The frontend does not independently authorize procurement.
          </p>
        </div>
      </div>

      {/* Existing auth state */}
      {demoAuth && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div className="card-header">
            <span style={{ fontWeight: 600 }}>Current Authorization State</span>
            <StatusBadge status={demoAuth.status} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
            {[
              { label: 'Authorization ID', value: demoAuth.authorization_id },
              { label: 'Vendor', value: demoAuth.vendor_id },
              { label: 'Requested Action', value: demoAuth.requested_action },
              { label: 'AI Recommendation', value: demoAuth.ai_recommendation },
              { label: 'Human Decision', value: demoAuth.human_decision ?? 'PENDING' },
              { label: 'Officer', value: demoAuth.authorizing_officer_id ?? '—' },
            ].map(({ label, value }) => (
              <div key={label} className="metric-box">
                <div className="metric-label">{label}</div>
                <div style={{ fontWeight: 600, fontSize: '13px', color: '#f1f5f9', marginTop: '4px' }}>{value}</div>
              </div>
            ))}
          </div>

          {demoAuth.justification && (
            <div style={{ marginTop: '12px' }}>
              <div className="section-title">Justification on Record</div>
              <p style={{ color: '#94a3b8', fontSize: '13px', marginTop: '4px' }}>{demoAuth.justification}</p>
            </div>
          )}

          {demoAuth.escalation_required && (
            <div className="alert alert-warning" style={{ marginTop: '12px' }}>
              <AlertTriangle size={13} />
              <span>Escalation required → {demoAuth.escalation_destination}</span>
            </div>
          )}
        </div>
      )}

      {/* Authorization form */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={15} color="#7c3aed" />
          Submit New Authorization Decision
        </div>

        <form onSubmit={handleSubmit} noValidate>
          {/* Vendor */}
          <div style={{ marginBottom: '14px' }}>
            <label htmlFor="vendor-select" style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px', fontWeight: 500 }}>
              Vendor *
            </label>
            <select
              id="vendor-select"
              value={selectedVendor}
              onChange={(e) => setSelectedVendor(e.target.value)}
              required
              style={{
                width: '100%', padding: '9px 12px', background: '#0f172a',
                border: '1px solid #334155', borderRadius: '6px', color: '#e2e8f0', fontSize: '13px',
              }}
              aria-required="true"
            >
              <option value="">— Select vendor —</option>
              {vendors.map((v) => (
                <option key={v.vendor_id} value={v.vendor_id}>
                  {v.display_name ?? v.vendor_id} ({v.vendor_id}) — {v.procurement_recommendation}
                </option>
              ))}
            </select>
          </div>

          {/* AI recommendation display */}
          {selectedVendor && (
            <div className="alert alert-info" style={{ marginBottom: '14px' }}>
              <AlertCircle size={13} />
              <span>AI Recommendation for <strong>{selectedVendor}</strong>: <StatusBadge status={aiRec} /></span>
            </div>
          )}

          {/* Action */}
          <div style={{ marginBottom: '14px' }}>
            <fieldset style={{ border: 'none', padding: 0 }}>
              <legend style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px', fontWeight: 500 }}>
                Action *
              </legend>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {(['APPROVE', 'REJECT', 'OVERRIDE', 'REQUEST_RETEST'] as HumanAction[]).map((a) => (
                  <label
                    key={a}
                    style={{
                      display: 'flex', alignItems: 'center', gap: '6px',
                      padding: '7px 14px', borderRadius: '6px', cursor: 'pointer',
                      background: action === a ? '#1d4ed8' : '#1e293b',
                      border: `1px solid ${action === a ? '#3b82f6' : '#334155'}`,
                      fontSize: '13px', fontWeight: action === a ? 600 : 400, color: action === a ? 'white' : '#94a3b8',
                    }}
                  >
                    <input
                      type="radio"
                      name="action"
                      value={a}
                      checked={action === a}
                      onChange={() => setAction(a)}
                      style={{ display: 'none' }}
                      aria-label={a}
                    />
                    {a}
                  </label>
                ))}
              </div>
            </fieldset>
          </div>

          {/* Override warning */}
          {isOverride && (
            <div className="alert alert-warning" style={{ marginBottom: '14px' }}>
              <AlertTriangle size={14} />
              <div>
                <strong>Human override detected.</strong>
                <p style={{ fontSize: '12px', marginTop: '2px' }}>
                  Your decision disagrees with the AI recommendation. Secondary authorization/review may be required per maker-checker policy.
                </p>
              </div>
            </div>
          )}

          {/* Officer ID */}
          <div style={{ marginBottom: '14px' }}>
            <label htmlFor="officer-id" style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px', fontWeight: 500 }}>
              Officer ID *
            </label>
            <input
              id="officer-id"
              type="text"
              value={officerId}
              onChange={(e) => setOfficerId(e.target.value)}
              placeholder="e.g., OFFICER-ALICE"
              required
              aria-required="true"
              style={{
                width: '100%', padding: '9px 12px', background: '#0f172a',
                border: '1px solid #334155', borderRadius: '6px', color: '#e2e8f0', fontSize: '13px',
              }}
            />
          </div>

          {/* Justification */}
          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="justification" style={{ display: 'block', fontSize: '12px', color: '#94a3b8', marginBottom: '6px', fontWeight: 500 }}>
              Justification * <span style={{ color: '#64748b' }}>(minimum 10 characters, no placeholders)</span>
            </label>
            <textarea
              id="justification"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Provide a substantive justification for this authorization decision…"
              rows={4}
              required
              aria-required="true"
              style={{
                width: '100%', padding: '9px 12px', background: '#0f172a',
                border: '1px solid #334155', borderRadius: '6px', color: '#e2e8f0',
                fontSize: '13px', resize: 'vertical', fontFamily: 'Inter, system-ui, sans-serif',
              }}
            />
            <div style={{ fontSize: '11px', color: justification.length < 10 ? '#dc2626' : '#64748b', marginTop: '4px' }}>
              {justification.length} characters — minimum 10 required
            </div>
          </div>

          {/* Error */}
          {submitError && (
            <div className="alert alert-error" style={{ marginBottom: '12px' }}>
              <AlertCircle size={13} />
              <span>{submitError}</span>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            id="submit-authorization-btn"
            className="btn btn-primary"
            disabled={submitting}
            aria-label="Submit authorization decision"
          >
            {submitting ? (
              <>
                <span className="spinner" style={{ width: '14px', height: '14px' }} />
                Submitting…
              </>
            ) : (
              <>
                <UserCheck size={14} />
                Submit Authorization
              </>
            )}
          </button>
        </form>
      </div>

      {/* Result */}
      {submitResult && (
        <div className="card">
          <div className="card-header">
            <span style={{ fontWeight: 600, color: '#4ade80' }}>Authorization Submitted</span>
            <StatusBadge status={String(submitResult.status ?? 'PENDING')} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
            {Object.entries(submitResult)
              .filter(([k]) => !['escalation_destination'].includes(k))
              .map(([k, v]) => (
                <div key={k} className="metric-box">
                  <div className="metric-label">{k.replace(/_/g, ' ')}</div>
                  <div style={{ fontWeight: 600, fontSize: '12px', color: '#e2e8f0', marginTop: '4px', wordBreak: 'break-all' }}>
                    {String(v ?? '—')}
                  </div>
                </div>
              ))}
          </div>
          {Boolean(submitResult.escalation_required) && (
            <div className="alert alert-warning" style={{ marginTop: '12px' }}>
              <AlertTriangle size={13} />
              <span>Escalation required → {String(submitResult.escalation_destination)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
