import hashlib
import json
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

EVALUATOR_DEVELOPMENT_ROLE = "EVALUATOR_DEVELOPMENT"

@dataclass
class GoldenCase:
    __test__ = False
    case_id: str
    description: str
    total_samples: int
    correct_samples: int
    expected_accuracy: float
    tolerance: float = 0.01

@dataclass
class GoldenReferenceSuite:
    suite_id: str
    version: str
    cases: List[GoldenCase]
    suite_hash: str = ""
    reviewer_role: str = ""
    approved_by: str = ""
    approved_at: str = ""

def calculate_suite_hash(suite_id: str, version: str, cases: List[GoldenCase]) -> str:
    canonical_cases = []
    for c in sorted(cases, key=lambda x: x.case_id):
        canonical_cases.append({
            "case_id": c.case_id,
            "description": c.description,
            "total_samples": c.total_samples,
            "correct_samples": c.correct_samples,
            "expected_accuracy": c.expected_accuracy,
            "tolerance": c.tolerance,
        })
    data = {
        "suite_id": suite_id,
        "version": version,
        "cases": canonical_cases
    }
    json_bytes = json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(json_bytes).hexdigest()

def create_initial_golden_suite() -> GoldenReferenceSuite:
    cases = [
        GoldenCase("GOLD-001", "Case 1", 100, 90, 90.0),
        GoldenCase("GOLD-002", "Case 2", 200, 190, 95.0),
        GoldenCase("GOLD-003", "Case 3", 100, 50, 50.0),
        GoldenCase("GOLD-004", "Case 4", 1000, 997, 99.7),
        GoldenCase("GOLD-005", "Case 5", 80, 0, 0.0),
    ]
    suite_id = "AXIOM-GOLDEN-001"
    version = "1.0"
    suite_hash = calculate_suite_hash(suite_id, version, cases)
    
    return GoldenReferenceSuite(
        suite_id=suite_id,
        version=version,
        cases=cases,
        suite_hash=suite_hash,
        reviewer_role="INDEPENDENT_EVALUATOR_REVIEWER",
        approved_by="PROTOTYPE_REVIEW_AUTHORITY",
        approved_at=datetime.now(timezone.utc).isoformat()
    )

@dataclass
class GoldenSuiteChange:
    change_type: str
    reason: str
    requested_by: str
    requested_at: str
    previous_hash: str
    proposed_hash: str
    status: str
    proposed_suite: GoldenReferenceSuite
    reviewer_role: str = ""
    reviewer_id: str = ""
    justification: str = ""
    reviewed_at: str = ""

def propose_golden_suite_change(
    active_suite: GoldenReferenceSuite,
    change_type: str,
    reason: str,
    requested_by: str,
    new_cases: List[GoldenCase],
    new_version: str
) -> GoldenSuiteChange:
    if not reason:
        raise ValueError("Change reason cannot be empty")
    
    proposed_hash = calculate_suite_hash(active_suite.suite_id, new_version, new_cases)
    
    proposed_suite = GoldenReferenceSuite(
        suite_id=active_suite.suite_id,
        version=new_version,
        cases=new_cases,
        suite_hash=proposed_hash,
        reviewer_role="",
        approved_by="",
        approved_at=""
    )
    
    return GoldenSuiteChange(
        change_type=change_type,
        reason=reason,
        requested_by=requested_by,
        requested_at=datetime.now(timezone.utc).isoformat(),
        previous_hash=active_suite.suite_hash,
        proposed_hash=proposed_hash,
        status="PENDING_REVIEW",
        proposed_suite=proposed_suite
    )

def review_golden_suite_change(
    change_record: GoldenSuiteChange,
    reviewer_role: str,
    reviewer_id: str,
    approve: bool,
    justification: str,
) -> GoldenSuiteChange:
    if reviewer_role == EVALUATOR_DEVELOPMENT_ROLE:
        raise ValueError("Evaluator development role cannot review Golden Suite changes")
    if not reviewer_id:
        raise ValueError("Reviewer ID cannot be empty")
    if not justification:
        raise ValueError("Justification cannot be empty")
        
    change_record.reviewer_role = reviewer_role
    change_record.reviewer_id = reviewer_id
    change_record.justification = justification
    change_record.reviewed_at = datetime.now(timezone.utc).isoformat()
    
    if approve:
        change_record.status = "APPROVED"
        change_record.proposed_suite.reviewer_role = reviewer_role
        change_record.proposed_suite.approved_by = reviewer_id
        change_record.proposed_suite.approved_at = change_record.reviewed_at
    else:
        change_record.status = "REJECTED"
        
    return change_record

@dataclass
class EvaluatorAuthorization:
    evaluator_version: str
    status: str
    golden_suite_version: str
    golden_suite_hash: str
    verified_at: str

# Allow passing an override function for testing
def verify_evaluator(
    evaluator_version: str,
    golden_suite: GoldenReferenceSuite,
    calculator_override=None
) -> Dict[str, Any]:
    
    if not evaluator_version:
        raise ValueError("Evaluator version is required")
        
    if not golden_suite.cases:
        raise ValueError("Golden suite cannot be empty")
        
    cases_result = []
    all_passed = True
    
    for case in golden_suite.cases:
        if calculator_override:
            calculated_accuracy = calculator_override(case)
        else:
            calculated_accuracy = (case.correct_samples / case.total_samples) * 100.0 if case.total_samples > 0 else 0.0
            
        difference = abs(calculated_accuracy - case.expected_accuracy)
        passed = difference <= case.tolerance
        
        if not passed:
            all_passed = False
            
        cases_result.append({
            "case_id": case.case_id,
            "expected": case.expected_accuracy,
            "calculated": calculated_accuracy,
            "difference": difference,
            "passed": passed
        })
        
    status = "AUTHORIZED" if all_passed else "UNAUTHORIZED"
    
    return {
        "evaluator_version": evaluator_version,
        "suite_id": golden_suite.suite_id,
        "suite_version": golden_suite.version,
        "suite_hash": golden_suite.suite_hash,
        "status": status,
        "cases": cases_result
    }

evaluator_registry: Dict[str, EvaluatorAuthorization] = {}

def authorize_evaluator(
    evaluator_version: str,
    golden_suite: GoldenReferenceSuite,
    calculator_override=None
) -> EvaluatorAuthorization:
    if not golden_suite.cases:
        raise ValueError("Cannot authorize with an empty suite")
        
    if not evaluator_version:
        raise ValueError("evaluator_version cannot be empty")

    result = verify_evaluator(evaluator_version, golden_suite, calculator_override)
    status = result["status"]
    
    record = EvaluatorAuthorization(
        evaluator_version=evaluator_version,
        status=status,
        golden_suite_version=golden_suite.version,
        golden_suite_hash=golden_suite.suite_hash,
        verified_at=datetime.now(timezone.utc).isoformat()
    )
    evaluator_registry[evaluator_version] = record
    return record

def invalidate_evaluator(evaluator_version: str, reason: str) -> EvaluatorAuthorization:
    if not reason:
        raise ValueError("Invalidation requires a reason")
        
    if evaluator_version not in evaluator_registry:
        raise ValueError("Evaluator not found in registry")
        
    record = evaluator_registry[evaluator_version]
    if record.status != "AUTHORIZED":
        raise ValueError(f"Cannot invalidate evaluator with status {record.status}")
        
    record.status = "INVALIDATED"
    return record
