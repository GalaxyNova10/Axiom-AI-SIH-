"""
End-to-End Orchestrator Pipeline

Demonstrates the complete Axiom AI workflow in one call:
Problem -> Outcome Contract -> Pilot Twin -> Private Test Matrix ->
Golden Suite Evaluator Verification -> Artifact Freeze -> Vendor Evaluation ->
Evidence Generation -> Evidence Confidence -> Failure Cartography ->
Procurement Decision -> Vendor Response Window -> Human Authorization ->
Scale-Up Policy (District Alpha -> District Beta).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import copy
import uuid

# Existing Axiom modules
from ai.contract_generator import generate_outcome_contract
from ai.pilot_twin import create_pilot_twin, PilotParameter
from ai.test_matrix import generate_test_suite, get_public_methodology
from ai.golden_suite import create_initial_golden_suite, authorize_evaluator
from ai.demo_vendors import VendorAAdapter, VendorBAdapter, VendorCAdapter
from ai.demo_dataset import get_demo_expected_outputs
from ai.artifact import register_artifact, freeze_artifact, verify_artifact_for_evaluation, create_evidence_validity
from ai.evaluator import evaluate_vendor, EvaluationRun
from ai.evidence_record import create_evidence_record, freeze_evidence, EvidenceRecord
from ai.confidence import calculate_evidence_confidence, explain_evidence_confidence
from ai.failure_cartography import generate_failure_map, explain_failure_map, FailureMap
from ai.decision_engine import evaluate_procurement
from ai.vendor_response import submit_vendor_response, review_vendor_response, get_response_history
from ai.human_authorization import create_authorization, review_override, get_authorization_history, AuthorizationRequest
from ai.scale_up import ScaleUpRequest, evaluate_scale_up_request
from ai.scale_policy import evaluate_scale_policy
from ai.data_governance import create_data_governance_schedule, sanitize_citizen_data


@dataclass
class AxiomDemoResult:
    contract: Dict[str, Any]
    pilot_twin: Dict[str, Any]
    test_suite_summary: Dict[str, Any]
    evaluator_status: Dict[str, Any]
    vendor_results: Dict[str, Any]
    evidence_summary: Dict[str, Any]
    confidence_summary: Dict[str, Any]
    failure_map_summary: Dict[str, Any]
    procurement_decisions: Dict[str, Any]
    vendor_response: Dict[str, Any]
    human_authorization: Dict[str, Any]
    scale_up_evaluation: Dict[str, Any]
    data_governance: Dict[str, Any]
    audit_summary: Dict[str, Any]

    def to_public_dict(self) -> Dict[str, Any]:
        """
        Returns a completely sanitized, JSON-safe public dictionary.
        Strictly scrubs any raw seeds, private parameters, source code, or internal tokens.
        """
        def _sanitize(obj: Any) -> Any:
            if isinstance(obj, dict):
                clean = {}
                for k, v in obj.items():
                    k_str = str(k).lower()
                    if k_str in ("raw_seed", "private_parameters", "seed", "source_code", "model_weights"):
                        continue
                    clean[k] = _sanitize(v)
                return clean
            elif isinstance(obj, list):
                return [_sanitize(item) for item in obj]
            elif hasattr(obj, "__dataclass_fields__"):
                return _sanitize(asdict(obj))
            return obj

        return _sanitize(asdict(self))


def run_axiom_demo(
    problem_statement: str = "Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays.",
    seed: int = 42,
) -> AxiomDemoResult:
    """
    Executes the 14-stage end-to-end Axiom governance demo workflow.
    """

    # --- STAGE 1: Outcome Contract ---
    contract = generate_outcome_contract(
        contract_id="CONTRACT-AGRI-001",
        problem_statement=problem_statement,
    )
    for k in contract.kpis:
        if k.name == "Delivery Success Rate":
            k.threshold = 80.0
        elif k.name == "Average Delivery Delay":
            k.threshold = 20.0
    contract.minimum_evidence_confidence = 70.0
    contract.evidence_validity_months = 12
    contract.locked = True

    contract_summary = {
        "contract_id": contract.contract_id,
        "problem_statement": problem_statement,
        "version": contract.version,
        "is_locked": contract.locked,
        "kpis": [
            {
                "name": k.name,
                "operator": k.operator,
                "threshold": k.threshold,
                "unit": k.unit,
            }
            for k in contract.kpis
        ],
        "minimum_evidence_confidence": contract.minimum_evidence_confidence,
        "evidence_validity_months": contract.evidence_validity_months,
    }

    # --- STAGE 2: Government Pilot Twin (District Alpha) ---
    pilot_twin = create_pilot_twin(
        twin_id="TWIN-DISTRICT-ALPHA",
        department="Department of Agriculture",
        district="District Alpha",
        parameters=[
            PilotParameter(name="connectivity", value="INTERMITTENT", evidence_level="OBSERVED", source="Telecom Log"),
            PilotParameter(name="device", value="LOW_END", evidence_level="DECLARED", source="Gov Survey"),
            PilotParameter(name="language", value="REGIONAL", evidence_level="OBSERVED", source="Census"),
            PilotParameter(name="input_quality", value="NOISY", evidence_level="UNVERIFIED", source="Field Estimate"),
        ]
    )
    pilot_twin.locked = True

    pilot_twin_summary = {
        "twin_id": pilot_twin.twin_id,
        "district": pilot_twin.district,
        "department": pilot_twin.department,
        "is_locked": pilot_twin.locked,
        "parameters": [
            {
                "name": p.name,
                "value": p.value,
                "evidence_level": p.evidence_level,
                "source": p.source,
            }
            for p in pilot_twin.parameters
        ],
    }

    # --- STAGE 3: Stratified Test Suite (24 public strata, private seeds) ---
    test_suite = generate_test_suite(
        suite_id="SUITE-AGRI-ALPHA-001",
        pilot_twin_id=pilot_twin.twin_id,
        seed=seed,
    )
    methodology = get_public_methodology(test_suite)
    test_suite_summary = {
        "suite_id": test_suite.suite_id,
        "version": test_suite.version,
        "total_conditions": len(test_suite.conditions),
        "total_public_strata": 24,
        "suite_hash": test_suite.seed_hash,
        "methodology": methodology,
    }

    # --- STAGE 4: Golden Reference Suite & Evaluator Verification ---
    golden_suite = create_initial_golden_suite()
    eval_auth = authorize_evaluator("1.0.0", golden_suite)
    evaluator_summary = {
        "evaluator_version": eval_auth.evaluator_version,
        "status": eval_auth.status,
        "golden_suite_version": eval_auth.golden_suite_version,
        "golden_suite_hash": eval_auth.golden_suite_hash,
        "verified_at": eval_auth.verified_at,
    }

    # --- STAGE 5: Artifact Registration & Freeze ---
    raw_artifacts = {
        "VendorA": b"vendor_a_production_bundle_v1.0",
        "VendorB": b"vendor_b_production_bundle_v1.0",
        "VendorC": b"vendor_c_production_bundle_v1.0",
    }

    artifact_records = {}
    for vid, raw_bytes in raw_artifacts.items():
        art = register_artifact(
            artifact_id=f"ART-{vid}-001",
            vendor_id=vid,
            data=raw_bytes,
            metadata={"environment": "production_release"}
        )
        artifact_records[vid] = freeze_artifact(art)

    # --- STAGE 6: Black-Box Evaluation of 3 Vendors ---
    adapters = {
        "VendorA": VendorAAdapter(),
        "VendorB": VendorBAdapter(),
        "VendorC": VendorCAdapter(),
    }
    expected_outputs = get_demo_expected_outputs(test_suite)

    evaluation_runs: Dict[str, EvaluationRun] = {}
    vendor_results_summary = {}

    for vid, adapter in adapters.items():
        run = evaluate_vendor(
            vendor_id=vid,
            artifact_id=artifact_records[vid].artifact_id,
            adapter=adapter,
            test_suite=test_suite,
            evaluator_version="1.0.0",
            evaluator_authorized=(eval_auth.status == "AUTHORIZED"),
            expected_outputs=expected_outputs,
        )
        evaluation_runs[vid] = run
        vendor_results_summary[vid] = {
            "evaluation_id": run.evaluation_id,
            "accuracy": run.accuracy,
            "average_latency_ms": run.average_latency_ms,
            "error_count": run.error_count,
            "total_cases": run.total_cases,
            "correct_cases": run.correct_cases,
            "status": run.status,
        }

    # --- STAGE 7: Evidence Generation ---
    evidence_records: Dict[str, EvidenceRecord] = {}
    evidence_summary = {}

    for vid, run in evaluation_runs.items():
        art_ver = verify_artifact_for_evaluation(artifact_records[vid], raw_artifacts[vid])
        ev_val = create_evidence_validity(
            evidence_id=f"EVID-{vid}-001",
            artifact_record=artifact_records[vid],
            validity_months=12,
        )
        ev_rec = create_evidence_record(
            evaluation_run=run,
            artifact_record=artifact_records[vid],
            artifact_verification=art_ver,
            evidence_validity=ev_val,
            evaluator_authorized=True,
            test_suite_valid=True,
            metric_name="Delivery Success Rate",
            metric_unit="%",
        )
        freeze_evidence(ev_rec)
        evidence_records[vid] = ev_rec
        evidence_summary[vid] = {
            "evidence_id": ev_rec.evidence_id,
            "evidence_level": ev_rec.evidence_level,
            "metric_name": ev_rec.metric_name,
            "metric_value": ev_rec.metric_value,
            "validation_status": ev_rec.validation_status,
            "validity_months": ev_rec.validity_months,
            "expires_at": ev_rec.expires_at,
        }

    # --- STAGE 8: Evidence Confidence Calculation ---
    confidence_summary = {}
    for vid in adapters.keys():
        conf_score = calculate_evidence_confidence(
            evaluator_integrity=100.0,
            contract_integrity=100.0,
            artifact_integrity=100.0,
            test_integrity=100.0,
            pilot_twin_evidence=80.0,
            measurement_quality=90.0,
        )
        conf_exp = explain_evidence_confidence(
            evaluator_integrity=100.0,
            contract_integrity=100.0,
            artifact_integrity=100.0,
            test_integrity=100.0,
            pilot_twin_evidence=80.0,
            measurement_quality=90.0,
        )
        confidence_summary[vid] = {
            "score": conf_score,
            "explanation": conf_exp,
        }

    # --- STAGE 9: Failure Cartography ---
    failure_maps: Dict[str, FailureMap] = {}
    failure_map_summary = {}

    for vid, run in evaluation_runs.items():
        fm = generate_failure_map(run)
        failure_maps[vid] = fm
        fm_exp = explain_failure_map(fm)
        failure_map_summary[vid] = {
            "overall_status": fm.status,
            "overall_accuracy": fm.overall_accuracy,
            "total_strata": len(fm.strata),
            "critical_hotspots_count": len([h for h in fm.hotspots if h.severity == "CRITICAL"]),
            "degraded_hotspots_count": len([h for h in fm.hotspots if h.severity == "DEGRADED"]),
            "watch_hotspots_count": len([h for h in fm.hotspots if h.severity == "WATCH"]),
            "hotspots": [
                {
                    "stratum_id": h.stratum_id,
                    "severity": h.severity,
                    "accuracy": h.accuracy,
                    "reason": h.reason,
                }
                for h in fm.hotspots
            ],
            "explanation": fm_exp,
        }

    # --- STAGE 10: Procurement Decision Engine ---
    procurement_decisions = {}
    pt_stratum_alpha = "INTERMITTENT_LOW_END_REGIONAL_NOISY"
    for vid, run in evaluation_runs.items():
        kpi_res = {
            "Delivery Success Rate": run.accuracy,
            "Average Delivery Delay": run.average_latency_ms / 10.0,
            "Solution Performance": run.accuracy,
        }
        has_critical = any(
            h.severity == "CRITICAL" and (h.stratum_id == pt_stratum_alpha or h.stratum_id in pt_stratum_alpha)
            for h in failure_maps[vid].hotspots
        )
        dec = evaluate_procurement(
            contract=contract,
            kpi_results=kpi_res,
            evaluator_status="AUTHORIZED",
            artifact_integrity=True,
            evidence_confidence=confidence_summary[vid]["score"],
            evidence_valid=True,
            critical_failures=has_critical,
        )
        procurement_decisions[vid] = {
            "decision": dec.decision,
            "reasons": dec.reasons,
            "gates": dec.gates,
        }

    # --- STAGE 11: Vendor Response Window ---
    # Submit response for Vendor C
    v_resp = submit_vendor_response(
        vendor_id="VendorC",
        request_id="REQ-DEMO-001",
        decision_status="DO_NOT_SCALE_YET",
        response_type="CLARIFICATION",
        explanation="We observed that regional noisy edge cases can be mitigated via a targeted edge-model update.",
        requested_action="REVIEW",
        response_id="RESP-DEMO-VC-001",
    )
    reviewed_resp = review_vendor_response(
        response=v_resp,
        reviewer_id="GOV-OFFICER-001",
        decision="REQUEST_MORE_INFORMATION",
        review_reason="Please provide targeted deployment benchmarks for low-end devices.",
    )
    resp_history = get_response_history("RESP-DEMO-VC-001")

    vendor_response_summary = {
        "response_id": reviewed_resp.response_id,
        "vendor_id": reviewed_resp.vendor_id,
        "response_type": reviewed_resp.response_type,
        "requested_action": reviewed_resp.requested_action,
        "status": reviewed_resp.status,
        "reviewed_by": reviewed_resp.reviewed_by,
        "review_reason": reviewed_resp.review_reason,
        "history_event_count": len(resp_history),
    }

    # --- STAGE 12: Human Authorization ---
    # Pick the eligible vendor
    eligible_vendor = "VendorA" if procurement_decisions.get("VendorA", {}).get("decision") == "ELIGIBLE" else ("VendorB" if procurement_decisions.get("VendorB", {}).get("decision") == "ELIGIBLE" else "VendorA")
    auth_req = AuthorizationRequest(
        authorization_id="AUTH-DEMO-001",
        decision_id="DEC-DEMO-001",
        vendor_id=eligible_vendor,
        department="Department of Agriculture",
        requested_action="PROCUREMENT",
        ai_recommendation=procurement_decisions[eligible_vendor]["decision"],
        evidence_ids=[evidence_records[eligible_vendor].evidence_id],
        created_at=datetime.now(timezone.utc).isoformat(),
        requesting_officer_id="OFFICER-ALICE",
        department_authority_count=2,
    )
    auth_dec = create_authorization(
        request=auth_req,
        authorizing_officer_id="OFFICER-ALICE",
        human_decision="APPROVE",
        justification="All evidence gates, confidence benchmarks, and deployment strata verified.",
    )
    auth_history = get_authorization_history("AUTH-DEMO-001")

    human_auth_summary = {
        "authorization_id": auth_dec.authorization_id,
        "vendor_id": auth_dec.vendor_id,
        "requested_action": auth_dec.requested_action,
        "ai_recommendation": auth_dec.ai_recommendation,
        "human_decision": auth_dec.human_decision,
        "status": auth_dec.status,
        "authorizing_officer_id": auth_dec.authorizing_officer_id,
        "justification": auth_dec.justification,
        "audit_event_count": len(auth_history),
    }

    # --- STAGE 13: Scale-Up Evaluation (District Beta) ---
    pilot_twin_beta = create_pilot_twin(
        twin_id="TWIN-DISTRICT-BETA",
        department="Department of Agriculture",
        district="District Beta",
        parameters=[
            PilotParameter(name="connectivity", value="INTERMITTENT", evidence_level="OBSERVED", source="Telecom Log"),
            PilotParameter(name="device", value="LOW_END", evidence_level="OBSERVED", source="Inventory"),
            PilotParameter(name="language", value="REGIONAL", evidence_level="OBSERVED", source="Census"),
            PilotParameter(name="input_quality", value="NOISY", evidence_level="OBSERVED", source="Sensor Calibration"),
        ]
    )

    scale_req_vc = ScaleUpRequest(
        request_id="SCALE-REQ-VC-001",
        vendor_id="VendorC",
        target_department="Department of Agriculture",
        target_district="District Beta",
        existing_evidence_id=evidence_records["VendorC"].evidence_id,
        existing_artifact_id=artifact_records["VendorC"].artifact_id,
        requested_at=datetime.now(timezone.utc).isoformat(),
        reason="Scale expansion proposal to District Beta.",
    )

    # For scale matching with PilotTwin object, we provide deployment attributes
    class _PilotTwinView:
        def __init__(self, conn, dev, lang, qual):
            self.connectivity = conn
            self.device = dev
            self.language = lang
            self.input_quality = qual
            self.stratum_id = f"{conn}_{dev}_{lang}_{qual}"

    pt_view_beta = _PilotTwinView("INTERMITTENT", "LOW_END", "REGIONAL", "NOISY")

    scale_policy_res = evaluate_scale_policy(
        request=scale_req_vc,
        current_artifact_bytes=raw_artifacts["VendorC"],
        artifact_record=artifact_records["VendorC"],
        evidence_record=evidence_records["VendorC"],
        failure_map=failure_maps["VendorC"],
        pilot_twin=pt_view_beta,
        contract=contract,
    )

    scale_up_summary = {
        "request_id": scale_req_vc.request_id,
        "vendor_id": scale_req_vc.vendor_id,
        "target_district": scale_req_vc.target_district,
        "status": scale_policy_res.decision.status,
        "policy_case": scale_policy_res.policy_case,
        "scale_eligible": scale_policy_res.scale_eligible,
        "failure_map_status": scale_policy_res.decision.failure_map_status,
        "matched_failure_strata": scale_policy_res.decision.matched_failure_strata,
        "reasons": scale_policy_res.reasons,
        "vendor_response_window_required": scale_policy_res.vendor_response_window_required,
    }

    # --- Data Governance Schedule ---
    data_gov_sched = create_data_governance_schedule(
        contract_id=contract.contract_id,
        pilot_twin_id=pilot_twin.twin_id,
        citizen_data_owner="Department of Agriculture",
        citizen_data_classification="SENSITIVE",
        retention_days=365,
        deletion_required=True,
    )
    data_gov_summary = {
        "schedule_id": data_gov_sched.schedule_id,
        "startup_ip_owner": data_gov_sched.ip_schedule.startup_ip_owner,
        "government_evidence_owner": data_gov_sched.ip_schedule.government_evidence_owner,
        "citizen_data_owner": data_gov_sched.ip_schedule.citizen_data_owner,
        "model_access_mode": data_gov_sched.ip_schedule.model_access_mode,
        "retention_days": data_gov_sched.retention_days,
        "disclaimer": data_gov_sched.disclaimer,
    }

    # --- Audit Summary ---
    audit_summary = {
        "contract_locked": contract.locked,
        "twin_locked": pilot_twin.locked,
        "evaluator_authorized": eval_auth.status == "AUTHORIZED",
        "human_authorization_status": auth_dec.status,
        "scale_up_policy_case": scale_policy_res.policy_case,
    }

    return AxiomDemoResult(
        contract=contract_summary,
        pilot_twin=pilot_twin_summary,
        test_suite_summary=test_suite_summary,
        evaluator_status=evaluator_summary,
        vendor_results=vendor_results_summary,
        evidence_summary=evidence_summary,
        confidence_summary=confidence_summary,
        failure_map_summary=failure_map_summary,
        procurement_decisions=procurement_decisions,
        vendor_response=vendor_response_summary,
        human_authorization=human_auth_summary,
        scale_up_evaluation=scale_up_summary,
        data_governance=data_gov_summary,
        audit_summary=audit_summary,
    )
