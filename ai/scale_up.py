from dataclasses import dataclass, field
from typing import List, Any, Optional
from datetime import datetime, timezone
from ai.artifact import verify_artifact_for_evaluation
from ai.failure_cartography import FailureMap

@dataclass
class ScaleUpRequest:
    request_id: str
    vendor_id: str
    target_department: str
    target_district: str
    existing_evidence_id: str
    existing_artifact_id: str
    requested_at: str
    reason: str
    
    def __post_init__(self):
        if not self.request_id:
            raise ValueError("request_id cannot be empty")
        if not self.vendor_id:
            raise ValueError("vendor_id cannot be empty")
        if not self.target_department:
            raise ValueError("target_department cannot be empty")
        if not self.target_district:
            raise ValueError("target_district cannot be empty")
        if not self.existing_evidence_id:
            raise ValueError("existing_evidence_id cannot be empty")
        if not self.existing_artifact_id:
            raise ValueError("existing_artifact_id cannot be empty")

@dataclass
class ScaleUpDecision:
    request_id: str
    vendor_id: str
    target_department: str
    target_district: str
    
    status: str
    
    artifact_status: str
    evidence_status: str
    pilot_twin_status: str
    failure_map_status: str
    
    matched_failure_strata: List[str]
    reasons: List[str]

def evaluate_scale_up_request(
    request: ScaleUpRequest,
    current_artifact_bytes: bytes,
    artifact_record: Any,
    evidence_record: Any,
    failure_map: FailureMap,
    pilot_twin: Any
) -> ScaleUpDecision:
    
    reasons = []
    
    art_ver = verify_artifact_for_evaluation(artifact_record, current_artifact_bytes)
    if art_ver.status != "MATCH":
        reasons.append("VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED")
        return ScaleUpDecision(
            request_id=request.request_id,
            vendor_id=request.vendor_id,
            target_department=request.target_department,
            target_district=request.target_district,
            status="REVALIDATION_REQUIRED",
            artifact_status="MISMATCH",
            evidence_status="UNKNOWN",
            pilot_twin_status="UNKNOWN",
            failure_map_status="UNKNOWN",
            matched_failure_strata=[],
            reasons=reasons
        )
    artifact_status = "MATCH"
    
    current_time = datetime.now(timezone.utc)
    expires_dt = datetime.fromisoformat(evidence_record.expires_at)
    if current_time > expires_dt:
        reasons.append("EVIDENCE EXPIRED — RE-VALIDATION REQUIRED")
        return ScaleUpDecision(
            request_id=request.request_id,
            vendor_id=request.vendor_id,
            target_department=request.target_department,
            target_district=request.target_district,
            status="REVALIDATION_REQUIRED",
            artifact_status=artifact_status,
            evidence_status="EXPIRED",
            pilot_twin_status="UNKNOWN",
            failure_map_status="UNKNOWN",
            matched_failure_strata=[],
            reasons=reasons
        )
    evidence_status = "VALID"
    
    if evidence_record.evidence_level != "INDEPENDENTLY_VALIDATED":
        reasons.append("Existing evidence is not independently validated")
        reasons.append("VENDOR RESPONSE WINDOW REQUIRED")
        return ScaleUpDecision(
            request_id=request.request_id,
            vendor_id=request.vendor_id,
            target_department=request.target_department,
            target_district=request.target_district,
            status="DO_NOT_SCALE_YET",
            artifact_status=artifact_status,
            evidence_status="INSUFFICIENT_LEVEL",
            pilot_twin_status="UNKNOWN",
            failure_map_status="UNKNOWN",
            matched_failure_strata=[],
            reasons=reasons
        )
        
    pilot_twin_status = "VERIFIED"
    for attr in ["connectivity", "device", "language", "input_quality"]:
        if getattr(pilot_twin, attr, None) == "UNVERIFIED":
            pilot_twin_status = "UNVERIFIED"
            reasons.append("Target deployment condition contains unverified parameters")
            break
            
    matched_failure_strata = []
    
    pt_attrs = [str(getattr(pilot_twin, attr, "")).upper() for attr in ["connectivity", "device", "language", "input_quality"]]
    pt_stratum_id = "_".join([a for a in pt_attrs if a])
    
    for hotspot in failure_map.hotspots:
        if hasattr(pilot_twin, 'stratum_id') and hotspot.stratum_id == pilot_twin.stratum_id:
            matched_failure_strata.append(hotspot.stratum_id)
        elif pt_stratum_id and hotspot.stratum_id == pt_stratum_id:
            matched_failure_strata.append(hotspot.stratum_id)
        elif hotspot.stratum_id in pt_stratum_id:
            matched_failure_strata.append(hotspot.stratum_id)

    matched_failure_strata = list(dict.fromkeys(matched_failure_strata))

    has_critical = False
    has_degraded = False
    has_watch = False

    for hotspot in failure_map.hotspots:
        if hotspot.stratum_id in matched_failure_strata:
            if hotspot.severity == "CRITICAL":
                has_critical = True
            elif hotspot.severity == "DEGRADED":
                has_degraded = True
            elif hotspot.severity == "WATCH":
                has_watch = True

    if has_critical:
        failure_map_status = "CRITICAL_MATCH"
    elif has_degraded:
        failure_map_status = "DEGRADED_MATCH"
    elif has_watch:
        failure_map_status = "WATCH_MATCH"
    else:
        failure_map_status = "NO_KNOWN_FAILURE_MATCH"

    if pilot_twin_status == "UNVERIFIED":
        status = "SCALE_REVIEW_REQUIRED"
        if "VENDOR RESPONSE WINDOW REQUIRED" not in reasons:
            reasons.append("VENDOR RESPONSE WINDOW REQUIRED")
    elif failure_map_status in ["CRITICAL_MATCH", "DEGRADED_MATCH"]:
        status = "SCALE_REVIEW_REQUIRED"
        if "VENDOR RESPONSE WINDOW REQUIRED" not in reasons:
            reasons.append("VENDOR RESPONSE WINDOW REQUIRED")
    elif failure_map_status == "WATCH_MATCH":
        status = "SCALE_ELIGIBLE"
        reasons.append("Target district matches a WATCH-level historical failure.")
    else:
        status = "SCALE_ELIGIBLE"

    return ScaleUpDecision(
        request_id=request.request_id,
        vendor_id=request.vendor_id,
        target_department=request.target_department,
        target_district=request.target_district,
        status=status,
        artifact_status=artifact_status,
        evidence_status=evidence_status,
        pilot_twin_status=pilot_twin_status,
        failure_map_status=failure_map_status,
        matched_failure_strata=matched_failure_strata,
        reasons=reasons
    )
