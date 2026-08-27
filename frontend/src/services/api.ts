// ============================================================
// Axiom AI — Centralized API Client
// All backend communication goes through this module.
// ============================================================

import type {
  HealthResponse,
  ScenarioMetadata,
  DemoResponse,
  VendorScorecard,
  DiagnosticReport,
  VendorFailureMap,
  ProcurementDecisionDetail,
  HumanAuthorizationSummary,
  AuthorizationActionRequest,
  ApiError,
} from '../types/api';

// ---- Config ----
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

// When using Vite dev proxy, base URL is empty (relative paths work).
// In production, set VITE_API_BASE_URL=http://your-server:8000

// ---- Forbidden sensitive keys — defense-in-depth sanitization ----
const FORBIDDEN_KEYS = new Set([
  'private_parameters',
  'raw_seed',
  'seed',
  'seed_hash',
  'secret',
  'private_key',
  'api_key',
  'openai_api_key',
  'model_weights',
]);

export function sanitizeResponse<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => sanitizeResponse(item)) as T;
  }
  if (obj !== null && typeof obj === 'object') {
    const clean: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(obj as Record<string, unknown>)) {
      if (FORBIDDEN_KEYS.has(k.toLowerCase())) continue;
      clean[k] = sanitizeResponse(v);
    }
    return clean as T;
  }
  return obj as T;
}

// ---- Base fetch wrapper ----
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  let response: Response;

  try {
    response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      ...options,
    });
  } catch (networkErr) {
    const err: ApiError = {
      status: 0,
      message: `Network error: Cannot reach Axiom API at ${url}. Make sure the backend is running at http://localhost:8000.`,
    };
    throw err;
  }

  if (!response.ok) {
    let detail: unknown = undefined;
    try { detail = await response.json(); } catch { /* ignore */ }
    const err: ApiError = {
      status: response.status,
      message: `API error ${response.status}: ${response.statusText}`,
      detail,
    };
    throw err;
  }

  let data: unknown;
  try {
    data = await response.json();
  } catch {
    const err: ApiError = { status: 200, message: 'Server returned malformed JSON.' };
    throw err;
  }

  return sanitizeResponse<T>(data);
}

// ============================================================
// Health
// ============================================================
export const checkHealth = (): Promise<HealthResponse> =>
  apiFetch<HealthResponse>('/health');

// ============================================================
// Demo
// ============================================================
export const getDemoScenario = (): Promise<ScenarioMetadata> =>
  apiFetch<ScenarioMetadata>('/api/v1/demo/scenario');

export const runDemoEvaluation = (): Promise<DemoResponse> =>
  apiFetch<DemoResponse>('/api/v1/demo/evaluate', { method: 'POST' });

// ============================================================
// Evaluations
// ============================================================
export const getEvaluation = (evaluationId: string): Promise<Record<string, unknown>> =>
  apiFetch<Record<string, unknown>>(`/api/v1/evaluations/${evaluationId}`);

export const getEvaluationVendors = (evaluationId: string): Promise<VendorScorecard[]> =>
  apiFetch<VendorScorecard[]>(`/api/v1/evaluations/${evaluationId}/vendors`);

export const getEvaluationDiagnostics = (evaluationId: string): Promise<Record<string, DiagnosticReport>> =>
  apiFetch<Record<string, DiagnosticReport>>(`/api/v1/evaluations/${evaluationId}/diagnostics`);

export const getEvaluationFailureMap = (evaluationId: string): Promise<Record<string, VendorFailureMap>> =>
  apiFetch<Record<string, VendorFailureMap>>(`/api/v1/evaluations/${evaluationId}/failure-map`);

export const getEvaluationDecision = (evaluationId: string): Promise<Record<string, ProcurementDecisionDetail>> =>
  apiFetch<Record<string, ProcurementDecisionDetail>>(`/api/v1/evaluations/${evaluationId}/decision`);

export const submitAuthorization = (
  evaluationId: string,
  request: AuthorizationActionRequest,
): Promise<HumanAuthorizationSummary> =>
  apiFetch<HumanAuthorizationSummary>(`/api/v1/evaluations/${evaluationId}/authorization`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
