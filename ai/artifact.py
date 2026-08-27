import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
import calendar
from typing import Optional, Dict

@dataclass
class ArtifactRecord:
    artifact_id: str
    vendor_id: str
    artifact_hash: str
    hash_algorithm: str
    created_at: str
    metadata: Dict[str, str] = field(default_factory=dict)

def compute_artifact_hash(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")
    return hashlib.sha256(data).hexdigest()

def register_artifact(
    artifact_id: str,
    vendor_id: str,
    data: bytes,
    metadata: Optional[Dict[str, str]] = None,
) -> ArtifactRecord:
    if not artifact_id:
        raise ValueError("artifact_id cannot be empty")
    if not vendor_id:
        raise ValueError("vendor_id cannot be empty")
    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes")
        
    return ArtifactRecord(
        artifact_id=artifact_id,
        vendor_id=vendor_id,
        artifact_hash=compute_artifact_hash(data),
        hash_algorithm="SHA-256",
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {}
    )

def verify_artifact(record: ArtifactRecord, current_data: bytes) -> bool:
    if not isinstance(current_data, bytes):
        raise TypeError("Current data must be bytes")
    return compute_artifact_hash(current_data) == record.artifact_hash

def freeze_artifact(record: ArtifactRecord) -> ArtifactRecord:
    # For prototype, freezing just returns the conceptually frozen record
    return record

@dataclass
class ArtifactVerification:
    artifact_id: str
    vendor_id: str
    expected_hash: str
    observed_hash: str
    status: str
    verified_at: str

def verify_artifact_for_evaluation(
    record: ArtifactRecord,
    current_data: bytes,
) -> ArtifactVerification:
    if not isinstance(current_data, bytes):
        raise TypeError("Current data must be bytes")
        
    observed_hash = compute_artifact_hash(current_data)
    status = "MATCH" if observed_hash == record.artifact_hash else "MISMATCH"
    
    return ArtifactVerification(
        artifact_id=record.artifact_id,
        vendor_id=record.vendor_id,
        expected_hash=record.artifact_hash,
        observed_hash=observed_hash,
        status=status,
        verified_at=datetime.now(timezone.utc).isoformat()
    )

def require_artifact_revalidation(verification: ArtifactVerification) -> bool:
    return verification.status == "MISMATCH"

def artifact_gate_status(verification: ArtifactVerification) -> str:
    if verification.status == "MATCH":
        return "ARTIFACT VERIFIED"
    return "VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"

@dataclass
class EvidenceValidity:
    evidence_id: str
    artifact_id: str
    artifact_hash: str
    created_at: str
    validity_months: int
    expires_at: str

def add_months(dt: datetime, months: int) -> datetime:
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)

def create_evidence_validity(
    evidence_id: str,
    artifact_record: ArtifactRecord,
    validity_months: int,
    created_at: Optional[datetime] = None
) -> EvidenceValidity:
    if validity_months <= 0:
        raise ValueError("validity_months must be > 0")
        
    if created_at is None:
        created_at = datetime.now(timezone.utc)
        
    expires_at = add_months(created_at, validity_months)
    
    return EvidenceValidity(
        evidence_id=evidence_id,
        artifact_id=artifact_record.artifact_id,
        artifact_hash=artifact_record.artifact_hash,
        created_at=created_at.isoformat(),
        validity_months=validity_months,
        expires_at=expires_at.isoformat()
    )

def is_evidence_expired(
    validity: EvidenceValidity,
    current_time: Optional[datetime] = None
) -> bool:
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    expires_dt = datetime.fromisoformat(validity.expires_at)
    return current_time > expires_dt

def validate_evidence_artifact(
    validity: EvidenceValidity,
    artifact_record: ArtifactRecord,
    current_data: bytes,
    current_time: Optional[datetime] = None
) -> str:
    
    current_hash = compute_artifact_hash(current_data)
    artifact_mismatch = (current_hash != artifact_record.artifact_hash) or (current_hash != validity.artifact_hash)
    
    expired = is_evidence_expired(validity, current_time)
    
    if expired and artifact_mismatch:
        return "EVIDENCE EXPIRED AND VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"
    elif expired:
        return "EVIDENCE EXPIRED — RE-VALIDATION REQUIRED"
    elif artifact_mismatch:
        return "VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"
    else:
        return "VALID"
