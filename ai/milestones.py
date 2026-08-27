"""
Procurement Milestone Gating

Manages milestone-based contracting, evidence gating for payments,
and human authorization for payment release.
NEVER directly transfers money or accesses banking APIs.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Any
import copy
from ai.schemas import OutcomeContract
from ai.evidence_record import EvidenceRecord

ALLOWED_MILESTONE_STATUSES = {
    "PENDING",
    "EVIDENCE_REQUIRED",
    "READY_FOR_AUTHORIZATION",
    "AUTHORIZED",
    "BLOCKED",
    "REVALIDATION_REQUIRED",
}

PLACEHOLDER_JUSTIFICATIONS = {"", "N/A", "none"}

@dataclass
class ProcurementMilestone:
    milestone_id: str
    contract_id: str
    vendor_id: str
    name: str
    required_kpi: str
    threshold_operator: str
    threshold_value: float
    required_evidence_level: str
    payment_percentage: float
    status: str
    evidence_id: Optional[str]
    created_at: str
    authorized_by: Optional[str] = None
    authorized_at: Optional[str] = None
    reasons: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.milestone_id:
            raise ValueError("milestone_id cannot be empty")
        if not self.contract_id:
            raise ValueError("contract_id cannot be empty")
        if not self.vendor_id:
            raise ValueError("vendor_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not (0.0 <= self.payment_percentage <= 100.0):
            raise ValueError("payment_percentage must be between 0.0 and 100.0")
        if self.status not in ALLOWED_MILESTONE_STATUSES:
            raise ValueError(
                f"Invalid status '{self.status}'. Allowed: {sorted(ALLOWED_MILESTONE_STATUSES)}"
            )

def evaluate_milestone(
    milestone: ProcurementMilestone,
    contract: OutcomeContract,
    evidence_record: Optional[EvidenceRecord],
    artifact_verified: bool,
    evidence_valid: bool,
    evidence_confidence: float,
) -> ProcurementMilestone:
    """
    Evaluates milestone readiness. Returns a new updated milestone copy.
    """
    updated = copy.deepcopy(milestone)
    updated.reasons = []

    # Check evidence existence
    if evidence_record is None:
        updated.status = "EVIDENCE_REQUIRED"
        updated.reasons.append("No evidence record provided for milestone gating.")
        return updated

    updated.evidence_id = evidence_record.evidence_id

    # Check artifact verification
    if not artifact_verified:
        updated.status = "REVALIDATION_REQUIRED"
        updated.reasons.append("Artifact mismatch detected — revalidation required.")
        return updated

    # Check evidence validity
    if not evidence_valid or evidence_record.validation_status == "REVALIDATION_REQUIRED":
        updated.status = "REVALIDATION_REQUIRED"
        updated.reasons.append("Evidence is invalid or expired — revalidation required.")
        return updated

    # Check evidence level
    # E.g., if milestone requires INDEPENDENTLY_VALIDATED, check match
    if milestone.required_evidence_level == "INDEPENDENTLY_VALIDATED":
        if evidence_record.evidence_level != "INDEPENDENTLY_VALIDATED":
            updated.status = "BLOCKED"
            updated.reasons.append(
                f"Required evidence level '{milestone.required_evidence_level}' not met "
                f"(current: '{evidence_record.evidence_level}')."
            )
            return updated

    # Check evidence confidence against contract
    if evidence_confidence < contract.minimum_evidence_confidence:
        updated.status = "BLOCKED"
        updated.reasons.append(
            f"Evidence confidence {evidence_confidence}% is below contract threshold {contract.minimum_evidence_confidence}%."
        )
        return updated

    # Check KPI threshold
    actual_value = evidence_record.metric_value
    req_value = milestone.threshold_value
    op = milestone.threshold_operator

    kpi_passed = False
    if op == ">=":
        kpi_passed = actual_value >= req_value
    elif op == "<=":
        kpi_passed = actual_value <= req_value
    elif op == ">":
        kpi_passed = actual_value > req_value
    elif op == "<":
        kpi_passed = actual_value < req_value
    elif op == "==":
        kpi_passed = actual_value == req_value
    else:
        kpi_passed = actual_value >= req_value

    if not kpi_passed:
        updated.status = "BLOCKED"
        updated.reasons.append(
            f"KPI threshold failed: {evidence_record.metric_name} = {actual_value}; required {op} {req_value}."
        )
        return updated

    # All gates passed -> READY_FOR_AUTHORIZATION
    updated.status = "READY_FOR_AUTHORIZATION"
    updated.reasons.append("All evidence, artifact, confidence, and KPI requirements verified.")
    return updated

def authorize_milestone_payment(
    milestone: ProcurementMilestone,
    authorizing_officer_id: str,
    justification: str,
    authorized_at: Optional[str] = None,
) -> ProcurementMilestone:
    """
    Records human authorization for milestone payment release.
    Does NOT transfer real funds.
    """
    if not authorizing_officer_id:
        raise ValueError("authorizing_officer_id cannot be empty")
    if justification in PLACEHOLDER_JUSTIFICATIONS:
        raise ValueError("Justification cannot be empty or placeholder")
    if milestone.status != "READY_FOR_AUTHORIZATION":
        raise ValueError(
            f"Cannot authorize payment for milestone with status '{milestone.status}'. "
            f"Must be 'READY_FOR_AUTHORIZATION'."
        )

    ts = authorized_at or datetime.now(timezone.utc).isoformat()
    updated = copy.deepcopy(milestone)
    updated.status = "AUTHORIZED"
    updated.authorized_by = authorizing_officer_id
    updated.authorized_at = ts
    updated.reasons.append("PAYMENT_AUTHORIZED_FOR_RELEASE")
    return updated

def invalidate_milestone_for_evidence(
    milestone: ProcurementMilestone,
    reason: str,
) -> ProcurementMilestone:
    updated = copy.deepcopy(milestone)
    updated.status = "REVALIDATION_REQUIRED"
    updated.reasons.append(reason)
    return updated
