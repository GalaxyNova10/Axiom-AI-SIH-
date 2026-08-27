// ============================================================
// Axiom AI â€” TypeScript API Types
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


// ============================================================
// Fintech Types — extends existing api.ts types
// ============================================================

export interface FintechTestConditions {
  connectivity: string;
  device: string;
  input: string;
}

export interface FintechTestResult {
  test_id: string;
  code: string;
  name: string;
  domain: string;
  description: string;
  conditions: FintechTestConditions;
  accuracy: number;
  latency_ms: number;
  passed: boolean;
  severity: string;
  evidence_level: string;
  evidence_hash: string;
  failure_reason?: string;
  feature_attribution?: Record<string, number>;
}

export interface EvidenceConfidenceBreakdown {
  evaluator_integrity: number;
  contract_integrity: number;
  artifact_integrity: number;
  test_coverage: number;
  pilot_twin_evidence: number;
  measurement_quality: number;
}

export interface EvidenceDistribution {
  INDEPENDENTLY_VALIDATED: number;
  OBSERVED: number;
  ESTIMATED: number;
  DECLARED: number;
  CLAIMED: number;
}

export interface PilotTwinParameters {
  twin_id: string;
  department: string;
  district: string;
  demographics: {
    rural_borrower_pct: number;
    unbanked_thin_file_pct: number;
    female_borrower_pct: number;
  };
  infrastructure: {
    connectivity_2g_3g_pct: number;
    low_end_device_pct: number;
    offline_kiosk_pct: number;
  };
  language_coverage: {
    indic_dialects_tested: number;
    primary_script: string;
  };
  regulatory_frame: Record<string, string>;
}

export interface FintechEvaluationResult {
  evaluation_id: string;
  scenario_id: string;
  startup_name: string;
  model_name: string;
  department: string;
  district: string;
  overall_accuracy: number;
  pass_rate: number;
  total_tests: number;
  passed_tests: number;
  critical_failures: number;
  degraded_failures: number;
  watch_failures: number;
  evidence_confidence_score: number;
  evidence_confidence_breakdown: EvidenceConfidenceBreakdown;
  evidence_distribution: EvidenceDistribution;
  pilot_twin_parameters: PilotTwinParameters;
  procurement_verdict: string;
  verdict_reasons: string[];
  test_results: FintechTestResult[];
}

export interface FintechStartupInput {
  startup_name: string;
  model_name: string;
  department: string;
  district: string;
  claimed_accuracy: number;
  seed?: number;
}

export interface FintechTestDefinition {
  test_id: string;
  code: string;
  name: string;
  domain: string;
  description: string;
  threshold_accuracy: number;
  threshold_latency_ms: number;
  severity_if_fail: string;
}

export interface FintechScenarioMetadata {
  scenario_id: string;
  scenario_name: string;
  title: string;
  problem_statement: string;
  department: string;
  district: string;
  description: string;
  preset: FintechStartupInput & { model_description?: string; architecture?: string; regulatory_claims?: string[] };
  test_definitions: FintechTestDefinition[];
}