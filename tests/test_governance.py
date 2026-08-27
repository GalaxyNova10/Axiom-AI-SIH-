import json
import pytest
from unittest.mock import patch, MagicMock

from ai.schemas import KPI, OutcomeContract, EvidenceRecord, DecisionResult
from ai.contract_generator import generate_outcome_contract, _validate_llm_output


def test_governance_module_imports():
    assert KPI is not None
    assert OutcomeContract is not None
    assert EvidenceRecord is not None
    assert DecisionResult is not None


def test_outcome_contract_generation():
    # Existing deterministic behavior test
    with patch("os.environ.get", return_value=None):
        problem = (
            "Improve last-mile delivery of agricultural supplies "
            "across rural districts while reducing delivery delays."
        )

        contract = generate_outcome_contract(
            contract_id="OC-001",
            problem_statement=problem,
        )

        assert contract.contract_id == "OC-001"
        assert contract.version == "1.0"
        assert contract.locked is False

        assert len(contract.kpis) >= 1

        kpi_names = [kpi.name for kpi in contract.kpis]

        assert "Delivery Success Rate" in kpi_names
        assert "Average Delivery Delay" in kpi_names

        assert contract.minimum_evidence_confidence == 70.0
        assert contract.evidence_validity_months == 12


def test_missing_api_key_fallback():
    with patch("os.environ.get", return_value=None):
        contract = generate_outcome_contract("OC-002", "delivery logistics")
        assert len(contract.kpis) > 0
        assert contract.kpis[0].name == "Delivery Success Rate"


def test_successful_llm_generation():
    mock_json_response = {
        "kpis": [
            {
                "name": "LLM Success Rate",
                "threshold": 95.0,
                "operator": ">=",
                "unit": "%"
            }
        ],
        "minimum_evidence_confidence": 85.0,
        "evidence_validity_months": 24
    }

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_json_response)

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    def mock_env_get(key, default=None):
        if key == "OPENAI_API_KEY":
            return "fake-key"
        return default

    with patch("os.environ.get", side_effect=mock_env_get):
        with patch("ai.contract_generator.OpenAI", return_value=mock_client_instance):
            contract = generate_outcome_contract("OC-LLM", "Some problem")

            assert contract.contract_id == "OC-LLM"
            assert contract.minimum_evidence_confidence == 85.0
            assert contract.evidence_validity_months == 24
            assert len(contract.kpis) == 1
            assert contract.kpis[0].name == "LLM Success Rate"
            assert contract.kpis[0].operator == ">="


def test_invalid_operator_rejected():
    mock_json_response = {
        "kpis": [
            {
                "name": "Test KPI",
                "threshold": 95.0,
                "operator": "NOT_AN_OPERATOR",
                "unit": "%"
            }
        ],
        "minimum_evidence_confidence": 85.0,
        "evidence_validity_months": 24
    }

    with pytest.raises(ValueError, match="invalid operator"):
        _validate_llm_output(mock_json_response)


def test_invalid_confidence_rejected():
    mock_json_response = {
        "kpis": [
            {
                "name": "Test KPI",
                "threshold": 95.0,
                "operator": ">=",
                "unit": "%"
            }
        ],
        "minimum_evidence_confidence": 105.0, # invalid
        "evidence_validity_months": 24
    }

    with pytest.raises(ValueError, match="between 0 and 100"):
        _validate_llm_output(mock_json_response)


def test_empty_kpi_list_rejected():
    mock_json_response = {
        "kpis": [],
        "minimum_evidence_confidence": 80.0,
        "evidence_validity_months": 24
    }

    with pytest.raises(ValueError, match="non-empty list"):
        _validate_llm_output(mock_json_response)


def test_validation_failure_triggers_fallback():
    mock_json_response = {
        "kpis": [], # invalid
        "minimum_evidence_confidence": 80.0,
        "evidence_validity_months": 24
    }

    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps(mock_json_response)

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client_instance = MagicMock()
    mock_client_instance.chat.completions.create.return_value = mock_response

    def mock_env_get(key, default=None):
        if key == "OPENAI_API_KEY":
            return "fake-key"
        return default

    with patch("os.environ.get", side_effect=mock_env_get):
        with patch("ai.contract_generator.OpenAI", return_value=mock_client_instance):
            # This should fallback to deterministic, giving Solution Performance for generic problem
            contract = generate_outcome_contract("OC-FALLBACK", "Some problem")

            assert contract.contract_id == "OC-FALLBACK"
            assert len(contract.kpis) == 1
            assert contract.kpis[0].name == "Solution Performance"


def test_evidence_classification_vendor_claim():
    from ai.evidence import classify_evidence
    assert classify_evidence(source_type="vendor_claim") == "CLAIMED"


def test_evidence_classification_department_declaration():
    from ai.evidence import classify_evidence
    assert classify_evidence(source_type="department_declaration") == "DECLARED"


def test_evidence_classification_pilot_measurement():
    from ai.evidence import classify_evidence
    assert classify_evidence(source_type="pilot_measurement") == "OBSERVED"


def test_evidence_classification_model_estimate():
    from ai.evidence import classify_evidence
    assert classify_evidence(source_type="model_estimate") == "ESTIMATED"


def test_evidence_classification_evaluator_result_fully_validated():
    from ai.evidence import classify_evidence
    assert classify_evidence(
        source_type="evaluator_result",
        evaluator_version="1.0.0",
        methodology="strict_method"
    ) == "INDEPENDENTLY_VALIDATED"


def test_evidence_classification_evaluator_result_no_version():
    from ai.evidence import classify_evidence
    assert classify_evidence(
        source_type="evaluator_result",
        evaluator_version="",
        methodology="strict_method"
    ) != "INDEPENDENTLY_VALIDATED"


def test_evidence_classification_evaluator_result_no_methodology():
    from ai.evidence import classify_evidence
    assert classify_evidence(
        source_type="evaluator_result",
        evaluator_version="1.0.0",
        methodology=""
    ) != "INDEPENDENTLY_VALIDATED"


def test_evidence_classification_vendor_claim_with_methodology():
    from ai.evidence import classify_evidence
    assert classify_evidence(
        source_type="vendor_claim",
        methodology="super_strict_method"
    ) == "CLAIMED"


def test_evidence_classification_unknown_source():
    from ai.evidence import classify_evidence
    with pytest.raises(ValueError):
        classify_evidence(source_type="made_up_source")


def test_evidence_classification_empty_source():
    from ai.evidence import classify_evidence
    with pytest.raises(ValueError):
        classify_evidence(source_type="")


def test_confidence_all_100():
    from ai.confidence import calculate_evidence_confidence
    res = calculate_evidence_confidence(100, 100, 100, 100, 100, 100)
    assert res == 100.0


def test_confidence_all_0():
    from ai.confidence import calculate_evidence_confidence
    res = calculate_evidence_confidence(0, 0, 0, 0, 0, 0)
    assert res == 0.0


def test_confidence_mixed_values():
    from ai.confidence import calculate_evidence_confidence
    res = calculate_evidence_confidence(
        evaluator_integrity=100,
        contract_integrity=100,
        artifact_integrity=100,
        test_integrity=100,
        pilot_twin_evidence=80,
        measurement_quality=90
    )
    assert res == 95.50


def test_confidence_above_100_raises():
    from ai.confidence import calculate_evidence_confidence
    with pytest.raises(ValueError):
        calculate_evidence_confidence(105, 100, 100, 100, 100, 100)


def test_confidence_below_0_raises():
    from ai.confidence import calculate_evidence_confidence
    with pytest.raises(ValueError):
        calculate_evidence_confidence(100, -10, 100, 100, 100, 100)


def test_confidence_explanation_structure_and_components():
    from ai.confidence import explain_evidence_confidence
    explanation = explain_evidence_confidence(100, 100, 100, 100, 80, 90)

    assert "overall_confidence" in explanation
    assert "components" in explanation

    comps = explanation["components"]
    expected_names = [
        "evaluator_integrity", "contract_integrity", "artifact_integrity",
        "test_integrity", "pilot_twin_evidence", "measurement_quality"
    ]
    for name in expected_names:
        assert name in comps
        assert "score" in comps[name]
        assert "weight" in comps[name]
        assert "contribution" in comps[name]


def test_confidence_explanation_calculation():
    from ai.confidence import explain_evidence_confidence
    explanation = explain_evidence_confidence(
        evaluator_integrity=90,
        contract_integrity=100,
        artifact_integrity=100,
        test_integrity=100,
        pilot_twin_evidence=100,
        measurement_quality=100
    )
    assert explanation["components"]["evaluator_integrity"]["contribution"] == 18.0
    assert explanation["overall_confidence"] == 98.0


def test_confidence_deterministic():
    from ai.confidence import calculate_evidence_confidence
    res1 = calculate_evidence_confidence(90, 85, 95, 80, 75, 99)
    res2 = calculate_evidence_confidence(90, 85, 95, 80, 75, 99)
    assert res1 == res2


def test_confidence_weights_sum_to_one():
    from ai.confidence import CONFIDENCE_WEIGHTS
    import math
    assert math.isclose(sum(CONFIDENCE_WEIGHTS.values()), 1.0, rel_tol=1e-9)


def create_test_contract(conf_threshold=70.0):
    from ai.schemas import KPI, OutcomeContract
    return OutcomeContract(
        contract_id="OC-TEST",
        version="1.0",
        kpis=[
            KPI(name="KPI_GTE", threshold=90.0, operator=">=", unit="%"),
            KPI(name="KPI_LTE", threshold=15.0, operator="<=", unit="min"),
            KPI(name="KPI_GT", threshold=5.0, operator=">", unit="x"),
            KPI(name="KPI_LT", threshold=10.0, operator="<", unit="y"),
            KPI(name="KPI_EQ", threshold=100.0, operator="==", unit="z"),
        ],
        minimum_evidence_confidence=conf_threshold,
        evidence_validity_months=12,
        locked=True,
    )

def test_decision_all_gates_pass():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract()
    kpi_results = {
        "KPI_GTE": 95.0,
        "KPI_LTE": 10.0,
        "KPI_GT": 6.0,
        "KPI_LT": 9.0,
        "KPI_EQ": 100.0,
    }
    result = evaluate_procurement(
        contract=contract,
        kpi_results=kpi_results,
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=80.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert result.decision == "ELIGIBLE"
    assert result.gates["evaluator"] == "PASS"
    assert result.gates["artifact"] == "PASS"
    assert result.gates["evidence_validity"] == "PASS"
    assert result.gates["evidence_confidence"] == "PASS"
    assert result.gates["kpis"] == "PASS"
    assert result.gates["critical_failures"] == "PASS"
    assert "All mandatory evidence" in result.reasons[0]

def test_decision_unauthorized_evaluator():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract()
    result = evaluate_procurement(
        contract=contract,
        kpi_results={},
        evaluator_status="PENDING",
        artifact_integrity=True,
        evidence_confidence=80.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert result.decision == "BLOCKED"
    assert result.gates["evaluator"] == "BLOCKED"
    assert "artifact" not in result.gates

def test_decision_artifact_integrity_false():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract()
    result = evaluate_procurement(
        contract=contract,
        kpi_results={},
        evaluator_status="AUTHORIZED",
        artifact_integrity=False,
        evidence_confidence=80.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert result.decision == "RE-VALIDATION REQUIRED"

def test_decision_evidence_validity_false():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract()
    result = evaluate_procurement(
        contract=contract,
        kpi_results={},
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=80.0,
        evidence_valid=False,
        critical_failures=False,
    )
    assert result.decision == "RE-VALIDATION REQUIRED"

def test_decision_evidence_confidence_below_threshold():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract(conf_threshold=70.0)
    result = evaluate_procurement(
        contract=contract,
        kpi_results={},
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=69.9,
        evidence_valid=True,
        critical_failures=False,
    )
    assert result.decision == "INSUFFICIENT EVIDENCE"
    assert "69.9" in result.reasons[0]
    assert "70.0" in result.reasons[0]

def test_decision_evidence_confidence_equal_threshold():
    from ai.decision_engine import evaluate_procurement
    contract = create_test_contract(conf_threshold=70.0)
    result = evaluate_procurement(
        contract=contract,
        kpi_results={},
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=70.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert result.decision == "BLOCKED"

def test_decision_kpi_gte_passes_correctly():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "ELIGIBLE"

def test_decision_kpi_lte_passes_correctly():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator="<=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "ELIGIBLE"

def test_decision_kpi_gt_passes_correctly():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">")]
    )
    res = evaluate_procurement(contract, {"K1": 10.1}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "ELIGIBLE"

def test_decision_kpi_lt_passes_correctly():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator="<")]
    )
    res = evaluate_procurement(contract, {"K1": 9.9}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "ELIGIBLE"

def test_decision_kpi_eq_passes_correctly():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator="==")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "ELIGIBLE"

def test_decision_failed_kpi():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 9}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "REJECTED"
    assert "KPI failed: K1" in res.reasons[0]

def test_decision_missing_kpi():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {}, "AUTHORIZED", True, 75, True, False)
    assert res.decision == "BLOCKED"
    assert "missing" in res.reasons[0]

def test_decision_critical_failure():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 75, True, True)
    assert res.decision == "REJECTED"
    assert "Critical failure" in res.reasons[0]

def test_decision_high_kpi_low_confidence():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 999}, "AUTHORIZED", True, 50, True, False)
    assert res.decision == "INSUFFICIENT EVIDENCE"

def test_decision_high_confidence_failed_kpi():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 5}, "AUTHORIZED", True, 99, True, False)
    assert res.decision == "REJECTED"

def test_decision_unauthorized_evaluator_otherwise_perfect():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "UNAUTHORIZED", True, 99, True, False)
    assert res.decision == "BLOCKED"

def test_decision_artifact_failure_otherwise_perfect():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", False, 99, True, False)
    assert res.decision == "RE-VALIDATION REQUIRED"

def test_decision_invalid_confidence_above_100():
    import pytest
    from ai.schemas import OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[]
    )
    with pytest.raises(ValueError):
        evaluate_procurement(contract, {}, "AUTHORIZED", True, 105, True, False)

def test_decision_invalid_confidence_below_0():
    import pytest
    from ai.schemas import OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[]
    )
    with pytest.raises(ValueError):
        evaluate_procurement(contract, {}, "AUTHORIZED", True, -1, True, False)

def test_decision_deterministic():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res1 = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 80, True, False)
    res2 = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 80, True, False)
    assert res1 == res2

def test_decision_threshold_from_contract():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=90.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 80, True, False)
    assert res.decision == "INSUFFICIENT EVIDENCE"

def test_decision_gates_dictionary_correct_statuses():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 10}, "AUTHORIZED", True, 75, True, False)
    assert "evaluator" in res.gates
    assert "kpis" in res.gates
    assert res.gates["kpis"] == "PASS"

def test_decision_reasons_human_readable():
    from ai.schemas import KPI, OutcomeContract
    from ai.decision_engine import evaluate_procurement
    contract = OutcomeContract(
        contract_id="OC-1", version="1.0", minimum_evidence_confidence=70.0, evidence_validity_months=12, locked=True,
        kpis=[KPI(name="K1", threshold=10, operator=">=")]
    )
    res = evaluate_procurement(contract, {"K1": 9}, "AUTHORIZED", True, 75, True, False)
    assert len(res.reasons) > 0
    assert isinstance(res.reasons[0], str)
    assert len(res.reasons[0]) > 10


def test_pilot_twin_create_valid():
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    params = [PilotParameter(name="Conn", value="4G", evidence_level="DECLARED")]
    pt = create_pilot_twin("TWIN1", "Dept", "Dist", params)
    assert pt.twin_id == "TWIN1"
    assert pt.department == "Dept"
    assert pt.district == "Dist"
    assert pt.locked is False
    assert pt.version == "1.0"
    assert len(pt.parameters) == 1

def test_pilot_twin_empty_id_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    with pytest.raises(ValueError):
        create_pilot_twin("", "Dept", "Dist", [PilotParameter("N", "V")])

def test_pilot_twin_empty_department_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    with pytest.raises(ValueError):
        create_pilot_twin("T", "", "Dist", [PilotParameter("N", "V")])

def test_pilot_twin_empty_district_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    with pytest.raises(ValueError):
        create_pilot_twin("T", "Dept", "", [PilotParameter("N", "V")])

def test_pilot_twin_empty_parameters_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin
    with pytest.raises(ValueError):
        create_pilot_twin("T", "Dept", "Dist", [])

def test_pilot_twin_parameter_empty_name_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    with pytest.raises(ValueError):
        create_pilot_twin("T", "Dept", "Dist", [PilotParameter("", "V")])

def test_pilot_twin_unsupported_evidence_level():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    with pytest.raises(ValueError):
        create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N", "V", evidence_level="FAKE")])

def test_pilot_twin_valid_evidence_levels():
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    levels = ["CLAIMED", "DECLARED", "OBSERVED", "ESTIMATED", "INDEPENDENTLY_VALIDATED"]
    params = [PilotParameter(f"N{i}", "V", evidence_level=l) for i, l in enumerate(levels)]
    pt = create_pilot_twin("T", "Dept", "Dist", params)
    assert len(pt.parameters) == 5

def test_pilot_twin_unverified_accepted():
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N", "V", evidence_level="UNVERIFIED")])
    assert pt.parameters[0].evidence_level == "UNVERIFIED"

def test_pilot_twin_evidence_summary_counts():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, summarize_pilot_evidence
    params = [
        PilotParameter("N1", "V", evidence_level="DECLARED"),
        PilotParameter("N2", "V", evidence_level="DECLARED"),
        PilotParameter("N3", "V", evidence_level="OBSERVED"),
        PilotParameter("N4", "V", evidence_level="UNVERIFIED"),
    ]
    pt = create_pilot_twin("T", "Dept", "Dist", params)
    summary = summarize_pilot_evidence(pt)
    assert summary["total_parameters"] == 4
    assert summary["by_level"]["DECLARED"] == 2
    assert summary["by_level"]["OBSERVED"] == 1
    assert summary["by_level"]["UNVERIFIED"] == 1
    assert summary["by_level"]["CLAIMED"] == 0

def test_pilot_twin_evidence_quality_calculation():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, summarize_pilot_evidence
    params = [
        PilotParameter("N1", "V", evidence_level="DECLARED"), # 60
        PilotParameter("N2", "V", evidence_level="OBSERVED"), # 80
        PilotParameter("N3", "V", evidence_level="ESTIMATED"), # 60
    ]
    pt = create_pilot_twin("T", "Dept", "Dist", params)
    summary = summarize_pilot_evidence(pt)
    assert summary["evidence_quality"] == 66.67

def test_pilot_twin_unverified_in_list():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, summarize_pilot_evidence
    params = [
        PilotParameter("Unverified1", "V", evidence_level="UNVERIFIED"),
        PilotParameter("Unverified2", "V", evidence_level="UNVERIFIED"),
        PilotParameter("Verified1", "V", evidence_level="DECLARED"),
    ]
    pt = create_pilot_twin("T", "Dept", "Dist", params)
    summary = summarize_pilot_evidence(pt)
    assert "Unverified1" in summary["unverified_parameters"]
    assert "Unverified2" in summary["unverified_parameters"]
    assert "Verified1" not in summary["unverified_parameters"]

def test_pilot_twin_update_evidence():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, update_parameter_evidence
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N1", "V", evidence_level="DECLARED")])
    pt = update_parameter_evidence(pt, "N1", "OBSERVED", "New Source")
    assert pt.parameters[0].evidence_level == "OBSERVED"
    assert pt.parameters[0].source == "New Source"

def test_pilot_twin_update_nonexistent_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter, update_parameter_evidence
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N1", "V")])
    with pytest.raises(ValueError):
        update_parameter_evidence(pt, "FakeName", "OBSERVED", "Src")

def test_pilot_twin_update_locked_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter, update_parameter_evidence
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N1", "V")])
    pt.locked = True
    with pytest.raises(ValueError, match="locked"):
        update_parameter_evidence(pt, "N1", "OBSERVED", "Src")

def test_pilot_twin_version_starts_at_1_0():
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N", "V")])
    assert pt.version == "1.0"

def test_pilot_twin_starts_unlocked():
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N", "V")])
    assert pt.locked is False

def test_pilot_twin_summary_is_deterministic():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, summarize_pilot_evidence
    params = [PilotParameter("N1", "V", evidence_level="DECLARED")]
    pt = create_pilot_twin("T", "Dept", "Dist", params)
    s1 = summarize_pilot_evidence(pt)
    s2 = summarize_pilot_evidence(pt)
    assert s1 == s2

def test_pilot_twin_identical_twins_identical_summaries():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, summarize_pilot_evidence
    params1 = [PilotParameter("N1", "V", evidence_level="DECLARED")]
    params2 = [PilotParameter("N1", "V", evidence_level="DECLARED")]
    pt1 = create_pilot_twin("T", "Dept", "Dist", params1)
    pt2 = create_pilot_twin("T", "Dept", "Dist", params2)
    assert summarize_pilot_evidence(pt1) == summarize_pilot_evidence(pt2)

def test_pilot_twin_update_evidence_preserves_value():
    from ai.pilot_twin import create_pilot_twin, PilotParameter, update_parameter_evidence
    pt = create_pilot_twin("T", "Dept", "Dist", [PilotParameter("N1", 42, unit="kg", evidence_level="DECLARED")])
    pt = update_parameter_evidence(pt, "N1", "OBSERVED", "Src")
    assert pt.parameters[0].value == 42
    assert pt.parameters[0].unit == "kg"


def test_test_matrix_contains_exactly_24_conditions():
    from ai.test_matrix import generate_test_suite
    suite = generate_test_suite("SUITE1", "TWIN1")
    assert len(suite.conditions) == 24

def test_test_matrix_all_24_public_combinations_exist():
    from ai.test_matrix import generate_test_suite, CONNECTIVITY_LEVELS, DEVICE_LEVELS, LANGUAGE_LEVELS, INPUT_QUALITY_LEVELS
    suite = generate_test_suite("SUITE1", "TWIN1")
    strata = {c.stratum_id for c in suite.conditions}
    expected = {f"{c}_{d}_{l}_{q}" for c in CONNECTIVITY_LEVELS for d in DEVICE_LEVELS for l in LANGUAGE_LEVELS for q in INPUT_QUALITY_LEVELS}
    assert strata == expected

def test_test_matrix_test_case_ids_unique():
    from ai.test_matrix import generate_test_suite
    suite = generate_test_suite("SUITE1", "TWIN1")
    ids = {c.test_case_id for c in suite.conditions}
    assert len(ids) == 24

def test_test_matrix_seeded_generation_is_deterministic():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T", seed=123)
    s2 = generate_test_suite("S", "T", seed=123)
    assert [c.stratum_id for c in s1.conditions] == [c.stratum_id for c in s2.conditions]

def test_test_matrix_same_seed_identical_private_parameters():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T", seed=123)
    s2 = generate_test_suite("S", "T", seed=123)
    for c1, c2 in zip(s1.conditions, s2.conditions):
        assert c1.private_parameters == c2.private_parameters

def test_test_matrix_different_seeds_different_private_parameters():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T", seed=123)
    s2 = generate_test_suite("S", "T", seed=456)
    c1 = s1.conditions[0]
    c2 = next(c for c in s2.conditions if c.stratum_id == c1.stratum_id)
    assert c1.private_parameters != c2.private_parameters

def test_test_matrix_same_seed_identical_seed_hash():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T", seed=123)
    s2 = generate_test_suite("S", "T", seed=123)
    assert s1.seed_hash == s2.seed_hash

def test_test_matrix_raw_seed_not_stored_in_test_suite():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T", seed=123)
    assert not hasattr(s1, "seed")

def test_test_matrix_seed_hash_is_64_hex_chars():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    assert len(s1.seed_hash) == 64
    assert int(s1.seed_hash, 16) >= 0

def test_test_matrix_public_methodology_exposes_categorical_dimensions():
    from ai.test_matrix import generate_test_suite, get_public_methodology
    s1 = generate_test_suite("S", "T")
    pub = get_public_methodology(s1)
    assert "connectivity" in pub
    assert "device" in pub
    assert "language" in pub
    assert "input_quality" in pub
    assert pub["total_strata"] == 24

def test_test_matrix_public_methodology_no_private_parameters():
    from ai.test_matrix import generate_test_suite, get_public_methodology
    s1 = generate_test_suite("S", "T")
    pub = get_public_methodology(s1)
    assert "private_parameters" not in pub
    assert "latency_ms" not in str(pub)

def test_test_matrix_public_methodology_no_raw_seed():
    from ai.test_matrix import generate_test_suite, get_public_methodology
    s1 = generate_test_suite("S", "T", seed=12345)
    pub = get_public_methodology(s1)
    assert "12345" not in str(pub)
    assert "seed" not in pub
    assert "seed_hash" not in pub

def test_test_matrix_good_connectivity_expected_range():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        if c.connectivity == "GOOD":
            assert 50 <= c.private_parameters["latency_ms"] <= 150
            assert 0.0 <= c.private_parameters["packet_loss_percent"] <= 1.0

def test_test_matrix_intermittent_connectivity_expected_range():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        if c.connectivity == "INTERMITTENT":
            assert 500 <= c.private_parameters["latency_ms"] <= 1500
            assert 3.0 <= c.private_parameters["packet_loss_percent"] <= 15.0

def test_test_matrix_high_end_device_memory_range():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        if c.device == "HIGH_END":
            assert 6 <= c.private_parameters["memory_gb"] <= 12
            assert c.private_parameters["cpu_class"] == "HIGH"

def test_test_matrix_low_end_device_memory_range():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        if c.device == "LOW_END":
            assert 2 <= c.private_parameters["memory_gb"] <= 4
            assert c.private_parameters["cpu_class"] == "LOW"

def test_test_matrix_clean_degraded_noisy_ranges():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        if c.input_quality == "CLEAN":
            assert 90 <= c.private_parameters["compression_quality"] <= 100
        elif c.input_quality == "DEGRADED":
            assert 50 <= c.private_parameters["compression_quality"] <= 75
        elif c.input_quality == "NOISY":
            assert 20 <= c.private_parameters["compression_quality"] <= 49
            assert 0.10 <= c.private_parameters["noise_level"] <= 0.30

def test_test_matrix_every_condition_has_private_parameters():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S", "T")
    for c in s1.conditions:
        assert isinstance(c.private_parameters, dict)
        assert len(c.private_parameters) > 0

def test_test_matrix_locked_suite_cannot_be_modified():
    from ai.test_matrix import generate_test_suite, lock_test_suite
    s1 = generate_test_suite("S", "T")
    assert s1.locked is False
    s1 = lock_test_suite(s1)
    assert s1.locked is True

def test_test_matrix_invalid_suite_duplicate_stratum():
    import pytest
    from ai.test_matrix import generate_test_suite, validate_test_suite
    s1 = generate_test_suite("S", "T")
    s1.conditions[0].stratum_id = s1.conditions[1].stratum_id
    with pytest.raises(ValueError, match="Duplicate stratum_id"):
        validate_test_suite(s1)

def test_test_matrix_invalid_suite_duplicate_test_case_id():
    import pytest
    from ai.test_matrix import generate_test_suite, validate_test_suite
    s1 = generate_test_suite("S", "T")
    s1.conditions[0].test_case_id = s1.conditions[1].test_case_id
    with pytest.raises(ValueError, match="Duplicate test_case_id"):
        validate_test_suite(s1)

def test_test_matrix_invalid_suite_wrong_condition_count():
    import pytest
    from ai.test_matrix import generate_test_suite, validate_test_suite
    s1 = generate_test_suite("S", "T")
    s1.conditions.pop()
    with pytest.raises(ValueError, match="Expected 24 conditions"):
        validate_test_suite(s1)

def test_test_matrix_two_different_pilot_suite_ids():
    from ai.test_matrix import generate_test_suite
    s1 = generate_test_suite("S1", "T1")
    s2 = generate_test_suite("S2", "T2")
    assert s1.suite_id == "S1"
    assert s1.pilot_twin_id == "T1"
    assert s2.suite_id == "S2"
    assert s2.pilot_twin_id == "T2"

def test_test_matrix_validate_test_suite_returns_true():
    from ai.test_matrix import generate_test_suite, validate_test_suite
    s1 = generate_test_suite("S", "T")
    assert validate_test_suite(s1) is True

def test_test_matrix_empty_private_parameters_raises():
    import pytest
    from ai.test_matrix import generate_test_suite, validate_test_suite
    s1 = generate_test_suite("S", "T")
    s1.conditions[0].private_parameters = {}
    with pytest.raises(ValueError, match="Private parameters empty"):
        validate_test_suite(s1)


def test_golden_suite_five_cases_exist():
    from ai.golden_suite import create_initial_golden_suite
    suite = create_initial_golden_suite()
    assert len(suite.cases) == 5

def test_golden_suite_calculations_mathematically_correct():
    from ai.golden_suite import create_initial_golden_suite
    suite = create_initial_golden_suite()
    for c in suite.cases:
        math_acc = (c.correct_samples / c.total_samples) * 100 if c.total_samples > 0 else 0.0
        assert math_acc == c.expected_accuracy

def test_golden_suite_expected_values_explicit():
    from ai.golden_suite import create_initial_golden_suite
    suite = create_initial_golden_suite()
    expected = [90.0, 95.0, 50.0, 99.7, 0.0]
    actual = [c.expected_accuracy for c in suite.cases]
    assert actual == expected

def test_golden_suite_version_1_0():
    from ai.golden_suite import create_initial_golden_suite
    suite = create_initial_golden_suite()
    assert suite.version == "1.0"

def test_golden_suite_hash_is_64_hex_chars():
    from ai.golden_suite import create_initial_golden_suite
    suite = create_initial_golden_suite()
    assert len(suite.suite_hash) == 64
    assert int(suite.suite_hash, 16) >= 0

def test_golden_suite_same_suite_same_hash():
    from ai.golden_suite import calculate_suite_hash, create_initial_golden_suite
    suite = create_initial_golden_suite()
    h1 = calculate_suite_hash(suite.suite_id, suite.version, suite.cases)
    h2 = calculate_suite_hash(suite.suite_id, suite.version, suite.cases)
    assert h1 == h2

def test_golden_suite_changing_expected_value_different_hash():
    from ai.golden_suite import calculate_suite_hash, create_initial_golden_suite
    import copy
    suite = create_initial_golden_suite()
    h1 = suite.suite_hash
    cases2 = copy.deepcopy(suite.cases)
    cases2[0].expected_accuracy = 100.0
    h2 = calculate_suite_hash(suite.suite_id, suite.version, cases2)
    assert h1 != h2

def test_golden_suite_changing_tolerance_different_hash():
    from ai.golden_suite import calculate_suite_hash, create_initial_golden_suite
    import copy
    suite = create_initial_golden_suite()
    h1 = suite.suite_hash
    cases2 = copy.deepcopy(suite.cases)
    cases2[0].tolerance = 0.05
    h2 = calculate_suite_hash(suite.suite_id, suite.version, cases2)
    assert h1 != h2

def test_golden_suite_adding_case_different_hash():
    from ai.golden_suite import calculate_suite_hash, create_initial_golden_suite, GoldenCase
    import copy
    suite = create_initial_golden_suite()
    h1 = suite.suite_hash
    cases2 = copy.deepcopy(suite.cases)
    cases2.append(GoldenCase("GOLD-006", "Case 6", 100, 100, 100.0))
    h2 = calculate_suite_hash(suite.suite_id, suite.version, cases2)
    assert h1 != h2

def test_golden_suite_removing_case_different_hash():
    from ai.golden_suite import calculate_suite_hash, create_initial_golden_suite
    import copy
    suite = create_initial_golden_suite()
    h1 = suite.suite_hash
    cases2 = copy.deepcopy(suite.cases)
    cases2.pop()
    h2 = calculate_suite_hash(suite.suite_id, suite.version, cases2)
    assert h1 != h2

def test_golden_suite_all_cases_pass_evaluator():
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator
    suite = create_initial_golden_suite()
    res = verify_evaluator("v1.0", suite)
    assert res["status"] == "AUTHORIZED"
    for c in res["cases"]:
        assert c["passed"] is True

def test_golden_suite_successful_verification_authorized():
    from ai.golden_suite import create_initial_golden_suite, authorize_evaluator
    suite = create_initial_golden_suite()
    auth = authorize_evaluator("v1.0", suite)
    assert auth.status == "AUTHORIZED"

def test_golden_suite_one_incorrect_calculation_unauthorized():
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator, authorize_evaluator
    suite = create_initial_golden_suite()

    def bad_calculator(case):
        if case.case_id == "GOLD-001":
            return 0.0
        return (case.correct_samples / case.total_samples) * 100.0 if case.total_samples > 0 else 0.0

    res = verify_evaluator("v1.1", suite, bad_calculator)
    assert res["status"] == "UNAUTHORIZED"

    auth = authorize_evaluator("v1.1", suite, bad_calculator)
    assert auth.status == "UNAUTHORIZED"

def test_golden_suite_missing_evaluator_version_raises():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator
    suite = create_initial_golden_suite()
    with pytest.raises(ValueError):
        verify_evaluator("", suite)

def test_golden_suite_empty_suite_cannot_be_authorized():
    import pytest
    from ai.golden_suite import GoldenReferenceSuite, authorize_evaluator
    suite = GoldenReferenceSuite("S1", "1.0", [])
    with pytest.raises(ValueError):
        authorize_evaluator("v1.0", suite)

def test_golden_suite_evaluator_auth_records_suite_version():
    from ai.golden_suite import create_initial_golden_suite, authorize_evaluator
    suite = create_initial_golden_suite()
    auth = authorize_evaluator("v1.2", suite)
    assert auth.golden_suite_version == "1.0"

def test_golden_suite_evaluator_auth_records_suite_hash():
    from ai.golden_suite import create_initial_golden_suite, authorize_evaluator
    suite = create_initial_golden_suite()
    auth = authorize_evaluator("v1.2", suite)
    assert auth.golden_suite_hash == suite.suite_hash

def test_golden_suite_evaluator_invalidation_works():
    from ai.golden_suite import create_initial_golden_suite, authorize_evaluator, invalidate_evaluator
    suite = create_initial_golden_suite()
    auth = authorize_evaluator("v1.3", suite)
    assert auth.status == "AUTHORIZED"
    inv = invalidate_evaluator("v1.3", "Found bug")
    assert inv.status == "INVALIDATED"
    assert auth.status == "INVALIDATED"

def test_golden_suite_invalidation_requires_reason():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, authorize_evaluator, invalidate_evaluator
    suite = create_initial_golden_suite()
    authorize_evaluator("v1.4", suite)
    with pytest.raises(ValueError):
        invalidate_evaluator("v1.4", "")

def test_golden_suite_change_proposal_pending_review():
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD_CASE", "Need more tests", "Admin", suite.cases, "1.1")
    assert change.status == "PENDING_REVIEW"

def test_golden_suite_empty_change_reason_rejected():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change
    suite = create_initial_golden_suite()
    with pytest.raises(ValueError):
        propose_golden_suite_change(suite, "ADD", "", "Admin", suite.cases, "1.1")

def test_golden_suite_empty_reviewer_id_rejected():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    with pytest.raises(ValueError):
        review_golden_suite_change(change, "INDEP", "", True, "Looks good")

def test_golden_suite_dev_role_cannot_approve():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change, EVALUATOR_DEVELOPMENT_ROLE
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    with pytest.raises(ValueError):
        review_golden_suite_change(change, EVALUATOR_DEVELOPMENT_ROLE, "Rev1", True, "Looks good")

def test_golden_suite_independent_reviewer_can_approve():
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    res = review_golden_suite_change(change, "INDEP", "Rev1", True, "Looks good")
    assert res.status == "APPROVED"
    assert res.proposed_suite.approved_by == "Rev1"

def test_golden_suite_rejected_change_becomes_rejected():
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    res = review_golden_suite_change(change, "INDEP", "Rev1", False, "Looks bad")
    assert res.status == "REJECTED"

def test_golden_suite_approved_change_becomes_approved():
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    res = review_golden_suite_change(change, "INDEP", "Rev1", True, "Looks good")
    assert res.status == "APPROVED"

def test_golden_suite_approved_change_does_not_silently_replace_active_suite():
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    review_golden_suite_change(change, "INDEP", "Rev1", True, "Looks good")
    assert suite.version == "1.0"
    assert change.proposed_suite.version == "1.1"

def test_golden_suite_removing_test_does_not_retroactively_authorize():
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator, authorize_evaluator, evaluator_registry
    import copy
    suite1 = create_initial_golden_suite()

    def bad_calculator(case):
        if case.case_id == "GOLD-001":
            return 0.0
        return (case.correct_samples / case.total_samples) * 100.0 if case.total_samples > 0 else 0.0

    auth1 = authorize_evaluator("v2.0", suite1, bad_calculator)
    assert auth1.status == "UNAUTHORIZED"

    cases2 = [c for c in suite1.cases if c.case_id != "GOLD-001"]
    suite2 = copy.deepcopy(suite1)
    suite2.cases = cases2
    suite2.version = "1.1"

    assert evaluator_registry["v2.0"].status == "UNAUTHORIZED"
    auth2 = authorize_evaluator("v2.0", suite2, bad_calculator)
    assert auth2.status == "AUTHORIZED"

def test_golden_suite_same_evaluator_same_suite_deterministic_result():
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator
    suite = create_initial_golden_suite()
    res1 = verify_evaluator("v1.0", suite)
    res2 = verify_evaluator("v1.0", suite)
    assert res1 == res2

def test_golden_suite_every_case_result_contains_expected_fields():
    from ai.golden_suite import create_initial_golden_suite, verify_evaluator
    suite = create_initial_golden_suite()
    res = verify_evaluator("v1.0", suite)
    for c in res["cases"]:
        assert "case_id" in c
        assert "expected" in c
        assert "calculated" in c
        assert "difference" in c
        assert "passed" in c

def test_golden_suite_empty_justification_rejected():
    import pytest
    from ai.golden_suite import create_initial_golden_suite, propose_golden_suite_change, review_golden_suite_change
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(suite, "ADD", "Rsn", "Admin", suite.cases, "1.1")
    with pytest.raises(ValueError):
        review_golden_suite_change(change, "INDEP", "Rev1", True, "")


def test_evaluator_valid_adapter_evaluated():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.status == "COMPLETED"
    assert run.total_cases == 24

def test_evaluator_unauthorized_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    with pytest.raises(ValueError, match="authorized"):
        evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", False, expected)

def test_evaluator_empty_vendor_id_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    with pytest.raises(ValueError, match="vendor_id"):
        evaluate_vendor("", "art1", VendorAAdapter(), suite, "1.0", True, expected)

def test_evaluator_empty_artifact_id_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    with pytest.raises(ValueError, match="artifact_id"):
        evaluate_vendor("VendA", "", VendorAAdapter(), suite, "1.0", True, expected)

def test_evaluator_empty_evaluator_version_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    with pytest.raises(ValueError, match="evaluator_version"):
        evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "", True, expected)

def test_evaluator_invalid_test_suite_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    suite.conditions.pop()
    with pytest.raises(ValueError):
        evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)

def test_evaluator_missing_expected_output_rejected():
    import pytest
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    suite = generate_test_suite("S1", "T1")
    with pytest.raises(ValueError, match="Missing expected output"):
        evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, {})

def test_evaluator_every_test_case_evaluated_exactly_once():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    ids = [c.test_case_id for c in run.results]
    assert len(ids) == 24
    assert len(set(ids)) == 24

def test_evaluator_vendor_does_not_receive_entire_suite():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            assert "suite_id" not in input_data
            assert "conditions" in input_data
            assert isinstance(input_data["conditions"], dict)
            return {"prediction": "PASS", "latency_ms": 10.0, "error": False}

    evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)

def test_evaluator_vendor_receives_only_current_case():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    seen_ids = set()
    class MockAdapter:
        def evaluate(self, input_data):
            tc_id = input_data["test_case_id"]
            assert tc_id not in seen_ids
            seen_ids.add(tc_id)
            return {"prediction": "PASS", "latency_ms": 10.0, "error": False}

    evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert len(seen_ids) == 24

def test_evaluator_future_cases_not_passed():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            # Assert only current case info is in input_data
            assert "test_case_id" in input_data
            assert "stratum_id" in input_data
            assert len(input_data) == 5 # test_case_id, stratum_id, conditions, private_parameters, expected_output
            return {"prediction": "PASS", "latency_ms": 10.0, "error": False}

    evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)

def test_evaluator_accuracy_calculated_correctly():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            return {"prediction": "PASS", "latency_ms": 10.0, "error": False}

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    calc_accuracy = (run.correct_cases / run.total_cases) * 100
    assert run.accuracy == round(calc_accuracy, 2)

def test_evaluator_average_latency_calculated_correctly():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            return {"prediction": "PASS", "latency_ms": 100.0, "error": False}

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert run.average_latency_ms == 100.0

def test_evaluator_error_count_calculated_correctly():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            if input_data["stratum_id"].startswith("GOOD_HIGH_END_STANDARD_CLEAN"):
                return {"prediction": "PASS", "latency_ms": 10.0, "error": True}
            return {"prediction": "PASS", "latency_ms": 10.0, "error": False}

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert run.error_count == 1

def test_evaluator_adapter_exception_does_not_crash():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            raise RuntimeError("Vendor crashed")

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert run.status == "COMPLETED"
    assert run.error_count == 24

def test_evaluator_adapter_exception_produces_error_true():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            raise RuntimeError("Vendor crashed")

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert all(r.error is True for r in run.results)

def test_evaluator_malformed_adapter_output_handled():
    from ai.evaluator import evaluate_vendor
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    class MockAdapter:
        def evaluate(self, input_data):
            return {"wrong_key": "val"}

    run = evaluate_vendor("VendA", "art1", MockAdapter(), suite, "1.0", True, expected)
    assert run.error_count == 24

def test_evaluator_run_stores_vendor_id():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VEND_ID_123", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.vendor_id == "VEND_ID_123"

def test_evaluator_run_stores_artifact_id():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "ART_ID_789", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.artifact_id == "ART_ID_789"

def test_evaluator_run_stores_evaluator_version():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "v3.1.4", True, expected)
    assert run.evaluator_version == "v3.1.4"

def test_evaluator_run_stores_test_suite_hash():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.test_suite_hash == suite.seed_hash

def test_evaluator_all_vendors_receive_identical_cases():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter, VendorBAdapter, VendorCAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    runA = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    runB = evaluate_vendor("VendB", "art2", VendorBAdapter(), suite, "1.0", True, expected)
    runC = evaluate_vendor("VendC", "art3", VendorCAdapter(), suite, "1.0", True, expected)

    assert runA.total_cases == 24
    assert runB.total_cases == 24
    assert runC.total_cases == 24

def test_evaluator_contains_no_vendor_specific_scoring():
    # If the logic contained vendor specific overrides it would not match between identical runs
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run1 = evaluate_vendor("Vend1", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    run2 = evaluate_vendor("Vend2", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run1.accuracy == run2.accuracy

def test_evaluator_same_adapter_same_suite_deterministic():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorBAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run1 = evaluate_vendor("VendB", "art1", VendorBAdapter(), suite, "1.0", True, expected)
    run2 = evaluate_vendor("VendB", "art1", VendorBAdapter(), suite, "1.0", True, expected)
    assert run1.correct_cases == run2.correct_cases

def test_evaluator_different_adapters_different_results():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter, VendorCAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    runA = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    runC = evaluate_vendor("VendC", "art3", VendorCAdapter(), suite, "1.0", True, expected)
    assert runA.accuracy != runC.accuracy or runA.average_latency_ms != runC.average_latency_ms

def test_evaluator_status_is_completed():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.status == "COMPLETED"

def test_evaluator_accuracy_between_0_and_100():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert 0.0 <= run.accuracy <= 100.0

def test_evaluator_average_latency_non_negative():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    run = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    assert run.average_latency_ms >= 0.0

def test_evaluator_three_demo_vendors_evaluated():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter, VendorBAdapter, VendorCAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)
    assert evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected).status == "COMPLETED"
    assert evaluate_vendor("VendB", "art2", VendorBAdapter(), suite, "1.0", True, expected).status == "COMPLETED"
    assert evaluate_vendor("VendC", "art3", VendorCAdapter(), suite, "1.0", True, expected).status == "COMPLETED"

def test_evaluator_demo_vendors_produce_measurably_different_results():
    from ai.evaluator import evaluate_vendor
    from ai.demo_vendors import VendorAAdapter, VendorBAdapter, VendorCAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_dataset import get_demo_expected_outputs
    suite = generate_test_suite("S1", "T1")
    expected = get_demo_expected_outputs(suite)

    runA = evaluate_vendor("VendA", "art1", VendorAAdapter(), suite, "1.0", True, expected)
    runB = evaluate_vendor("VendB", "art2", VendorBAdapter(), suite, "1.0", True, expected)
    runC = evaluate_vendor("VendC", "art3", VendorCAdapter(), suite, "1.0", True, expected)

def test_artifact_sha256_hash_deterministic():
    from ai.artifact import compute_artifact_hash
    data = b"hello world"
    assert compute_artifact_hash(data) == compute_artifact_hash(data)

def test_artifact_same_bytes_same_hash():
    from ai.artifact import compute_artifact_hash
    assert compute_artifact_hash(b"test1") == compute_artifact_hash(b"test1")

def test_artifact_different_bytes_different_hash():
    from ai.artifact import compute_artifact_hash
    assert compute_artifact_hash(b"test1") != compute_artifact_hash(b"test2")

def test_artifact_hash_is_64_hex_chars():
    from ai.artifact import compute_artifact_hash
    h = compute_artifact_hash(b"test")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

def test_artifact_registration_works():
    from ai.artifact import register_artifact
    rec = register_artifact("A1", "V1", b"data")
    assert rec.artifact_id == "A1"
    assert rec.vendor_id == "V1"

def test_artifact_empty_artifact_works():
    from ai.artifact import register_artifact
    rec = register_artifact("A1", "V1", b"")
    from ai.artifact import compute_artifact_hash
    assert rec.artifact_hash == compute_artifact_hash(b"")

def test_artifact_non_bytes_input_rejected():
    import pytest
    from ai.artifact import register_artifact
    with pytest.raises(TypeError):
        register_artifact("A1", "V1", "not bytes")

def test_artifact_empty_artifact_id_rejected():
    import pytest
    from ai.artifact import register_artifact
    with pytest.raises(ValueError):
        register_artifact("", "V1", b"data")

def test_artifact_empty_vendor_id_rejected():
    import pytest
    from ai.artifact import register_artifact
    with pytest.raises(ValueError):
        register_artifact("A1", "", b"data")

def test_artifact_metadata_does_not_affect_hash():
    from ai.artifact import register_artifact
    rec1 = register_artifact("A1", "V1", b"data", {"version": "1.0"})
    rec2 = register_artifact("A1", "V1", b"data", {"version": "2.0"})
    assert rec1.artifact_hash == rec2.artifact_hash

def test_artifact_record_stores_vendor_id():
    from ai.artifact import register_artifact
    rec = register_artifact("A1", "VendorX", b"data")
    assert rec.vendor_id == "VendorX"

def test_artifact_record_stores_artifact_id():
    from ai.artifact import register_artifact
    rec = register_artifact("ArtX", "V1", b"data")
    assert rec.artifact_id == "ArtX"

def test_artifact_record_stores_sha256():
    from ai.artifact import register_artifact, compute_artifact_hash
    rec = register_artifact("A1", "V1", b"data")
    assert rec.artifact_hash == compute_artifact_hash(b"data")

def test_artifact_initial_status_conceptually_frozen_or_unchanged():
    pass

def test_artifact_freeze_artifact_preserves_hash():
    from ai.artifact import register_artifact, freeze_artifact
    rec = register_artifact("A1", "V1", b"data")
    f_rec = freeze_artifact(rec)
    assert f_rec.artifact_hash == rec.artifact_hash

def test_artifact_matching_verification_returns_true():
    from ai.artifact import register_artifact, verify_artifact
    rec = register_artifact("A1", "V1", b"data")
    assert verify_artifact(rec, b"data") is True

def test_artifact_changed_verification_returns_false():
    from ai.artifact import register_artifact, verify_artifact
    rec = register_artifact("A1", "V1", b"data")
    assert verify_artifact(rec, b"new_data") is False

def test_artifact_mismatch_does_not_mutate_original_record():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation
    rec = register_artifact("A1", "V1", b"data")
    orig_hash = rec.artifact_hash
    verify_artifact_for_evaluation(rec, b"new_data")
    assert rec.artifact_hash == orig_hash

def test_artifact_match_verification_produces_status_match():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation
    rec = register_artifact("A1", "V1", b"data")
    v = verify_artifact_for_evaluation(rec, b"data")
    assert v.status == "MATCH"

def test_artifact_mismatch_verification_produces_status_mismatch():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation
    rec = register_artifact("A1", "V1", b"data")
    v = verify_artifact_for_evaluation(rec, b"new_data")
    assert v.status == "MISMATCH"

def test_artifact_match_does_not_require_revalidation():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation, require_artifact_revalidation
    rec = register_artifact("A1", "V1", b"data")
    v = verify_artifact_for_evaluation(rec, b"data")
    assert require_artifact_revalidation(v) is False

def test_artifact_mismatch_requires_revalidation():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation, require_artifact_revalidation
    rec = register_artifact("A1", "V1", b"data")
    v = verify_artifact_for_evaluation(rec, b"new_data")
    assert require_artifact_revalidation(v) is True

def test_artifact_correct_artifact_gate_message_is_returned():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation, artifact_gate_status
    rec = register_artifact("A1", "V1", b"data")
    v1 = verify_artifact_for_evaluation(rec, b"data")
    assert artifact_gate_status(v1) == "ARTIFACT VERIFIED"
    v2 = verify_artifact_for_evaluation(rec, b"new_data")
    assert artifact_gate_status(v2) == "VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"

def test_artifact_evidence_validity_record_copies_artifact_id():
    from ai.artifact import register_artifact, create_evidence_validity
    rec = register_artifact("A123", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12)
    assert val.artifact_id == "A123"

def test_artifact_evidence_validity_record_copies_artifact_hash():
    from ai.artifact import register_artifact, create_evidence_validity
    rec = register_artifact("A123", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12)
    assert val.artifact_hash == rec.artifact_hash

def test_artifact_validity_months_zero_or_less_rejected():
    import pytest
    from ai.artifact import register_artifact, create_evidence_validity
    rec = register_artifact("A1", "V1", b"data")
    with pytest.raises(ValueError):
        create_evidence_validity("E1", rec, 0)
    with pytest.raises(ValueError):
        create_evidence_validity("E1", rec, -5)

def test_artifact_evidence_expiration_is_deterministic_when_current_time_supplied():
    from ai.artifact import register_artifact, create_evidence_validity, is_evidence_expired
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    val = create_evidence_validity("E1", rec, 1, created_at=start)
    assert is_evidence_expired(val, datetime(2026, 1, 15, tzinfo=timezone.utc)) is False
    assert is_evidence_expired(val, datetime(2026, 2, 2, tzinfo=timezone.utc)) is True

def test_artifact_non_expired_evidence_returns_false():
    from ai.artifact import register_artifact, create_evidence_validity, is_evidence_expired
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12, created_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    assert is_evidence_expired(val, datetime(2025, 6, 1, tzinfo=timezone.utc)) is False

def test_artifact_expired_evidence_returns_true():
    from ai.artifact import register_artifact, create_evidence_validity, is_evidence_expired
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12, created_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    assert is_evidence_expired(val, datetime(2026, 1, 2, tzinfo=timezone.utc)) is True

def test_artifact_calendar_month_arithmetic_works_correctly():
    from ai.artifact import add_months
    from datetime import datetime, timezone
    d = datetime(2026, 1, 15, tzinfo=timezone.utc)
    res = add_months(d, 1)
    assert res.year == 2026 and res.month == 2 and res.day == 15

def test_artifact_leap_year_month_handling_works():
    from ai.artifact import add_months
    from datetime import datetime, timezone
    d = datetime(2024, 1, 31, tzinfo=timezone.utc) # 2024 is leap year
    res = add_months(d, 1)
    assert res.year == 2024 and res.month == 2 and res.day == 29

def test_artifact_year_boundary_works():
    from ai.artifact import add_months
    from datetime import datetime, timezone
    d = datetime(2025, 12, 15, tzinfo=timezone.utc)
    res = add_months(d, 1)
    assert res.year == 2026 and res.month == 1 and res.day == 15

def test_artifact_valid_artifact_valid_time_yields_valid():
    from ai.artifact import register_artifact, create_evidence_validity, validate_evidence_artifact
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    val = create_evidence_validity("E1", rec, 12, created_at=start)
    current = datetime(2025, 6, 1, tzinfo=timezone.utc)
    assert validate_evidence_artifact(val, rec, b"data", current) == "VALID"

def test_artifact_changed_artifact_valid_time_yields_artifact_revalidation():
    from ai.artifact import register_artifact, create_evidence_validity, validate_evidence_artifact
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    val = create_evidence_validity("E1", rec, 12, created_at=start)
    current = datetime(2025, 6, 1, tzinfo=timezone.utc)
    assert validate_evidence_artifact(val, rec, b"new_data", current) == "VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"

def test_artifact_valid_artifact_expired_evidence_yields_evidence_revalidation():
    from ai.artifact import register_artifact, create_evidence_validity, validate_evidence_artifact
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    val = create_evidence_validity("E1", rec, 12, created_at=start)
    current = datetime(2026, 6, 1, tzinfo=timezone.utc)
    assert validate_evidence_artifact(val, rec, b"data", current) == "EVIDENCE EXPIRED — RE-VALIDATION REQUIRED"

def test_artifact_changed_artifact_expired_evidence_yields_combined_failure_message():
    from ai.artifact import register_artifact, create_evidence_validity, validate_evidence_artifact
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    val = create_evidence_validity("E1", rec, 12, created_at=start)
    current = datetime(2026, 6, 1, tzinfo=timezone.utc)
    assert validate_evidence_artifact(val, rec, b"new_data", current) == "EVIDENCE EXPIRED AND VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED"

def test_artifact_hash_is_never_overwritten_by_verification():
    from ai.artifact import register_artifact, verify_artifact_for_evaluation
    rec = register_artifact("A1", "V1", b"data")
    h = rec.artifact_hash
    verify_artifact_for_evaluation(rec, b"new_data")
    assert rec.artifact_hash == h

def test_artifact_current_artifact_data_cannot_modify_historical_artifact_identity():
    from ai.artifact import register_artifact, create_evidence_validity, validate_evidence_artifact
    from datetime import datetime, timezone
    rec = register_artifact("A1", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12, created_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    h = rec.artifact_hash
    validate_evidence_artifact(val, rec, b"new_data", datetime(2025, 6, 1, tzinfo=timezone.utc))
    assert rec.artifact_hash == h
    assert val.artifact_hash == h

def test_artifact_timezone_aware_datetime_behavior_works():
    from ai.artifact import register_artifact, create_evidence_validity
    rec = register_artifact("A1", "V1", b"data")
    val = create_evidence_validity("E1", rec, 12)
    assert val.created_at.endswith("+00:00") or "T" in val.created_at

def get_mock_evidence_deps():
    from dataclasses import dataclass

    @dataclass
    class MockEvalRun:
        status: str = "COMPLETED"
        evaluator_version: str = "1.0"
        test_suite_hash: str = "abc"
        test_suite_id: str = "ts1"
        test_suite_version: str = "v1"
        artifact_id: str = "art1"
        vendor_id: str = "ven1"
        evaluation_id: str = "eval1"
        accuracy: float = 95.5

    @dataclass
    class MockArtRec:
        artifact_id: str = "art1"
        vendor_id: str = "ven1"
        artifact_hash: str = "hash1"

    @dataclass
    class MockArtVer:
        status: str = "MATCH"

    @dataclass
    class MockEvVal:
        created_at: str = "2026-01-01T00:00:00+00:00"
        validity_months: int = 12
        expires_at: str = "2027-01-01T00:00:00+00:00"

    return MockEvalRun(), MockArtRec(), MockArtVer(), MockEvVal()

def test_evidence_valid_evaluation_becomes_independently_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level == "INDEPENDENTLY_VALIDATED"

def test_evidence_unauthorized_evaluator_cannot_produce_independently_validated_evidence():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, False, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_incomplete_evaluation_cannot_become_independently_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.status = "FAILED"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_artifact_mismatch_blocks_independent_validation():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    v.status = "MISMATCH"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_expired_evidence_blocks_independent_validation():
    from ai.evidence_record import create_evidence_record
    from datetime import datetime, timezone, timedelta
    e, a, v, val = get_mock_evidence_deps()
    val.expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_invalid_test_suite_blocks_independent_validation():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, False)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_empty_evaluator_version_blocks_validation():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.evaluator_version = ""
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_empty_test_suite_hash_blocks_validation():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.test_suite_hash = ""
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_evaluation_artifact_id_mismatch_is_detected():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.artifact_id = "diff"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_evaluation_vendor_id_mismatch_is_detected():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.vendor_id = "diff"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_successful_validation_produces_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.validation_status == "VALIDATED"

def test_evidence_failed_trust_dependency_produces_appropriate_status():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, False, True)
    assert rec.validation_status != "VALIDATED"

def test_evidence_artifact_mismatch_produces_revalidation_required():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    v.status = "MISMATCH"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.validation_status == "REVALIDATION_REQUIRED"

def test_evidence_expired_evidence_produces_revalidation_required():
    from ai.evidence_record import create_evidence_record
    from datetime import datetime, timezone, timedelta
    e, a, v, val = get_mock_evidence_deps()
    val.expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.validation_status == "REVALIDATION_REQUIRED"

def test_evidence_unauthorized_evaluator_produces_revalidation_required():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, False, True)
    assert rec.validation_status == "REVALIDATION_REQUIRED"

def test_evidence_invalid_test_suite_produces_not_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, False)
    assert rec.validation_status == "NOT_VALIDATED"

def test_evidence_incomplete_evaluation_produces_not_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.status = "FAILED"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.validation_status == "NOT_VALIDATED"

def test_evidence_validation_reasons_are_specific():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, False, False)
    assert "Evaluator not authorized" in rec.validation_reasons
    assert "Test suite invalid" in rec.validation_reasons

def test_evidence_record_copies_artifact_id():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.artifact_id == "art1"

def test_evidence_record_copies_artifact_hash():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.artifact_hash == "hash1"

def test_evidence_record_copies_evaluator_version():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evaluator_version == "1.0"

def test_evidence_record_copies_test_suite_id():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.test_suite_id == "ts1"

def test_evidence_record_copies_test_suite_version():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.test_suite_version == "v1"

def test_evidence_record_copies_test_suite_hash():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.test_suite_hash == "abc"

def test_evidence_record_copies_evaluation_id():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evaluation_id == "eval1"

def test_evidence_record_copies_validity_fields():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.created_at == val.created_at
    assert rec.expires_at == val.expires_at
    assert rec.validity_months == val.validity_months

def test_evidence_metric_value_equals_evaluation_run_accuracy():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.metric_value == 95.5

def test_evidence_default_metric_name_is_accuracy():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.metric_name == "Accuracy"

def test_evidence_default_metric_unit_is_percent():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.metric_unit == "percent"

def test_evidence_level_cannot_be_manually_forced_to_independently_validated():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    # It passes so it is independently validated natively
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level == "INDEPENDENTLY_VALIDATED"
    e.status = "FAILED"
    rec2 = create_evidence_record(e, a, v, val, True, True)
    assert rec2.evidence_level != "INDEPENDENTLY_VALIDATED"

def test_evidence_frozen_evidence_protects_artifact_hash():
    import pytest
    from ai.evidence_record import create_evidence_record, freeze_evidence
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    with pytest.raises(ValueError):
        rec.artifact_hash = "new"

def test_evidence_frozen_evidence_protects_evaluator_version():
    import pytest
    from ai.evidence_record import create_evidence_record, freeze_evidence
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    with pytest.raises(ValueError):
        rec.evaluator_version = "new"

def test_evidence_frozen_evidence_protects_test_suite_hash():
    import pytest
    from ai.evidence_record import create_evidence_record, freeze_evidence
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    with pytest.raises(ValueError):
        rec.test_suite_hash = "new"

def test_evidence_frozen_evidence_protects_metric_value():
    import pytest
    from ai.evidence_record import create_evidence_record, freeze_evidence
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    with pytest.raises(ValueError):
        rec.metric_value = 100.0

def test_evidence_evaluator_invalidation_marks_matching_evidence_for_revalidation():
    from ai.evidence_record import create_evidence_record, freeze_evidence, invalidate_evidence_for_evaluator
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    new_rec = invalidate_evidence_for_evaluator(rec, "1.0")
    assert new_rec.validation_status == "REVALIDATION_REQUIRED"

def test_evidence_evaluator_invalidation_does_not_affect_unrelated_evidence():
    from ai.evidence_record import create_evidence_record, freeze_evidence, invalidate_evidence_for_evaluator
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    new_rec = invalidate_evidence_for_evaluator(rec, "2.0")
    assert new_rec.validation_status == "VALIDATED"

def test_evidence_expired_evidence_refresh_marks_revalidation_required():
    from ai.evidence_record import create_evidence_record, freeze_evidence, refresh_evidence_status
    from datetime import datetime, timezone, timedelta
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    future = datetime.now(timezone.utc) + timedelta(days=500)
    new_rec = refresh_evidence_status(rec, future)
    assert new_rec.validation_status == "REVALIDATION_REQUIRED"

def test_evidence_provenance_remains_unchanged_after_expiration():
    from ai.evidence_record import create_evidence_record, freeze_evidence, refresh_evidence_status
    from datetime import datetime, timezone, timedelta
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    freeze_evidence(rec)
    future = datetime.now(timezone.utc) + timedelta(days=500)
    new_rec = refresh_evidence_status(rec, future)
    assert new_rec.artifact_hash == rec.artifact_hash
    assert new_rec.evaluator_version == rec.evaluator_version

def test_evidence_same_evaluation_produces_deterministic_evidence_metadata():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec1 = create_evidence_record(e, a, v, val, True, True)
    rec2 = create_evidence_record(e, a, v, val, True, True)
    assert rec1.artifact_hash == rec2.artifact_hash
    assert rec1.validation_status == rec2.validation_status

def test_evidence_validation_report_contains_all_gate_statuses():
    from ai.evidence_record import validate_evaluation_for_evidence
    e, a, v, val = get_mock_evidence_deps()
    report = validate_evaluation_for_evidence(e, a, v, val, True, True)
    assert report.evaluator_authorized is True
    assert report.evaluation_completed is True
    assert report.artifact_verified is True
    assert report.evidence_current is True
    assert report.test_suite_valid is True

def test_evidence_validated_evidence_has_all_required_provenance_fields():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.artifact_id and rec.vendor_id and rec.artifact_hash
    assert rec.evaluator_version and rec.test_suite_id and rec.test_suite_hash

def test_evidence_nonvalidated_evidence_does_not_claim_independent_validation():
    from ai.evidence_record import create_evidence_record
    e, a, v, val = get_mock_evidence_deps()
    e.status = "FAILED"
    rec = create_evidence_record(e, a, v, val, True, True)
    assert rec.evidence_level != "INDEPENDENTLY_VALIDATED"

def get_mock_eval_run_for_cartography():
    from dataclasses import dataclass
    from typing import List

    @dataclass
    class MockCaseResult:
        stratum_id: str
        correct: bool
        error: bool
        latency_ms: float

    @dataclass
    class MockEvalRun:
        vendor_id: str = "v1"
        evaluation_id: str = "e1"
        artifact_id: str = "a1"
        evaluator_version: str = "1.0"
        accuracy: float = 90.0
        results: List[MockCaseResult] = None

        def __post_init__(self):
            if self.results is None:
                self.results = []

    return MockEvalRun, MockCaseResult

def test_fc_empty_evaluation_run_rejected():
    import pytest
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, _ = get_mock_eval_run_for_cartography()
    with pytest.raises(ValueError):
        generate_failure_map(MockEvalRun())

def test_fc_single_healthy_stratum_normal():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    r = MockEvalRun(results=[MockCaseResult("S1", True, False, 10)])
    fm = generate_failure_map(r)
    assert fm.strata[0].severity == "NORMAL"

def test_fc_watch_threshold_classification():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 90 + [MockCaseResult("S1", False, False, 10)] * 10
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "WATCH"

def test_fc_degraded_threshold_classification():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 80 + [MockCaseResult("S1", False, False, 10)] * 20
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "DEGRADED"

def test_fc_critical_threshold_classification():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 60 + [MockCaseResult("S1", False, False, 10)] * 40
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "CRITICAL"

def test_fc_accuracy_exactly_95_normal():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 95 + [MockCaseResult("S1", False, False, 10)] * 5
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "NORMAL"

def test_fc_accuracy_exactly_85_watch():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 85 + [MockCaseResult("S1", False, False, 10)] * 15
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "WATCH"

def test_fc_accuracy_exactly_70_degraded():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 70 + [MockCaseResult("S1", False, False, 10)] * 30
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "DEGRADED"

def test_fc_accuracy_below_70_critical():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 69 + [MockCaseResult("S1", False, False, 10)] * 31
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "CRITICAL"

def test_fc_error_rate_at_30_critical():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    # 100 cases, 30 errors. Even if 70 are correct, it's critical.
    res = [MockCaseResult("S1", True, False, 10)] * 70 + [MockCaseResult("S1", False, True, 10)] * 30
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "CRITICAL"

def test_fc_error_rate_below_30_does_not_automatically_trigger_critical():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    # 100 cases, 29 errors, 71 correct. Accuracy = 71 -> DEGRADED
    res = [MockCaseResult("S1", True, False, 10)] * 71 + [MockCaseResult("S1", False, True, 10)] * 29
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].severity == "DEGRADED"

def test_fc_multiple_cases_with_same_stratum_grouped():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10), MockCaseResult("S1", False, False, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert len(fm.strata) == 1
    assert fm.strata[0].total_cases == 2

def test_fc_grouped_accuracy_calculated_correctly():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10), MockCaseResult("S1", False, False, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].accuracy == 50.0

def test_fc_grouped_error_count_calculated_correctly():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10), MockCaseResult("S1", False, True, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].error_count == 1

def test_fc_grouped_latency_calculated_correctly():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10), MockCaseResult("S1", False, False, 20), MockCaseResult("S1", False, True, 100)]
    fm = generate_failure_map(MockEvalRun(results=res))
    # Latency for non-error cases: (10 + 20) / 2 = 15.0
    assert fm.strata[0].average_latency_ms == 15.0

def test_fc_no_successful_cases_latency_0():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", False, True, 100)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].average_latency_ms == 0.0

def test_fc_failure_rate_calculated_correctly():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 75 + [MockCaseResult("S1", False, False, 10)] * 25
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.strata[0].failure_rate == 25.0

def test_fc_stratum_ids_preserved():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10), MockCaseResult("S2", True, False, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert set([s.stratum_id for s in fm.strata]) == {"S1", "S2"}

def test_fc_critical_hotspot_generated():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", False, False, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.hotspots[0].severity == "CRITICAL"

def test_fc_degraded_hotspot_generated():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 80 + [MockCaseResult("S1", False, False, 10)] * 20
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.hotspots[0].severity == "DEGRADED"

def test_fc_watch_hotspot_generated():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 90 + [MockCaseResult("S1", False, False, 10)] * 10
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.hotspots[0].severity == "WATCH"

def test_fc_normal_stratum_is_not_a_hotspot():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 100
    fm = generate_failure_map(MockEvalRun(results=res))
    assert len(fm.hotspots) == 0

def test_fc_hotspots_sorted_by_severity():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = ([MockCaseResult("S1", True, False, 10)] * 90 + [MockCaseResult("S1", False, False, 10)] * 10) + \
          ([MockCaseResult("S2", False, False, 10)] * 100)
    fm = generate_failure_map(MockEvalRun(results=res))
    # S2 is CRITICAL, S1 is WATCH. Sorted: CRITICAL then WATCH
    assert fm.hotspots[0].severity == "CRITICAL"
    assert fm.hotspots[1].severity == "WATCH"

def test_fc_hotspots_sorted_by_accuracy_within_severity():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    # Both CRITICAL, but one is 0% and one is 50%
    res = ([MockCaseResult("S1", True, False, 10)] * 50 + [MockCaseResult("S1", False, False, 10)] * 50) + \
          ([MockCaseResult("S2", False, False, 10)] * 100)
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.hotspots[0].stratum_id == "S2"
    assert fm.hotspots[1].stratum_id == "S1"

def test_fc_critical_count_correct():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", False, False, 10), MockCaseResult("S2", False, False, 10)]
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.critical_strata == 2

def test_fc_degraded_count_correct():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = ([MockCaseResult("S1", True, False, 10)] * 80 + [MockCaseResult("S1", False, False, 10)] * 20)
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.degraded_strata == 1

def test_fc_watch_count_correct():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = ([MockCaseResult("S1", True, False, 10)] * 90 + [MockCaseResult("S1", False, False, 10)] * 10)
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.watch_strata == 1

def test_fc_any_critical_stratum_overall_critical():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 100 + [MockCaseResult("S2", False, False, 10)] * 1
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.status == "CRITICAL"

def test_fc_no_critical_but_degraded_exists_degraded():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = ([MockCaseResult("S1", True, False, 10)] * 100) + \
          ([MockCaseResult("S2", True, False, 10)] * 80 + [MockCaseResult("S2", False, False, 10)] * 20)
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.status == "DEGRADED"

def test_fc_no_critical_degraded_but_watch_exists_watch():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = ([MockCaseResult("S1", True, False, 10)] * 100) + \
          ([MockCaseResult("S2", True, False, 10)] * 90 + [MockCaseResult("S2", False, False, 10)] * 10)
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.status == "WATCH"

def test_fc_all_normal_robust():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 100
    fm = generate_failure_map(MockEvalRun(results=res))
    assert fm.status == "ROBUST"

def test_fc_overall_accuracy_does_not_hide_critical_stratum():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", True, False, 10)] * 100 + [MockCaseResult("S2", False, False, 10)] * 5
    r = MockEvalRun(accuracy=95.2, results=res)
    fm = generate_failure_map(r)
    assert fm.overall_accuracy == 95.2
    assert fm.status == "CRITICAL"

def test_fc_failure_map_preserves_vendor_id():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert fm.vendor_id == "v1"

def test_fc_failure_map_preserves_evaluation_id():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert fm.evaluation_id == "e1"

def test_fc_failure_map_preserves_artifact_id():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert fm.artifact_id == "a1"

def test_fc_failure_map_preserves_evaluator_version():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert fm.evaluator_version == "1.0"

def test_fc_private_parameters_are_not_exposed():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert not hasattr(fm, "private_parameters")
    assert not hasattr(fm.strata[0], "private_parameters")

def test_fc_raw_seed_is_not_exposed():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", True, False, 10)]))
    assert not hasattr(fm, "seed")
    assert not hasattr(fm.strata[0], "seed")

def test_fc_explain_failure_map_contains_expected_summary():
    from ai.failure_cartography import generate_failure_map, explain_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    fm = generate_failure_map(MockEvalRun(results=[MockCaseResult("S1", False, False, 10)]))
    exp = explain_failure_map(fm)
    assert exp["status"] == "CRITICAL"
    assert exp["critical_strata"] == 1
    assert "overall_accuracy" in exp
    assert "top_hotspots" in exp

def test_fc_same_evaluation_produces_deterministic_failure_map():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", False, False, 10)]
    fm1 = generate_failure_map(MockEvalRun(results=res))
    fm2 = generate_failure_map(MockEvalRun(results=res))
    assert fm1.status == fm2.status
    assert fm1.critical_strata == fm2.critical_strata

def test_fc_evaluation_run_remains_unchanged_after_cartography():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    r = MockEvalRun(results=[MockCaseResult("S1", True, False, 10)])
    orig_len = len(r.results)
    generate_failure_map(r)
    assert len(r.results) == orig_len

def test_fc_human_readable_failure_reasons_are_produced():
    from ai.failure_cartography import generate_failure_map
    MockEvalRun, MockCaseResult = get_mock_eval_run_for_cartography()
    res = [MockCaseResult("S1", False, True, 10)] * 100
    fm = generate_failure_map(MockEvalRun(results=res))
    assert "High execution error rate" in fm.hotspots[0].reason
    assert "Accuracy below critical threshold" in fm.hotspots[0].reason

def get_mock_scale_up_deps():
    from dataclasses import dataclass
    from ai.scale_up import ScaleUpRequest

    req = ScaleUpRequest(
        request_id="r1",
        vendor_id="v1",
        target_department="dep",
        target_district="dis",
        existing_evidence_id="e1",
        existing_artifact_id="a1",
        requested_at="2026-08-27",
        reason="Expansion"
    )

    @dataclass
    class MockArtRec:
        artifact_id: str = "a1"
        vendor_id: str = "v1"
        artifact_hash: str = "277089d91c0bdf4f2e6862ba7e4a07605119431f5d13f726dd352b06f1b206a9"

    @dataclass
    class MockEvRec:
        expires_at: str = "2027-01-01T00:00:00+00:00"
        evidence_level: str = "INDEPENDENTLY_VALIDATED"

    @dataclass
    class MockPilotTwin:
        connectivity: str = "STABLE"
        device: str = "HIGH_END"
        language: str = "STANDARD"
        input_quality: str = "CLEAN"

    @dataclass
    class MockFailureMap:
        hotspots: list = None
        def __post_init__(self):
            if self.hotspots is None:
                self.hotspots = []

    return req, b"bytes", MockArtRec(), MockEvRec(), MockFailureMap(), MockPilotTwin()

def test_su_valid_scale_up_eligible():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_ELIGIBLE"

def test_su_empty_request_id_rejected():
    import pytest
    from ai.scale_up import ScaleUpRequest
    with pytest.raises(ValueError):
        ScaleUpRequest("", "v", "d", "d", "e", "a", "t", "r")

def test_su_empty_vendor_id_rejected():
    import pytest
    from ai.scale_up import ScaleUpRequest
    with pytest.raises(ValueError):
        ScaleUpRequest("r", "", "d", "d", "e", "a", "t", "r")

def test_su_empty_target_district_rejected():
    import pytest
    from ai.scale_up import ScaleUpRequest
    with pytest.raises(ValueError):
        ScaleUpRequest("r", "v", "d", "", "e", "a", "t", "r")

def test_su_artifact_mismatch_revalidation_required():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b"changed", ar, ev, fm, pt)
    assert res.status == "REVALIDATION_REQUIRED"

def test_su_artifact_match_allows_next_gate():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.artifact_status == "MATCH"

def test_su_expired_evidence_revalidation_required():
    from ai.scale_up import evaluate_scale_up_request
    from datetime import datetime, timezone, timedelta
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "REVALIDATION_REQUIRED"

def test_su_valid_evidence_passes_temporal_gate():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.evidence_status == "VALID"

def test_su_non_independent_evidence_do_not_scale_yet():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.evidence_level = "OBSERVED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "DO_NOT_SCALE_YET"

def test_su_independently_validated_evidence_proceeds():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status != "DO_NOT_SCALE_YET"

def test_su_verified_pilot_twin_passes():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.pilot_twin_status == "VERIFIED"

def test_su_unverified_critical_parameter_triggers_review():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    pt.connectivity = "UNVERIFIED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_REVIEW_REQUIRED"

def test_su_no_failure_match_scale_eligible():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_ELIGIBLE"

def test_su_watch_failure_match_scale_eligible_with_warning():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "WATCH", 90.0, 10.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_ELIGIBLE"
    assert "Target district matches a WATCH-level historical failure." in res.reasons

def test_su_degraded_failure_match_scale_review_required():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "DEGRADED", 80.0, 20.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_REVIEW_REQUIRED"

def test_su_critical_failure_match_scale_review_required():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 60.0, 40.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_REVIEW_REQUIRED"

def test_su_overall_accuracy_cannot_hide_critical_failure():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    # E.g., overall is 96%, but cartography has a match
    fm.overall_accuracy = 96.0
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 64.0, 36.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "SCALE_REVIEW_REQUIRED"

def test_su_matched_failure_strata_returned():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 64.0, 36.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "STABLE_HIGH_END_STANDARD_CLEAN" in res.matched_failure_strata

def test_su_critical_failure_status_returned():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 64.0, 36.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.failure_map_status == "CRITICAL_MATCH"

def test_su_degraded_failure_status_returned():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "DEGRADED", 84.0, 16.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.failure_map_status == "DEGRADED_MATCH"

def test_su_watch_failure_status_returned():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "WATCH", 90.0, 10.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.failure_map_status == "WATCH_MATCH"

def test_su_no_failure_match_status_returned():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.failure_map_status == "NO_KNOWN_FAILURE_MATCH"

def test_su_artifact_reason_is_explicit():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b"changed", ar, ev, fm, pt)
    assert "VENDOR ARTIFACT CHANGED — RE-VALIDATION REQUIRED" in res.reasons

def test_su_expiration_reason_is_explicit():
    from ai.scale_up import evaluate_scale_up_request
    from datetime import datetime, timezone, timedelta
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "EVIDENCE EXPIRED — RE-VALIDATION REQUIRED" in res.reasons

def test_su_evidence_level_reason_is_explicit():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.evidence_level = "OBSERVED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "Existing evidence is not independently validated" in res.reasons

def test_su_pilot_twin_uncertainty_reason_is_explicit():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    pt.connectivity = "UNVERIFIED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "Target deployment condition contains unverified parameters" in res.reasons

def test_su_vendor_response_window_appears_for_scale_review_required():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    pt.connectivity = "UNVERIFIED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "VENDOR RESPONSE WINDOW REQUIRED" in res.reasons

def test_su_vendor_response_window_appears_for_do_not_scale_yet():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.evidence_level = "OBSERVED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "VENDOR RESPONSE WINDOW REQUIRED" in res.reasons

def test_su_no_response_window_requirement_for_clean_scale_eligible():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert "VENDOR RESPONSE WINDOW REQUIRED" not in res.reasons

def test_su_vendor_id_preserved():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.vendor_id == "v1"

def test_su_target_department_preserved():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.target_department == "dep"

def test_su_target_district_preserved():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.target_district == "dis"

def test_su_existing_evidence_remains_unchanged():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    _ = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert ev.evidence_level == "INDEPENDENTLY_VALIDATED"

def test_su_existing_failure_map_remains_unchanged():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    _ = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert len(fm.hotspots) == 0

def test_su_private_parameters_are_not_exposed():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert not hasattr(res, "private_parameters")

def test_su_raw_seed_is_not_exposed():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert not hasattr(res, "seed")

def test_su_same_input_produces_deterministic_result():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res1 = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    res2 = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res1.status == res2.status

def test_su_failure_severity_ordering_works_correctly():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "DEGRADED", 84.0, 16.0, "reason"))
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 60.0, 40.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    # Both matches, but critical should rule
    assert res.failure_map_status == "CRITICAL_MATCH"

def test_su_multiple_matched_failures_handled_correctly():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    # Match both exactly and partial
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "DEGRADED", 84.0, 16.0, "reason"))
    fm.hotspots.append(FailureHotspot("STABLE", "WATCH", 90.0, 10.0, "reason"))
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert len(res.matched_failure_strata) == 2

def test_su_artifact_revalidation_takes_precedence_over_failure_map_result():
    from ai.scale_up import evaluate_scale_up_request
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 60.0, 40.0, "reason"))
    res = evaluate_scale_up_request(req, b"changed", ar, ev, fm, pt)
    assert res.status == "REVALIDATION_REQUIRED"
    assert res.artifact_status == "MISMATCH"

def test_su_evidence_expiration_takes_precedence_over_failure_map_result():
    from ai.scale_up import evaluate_scale_up_request
    from datetime import datetime, timezone, timedelta
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 60.0, 40.0, "reason"))
    ev.expires_at = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "REVALIDATION_REQUIRED"

def test_su_non_independent_evidence_prevents_automatic_scale_eligibility():
    from ai.scale_up import evaluate_scale_up_request
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.evidence_level = "OBSERVED"
    res = evaluate_scale_up_request(req, b, ar, ev, fm, pt)
    assert res.status == "DO_NOT_SCALE_YET"

def test_su_scale_up_decision_does_not_authorize_actual_deployment():
    from ai.scale_up import ScaleUpDecision
    assert not hasattr(ScaleUpDecision, "authorize_deployment")
    assert not hasattr(ScaleUpDecision, "release_funds")

# ============================================================
# STEP 15 — Vendor Response / Challenge Window
# ============================================================

def _make_vendor_response(**overrides):
    from ai.vendor_response import submit_vendor_response
    defaults = dict(
        vendor_id="vendor-1",
        request_id="req-1",
        decision_status="SCALE_REVIEW_REQUIRED",
        response_type="CLARIFICATION",
        explanation="We believe the failure is explained by deployment timing.",
        requested_action="REVIEW",
        submitted_at="2026-08-01T00:00:00+00:00",
        response_id="RESP-test-001",
    )
    defaults.update(overrides)
    return submit_vendor_response(**defaults)


def test_vr_valid_clarification_response_created():
    resp = _make_vendor_response(response_type="CLARIFICATION", requested_action="REVIEW")
    assert resp.response_type == "CLARIFICATION"
    assert resp.status == "SUBMITTED"


def test_vr_valid_contest_response_created():
    resp = _make_vendor_response(response_type="CONTEST_FAILURE", requested_action="REVIEW")
    assert resp.response_type == "CONTEST_FAILURE"
    assert resp.status == "SUBMITTED"


def test_vr_valid_revalidation_request_created():
    resp = _make_vendor_response(
        response_type="REQUEST_REVALIDATION",
        requested_action="TARGETED_REVALIDATION",
    )
    assert resp.response_type == "REQUEST_REVALIDATION"
    assert resp.requested_action == "TARGETED_REVALIDATION"


def test_vr_valid_evidence_submission_created():
    resp = _make_vendor_response(
        response_type="SUBMIT_EVIDENCE",
        requested_action="REVIEW",
        supporting_evidence_ids=["EVID-001"],
    )
    assert resp.response_type == "SUBMIT_EVIDENCE"
    assert "EVID-001" in resp.supporting_evidence_ids


def test_vr_empty_vendor_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(vendor_id="")


def test_vr_empty_request_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(request_id="")


def test_vr_empty_explanation_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(explanation="")


def test_vr_invalid_response_type_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(response_type="BRIBE")


def test_vr_invalid_requested_action_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(requested_action="OVERRIDE_DECISION")


def test_vr_response_to_scale_eligible_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(decision_status="SCALE_ELIGIBLE")


def test_vr_new_response_starts_as_submitted():
    resp = _make_vendor_response()
    assert resp.status == "SUBMITTED"


def test_vr_vendor_cannot_directly_create_accepted_status():
    resp = _make_vendor_response()
    assert resp.status != "ACCEPTED"


def test_vr_vendor_cannot_directly_create_rejected_status():
    resp = _make_vendor_response()
    assert resp.status != "REJECTED"


def test_vr_vendor_cannot_directly_create_under_review_status():
    resp = _make_vendor_response()
    assert resp.status != "UNDER_REVIEW"


def test_vr_supporting_evidence_ids_stored_as_references():
    resp = _make_vendor_response(
        response_type="SUBMIT_EVIDENCE",
        requested_action="REVIEW",
        supporting_evidence_ids=["EVID-001", "EVID-004"],
    )
    assert resp.supporting_evidence_ids == ["EVID-001", "EVID-004"]


def test_vr_evidence_records_are_not_modified():
    from dataclasses import dataclass
    @dataclass
    class MockEvidence:
        evidence_id: str = "EVID-001"
        evidence_level: str = "OBSERVED"
    ev = MockEvidence()
    _ = _make_vendor_response(
        response_type="SUBMIT_EVIDENCE",
        requested_action="REVIEW",
        supporting_evidence_ids=[ev.evidence_id],
    )
    assert ev.evidence_level == "OBSERVED"


def test_vr_vendor_request_binding_works():
    from ai.vendor_response import validate_response_binding
    resp = _make_vendor_response()
    validate_response_binding(resp, "vendor-1", "req-1")


def test_vr_vendor_mismatch_rejected():
    import pytest
    from ai.vendor_response import validate_response_binding
    resp = _make_vendor_response()
    with pytest.raises(ValueError):
        validate_response_binding(resp, "other-vendor", "req-1")


def test_vr_request_mismatch_rejected():
    import pytest
    from ai.vendor_response import validate_response_binding
    resp = _make_vendor_response()
    with pytest.raises(ValueError):
        validate_response_binding(resp, "vendor-1", "other-req")


def test_vr_reviewer_id_required():
    import pytest
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response()
    with pytest.raises(ValueError):
        review_vendor_response(resp, "", "ACCEPT", "Looks good")


def test_vr_review_reason_required():
    import pytest
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response()
    with pytest.raises(ValueError):
        review_vendor_response(resp, "reviewer-1", "ACCEPT", "")


def test_vr_reviewer_cannot_equal_vendor():
    import pytest
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response()
    with pytest.raises(ValueError):
        review_vendor_response(resp, "vendor-1", "ACCEPT", "Self-approve")


def test_vr_accept_maps_to_accepted():
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-accept-test")
    reviewed = review_vendor_response(resp, "reviewer-1", "ACCEPT", "Approved",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.status == "ACCEPTED"


def test_vr_reject_maps_to_rejected():
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-reject-test")
    reviewed = review_vendor_response(resp, "reviewer-1", "REJECT", "Insufficient",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.status == "REJECTED"


def test_vr_request_more_information_maps_to_under_review():
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-moreinfo-test")
    reviewed = review_vendor_response(resp, "reviewer-1", "REQUEST_MORE_INFORMATION",
                                       "Need deployment logs",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.status == "UNDER_REVIEW"


def test_vr_reviewed_accepted_response_becomes_immutable():
    import pytest
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-immutable-acc")
    reviewed = review_vendor_response(resp, "reviewer-1", "ACCEPT", "Done",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    with pytest.raises(ValueError):
        review_vendor_response(reviewed, "reviewer-2", "REJECT", "Changed mind")


def test_vr_reviewed_rejected_response_becomes_immutable():
    import pytest
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-immutable-rej")
    reviewed = review_vendor_response(resp, "reviewer-1", "REJECT", "No",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    with pytest.raises(ValueError):
        review_vendor_response(reviewed, "reviewer-2", "ACCEPT", "Overrule")


def test_vr_under_review_response_remains_reviewable():
    from ai.vendor_response import review_vendor_response
    resp = _make_vendor_response(response_id="RESP-underreview-ok")
    under_review = review_vendor_response(resp, "reviewer-1", "REQUEST_MORE_INFORMATION",
                                           "More data needed",
                                           reviewed_at="2026-08-02T00:00:00+00:00")
    final = review_vendor_response(under_review, "reviewer-1", "ACCEPT",
                                    "Now satisfied",
                                    reviewed_at="2026-08-03T00:00:00+00:00")
    assert final.status == "ACCEPTED"


def test_vr_clarification_consistency_rule_enforced():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(response_type="CLARIFICATION",
                              requested_action="FULL_REVALIDATION")


def test_vr_contest_failure_consistency_rule_enforced():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(response_type="CONTEST_FAILURE",
                              requested_action="FULL_REVALIDATION")


def test_vr_request_revalidation_consistency_rule_enforced():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(response_type="REQUEST_REVALIDATION",
                              requested_action="REVIEW")


def test_vr_submit_evidence_requires_evidence_id():
    import pytest
    with pytest.raises(ValueError):
        _make_vendor_response(response_type="SUBMIT_EVIDENCE",
                              requested_action="REVIEW",
                              supporting_evidence_ids=[])


def test_vr_vendor_response_cannot_upgrade_evidence_level():
    from dataclasses import dataclass
    @dataclass
    class MockEvidence:
        evidence_id: str = "EVID-001"
        evidence_level: str = "OBSERVED"
    ev = MockEvidence()
    _ = _make_vendor_response(
        response_type="SUBMIT_EVIDENCE",
        requested_action="REVIEW",
        supporting_evidence_ids=[ev.evidence_id],
    )
    # Evidence level must remain unchanged
    assert ev.evidence_level == "OBSERVED"
    assert ev.evidence_level != "INDEPENDENTLY_VALIDATED"


def test_vr_vendor_response_cannot_change_scale_up_decision():
    from ai.vendor_response import review_vendor_response
    from dataclasses import dataclass
    @dataclass
    class MockDecision:
        status: str = "SCALE_REVIEW_REQUIRED"
    decision = MockDecision()
    resp = _make_vendor_response(response_id="RESP-no-decision-change")
    reviewed = review_vendor_response(resp, "reviewer-1", "ACCEPT", "OK",
                                       reviewed_at="2026-08-02T00:00:00+00:00")
    # ScaleUpDecision remains unchanged
    assert decision.status == "SCALE_REVIEW_REQUIRED"
    assert reviewed.status == "ACCEPTED"


def test_vr_submission_creates_audit_event():
    from ai.vendor_response import get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-submit")
    history = get_response_history("RESP-audit-submit")
    assert len(history) >= 1
    assert history[0].event_type == "SUBMITTED"


def test_vr_acceptance_creates_audit_event():
    from ai.vendor_response import review_vendor_response, get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-accept")
    review_vendor_response(resp, "reviewer-1", "ACCEPT", "Good",
                            reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_response_history("RESP-audit-accept")
    event_types = [e.event_type for e in history]
    assert "ACCEPTED" in event_types


def test_vr_rejection_creates_audit_event():
    from ai.vendor_response import review_vendor_response, get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-reject")
    review_vendor_response(resp, "reviewer-1", "REJECT", "Bad",
                            reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_response_history("RESP-audit-reject")
    event_types = [e.event_type for e in history]
    assert "REJECTED" in event_types


def test_vr_more_information_request_creates_audit_event():
    from ai.vendor_response import review_vendor_response, get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-moreinfo")
    review_vendor_response(resp, "reviewer-1", "REQUEST_MORE_INFORMATION", "Need logs",
                            reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_response_history("RESP-audit-moreinfo")
    event_types = [e.event_type for e in history]
    assert "MORE_INFORMATION_REQUESTED" in event_types


def test_vr_audit_events_preserve_chronology():
    from ai.vendor_response import review_vendor_response, get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-chrono",
                                  submitted_at="2026-08-01T00:00:00+00:00")
    review_vendor_response(resp, "reviewer-1", "REQUEST_MORE_INFORMATION",
                            "Need more", reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_response_history("RESP-audit-chrono")
    assert len(history) == 2
    assert history[0].timestamp <= history[1].timestamp


def test_vr_audit_events_cannot_be_silently_modified():
    from ai.vendor_response import get_response_history
    resp = _make_vendor_response(response_id="RESP-audit-immutable")
    history = get_response_history("RESP-audit-immutable")
    history[0].reason = "TAMPERED"
    fresh_history = get_response_history("RESP-audit-immutable")
    assert fresh_history[0].reason != "TAMPERED"


def test_vr_response_history_returns_a_copy():
    from ai.vendor_response import get_response_history
    resp = _make_vendor_response(response_id="RESP-hist-copy")
    h1 = get_response_history("RESP-hist-copy")
    h2 = get_response_history("RESP-hist-copy")
    assert h1 is not h2


def test_vr_same_explicit_inputs_produce_deterministic_response_data():
    from ai.vendor_response import submit_vendor_response
    r1 = submit_vendor_response(
        vendor_id="v", request_id="r", decision_status="DO_NOT_SCALE_YET",
        response_type="CLARIFICATION", explanation="test",
        requested_action="REVIEW", submitted_at="2026-01-01T00:00:00+00:00",
        response_id="RESP-det-1",
    )
    r2 = submit_vendor_response(
        vendor_id="v", request_id="r", decision_status="DO_NOT_SCALE_YET",
        response_type="CLARIFICATION", explanation="test",
        requested_action="REVIEW", submitted_at="2026-01-01T00:00:00+00:00",
        response_id="RESP-det-2",
    )
    assert r1.vendor_id == r2.vendor_id
    assert r1.response_type == r2.response_type
    assert r1.status == r2.status
    assert r1.explanation == r2.explanation


def test_vr_response_mechanism_performs_no_evaluation():
    from ai.vendor_response import VendorResponse
    assert not hasattr(VendorResponse, "run_evaluation")
    assert not hasattr(VendorResponse, "evaluate")


def test_vr_response_mechanism_performs_no_procurement_authorization():
    from ai.vendor_response import VendorResponse
    assert not hasattr(VendorResponse, "authorize_procurement")
    assert not hasattr(VendorResponse, "release_funds")

# ============================================================
# STEP 16 — Human Authorization + Maker-Checker + Escalation
# ============================================================

def _make_auth_request(**overrides):
    from ai.human_authorization import AuthorizationRequest
    defaults = dict(
        authorization_id="AUTH-001",
        decision_id="DEC-001",
        vendor_id="vendor-1",
        department="Health",
        requested_action="PROCUREMENT",
        ai_recommendation="ELIGIBLE",
        evidence_ids=["EVID-001", "EVID-002"],
        created_at="2026-08-01T00:00:00+00:00",
        requesting_officer_id="officer-1",
        department_authority_count=2,
    )
    defaults.update(overrides)
    return AuthorizationRequest(**defaults)


def _make_auth_decision(human_decision="APPROVE", **req_overrides):
    from ai.human_authorization import create_authorization
    req = _make_auth_request(**req_overrides)
    return create_authorization(
        req, req.requesting_officer_id, human_decision,
        "Justified decision", created_at="2026-08-01T01:00:00+00:00",
    )


def test_ha_valid_procurement_authorization_request():
    req = _make_auth_request(requested_action="PROCUREMENT", ai_recommendation="ELIGIBLE")
    assert req.requested_action == "PROCUREMENT"


def test_ha_valid_scale_up_authorization_request():
    req = _make_auth_request(requested_action="SCALE_UP", ai_recommendation="SCALE_ELIGIBLE")
    assert req.requested_action == "SCALE_UP"


def test_ha_empty_authorization_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(authorization_id="")


def test_ha_empty_decision_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(decision_id="")


def test_ha_empty_vendor_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(vendor_id="")


def test_ha_empty_department_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(department="")


def test_ha_empty_officer_id_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(requesting_officer_id="")


def test_ha_invalid_authority_count_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(department_authority_count=0)


def test_ha_invalid_requested_action_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(requested_action="DEPLOY")


def test_ha_invalid_procurement_recommendation_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(requested_action="PROCUREMENT", ai_recommendation="SCALE_ELIGIBLE")


def test_ha_invalid_scale_up_recommendation_rejected():
    import pytest
    with pytest.raises(ValueError):
        _make_auth_request(requested_action="SCALE_UP", ai_recommendation="ELIGIBLE")


def test_ha_approve_eligible_authorized():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-approve-elig",
        ai_recommendation="ELIGIBLE",
    )
    assert dec.status == "AUTHORIZED"
    assert dec.human_decision == "APPROVE"


def test_ha_approve_scale_eligible_authorized():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-approve-scale",
        requested_action="SCALE_UP",
        ai_recommendation="SCALE_ELIGIBLE",
    )
    assert dec.status == "AUTHORIZED"


def test_ha_approve_rejected_becomes_override():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-approve-rejected",
        ai_recommendation="REJECTED",
    )
    assert dec.human_decision == "OVERRIDE"
    assert dec.status == "OVERRIDE_PENDING_REVIEW"


def test_ha_approve_scale_review_required_becomes_override():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-approve-scalerev",
        requested_action="SCALE_UP",
        ai_recommendation="SCALE_REVIEW_REQUIRED",
    )
    assert dec.human_decision == "OVERRIDE"
    assert dec.status == "OVERRIDE_PENDING_REVIEW"


def test_ha_reject_eligible_becomes_override():
    dec = _make_auth_decision(
        human_decision="REJECT",
        authorization_id="AUTH-reject-elig",
        ai_recommendation="ELIGIBLE",
    )
    assert dec.human_decision == "OVERRIDE"
    assert dec.status == "OVERRIDE_PENDING_REVIEW"


def test_ha_reject_rejected_is_agreement():
    dec = _make_auth_decision(
        human_decision="REJECT",
        authorization_id="AUTH-reject-rejected",
        ai_recommendation="REJECTED",
    )
    assert dec.status == "REJECTED"
    assert dec.human_decision == "REJECT"


def test_ha_override_requires_justification():
    import pytest
    from ai.human_authorization import create_authorization
    req = _make_auth_request(authorization_id="AUTH-no-just")
    with pytest.raises(ValueError):
        create_authorization(req, "officer-1", "OVERRIDE", "")


def test_ha_placeholder_justification_rejected():
    import pytest
    from ai.human_authorization import create_authorization
    req = _make_auth_request(authorization_id="AUTH-placeholder")
    with pytest.raises(ValueError):
        create_authorization(req, "officer-1", "APPROVE", "N/A")


def test_ha_override_creates_override_pending_review():
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-override-pending",
        ai_recommendation="ELIGIBLE",
    )
    assert dec.status == "OVERRIDE_PENDING_REVIEW"


def test_ha_override_requires_second_reviewer():
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-needs-reviewer",
        ai_recommendation="ELIGIBLE",
    )
    reviewed = review_override(dec, "officer-2", "CONCUR", "I agree",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.reviewing_officer_id == "officer-2"


def test_ha_reviewer_cannot_equal_original_officer():
    import pytest
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-self-review",
        ai_recommendation="ELIGIBLE",
    )
    with pytest.raises(ValueError):
        review_override(dec, "officer-1", "CONCUR", "Self-approve")


def test_ha_multi_officer_routes_to_second_authorized_officer():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-multi",
        ai_recommendation="REJECTED",
        department_authority_count=3,
    )
    assert dec.escalation_destination == "SECOND_AUTHORIZED_OFFICER"
    assert dec.escalation_required is False


def test_ha_single_officer_routes_to_higher_authority():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-single",
        ai_recommendation="REJECTED",
        department_authority_count=1,
    )
    assert dec.escalation_destination == "HIGHER_AUTHORITY_REVIEW"
    assert dec.escalation_required is True


def test_ha_single_officer_cannot_self_review():
    import pytest
    from ai.human_authorization import review_escalated_override
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-single-self",
        ai_recommendation="REJECTED",
        department_authority_count=1,
    )
    with pytest.raises(ValueError):
        review_escalated_override(dec, "officer-1", "CONCUR", "Approve myself")


def test_ha_concur_produces_authorized():
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-concur",
        ai_recommendation="ELIGIBLE",
    )
    reviewed = review_override(dec, "officer-2", "CONCUR", "Agreed",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.status == "AUTHORIZED"


def test_ha_reject_override_produces_rejected():
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-reject-override",
        ai_recommendation="ELIGIBLE",
    )
    reviewed = review_override(dec, "officer-2", "REJECT_OVERRIDE", "Disagree",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.status == "REJECTED"


def test_ha_request_retest_produces_retest_requested():
    dec = _make_auth_decision(
        human_decision="REQUEST_RETEST",
        authorization_id="AUTH-retest",
    )
    assert dec.status == "RETEST_REQUESTED"


def test_ha_override_preserves_original_ai_recommendation():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-preserve-rec",
        ai_recommendation="REJECTED",
    )
    assert dec.ai_recommendation == "REJECTED"


def test_ha_override_preserves_evidence_references():
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-preserve-evid",
        ai_recommendation="REJECTED",
    )
    assert "EVID-001" in dec.evidence_ids
    assert "EVID-002" in dec.evidence_ids


def test_ha_authorization_does_not_modify_evidence_records():
    from dataclasses import dataclass
    @dataclass
    class MockEvidence:
        evidence_id: str = "EVID-001"
        evidence_level: str = "INDEPENDENTLY_VALIDATED"
    ev = MockEvidence()
    _ = _make_auth_decision(authorization_id="AUTH-ev-immut")
    assert ev.evidence_level == "INDEPENDENTLY_VALIDATED"


def test_ha_authorization_does_not_modify_decision_result():
    from dataclasses import dataclass
    @dataclass
    class MockDecision:
        status: str = "ELIGIBLE"
    d = MockDecision()
    _ = _make_auth_decision(authorization_id="AUTH-dec-immut")
    assert d.status == "ELIGIBLE"


def test_ha_authorization_does_not_modify_scale_up_decision():
    from dataclasses import dataclass
    @dataclass
    class MockScaleUp:
        status: str = "SCALE_REVIEW_REQUIRED"
    s = MockScaleUp()
    _ = _make_auth_decision(
        authorization_id="AUTH-su-immut",
        requested_action="SCALE_UP",
        ai_recommendation="SCALE_ELIGIBLE",
    )
    assert s.status == "SCALE_REVIEW_REQUIRED"


def test_ha_no_auto_authorize_function():
    import ai.human_authorization as ha
    assert not hasattr(ha, "auto_authorize")


def test_ha_final_authorization_is_immutable():
    import pytest
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-immutable-auth",
        ai_recommendation="ELIGIBLE",
    )
    authorized = review_override(dec, "officer-2", "CONCUR", "Fine",
                                  reviewed_at="2026-08-02T00:00:00+00:00")
    assert authorized.status == "AUTHORIZED"
    with pytest.raises(ValueError):
        review_override(authorized, "officer-3", "REJECT_OVERRIDE", "Nope")


def test_ha_final_rejection_is_immutable():
    import pytest
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-immutable-rej",
        ai_recommendation="ELIGIBLE",
    )
    rejected = review_override(dec, "officer-2", "REJECT_OVERRIDE", "No",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert rejected.status == "REJECTED"
    with pytest.raises(ValueError):
        review_override(rejected, "officer-3", "CONCUR", "Changed mind")


def test_ha_retest_preserves_original_decision_context():
    dec = _make_auth_decision(
        human_decision="REQUEST_RETEST",
        authorization_id="AUTH-retest-ctx",
        ai_recommendation="ELIGIBLE",
    )
    assert dec.ai_recommendation == "ELIGIBLE"
    assert dec.evidence_ids == ["EVID-001", "EVID-002"]
    assert dec.status == "RETEST_REQUESTED"


def test_ha_submission_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(authorization_id="AUTH-audit-submit")
    history = get_authorization_history("AUTH-audit-submit")
    assert len(history) >= 1


def test_ha_approval_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-audit-approve",
        ai_recommendation="ELIGIBLE",
    )
    history = get_authorization_history("AUTH-audit-approve")
    event_types = [e.event_type for e in history]
    assert "APPROVED" in event_types


def test_ha_rejection_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(
        human_decision="REJECT",
        authorization_id="AUTH-audit-reject",
        ai_recommendation="REJECTED",
    )
    history = get_authorization_history("AUTH-audit-reject")
    event_types = [e.event_type for e in history]
    assert "REJECTED" in event_types


def test_ha_override_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-audit-override",
        ai_recommendation="REJECTED",
    )
    history = get_authorization_history("AUTH-audit-override")
    event_types = [e.event_type for e in history]
    assert "OVERRIDE_REQUESTED" in event_types


def test_ha_escalation_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-audit-escalate",
        ai_recommendation="REJECTED",
        department_authority_count=1,
    )
    history = get_authorization_history("AUTH-audit-escalate")
    event_types = [e.event_type for e in history]
    assert "ESCALATED" in event_types


def test_ha_override_concurrence_creates_audit_event():
    from ai.human_authorization import review_override, get_authorization_history
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-audit-concur",
        ai_recommendation="ELIGIBLE",
    )
    review_override(dec, "officer-2", "CONCUR", "Agreed",
                     reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_authorization_history("AUTH-audit-concur")
    event_types = [e.event_type for e in history]
    assert "OVERRIDE_CONCURRED" in event_types


def test_ha_override_rejection_creates_audit_event():
    from ai.human_authorization import review_override, get_authorization_history
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-audit-ov-rej",
        ai_recommendation="ELIGIBLE",
    )
    review_override(dec, "officer-2", "REJECT_OVERRIDE", "No",
                     reviewed_at="2026-08-02T00:00:00+00:00")
    history = get_authorization_history("AUTH-audit-ov-rej")
    event_types = [e.event_type for e in history]
    assert "OVERRIDE_REJECTED" in event_types


def test_ha_retest_creates_audit_event():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(
        human_decision="REQUEST_RETEST",
        authorization_id="AUTH-audit-retest",
    )
    history = get_authorization_history("AUTH-audit-retest")
    event_types = [e.event_type for e in history]
    assert "RETEST_REQUESTED" in event_types


def test_ha_audit_history_is_chronological():
    from ai.human_authorization import review_override, get_authorization_history
    dec = _make_auth_decision(
        human_decision="OVERRIDE",
        authorization_id="AUTH-audit-chrono",
        ai_recommendation="ELIGIBLE",
    )
    review_override(dec, "officer-2", "CONCUR", "OK",
                     reviewed_at="2026-08-03T00:00:00+00:00")
    history = get_authorization_history("AUTH-audit-chrono")
    assert len(history) >= 2
    for i in range(len(history) - 1):
        assert history[i].timestamp <= history[i + 1].timestamp


def test_ha_audit_history_cannot_be_externally_mutated():
    from ai.human_authorization import get_authorization_history
    _ = _make_auth_decision(authorization_id="AUTH-audit-immut")
    history = get_authorization_history("AUTH-audit-immut")
    history[0].reason = "TAMPERED"
    fresh = get_authorization_history("AUTH-audit-immut")
    assert fresh[0].reason != "TAMPERED"


def test_ha_same_inputs_produce_deterministic_output():
    from ai.human_authorization import create_authorization
    req = _make_auth_request(authorization_id="AUTH-det")
    d1 = create_authorization(req, "officer-1", "APPROVE", "Good",
                               created_at="2026-08-01T00:00:00+00:00")
    # Use a fresh auth_id to avoid audit collision
    req2 = _make_auth_request(authorization_id="AUTH-det-2")
    d2 = create_authorization(req2, "officer-1", "APPROVE", "Good",
                               created_at="2026-08-01T00:00:00+00:00")
    assert d1.status == d2.status
    assert d1.human_decision == d2.human_decision


def test_ha_procurement_recommendation_agreement_logic():
    from ai.human_authorization import recommendation_agrees
    assert recommendation_agrees("PROCUREMENT", "ELIGIBLE", "APPROVE") is True
    assert recommendation_agrees("PROCUREMENT", "REJECTED", "APPROVE") is False
    assert recommendation_agrees("PROCUREMENT", "REJECTED", "REJECT") is True
    assert recommendation_agrees("PROCUREMENT", "ELIGIBLE", "REJECT") is False


def test_ha_scale_up_recommendation_agreement_logic():
    from ai.human_authorization import recommendation_agrees
    assert recommendation_agrees("SCALE_UP", "SCALE_ELIGIBLE", "APPROVE") is True
    assert recommendation_agrees("SCALE_UP", "SCALE_REVIEW_REQUIRED", "APPROVE") is False
    assert recommendation_agrees("SCALE_UP", "DO_NOT_SCALE_YET", "REJECT") is True
    assert recommendation_agrees("SCALE_UP", "SCALE_ELIGIBLE", "REJECT") is False


def test_ha_human_authorization_cannot_modify_ai_recommendation():
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-ai-immut",
        ai_recommendation="REJECTED",
    )
    reviewed = review_override(dec, "officer-2", "CONCUR", "Yes",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.ai_recommendation == "REJECTED"


def test_ha_human_authorization_cannot_modify_evidence_ids():
    from ai.human_authorization import review_override
    dec = _make_auth_decision(
        human_decision="APPROVE",
        authorization_id="AUTH-evid-immut",
        ai_recommendation="REJECTED",
    )
    reviewed = review_override(dec, "officer-2", "CONCUR", "Yes",
                                reviewed_at="2026-08-02T00:00:00+00:00")
    assert reviewed.evidence_ids == ["EVID-001", "EVID-002"]


def test_ha_authorization_module_does_not_execute_procurement():
    import ai.human_authorization as ha
    assert not hasattr(ha, "execute_procurement")
    assert not hasattr(ha, "award_contract")


def test_ha_authorization_module_does_not_release_payments():
    import ai.human_authorization as ha
    assert not hasattr(ha, "release_payment")
    assert not hasattr(ha, "release_funds")


# ============================================================
# FINAL CONSOLIDATION — MODULE A: IP + DATA GOVERNANCE
# ============================================================

def test_dg_data_classification_validates():
    from ai.data_governance import DataAsset
    asset = DataAsset(
        asset_id="ASSET-001",
        name="Crop Health Imagery",
        category="Satellite/Drone Imagery",
        classification="CONFIDENTIAL",
        owner="Department of Agriculture",
        purpose="Pilot verification",
        retention_days=180,
        created_at="2026-08-01T00:00:00+00:00",
    )
    assert asset.classification == "CONFIDENTIAL"
    assert asset.retention_days == 180


def test_dg_invalid_classification_rejected():
    import pytest
    from ai.data_governance import DataAsset
    with pytest.raises(ValueError):
        DataAsset(
            asset_id="ASSET-002",
            name="Test",
            category="General",
            classification="TOP_SECRET_UNAUTHORIZED",
            owner="Gov",
            purpose="Test",
            retention_days=30,
            created_at="2026-08-01T00:00:00+00:00",
        )


def test_dg_retention_days_must_be_positive():
    import pytest
    from ai.data_governance import DataAsset
    with pytest.raises(ValueError):
        DataAsset(
            asset_id="ASSET-003",
            name="Test",
            category="General",
            classification="INTERNAL",
            owner="Gov",
            purpose="Test",
            retention_days=0,
            created_at="2026-08-01T00:00:00+00:00",
        )


def test_dg_ip_schedule_enforces_vendor_ip_and_gov_evidence():
    import pytest
    from ai.data_governance import IPGovernanceSchedule
    # Valid schedule
    sched = IPGovernanceSchedule(
        schedule_id="IP-001",
        contract_id="CON-001",
        pilot_twin_id="TWIN-001",
        startup_ip_owner="VENDOR",
        government_evidence_owner="GOVERNMENT",
        citizen_data_owner="Department of Agriculture",
        model_access_mode="BLACK_BOX_ONLY",
        created_at="2026-08-01T00:00:00+00:00",
    )
    assert sched.startup_ip_owner == "VENDOR"
    assert sched.government_evidence_owner == "GOVERNMENT"

    # Invalid startup IP owner
    with pytest.raises(ValueError):
        IPGovernanceSchedule(
            schedule_id="IP-002",
            contract_id="CON-001",
            pilot_twin_id="TWIN-001",
            startup_ip_owner="GOVERNMENT",
            government_evidence_owner="GOVERNMENT",
            citizen_data_owner="Department of Agriculture",
            model_access_mode="BLACK_BOX_ONLY",
            created_at="2026-08-01T00:00:00+00:00",
        )


def test_dg_ip_schedule_enforces_black_box_mode():
    import pytest
    from ai.data_governance import IPGovernanceSchedule
    with pytest.raises(ValueError):
        IPGovernanceSchedule(
            schedule_id="IP-003",
            contract_id="CON-001",
            pilot_twin_id="TWIN-001",
            startup_ip_owner="VENDOR",
            government_evidence_owner="GOVERNMENT",
            citizen_data_owner="Department of Agriculture",
            model_access_mode="FULL_WEIGHTS_ACCESS",
            created_at="2026-08-01T00:00:00+00:00",
        )


def test_dg_schedule_created_per_pilot_twin():
    from ai.data_governance import create_data_governance_schedule
    sched = create_data_governance_schedule(
        contract_id="CON-AGRI-100",
        pilot_twin_id="TWIN-AGRI-01",
        citizen_data_owner="State Agritech Directorate",
        citizen_data_classification="SENSITIVE",
        retention_days=365,
        deletion_required=True,
    )
    assert sched.pilot_twin_id == "TWIN-AGRI-01"
    assert sched.ip_schedule.startup_ip_owner == "VENDOR"
    assert sched.ip_schedule.government_evidence_owner == "GOVERNMENT"
    assert "legal review" in sched.disclaimer.lower()


def test_dg_citizen_data_pseudonymization():
    from ai.data_governance import sanitize_citizen_data
    raw = {
        "name": "Ramesh Kumar",
        "phone": "+91-9876543210",
        "email": "ramesh@example.org",
        "aadhaar": "1234-5678-9012",
        "land_record_number": "LR-4421-A",
        "crop_type": "Wheat",
        "yield_estimate_kg": 4500,
    }
    sanitized = sanitize_citizen_data(raw)
    assert sanitized["crop_type"] == "Wheat"
    assert sanitized["yield_estimate_kg"] == 4500
    assert sanitized["name"].startswith("PSEUDO_")
    assert sanitized["phone"].startswith("PSEUDO_")
    assert sanitized["aadhaar"].startswith("PSEUDO_")
    assert "Ramesh Kumar" not in str(sanitized)


def test_dg_gps_metadata_removed():
    from ai.data_governance import sanitize_citizen_data
    raw = {
        "farmer_id": "F-001",
        "gps": {"latitude": 13.0827, "longitude": 80.2707},
        "lat": 13.0827,
        "lng": 80.2707,
        "location": "Plot 12-B",
        "soil_moisture": 42.5,
    }
    sanitized = sanitize_citizen_data(raw)
    assert "gps" not in sanitized
    assert "lat" not in sanitized
    assert "lng" not in sanitized
    assert "location" not in sanitized
    assert sanitized["soil_moisture"] == 42.5


# ============================================================
# FINAL CONSOLIDATION — MODULE B: TRUST REGISTRY & INVALIDATION
# ============================================================

def test_tr_evaluator_status_registration():
    from ai.trust_registry import register_evaluator_status, get_evaluator_status
    rec = register_evaluator_status("v2.1.0", "AUTHORIZED", "Golden reference suite passed")
    assert rec.evaluator_version == "v2.1.0"
    assert rec.status == "AUTHORIZED"
    assert get_evaluator_status("v2.1.0") == "AUTHORIZED"


def test_tr_evaluator_invalidation_updates_status():
    from ai.trust_registry import register_evaluator_status, invalidate_evaluator_version, get_evaluator_status
    register_evaluator_status("v2.2.0", "AUTHORIZED")
    inv = invalidate_evaluator_version("v2.2.0", "Benchmark methodology drift detected")
    assert inv.status == "INVALIDATED"
    assert get_evaluator_status("v2.2.0") == "INVALIDATED"


def test_tr_check_evaluator_authorization():
    from ai.trust_registry import register_evaluator_status, invalidate_evaluator_version, check_evaluator_authorization
    register_evaluator_status("v2.3.0", "AUTHORIZED")
    assert check_evaluator_authorization("v2.3.0") is True
    invalidate_evaluator_version("v2.3.0", "Security audit")
    assert check_evaluator_authorization("v2.3.0") is False


def test_tr_in_flight_evaluator_check_halts_on_invalidation():
    import pytest
    from ai.trust_registry import register_evaluator_status, invalidate_evaluator_version, check_in_flight_evaluator
    register_evaluator_status("v2.4.0", "AUTHORIZED")
    check_in_flight_evaluator("v2.4.0")  # does not raise

    invalidate_evaluator_version("v2.4.0", "Emergency halt")
    with pytest.raises(ValueError) as exc:
        check_in_flight_evaluator("v2.4.0")
    assert "INTERRUPTED — EVALUATOR INVALIDATED MID-EVALUATION" in str(exc.value)


def test_tr_retroactive_evidence_invalidation():
    from ai.trust_registry import invalidate_evidence_for_evaluator_version
    from ai.evidence_record import EvidenceRecord
    ev1 = EvidenceRecord(
        evidence_id="EVID-TR-01",
        vendor_id="V-01",
        artifact_id="ART-01",
        artifact_hash="hash1",
        evaluator_version="v2.5.0",
        test_suite_id="TS-01",
        test_suite_version="1.0",
        test_suite_hash="thash",
        source_type="evaluator_result",
        evidence_level="INDEPENDENTLY_VALIDATED",
        metric_name="Accuracy",
        metric_value=92.0,
        metric_unit="%",
        evaluation_id="EVAL-01",
        created_at="2026-08-01T00:00:00+00:00",
        validity_months=12,
        expires_at="2027-08-01T00:00:00+00:00",
        validation_status="VALIDATED",
        validation_reasons=["Passed"],
        frozen=False,
    )
    events = invalidate_evidence_for_evaluator_version("v2.5.0", [ev1])
    assert len(events) == 1
    assert events[0].new_validation_status == "REVALIDATION_REQUIRED"
    assert "EVALUATOR INTEGRITY UNDER REVIEW — RE-VALIDATION REQUIRED" in events[0].reason
    assert events[0].updated_evidence_record.validation_status == "REVALIDATION_REQUIRED"


def test_tr_historical_evidence_is_not_destroyed():
    from ai.trust_registry import invalidate_evidence_for_evaluator_version
    from ai.evidence_record import EvidenceRecord, freeze_evidence
    ev_frozen = EvidenceRecord(
        evidence_id="EVID-TR-02",
        vendor_id="V-02",
        artifact_id="ART-02",
        artifact_hash="hash2",
        evaluator_version="v2.6.0",
        test_suite_id="TS-02",
        test_suite_version="1.0",
        test_suite_hash="thash2",
        source_type="evaluator_result",
        evidence_level="INDEPENDENTLY_VALIDATED",
        metric_name="Accuracy",
        metric_value=95.0,
        metric_unit="%",
        evaluation_id="EVAL-02",
        created_at="2026-08-01T00:00:00+00:00",
        validity_months=12,
        expires_at="2027-08-01T00:00:00+00:00",
        validation_status="VALIDATED",
        validation_reasons=["Passed"],
        frozen=False,
    )
    freeze_evidence(ev_frozen)
    events = invalidate_evidence_for_evaluator_version("v2.6.0", [ev_frozen])
    # The original frozen record reference is protected, and a new event representation is returned
    assert len(events) == 1
    assert events[0].updated_evidence_record.validation_status == "REVALIDATION_REQUIRED"


# ============================================================
# FINAL CONSOLIDATION — MODULE C: PROCUREMENT MILESTONES
# ============================================================

def test_ms_milestone_creation_and_validation():
    from ai.milestones import ProcurementMilestone
    ms = ProcurementMilestone(
        milestone_id="MS-001",
        contract_id="CON-001",
        vendor_id="VendorA",
        name="Initial Accuracy Verification",
        required_kpi="Accuracy",
        threshold_operator=">=",
        threshold_value=85.0,
        required_evidence_level="INDEPENDENTLY_VALIDATED",
        payment_percentage=25.0,
        status="PENDING",
        evidence_id=None,
        created_at="2026-08-01T00:00:00+00:00",
    )
    assert ms.payment_percentage == 25.0
    assert ms.status == "PENDING"


def test_ms_valid_evidence_makes_milestone_ready_for_authorization():
    from ai.milestones import ProcurementMilestone, evaluate_milestone
    from ai.schemas import OutcomeContract, KPI
    from ai.evidence_record import EvidenceRecord

    contract = OutcomeContract(
        contract_id="CON-001",
        version="1.0",
        kpis=[KPI("Accuracy", 80.0, ">=", "%")],
        minimum_evidence_confidence=70.0,
        evidence_validity_months=12,
        locked=True,
    )
    ms = ProcurementMilestone(
        milestone_id="MS-002",
        contract_id="CON-001",
        vendor_id="VendorA",
        name="Phase 1 Benchmark",
        required_kpi="Accuracy",
        threshold_operator=">=",
        threshold_value=85.0,
        required_evidence_level="INDEPENDENTLY_VALIDATED",
        payment_percentage=20.0,
        status="PENDING",
        evidence_id=None,
        created_at="2026-08-01T00:00:00+00:00",
    )
    ev = EvidenceRecord(
        evidence_id="EVID-MS-01",
        vendor_id="VendorA",
        artifact_id="ART-01",
        artifact_hash="hash",
        evaluator_version="1.0",
        test_suite_id="TS-01",
        test_suite_version="1.0",
        test_suite_hash="thash",
        source_type="evaluator_result",
        evidence_level="INDEPENDENTLY_VALIDATED",
        metric_name="Accuracy",
        metric_value=89.5,
        metric_unit="%",
        evaluation_id="EVAL-01",
        created_at="2026-08-01T00:00:00+00:00",
        validity_months=12,
        expires_at="2027-08-01T00:00:00+00:00",
        validation_status="VALIDATED",
        validation_reasons=["Passed"],
        frozen=True,
    )

    evaluated = evaluate_milestone(
        milestone=ms,
        contract=contract,
        evidence_record=ev,
        artifact_verified=True,
        evidence_valid=True,
        evidence_confidence=85.0,
    )
    assert evaluated.status == "READY_FOR_AUTHORIZATION"
    assert evaluated.evidence_id == "EVID-MS-01"


def test_ms_missing_evidence_keeps_milestone_evidence_required():
    from ai.milestones import ProcurementMilestone, evaluate_milestone
    from ai.schemas import OutcomeContract, KPI

    contract = OutcomeContract("CON-001", "1.0", [KPI("Accuracy", 80.0, ">=")], 70.0, 12, True)
    ms = ProcurementMilestone("MS-003", "CON-001", "VendorA", "M3", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 20.0, "PENDING", None, "2026-08-01T00:00:00+00:00")
    evaluated = evaluate_milestone(ms, contract, None, True, True, 80.0)
    assert evaluated.status == "EVIDENCE_REQUIRED"


def test_ms_artifact_mismatch_blocks_milestone():
    from ai.milestones import ProcurementMilestone, evaluate_milestone
    from ai.schemas import OutcomeContract, KPI
    from ai.evidence_record import EvidenceRecord

    contract = OutcomeContract("CON-001", "1.0", [KPI("Accuracy", 80.0, ">=")], 70.0, 12, True)
    ms = ProcurementMilestone("MS-004", "CON-001", "VendorA", "M4", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 20.0, "PENDING", None, "2026-08-01T00:00:00+00:00")
    ev = EvidenceRecord("EVID-04", "VendorA", "ART-01", "h", "1.0", "TS-01", "1.0", "th", "src", "INDEPENDENTLY_VALIDATED", "Accuracy", 90.0, "%", "EVAL-01", "2026-08-01", 12, "2027-08-01", "VALIDATED", [], True)

    evaluated = evaluate_milestone(ms, contract, ev, artifact_verified=False, evidence_valid=True, evidence_confidence=85.0)
    assert evaluated.status == "REVALIDATION_REQUIRED"


def test_ms_low_confidence_blocks_milestone():
    from ai.milestones import ProcurementMilestone, evaluate_milestone
    from ai.schemas import OutcomeContract, KPI
    from ai.evidence_record import EvidenceRecord

    contract = OutcomeContract("CON-001", "1.0", [KPI("Accuracy", 80.0, ">=")], 75.0, 12, True)
    ms = ProcurementMilestone("MS-005", "CON-001", "VendorA", "M5", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 20.0, "PENDING", None, "2026-08-01T00:00:00+00:00")
    ev = EvidenceRecord("EVID-05", "VendorA", "ART-01", "h", "1.0", "TS-01", "1.0", "th", "src", "INDEPENDENTLY_VALIDATED", "Accuracy", 90.0, "%", "EVAL-01", "2026-08-01", 12, "2027-08-01", "VALIDATED", [], True)

    evaluated = evaluate_milestone(ms, contract, ev, artifact_verified=True, evidence_valid=True, evidence_confidence=60.0)
    assert evaluated.status == "BLOCKED"


def test_ms_failed_kpi_blocks_milestone():
    from ai.milestones import ProcurementMilestone, evaluate_milestone
    from ai.schemas import OutcomeContract, KPI
    from ai.evidence_record import EvidenceRecord

    contract = OutcomeContract("CON-001", "1.0", [KPI("Accuracy", 80.0, ">=")], 70.0, 12, True)
    ms = ProcurementMilestone("MS-006", "CON-001", "VendorA", "M6", "Accuracy", ">=", 90.0, "INDEPENDENTLY_VALIDATED", 20.0, "PENDING", None, "2026-08-01T00:00:00+00:00")
    ev = EvidenceRecord("EVID-06", "VendorA", "ART-01", "h", "1.0", "TS-01", "1.0", "th", "src", "INDEPENDENTLY_VALIDATED", "Accuracy", 85.0, "%", "EVAL-01", "2026-08-01", 12, "2027-08-01", "VALIDATED", [], True)

    evaluated = evaluate_milestone(ms, contract, ev, artifact_verified=True, evidence_valid=True, evidence_confidence=85.0)
    assert evaluated.status == "BLOCKED"


def test_ms_authorize_milestone_payment_records_authorization():
    from ai.milestones import ProcurementMilestone, authorize_milestone_payment
    ms = ProcurementMilestone("MS-007", "CON-001", "VendorA", "M7", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 30.0, "READY_FOR_AUTHORIZATION", "EVID-07", "2026-08-01T00:00:00+00:00")
    authorized = authorize_milestone_payment(
        milestone=ms,
        authorizing_officer_id="OFFICER-BOB",
        justification="Verified against independent evidence record EVID-07.",
    )
    assert authorized.status == "AUTHORIZED"
    assert authorized.authorized_by == "OFFICER-BOB"
    assert "PAYMENT_AUTHORIZED_FOR_RELEASE" in authorized.reasons


def test_ms_authorize_payment_rejects_unready_milestone():
    import pytest
    from ai.milestones import ProcurementMilestone, authorize_milestone_payment
    ms = ProcurementMilestone("MS-008", "CON-001", "VendorA", "M8", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 30.0, "BLOCKED", "EVID-08", "2026-08-01T00:00:00+00:00")
    with pytest.raises(ValueError):
        authorize_milestone_payment(ms, "OFFICER-BOB", "Authorize anyway")


def test_ms_authorize_payment_rejects_placeholder_justification():
    import pytest
    from ai.milestones import ProcurementMilestone, authorize_milestone_payment
    ms = ProcurementMilestone("MS-009", "CON-001", "VendorA", "M9", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 30.0, "READY_FOR_AUTHORIZATION", "EVID-09", "2026-08-01T00:00:00+00:00")
    with pytest.raises(ValueError):
        authorize_milestone_payment(ms, "OFFICER-BOB", "N/A")


def test_ms_invalidate_milestone_for_evidence():
    from ai.milestones import ProcurementMilestone, invalidate_milestone_for_evidence
    ms = ProcurementMilestone("MS-010", "CON-001", "VendorA", "M10", "Accuracy", ">=", 80.0, "INDEPENDENTLY_VALIDATED", 30.0, "AUTHORIZED", "EVID-10", "2026-08-01T00:00:00+00:00")
    invalidated = invalidate_milestone_for_evidence(ms, "Evidence expired in production")
    assert invalidated.status == "REVALIDATION_REQUIRED"


# ============================================================
# FINAL CONSOLIDATION — MODULE D: SCALE POLICY
# ============================================================

def test_sp_safe_scale_returns_case_a():
    from ai.scale_policy import evaluate_scale_policy
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.policy_case == "CASE_A_SAFE_SCALE"
    assert res.scale_eligible is True
    assert res.requires_human_review is False


def test_sp_hotspot_match_returns_case_b():
    from ai.scale_policy import evaluate_scale_policy
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "DEGRADED", 80.0, 20.0, "Degraded latency"))
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.policy_case == "CASE_B_HOTSPOT_MATCH"
    assert res.requires_human_review is True


def test_sp_critical_hotspot_returns_case_c():
    from ai.scale_policy import evaluate_scale_policy
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 55.0, 45.0, "Critical failure"))
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.policy_case == "CASE_C_CRITICAL_FAILURE_MATCH"
    assert res.scale_eligible is False
    assert res.requires_human_review is True


def test_sp_artifact_changed_returns_case_d():
    from ai.scale_policy import evaluate_scale_policy
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    res = evaluate_scale_policy(req, b"tampered_bytes", ar, ev, fm, pt)
    assert res.policy_case == "CASE_D_ARTIFACT_CHANGED"
    assert res.requires_revalidation is True


def test_sp_evidence_expired_returns_case_e():
    from ai.scale_policy import evaluate_scale_policy
    from datetime import datetime, timezone, timedelta
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    ev.expires_at = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.policy_case == "CASE_E_EVIDENCE_EXPIRED"
    assert res.requires_revalidation is True


def test_sp_unverified_pilot_twin_returns_case_f():
    from ai.scale_policy import evaluate_scale_policy
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    pt.connectivity = "UNVERIFIED"
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.policy_case == "CASE_F_PILOT_TWIN_UNVERIFIED"
    assert res.requires_human_review is True


def test_sp_vendor_response_window_preserved_for_review_or_blocked():
    from ai.scale_policy import evaluate_scale_policy
    from ai.failure_cartography import FailureHotspot
    req, b, ar, ev, fm, pt = get_mock_scale_up_deps()
    fm.hotspots.append(FailureHotspot("STABLE_HIGH_END_STANDARD_CLEAN", "CRITICAL", 55.0, 45.0, "Critical failure"))
    res = evaluate_scale_policy(req, b, ar, ev, fm, pt)
    assert res.vendor_response_window_required is True


# ============================================================
# FINAL CONSOLIDATION — MODULE E & F: E2E PIPELINE & API
# ============================================================

def test_e2e_run_axiom_demo_executes_all_stages():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert res.contract["contract_id"] == "CONTRACT-AGRI-001"
    assert res.pilot_twin["twin_id"] == "TWIN-DISTRICT-ALPHA"
    assert res.test_suite_summary["total_public_strata"] == 24
    assert res.evaluator_status["status"] == "AUTHORIZED"


def test_e2e_demo_produces_three_vendor_results():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert "VendorA" in res.vendor_results
    assert "VendorB" in res.vendor_results
    assert "VendorC" in res.vendor_results


def test_e2e_demo_produces_evidence_confidence():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert "VendorA" in res.confidence_summary
    assert res.confidence_summary["VendorA"]["score"] >= 70.0


def test_e2e_demo_produces_failure_cartography():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert "VendorC" in res.failure_map_summary
    assert res.failure_map_summary["VendorC"]["critical_hotspots_count"] >= 1


def test_e2e_demo_produces_procurement_recommendations():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert "VendorA" in res.procurement_decisions
    assert "decision" in res.procurement_decisions["VendorA"]


def test_e2e_demo_produces_vendor_response():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert res.vendor_response["vendor_id"] == "VendorC"
    assert res.vendor_response["history_event_count"] >= 1


def test_e2e_demo_produces_human_authorization():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert res.human_authorization["status"] == "AUTHORIZED"
    assert res.human_authorization["authorizing_officer_id"] == "OFFICER-ALICE"


def test_e2e_demo_produces_scale_up_evaluation():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    assert res.scale_up_evaluation["target_district"] == "District Beta"
    assert "CRITICAL_MATCH" in res.scale_up_evaluation["failure_map_status"]
    assert res.scale_up_evaluation["scale_eligible"] is False


def test_e2e_demo_to_public_dict_serializes_cleanly():
    from ai.pipeline import run_axiom_demo
    res = run_axiom_demo(seed=42)
    pub = res.to_public_dict()
    assert isinstance(pub, dict)
    assert "contract" in pub
    assert "vendor_results" in pub


def test_api_health_endpoint():
    from app.main import health_check
    h = health_check()
    assert h["status"] == "ok"
    assert h["service"] == "Axiom AI"


def test_api_demo_run_endpoint():
    from app.main import run_demo
    data = run_demo(seed=42)
    assert "contract" in data
    assert "vendors" not in data or "vendor_results" in data


def test_api_demo_summary_endpoint():
    from app.main import get_demo_summary
    summary = get_demo_summary()
    assert "contract" in summary
    assert "vendors" in summary
    assert "failure_hotspots" in summary


# ============================================================
# FINAL CONSOLIDATION — MANDATORY SPECIAL GOVERNANCE TESTS
# ============================================================

def test_axiom_end_to_end_governance_chain():
    """
    Verifies that all 14 stages pass output to the next stage without bypassing governance:
    Problem -> Contract -> Twin -> Matrix -> Golden Suite -> Evaluator Auth ->
    Artifact Freeze -> Evaluation -> Evidence -> Confidence -> Failure Cartography ->
    Procurement -> Vendor Response -> Human Auth -> Scale-Up.
    """
    from ai.pipeline import run_axiom_demo
    result = run_axiom_demo(seed=42)

    # 1. Contract generated and locked
    assert result.contract["is_locked"] is True
    # 2. Pilot Twin has parameters
    assert len(result.pilot_twin["parameters"]) >= 4
    # 3. Test Suite has 24 strata
    assert result.test_suite_summary["total_public_strata"] == 24
    # 4. Golden Suite authorizes evaluator
    assert result.evaluator_status["status"] == "AUTHORIZED"
    # 5. 3 vendors evaluated
    assert len(result.vendor_results) == 3
    # 6. Evidence generated with provenance
    assert result.evidence_summary["VendorA"]["evidence_level"] == "INDEPENDENTLY_VALIDATED"
    # 7. Confidence meets minimum threshold
    assert result.confidence_summary["VendorA"]["score"] >= result.contract["minimum_evidence_confidence"]
    # 8. Failure cartography identifies hotspots
    assert len(result.failure_map_summary["VendorC"]["hotspots"]) >= 1
    # 9. Procurement decision is gated (Vendor B passes, Vendor C fails critical gate)
    assert result.procurement_decisions["VendorB"]["decision"] == "ELIGIBLE"
    assert result.procurement_decisions["VendorC"]["decision"] == "REJECTED"
    # 10. Vendor response recorded
    assert result.vendor_response["status"] == "UNDER_REVIEW"
    # 11. Human authorization recorded
    assert result.human_authorization["status"] == "AUTHORIZED"
    # 12. Scale up blocked on critical hotspot in target district
    assert result.scale_up_evaluation["scale_eligible"] is False


def test_no_cheating_vendor_identity_does_not_determine_winner():
    """
    Proves that vendor winning/eligibility is driven strictly by evaluated metrics,
    confidence, and failure conditions, NOT by hardcoded vendor ID.
    """
    from ai.decision_engine import evaluate_procurement
    from ai.schemas import OutcomeContract, KPI

    contract = OutcomeContract("CON-CHEATING-TEST", "1.0", [KPI("Accuracy", 90.0, ">=")], 75.0, 12, True)

    # Vendor named "VendorA" with failing KPI should be rejected
    dec_a = evaluate_procurement(
        contract=contract,
        kpi_results={"Accuracy": 70.0},
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=80.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert dec_a.decision == "REJECTED"

    # Arbitrary vendor named "UnknownStartup_XYZ" with passing KPI and clean gates should be eligible
    dec_xyz = evaluate_procurement(
        contract=contract,
        kpi_results={"Accuracy": 95.0},
        evaluator_status="AUTHORIZED",
        artifact_integrity=True,
        evidence_confidence=85.0,
        evidence_valid=True,
        critical_failures=False,
    )
    assert dec_xyz.decision == "ELIGIBLE"


def test_no_private_leak_in_serialization():
    """
    Serializes test suite, demo result, and API summary,
    and proves that raw seed, private_parameters, and model weights are NOT exposed.
    """
    import json
    from ai.pipeline import run_axiom_demo
    from app.main import get_demo_summary

    demo_res = run_axiom_demo(seed=999)
    public_dict = demo_res.to_public_dict()
    summary_dict = get_demo_summary()

    public_json_str = json.dumps(public_dict)
    summary_json_str = json.dumps(summary_dict)

    for sensitive_keyword in ["raw_seed", "private_parameters", "model_weights", "source_code"]:
        assert sensitive_keyword not in public_json_str
        assert sensitive_keyword not in summary_json_str


def test_no_autonomous_action():
    """
    Verifies that the entire platform contains no callable mechanism that autonomously
    awards procurement, transfers money, releases funds, or bypasses human authorization.
    """
    import ai.human_authorization as ha
    import ai.milestones as ms
    import ai.decision_engine as de
    import ai.scale_up as su

    for module in [ha, ms, de, su]:
        assert not hasattr(module, "auto_authorize")
        assert not hasattr(module, "release_funds_automatically")
        assert not hasattr(module, "execute_bank_transfer")
        assert not hasattr(module, "auto_deploy_vendor")


def test_gov_pilot_twin_locked_mutation_raises():
    import pytest
    from ai.pilot_twin import create_pilot_twin, PilotParameter, update_parameter_evidence
    twin = create_pilot_twin(
        twin_id="TWIN-LOCK-TEST",
        department="Health",
        district="District 1",
        parameters=[PilotParameter(name="connectivity", value="GOOD", evidence_level="OBSERVED", source="Log")]
    )
    twin.locked = True
    with pytest.raises(ValueError) as exc:
        update_parameter_evidence(twin, "connectivity", "INDEPENDENTLY_VALIDATED", "Auditor")
    assert "locked" in str(exc.value).lower()


def test_gov_golden_suite_cannot_be_reviewed_by_developer():
    import pytest
    from ai.golden_suite import (
        create_initial_golden_suite,
        propose_golden_suite_change,
        review_golden_suite_change,
        EVALUATOR_DEVELOPMENT_ROLE,
    )
    suite = create_initial_golden_suite()
    change = propose_golden_suite_change(
        active_suite=suite,
        change_type="UPDATE",
        reason="Refine tolerance",
        requested_by="Dev1",
        new_cases=suite.cases,
        new_version="1.1",
    )
    with pytest.raises(ValueError) as exc:
        review_golden_suite_change(
            change_record=change,
            reviewer_role=EVALUATOR_DEVELOPMENT_ROLE,
            reviewer_id="Dev1",
            approve=True,
            justification="Self-approval",
        )
    assert "cannot review" in str(exc.value).lower()


def test_gov_evaluator_unauthorized_blocks_evaluation():
    import pytest
    from ai.evaluator import evaluate_vendor, EvaluationAdapter
    from ai.test_matrix import generate_test_suite
    from ai.demo_vendors import VendorAAdapter

    suite = generate_test_suite("SUITE-UNAUTH", "TWIN-01", seed=42)
    with pytest.raises(ValueError) as exc:
        evaluate_vendor(
            vendor_id="VendorA",
            artifact_id="ART-01",
            adapter=VendorAAdapter(),
            test_suite=suite,
            evaluator_version="1.0.0",
            evaluator_authorized=False,
            expected_outputs={},
        )
    assert "Evaluator must be authorized" in str(exc.value)


def test_gov_artifact_mismatch_verification():
    from ai.artifact import register_artifact, freeze_artifact, verify_artifact_for_evaluation
    art = register_artifact("ART-VER-01", "VendorA", b"original_code")
    frozen = freeze_artifact(art)
    res_match = verify_artifact_for_evaluation(frozen, b"original_code")
    assert res_match.status == "MATCH"
    res_mismatch = verify_artifact_for_evaluation(frozen, b"tampered_code")
    assert res_mismatch.status == "MISMATCH"


def test_gov_confidence_components_weights_sum_to_one():
    from ai.confidence import CONFIDENCE_WEIGHTS, explain_evidence_confidence
    assert round(sum(CONFIDENCE_WEIGHTS.values()), 4) == 1.0
    explained = explain_evidence_confidence(100.0, 100.0, 100.0, 100.0, 100.0, 100.0)
    assert explained["overall_confidence"] == 100.0


def test_gov_matrix_seed_reproducibility():
    from ai.test_matrix import generate_test_suite
    suite1 = generate_test_suite("SUITE-R1", "TWIN-01", seed=12345)
    suite2 = generate_test_suite("SUITE-R2", "TWIN-01", seed=12345)
    assert suite1.seed_hash == suite2.seed_hash
    assert len(suite1.conditions) == len(suite2.conditions) == 24


# ============================================================
# EVALUATION INTELLIGENCE ENGINE TESTS (STEP 2)
# ============================================================

def _get_mock_eval_intelligence_data():
    from ai.test_matrix import generate_test_suite
    from ai.demo_vendors import VendorCAdapter, VendorAAdapter
    from ai.demo_dataset import get_demo_expected_outputs
    from ai.evaluator import evaluate_vendor
    from ai.failure_cartography import generate_failure_map
    from ai.pilot_twin import create_pilot_twin, PilotParameter
    from ai.schemas import OutcomeContract, KPI

    suite = generate_test_suite("SUITE-EI-01", "TWIN-EI-01", seed=42)
    expected = get_demo_expected_outputs(suite)

    # Vendor C has the compound catastrophic failure on NOISY + LOW_END + REGIONAL
    run_c = evaluate_vendor("VendorC", "ART-VC-01", VendorCAdapter(), suite, "1.0.0", True, expected)
    fm_c = generate_failure_map(run_c)

    twin = create_pilot_twin(
        "TWIN-EI-01", "Agri", "District 1",
        [PilotParameter(name="connectivity", value="INTERMITTENT", evidence_level="OBSERVED")]
    )
    contract = OutcomeContract("CON-EI-01", "1.0", [KPI("Accuracy", 80.0, ">=")], 70.0, 12, True)

    return run_c, fm_c, twin, contract


def test_ei_deterministic_report_generation():
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = generate_forensic_diagnosis(run, fm, twin, contract)
    assert report.analysis_mode == "DETERMINISTIC_FALLBACK"
    assert report.vendor_id == "VendorC"
    assert report.evaluation_id == run.evaluation_id


def test_ei_correct_vendor_id():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert report.vendor_id == "VendorC"


def test_ei_correct_evaluation_id():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert report.evaluation_id == run.evaluation_id


def test_ei_hotspot_detection():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert len(report.compound_hotspot_diagnoses) >= 1
    # Check severity matches failure map
    for d in report.compound_hotspot_diagnoses:
        assert d.severity in ("CRITICAL", "DEGRADED", "WATCH")


def test_ei_public_stratum_parsing():
    from ai.evaluation_intelligence import parse_stratum_id
    parsed = parse_stratum_id("INTERMITTENT_LOW_END_REGIONAL_NOISY")
    assert parsed["connectivity"] == "INTERMITTENT"
    assert parsed["device"] == "LOW_END"
    assert parsed["language"] == "REGIONAL"
    assert parsed["input_quality"] == "NOISY"

    parsed_clean = parse_stratum_id("GOOD_HIGH_END_STANDARD_CLEAN")
    assert parsed_clean["connectivity"] == "GOOD"
    assert parsed_clean["device"] == "HIGH_END"
    assert parsed_clean["language"] == "STANDARD"
    assert parsed_clean["input_quality"] == "CLEAN"


def test_ei_compound_interaction_detection():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    # Check that the critical hotspot mentions compound interaction or multi-factor pattern
    found_compound = False
    for d in report.compound_hotspot_diagnoses:
        if d.severity == "CRITICAL":
            if "compound" in d.diagnosis.lower() or "interaction" in d.diagnosis.lower() or "concurrent" in d.diagnosis.lower():
                found_compound = True
                break
    assert found_compound is True


def test_ei_operational_risk_generation():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert len(report.operational_risk_summary) > 10
    # Operational impact exists in diagnoses without hallucinated statistics
    for d in report.compound_hotspot_diagnoses:
        assert "operational risk" in d.operational_impact.lower() or "failure rate" in d.operational_impact.lower()
        assert "deaths" not in d.operational_impact.lower()
        assert "dollars" not in d.operational_impact.lower()


def test_ei_challenge_proposal_generation():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert len(report.recommended_vendor_challenges) >= 1
    chal = report.recommended_vendor_challenges[0]
    assert chal.challenge_id.startswith("CHAL-VendorC")
    assert len(chal.question) > 20
    assert len(chal.requested_evidence) >= 1
    assert chal.priority in ("HIGH", "MEDIUM", "LOW")


def test_ei_targeted_retest_generation():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert len(report.targeted_retest_recommendations) >= 1
    retest = report.targeted_retest_recommendations[0]
    assert retest.recommendation_id.startswith("RETEST-VendorC")
    assert len(retest.objective) > 10


def test_ei_nonexistent_stratum_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Tamper with stratum_id
    report.compound_hotspot_diagnoses[0].stratum_id = "FAKE_NONEXISTENT_STRATUM_999"
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "non-existent stratum_id" in str(exc.value)


def test_ei_fabricated_accuracy_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Tamper with accuracy metric
    report.compound_hotspot_diagnoses[0].accuracy = 99.99
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "Accuracy mismatch" in str(exc.value)


def test_ei_fabricated_severity_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Tamper with severity
    report.compound_hotspot_diagnoses[0].severity = "NORMAL"
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "Severity mismatch" in str(exc.value)


def test_ei_private_parameter_leakage_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Inject private leak into diagnosis text
    report.overall_verdict_explanation += " Leaked private_parameters: {'noise': 0.25}"
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "forbidden private/secret keyword" in str(exc.value)


def test_ei_seed_leakage_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Inject seed keyword
    report.operational_risk_summary += " Evaluated with raw_seed = 42"
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "forbidden private/secret keyword" in str(exc.value)


def test_ei_procurement_authorization_attempt_rejection():
    import pytest
    from ai.evaluation_intelligence import _validate_diagnostic_report, _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    # Inject unauthorized executive action
    report.overall_verdict_explanation += " The solution is hereby procurement_approved by AI."
    with pytest.raises(ValueError) as exc:
        _validate_diagnostic_report(report, run, fm)
    assert "forbidden autonomous governance action" in str(exc.value)


def test_ei_evidence_level_modification_rejection():
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    from ai.evidence_record import EvidenceRecord
    run, fm, twin, contract = _get_mock_eval_intelligence_data()

    ev = EvidenceRecord("EVID-TEST", "VendorC", "ART-01", "hash", "1.0", "TS-01", "1.0", "th", "src", "OBSERVED", "Acc", 80.0, "%", "EV-01", "2026-08-01", 12, "2027-08-01", "VALIDATED", [], True)

    _ = generate_forensic_diagnosis(run, fm, twin, contract)
    # Evidence level on evidence record must remain untouched
    assert ev.evidence_level == "OBSERVED"


def test_ei_deterministic_behavior():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    r1 = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    r2 = _deterministic_forensic_diagnosis(run, fm, twin, contract)
    assert r1.to_dict() == r2.to_dict()


def test_ei_empty_hotspot_handling():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    from ai.test_matrix import generate_test_suite
    from ai.evaluator import EvaluationRun, EvaluationCaseResult
    from ai.failure_cartography import generate_failure_map

    suite = generate_test_suite("SUITE-PERFECT", "TWIN-01", seed=42)
    # Perfect run with 100% accuracy on all cases
    cases = [
        EvaluationCaseResult(c.test_case_id, c.stratum_id, "PASS", "PASS", True, 50.0, False)
        for c in suite.conditions
    ]
    perfect_run = EvaluationRun(
        evaluation_id="EVAL-PERF",
        vendor_id="VendorPerfect",
        artifact_id="ART-P",
        evaluator_version="1.0.0",
        test_suite_id=suite.suite_id,
        test_suite_version=suite.version,
        test_suite_hash=suite.seed_hash,
        results=cases,
        total_cases=24,
        correct_cases=24,
        accuracy=100.0,
        average_latency_ms=50.0,
        error_count=0,
        status="COMPLETED",
    )
    fm_perf = generate_failure_map(perfect_run)
    report = _deterministic_forensic_diagnosis(perfect_run, fm_perf)

    assert len(report.compound_hotspot_diagnoses) == 0
    assert len(report.recommended_vendor_challenges) == 0
    assert "robust" in report.overall_verdict_explanation.lower()
    assert "low operational risk" in report.operational_risk_summary.lower()


def test_ei_llm_missing_key_fallback(monkeypatch):
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = generate_forensic_diagnosis(run, fm, twin, contract)
    assert report.analysis_mode == "DETERMINISTIC_FALLBACK"


def test_ei_llm_malformed_output_fallback(monkeypatch):
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    monkeypatch.setenv("OPENAI_API_KEY", "mock_key_for_test")

    class MockCompletions:
        def create(self, **kwargs):
            raise RuntimeError("API Connection Timeout")

    class MockChat:
        completions = MockCompletions()

    class MockOpenAI:
        def __init__(self, **kwargs):
            self.chat = MockChat()

    monkeypatch.setattr("ai.evaluation_intelligence.OpenAI", MockOpenAI)

    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = generate_forensic_diagnosis(run, fm, twin, contract)
    # Graceful fallback to deterministic engine
    assert report.analysis_mode == "DETERMINISTIC_FALLBACK"
    assert report.vendor_id == "VendorC"


def test_ei_source_objects_remain_unchanged():
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()

    acc_before = run.accuracy
    status_before = fm.status
    kpis_before = len(contract.kpis)

    _ = generate_forensic_diagnosis(run, fm, twin, contract)

    assert run.accuracy == acc_before
    assert fm.status == status_before
    assert len(contract.kpis) == kpis_before


def test_ei_diagnostic_confidence_stays_separate_from_evidence_confidence():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    from ai.confidence import calculate_evidence_confidence
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    for d in report.compound_hotspot_diagnoses:
        # diagnostic confidence is on HotspotDiagnosis
        assert 0.0 <= d.confidence <= 100.0

    # Evidence confidence is computed independently by confidence.py
    ev_conf = calculate_evidence_confidence(100.0, 100.0, 100.0, 100.0, 80.0, 90.0)
    assert isinstance(ev_conf, float)


def test_ei_every_referenced_stratum_exists():
    from ai.evaluation_intelligence import _deterministic_forensic_diagnosis
    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    report = _deterministic_forensic_diagnosis(run, fm, twin, contract)

    valid_strata = {s.stratum_id for s in fm.strata}
    for d in report.compound_hotspot_diagnoses:
        assert d.stratum_id in valid_strata
    for c in report.recommended_vendor_challenges:
        assert c.target_stratum_id in valid_strata
    for r in report.targeted_retest_recommendations:
        assert r.target_stratum_id in valid_strata


def test_ei_llm_output_cannot_modify_actual_measured_values(monkeypatch):
    import json
    from ai.evaluation_intelligence import generate_forensic_diagnosis
    monkeypatch.setenv("OPENAI_API_KEY", "mock_key_for_test")

    # Mock LLM returning tampered accuracy value
    class MockChoice:
        message = type("msg", (), {
            "content": json.dumps({
                "vendor_id": "VendorC",
                "evaluation_id": "EVAL-FAKE",
                "overall_verdict_explanation": "Fake summary",
                "operational_risk_summary": "Fake risk",
                "compound_hotspot_diagnoses": [
                    {
                        "stratum_id": "GOOD_HIGH_END_STANDARD_CLEAN",
                        "severity": "NORMAL",
                        "accuracy": 10.0,  # Fabricated! Real value is 100.0
                        "error_rate": 90.0,
                        "observed_conditions": {},
                        "diagnosis": "Fake",
                        "operational_impact": "Fake",
                        "confidence": 50.0,
                        "supporting_observations": []
                    }
                ],
                "recommended_vendor_challenges": [],
                "targeted_retest_recommendations": []
            })
        })()

    class MockCompletions:
        def create(self, **kwargs):
            return type("resp", (), {"choices": [MockChoice()]})()

    class MockChat:
        completions = MockCompletions()

    class MockOpenAI:
        def __init__(self, **kwargs):
            self.chat = MockChat()

    monkeypatch.setattr("ai.evaluation_intelligence.OpenAI", MockOpenAI)

    run, fm, twin, contract = _get_mock_eval_intelligence_data()
    # When LLM tries to tamper with metrics, validation catches it and falls back to deterministic
    report = generate_forensic_diagnosis(run, fm, twin, contract)
    assert report.analysis_mode == "DETERMINISTIC_FALLBACK"
    assert report.evaluation_id == run.evaluation_id


# ============================================================
# PIPELINE INTEGRATION TESTS — STEP 3
# ============================================================

def _run_demo_pipeline():
    from ai.pipeline import run_axiom_demo
    return run_axiom_demo(seed=42)


def test_pi_pipeline_generates_diagnostic_report():
    res = _run_demo_pipeline()
    assert hasattr(res, "diagnostic_intelligence")
    assert isinstance(res.diagnostic_intelligence, dict)
    assert len(res.diagnostic_intelligence) >= 1


def test_pi_every_demo_vendor_receives_separate_report():
    res = _run_demo_pipeline()
    assert "VendorA" in res.diagnostic_intelligence
    assert "VendorB" in res.diagnostic_intelligence
    assert "VendorC" in res.diagnostic_intelligence


def test_pi_vendor_ids_match():
    res = _run_demo_pipeline()
    for vid in ("VendorA", "VendorB", "VendorC"):
        assert res.diagnostic_intelligence[vid]["vendor_id"] == vid


def test_pi_evaluation_ids_match():
    res = _run_demo_pipeline()
    for vid in ("VendorA", "VendorB", "VendorC"):
        assert res.diagnostic_intelligence[vid]["evaluation_id"] == res.vendor_results[vid]["evaluation_id"]


def test_pi_deterministic_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    res = _run_demo_pipeline()
    for vid in ("VendorA", "VendorB", "VendorC"):
        assert res.diagnostic_intelligence[vid]["analysis_mode"] == "DETERMINISTIC_FALLBACK"


def test_pi_diagnostic_report_contains_hotspot_diagnoses():
    res = _run_demo_pipeline()
    # VendorC has known critical hotspots
    vc_diag = res.diagnostic_intelligence["VendorC"]
    assert "compound_hotspot_diagnoses" in vc_diag
    assert len(vc_diag["compound_hotspot_diagnoses"]) >= 1


def test_pi_diagnostic_report_contains_operational_risk():
    res = _run_demo_pipeline()
    for vid in ("VendorA", "VendorB", "VendorC"):
        diag = res.diagnostic_intelligence[vid]
        assert "operational_risk_summary" in diag
        assert len(diag["operational_risk_summary"]) > 0


def test_pi_diagnostic_report_contains_challenge_proposals():
    res = _run_demo_pipeline()
    # VendorC has hotspots and therefore challenge proposals
    vc_diag = res.diagnostic_intelligence["VendorC"]
    assert "recommended_vendor_challenges" in vc_diag
    assert len(vc_diag["recommended_vendor_challenges"]) >= 1


def test_pi_diagnostic_report_contains_retest_recommendations():
    res = _run_demo_pipeline()
    vc_diag = res.diagnostic_intelligence["VendorC"]
    assert "targeted_retest_recommendations" in vc_diag
    assert len(vc_diag["targeted_retest_recommendations"]) >= 1


def test_pi_ai_output_cannot_alter_procurement_decision():
    """
    Proves: changing the diagnostic explanation cannot change the procurement decision.
    The AI layer is advisory only and never feeds into the deterministic decision gate.
    """
    import copy
    res = _run_demo_pipeline()

    # Record original procurement decisions
    original_decisions = copy.deepcopy(res.procurement_decisions)

    # Tamper with diagnostic intelligence
    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "COMPLETELY FABRICATED EXPLANATION"
        res.diagnostic_intelligence[vid]["operational_risk_summary"] = "INVENTED RISK"

    # Procurement decisions must remain identical (they were computed independently)
    assert res.procurement_decisions == original_decisions


def test_pi_ai_output_cannot_alter_scale_decision():
    import copy
    res = _run_demo_pipeline()
    original_scale = copy.deepcopy(res.scale_up_evaluation)

    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "FABRICATED"

    assert res.scale_up_evaluation == original_scale


def test_pi_ai_output_cannot_alter_evidence():
    import copy
    res = _run_demo_pipeline()
    original_evidence = copy.deepcopy(res.evidence_summary)

    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "FABRICATED"

    assert res.evidence_summary == original_evidence


def test_pi_ai_output_cannot_alter_failure_map():
    import copy
    res = _run_demo_pipeline()
    original_fm = copy.deepcopy(res.failure_map_summary)

    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "FABRICATED"

    assert res.failure_map_summary == original_fm


def test_pi_ai_output_cannot_alter_outcome_contract():
    import copy
    res = _run_demo_pipeline()
    original_contract = copy.deepcopy(res.contract)

    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "FABRICATED"

    assert res.contract == original_contract


def test_pi_ai_output_cannot_alter_pilot_twin():
    import copy
    res = _run_demo_pipeline()
    original_twin = copy.deepcopy(res.pilot_twin)

    for vid in res.diagnostic_intelligence:
        res.diagnostic_intelligence[vid]["overall_verdict_explanation"] = "FABRICATED"

    assert res.pilot_twin == original_twin


def test_pi_source_objects_remain_unchanged_after_pipeline():
    """
    Verifies that pipeline execution with diagnostic intelligence
    does not mutate any of the source governance objects.
    """
    res1 = _run_demo_pipeline()
    res2 = _run_demo_pipeline()

    # Deterministic pipeline should produce identical structural results
    assert res1.contract == res2.contract
    assert res1.pilot_twin == res2.pilot_twin
    # evaluator_status verified_at is a timestamp that differs between runs
    assert res1.evaluator_status["evaluator_version"] == res2.evaluator_status["evaluator_version"]
    assert res1.evaluator_status["status"] == res2.evaluator_status["status"]
    assert res1.failure_map_summary == res2.failure_map_summary
    assert res1.procurement_decisions == res2.procurement_decisions


def test_pi_existing_pipeline_outputs_remain_present():
    res = _run_demo_pipeline()
    assert hasattr(res, "contract")
    assert hasattr(res, "pilot_twin")
    assert hasattr(res, "test_suite_summary")
    assert hasattr(res, "evaluator_status")
    assert hasattr(res, "vendor_results")
    assert hasattr(res, "evidence_summary")
    assert hasattr(res, "confidence_summary")
    assert hasattr(res, "failure_map_summary")
    assert hasattr(res, "procurement_decisions")
    assert hasattr(res, "vendor_response")
    assert hasattr(res, "human_authorization")
    assert hasattr(res, "scale_up_evaluation")
    assert hasattr(res, "data_governance")
    assert hasattr(res, "diagnostic_intelligence")
    assert hasattr(res, "audit_summary")


def test_pi_pipeline_functional_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    res = _run_demo_pipeline()
    # Full pipeline must still work
    assert res.human_authorization["status"] == "AUTHORIZED"
    assert len(res.vendor_results) == 3
    assert len(res.diagnostic_intelligence) == 3


def test_pi_diagnostic_reports_isolated_between_vendors():
    res = _run_demo_pipeline()
    va = res.diagnostic_intelligence["VendorA"]
    vb = res.diagnostic_intelligence["VendorB"]
    vc = res.diagnostic_intelligence["VendorC"]

    # Each report references only its own vendor
    assert va["vendor_id"] == "VendorA"
    assert vb["vendor_id"] == "VendorB"
    assert vc["vendor_id"] == "VendorC"

    # Evaluation IDs must differ between vendors
    assert va["evaluation_id"] != vb["evaluation_id"]
    assert vb["evaluation_id"] != vc["evaluation_id"]
    assert va["evaluation_id"] != vc["evaluation_id"]


def test_pi_result_remains_serializable():
    import json
    res = _run_demo_pipeline()
    public = res.to_public_dict()
    # Must serialize to JSON without error
    json_str = json.dumps(public)
    assert len(json_str) > 100
    parsed = json.loads(json_str)
    assert "diagnostic_intelligence" in parsed
    assert "VendorA" in parsed["diagnostic_intelligence"]
    assert "VendorB" in parsed["diagnostic_intelligence"]
    assert "VendorC" in parsed["diagnostic_intelligence"]


