"""
Scale-Up Trust Revalidation Policy

Consumes ScaleUpRequest, FailureMap, PilotTwin, ArtifactRecord, EvidenceRecord,
and OutcomeContract to evaluate regional scale-up safety.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from ai.scale_up import ScaleUpRequest, ScaleUpDecision, evaluate_scale_up_request
from ai.failure_cartography import FailureMap
from ai.schemas import OutcomeContract
from ai.evidence_record import EvidenceRecord

@dataclass
class ScalePolicyResult:
    decision: ScaleUpDecision
    policy_case: str
    scale_eligible: bool
    requires_human_review: bool
    requires_revalidation: bool
    vendor_response_window_required: bool
    reasons: List[str]

def evaluate_scale_policy(
    request: ScaleUpRequest,
    current_artifact_bytes: bytes,
    artifact_record: Any,
    evidence_record: Any,
    failure_map: FailureMap,
    pilot_twin: Any,
    contract: Optional[OutcomeContract] = None,
) -> ScalePolicyResult:
    """
    Evaluates scale policy according to multi-gate evidence governance rules.
    """
    decision = evaluate_scale_up_request(
        request=request,
        current_artifact_bytes=current_artifact_bytes,
        artifact_record=artifact_record,
        evidence_record=evidence_record,
        failure_map=failure_map,
        pilot_twin=pilot_twin,
    )

    reasons = list(decision.reasons)
    status = decision.status

    if decision.artifact_status == "MISMATCH":
        policy_case = "CASE_D_ARTIFACT_CHANGED"
        requires_revalidation = True
        scale_eligible = False
        requires_human_review = True
    elif decision.evidence_status == "EXPIRED":
        policy_case = "CASE_E_EVIDENCE_EXPIRED"
        requires_revalidation = True
        scale_eligible = False
        requires_human_review = True
    elif decision.pilot_twin_status == "UNVERIFIED":
        policy_case = "CASE_F_PILOT_TWIN_UNVERIFIED"
        requires_revalidation = False
        scale_eligible = False
        requires_human_review = True
    elif decision.failure_map_status == "CRITICAL_MATCH":
        policy_case = "CASE_C_CRITICAL_FAILURE_MATCH"
        requires_revalidation = False
        scale_eligible = False
        requires_human_review = True
    elif decision.failure_map_status in ("DEGRADED_MATCH", "WATCH_MATCH"):
        policy_case = "CASE_B_HOTSPOT_MATCH"
        requires_revalidation = False
        scale_eligible = (status == "SCALE_ELIGIBLE")
        requires_human_review = (status == "SCALE_REVIEW_REQUIRED")
    else:
        policy_case = "CASE_A_SAFE_SCALE"
        requires_revalidation = False
        scale_eligible = (status == "SCALE_ELIGIBLE")
        requires_human_review = False

    vendor_response_window = "VENDOR RESPONSE WINDOW REQUIRED" in reasons

    return ScalePolicyResult(
        decision=decision,
        policy_case=policy_case,
        scale_eligible=scale_eligible,
        requires_human_review=requires_human_review,
        requires_revalidation=requires_revalidation,
        vendor_response_window_required=vendor_response_window,
        reasons=reasons,
    )
