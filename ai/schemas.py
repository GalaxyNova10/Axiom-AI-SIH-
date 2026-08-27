from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class KPI:
    name: str
    threshold: float
    operator: str
    unit: str = ""


@dataclass
class OutcomeContract:
    contract_id: str
    version: str
    kpis: List[KPI]
    minimum_evidence_confidence: float
    evidence_validity_months: int
    locked: bool = False


@dataclass
class EvidenceRecord:
    evidence_id: str
    source_type: str
    level: str
    value: Any
    methodology: str = ""
    evaluator_version: str = ""
    artifact_hash: str = ""


@dataclass
class DecisionResult:
    decision: str
    reasons: List[str] = field(default_factory=list)
    gates: Dict[str, str] = field(default_factory=dict)