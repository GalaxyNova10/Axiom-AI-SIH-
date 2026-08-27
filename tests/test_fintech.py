"""
Tests for Fintech 15-Point Model Evaluator & Scenario Pipeline
"""
import pytest
from ai.fintech_evaluator import run_fintech_evaluation, get_fintech_test_definitions, FINTECH_TESTS
from ai.fintech_scenario import run_fintech_demo, get_fintech_scenario_metadata, CREDVEDA_PRESET


def test_fintech_test_definitions_count():
    defs = get_fintech_test_definitions()
    assert len(defs) == 15
    assert len(FINTECH_TESTS) == 15


def test_fintech_evaluation_run():
    result = run_fintech_evaluation(
        startup_name="CredVeda AI",
        model_name="MSME Underwriter",
        claimed_accuracy=94.5,
        seed=42,
    )
    assert result.model_name == "MSME Underwriter"
    assert len(result.test_results) == 15
    assert 0.0 <= result.overall_accuracy <= 100.0
    assert 0.0 <= result.evidence_confidence_score <= 100.0
    assert result.procurement_verdict in ("ELIGIBLE", "REJECTED")
    assert "evaluator_integrity" in result.evidence_confidence_breakdown


def test_fintech_scenario_demo():
    res = run_fintech_demo()
    assert res["total_tests"] == 15
    assert len(res["test_results"]) == 15
    assert "evidence_confidence_score" in res
    assert "pilot_twin_parameters" in res
    assert res["scenario_id"] == "AXIOM-FINTECH-001"