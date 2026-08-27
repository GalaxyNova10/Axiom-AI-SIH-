// ============================================================
// Axiom AI — Global Demo State (React Context)
// Stores the complete demo evaluation result after "Run Demo".
// ============================================================

import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { DemoResponse } from '../types/api';

interface DemoState {
  data: DemoResponse | null;
  loading: boolean;
  error: string | null;
  setDemoData: (d: DemoResponse | null) => void;
  setLoading: (b: boolean) => void;
  setError: (e: string | null) => void;
}

const DemoContext = createContext<DemoState | null>(null);

export function DemoProvider({ children }: { children: ReactNode }) {
  const [data, setDemoData] = useState<DemoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <DemoContext.Provider value={{ data, loading, error, setDemoData, setLoading, setError }}>
      {children}
    </DemoContext.Provider>
  );
}

export function useDemoContext(): DemoState {
  const ctx = useContext(DemoContext);
  if (!ctx) throw new Error('useDemoContext must be used within DemoProvider');
  return ctx;
}
