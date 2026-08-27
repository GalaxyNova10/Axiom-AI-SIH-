// StartupInputModal.tsx — Interactive Startup Plan Submission & Configuration Modal
import { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Sparkles, Send, Landmark, Cpu, Percent, MapPin, Building } from 'lucide-react';
import type { FintechStartupInput } from '../types/api';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: FintechStartupInput) => Promise<void>;
  initialData?: FintechStartupInput;
  isLoading?: boolean;
}

const DEFAULT_PRESET: FintechStartupInput = {
  startup_name: 'CredVeda AI',
  model_name: 'Vernacular MSME Underwriting & Credit Risk Engine',
  department: 'Department of Financial Services',
  district: 'DFS Digital Finance Pilot District (Tier-3/4)',
  claimed_accuracy: 94.5,
  seed: 42,
};

export default function StartupInputModal({ isOpen, onClose, onSubmit, initialData, isLoading = false }: Props) {
  const [formData, setFormData] = useState<FintechStartupInput>(initialData || DEFAULT_PRESET);
  const [error, setError] = useState<string | null>(null);

  const handlePreset = () => {
    setFormData(DEFAULT_PRESET);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.startup_name.trim()) {
      setError('Startup name is required.');
      return;
    }
    if (!formData.model_name.trim()) {
      setError('Model name is required.');
      return;
    }
    if (formData.claimed_accuracy <= 0 || formData.claimed_accuracy > 100) {
      setError('Claimed accuracy must be between 1% and 100%.');
      return;
    }

    setError(null);
    await onSubmit(formData);
    onClose();
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px 14px',
    borderRadius: 'var(--r-md)',
    border: '1px solid var(--border-strong)',
    background: 'var(--bg-elevated)',
    color: 'var(--text-primary)',
    fontSize: '13.5px',
    fontFamily: 'inherit',
    outline: 'none',
    transition: 'all 0.15s ease',
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'var(--bg-overlay)',
              backdropFilter: 'blur(6px)',
              zIndex: 100,
            }}
          />

          {/* Modal Card */}
          <div style={{
            position: 'fixed',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            zIndex: 101,
            pointerEvents: 'none',
          }}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 16 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              style={{
                width: '100%',
                maxWidth: '560px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-strong)',
                borderRadius: 'var(--r-xl)',
                boxShadow: 'var(--shadow-xl)',
                padding: '28px',
                pointerEvents: 'auto',
                position: 'relative',
                maxHeight: '90vh',
                overflowY: 'auto',
              }}
            >
              {/* Close Button */}
              <button
                onClick={onClose}
                className="btn btn-ghost btn-xs"
                style={{ position: 'absolute', top: '20px', right: '20px' }}
              >
                <X size={16} />
              </button>

              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--r-md)',
                  background: 'linear-gradient(135deg, var(--accent), #8b5cf6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Cpu size={18} color="white" />
                </div>
                <div>
                  <div className="font-label" style={{ marginBottom: '2px' }}>GOVERNMENT INTAKE SANDBOX</div>
                  <h2 style={{ fontSize: '18px', fontWeight: 750, color: 'var(--text-primary)', lineHeight: 1.2 }}>
                    Submit Startup AI Proposal
                  </h2>
                </div>
              </div>

              <p style={{ fontSize: '12.5px', color: 'var(--text-secondary)', marginBottom: '20px', lineHeight: 1.5 }}>
                Input startup model specifications and claims to trigger the automated 15-point Government Pilot Twin evaluation.
              </p>

              {/* Form */}
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Startup & Model Name */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      <Building size={12} /> Startup Name
                    </label>
                    <input
                      type="text"
                      value={formData.startup_name}
                      onChange={(e) => setFormData({ ...formData, startup_name: e.target.value })}
                      placeholder="e.g. CredVeda AI"
                      style={inputStyle}
                      required
                    />
                  </div>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      <Cpu size={12} /> Model Name
                    </label>
                    <input
                      type="text"
                      value={formData.model_name}
                      onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                      placeholder="e.g. MSME Underwriter v2"
                      style={inputStyle}
                      required
                    />
                  </div>
                </div>

                {/* Department & District */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      <Landmark size={12} /> Government Department
                    </label>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      placeholder="e.g. Dept of Financial Services"
                      style={inputStyle}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      <MapPin size={12} /> Target Pilot District
                    </label>
                    <input
                      type="text"
                      value={formData.district}
                      onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                      placeholder="e.g. Tier-3 Rural District"
                      style={inputStyle}
                    />
                  </div>
                </div>

                {/* Claimed Accuracy & Seed */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      <Percent size={12} /> Vendor Claimed Accuracy (%)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="1"
                      max="100"
                      value={formData.claimed_accuracy}
                      onChange={(e) => setFormData({ ...formData, claimed_accuracy: parseFloat(e.target.value) || 0 })}
                      style={inputStyle}
                      required
                    />
                  </div>
                  <div>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', fontWeight: 650, color: 'var(--text-faint)', textTransform: 'uppercase', marginBottom: '6px' }}>
                      Evaluation Seed
                    </label>
                    <input
                      type="number"
                      value={formData.seed || 42}
                      onChange={(e) => setFormData({ ...formData, seed: parseInt(e.target.value) || 42 })}
                      style={inputStyle}
                    />
                  </div>
                </div>

                {error && (
                  <div className="alert alert-error" style={{ fontSize: '12.5px', padding: '10px 14px' }}>
                    {error}
                  </div>
                )}

                {/* Action Buttons */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '12px', gap: '12px' }}>
                  <button
                    type="button"
                    onClick={handlePreset}
                    className="btn btn-secondary btn-sm"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                  >
                    <Sparkles size={13} color="var(--accent)" /> Load CredVeda Preset
                  </button>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button type="button" onClick={onClose} className="btn btn-ghost btn-sm">
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="btn btn-accent"
                      style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                    >
                      {isLoading ? (
                        <>
                          <span className="spinner" style={{ width: '14px', height: '14px' }} />
                          Running 15 Tests...
                        </>
                      ) : (
                        <>
                          <Send size={14} /> Run Stress Battery
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}