"""
Canonical Demo Scenario Tests (Step 5)

Verifies that the canonical demonstration scenario generates presentation-ready,
differentiated vendor results, failure cartography, forensic diagnostics,
deterministic procurement, human authorization, and scale-up gating without
exposing private test parameters or leaking seeds/secrets.
"""

import json
import pytest
from fastapi.testclient import TestClient

from ai.demo_scenario import (
    get_demo_scenario_metadata,
    run_demo_scenario,
    format_demo_summary,
    CANONICAL_SCENARIO_ID,
    CANONICAL_DEPARTMENT,
    CANONICAL_DISTRICT,
)
from app.main import app

client = TestClient(app)


# ============================================================
# METADATA & STRUCTURE TESTS
# ============================================================

def test_scenario_metadata_exists():
    meta = get_demo_scenario_metadata()
    assert isinstance(meta, dict)
    assert meta["scenario_id"] == CANONICAL_SCENARIO_ID
    assert meta["department"] == CANONICAL_DEPARTMENT
    assert meta["district"] == CANONICAL_DISTRICT


def test_scenario_id_is_stable():
    meta1 = get_demo_scenario_metadata()
    meta2 = get_demo_scenario_metadata()
    assert meta1["scenario_id"] == meta2["scenario_id"] == "AXIOM-DEMO-001"


def test_problem_statement_is_non_empty():
    meta = get_demo_scenario_metadata()
    assert len(meta["problem_statement"].strip()) > 30


def test_department_and_district_are_present():
    meta = get_demo_scenario_metadata()
    assert "Agricultural Logistics" in meta["department"]
    assert "Rural Demonstration District" in meta["district"]


def test_exactly_three_demo_vendors_exist():
    meta = get_demo_scenario_metadata()
    assert len(meta["vendors"]) == 3
    v_ids = [v["vendor_id"] for v in meta["vendors"]]
    assert set(v_ids) == {"VendorA", "VendorB", "VendorC"}


# ============================================================
# EVALUATION & DIFFERENTIATION TESTS
# ============================================================

def test_all_three_vendors_receive_evaluations():
    summary = run_demo_scenario(seed=42)
    assert len(summary["vendors"]) == 3
    v_ids = [v["vendor_id"] for v in summary["vendors"]]
    assert "VendorA" in v_ids
    assert "VendorB" in v_ids
    assert "VendorC" in v_ids


def test_vendor_ids_are_unique():
    summary = run_demo_scenario(seed=42)
    v_ids = [v["vendor_id"] for v in summary["vendors"]]
    assert len(v_ids) == len(set(v_ids)) == 3


def test_evaluation_ids_are_present_and_unique():
    summary = run_demo_scenario(seed=42)
    eval_ids = [v["evaluation_id"] for v in summary["vendors"]]
    assert all(eid is not None and len(eid) > 0 for eid in eval_ids)
    assert len(set(eval_ids)) == 3


def test_vendor_results_contain_accuracy_and_metrics():
    summary = run_demo_scenario(seed=42)
    for v in summary["vendors"]:
        assert isinstance(v["accuracy"], float)
        assert isinstance(v["latency"], float)
        assert isinstance(v["error_count"], int)
        assert 0.0 <= v["accuracy"] <= 100.0


def test_vendor_results_contain_diagnostic_information():
    summary = run_demo_scenario(seed=42)
    for v in summary["vendors"]:
        assert "diagnostic_summary" in v
        assert len(v["diagnostic_summary"]) > 10


def test_failure_cartography_is_present():
    summary = run_demo_scenario(seed=42)
    assert "failure_maps" in summary
    assert len(summary["failure_maps"]) == 3
    for fm in summary["failure_maps"]:
        assert "overall_status" in fm
        assert "overall_accuracy" in fm
        assert "hotspots" in fm
        assert fm["total_strata"] == 24


def test_procurement_information_is_present():
    summary = run_demo_scenario(seed=42)
    assert "procurement" in summary
    assert "VendorA" in summary["procurement"]
    assert "VendorB" in summary["procurement"]
    assert "VendorC" in summary["procurement"]
    assert summary["procurement"]["VendorB"]["decision"] == "ELIGIBLE"
    assert summary["procurement"]["VendorC"]["decision"] == "REJECTED"


def test_human_authorization_information_is_present():
    summary = run_demo_scenario(seed=42)
    assert "human_authorization" in summary
    auth = summary["human_authorization"]
    assert auth["status"] in ("AUTHORIZED", "PENDING", "OVERRIDE_PENDING_REVIEW")
    assert "authorizing_officer_id" in auth


def test_scale_up_information_is_present():
    summary = run_demo_scenario(seed=42)
    assert "scale_up" in summary
    scale = summary["scale_up"]
    assert "target_district" in scale
    assert "policy_case" in scale
    assert scale["scale_eligible"] is False  # Target resembles known failure hotspot for Vendor C


# ============================================================
# SECURITY & PRIVACY TESTS: NO PRIVATE LEAKS
# ============================================================

def _recursive_check_no_forbidden_keys(obj, path="root"):
    forbidden = {
        "private_parameters",
        "raw_seed",
        "seed",
        "seed_hash",
        "secret",
        "private_key",
        "api_key",
        "openai_api_key",
        "model_weights",
    }
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_lower = str(k).lower()
            for f in forbidden:
                assert f != k_lower, f"Forbidden key '{f}' found at '{path}.{k}'"
            _recursive_check_no_forbidden_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _recursive_check_no_forbidden_keys(item, f"{path}[{idx}]")


def test_public_summary_contains_no_private_parameters():
    summary = run_demo_scenario(seed=42)
    _recursive_check_no_forbidden_keys(summary)


def test_public_summary_json_contains_no_secrets():
    summary = run_demo_scenario(seed=42)
    json_str = json.dumps(summary).lower()
    for forbidden in ["private_parameters", "raw_seed", "seed_hash", "private_key", "api_key", "model_weights"]:
        assert forbidden not in json_str, f"Forbidden keyword '{forbidden}' leaked in serialized JSON"


# ============================================================
# API ENDPOINT TESTS
# ============================================================

def test_scenario_endpoint_works():
    response = client.get("/api/v1/demo/scenario")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "AXIOM-DEMO-001"
    assert len(data["vendors"]) == 3
    _recursive_check_no_forbidden_keys(data)


def test_demo_evaluation_endpoint_works():
    response = client.post("/api/v1/demo/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert "scenario" in data
    assert "outcome_contract" in data
    assert "pilot_twin" in data
    assert "evaluation" in data
    assert "vendors" in data
    assert "failure_maps" in data
    assert "diagnostics" in data
    assert "procurement" in data
    assert "scale_up" in data
    assert "human_authorization" in data
    assert len(data["vendors"]) == 3
    _recursive_check_no_forbidden_keys(data)


def test_demo_endpoint_works_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/api/v1/demo/evaluate")
    assert response.status_code == 200
    data = response.json()
    assert len(data["vendors"]) == 3
    # Check diagnostics analysis_mode is fallback
    for d in data["diagnostics"]:
        assert d["analysis_mode"] == "DETERMINISTIC_FALLBACK"


def test_repeated_execution_produces_consistent_results():
    res1 = run_demo_scenario(seed=42)
    res2 = run_demo_scenario(seed=42)

    # Structural consistency
    assert len(res1["vendors"]) == len(res2["vendors"]) == 3
    for i in range(3):
        assert res1["vendors"][i]["vendor_id"] == res2["vendors"][i]["vendor_id"]
        assert res1["vendors"][i]["accuracy"] == res2["vendors"][i]["accuracy"]
        assert res1["vendors"][i]["procurement_recommendation"] == res2["vendors"][i]["procurement_recommendation"]

    assert res1["procurement"] == res2["procurement"]
    assert res1["scale_up"]["policy_case"] == res2["scale_up"]["policy_case"]
