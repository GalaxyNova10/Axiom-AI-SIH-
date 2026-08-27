"""
Trust Invalidation Propagation Registry

Connects evaluator integrity to previously generated evidence.
Allows tracking evaluator states (AUTHORIZED, INVALIDATED, REVOKED),
retroactively flagging dependent evidence for revalidation without destroying history,
and checking in-flight evaluation authorization.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import copy
from ai.evidence_record import EvidenceRecord, mark_evidence_for_revalidation

ALLOWED_EVALUATOR_STATUSES = {"AUTHORIZED", "INVALIDATED", "REVOKED"}

@dataclass
class EvaluatorStatusRecord:
    evaluator_version: str
    status: str
    reason: str
    updated_at: str

# In-memory registry for prototype
_evaluator_status_registry: Dict[str, EvaluatorStatusRecord] = {}

def register_evaluator_status(
    evaluator_version: str,
    status: str,
    reason: str = "",
    updated_at: Optional[str] = None,
) -> EvaluatorStatusRecord:
    if not evaluator_version:
        raise ValueError("evaluator_version cannot be empty")
    if status not in ALLOWED_EVALUATOR_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Allowed: {sorted(ALLOWED_EVALUATOR_STATUSES)}"
        )
    
    ts = updated_at or datetime.now(timezone.utc).isoformat()
    record = EvaluatorStatusRecord(
        evaluator_version=evaluator_version,
        status=status,
        reason=reason,
        updated_at=ts,
    )
    _evaluator_status_registry[evaluator_version] = record
    return record

def get_evaluator_status(evaluator_version: str) -> str:
    if not evaluator_version:
        raise ValueError("evaluator_version cannot be empty")
    record = _evaluator_status_registry.get(evaluator_version)
    if record:
        return record.status
    # Default to AUTHORIZED if unknown in simple test mocks, or check
    return "UNKNOWN"

def invalidate_evaluator_version(
    evaluator_version: str,
    reason: str,
    updated_at: Optional[str] = None,
) -> EvaluatorStatusRecord:
    if not reason:
        raise ValueError("Reason for invalidation must be non-empty")
    return register_evaluator_status(
        evaluator_version=evaluator_version,
        status="INVALIDATED",
        reason=reason,
        updated_at=updated_at,
    )

def revoke_evaluator_version(
    evaluator_version: str,
    reason: str,
    updated_at: Optional[str] = None,
) -> EvaluatorStatusRecord:
    if not reason:
        raise ValueError("Reason for revocation must be non-empty")
    return register_evaluator_status(
        evaluator_version=evaluator_version,
        status="REVOKED",
        reason=reason,
        updated_at=updated_at,
    )

def check_evaluator_authorization(evaluator_version: str) -> bool:
    if not evaluator_version:
        return False
    status = get_evaluator_status(evaluator_version)
    if status == "UNKNOWN":
        # If not explicitly invalidated or registered, consider valid if version non-empty
        return True
    return status == "AUTHORIZED"

def check_in_flight_evaluator(evaluator_version: str) -> None:
    status = get_evaluator_status(evaluator_version)
    if status in ("INVALIDATED", "REVOKED"):
        raise ValueError("INTERRUPTED — EVALUATOR INVALIDATED MID-EVALUATION")

@dataclass
class EvidenceRevalidationEvent:
    event_id: str
    evidence_id: str
    evaluator_version: str
    previous_validation_status: str
    new_validation_status: str
    reason: str
    timestamp: str
    updated_evidence_record: EvidenceRecord

def invalidate_evidence_for_evaluator_version(
    evaluator_version: str,
    evidence_records: List[EvidenceRecord],
    timestamp: Optional[str] = None,
) -> List[EvidenceRevalidationEvent]:
    """
    For every evidence record matching the invalidated evaluator version,
    produces a revalidation event with updated representation.
    Historical evidence records are preserved immutably.
    """
    if not evaluator_version:
        raise ValueError("evaluator_version cannot be empty")

    ts = timestamp or datetime.now(timezone.utc).isoformat()
    required_reason = "EVALUATOR INTEGRITY UNDER REVIEW — RE-VALIDATION REQUIRED"
    events: List[EvidenceRevalidationEvent] = []

    for ev in evidence_records:
        if ev.evaluator_version == evaluator_version:
            updated_record = mark_evidence_for_revalidation(ev, required_reason)
            event = EvidenceRevalidationEvent(
                event_id=f"REVAL-EVT-{ev.evidence_id[:8]}",
                evidence_id=ev.evidence_id,
                evaluator_version=evaluator_version,
                previous_validation_status=ev.validation_status,
                new_validation_status="REVALIDATION_REQUIRED",
                reason=required_reason,
                timestamp=ts,
                updated_evidence_record=updated_record,
            )
            events.append(event)

    return events
