import math
from typing import Dict, Any

CONFIDENCE_WEIGHTS = {
    "evaluator_integrity": 0.20,
    "contract_integrity": 0.20,
    "artifact_integrity": 0.15,
    "test_integrity": 0.15,
    "pilot_twin_evidence": 0.15,
    "measurement_quality": 0.15,
}

if not math.isclose(sum(CONFIDENCE_WEIGHTS.values()), 1.0, rel_tol=1e-9):
    raise ValueError("CONFIDENCE_WEIGHTS must sum to exactly 1.0")


def _validate_score(name: str, score: float) -> None:
    if not isinstance(score, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not (0 <= score <= 100):
        raise ValueError(f"{name} must be between 0 and 100, got {score}")


def calculate_evidence_confidence(
    evaluator_integrity: float,
    contract_integrity: float,
    artifact_integrity: float,
    test_integrity: float,
    pilot_twin_evidence: float,
    measurement_quality: float,
) -> float:
    scores = {
        "evaluator_integrity": evaluator_integrity,
        "contract_integrity": contract_integrity,
        "artifact_integrity": artifact_integrity,
        "test_integrity": test_integrity,
        "pilot_twin_evidence": pilot_twin_evidence,
        "measurement_quality": measurement_quality,
    }

    for name, score in scores.items():
        _validate_score(name, score)

    confidence = sum(scores[name] * CONFIDENCE_WEIGHTS[name] for name in scores)
    return round(confidence, 2)


def explain_evidence_confidence(
    evaluator_integrity: float,
    contract_integrity: float,
    artifact_integrity: float,
    test_integrity: float,
    pilot_twin_evidence: float,
    measurement_quality: float,
) -> Dict[str, Any]:
    scores = {
        "evaluator_integrity": evaluator_integrity,
        "contract_integrity": contract_integrity,
        "artifact_integrity": artifact_integrity,
        "test_integrity": test_integrity,
        "pilot_twin_evidence": pilot_twin_evidence,
        "measurement_quality": measurement_quality,
    }

    for name, score in scores.items():
        _validate_score(name, score)

    components = {}
    overall = 0.0

    for name, score in scores.items():
        weight = CONFIDENCE_WEIGHTS[name]
        contribution = score * weight
        components[name] = {
            "score": score,
            "weight": weight,
            "contribution": round(contribution, 2)
        }
        overall += contribution

    return {
        "overall_confidence": round(overall, 2),
        "components": components
    }
