"""
Axiom AI FastAPI Application Service

Provides a clean, evidence-governed API layer for frontend clients to:
1. Submit problem statements and trigger the Axiom demonstration pipeline.
2. Retrieve structured evaluation results, vendor scorecards, and failure maps.
3. Access forensic Diagnostic Intelligence (Step 2/3 intelligence layer).
4. Inspect deterministic procurement and scale-up decisions.
5. Record human authorization decisions with strict maker-checker governance.

All business and governance calculations remain strictly within ai/* modules.
FastAPI acts solely as a safe presentation and integration layer.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.pipeline import run_axiom_demo, AxiomDemoResult
from ai.demo_scenario import get_demo_scenario_metadata, run_demo_scenario
from ai.human_authorization import (
    AuthorizationRequest as HumanAuthRequest,
    create_authorization,
    get_authorization_history,
)

# ============================================================
# FASTAPI APP & CORS CONFIGURATION
# ============================================================

app = FastAPI(
    title="Axiom AI",
    description="Evidence-Governed Innovation Procurement Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# IN-MEMORY PROTOTYPE REGISTRY
# ============================================================
# Note: For this hackathon prototype, evaluation runs and authorizations
# are stored in an in-memory dictionary. Production implementations
# will replace this with persistent append-only database storage.

_evaluations: Dict[str, Dict[str, Any]] = {}
_latest_demo_result: Optional[AxiomDemoResult] = None


# ============================================================
# SAFE SERIALIZATION LAYER
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


def safe_serialize(obj: Any) -> Any:
    """
    Recursively serializes python objects to JSON-safe structures while
    strictly scrubbing any sensitive parameters, seeds, or secrets.
    """
    if isinstance(obj, dict):
        clean = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if k_lower in FORBIDDEN_SENSITIVE_KEYS:
                continue
            clean[k] = safe_serialize(v)
        return clean
    elif isinstance(obj, list):
        return [safe_serialize(item) for item in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return safe_serialize(asdict(obj))
    elif hasattr(obj, "dict") and callable(getattr(obj, "dict")):
        return safe_serialize(obj.dict())
    return obj


# ============================================================
# PYDANTIC REQUEST / RESPONSE MODELS
# ============================================================

class EvaluateRequest(BaseModel):
    problem_statement: str = Field(
        default="Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays.",
        description="Government operational problem description",
    )
    department: Optional[str] = Field(
        default="Department of Agriculture",
        description="Purchasing government department",
    )
    district: Optional[str] = Field(
        default="District Alpha",
        description="Target administrative district for pilot deployment",
    )
    seed: Optional[int] = Field(
        default=42,
        description="Deterministic evaluation seed",
    )


class AuthorizationActionRequest(BaseModel):
    vendor_id: str = Field(..., description="Target vendor identifier")
    action: str = Field(..., description="Action: APPROVE, REJECT, REQUEST_RETEST, or OVERRIDE")
    officer_id: str = Field(..., description="Authorizing officer ID")
    justification: str = Field(..., description="Mandatory governance justification")
    requested_action: Optional[str] = Field(
        default="PROCUREMENT",
        description="Action type: PROCUREMENT or SCALE_UP",
    )


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get(
    "/health",
    summary="Health check",
    description="Returns the operational status and service identity of Axiom AI.",
    tags=["System"],
)
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "Axiom AI",
    }


# ============================================================
# EVALUATION WORKFLOW ENDPOINTS (API V1)
# ============================================================

@app.post(
    "/api/v1/evaluate",
    summary="Run an Axiom evidence-gated evaluation",
    description="Executes the full 14-stage Axiom governance demo pipeline and returns the complete result.",
    tags=["Evaluations"],
)
def evaluate_problem(request: EvaluateRequest) -> Dict[str, Any]:
    global _latest_demo_result

    if not request.problem_statement or not request.problem_statement.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="problem_statement cannot be empty",
        )

    # Execute deterministic governance pipeline
    seed_val = request.seed if request.seed is not None else 42
    result = run_axiom_demo(
        problem_statement=request.problem_statement,
        seed=seed_val,
    )
    _latest_demo_result = result

    # Generate top-level evaluation tracking ID
    evaluation_id = f"eval_{uuid.uuid4().hex[:12]}"

    public_result = result.to_public_dict()
    public_result["evaluation_id"] = evaluation_id
    public_result["submitted_problem_statement"] = request.problem_statement
    public_result["department"] = request.department or "Department of Agriculture"
    public_result["district"] = request.district or "District Alpha"
    public_result["created_at"] = datetime.now(timezone.utc).isoformat()

    # Store in prototype registry
    _evaluations[evaluation_id] = public_result

    return safe_serialize(public_result)


@app.get(
    "/api/v1/evaluations/{evaluation_id}",
    summary="Retrieve full evaluation result",
    description="Returns the stored evaluation record for the specified evaluation ID.",
    tags=["Evaluations"],
)
def get_evaluation(evaluation_id: str) -> Dict[str, Any]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )
    return safe_serialize(_evaluations[evaluation_id])


@app.get(
    "/api/v1/evaluations/{evaluation_id}/vendors",
    summary="Retrieve vendor scorecards",
    description="Returns a frontend-friendly list of vendor performance metrics, hotspots, and procurement recommendations.",
    tags=["Evaluations"],
)
def get_evaluation_vendors(evaluation_id: str) -> List[Dict[str, Any]]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )

    eval_data = _evaluations[evaluation_id]
    vendor_results = eval_data.get("vendor_results", {})
    failure_maps = eval_data.get("failure_map_summary", {})
    procurement = eval_data.get("procurement_decisions", {})
    evidence = eval_data.get("evidence_summary", {})
    confidence = eval_data.get("confidence_summary", {})
    diagnostics = eval_data.get("diagnostic_intelligence", {})

    vendors_list = []
    for vid, vdata in vendor_results.items():
        fm = failure_maps.get(vid, {})
        diag = diagnostics.get(vid, {})

        vendors_list.append({
            "vendor_id": vid,
            "evaluation_id": vdata.get("evaluation_id"),
            "accuracy": vdata.get("accuracy"),
            "latency": vdata.get("average_latency_ms"),
            "error_count": vdata.get("error_count"),
            "overall_failure_status": fm.get("overall_status", "NORMAL"),
            "failure_hotspots": fm.get("hotspots", []),
            "diagnostic_summary": diag.get("overall_verdict_explanation", ""),
            "evidence_confidence": confidence.get(vid, {}).get("score"),
            "procurement_recommendation": procurement.get(vid, {}).get("decision", "PENDING"),
            "evidence_level": evidence.get(vid, {}).get("evidence_level"),
        })

    return safe_serialize(vendors_list)


@app.get(
    "/api/v1/evaluations/{evaluation_id}/diagnostics",
    summary="Retrieve forensic diagnostic intelligence",
    description="Returns the structured forensic DiagnosticReport generated by the AI evaluation intelligence layer.",
    tags=["Diagnostics"],
)
def get_evaluation_diagnostics(evaluation_id: str) -> Dict[str, Any]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )
    diag_data = _evaluations[evaluation_id].get("diagnostic_intelligence", {})
    return safe_serialize(diag_data)


@app.get(
    "/api/v1/evaluations/{evaluation_id}/failure-map",
    summary="Retrieve Failure Cartography",
    description="Returns sanitized multi-stratum failure cartography mapping operational hotspots and severity levels.",
    tags=["Failure Cartography"],
)
def get_evaluation_failure_map(evaluation_id: str) -> Dict[str, Any]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )
    fm_data = _evaluations[evaluation_id].get("failure_map_summary", {})
    return safe_serialize(fm_data)


@app.get(
    "/api/v1/evaluations/{evaluation_id}/decision",
    summary="Retrieve deterministic procurement decisions",
    description="Returns the deterministic gate results and final procurement recommendations. Strictly read-only.",
    tags=["Procurement"],
)
def get_evaluation_decision(evaluation_id: str) -> Dict[str, Any]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )
    proc_data = _evaluations[evaluation_id].get("procurement_decisions", {})
    return safe_serialize(proc_data)


@app.post(
    "/api/v1/evaluations/{evaluation_id}/authorization",
    summary="Record human authorization decision",
    description="Applies maker-checker and override governance rules to record human authorization.",
    tags=["Authorization"],
)
def submit_human_authorization(
    evaluation_id: str,
    action_req: AuthorizationActionRequest,
) -> Dict[str, Any]:
    if evaluation_id not in _evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Evaluation not found", "evaluation_id": evaluation_id},
        )

    eval_data = _evaluations[evaluation_id]
    vendor_id = action_req.vendor_id
    procurement = eval_data.get("procurement_decisions", {})

    if vendor_id not in procurement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vendor '{vendor_id}' is not part of evaluation '{evaluation_id}'",
        )

    ai_rec = procurement[vendor_id].get("decision", "REJECTED")
    evidence_summary = eval_data.get("evidence_summary", {})
    ev_id = evidence_summary.get(vendor_id, {}).get("evidence_id", f"EVID-{vendor_id}-001")

    # Construct Human Authorization Request object
    auth_id = f"AUTH-{uuid.uuid4().hex[:8]}"
    dec_id = f"DEC-{uuid.uuid4().hex[:8]}"

    try:
        auth_req = HumanAuthRequest(
            authorization_id=auth_id,
            decision_id=dec_id,
            vendor_id=vendor_id,
            department=eval_data.get("department", "Department of Agriculture"),
            requested_action=action_req.requested_action or "PROCUREMENT",
            ai_recommendation=ai_rec,
            evidence_ids=[ev_id],
            created_at=datetime.now(timezone.utc).isoformat(),
            requesting_officer_id=action_req.officer_id,
            department_authority_count=2,
        )

        auth_dec = create_authorization(
            request=auth_req,
            authorizing_officer_id=action_req.officer_id,
            human_decision=action_req.action,
            justification=action_req.justification,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )

    auth_history = get_authorization_history(auth_id)

    auth_summary = {
        "authorization_id": auth_dec.authorization_id,
        "vendor_id": auth_dec.vendor_id,
        "requested_action": auth_dec.requested_action,
        "ai_recommendation": auth_dec.ai_recommendation,
        "human_decision": auth_dec.human_decision,
        "status": auth_dec.status,
        "authorizing_officer_id": auth_dec.authorizing_officer_id,
        "justification": auth_dec.justification,
        "escalation_required": auth_dec.escalation_required,
        "escalation_destination": auth_dec.escalation_destination,
        "audit_event_count": len(auth_history),
    }

    # Update stored evaluation state
    eval_data["human_authorization"] = auth_summary
    return safe_serialize(auth_summary)


# ============================================================
# CANONICAL DEMO SCENARIO ENDPOINTS
# ============================================================

@app.get(
    "/api/v1/demo/scenario",
    summary="Retrieve canonical demo scenario metadata",
    description="Returns public configuration and problem definitions for the canonical agricultural logistics demo scenario.",
    tags=["Demo Scenario"],
)
def get_demo_scenario() -> Dict[str, Any]:
    return safe_serialize(get_demo_scenario_metadata())


@app.post(
    "/api/v1/demo/evaluate",
    summary="Run canonical demonstration evaluation",
    description="Executes the canonical demonstration scenario and returns the presentation-ready frontend contract summary.",
    tags=["Demo Scenario"],
)
def evaluate_demo_scenario(seed: Optional[int] = 42) -> Dict[str, Any]:
    seed_val = seed if seed is not None else 42
    summary = run_demo_scenario(seed=seed_val)
    return safe_serialize(summary)


# ============================================================
# LEGACY DEMO ENDPOINTS (BACKWARD COMPATIBILITY)
# ============================================================

@app.post(
    "/api/demo/run",
    summary="Legacy demo run endpoint",
    tags=["Legacy"],
)
def run_demo(problem_statement: Optional[str] = None, seed: int = 42) -> Dict[str, Any]:
    global _latest_demo_result
    ps = problem_statement or "Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays."
    result = run_axiom_demo(problem_statement=ps, seed=seed)
    _latest_demo_result = result
    return result.to_public_dict()


@app.get(
    "/api/demo/summary",
    summary="Legacy demo summary endpoint",
    tags=["Legacy"],
)
def get_demo_summary() -> Dict[str, Any]:
    global _latest_demo_result
    if _latest_demo_result is None:
        _latest_demo_result = run_axiom_demo()

    res = _latest_demo_result
    vendors_list = []
    for vid, vdata in res.vendor_results.items():
        vendors_list.append({
            "vendor_id": vid,
            "accuracy": vdata.get("accuracy"),
            "average_latency_ms": vdata.get("average_latency_ms"),
            "procurement_decision": res.procurement_decisions.get(vid, {}).get("decision"),
            "evidence_level": res.evidence_summary.get(vid, {}).get("evidence_level"),
        })

    all_hotspots = []
    for vid, fm in res.failure_map_summary.items():
        for hs in fm.get("hotspots", []):
            all_hotspots.append({
                "vendor_id": vid,
                "stratum_id": hs.get("stratum_id"),
                "severity": hs.get("severity"),
                "accuracy": hs.get("accuracy"),
                "reason": hs.get("reason"),
            })

    return {
        "contract": res.contract,
        "pilot_twin": res.pilot_twin,
        "vendors": vendors_list,
        "evidence_confidence": {vid: cdata.get("score") for vid, cdata in res.confidence_summary.items()},
        "failure_hotspots": all_hotspots,
        "procurement": res.procurement_decisions,
        "scale_up": res.scale_up_evaluation,
        "authorization": res.human_authorization,
    }
