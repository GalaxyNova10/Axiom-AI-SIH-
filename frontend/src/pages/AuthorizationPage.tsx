import { useState } from 'react';
import { useDemoContext } from '../context/DemoContext';
import { submitAuthorization } from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { UserCheck, ShieldAlert, CheckCircle, Clock } from 'lucide-react';

export default function AuthorizationPage() {
  const { data, setDemoData } = useDemoContext();
  const vendors = data?.vendors ?? [];
  const evalId = vendors[0]?.evaluation_id ?? 'demo';

  const [selectedVendor, setSelectedVendor] = useState('');
  const [action, setAction] = useState('APPROVE');
  const [officerId, setOfficerId] = useState('');
  const [justification, setJustification] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<Record<string, unknown> | null>(null);

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to enable authorization workflows.</p>
      </div>
    );
  }

  const vendor = vendors.find(v => v.vendor_id === selectedVendor);
  const aiRec = (data.procurement?.[selectedVendor]?.decision ?? vendor?.procurement_recommendation ?? 'PENDING');
  const isOverride = selectedVendor && (
    (action === 'APPROVE' && aiRec === 'REJECTED') ||
    (action === 'REJECT' && aiRec === 'ELIGIBLE') ||
    action === 'OVERRIDE'
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedVendor) { setError('Please select a vendor.'); return; }
    if (!officerId.trim()) { setError('Officer ID is required.'); return; }
    if (justification.trim().length < 10) { setError('Justification must be at least 10 characters.'); return; }

    setLoading(true);
    setError(null);
    try {
      const result = await submitAuthorization(evalId, {
        vendor_id: selectedVendor,
        action,
        officer_id: officerId,
        justification,
        requested_action: 'PROCUREMENT',
      });
      setSubmitted(result as unknown as Record<string, unknown>);
      // Update demo state
      if (data) {
        setDemoData({ ...data, human_authorization: result });
      }
    } catch (err: unknown) {
      setError((err as { message?: string })?.message ?? 'Authorization submission failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px', color: 'var(--critical)' }}>HUMAN DECISION REQUIRED</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <UserCheck size={28} color="var(--accent)" /> Human Authorization
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>AI recommends. Humans authorize. Maker-checker workflow enforced.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '28px' }}>
        {/* Form */}
        <div className="card">
          <div className="card-header"><span style={{ fontWeight: 600 }}>Authorization Form</span></div>
          {submitted ? (
            <div style={{ textAlign: 'center', padding: '20px 0' }}>
              <CheckCircle size={40} color="var(--eligible)" style={{ margin: '0 auto 16px' }} />
              <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>Authorization Recorded</h3>
              <p className="font-body" style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>
                Status: <strong>{String(submitted.status ?? 'RECORDED')}</strong>
              </p>
              {!!submitted.escalation_required && (
                <div className="alert alert-warning">
                  <ShieldAlert size={16} />
                  Second officer review required (override detected).
                </div>
              )}
              <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => setSubmitted(null)}>
                Submit Another
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Vendor Select */}
              <div>
                <label className="font-label" style={{ display: 'block', marginBottom: '6px' }}>Select Vendor</label>
                <select
                  value={selectedVendor}
                  onChange={e => setSelectedVendor(e.target.value)}
                  required
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-strong)', background: 'var(--surface)', color: 'var(--text)', fontSize: '14px', outline: 'none' }}
                >
                  <option value="">Choose a vendor…</option>
                  {vendors.map(v => (
                    <option key={v.vendor_id} value={v.vendor_id}>
                      {v.display_name ?? v.vendor_id} — AI: {data.procurement?.[v.vendor_id]?.decision ?? v.procurement_recommendation}
                    </option>
                  ))}
                </select>
              </div>

              {/* AI Recommendation */}
              {selectedVendor && (
                <div style={{ background: 'var(--surface-muted)', padding: '12px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="font-label">AI RECOMMENDATION</span>
                  <StatusBadge status={aiRec} />
                </div>
              )}

              {/* Action */}
              <div>
                <label className="font-label" style={{ display: 'block', marginBottom: '8px' }}>Action</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  {(['APPROVE', 'REJECT', 'OVERRIDE', 'REQUEST_RETEST'] as string[]).map(act => (
                    <label key={act} style={{
                      padding: '10px 12px', borderRadius: '8px',
                      border: action === act ? '2px solid var(--accent)' : '1px solid var(--border-strong)',
                      background: action === act ? 'var(--accent-faint)' : 'var(--surface)',
                      cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                      fontWeight: action === act ? 600 : 500, fontSize: '13px'
                    }}>
                      <input type="radio" name="action" value={act} checked={action === act} onChange={() => setAction(act)} style={{ accentColor: 'var(--accent)' }} />
                      {String(act).replace('_', ' ')}
                    </label>
                  ))}
                </div>
              </div>

              {/* Override Warning */}
              {isOverride && (
                <div className="alert alert-warning animate-in">
                  <ShieldAlert size={18} style={{ flexShrink: 0 }} />
                  <div>
                    <strong>Override detected.</strong> A second authorized officer review will be required.
                  </div>
                </div>
              )}

              {/* Officer ID */}
              <div>
                <label className="font-label" style={{ display: 'block', marginBottom: '6px' }}>Officer ID</label>
                <input
                  type="text"
                  value={officerId}
                  onChange={e => setOfficerId(e.target.value)}
                  placeholder="e.g. OFF-8891"
                  required
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-strong)', background: 'var(--surface)', color: 'var(--text)', fontSize: '14px', outline: 'none', fontFamily: 'monospace' }}
                />
              </div>

              {/* Justification */}
              <div>
                <label className="font-label" style={{ display: 'block', marginBottom: '6px' }}>Justification</label>
                <textarea
                  value={justification}
                  onChange={e => setJustification(e.target.value)}
                  placeholder="Detailed justification for this authorization action. Minimum 10 characters required."
                  required
                  rows={4}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border-strong)', background: 'var(--surface)', color: 'var(--text)', fontSize: '14px', outline: 'none', resize: 'vertical' }}
                />
              </div>

              {error && (
                <div style={{ color: 'var(--critical)', fontSize: '13px', padding: '8px 12px', background: 'var(--critical-bg)', borderRadius: '6px', border: '1px solid var(--critical-border)' }}>
                  {error}
                </div>
              )}

              <button type="submit" className="btn btn-primary btn-lg" disabled={loading || !selectedVendor}>
                {loading ? 'Submitting…' : 'Sign & Submit Authorization'}
              </button>
            </form>
          )}
        </div>

        {/* Workflow Explanation */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="card">
            <div className="card-header"><span style={{ fontWeight: 600 }}>Maker-Checker Flow</span></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0' }}>
              {[
                { label: 'AI Recommendation Generated', done: true },
                { label: 'Requesting Officer Submission', done: !!submitted },
                { label: 'Second Officer Review (if override)', done: false, isOverride: !!isOverride },
                { label: 'Final Procurement Action', done: submitted?.status === 'AUTHORIZED' || submitted?.status === 'REJECTED', last: true },
              ].map((step, i) => (
                <div key={i} style={{ display: 'flex', gap: '14px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={{
                      width: '28px', height: '28px', borderRadius: '50%', flexShrink: 0,
                      background: step.done ? 'var(--eligible)' : 'var(--surface-sunken)',
                      border: step.done ? 'none' : '2px solid var(--border-strong)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white'
                    }}>
                      {step.done ? <CheckCircle size={14} /> : <Clock size={14} color="var(--text-muted)" />}
                    </div>
                    {!step.last && <div style={{ width: '2px', flex: 1, background: step.done ? 'var(--eligible)' : 'var(--border-subtle)', margin: '4px 0', minHeight: '20px' }} />}
                  </div>
                  <div style={{ paddingBottom: step.last ? 0 : '18px', paddingTop: '4px' }}>
                    <div style={{ fontSize: '14px', fontWeight: step.done ? 600 : 400, color: step.done ? 'var(--text)' : 'var(--text-muted)' }}>
                      {step.label}
                    </div>
                    {step.isOverride && <div style={{ fontSize: '11px', color: 'var(--watch)', fontWeight: 600, marginTop: '2px', textTransform: 'uppercase' }}>Required for overrides</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {data.human_authorization && Object.keys(data.human_authorization).length > 0 && (
            <div className="card animate-in" style={{ borderColor: 'var(--eligible-border)', background: 'var(--eligible-bg)' }}>
              <div className="card-header" style={{ borderBottomColor: 'var(--eligible-border)' }}>
                <span style={{ fontWeight: 600 }}>Previous Authorization State</span>
                <StatusBadge status={String(data.human_authorization.status ?? 'RECORDED')} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {Object.entries(data.human_authorization).filter(([k]) => !['authorization_id'].includes(k)).map(([k, v]) => (
                  <div key={k} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--eligible-border)', paddingBottom: '8px' }}>
                    <span className="font-label">{k.replace(/_/g, ' ')}</span>
                    <span style={{ fontSize: '13px', color: 'var(--text)', fontWeight: 500, maxWidth: '200px', textAlign: 'right' }}>{String(v ?? '—')}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
