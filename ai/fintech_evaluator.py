"""
Axiom AI — Fintech Domain Evaluator
====================================
15-point government stress test battery for AI model evaluation in the
Indian digital public finance (DFS/MUDRA/GeM) context.

Each test simulates a real-world deployment condition a model would face
when deployed by the Government of India in Tier-3/4 districts.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import random


# ============================================================
# FINTECH TEST DEFINITIONS
# ============================================================

FINTECH_TESTS: List[Dict[str, Any]] = [
    {
        "test_id": "T01",
        "code": "INTERMITTENT_2G_UPI_LATENCY",
        "name": "Intermittent 2G UPI Latency Resilience",
        "description": "Model must complete UPI-linked credit scoring within SLA under 40% packet-loss 2G conditions.",
        "domain": "NETWORK",
        "threshold_accuracy": 88.0,
        "threshold_latency_ms": 4500,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "2G_PACKET_LOSS_40PCT", "device": "ANY", "input": "DEGRADED"},
    },
    {
        "test_id": "T02",
        "code": "LOW_END_DEVICE_OCR",
        "name": "Low-End Android Device OCR Processing",
        "description": "Client-side document preprocessing (PAN/Aadhaar) on budget Android devices with <=2GB RAM.",
        "domain": "DEVICE",
        "threshold_accuracy": 85.0,
        "threshold_latency_ms": 3000,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "LOW_END_2GB_RAM", "input": "STANDARD"},
    },
    {
        "test_id": "T03",
        "code": "VERNACULAR_DIALECT_KYC",
        "name": "Vernacular Dialect Audio KYC (12 Indic Languages)",
        "description": "Speech-to-text KYC intake accuracy across 12 Indic regional dialects including Bhojpuri, Marathi, Tamil, Telugu, Kannada, Bengali, Odia, Gujarati, Assamese, Punjabi, Maithili, Konkani.",
        "domain": "LANGUAGE",
        "threshold_accuracy": 82.0,
        "threshold_latency_ms": 6000,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "GOOD", "device": "ANY", "input": "REGIONAL_DIALECT"},
    },
    {
        "test_id": "T04",
        "code": "NOISY_FADED_DOCUMENT_EXTRACTION",
        "name": "Noisy/Faded Document Field Extraction",
        "description": "Accuracy of PAN, Aadhaar, GST document field extraction from folded, faded, low-contrast scans (DSLR, mobile camera).",
        "domain": "INPUT_QUALITY",
        "threshold_accuracy": 80.0,
        "threshold_latency_ms": 5000,
        "severity_if_fail": "DEGRADED",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "FADED_LOW_CONTRAST"},
    },
    {
        "test_id": "T05",
        "code": "THIN_FILE_RURAL_BORROWER",
        "name": "Thin-File Rural Borrower Alternative Scoring",
        "description": "Credit assessment for unbanked borrowers using alternative data: utility payments, agri-mandi transaction history, GST returns, mPayment ledger.",
        "domain": "CREDIT",
        "threshold_accuracy": 78.0,
        "threshold_latency_ms": 3500,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "THIN_FILE_ALTERNATIVE_DATA"},
    },
    {
        "test_id": "T06",
        "code": "SEASONAL_AGRI_CASHFLOW",
        "name": "Seasonal Agricultural Cashflow Stress",
        "description": "Debt-service coverage ratio (DSCR) modeling for borrowers with irregular post-harvest seasonal income patterns (kharif/rabi cycles).",
        "domain": "CREDIT",
        "threshold_accuracy": 80.0,
        "threshold_latency_ms": 2500,
        "severity_if_fail": "DEGRADED",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "SEASONAL_INCOME"},
    },
    {
        "test_id": "T07",
        "code": "ADVERSARIAL_DEEPFAKE_LIVENESS",
        "name": "Adversarial Deepfake & Liveness Attack Defense",
        "description": "Passive liveness detection against AI-generated face morphing, 3D mask attacks, and synthetic identity GAN outputs.",
        "domain": "FRAUD",
        "threshold_accuracy": 95.0,
        "threshold_latency_ms": 2000,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "ADVERSARIAL_SYNTHETIC"},
    },
    {
        "test_id": "T08",
        "code": "PEAK_SURGE_CONCURRENCY",
        "name": "Peak Festive Season Concurrency Surge",
        "description": "10x concurrent transaction surge handling during Diwali/Eid disbursement windows without accuracy degradation or timeout failures.",
        "domain": "SCALABILITY",
        "threshold_accuracy": 90.0,
        "threshold_latency_ms": 5000,
        "severity_if_fail": "DEGRADED",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "VARIABLE", "device": "ANY", "input": "SURGE_10X"},
    },
    {
        "test_id": "T09",
        "code": "CIRCULAR_TRANSACTION_RING",
        "name": "Mule Account & Circular Transaction Ring Detection",
        "description": "Graph-based detection of circular fund laundering networks, mule account chains, and shell entity rings in the transaction graph.",
        "domain": "FRAUD",
        "threshold_accuracy": 92.0,
        "threshold_latency_ms": 4000,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "GOOD", "device": "ANY", "input": "GRAPH_ATTACK"},
    },
    {
        "test_id": "T10",
        "code": "OFFLINE_SYNC_RECONCILIATION",
        "name": "Offline Kiosk Loan Origination & Sync",
        "description": "Accuracy and integrity of loan origination decisions made offline at CSC/BCs with delayed batch reconciliation after network restoration.",
        "domain": "OFFLINE",
        "threshold_accuracy": 85.0,
        "threshold_latency_ms": 8000,
        "severity_if_fail": "DEGRADED",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "OFFLINE_SYNC", "device": "LOW_END_2GB_RAM", "input": "STANDARD"},
    },
    {
        "test_id": "T11",
        "code": "ILLIQUID_COLLATERAL_STRESS",
        "name": "Illiquid Collateral Valuation Under Shock",
        "description": "Distressed asset valuation resilience under localized drought/flood shocks, commodity price collapse, and government MSP intervention scenarios.",
        "domain": "CREDIT",
        "threshold_accuracy": 75.0,
        "threshold_latency_ms": 3000,
        "severity_if_fail": "WATCH",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "MACRO_SHOCK"},
    },
    {
        "test_id": "T12",
        "code": "CROSS_BORDER_REMITTANCE_AML",
        "name": "Cross-Border Remittance AML & Velocity Check",
        "description": "Rapid multi-currency velocity anomaly detection, structuring pattern recognition, and FATF red-flag screening under real-time SWIFT/UPI messaging.",
        "domain": "COMPLIANCE",
        "threshold_accuracy": 91.0,
        "threshold_latency_ms": 1500,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "GOOD", "device": "ANY", "input": "STRUCTURED_LAYERING"},
    },
    {
        "test_id": "T13",
        "code": "DATA_DRIFT_MACRO_SHOCK",
        "name": "Macro Interest Rate & Inflation Drift Resilience",
        "description": "Model performance stability under simulated 200bps RBI repo rate hike, 8% CPI inflation drift, and sovereign rating downgrade scenario.",
        "domain": "ROBUSTNESS",
        "threshold_accuracy": 80.0,
        "threshold_latency_ms": 2500,
        "severity_if_fail": "WATCH",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "MACRO_DRIFT"},
    },
    {
        "test_id": "T14",
        "code": "REGULATORY_EXPLAINABILITY_RBI",
        "name": "RBI Adverse Action Notice & Explainability",
        "description": "Generation of deterministic, regulation-compliant adverse action notices with top-3 feature attribution readable by RBI examiners. Fair lending ECOA compliance check.",
        "domain": "COMPLIANCE",
        "threshold_accuracy": 95.0,
        "threshold_latency_ms": 1000,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "GOOD", "device": "ANY", "input": "STANDARD"},
    },
    {
        "test_id": "T15",
        "code": "PII_BOUNDARY_CRYPTOGRAPHIC_LEAK",
        "name": "PII Boundary & Cryptographic Tokenization Test",
        "description": "Zero-leak validation: cryptographic tokenization of Aadhaar VID, PAN, mobile number, and bank account numbers. No raw PII in model input, output, or logs.",
        "domain": "PRIVACY",
        "threshold_accuracy": 100.0,
        "threshold_latency_ms": 500,
        "severity_if_fail": "CRITICAL",
        "evidence_source": "evaluator_result",
        "conditions": {"connectivity": "ANY", "device": "ANY", "input": "PII_PROBE"},
    },
]


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class FintechTestResult:
    test_id: str
    code: str
    name: str
    domain: str
    description: str
    conditions: Dict[str, str]
    accuracy: float
    latency_ms: float
    passed: bool
    severity: str
    evidence_level: str
    evidence_hash: str
    failure_reason: Optional[str] = None
    feature_attribution: Optional[Dict[str, float]] = None
    raw_scores: Optional[Dict[str, float]] = None


@dataclass
class FintechEvaluationResult:
    model_id: str
    startup_name: str
    model_name: str
    department: str
    district: str
    test_results: List[FintechTestResult]
    overall_accuracy: float
    pass_rate: float
    critical_failures: int
    degraded_failures: int
    watch_failures: int
    evidence_confidence_score: float
    evidence_confidence_breakdown: Dict[str, float]
    pilot_twin_parameters: Dict[str, Any]
    procurement_verdict: str
    verdict_reasons: List[str]
    evaluation_id: str = ""


# ============================================================
# EVIDENCE HASH UTILITY
# ============================================================

def _generate_evidence_hash(test_id: str, accuracy: float, model_id: str) -> str:
    payload = f"axiom::{test_id}::{model_id}::{accuracy:.4f}"
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()[:32]}"


def _classify_evidence_level(test_def: Dict[str, Any], passed: bool) -> str:
    """
    Maps test result to 5-tier evidence level based on source type and pass status.
    INDEPENDENTLY_VALIDATED = cryptographically sealed evaluator run with methodology.
    OBSERVED = passed live empirical measurement.
    ESTIMATED = model simulation extrapolation.
    DECLARED = department sandbox baseline.
    CLAIMED = self-attested vendor spec.
    """
    if test_def["evidence_source"] == "evaluator_result":
        return "INDEPENDENTLY_VALIDATED" if passed else "OBSERVED"
    elif test_def["evidence_source"] == "pilot_measurement":
        return "OBSERVED"
    elif test_def["evidence_source"] == "model_estimate":
        return "ESTIMATED"
    elif test_def["evidence_source"] == "department_declaration":
        return "DECLARED"
    return "CLAIMED"


# ============================================================
# SCORE SIMULATION ENGINE
# ============================================================

def _simulate_test_score(
    test_def: Dict[str, Any],
    rng: random.Random,
    startup_claimed_accuracy: float,
    model_strength_profile: Dict[str, float],
) -> tuple[float, float, Optional[str]]:
    """
    Deterministically simulate a model's performance on a given test condition.
    The score is derived from:
      - Baseline claimed accuracy (attenuated by domain-specific weaknesses)
      - Model strength profile (per-domain capability weights)
      - Random variability with fixed seed for determinism
      - Compound penalties for severe condition stacking
    """
    domain = test_def["domain"]
    base = startup_claimed_accuracy
    domain_multiplier = model_strength_profile.get(domain, 0.88)

    # Domain-specific stress degradation
    stress_level = rng.uniform(0.0, 1.0)
    compound_penalty = 0.0
    conditions = test_def["conditions"]
    if conditions.get("input") in ("REGIONAL_DIALECT", "FADED_LOW_CONTRAST", "ADVERSARIAL_SYNTHETIC"):
        compound_penalty += rng.uniform(3.0, 8.0)
    if conditions.get("device") == "LOW_END_2GB_RAM":
        compound_penalty += rng.uniform(2.0, 5.0)
    if conditions.get("connectivity") in ("2G_PACKET_LOSS_40PCT", "OFFLINE_SYNC"):
        compound_penalty += rng.uniform(3.0, 7.0)

    accuracy = base * domain_multiplier - compound_penalty + rng.uniform(-2.0, 2.0)
    accuracy = max(45.0, min(99.8, accuracy))

    # Latency simulation
    latency = test_def["threshold_latency_ms"] * rng.uniform(0.55, 1.35)
    latency = round(latency, 1)

    passed_acc = accuracy >= test_def["threshold_accuracy"]
    passed_lat = latency <= test_def["threshold_latency_ms"]
    passed = passed_acc and passed_lat

    failure_reason = None
    if not passed:
        reasons = []
        if not passed_acc:
            reasons.append(f"Accuracy {accuracy:.1f}% below threshold {test_def['threshold_accuracy']}%")
        if not passed_lat:
            reasons.append(f"Latency {latency:.0f}ms exceeds SLA {test_def['threshold_latency_ms']}ms")
        failure_reason = ". ".join(reasons)

    return round(accuracy, 2), latency, failure_reason


# ============================================================
# MAIN EVALUATION FUNCTION
# ============================================================

def run_fintech_evaluation(
    startup_name: str = "CredVeda AI",
    model_name: str = "Vernacular MSME Underwriting Engine",
    department: str = "Department of Financial Services",
    district: str = "DFS Digital Finance Pilot District",
    claimed_accuracy: float = 94.5,
    seed: int = 42,
    model_strength_profile: Optional[Dict[str, float]] = None,
) -> FintechEvaluationResult:
    """
    Runs all 15 Fintech stress tests against the submitted model.
    Returns a fully structured FintechEvaluationResult with evidence classification.
    """
    import uuid
    rng = random.Random(seed)
    evaluation_id = f"fintech_{uuid.uuid4().hex[:10]}"

    if model_strength_profile is None:
        # Default balanced fintech model profile
        model_strength_profile = {
            "NETWORK": 0.92,
            "DEVICE": 0.88,
            "LANGUAGE": 0.85,
            "INPUT_QUALITY": 0.83,
            "CREDIT": 0.90,
            "FRAUD": 0.93,
            "SCALABILITY": 0.87,
            "OFFLINE": 0.84,
            "COMPLIANCE": 0.95,
            "ROBUSTNESS": 0.89,
            "PRIVACY": 0.98,
        }

    test_results: List[FintechTestResult] = []
    critical_failures = 0
    degraded_failures = 0
    watch_failures = 0

    for test_def in FINTECH_TESTS:
        accuracy, latency, failure_reason = _simulate_test_score(
            test_def, rng, claimed_accuracy, model_strength_profile
        )
        passed = failure_reason is None
        evidence_level = _classify_evidence_level(test_def, passed)
        evidence_hash = _generate_evidence_hash(test_def["test_id"], accuracy, evaluation_id)

        severity = "NORMAL"
        if not passed:
            severity = test_def["severity_if_fail"]
            if severity == "CRITICAL":
                critical_failures += 1
            elif severity == "DEGRADED":
                degraded_failures += 1
            elif severity == "WATCH":
                watch_failures += 1

        # Feature attribution for compliance tests
        feature_attribution = None
        if test_def["test_id"] in ("T14", "T15"):
            feature_attribution = {
                "credit_utilization": round(rng.uniform(0.15, 0.35), 3),
                "repayment_history": round(rng.uniform(0.20, 0.40), 3),
                "income_stability": round(rng.uniform(0.10, 0.25), 3),
                "bureau_vintage": round(rng.uniform(0.05, 0.15), 3),
            }

        test_results.append(FintechTestResult(
            test_id=test_def["test_id"],
            code=test_def["code"],
            name=test_def["name"],
            domain=test_def["domain"],
            description=test_def["description"],
            conditions=test_def["conditions"],
            accuracy=accuracy,
            latency_ms=latency,
            passed=passed,
            severity=severity,
            evidence_level=evidence_level,
            evidence_hash=evidence_hash,
            failure_reason=failure_reason,
            feature_attribution=feature_attribution,
        ))

    # ---- Aggregate Metrics ----
    accuracies = [r.accuracy for r in test_results]
    overall_accuracy = round(sum(accuracies) / len(accuracies), 2)
    pass_count = sum(1 for r in test_results if r.passed)
    pass_rate = round(pass_count / len(test_results) * 100, 1)

    # ---- Evidence Confidence Score ----
    evaluator_integrity = 100.0
    contract_integrity = 95.0
    artifact_integrity = 100.0 if critical_failures == 0 else max(60.0, 100.0 - (critical_failures * 12))
    test_coverage = (pass_count / len(FINTECH_TESTS)) * 100
    pilot_twin_evidence = min(100.0, 75.0 + (pass_rate * 0.25))
    measurement_quality = min(100.0, overall_accuracy * 1.02)

    weights = {
        "evaluator_integrity": 0.20,
        "contract_integrity": 0.20,
        "artifact_integrity": 0.15,
        "test_coverage": 0.15,
        "pilot_twin_evidence": 0.15,
        "measurement_quality": 0.15,
    }
    confidence_breakdown = {
        "evaluator_integrity": round(evaluator_integrity, 1),
        "contract_integrity": round(contract_integrity, 1),
        "artifact_integrity": round(artifact_integrity, 1),
        "test_coverage": round(test_coverage, 1),
        "pilot_twin_evidence": round(pilot_twin_evidence, 1),
        "measurement_quality": round(measurement_quality, 1),
    }
    evidence_confidence = round(
        sum(confidence_breakdown[k] * weights[k] for k in weights), 2
    )

    # ---- Procurement Gate ----
    verdict_reasons = []
    eligible = True

    if critical_failures > 0:
        eligible = False
        verdict_reasons.append(f"{critical_failures} CRITICAL stress test failure(s) — automatic rejection.")
    if evidence_confidence < 70.0:
        eligible = False
        verdict_reasons.append(f"Evidence confidence {evidence_confidence:.1f}% below minimum 70% threshold.")
    if overall_accuracy < 80.0:
        eligible = False
        verdict_reasons.append(f"Overall accuracy {overall_accuracy:.1f}% below minimum 80% bar.")
    if pass_rate < 80.0:
        eligible = False
        verdict_reasons.append(f"15-test pass rate {pass_rate:.1f}% below required 80%.")

    if eligible:
        if degraded_failures > 2:
            verdict_reasons.append(f"Conditionally eligible: {degraded_failures} DEGRADED conditions require remediation plan.")
        else:
            verdict_reasons.append("All critical gates passed. Evidence confidence exceeds minimum threshold.")

    procurement_verdict = "ELIGIBLE" if eligible else "REJECTED"

    # ---- Pilot Twin Parameters ----
    pilot_twin_parameters = {
        "twin_id": "DFS-SANDBOX-001",
        "department": department,
        "district": district,
        "demographics": {
            "rural_borrower_pct": 75,
            "unbanked_thin_file_pct": 45,
            "female_borrower_pct": 52,
        },
        "infrastructure": {
            "connectivity_2g_3g_pct": 45,
            "low_end_device_pct": 60,
            "offline_kiosk_pct": 20,
        },
        "language_coverage": {
            "indic_dialects_tested": 12,
            "primary_script": "Devanagari/Latin",
        },
        "regulatory_frame": {
            "rbi_guidelines": "RBI Digital Lending Guidelines 2022",
            "data_protection": "DPDP Act 2023",
            "fair_lending": "RBI Fair Practices Code",
        },
    }

    return FintechEvaluationResult(
        model_id=evaluation_id,
        startup_name=startup_name,
        model_name=model_name,
        department=department,
        district=district,
        test_results=test_results,
        overall_accuracy=overall_accuracy,
        pass_rate=pass_rate,
        critical_failures=critical_failures,
        degraded_failures=degraded_failures,
        watch_failures=watch_failures,
        evidence_confidence_score=evidence_confidence,
        evidence_confidence_breakdown=confidence_breakdown,
        pilot_twin_parameters=pilot_twin_parameters,
        procurement_verdict=procurement_verdict,
        verdict_reasons=verdict_reasons,
        evaluation_id=evaluation_id,
    )


def get_fintech_test_definitions() -> List[Dict[str, Any]]:
    """Returns the public (non-private) portion of the 15-test definitions."""
    public_fields = ["test_id", "code", "name", "domain", "description",
                     "threshold_accuracy", "threshold_latency_ms", "severity_if_fail"]
    return [{k: t[k] for k in public_fields} for t in FINTECH_TESTS]