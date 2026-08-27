"""
IP + Data Governance

Cross-cutting governance layer defining data classification,
IP schedules (black-box model access, startup IP ownership, government evidence ownership),
data retention policies, and deterministic pseudonymization/redaction for citizen data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set
import hashlib
import copy

# --- Data Classification ---

ALLOWED_DATA_CLASSIFICATIONS: Set[str] = {
    "PUBLIC",
    "INTERNAL",
    "CONFIDENTIAL",
    "SENSITIVE",
    "HIGHLY_SENSITIVE",
}

@dataclass
class DataAsset:
    asset_id: str
    name: str
    category: str
    classification: str
    owner: str
    purpose: str
    retention_days: int
    created_at: str

    def __post_init__(self):
        if not self.asset_id:
            raise ValueError("asset_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.category:
            raise ValueError("category cannot be empty")
        if not self.owner:
            raise ValueError("owner cannot be empty")
        if not self.purpose:
            raise ValueError("purpose cannot be empty")
        if self.retention_days <= 0:
            raise ValueError("retention_days must be > 0")
        if self.classification not in ALLOWED_DATA_CLASSIFICATIONS:
            raise ValueError(
                f"Invalid classification '{self.classification}'. "
                f"Allowed: {sorted(ALLOWED_DATA_CLASSIFICATIONS)}"
            )


# --- IP Governance Schedule ---

@dataclass
class IPGovernanceSchedule:
    schedule_id: str
    contract_id: str
    pilot_twin_id: str
    startup_ip_owner: str
    government_evidence_owner: str
    citizen_data_owner: str
    model_access_mode: str
    created_at: str
    confirmed: bool = True
    disclaimer: str = "Prototype governance policy — requires departmental/legal review"

    def __post_init__(self):
        if not self.schedule_id:
            raise ValueError("schedule_id cannot be empty")
        if not self.contract_id:
            raise ValueError("contract_id cannot be empty")
        if not self.pilot_twin_id:
            raise ValueError("pilot_twin_id cannot be empty")
        if self.startup_ip_owner != "VENDOR":
            raise ValueError("startup_ip_owner must be 'VENDOR'")
        if self.government_evidence_owner != "GOVERNMENT":
            raise ValueError("government_evidence_owner must be 'GOVERNMENT'")
        if not self.citizen_data_owner:
            raise ValueError("citizen_data_owner must be explicitly specified and non-empty")
        if self.model_access_mode != "BLACK_BOX_ONLY":
            raise ValueError("model_access_mode must be 'BLACK_BOX_ONLY'")


# --- Data Governance Schedule Per Pilot Twin ---

@dataclass
class DataGovernanceSchedule:
    schedule_id: str
    contract_id: str
    pilot_twin_id: str
    ip_schedule: IPGovernanceSchedule
    citizen_data_classification: str
    retention_days: int
    deletion_required: bool
    created_at: str
    disclaimer: str = "Prototype governance policy — requires departmental/legal review"

    def __post_init__(self):
        if self.citizen_data_classification not in ALLOWED_DATA_CLASSIFICATIONS:
            raise ValueError(
                f"Invalid citizen_data_classification '{self.citizen_data_classification}'. "
                f"Allowed: {sorted(ALLOWED_DATA_CLASSIFICATIONS)}"
            )
        if self.retention_days <= 0:
            raise ValueError("retention_days must be > 0")


def create_data_governance_schedule(
    contract_id: str,
    pilot_twin_id: str,
    citizen_data_owner: str,
    citizen_data_classification: str = "SENSITIVE",
    retention_days: int = 365,
    deletion_required: bool = True,
    created_at: Optional[str] = None,
) -> DataGovernanceSchedule:
    if not contract_id:
        raise ValueError("contract_id cannot be empty")
    if not pilot_twin_id:
        raise ValueError("pilot_twin_id cannot be empty")
    if not citizen_data_owner:
        raise ValueError("citizen_data_owner cannot be empty")

    ts = created_at or datetime.now(timezone.utc).isoformat()
    sched_id = f"DGS-{pilot_twin_id}-{hashlib.sha256((contract_id + pilot_twin_id).encode()).hexdigest()[:8]}"

    ip_sched = IPGovernanceSchedule(
        schedule_id=f"IP-{sched_id}",
        contract_id=contract_id,
        pilot_twin_id=pilot_twin_id,
        startup_ip_owner="VENDOR",
        government_evidence_owner="GOVERNMENT",
        citizen_data_owner=citizen_data_owner,
        model_access_mode="BLACK_BOX_ONLY",
        created_at=ts,
        confirmed=True,
    )

    return DataGovernanceSchedule(
        schedule_id=sched_id,
        contract_id=contract_id,
        pilot_twin_id=pilot_twin_id,
        ip_schedule=ip_sched,
        citizen_data_classification=citizen_data_classification,
        retention_days=retention_days,
        deletion_required=deletion_required,
        created_at=ts,
    )


# --- Pseudonymization & Redaction ---

IDENTITY_FIELDS = {
    "name",
    "phone",
    "telephone",
    "mobile",
    "email",
    "aadhaar",
    "aadhar",
    "ssn",
    "address",
    "land_record_number",
    "citizen_id",
}

LOCATION_FIELDS = {
    "gps",
    "latitude",
    "longitude",
    "lat",
    "lng",
    "location",
    "coordinates",
    "exif",
}

def sanitize_citizen_data(data: Any) -> Any:
    """
    Deterministic sanitization layer.
    Replaces identifiable citizen fields with pseudonymous tokens and strips location/EXIF metadata.
    Output is explicitly labeled PSEUDONYMIZED (not anonymized).
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            key_lower = str(k).lower().strip()
            
            # Check location/EXIF removal
            if key_lower in LOCATION_FIELDS:
                continue
                
            # Check identity replacement
            if key_lower in IDENTITY_FIELDS:
                if v is not None:
                    # Deterministic pseudonymous token
                    pseudo_hash = hashlib.sha256(str(v).encode("utf-8")).hexdigest()[:12]
                    sanitized[k] = f"PSEUDO_{pseudo_hash}"
                else:
                    sanitized[k] = None
            else:
                sanitized[k] = sanitize_citizen_data(v)
                
        return sanitized
    elif isinstance(data, list):
        return [sanitize_citizen_data(item) for item in data]
    else:
        return data
