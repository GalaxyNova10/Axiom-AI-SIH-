// ============================================================
// Axiom AI — TypeScript API Types
// Strictly mirrors actual backend response shapes from demo_scenario.py
// DO NOT add frontend-derived fields here.
// ============================================================

export type EvidenceLevel = 'INDEPENDENTLY_VALIDATED' | 'OBSERVED' | 'DECLARED' | 'ESTIMATED' | 'UNVERIFIED';
export type AnalysisMode = 'LLM' | 'DETERMINISTIC_FALLBACK';
export type Severity = 'CRITICAL' | 'DEGRADED' | 'WATCH' | 'NORMAL';
export type ProcurementDecision = 'ELIGIBLE' | 'REJECTED' | 'PENDING';
export type HumanAction = 'APPROVE' | 'REJECT' | 'OVERRIDE' | 'REQUEST_RETEST';

// ---- Health ----
export interface HealthResponse {
  status: string;
  service: string;
}

// ---- Scenario ----
export interface VendorMetadata {
  vendor_id: string;
  display_name: string;
  description: string;
  profile: string;
}

export interface ScenarioMetadata {
  scenario_id: string;
  scenario_name: string;
  title: string;
  problem_statement: string;
  department: string;
  district: string;
  description: string;
  vendors: VendorMetadata[];
  key_conditions: Record<string, string[]>;
  expected_demo_story: string;
}

// ---- Contract ----
export interface KPI {
  name: string;
  operator: string;
  threshold: number;
  unit: string;
}

export interface OutcomeContract {
  contract_id: string;
  problem_statement?: string;
  version?: string;
  is_locked?: boolean;
  kpis?: KPI[];
  minimum_evidence_confidence?: number;
  evidence_validity_months?: number;
  [key: string]: unknown;
}

// ---- Failure Hotspot ----
export interface FailureHotspot {
  stratum_id: string;
  severity: string;
  accuracy: number;
  reason?: string;
  failure_rate?: number;
  confidence?: number;
}

// ---- Vendor Scorecard (from vendors array in demo response) ----
export interface VendorScorecard {
  vendor_id: string;
  display_name?: string;
  description?: string;
  evaluation_id?: string;
  accuracy?: number;
  latency?: number;
  error_count?: number;
  evidence_level?: string;
  evidence_confidence?: number;
  overall_status?: string;
  failure_hotspots?: FailureHotspot[];
  top_failure_hotspot?: FailureHotspot | null;
  diagnostic_summary?: string;
  procurement_recommendation: string;
}

// ---- Hotspot Diagnosis ----
export interface HotspotDiagnosis {
  stratum_id: string;
  observed_conditions?: string[];
  interaction_diagnosis?: string;
  operational_impact?: string;
  diagnostic_confidence?: number | string;
  accuracy?: number;
  failure_rate?: number;
}

// ---- Vendor Challenge ----
export interface VendorChallenge {
  challenge_id: string;
  target_stratum_id: string;
  question: string;
  rationale: string;
  requested_evidence: string[];
  priority: string;
}

// ---- Retest Recommendation ----
export interface RetestRecommendation {
  recommendation_id: string;
  target_stratum_id: string;
  reason: string;
}

// ---- Diagnostic Report (from diagnostics array) ----
export interface DiagnosticReport {
  vendor_id: string;
  display_name?: string;
  analysis_mode: string;
  overall_verdict_explanation: string;
  operational_risk_summary?: string;
  compound_hotspot_diagnoses: HotspotDiagnosis[];
  recommended_vendor_challenges: VendorChallenge[];
  targeted_retest_recommendations: RetestRecommendation[];
}

// ---- Failure Map per vendor (from failure_maps array) ----
export interface VendorFailureMap {
  vendor_id: string;
  display_name?: string;
  overall_status: string;
  overall_accuracy?: number;
  total_strata?: number;
  critical_hotspots_count?: number;
  degraded_hotspots_count?: number;
  watch_hotspots_count?: number;
  hotspots: FailureHotspot[];
  explanation?: Record<string, string>;
}

// ---- Procurement Decision (value in procurement dict keyed by vendor_id) ----
export interface ProcurementDecisionDetail {
  decision: string;
  reasons?: string[];
  gates?: Array<{ gate: string; passed: boolean; value?: unknown; required?: unknown }>;
  is_eligible?: boolean;
  [key: string]: unknown;
}

// ---- Human Authorization ----
export interface HumanAuthorizationSummary {
  authorization_id?: string;
  vendor_id?: string;
  requested_action?: string;
  ai_recommendation?: string;
  human_decision?: string;
  status?: string;
  authorizing_officer_id?: string;
  justification?: string;
  escalation_required?: boolean;
  escalation_destination?: string;
  audit_event_count?: number;
  [key: string]: unknown;
}

// ---- Complete Demo Response (from /api/v1/demo/evaluate) ----
export interface DemoResponse {
  scenario: ScenarioMetadata;
  outcome_contract: OutcomeContract;
  pilot_twin: Record<string, unknown>;
  evaluation: {
    test_suite_summary: Record<string, unknown>;
    evaluator_status: Record<string, unknown>;
  };
  vendors: VendorScorecard[];
  failure_maps: VendorFailureMap[];        // array, indexed by position (matches vendors order)
  diagnostics: DiagnosticReport[];         // array, indexed by position
  procurement: Record<string, ProcurementDecisionDetail>;  // keyed by vendor_id
  scale_up: Record<string, unknown>;
  human_authorization: HumanAuthorizationSummary;
  data_governance: Record<string, unknown>;
  audit_summary: Record<string, unknown>;
}

// ---- Authorization Request (matches backend AuthorizationActionRequest) ----
export interface AuthorizationActionRequest {
  vendor_id: string;
  action: string;
  officer_id: string;
  justification: string;
  requested_action?: string;
}

// ---- API Error ----
export interface ApiError {
  status: number;
  message: string;
  detail?: unknown;
}
