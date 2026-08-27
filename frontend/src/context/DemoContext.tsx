// ============================================================
// Axiom AI — Global Demo State (React Context)
// Stores and auto-initializes the canonical evaluation data.
// ============================================================

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { DemoResponse } from '../types/api';
import { runDemoEvaluation } from '../services/api';

interface DemoState {
  data: DemoResponse | null;
  loading: boolean;
  error: string | null;
  setDemoData: (d: DemoResponse | null) => void;
  setLoading: (b: boolean) => void;
  setError: (e: string | null) => void;
  refreshData: () => Promise<void>;
}

const DemoContext = createContext<DemoState | null>(null);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [data, setDemoData] = useState<DemoResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runDemoEvaluation();
      setDemoData(res);
    } catch (err: any) {
      console.error('Failed to auto-load canonical demo data:', err);
      setError(err?.message || 'Failed to connect to Axiom API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemo();
  }, []);

  return (
    <DemoContext.Provider value={{ data, loading, error, setDemoData, setLoading, setError, refreshData: fetchDemo }}>
      {children}
    </DemoContext.Provider>
  );
}

export function useDemoContext(): DemoState {
  const ctx = useContext(DemoContext);
  if (!ctx) throw new Error('useDemoContext must be used within DemoProvider');
  return ctx;
}