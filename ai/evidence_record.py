import uuid
import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Any

@dataclass
class ValidationReport:
    validation_status: str
    evidence_level: str
    reasons: List[str]
    evaluator_authorized: bool
    evaluation_completed: bool
    artifact_verified: bool
    evidence_current: bool
    test_suite_valid: bool

@dataclass
class EvidenceRecord:
    evidence_id: str
    vendor_id: str
    artifact_id: str
    artifact_hash: str
    evaluator_version: str
    test_suite_id: str
    test_suite_version: str
    test_suite_hash: str
    
    source_type: str
    evidence_level: str
    
    metric_name: str
    metric_value: float
    metric_unit: str
    
    evaluation_id: str
    
    created_at: str
    validity_months: int
    expires_at: str
    
    validation_status: str
    validation_reasons: List[str]
    
    frozen: bool = False

    def __setattr__(self, key, value):
        if getattr(self, "frozen", False) and key in (
            "artifact_hash", 
            "evaluator_version", 
            "test_suite_hash", 
            "metric_value", 
            "validation_status", 
            "evidence_level"
        ):
            raise ValueError(f"Cannot modify protected field '{key}' of frozen evidence.")
        super().__setattr__(key, value)

def validate_evaluation_for_evidence(
    evaluation_run: Any,
    artifact_record: Any,
    artifact_verification: Any,
    evidence_validity: Any,
    evaluator_authorized: bool,
    test_suite_valid: bool,
) -> ValidationReport:
    
    reasons = []
    
    eval_auth = bool(evaluator_authorized)
    if eval_auth:
        reasons.append("Evaluator authorized")
    else:
        reasons.append("Evaluator not authorized")
        
    eval_comp = (evaluation_run.status == "COMPLETED")
    if eval_comp:
        reasons.append("Evaluation completed")
    else:
        reasons.append("Evaluation did not complete")
        
    art_ver = (artifact_verification.status == "MATCH")
    if art_ver:
        reasons.append("Artifact hash matched")
    else:
        reasons.append("Artifact hash mismatch")
        
    expires_dt = datetime.fromisoformat(evidence_validity.expires_at)
    current_time = datetime.now(timezone.utc)
    ev_curr = current_time <= expires_dt
    if ev_curr:
        reasons.append("Evidence validity window active")
    else:
        reasons.append("Evidence expired")
        
    ts_val = bool(test_suite_valid)
    if ts_val:
        reasons.append("Test suite valid")
    else:
        reasons.append("Test suite invalid")
        
    eval_ver_nonempty = bool(evaluation_run.evaluator_version)
    if not eval_ver_nonempty:
        reasons.append("Evaluator version empty")
        
    ts_hash_nonempty = bool(evaluation_run.test_suite_hash)
    if not ts_hash_nonempty:
        reasons.append("Test suite hash empty")
        
    art_id_match = (evaluation_run.artifact_id == artifact_record.artifact_id)
    if not art_id_match:
        reasons.append("Artifact identity mismatch")
        
    vend_id_match = (evaluation_run.vendor_id == artifact_record.vendor_id)
    if not vend_id_match:
        reasons.append("Vendor identity mismatch")
        
    all_passed = (
        eval_auth and eval_comp and art_ver and ev_curr and ts_val and
        eval_ver_nonempty and ts_hash_nonempty and art_id_match and vend_id_match
    )
    
    status = "VALIDATED"
    
    if not all_passed:
        if not art_ver or not ev_curr or not eval_auth:
            status = "REVALIDATION_REQUIRED"
        else:
            status = "NOT_VALIDATED"
            
    if status == "VALIDATED":
        evidence_level = "INDEPENDENTLY_VALIDATED"
    else:
        if eval_comp:
            evidence_level = "OBSERVED"
        else:
            evidence_level = "NONE"
            
    return ValidationReport(
        validation_status=status,
        evidence_level=evidence_level,
        reasons=reasons,
        evaluator_authorized=eval_auth,
        evaluation_completed=eval_comp,
        artifact_verified=art_ver,
        evidence_current=ev_curr,
        test_suite_valid=ts_val
    )

def create_evidence_record(
    evaluation_run: Any,
    artifact_record: Any,
    artifact_verification: Any,
    evidence_validity: Any,
    evaluator_authorized: bool,
    test_suite_valid: bool,
    metric_name: str = "Accuracy",
    metric_unit: str = "percent",
) -> EvidenceRecord:
    
    report = validate_evaluation_for_evidence(
        evaluation_run,
        artifact_record,
        artifact_verification,
        evidence_validity,
        evaluator_authorized,
        test_suite_valid
    )
    
    return EvidenceRecord(
        evidence_id=str(uuid.uuid4()),
        vendor_id=artifact_record.vendor_id,
        artifact_id=artifact_record.artifact_id,
        artifact_hash=artifact_record.artifact_hash,
        evaluator_version=evaluation_run.evaluator_version,
        test_suite_id=evaluation_run.test_suite_id,
        test_suite_version=evaluation_run.test_suite_version,
        test_suite_hash=evaluation_run.test_suite_hash,
        source_type="evaluator_result",
        evidence_level=report.evidence_level,
        metric_name=metric_name,
        metric_value=evaluation_run.accuracy,
        metric_unit=metric_unit,
        evaluation_id=evaluation_run.evaluation_id,
        created_at=evidence_validity.created_at,
        validity_months=evidence_validity.validity_months,
        expires_at=evidence_validity.expires_at,
        validation_status=report.validation_status,
        validation_reasons=report.reasons,
        frozen=False
    )

def freeze_evidence(record: EvidenceRecord) -> None:
    record.frozen = True

def mark_evidence_for_revalidation(
    evidence_record: EvidenceRecord,
    reason: str
) -> EvidenceRecord:
    if evidence_record.frozen:
        new_record = copy.deepcopy(evidence_record)
        new_record.frozen = False
        new_record.validation_status = "REVALIDATION_REQUIRED"
        new_record.validation_reasons.append(reason)
        new_record.frozen = True
        return new_record
    else:
        evidence_record.validation_status = "REVALIDATION_REQUIRED"
        evidence_record.validation_reasons.append(reason)
        return evidence_record

def invalidate_evidence_for_evaluator(
    evidence_record: EvidenceRecord,
    invalidated_evaluator_version: str,
) -> EvidenceRecord:
    if evidence_record.evaluator_version == invalidated_evaluator_version:
        return mark_evidence_for_revalidation(
            evidence_record,
            "Evaluator version invalidated"
        )
    return copy.deepcopy(evidence_record) if evidence_record.frozen else evidence_record

def refresh_evidence_status(
    evidence_record: EvidenceRecord,
    current_time: Optional[datetime] = None
) -> EvidenceRecord:
    if current_time is None:
        current_time = datetime.now(timezone.utc)
        
    expires_dt = datetime.fromisoformat(evidence_record.expires_at)
    if current_time > expires_dt:
        return mark_evidence_for_revalidation(
            evidence_record,
            "Evidence validity window expired"
        )
    return copy.deepcopy(evidence_record) if evidence_record.frozen else evidence_record
