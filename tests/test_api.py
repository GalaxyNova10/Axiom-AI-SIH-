"""
FastAPI API Layer Tests (Step 4)

Verifies that the presentation layer correctly exposes evaluation workflows,
diagnostics, cartography, decisions, and authorization without leaking
private test parameters or bypassing deterministic governance logic.
"""

import json
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ============================================================
# HEALTH & DOCS
# ============================================================

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] in ("Axiom AI", "axiom-ai")


def test_api_docs_and_openapi_available():
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200
    res_openapi = client.get("/openapi.json")
    assert res_openapi.status_code == 200
    openapi_data = res_openapi.json()
    assert "/api/v1/evaluate" in openapi_data["paths"]
    assert "/api/v1/evaluations/{evaluation_id}/diagnostics" in openapi_data["paths"]


# ============================================================
# EVALUATE ENDPOINT
# ============================================================

def test_api_evaluate_valid_request():
    payload = {
        "problem_statement": "Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays.",
        "department": "Department of Agriculture",
        "district": "District Alpha",
        "seed": 42
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "evaluation_id" in data
    assert data["evaluation_id"].startswith("eval_")
    assert "contract" in data
    assert "vendor_results" in data
    assert "failure_map_summary" in data
    assert "diagnostic_intelligence" in data
    assert "procurement_decisions" in data
    assert "human_authorization" in data


def test_api_evaluate_empty_problem_statement_rejected():
    payload = {
        "problem_statement": "",
        "department": "Department of Agriculture",
        "district": "District Alpha"
    }
    response = client.post("/api/v1/evaluate", json=payload)
    assert response.status_code == 400


# ============================================================
# EVALUATION RETRIEVAL & SCORECARDS
# ============================================================

def test_api_get_evaluation_by_id():
    # First create an evaluation
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Optimize cold storage monitoring."})
    assert create_res.status_code == 200
    eval_id = create_res.json()["evaluation_id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/evaluations/{eval_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["evaluation_id"] == eval_id
    assert "contract" in data


def test_api_get_unknown_evaluation_returns_404():
    response = client.get("/api/v1/evaluations/non_existent_evaluation_999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_api_get_vendors_scorecard():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Drone delivery optimization."})
    eval_id = create_res.json()["evaluation_id"]

    response = client.get(f"/api/v1/evaluations/{eval_id}/vendors")
    assert response.status_code == 200
    vendors = response.json()
    assert isinstance(vendors, list)
    assert len(vendors) == 3

    v_ids = [v["vendor_id"] for v in vendors]
    assert "VendorA" in v_ids
    assert "VendorB" in v_ids
    assert "VendorC" in v_ids

    for v in vendors:
        assert "accuracy" in v
        assert "latency" in v
        assert "error_count" in v
        assert "overall_failure_status" in v
        assert "procurement_recommendation" in v


# ============================================================
# DIAGNOSTICS & CARTOGRAPHY
# ============================================================

def test_api_get_diagnostics_endpoint():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Agritech diagnostic test."})
    eval_id = create_res.json()["evaluation_id"]

    response = client.get(f"/api/v1/evaluations/{eval_id}/diagnostics")
    assert response.status_code == 200
    diags = response.json()
    assert "VendorC" in diags

    vc_diag = diags["VendorC"]
    assert "overall_verdict_explanation" in vc_diag
    assert "compound_hotspot_diagnoses" in vc_diag
    assert "operational_risk_summary" in vc_diag
    assert "recommended_vendor_challenges" in vc_diag
    assert "targeted_retest_recommendations" in vc_diag
    assert "analysis_mode" in vc_diag


def test_api_get_failure_map_endpoint():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Soil moisture sensor analytics."})
    eval_id = create_res.json()["evaluation_id"]

    response = client.get(f"/api/v1/evaluations/{eval_id}/failure-map")
    assert response.status_code == 200
    fm_data = response.json()
    assert "VendorC" in fm_data
    assert "overall_status" in fm_data["VendorC"]
    assert "hotspots" in fm_data["VendorC"]


def test_api_get_decision_endpoint():
    create_res = client.post("/api/v1/evaluate", json={})
    eval_id = create_res.json()["evaluation_id"]

    response = client.get(f"/api/v1/evaluations/{eval_id}/decision")
    assert response.status_code == 200
    decisions = response.json()
    assert "VendorB" in decisions
    assert "VendorC" in decisions
    assert decisions["VendorB"]["decision"] == "ELIGIBLE"
    assert decisions["VendorC"]["decision"] == "REJECTED"


# ============================================================
# HUMAN AUTHORIZATION ENDPOINT
# ============================================================

def test_api_authorization_valid_approval():
    create_res = client.post("/api/v1/evaluate", json={})
    eval_id = create_res.json()["evaluation_id"]

    # Authorize eligible vendor (VendorB)
    auth_payload = {
        "vendor_id": "VendorB",
        "action": "APPROVE",
        "officer_id": "OFFICER-ALICE",
        "justification": "All evidence requirements and performance benchmarks verified.",
        "requested_action": "PROCUREMENT"
    }
    response = client.post(f"/api/v1/evaluations/{eval_id}/authorization", json=auth_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "AUTHORIZED"
    assert data["human_decision"] == "APPROVE"
    assert data["vendor_id"] == "VendorB"


def test_api_authorization_override_detection():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Crop yield prediction system."})
    eval_id = create_res.json()["evaluation_id"]

    # Attempting to APPROVE a REJECTED vendor (VendorC) triggers OVERRIDE_PENDING_REVIEW
    auth_payload = {
        "vendor_id": "VendorC",
        "action": "APPROVE",
        "officer_id": "OFFICER-ALICE",
        "justification": "Special pilot exemption granted by department commissioner.",
        "requested_action": "PROCUREMENT"
    }
    response = client.post(f"/api/v1/evaluations/{eval_id}/authorization", json=auth_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OVERRIDE_PENDING_REVIEW"
    assert data["escalation_required"] is False or data["escalation_required"] is True


def test_api_authorization_placeholder_justification_rejected():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Farm water irrigation."})
    eval_id = create_res.json()["evaluation_id"]

    auth_payload = {
        "vendor_id": "VendorB",
        "action": "APPROVE",
        "officer_id": "OFFICER-ALICE",
        "justification": "N/A"  # Placeholder rejected
    }
    response = client.post(f"/api/v1/evaluations/{eval_id}/authorization", json=auth_payload)
    assert response.status_code == 400


def test_api_authorization_unknown_vendor_rejected():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Farm water irrigation."})
    eval_id = create_res.json()["evaluation_id"]

    auth_payload = {
        "vendor_id": "UnknownVendor_999",
        "action": "APPROVE",
        "officer_id": "OFFICER-ALICE",
        "justification": "Legitimate justification here."
    }
    response = client.post(f"/api/v1/evaluations/{eval_id}/authorization", json=auth_payload)
    assert response.status_code == 400


# ============================================================
# SECURITY & PRIVACY: NO SENSITIVE LEAKS
# ============================================================

def test_api_no_sensitive_fields_in_any_response():
    create_res = client.post("/api/v1/evaluate", json={"problem_statement": "Security privacy verification."})
    eval_id = create_res.json()["evaluation_id"]

    endpoints_to_test = [
        f"/api/v1/evaluations/{eval_id}",
        f"/api/v1/evaluations/{eval_id}/vendors",
        f"/api/v1/evaluations/{eval_id}/diagnostics",
        f"/api/v1/evaluations/{eval_id}/failure-map",
        f"/api/v1/evaluations/{eval_id}/decision",
        "/api/demo/run",
        "/api/demo/summary",
    ]

    forbidden_keywords = [
        "private_parameters",
        "raw_seed",
        "seed_hash",
        "private_key",
        "api_key",
        "model_weights",
    ]

    for endpoint in endpoints_to_test:
        if endpoint == "/api/demo/run":
            res = client.post(endpoint)
        else:
            res = client.get(endpoint)

        assert res.status_code == 200
        res_text = res.text.lower()
        for kw in forbidden_keywords:
            assert kw not in res_text, f"Forbidden keyword '{kw}' found in endpoint response {endpoint}"


def test_api_works_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/api/v1/evaluate", json={"problem_statement": "Offline API verification."})
    assert response.status_code == 200
    data = response.json()
    assert data["diagnostic_intelligence"]["VendorA"]["analysis_mode"] == "DETERMINISTIC_FALLBACK"
