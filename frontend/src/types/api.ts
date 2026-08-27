// ============================================================
// Axiom AI — TypeScript API Types
// Strictly mirrors actual backend response shapes.
// DO NOT add frontend-derived fields here.
// ============================================================

export type EvidenceLevel = 'INDEPENDENTLY_VALIDATED' | 'OBSERVED' | 'DECLARED' | 'ESTIMATED' | 'UNVERIFIED';
export type AnalysisMode = 'LLM' | 'DETERMINISTIC_FALLBACK';
export type Severity = 'CRITICAL' | 'DEGRADED' | 'WATCH' | 'NORMAL';
export type ProcurementDecision = 'ELIGIBLE' | 'REJECTED' | 'PENDING';
export type HumanAction = 'APPROVE' | 'REJECT' | 'OVERRIDE' | 'REQUEST_RETEST';
export type ScaleStatus =
  | 'SCALE_ELIGIBLE'
  | 'SCALE_REVIEW_REQUIRED'
  | 'DO_NOT_SCALE_YET'
  | 'REVALIDATION_REQUIRED';

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
  problem_statement: string;
  version: string;
  is_locked: boolean;
  kpis: KPI[];
  minimum_evidence_confidence: number;
  evidence_validity_months: number;
}

// ---- Pilot Twin ----
export interface PilotParameter {
  name: string;
  value: string;
  evidence_level: EvidenceLevel;
  source: string;
}

export interface PilotTwin {
  twin_id: string;
  district: string;
  department: string;
  is_locked: boolean;
  parameters: PilotParameter[];
}

// ---- Failure Hotspot ----
export interface FailureHotspot {
  stratum_id: string;
  severity: Severity;
  accuracy: number;
  reason: string;
}

// ---- Vendor Scorecard (from /vendors endpoint) ----
export interface VendorScorecard {
  vendor_id: string;
  display_name?: string;
  description?: string;
  evaluation_id?: string;
  accuracy?: number;
  latency?: number;
  error_count?: number;
  evidence_level?: EvidenceLevel;
  evidence_confidence?: number;
  overall_status: string;
  failure_hotspots: FailureHotspot[];
  top_failure_hotspot?: FailureHotspot;
  diagnostic_summary?: string;
  procurement_recommendation: ProcurementDecision;
}

// ---- Hotspot Diagnosis ----
export interface HotspotDiagnosis {
  stratum_id: string;
  observed_conditions: string[];
  interaction_diagnosis?: string;
  operational_impact?: string;
  diagnostic_confidence?: string;
}

// ---- Diagnostic Report ----
export interface DiagnosticReport {
  vendor_id: string;
  display_name?: string;
  analysis_mode: AnalysisMode;
  overall_verdict_explanation: string;
  operational_risk_summary?: string;
  compound_hotspot_diagnoses: HotspotDiagnosis[];
  recommended_vendor_challenges: string[];
  targeted_retest_recommendations: string[];
}

// ---- Failure Map per vendor ----
export interface VendorFailureMap {
  vendor_id: string;
  display_name?: string;
  overall_status: string;
  overall_accuracy?: number;
  total_strata: number;
  critical_hotspots_count: number;
  degraded_hotspots_count: number;
  watch_hotspots_count: number;
  hotspots: FailureHotspot[];
  explanation?: Record<string, string>;
}

// ---- Procurement Gate ----
export interface ProcurementGate {
  gate: string;
  passed: boolean;
  value?: number | string | boolean;
  required?: number | string | boolean;
}

export interface ProcurementDecisionDetail {
  decision: ProcurementDecision;
  reasons: string[];
  gates: ProcurementGate[];
}

// ---- Scale Up ----
export interface ScaleUpSummary {
  request_id: string;
  vendor_id: string;
  target_district: string;
  status: ScaleStatus;
  policy_case: string;
  scale_eligible: boolean;
  failure_map_status?: string;
  matched_failure_strata?: string[];
  reasons: string[];
  vendor_response_window_required: boolean;
}

// ---- Human Authorization ----
export interface HumanAuthorizationSummary {
  authorization_id: string;
  vendor_id: string;
  requested_action: string;
  ai_recommendation: string;
  human_decision?: string;
  status: string;
  authorizing_officer_id?: string;
  justification?: string;
  escalation_required?: boolean;
  escalation_destination?: string;
  audit_event_count?: number;
}

// ---- Data Governance ----
export interface DataGovernanceSummary {
  schedule_id: string;
  startup_ip_owner: string;
  government_evidence_owner: string;
  citizen_data_owner: string;
  model_access_mode: string;
  retention_days: number;
  disclaimer: string;
}

// ---- Audit Summary ----
export interface AuditSummary {
  contract_locked: boolean;
  twin_locked: boolean;
  evaluator_authorized: boolean;
  human_authorization_status: string;
  scale_up_policy_case: string;
}

// ---- Complete Demo Response ----
export interface DemoResponse {
  scenario: ScenarioMetadata;
  outcome_contract: OutcomeContract;
  pilot_twin: PilotTwin;
  evaluation: {
    test_suite_summary: Record<string, unknown>;
    evaluator_status: Record<string, unknown>;
  };
  vendors: VendorScorecard[];
  failure_maps: VendorFailureMap[];
  diagnostics: DiagnosticReport[];
  procurement: Record<string, ProcurementDecisionDetail>;
  scale_up: ScaleUpSummary;
  human_authorization: HumanAuthorizationSummary;
  data_governance: DataGovernanceSummary;
  audit_summary: AuditSummary;
}

// ---- Authorization Request ----
export interface AuthorizationActionRequest {
  vendor_id: string;
  action: HumanAction;
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
