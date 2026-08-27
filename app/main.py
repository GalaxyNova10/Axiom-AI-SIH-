"""
Axiom AI Prototype API Service

FastAPI-powered lightweight demo API for interacting with the Axiom AI
evidence-governed innovation procurement platform.

Endpoints:
- GET /health
- POST /api/demo/run
- GET /api/demo/summary
"""

from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai.pipeline import run_axiom_demo, AxiomDemoResult

app = FastAPI(
    title="Axiom AI",
    description="Evidence-Governed Innovation Procurement Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cached latest run for summary endpoint
_latest_demo_result: Optional[AxiomDemoResult] = None

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "Axiom AI",
    }

@app.post("/api/demo/run")
def run_demo(problem_statement: Optional[str] = None, seed: int = 42) -> Dict[str, Any]:
    global _latest_demo_result
    ps = problem_statement or "Improve last-mile delivery of agricultural supplies across rural districts while reducing delivery delays."
    result = run_axiom_demo(problem_statement=ps, seed=seed)
    _latest_demo_result = result
    return result.to_public_dict()

@app.get("/api/demo/summary")
def get_demo_summary() -> Dict[str, Any]:
    global _latest_demo_result
    if _latest_demo_result is None:
        _latest_demo_result = run_axiom_demo()

    res = _latest_demo_result
    vendors_list = []
    for vid, vdata in res.vendor_results.items():
        vendors_list.append({
            "vendor_id": vid,
            "accuracy": vdata.get("accuracy"),
            "average_latency_ms": vdata.get("average_latency_ms"),
            "procurement_decision": res.procurement_decisions.get(vid, {}).get("decision"),
            "evidence_level": res.evidence_summary.get(vid, {}).get("evidence_level"),
        })

    all_hotspots = []
    for vid, fm in res.failure_map_summary.items():
        for hs in fm.get("hotspots", []):
            all_hotspots.append({
                "vendor_id": vid,
                "stratum_id": hs.get("stratum_id"),
                "severity": hs.get("severity"),
                "accuracy": hs.get("accuracy"),
                "reason": hs.get("reason"),
            })

    return {
        "contract": res.contract,
        "pilot_twin": res.pilot_twin,
        "vendors": vendors_list,
        "evidence_confidence": {vid: cdata.get("score") for vid, cdata in res.confidence_summary.items()},
        "failure_hotspots": all_hotspots,
        "procurement": res.procurement_decisions,
        "scale_up": res.scale_up_evaluation,
        "authorization": res.human_authorization,
    }
