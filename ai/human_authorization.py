"""
Human Authorization + Maker-Checker + Escalation

The final human governance boundary.

    AI ASSISTS.
    EVIDENCE PROVES.
    RULES GATE.
    HUMANS AUTHORIZE.

This module records human authorization decisions. It does NOT
evaluate vendors, modify evidence, change KPIs, release payments,
or execute procurement.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
import copy
import uuid


# --- Constants ---

ALLOWED_REQUESTED_ACTIONS = frozenset({"PROCUREMENT", "SCALE_UP"})

ALLOWED_PROCUREMENT_RECOMMENDATIONS = frozenset({
    "ELIGIBLE",
    "REJECTED",
    "INSUFFICIENT EVIDENCE",
    "BLOCKED",
    "RE-VALIDATION REQUIRED",
})

ALLOWED_SCALE_UP_RECOMMENDATIONS = frozenset({
    "SCALE_ELIGIBLE",
    "SCALE_REVIEW_REQUIRED",
    "DO_NOT_SCALE_YET",
    "REVALIDATION_REQUIRED",
})

ALLOWED_HUMAN_DECISIONS = frozenset({
    "APPROVE",
    "REJECT",
    "OVERRIDE",
    "REQUEST_RETEST",
})

ALLOWED_AUTHORIZATION_STATUSES = frozenset({
    "PENDING",
    "AUTHORIZED",
    "REJECTED",
    "OVERRIDE_PENDING_REVIEW",
    "RETEST_REQUESTED",
})

ALLOWED_REVIEWER_DECISIONS = frozenset({
    "CONCUR",
    "REJECT_OVERRIDE",
    "REQUEST_RETEST",
})

ALLOWED_AUDIT_EVENT_TYPES = frozenset({
    "AUTHORIZATION_REQUESTED",
    "APPROVED",
    "REJECTED",
    "OVERRIDE_REQUESTED",
    "OVERRIDE_CONCURRED",
    "OVERRIDE_REJECTED",
    "RETEST_REQUESTED",
    "ESCALATED",
})

PLACEHOLDER_JUSTIFICATIONS = frozenset({"", "N/A", "none"})

# Procurement: APPROVE agrees only with ELIGIBLE
PROCUREMENT_APPROVE_AGREES = frozenset({"ELIGIBLE"})
# Scale-up: APPROVE agrees only with SCALE_ELIGIBLE
SCALE_UP_APPROVE_AGREES = frozenset({"SCALE_ELIGIBLE"})

# Procurement: REJECT agrees with non-eligible recommendations
PROCUREMENT_REJECT_AGREES = frozenset({
    "REJECTED",
    "INSUFFICIENT EVIDENCE",
    "BLOCKED",
    "RE-VALIDATION REQUIRED",
})
# Scale-up: REJECT agrees with non-eligible recommendations
SCALE_UP_REJECT_AGREES = frozenset({
    "SCALE_REVIEW_REQUIRED",
    "DO_NOT_SCALE_YET",
    "REVALIDATION_REQUIRED",
})


# --- Data Structures ---

@dataclass
class AuthorizationRequest:
    authorization_id: str
    decision_id: str
    vendor_id: str
    department: str
    requested_action: str
    ai_recommendation: str
    evidence_ids: List[str]
    created_at: str
    requesting_officer_id: str
    department_authority_count: int

    def __post_init__(self):
        if not self.authorization_id:
            raise ValueError("authorization_id cannot be empty")
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty")
        if not self.vendor_id:
            raise ValueError("vendor_id cannot be empty")
        if not self.department:
            raise ValueError("department cannot be empty")
        if not self.requesting_officer_id:
            raise ValueError("requesting_officer_id cannot be empty")
        if self.department_authority_count < 1:
            raise ValueError("department_authority_count must be >= 1")
        if self.requested_action not in ALLOWED_REQUESTED_ACTIONS:
            raise ValueError(
                f"Invalid requested_action '{self.requested_action}'. "
                f"Allowed: {sorted(ALLOWED_REQUESTED_ACTIONS)}"
            )
        if self.requested_action == "PROCUREMENT":
            if self.ai_recommendation not in ALLOWED_PROCUREMENT_RECOMMENDATIONS:
                raise ValueError(
                    f"Invalid procurement recommendation '{self.ai_recommendation}'. "
                    f"Allowed: {sorted(ALLOWED_PROCUREMENT_RECOMMENDATIONS)}"
                )
        elif self.requested_action == "SCALE_UP":
            if self.ai_recommendation not in ALLOWED_SCALE_UP_RECOMMENDATIONS:
                raise ValueError(
                    f"Invalid scale-up recommendation '{self.ai_recommendation}'. "
                    f"Allowed: {sorted(ALLOWED_SCALE_UP_RECOMMENDATIONS)}"
                )


@dataclass
class AuthorizationDecision:
    authorization_id: str
    decision_id: str
    vendor_id: str
    requested_action: str
    ai_recommendation: str
    human_decision: str
    status: str
    authorizing_officer_id: str
    reviewing_officer_id: Optional[str]
    justification: str
    created_at: str
    reviewed_at: Optional[str]
    escalation_required: bool
    escalation_destination: Optional[str]
    evidence_ids: List[str] = field(default_factory=list)


@dataclass
class AuthorizationAuditEvent:
    event_id: str
    authorization_id: str
    event_type: str
    actor_id: str
    timestamp: str
    reason: str


# --- Internal audit storage ---

_audit_registry: dict = {}


def _generate_event_id() -> str:
    return f"AUTH-EVT-{uuid.uuid4().hex[:12]}"


def _record_audit_event(
    authorization_id: str,
    event_type: str,
    actor_id: str,
    reason: str,
    timestamp: Optional[str] = None,
) -> AuthorizationAuditEvent:
    if event_type not in ALLOWED_AUDIT_EVENT_TYPES:
        raise ValueError(f"Unknown audit event type: {event_type}")

    ts = timestamp or datetime.now(timezone.utc).isoformat()

    event = AuthorizationAuditEvent(
        event_id=_generate_event_id(),
        authorization_id=authorization_id,
        event_type=event_type,
        actor_id=actor_id,
        timestamp=ts,
        reason=reason,
    )

    if authorization_id not in _audit_registry:
        _audit_registry[authorization_id] = []
    _audit_registry[authorization_id].append(event)

    return event


# --- Recommendation agreement ---

def recommendation_agrees(
    requested_action: str,
    ai_recommendation: str,
    human_intent: str,
) -> bool:
    """Deterministic check: does the human intent agree with the AI recommendation?"""
    if human_intent == "APPROVE":
        if requested_action == "PROCUREMENT":
            return ai_recommendation in PROCUREMENT_APPROVE_AGREES
        elif requested_action == "SCALE_UP":
            return ai_recommendation in SCALE_UP_APPROVE_AGREES
    elif human_intent == "REJECT":
        if requested_action == "PROCUREMENT":
            return ai_recommendation in PROCUREMENT_REJECT_AGREES
        elif requested_action == "SCALE_UP":
            return ai_recommendation in SCALE_UP_REJECT_AGREES
    return False


def _validate_justification(justification: str) -> None:
    if justification in PLACEHOLDER_JUSTIFICATIONS:
        raise ValueError(
            f"Justification cannot be empty or a placeholder value. "
            f"Rejected: {sorted(PLACEHOLDER_JUSTIFICATIONS)}"
        )


# --- Public API ---

def create_authorization(
    request: AuthorizationRequest,
    authorizing_officer_id: str,
    human_decision: str,
    justification: str,
    created_at: Optional[str] = None,
) -> AuthorizationDecision:
    """Create an authorization decision from a human officer."""

    if not authorizing_officer_id:
        raise ValueError("authorizing_officer_id cannot be empty")

    if human_decision not in ALLOWED_HUMAN_DECISIONS:
        raise ValueError(
            f"Invalid human_decision '{human_decision}'. "
            f"Allowed: {sorted(ALLOWED_HUMAN_DECISIONS)}"
        )

    _validate_justification(justification)

    ts = created_at or datetime.now(timezone.utc).isoformat()

    # Determine if this is an agreement or override
    agrees = recommendation_agrees(
        request.requested_action,
        request.ai_recommendation,
        human_decision,
    )

    # REQUEST_RETEST is always its own path
    if human_decision == "REQUEST_RETEST":
        status = "RETEST_REQUESTED"
        escalation_required = False
        escalation_destination = None

        decision = AuthorizationDecision(
            authorization_id=request.authorization_id,
            decision_id=request.decision_id,
            vendor_id=request.vendor_id,
            requested_action=request.requested_action,
            ai_recommendation=request.ai_recommendation,
            human_decision="REQUEST_RETEST",
            status=status,
            authorizing_officer_id=authorizing_officer_id,
            reviewing_officer_id=None,
            justification=justification,
            created_at=ts,
            reviewed_at=None,
            escalation_required=escalation_required,
            escalation_destination=escalation_destination,
            evidence_ids=list(request.evidence_ids),
        )

        _record_audit_event(
            request.authorization_id, "RETEST_REQUESTED",
            authorizing_officer_id, justification, ts,
        )
        return decision

    # OVERRIDE path: explicit override or disagreement
    if human_decision == "OVERRIDE" or not agrees:
        effective_decision = "OVERRIDE"
        status = "OVERRIDE_PENDING_REVIEW"

        if request.department_authority_count == 1:
            escalation_required = True
            escalation_destination = "HIGHER_AUTHORITY_REVIEW"
        else:
            escalation_required = False
            escalation_destination = "SECOND_AUTHORIZED_OFFICER"

        decision = AuthorizationDecision(
            authorization_id=request.authorization_id,
            decision_id=request.decision_id,
            vendor_id=request.vendor_id,
            requested_action=request.requested_action,
            ai_recommendation=request.ai_recommendation,
            human_decision=effective_decision,
            status=status,
            authorizing_officer_id=authorizing_officer_id,
            reviewing_officer_id=None,
            justification=justification,
            created_at=ts,
            reviewed_at=None,
            escalation_required=escalation_required,
            escalation_destination=escalation_destination,
            evidence_ids=list(request.evidence_ids),
        )

        _record_audit_event(
            request.authorization_id, "OVERRIDE_REQUESTED",
            authorizing_officer_id, justification, ts,
        )
        if escalation_required:
            _record_audit_event(
                request.authorization_id, "ESCALATED",
                authorizing_officer_id,
                f"Escalated to {escalation_destination}",
                ts,
            )
        return decision

    # Normal agreement path: APPROVE agrees with recommendation or REJECT agrees
    if human_decision == "APPROVE" and agrees:
        status = "AUTHORIZED"
        audit_event_type = "APPROVED"
    elif human_decision == "REJECT" and agrees:
        status = "REJECTED"
        audit_event_type = "REJECTED"
    else:
        # Fallback — should not reach here
        status = "PENDING"
        audit_event_type = "AUTHORIZATION_REQUESTED"

    decision = AuthorizationDecision(
        authorization_id=request.authorization_id,
        decision_id=request.decision_id,
        vendor_id=request.vendor_id,
        requested_action=request.requested_action,
        ai_recommendation=request.ai_recommendation,
        human_decision=human_decision,
        status=status,
        authorizing_officer_id=authorizing_officer_id,
        reviewing_officer_id=None,
        justification=justification,
        created_at=ts,
        reviewed_at=None,
        escalation_required=False,
        escalation_destination=None,
        evidence_ids=list(request.evidence_ids),
    )

    _record_audit_event(
        request.authorization_id, audit_event_type,
        authorizing_officer_id, justification, ts,
    )
    return decision


def review_override(
    authorization_decision: AuthorizationDecision,
    reviewing_officer_id: str,
    decision: str,
    justification: str,
    reviewed_at: Optional[str] = None,
) -> AuthorizationDecision:
    """Second-officer review of an override decision."""

    if not reviewing_officer_id:
        raise ValueError("reviewing_officer_id cannot be empty")

    _validate_justification(justification)

    if decision not in ALLOWED_REVIEWER_DECISIONS:
        raise ValueError(
            f"Invalid reviewer decision '{decision}'. "
            f"Allowed: {sorted(ALLOWED_REVIEWER_DECISIONS)}"
        )

    # Separation of duties
    if reviewing_officer_id == authorization_decision.authorizing_officer_id:
        raise ValueError("Reviewer cannot be the same as the authorizing officer")

    # Only OVERRIDE_PENDING_REVIEW can be reviewed
    if authorization_decision.status != "OVERRIDE_PENDING_REVIEW":
        raise ValueError(
            f"Cannot review authorization in status '{authorization_decision.status}'. "
            f"Only OVERRIDE_PENDING_REVIEW can be reviewed."
        )

    ts = reviewed_at or datetime.now(timezone.utc).isoformat()

    if decision == "CONCUR":
        new_status = "AUTHORIZED"
        audit_event_type = "OVERRIDE_CONCURRED"
    elif decision == "REJECT_OVERRIDE":
        new_status = "REJECTED"
        audit_event_type = "OVERRIDE_REJECTED"
    else:  # REQUEST_RETEST
        new_status = "RETEST_REQUESTED"
        audit_event_type = "RETEST_REQUESTED"

    reviewed = AuthorizationDecision(
        authorization_id=authorization_decision.authorization_id,
        decision_id=authorization_decision.decision_id,
        vendor_id=authorization_decision.vendor_id,
        requested_action=authorization_decision.requested_action,
        ai_recommendation=authorization_decision.ai_recommendation,
        human_decision=authorization_decision.human_decision,
        status=new_status,
        authorizing_officer_id=authorization_decision.authorizing_officer_id,
        reviewing_officer_id=reviewing_officer_id,
        justification=authorization_decision.justification,
        created_at=authorization_decision.created_at,
        reviewed_at=ts,
        escalation_required=authorization_decision.escalation_required,
        escalation_destination=authorization_decision.escalation_destination,
        evidence_ids=list(authorization_decision.evidence_ids),
    )

    _record_audit_event(
        authorization_decision.authorization_id, audit_event_type,
        reviewing_officer_id, justification, ts,
    )
    return reviewed


def review_escalated_override(
    authorization_decision: AuthorizationDecision,
    reviewing_officer_id: str,
    decision: str,
    justification: str,
    reviewed_at: Optional[str] = None,
) -> AuthorizationDecision:
    """Higher-authority review of an escalated override decision."""

    if not reviewing_officer_id:
        raise ValueError("reviewing_officer_id cannot be empty")

    _validate_justification(justification)

    if decision not in ALLOWED_REVIEWER_DECISIONS:
        raise ValueError(
            f"Invalid reviewer decision '{decision}'. "
            f"Allowed: {sorted(ALLOWED_REVIEWER_DECISIONS)}"
        )

    # Separation of duties
    if reviewing_officer_id == authorization_decision.authorizing_officer_id:
        raise ValueError("Reviewer cannot be the same as the authorizing officer")

    # Only OVERRIDE_PENDING_REVIEW can be reviewed
    if authorization_decision.status != "OVERRIDE_PENDING_REVIEW":
        raise ValueError(
            f"Cannot review authorization in status '{authorization_decision.status}'. "
            f"Only OVERRIDE_PENDING_REVIEW can be reviewed."
        )

    ts = reviewed_at or datetime.now(timezone.utc).isoformat()

    if decision == "CONCUR":
        new_status = "AUTHORIZED"
        audit_event_type = "OVERRIDE_CONCURRED"
    elif decision == "REJECT_OVERRIDE":
        new_status = "REJECTED"
        audit_event_type = "OVERRIDE_REJECTED"
    else:  # REQUEST_RETEST
        new_status = "RETEST_REQUESTED"
        audit_event_type = "RETEST_REQUESTED"

    reviewed = AuthorizationDecision(
        authorization_id=authorization_decision.authorization_id,
        decision_id=authorization_decision.decision_id,
        vendor_id=authorization_decision.vendor_id,
        requested_action=authorization_decision.requested_action,
        ai_recommendation=authorization_decision.ai_recommendation,
        human_decision=authorization_decision.human_decision,
        status=new_status,
        authorizing_officer_id=authorization_decision.authorizing_officer_id,
        reviewing_officer_id=reviewing_officer_id,
        justification=authorization_decision.justification,
        created_at=authorization_decision.created_at,
        reviewed_at=ts,
        escalation_required=authorization_decision.escalation_required,
        escalation_destination=authorization_decision.escalation_destination,
        evidence_ids=list(authorization_decision.evidence_ids),
    )

    _record_audit_event(
        authorization_decision.authorization_id, audit_event_type,
        reviewing_officer_id, justification, ts,
    )
    return reviewed


def get_authorization_history(authorization_id: str) -> List[AuthorizationAuditEvent]:
    """Return a chronologically ordered copy of audit events."""
    events = _audit_registry.get(authorization_id, [])
    return copy.deepcopy(events)
