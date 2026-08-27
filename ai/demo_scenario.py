"""
Axiom AI Canonical Demo Scenario Module

Provides the canonical, deterministic demonstration scenario for frontend and SIH evaluators:
"Rural Agricultural Logistics — Evidence-Gated Procurement"

Demonstrates:
1. Government defines the Outcome Contract and locks KPIs.
2. Government Pilot Twin captures real-world rural operating conditions.
3. Private Test Matrix evaluates three distinct vendor architectures.
4. Evaluator self-verifies on Golden Reference Suite before running.
5. Failure Cartography maps exact stratum breakdown points.
6. Forensic Evaluation Intelligence diagnoses multi-factor failure interactions.
7. Deterministic Procurement Engine gates eligibility without LLM bias.
8. Human Authorization retains final decision-making authority.
9. Scale-Up Engine prevents hazardous deployment expansion into matching failure profiles.
"""

from typing import Dict, Any, List, Optional
import copy

from ai.pipeline import run_axiom_demo, AxiomDemoResult


# ============================================================
# CANONICAL DEMO METADATA
# ============================================================

CANONICAL_SCENARIO_ID = "AXIOM-DEMO-001"
CANONICAL_SCENARIO_NAME = "Rural Agricultural Logistics — Evidence-Gated Procurement"
CANONICAL_DEPARTMENT = "Department of Agricultural Logistics"
CANONICAL_DISTRICT = "Rural Demonstration District"
CANONICAL_PROBLEM_STATEMENT = (
    "Improve last-mile delivery of agricultural supplies across rural districts while reducing "
    "delivery delays and maintaining reliable service under intermittent connectivity, low-end "
    "devices, regional languages, and degraded input conditions."
)

DEMO_VENDORS_METADATA = [
    {
        "vendor_id": "VendorA",
        "display_name": "AgriRoute Systems",
        "description": "High-throughput route optimizer with standard device focus",
        "profile": "Strong performance on standard hardware; degrades under noisy regional conditions."
    },
    {
        "vendor_id": "VendorB",
        "display_name": "RuralFlow AI",
        "description": "Offline-first resilient routing engine designed for intermittent connectivity",
        "profile": "Robust intermittent-connectivity performance; satisfies rural baseline criteria."
    },
    {
        "vendor_id": "VendorC",
        "display_name": "KrishiLink Technologies",
        "description": "Deep learning vernacular voice/text dispatch platform",
        "profile": "High overall benchmark score, but suffers acute compound failure on NOISY + LOW_END + REGIONAL."
    },
]

VENDOR_DISPLAY_NAMES = {v["vendor_id"]: v["display_name"] for v in DEMO_VENDORS_METADATA}


# ============================================================
# SANITIZATION HELPER
# ============================================================

FORBIDDEN_SENSITIVE_KEYS = frozenset({
    "private_parameters",
    "raw_seed",
    "seed",
    "seed_hash",
    "secret",
    "private_key",
    "api_key",
    "openai_api_key",
    "model_weights",
    "source_code",
})


def _sanitize_public_payload(obj: Any) -> Any:
    """
    Recursively scrubs any private parameters, raw seeds, or sensitive keys.
    """
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            if str(k).lower() in FORBIDDEN_SENSITIVE_KEYS:
                continue
            clean[k] = _sanitize_public_payload(v)
        return clean
    elif isinstance(obj, list):
        return [_sanitize_public_payload(item) for item in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return _sanitize_public_payload(asdict(obj))
    return obj


# ============================================================
# PUBLIC SCENARIO INTERFACE
# ============================================================

def get_demo_scenario_metadata() -> Dict[str, Any]:
    """
    Returns the public metadata describing the canonical demonstration scenario.
    """
    return {
        "scenario_id": CANONICAL_SCENARIO_ID,
        "scenario_name": CANONICAL_SCENARIO_NAME,
        "title": CANONICAL_SCENARIO_NAME,
        "problem_statement": CANONICAL_PROBLEM_STATEMENT,
        "department": CANONICAL_DEPARTMENT,
        "district": CANONICAL_DISTRICT,
        "description": (
            "Canonical demonstration scenario evaluating three AI logistics solutions "
            "under realistic rural deployment conditions."
        ),
        "vendors": copy.deepcopy(DEMO_VENDORS_METADATA),
        "key_conditions": {
            "connectivity": ["GOOD", "INTERMITTENT"],
            "device": ["HIGH_END", "LOW_END"],
            "language": ["STANDARD", "REGIONAL"],
            "input_quality": ["CLEAN", "DEGRADED", "NOISY"],
        },
        "expected_demo_story": (
            "Demonstrates how Axiom AI evaluates three solutions across 24 deployment strata, "
            "identifies compound failure modes using Failure Cartography, explains operational "
            "risks using forensic diagnostic intelligence, applies deterministic procurement gates, "
            "records human authorization, and prevents unsafe regional scale-up."
        ),
    }


def format_demo_summary(
    result: AxiomDemoResult,
    scenario_meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Formats an AxiomDemoResult into a stable, presentation-ready JSON dictionary
    strictly conforming to the frontend contract.
    """
    meta = scenario_meta or get_demo_scenario_metadata()
    public_dict = result.to_public_dict()

    # Build vendor scorecard list
    vendors_list = []
    failure_maps_list = []
    diagnostics_list = []

    for v_meta in meta.get("vendors", []):
        vid = v_meta["vendor_id"]
        v_res = public_dict.get("vendor_results", {}).get(vid, {})
        v_ev = public_dict.get("evidence_summary", {}).get(vid, {})
        v_conf = public_dict.get("confidence_summary", {}).get(vid, {})
        v_proc = public_dict.get("procurement_decisions", {}).get(vid, {})
        v_fm = public_dict.get("failure_map_summary", {}).get(vid, {})
        v_diag = public_dict.get("diagnostic_intelligence", {}).get(vid, {})

        # Find top hotspot
        hotspots = v_fm.get("hotspots", [])
        top_hotspot = hotspots[0] if hotspots else None

        vendors_list.append({
            "vendor_id": vid,
            "display_name": v_meta["display_name"],
            "description": v_meta.get("description", ""),
            "evaluation_id": v_res.get("evaluation_id"),
            "accuracy": v_res.get("accuracy"),
            "latency": v_res.get("average_latency_ms"),
            "error_count": v_res.get("error_count"),
            "evidence_level": v_ev.get("evidence_level"),
            "evidence_confidence": v_conf.get("score"),
            "overall_status": v_fm.get("overall_status", "NORMAL"),
            "top_failure_hotspot": top_hotspot,
            "diagnostic_summary": v_diag.get("overall_verdict_explanation", ""),
            "procurement_recommendation": v_proc.get("decision", "PENDING"),
        })

        failure_maps_list.append({
            "vendor_id": vid,
            "display_name": v_meta["display_name"],
            "overall_status": v_fm.get("overall_status", "NORMAL"),
            "overall_accuracy": v_fm.get("overall_accuracy"),
            "total_strata": v_fm.get("total_strata", 24),
            "critical_hotspots_count": v_fm.get("critical_hotspots_count", 0),
            "degraded_hotspots_count": v_fm.get("degraded_hotspots_count", 0),
            "watch_hotspots_count": v_fm.get("watch_hotspots_count", 0),
            "hotspots": hotspots,
            "explanation": v_fm.get("explanation", {}),
        })

        diagnostics_list.append({
            "vendor_id": vid,
            "display_name": v_meta["display_name"],
            "analysis_mode": v_diag.get("analysis_mode", "DETERMINISTIC_FALLBACK"),
            "overall_verdict_explanation": v_diag.get("overall_verdict_explanation", ""),
            "operational_risk_summary": v_diag.get("operational_risk_summary", ""),
            "compound_hotspot_diagnoses": v_diag.get("compound_hotspot_diagnoses", []),
            "recommended_vendor_challenges": v_diag.get("recommended_vendor_challenges", []),
            "targeted_retest_recommendations": v_diag.get("targeted_retest_recommendations", []),
        })

    summary = {
        "scenario": meta,
        "outcome_contract": public_dict.get("contract", {}),
        "pilot_twin": public_dict.get("pilot_twin", {}),
        "evaluation": {
            "test_suite_summary": public_dict.get("test_suite_summary", {}),
            "evaluator_status": public_dict.get("evaluator_status", {}),
        },
        "vendors": vendors_list,
        "failure_maps": failure_maps_list,
        "diagnostics": diagnostics_list,
        "procurement": public_dict.get("procurement_decisions", {}),
        "scale_up": public_dict.get("scale_up_evaluation", {}),
        "human_authorization": public_dict.get("human_authorization", {}),
        "data_governance": public_dict.get("data_governance", {}),
        "audit_summary": public_dict.get("audit_summary", {}),
    }

    return _sanitize_public_payload(summary)


def run_demo_scenario(seed: int = 42) -> Dict[str, Any]:
    """
    Executes the canonical Axiom demonstration scenario and returns the
    sanitized, presentation-ready frontend contract.
    """
    meta = get_demo_scenario_metadata()
    pipeline_result = run_axiom_demo(
        problem_statement=meta["problem_statement"],
        seed=seed,
    )
    return format_demo_summary(pipeline_result, scenario_meta=meta)
