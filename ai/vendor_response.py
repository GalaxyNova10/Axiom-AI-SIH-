"""
Vendor Response / Challenge Window

Provides a formal, auditable mechanism for a vendor to respond to:
    SCALE_REVIEW_REQUIRED
    DO_NOT_SCALE_YET
    REVALIDATION_REQUIRED

Core principle:
    VENDOR MAY RESPOND.
    VENDOR MAY REQUEST RE-VALIDATION.
    VENDOR MAY PROVIDE EVIDENCE.
    VENDOR MAY NOT ALTER THE RECORD.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import copy
import uuid

# --- Constants ---

ALLOWED_RESPONSE_TYPES = frozenset({
    "CLARIFICATION",
    "CONTEST_FAILURE",
    "REQUEST_REVALIDATION",
    "SUBMIT_EVIDENCE",
})

ALLOWED_REQUESTED_ACTIONS = frozenset({
    "NO_ACTION",
    "REVIEW",
    "TARGETED_REVALIDATION",
    "FULL_REVALIDATION",
})

ALLOWED_RESPONSE_STATUSES = frozenset({
    "SUBMITTED",
    "UNDER_REVIEW",
    "ACCEPTED",
    "REJECTED",
})

RESPONDABLE_DECISION_STATUSES = frozenset({
    "SCALE_REVIEW_REQUIRED",
    "DO_NOT_SCALE_YET",
    "REVALIDATION_REQUIRED",
})

ALLOWED_REVIEWER_DECISIONS = frozenset({
    "ACCEPT",
    "REJECT",
    "REQUEST_MORE_INFORMATION",
})

REVIEWER_DECISION_TO_STATUS = {
    "ACCEPT": "ACCEPTED",
    "REJECT": "REJECTED",
    "REQUEST_MORE_INFORMATION": "UNDER_REVIEW",
}

ALLOWED_AUDIT_EVENT_TYPES = frozenset({
    "SUBMITTED",
    "REVIEW_STARTED",
    "ACCEPTED",
    "REJECTED",
    "MORE_INFORMATION_REQUESTED",
})


# --- Data Structures ---

@dataclass
class VendorResponse:
    response_id: str
    vendor_id: str
    request_id: str
    decision_status: str
    submitted_at: str
    response_type: str
    explanation: str
    supporting_evidence_ids: List[str]
    requested_action: str
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_reason: Optional[str] = None


@dataclass
class ResponseAuditEvent:
    event_id: str
    response_id: str
    event_type: str
    actor_id: str
    timestamp: str
    reason: str


# --- Internal audit storage (per-response) ---

_audit_registry: dict = {}


def _generate_event_id() -> str:
    return f"EVT-{uuid.uuid4().hex[:12]}"


def _record_audit_event(
    response_id: str,
    event_type: str,
    actor_id: str,
    reason: str,
    timestamp: Optional[str] = None,
) -> ResponseAuditEvent:
    if event_type not in ALLOWED_AUDIT_EVENT_TYPES:
        raise ValueError(f"Unknown audit event type: {event_type}")

    ts = timestamp or datetime.now(timezone.utc).isoformat()

    event = ResponseAuditEvent(
        event_id=_generate_event_id(),
        response_id=response_id,
        event_type=event_type,
        actor_id=actor_id,
        timestamp=ts,
        reason=reason,
    )

    if response_id not in _audit_registry:
        _audit_registry[response_id] = []
    _audit_registry[response_id].append(event)

    return event


# --- Consistency rules ---

def _validate_consistency(response_type: str, requested_action: str, evidence_ids: List[str]) -> None:
    if response_type == "REQUEST_REVALIDATION":
        if requested_action not in ("TARGETED_REVALIDATION", "FULL_REVALIDATION"):
            raise ValueError(
                "REQUEST_REVALIDATION response_type requires requested_action "
                "to be TARGETED_REVALIDATION or FULL_REVALIDATION"
            )

    if response_type == "CLARIFICATION":
        if requested_action not in ("REVIEW", "NO_ACTION"):
            raise ValueError(
                "CLARIFICATION response_type requires requested_action to be REVIEW or NO_ACTION"
            )

    if response_type == "CONTEST_FAILURE":
        if requested_action not in ("REVIEW", "TARGETED_REVALIDATION"):
            raise ValueError(
                "CONTEST_FAILURE response_type requires requested_action "
                "to be REVIEW or TARGETED_REVALIDATION"
            )

    if response_type == "SUBMIT_EVIDENCE":
        if not evidence_ids:
            raise ValueError(
                "SUBMIT_EVIDENCE response_type requires at least one supporting_evidence_id"
            )


# --- Public API ---

def submit_vendor_response(
    vendor_id: str,
    request_id: str,
    decision_status: str,
    response_type: str,
    explanation: str,
    requested_action: str,
    supporting_evidence_ids: Optional[List[str]] = None,
    submitted_at: Optional[str] = None,
    response_id: Optional[str] = None,
) -> VendorResponse:
    """Create and validate a new vendor response."""

    # Identity validation
    if not vendor_id:
        raise ValueError("vendor_id cannot be empty")
    if not request_id:
        raise ValueError("request_id cannot be empty")
    if not explanation:
        raise ValueError("explanation cannot be empty")

    # Decision status restriction
    if decision_status not in RESPONDABLE_DECISION_STATUSES:
        raise ValueError(
            f"Cannot respond to decision status '{decision_status}'. "
            f"Allowed: {sorted(RESPONDABLE_DECISION_STATUSES)}"
        )

    # Response type validation
    if response_type not in ALLOWED_RESPONSE_TYPES:
        raise ValueError(
            f"Unknown response_type '{response_type}'. "
            f"Allowed: {sorted(ALLOWED_RESPONSE_TYPES)}"
        )

    # Requested action validation
    if requested_action not in ALLOWED_REQUESTED_ACTIONS:
        raise ValueError(
            f"Unknown requested_action '{requested_action}'. "
            f"Allowed: {sorted(ALLOWED_REQUESTED_ACTIONS)}"
        )

    evidence_ids = supporting_evidence_ids or []

    # Consistency validation
    _validate_consistency(response_type, requested_action, evidence_ids)

    ts = submitted_at or datetime.now(timezone.utc).isoformat()
    rid = response_id or f"RESP-{uuid.uuid4().hex[:12]}"

    response = VendorResponse(
        response_id=rid,
        vendor_id=vendor_id,
        request_id=request_id,
        decision_status=decision_status,
        submitted_at=ts,
        response_type=response_type,
        explanation=explanation,
        supporting_evidence_ids=list(evidence_ids),
        requested_action=requested_action,
        status="SUBMITTED",
        reviewed_by=None,
        reviewed_at=None,
        review_reason=None,
    )

    # Record audit event
    _record_audit_event(
        response_id=response.response_id,
        event_type="SUBMITTED",
        actor_id=vendor_id,
        reason=f"Vendor response submitted: {response_type}",
        timestamp=ts,
    )

    return response


def validate_response_binding(
    response: VendorResponse,
    expected_vendor_id: str,
    expected_request_id: str,
) -> None:
    """Validate that a response belongs to the expected vendor and request."""
    if response.vendor_id != expected_vendor_id:
        raise ValueError(
            f"Response vendor_id '{response.vendor_id}' does not match "
            f"expected '{expected_vendor_id}'"
        )
    if response.request_id != expected_request_id:
        raise ValueError(
            f"Response request_id '{response.request_id}' does not match "
            f"expected '{expected_request_id}'"
        )


def review_vendor_response(
    response: VendorResponse,
    reviewer_id: str,
    decision: str,
    review_reason: str,
    reviewed_at: Optional[str] = None,
) -> VendorResponse:
    """Review a vendor response. Returns an updated copy."""

    # Reviewer validation
    if not reviewer_id:
        raise ValueError("reviewer_id cannot be empty")
    if not review_reason:
        raise ValueError("review_reason cannot be empty")

    # Separation of duties
    if reviewer_id == response.vendor_id:
        raise ValueError("Reviewer cannot be the same as the vendor")

    # Decision validation
    if decision not in ALLOWED_REVIEWER_DECISIONS:
        raise ValueError(
            f"Unknown reviewer decision '{decision}'. "
            f"Allowed: {sorted(ALLOWED_REVIEWER_DECISIONS)}"
        )

    # Immutability: already finalized responses cannot be re-reviewed
    if response.status in ("ACCEPTED", "REJECTED"):
        raise ValueError(
            f"Response is already '{response.status}' and cannot be reviewed again"
        )

    ts = reviewed_at or datetime.now(timezone.utc).isoformat()
    new_status = REVIEWER_DECISION_TO_STATUS[decision]

    # Determine audit event type
    if decision == "ACCEPT":
        audit_event_type = "ACCEPTED"
    elif decision == "REJECT":
        audit_event_type = "REJECTED"
    else:
        audit_event_type = "MORE_INFORMATION_REQUESTED"

    # Create reviewed copy
    reviewed = VendorResponse(
        response_id=response.response_id,
        vendor_id=response.vendor_id,
        request_id=response.request_id,
        decision_status=response.decision_status,
        submitted_at=response.submitted_at,
        response_type=response.response_type,
        explanation=response.explanation,
        supporting_evidence_ids=list(response.supporting_evidence_ids),
        requested_action=response.requested_action,
        status=new_status,
        reviewed_by=reviewer_id,
        reviewed_at=ts,
        review_reason=review_reason,
    )

    # Record audit event
    _record_audit_event(
        response_id=response.response_id,
        event_type=audit_event_type,
        actor_id=reviewer_id,
        reason=review_reason,
        timestamp=ts,
    )

    return reviewed


def get_response_history(response_id: str) -> List[ResponseAuditEvent]:
    """Return a chronologically ordered copy of audit events for a response."""
    events = _audit_registry.get(response_id, [])
    return copy.deepcopy(events)
