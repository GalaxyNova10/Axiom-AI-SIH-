// GovernmentPilotTwinCard.tsx — Government Pilot Twin (DFS Sandbox) Environment Visualization
import { Landmark, Wifi, Smartphone, Languages, Scale, Users } from 'lucide-react';
import type { PilotTwinParameters } from '../types/api';

interface Props {
  pilotTwin: PilotTwinParameters;
}

export default function GovernmentPilotTwinCard({ pilotTwin }: Props) {
  const { demographics, infrastructure, language_coverage, regulatory_frame } = pilotTwin || {
    demographics: { rural_borrower_pct: 75, unbanked_thin_file_pct: 45, female_borrower_pct: 52 },
    infrastructure: { connectivity_2g_3g_pct: 45, low_end_device_pct: 60, offline_kiosk_pct: 20 },
    language_coverage: { indic_dialects_tested: 12, primary_script: 'Devanagari/Latin' },
    regulatory_frame: { rbi_guidelines: 'RBI Digital Lending 2022', data_protection: 'DPDP Act 2023', fair_lending: 'RBI Fair Practices Code' },
  };

  return (
    <div>
      {/* Sandbox Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: 'var(--r-md)',
            background: 'var(--accent-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Landmark size={16} color="var(--accent)" />
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 650, color: 'var(--text-primary)' }}>
              {pilotTwin.department || 'Department of Financial Services'}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Pilot Twin ID: <span className="font-mono" style={{ color: 'var(--text-secondary)' }}>{pilotTwin.twin_id || 'DFS-SANDBOX-001'}</span>
            </div>
          </div>
        </div>
        <span style={{
          fontSize: '11px',
          fontWeight: 700,
          padding: '3px 8px',
          borderRadius: '4px',
          background: 'var(--eligible-bg)',
          color: 'var(--eligible)',
          border: '1px solid var(--eligible-border)',
        }}>
          ACTIVE TWIN
        </span>
      </div>

      {/* Constraints Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px', marginBottom: '16px' }}>
        {/* Network Stress */}
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-md)', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Wifi size={14} color="var(--watch)" />
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>Network Constraints</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>2G/3G Packet Drop Rate</span>
            <span className="font-number" style={{ fontWeight: 700, color: 'var(--watch)' }}>{infrastructure?.connectivity_2g_3g_pct || 45}%</span>
          </div>
          <div style={{ height: '4px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${infrastructure?.connectivity_2g_3g_pct || 45}%`, background: 'var(--watch)', borderRadius: '99px' }} />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '6px' }}>
            Simulates rural mobile tower drops & UPI timeout surges
          </div>
        </div>

        {/* Device Constraint */}
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-md)', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Smartphone size={14} color="var(--accent)" />
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>Device Heterogeneity</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Low-End Devices (&le;2GB RAM)</span>
            <span className="font-number" style={{ fontWeight: 700, color: 'var(--accent)' }}>{infrastructure?.low_end_device_pct || 60}%</span>
          </div>
          <div style={{ height: '4px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${infrastructure?.low_end_device_pct || 60}%`, background: 'var(--accent)', borderRadius: '99px' }} />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '6px' }}>
            Tests on-device OCR latency & client memory caps
          </div>
        </div>

        {/* Demographics & Thin-file */}
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-md)', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Users size={14} color="var(--eligible)" />
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>Borrower Demographics</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Rural / Unbanked (Thin-file)</span>
            <span className="font-number" style={{ fontWeight: 700, color: 'var(--eligible)' }}>{demographics?.unbanked_thin_file_pct || 45}%</span>
          </div>
          <div style={{ height: '4px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${demographics?.unbanked_thin_file_pct || 45}%`, background: 'var(--eligible)', borderRadius: '99px' }} />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '6px' }}>
            Tests utility, mandi cashflows & non-bureau surrogates
          </div>
        </div>

        {/* Vernacular Language Dialects */}
        <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--r-md)', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Languages size={14} color="var(--advisory)" />
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)' }}>Linguistic Diversity</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11.5px', marginBottom: '4px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Regional Indic Dialects</span>
            <span className="font-number" style={{ fontWeight: 700, color: 'var(--advisory)' }}>{language_coverage?.indic_dialects_tested || 12} Languages</span>
          </div>
          <div style={{ height: '4px', background: 'var(--bg-sunken)', borderRadius: '99px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '100%', background: 'var(--advisory)', borderRadius: '99px' }} />
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-faint)', marginTop: '6px' }}>
            Includes Bhojpuri, Marwari, Bengali, Tamil, Telugu, Kannada
          </div>
        </div>
      </div>

      {/* Regulatory Compliance Bar */}
      <div style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--r-md)',
        padding: '10px 14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Scale size={13} color="var(--text-muted)" />
          <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)' }}>Statutory Sandbox Anchors:</span>
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {Object.values(regulatory_frame || {}).map((item, idx) => (
            <span key={idx} style={{
              fontSize: '10px',
              fontWeight: 500,
              padding: '2px 8px',
              borderRadius: '4px',
              background: 'var(--bg-sunken)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border)',
            }}>
              {String(item)}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}