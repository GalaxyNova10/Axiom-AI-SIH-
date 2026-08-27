from ai.schemas import OutcomeContract, DecisionResult

def evaluate_procurement(
    contract: OutcomeContract,
    kpi_results: dict,
    evaluator_status: str,
    artifact_integrity: bool,
    evidence_confidence: float,
    evidence_valid: bool,
    critical_failures: bool,
) -> DecisionResult:
    # Type validation
    if not isinstance(contract, OutcomeContract):
        raise TypeError("contract must be an OutcomeContract")
    if not isinstance(evaluator_status, str):
        raise TypeError("evaluator_status must be a string")
    if not isinstance(artifact_integrity, bool):
        raise TypeError("artifact_integrity must be boolean")
    if not isinstance(evidence_valid, bool):
        raise TypeError("evidence_valid must be boolean")
    if not isinstance(critical_failures, bool):
        raise TypeError("critical_failures must be boolean")
    if not isinstance(evidence_confidence, (int, float)):
        raise TypeError("evidence_confidence must be numeric")
    
    if not (0 <= evidence_confidence <= 100):
        raise ValueError("evidence_confidence must be between 0 and 100")

    result = DecisionResult(decision="ELIGIBLE", reasons=[], gates={})
    
    # GATE 1 — EVALUATOR AUTHORIZATION
    if evaluator_status != "AUTHORIZED":
        result.decision = "BLOCKED"
        result.reasons.append("Evaluator is not authorized.")
        result.gates["evaluator"] = "BLOCKED"
        return result
    else:
        result.gates["evaluator"] = "PASS"
        
    # GATE 2 — ARTIFACT INTEGRITY
    if artifact_integrity is False:
        result.decision = "RE-VALIDATION REQUIRED"
        result.reasons.append("Vendor artifact integrity could not be verified.")
        result.gates["artifact"] = "REQUIRES_REVALIDATION"
        return result
    else:
        result.gates["artifact"] = "PASS"
        
    # GATE 3 — EVIDENCE VALIDITY
    if evidence_valid is False:
        result.decision = "RE-VALIDATION REQUIRED"
        result.reasons.append("Evidence is outside its permitted validity window.")
        result.gates["evidence_validity"] = "REQUIRES_REVALIDATION"
        return result
    else:
        result.gates["evidence_validity"] = "PASS"
        
    # GATE 4 — EVIDENCE CONFIDENCE
    min_conf = contract.minimum_evidence_confidence
    if evidence_confidence < min_conf:
        result.decision = "INSUFFICIENT EVIDENCE"
        result.reasons.append(f"Evidence confidence {evidence_confidence}% is below the required {min_conf}%.")
        result.gates["evidence_confidence"] = "FAIL"
        return result
    else:
        result.gates["evidence_confidence"] = "PASS"
        
    # GATE 5 — KPI COMPLIANCE
    for kpi in contract.kpis:
        if kpi.name not in kpi_results:
            result.decision = "BLOCKED"
            result.reasons.append(f"Required KPI result is missing: {kpi.name}")
            result.gates["kpis"] = "BLOCKED"
            return result
            
        actual = kpi_results[kpi.name]
        req = kpi.threshold
        op = kpi.operator
        
        passed = False
        if op == ">=":
            passed = actual >= req
        elif op == "<=":
            passed = actual <= req
        elif op == ">":
            passed = actual > req
        elif op == "<":
            passed = actual < req
        elif op == "==":
            passed = actual == req
            
        if not passed:
            result.decision = "REJECTED"
            unit_str = f" {kpi.unit}" if kpi.unit else ""
            result.reasons.append(f"KPI failed: {kpi.name} = {actual}{unit_str}; required {op} {req}{unit_str}.")
            result.gates["kpis"] = "FAIL"
            return result

    result.gates["kpis"] = "PASS"
    
    # GATE 6 — CRITICAL FAILURE CHECK
    if critical_failures is True:
        result.decision = "REJECTED"
        result.reasons.append("Critical failure condition detected in evaluated deployment conditions.")
        result.gates["critical_failures"] = "FAIL"
        return result
    else:
        result.gates["critical_failures"] = "PASS"

    # FINAL ELIGIBILITY
    result.decision = "ELIGIBLE"
    result.reasons.append("All mandatory evidence, integrity, confidence, KPI, and failure gates passed.")
    return result
