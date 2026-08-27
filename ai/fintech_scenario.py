"""
Axiom AI — Fintech Canonical Demo Scenario
==========================================
Canonical DFS pilot scenario: CredVeda AI — Vernacular MSME Underwriting Engine
submitted to Ministry of Finance / Department of Financial Services.
"""
from typing import Any, Dict, List
from dataclasses import asdict

from ai.fintech_evaluator import (
    run_fintech_evaluation,
    get_fintech_test_definitions,
    FintechEvaluationResult,
)

FINTECH_SCENARIO_ID = "AXIOM-FINTECH-001"
FINTECH_SCENARIO_NAME = "DFS Vernacular MSME Credit Engine — Evidence-Gated Procurement"
FINTECH_DEPARTMENT = "Department of Financial Services"
FINTECH_DISTRICT = "DFS Digital Finance Pilot District (Tier-3/4 Districts)"
FINTECH_PROBLEM_STATEMENT = (
    "Procure an AI-powered credit underwriting engine for MSME borrowers in Tier-3/4 "
    "districts under the PM SVANidhi and MUDRA Yojana schemes. The engine must operate "
    "under intermittent 2G connectivity, low-end Android devices, vernacular regional "
    "languages, and must satisfy RBI Digital Lending Guidelines 2022 and DPDP Act 2023."
)

CREDVEDA_PRESET = {
    "startup_name": "CredVeda AI",
    "model_name": "Vernacular MSME Underwriting & Credit Risk Engine",
    "department": FINTECH_DEPARTMENT,
    "district": FINTECH_DISTRICT,
    "claimed_accuracy": 94.5,
    "model_description": (
        "Multimodal LLM + Graph Neural Network ensemble for thin-file and "
        "vernacular-first credit assessment. Supports 12 Indic languages, "
        "Aadhaar eKYC, GST cashflow, and agri-mandi transaction history."
    ),
    "architecture": "Multimodal LLM + GNN Risk Ensemble",
    "regulatory_claims": [
        "RBI Digital Lending Guidelines 2022 compliant",
        "DPDP Act 2023 PII tokenization",
        "FATF AML/CFT screening integrated",
        "Explainable AI with adverse action notices",
    ],
}


def get_fintech_scenario_metadata() -> Dict[str, Any]:
    return {
        "scenario_id": FINTECH_SCENARIO_ID,
        "scenario_name": FINTECH_SCENARIO_NAME,
        "title": FINTECH_SCENARIO_NAME,
        "problem_statement": FINTECH_PROBLEM_STATEMENT,
        "department": FINTECH_DEPARTMENT,
        "district": FINTECH_DISTRICT,
        "description": (
            "15-point government stress test battery evaluating a vernacular MSME credit "
            "engine across network resilience, device constraints, dialect coverage, "
            "fraud defense, regulatory compliance, and data privacy."
        ),
        "preset": CREDVEDA_PRESET,
        "test_definitions": get_fintech_test_definitions(),
        "key_conditions": {
            "connectivity": ["2G_PACKET_LOSS_40PCT", "GOOD", "OFFLINE_SYNC", "VARIABLE"],
            "device": ["LOW_END_2GB_RAM", "MID_RANGE", "HIGH_END"],
            "input": [
                "REGIONAL_DIALECT", "FADED_LOW_CONTRAST", "ADVERSARIAL_SYNTHETIC",
                "THIN_FILE_ALTERNATIVE_DATA", "SEASONAL_INCOME", "SURGE_10X",
                "GRAPH_ATTACK", "MACRO_SHOCK", "STRUCTURED_LAYERING", "PII_PROBE",
            ],
        },
    }


def run_fintech_demo(
    startup_name: str = CREDVEDA_PRESET["startup_name"],
    model_name: str = CREDVEDA_PRESET["model_name"],
    department: str = FINTECH_DEPARTMENT,
    district: str = FINTECH_DISTRICT,
    claimed_accuracy: float = CREDVEDA_PRESET["claimed_accuracy"],
    seed: int = 42,
) -> Dict[str, Any]:
    """Run the full 15-test fintech evaluation and return serializable dict."""
    result: FintechEvaluationResult = run_fintech_evaluation(
        startup_name=startup_name,
        model_name=model_name,
        department=department,
        district=district,
        claimed_accuracy=claimed_accuracy,
        seed=seed,
    )

    # Serialize test results
    serialized_tests = []
    for tr in result.test_results:
        serialized_tests.append({
            "test_id": tr.test_id,
            "code": tr.code,
            "name": tr.name,
            "domain": tr.domain,
            "description": tr.description,
            "conditions": tr.conditions,
            "accuracy": tr.accuracy,
            "latency_ms": tr.latency_ms,
            "passed": tr.passed,
            "severity": tr.severity,
            "evidence_level": tr.evidence_level,
            "evidence_hash": tr.evidence_hash,
            "failure_reason": tr.failure_reason,
            "feature_attribution": tr.feature_attribution,
        })

    # Evidence classification distribution
    evidence_distribution: Dict[str, int] = {
        "INDEPENDENTLY_VALIDATED": 0,
        "OBSERVED": 0,
        "ESTIMATED": 0,
        "DECLARED": 0,
        "CLAIMED": 0,
    }
    for tr in result.test_results:
        level = tr.evidence_level
        if level in evidence_distribution:
            evidence_distribution[level] += 1

    return {
        "evaluation_id": result.evaluation_id,
        "scenario_id": FINTECH_SCENARIO_ID,
        "startup_name": result.startup_name,
        "model_name": result.model_name,
        "department": result.department,
        "district": result.district,
        "overall_accuracy": result.overall_accuracy,
        "pass_rate": result.pass_rate,
        "total_tests": len(result.test_results),
        "passed_tests": sum(1 for tr in result.test_results if tr.passed),
        "critical_failures": result.critical_failures,
        "degraded_failures": result.degraded_failures,
        "watch_failures": result.watch_failures,
        "evidence_confidence_score": result.evidence_confidence_score,
        "evidence_confidence_breakdown": result.evidence_confidence_breakdown,
        "evidence_distribution": evidence_distribution,
        "pilot_twin_parameters": result.pilot_twin_parameters,
        "procurement_verdict": result.procurement_verdict,
        "verdict_reasons": result.verdict_reasons,
        "test_results": serialized_tests,
    }