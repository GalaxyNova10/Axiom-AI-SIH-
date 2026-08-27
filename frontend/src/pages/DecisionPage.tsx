import { useState } from 'react';
import { useDemoContext } from '../context/DemoContext';
import StatusBadge from '../components/StatusBadge';
import { ShieldCheck, AlertTriangle, ChevronDown, ChevronRight, CheckCircle, XCircle } from 'lucide-react';

export default function DecisionPage() {
  const { data } = useDemoContext();
  const vendors = data?.vendors ?? [];
  const procurement = data?.procurement ?? {};
  const [selected, setSelected] = useState<string>('');

  if (!data) {
    return (
      <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <p className="font-subheading" style={{ color: 'var(--text-muted)' }}>Run the canonical demo to load procurement decisions.</p>
      </div>
    );
  }

  const activeVendorId = selected || vendors[0]?.vendor_id || '';
  const vendor = vendors.find(v => v.vendor_id === activeVendorId);
  const decision = procurement[activeVendorId];
  const finalDecision = decision?.decision ?? vendor?.procurement_recommendation ?? 'PENDING';
  const isEligible = finalDecision === 'ELIGIBLE';

  return (
    <div className="page animate-in">
      <div style={{ marginBottom: '32px' }}>
        <div className="font-label" style={{ marginBottom: '6px' }}>DETERMINISTIC GATE</div>
        <h1 className="font-display" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ShieldCheck size={28} color="var(--accent)" /> Procurement Decision Gate
        </h1>
        <p className="font-subheading" style={{ marginTop: '8px' }}>
          Rules gate. Humans authorize. The frontend never calculates eligibility.
        </p>
      </div>

      <div className="alert alert-warning" style={{ marginBottom: '24px' }}>
        <AlertTriangle size={18} style={{ flexShrink: 0 }} />
        <div>
          <strong>AI recommendation is advisory.</strong>{' '}
          Deterministic governance rules produce the gate outcome. Human authorization is required for final procurement action.
        </div>
      </div>

      {/* Vendor Selector */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
        {vendors.map(v => {
          const dec = procurement[v.vendor_id]?.decision ?? v.procurement_recommendation ?? 'PENDING';
          return (
            <button
              key={v.vendor_id}
              className={`btn ${activeVendorId === v.vendor_id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSelected(v.vendor_id)}
            >
              {v.display_name ?? v.vendor_id}
              <span style={{ marginLeft: '4px' }}>
                {dec === 'ELIGIBLE' ? '✓' : dec === 'REJECTED' ? '✗' : '·'}
              </span>
            </button>
          );
        })}
      </div>

      {/* Outcome Banner */}
      <div className="card" style={{
        borderColor: isEligible ? 'var(--eligible-border)' : 'var(--critical-border)',
        background: isEligible ? 'var(--eligible-bg)' : 'var(--critical-bg)',
        marginBottom: '24px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px'
      }}>
        <div>
          <div className="font-label" style={{ color: isEligible ? 'var(--eligible)' : 'var(--critical)', marginBottom: '6px' }}>
            {vendor?.display_name ?? activeVendorId}
          </div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text)' }}>
            {decision?.reasons?.[0] ?? (isEligible ? 'All procurement gates passed.' : 'One or more procurement gates failed.')}
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
          <div className="font-label">FINAL DECISION</div>
          <StatusBadge status={finalDecision} />
        </div>
      </div>

      {/* Gate Timeline */}
      {decision?.gates && decision.gates.length > 0 ? (
        <div style={{ position: 'relative', paddingLeft: '32px' }}>
          <div style={{ position: 'absolute', top: 0, bottom: '20px', left: '15px', width: '2px', background: 'var(--border-subtle)' }} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {decision.gates.map((gate, i) => (
              <GateRow key={i} num={i + 1} gate={String(gate.gate)} passed={gate.passed} value={gate.value} required={gate.required} />
            ))}
            {/* Final node */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '16px', paddingTop: '8px' }}>
              <div style={{
                width: '32px', height: '32px', borderRadius: '50%',
                background: isEligible ? 'var(--eligible)' : 'var(--critical)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginLeft: '-31px', border: '4px solid var(--surface)'
              }}>
                {isEligible ? <CheckCircle size={18} color="white" /> : <XCircle size={18} color="white" />}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className="font-label">FINAL DETERMINISTIC DECISION</span>
                <StatusBadge status={finalDecision} />
              </div>
            </div>
          </div>
        </div>
      ) : decision ? (
        /* Fallback: show reasons if no gates array */
        <div className="card">
          <div className="font-label" style={{ marginBottom: '12px' }}>Decision Reasons</div>
          {(decision.reasons ?? []).length > 0 ? (
            <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {(decision.reasons ?? []).map((r, i) => (
                <li key={i} className="font-body" style={{ color: 'var(--text-secondary)' }}>{r}</li>
              ))}
            </ul>
          ) : (
            <p className="font-body" style={{ color: 'var(--text-muted)' }}>No detailed gate data returned by backend.</p>
          )}
        </div>
      ) : (
        <div className="card">
          <p className="font-body" style={{ color: 'var(--text-muted)' }}>No procurement decision data available for this vendor.</p>
        </div>
      )}
    </div>
  );
}

function GateRow({ num, gate, passed, value, required }: { num: number; gate: string; passed: boolean; value?: unknown; required?: unknown }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div style={{ position: 'relative', display: 'flex', gap: '16px', zIndex: 1 }}>
      <div style={{
        width: '30px', height: '30px', borderRadius: '50%', flexShrink: 0, marginLeft: '-29px',
        background: passed ? 'var(--eligible)' : 'var(--critical)',
        border: '3px solid var(--surface)', display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        {passed ? <CheckCircle size={14} color="white" /> : <XCircle size={14} color="white" />}
      </div>
      <div
        className="card"
        style={{ flex: 1, padding: '10px 16px', cursor: 'pointer', borderColor: passed ? 'var(--eligible-border)' : 'var(--critical-border)', marginTop: '-6px' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="font-label" style={{ color: 'var(--text-faint)' }}>GATE {num}</span>
            <span style={{ fontSize: '14px', fontWeight: 600 }}>{gate}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <StatusBadge status={passed ? 'PASS' : 'FAIL'} size="sm" />
            {(value != null || required != null) && (
              expanded ? <ChevronDown size={14} color="var(--text-muted)" /> : <ChevronRight size={14} color="var(--text-muted)" />
            )}
          </div>
        </div>
        {expanded && (value != null || required != null) && (
          <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px dashed var(--border-subtle)', display: 'flex', gap: '24px', fontSize: '13px' }}>
            {value != null && <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Actual: </span><span className="font-mono">{String(value)}</span></div>}
            {required != null && <div><span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Required: </span><span className="font-mono">{String(required)}</span></div>}
          </div>
        )}
      </div>
    </div>
  );
}
