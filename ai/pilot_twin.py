from dataclasses import dataclass
from typing import Any, List, Dict

@dataclass
class PilotParameter:
    name: str
    value: Any
    unit: str = ""
    evidence_level: str = "UNVERIFIED"
    source: str = ""

@dataclass
class PilotTwin:
    twin_id: str
    department: str
    district: str
    parameters: List[PilotParameter]
    version: str = "1.0"
    locked: bool = False

VALID_EVIDENCE_LEVELS = {
    "CLAIMED",
    "DECLARED",
    "OBSERVED",
    "ESTIMATED",
    "INDEPENDENTLY_VALIDATED",
    "UNVERIFIED",
}

EVIDENCE_SCORES = {
    "CLAIMED": 40.0,
    "DECLARED": 60.0,
    "OBSERVED": 80.0,
    "ESTIMATED": 60.0,
    "INDEPENDENTLY_VALIDATED": 100.0,
    "UNVERIFIED": 0.0,
}

def create_pilot_twin(
    twin_id: str,
    department: str,
    district: str,
    parameters: List[PilotParameter],
) -> PilotTwin:
    if not twin_id:
        raise ValueError("twin_id cannot be empty")
    if not department:
        raise ValueError("department cannot be empty")
    if not district:
        raise ValueError("district cannot be empty")
    if not parameters:
        raise ValueError("parameters cannot be empty")

    for p in parameters:
        if not p.name:
            raise ValueError("Parameter name cannot be empty")
        if p.evidence_level not in VALID_EVIDENCE_LEVELS:
            raise ValueError(f"Unsupported evidence level: {p.evidence_level}")

    return PilotTwin(
        twin_id=twin_id,
        department=department,
        district=district,
        parameters=parameters,
        version="1.0",
        locked=False
    )

def summarize_pilot_evidence(pilot_twin: PilotTwin) -> Dict[str, Any]:
    total = len(pilot_twin.parameters)
    by_level = {k: 0 for k in VALID_EVIDENCE_LEVELS}
    unverified = []
    
    score_sum = 0.0
    for p in pilot_twin.parameters:
        by_level[p.evidence_level] += 1
        if p.evidence_level == "UNVERIFIED":
            unverified.append(p.name)
        score_sum += EVIDENCE_SCORES[p.evidence_level]
        
    avg_score = score_sum / total if total > 0 else 0.0
    
    return {
        "total_parameters": total,
        "by_level": by_level,
        "unverified_parameters": unverified,
        "evidence_quality": round(avg_score, 2),
    }

def update_parameter_evidence(
    pilot_twin: PilotTwin,
    parameter_name: str,
    evidence_level: str,
    source: str,
) -> PilotTwin:
    if pilot_twin.locked:
        raise ValueError("Pilot Twin is locked and cannot be modified.")
        
    if evidence_level not in VALID_EVIDENCE_LEVELS:
        raise ValueError(f"Unsupported evidence level: {evidence_level}")
        
    found = False
    for p in pilot_twin.parameters:
        if p.name == parameter_name:
            p.evidence_level = evidence_level
            p.source = source
            found = True
            break
            
    if not found:
        raise ValueError(f"Parameter '{parameter_name}' not found in Pilot Twin.")
        
    return pilot_twin
