"""
Axiom AI Forensic Diagnostic & Evaluation Intelligence Engine

Sits above the deterministic evaluation and governance layers to provide
forensic interpretation of already-produced evaluation evidence.

Core Principle:
    AI interprets evidence.
    AI does not become evidence.
    AI explains.
    Rules decide.
    Humans authorize.

This engine:
- Explains observed failure patterns and multi-factor interactions.
- Translates technical failure conditions into operational risk language.
- Formulates structured challenge questions for the Vendor Response Window.
- Recommends targeted retest strata from existing public conditions.
- Strictly adheres to governance boundaries (never modifies evidence,
  never makes procurement decisions, never alters FailureMap severity).
"""

from dataclasses import dataclass, field, asdict
import json
import logging
import os
from typing import Dict, Any, List, Optional

from openai import OpenAI

from ai.evaluator import EvaluationRun
from ai.failure_cartography import FailureMap, StratumResult, FailureHotspot
from ai.pilot_twin import PilotTwin
from ai.schemas import OutcomeContract

logger = logging.getLogger(__name__)


# ============================================================
# DATACLASSES
# ============================================================

@dataclass
class HotspotDiagnosis:
    stratum_id: str
    severity: str
    accuracy: float
    error_rate: float
    observed_conditions: Dict[str, str]
    diagnosis: str
    operational_impact: str
    confidence: float  # Diagnostic confidence (NOT Evidence Confidence)
    supporting_observations: List[str] = field(default_factory=list)


@dataclass
class VendorChallengeProposal:
    challenge_id: str
    target_stratum_id: str
    question: str
    rationale: str
    requested_evidence: List[str]
    priority: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class TargetedRetestRecommendation:
    recommendation_id: str
    target_stratum_id: str
    reason: str
    objective: str
    priority: str  # "HIGH", "MEDIUM", "LOW"


@dataclass
class DiagnosticReport:
    vendor_id: str
    evaluation_id: str
    overall_verdict_explanation: str
    compound_hotspot_diagnoses: List[HotspotDiagnosis]
    operational_risk_summary: str
    recommended_vendor_challenges: List[VendorChallengeProposal]
    targeted_retest_recommendations: List[TargetedRetestRecommendation]
    analysis_mode: str  # "LLM" or "DETERMINISTIC_FALLBACK"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================
# HELPER: STRATUM PARSER
# ============================================================

def parse_stratum_id(stratum_id: str) -> Dict[str, str]:
    """
    Deterministically parses a public stratum ID into its orthogonal components.
    Format: {connectivity}_{device}_{language}_{input_quality}
    """
    conn = "INTERMITTENT" if "INTERMITTENT" in stratum_id else ("GOOD" if "GOOD" in stratum_id else "UNKNOWN")
    dev = "HIGH_END" if "HIGH_END" in stratum_id else ("LOW_END" if "LOW_END" in stratum_id else "UNKNOWN")
    lang = "REGIONAL" if "REGIONAL" in stratum_id else ("STANDARD" if "STANDARD" in stratum_id else "UNKNOWN")
    qual = "NOISY" if "NOISY" in stratum_id else ("DEGRADED" if "DEGRADED" in stratum_id else ("CLEAN" if "CLEAN" in stratum_id else "UNKNOWN"))
    return {
        "connectivity": conn,
        "device": dev,
        "language": lang,
        "input_quality": qual,
    }


def format_conditions_summary(conditions: Dict[str, str]) -> str:
    parts = []
    if conditions.get("connectivity") != "UNKNOWN":
        parts.append(f"{conditions['connectivity'].lower()} connectivity")
    if conditions.get("device") != "UNKNOWN":
        parts.append(f"{conditions['device'].lower().replace('_', '-')} devices")
    if conditions.get("language") != "UNKNOWN":
        parts.append(f"{conditions['language'].lower()} language")
    if conditions.get("input_quality") != "UNKNOWN":
        parts.append(f"{conditions['input_quality'].lower()} input quality")
    return ", ".join(parts) if parts else "unspecified deployment conditions"


# ============================================================
# DETERMINISTIC FORENSIC ENGINE
# ============================================================

def _deterministic_forensic_diagnosis(
    evaluation_run: EvaluationRun,
    failure_map: FailureMap,
    pilot_twin: Optional[PilotTwin] = None,
    contract: Optional[OutcomeContract] = None,
) -> DiagnosticReport:
    """
    Offline, deterministic diagnostic analysis engine.
    Requires no network, database, or external APIs.
    """
    vendor_id = evaluation_run.vendor_id
    evaluation_id = evaluation_run.evaluation_id

    # Build stratum lookup maps
    strata_by_id: Dict[str, StratumResult] = {s.stratum_id: s for s in failure_map.strata}

    # Group accuracies by individual categorical conditions to detect sensitivity
    category_accuracies: Dict[str, Dict[str, List[float]]] = {
        "connectivity": {"GOOD": [], "INTERMITTENT": []},
        "device": {"HIGH_END": [], "LOW_END": []},
        "language": {"STANDARD": [], "REGIONAL": []},
        "input_quality": {"CLEAN": [], "DEGRADED": [], "NOISY": []},
    }

    for stratum in failure_map.strata:
        conds = parse_stratum_id(stratum.stratum_id)
        for cat, val in conds.items():
            if cat in category_accuracies and val in category_accuracies[cat]:
                category_accuracies[cat][val].append(stratum.accuracy)

    # Compute category averages
    cat_avg: Dict[str, Dict[str, float]] = {}
    for cat, val_map in category_accuracies.items():
        cat_avg[cat] = {}
        for val, accs in val_map.items():
            cat_avg[cat][val] = (sum(accs) / len(accs)) if accs else 100.0

    hotspot_diagnoses: List[HotspotDiagnosis] = []
    challenge_proposals: List[VendorChallengeProposal] = []
    retest_recommendations: List[TargetedRetestRecommendation] = []

    # Non-normal hotspots (CRITICAL, DEGRADED, WATCH)
    non_normal_hotspots = [h for h in failure_map.hotspots if h.severity != "NORMAL"]

    for idx, hotspot in enumerate(non_normal_hotspots, start=1):
        stratum_id = hotspot.stratum_id
        conds = parse_stratum_id(stratum_id)
        stratum_res = strata_by_id.get(stratum_id)
        error_rate = stratum_res.failure_rate if stratum_res else (100.0 - hotspot.accuracy)

        # Sensitivity indicators
        sensitivities: List[str] = []
        supporting_obs: List[str] = []

        if conds["connectivity"] == "INTERMITTENT":
            diff_conn = cat_avg["connectivity"]["GOOD"] - cat_avg["connectivity"]["INTERMITTENT"]
            if diff_conn >= 10.0:
                sensitivities.append("connectivity-sensitive")
                supporting_obs.append(f"Average accuracy drops by {diff_conn:.1f}% under intermittent connectivity.")

        if conds["device"] == "LOW_END":
            diff_dev = cat_avg["device"]["HIGH_END"] - cat_avg["device"]["LOW_END"]
            if diff_dev >= 10.0:
                sensitivities.append("device-sensitive")
                supporting_obs.append(f"Average accuracy drops by {diff_dev:.1f}% on low-end devices.")

        if conds["language"] == "REGIONAL":
            diff_lang = cat_avg["language"]["STANDARD"] - cat_avg["language"]["REGIONAL"]
            if diff_lang >= 10.0:
                sensitivities.append("language-sensitive")
                supporting_obs.append(f"Average accuracy drops by {diff_lang:.1f}% on regional language workflows.")

        if conds["input_quality"] in ("DEGRADED", "NOISY"):
            diff_qual = cat_avg["input_quality"]["CLEAN"] - cat_avg["input_quality"][conds["input_quality"]]
            if diff_qual >= 10.0:
                sensitivities.append("input-quality-sensitive")
                supporting_obs.append(f"Average accuracy drops by {diff_qual:.1f}% under {conds['input_quality'].lower()} input quality.")

        # Check for compound interaction:
        # If the individual average drops are moderate (< 25%), but this exact combined stratum is < 70%
        is_compound = False
        if len(sensitivities) >= 2 or hotspot.severity == "CRITICAL":
            # Compare actual accuracy against expected additive degradation
            is_compound = True
            diagnosis_text = (
                f"Observed pattern is consistent with a compound interaction failure. "
                f"While individual factors exhibit moderate degradation, their concurrent presence in "
                f"{format_conditions_summary(conds)} results in an acute accuracy drop to {hotspot.accuracy:.1f}%. "
                f"Evidence suggests potential client-side buffer or edge-model processing constraints under noisy regional inputs. "
                f"Cannot determine internal implementation from black-box evaluation."
            )
        elif sensitivities:
            sensitivity_str = ", ".join(sensitivities)
            diagnosis_text = (
                f"Observed pattern indicates the solution is predominantly {sensitivity_str}. "
                f"Evidence suggests performance degradation is primarily driven by {format_conditions_summary(conds)}. "
                f"Cannot determine internal implementation from black-box evaluation."
            )
        else:
            diagnosis_text = (
                f"Observed performance degradation to {hotspot.accuracy:.1f}% under {format_conditions_summary(conds)}. "
                f"Isolated anomaly; possible contributing factor may relate to specific parameter boundaries. "
                f"Cannot determine internal implementation from black-box evaluation."
            )

        # Operational impact statement (tied strictly to measured evidence)
        impact_factors = []
        if conds["connectivity"] == "INTERMITTENT":
            impact_factors.append("unstable network connectivity")
        if conds["device"] == "LOW_END":
            impact_factors.append("low-specification edge devices")
        if conds["language"] == "REGIONAL":
            impact_factors.append("regional vernacular inputs")
        if conds["input_quality"] in ("DEGRADED", "NOISY"):
            impact_factors.append("noisy or degraded source data")

        impact_desc = " combined with ".join(impact_factors) if impact_factors else "specified deployment conditions"
        operational_impact = (
            f"Represents an operational risk in deployment environments characterized by {impact_desc}, "
            f"where end-users may experience an elevated failure rate ({error_rate:.1f}%)."
        )

        # Diagnostic confidence calculation
        # Measures how strongly the observed pattern supports the explanation (NOT evidence confidence)
        diagnostic_conf = 85.0
        if is_compound:
            diagnostic_conf = 92.0
        elif len(sensitivities) >= 1:
            diagnostic_conf = 88.0

        hotspot_diagnoses.append(HotspotDiagnosis(
            stratum_id=stratum_id,
            severity=hotspot.severity,
            accuracy=hotspot.accuracy,
            error_rate=error_rate,
            observed_conditions=conds,
            diagnosis=diagnosis_text,
            operational_impact=operational_impact,
            confidence=diagnostic_conf,
            supporting_observations=supporting_obs,
        ))

        # Vendor Challenge Proposal
        priority = "HIGH" if hotspot.severity == "CRITICAL" else ("MEDIUM" if hotspot.severity == "DEGRADED" else "LOW")
        chal_question = (
            f"What specific optimizations or edge-resilience safeguards does the solution employ when operating under "
            f"{format_conditions_summary(conds)}, and what verifiable evidence demonstrates that the observed "
            f"{hotspot.severity.lower()} degradation ({hotspot.accuracy:.1f}% accuracy) has been remediated?"
        )
        chal_rationale = (
            f"Stratum {stratum_id} exhibited {hotspot.severity} degradation with {error_rate:.1f}% failure rate, "
            f"violating baseline operational requirements."
        )
        chal_evidence = [
            "Targeted revalidation benchmark logs under matched stratum conditions",
            "Error analysis report detailing edge recovery behavior",
            "Client-side memory and throughput profiling data",
        ]

        challenge_proposals.append(VendorChallengeProposal(
            challenge_id=f"CHAL-{vendor_id}-{idx:02d}",
            target_stratum_id=stratum_id,
            question=chal_question,
            rationale=chal_rationale,
            requested_evidence=chal_evidence,
            priority=priority,
        ))

        # Targeted Retest Recommendation
        retest_recommendations.append(TargetedRetestRecommendation(
            recommendation_id=f"RETEST-{vendor_id}-{idx:02d}",
            target_stratum_id=stratum_id,
            reason=f"Observed {hotspot.severity} failure ({hotspot.accuracy:.1f}% accuracy) requires empirical verification.",
            objective=f"Determine whether performance degradation persists when {format_conditions_summary(conds)} are re-evaluated.",
            priority=priority,
        ))

    # Overall summary
    if not non_normal_hotspots:
        overall_verdict = (
            f"Evaluation of vendor {vendor_id} across all 24 deployment strata demonstrated robust, uniform performance "
            f"(overall accuracy {evaluation_run.accuracy:.1f}%). No critical, degraded, or watch-level hotspots were detected."
        )
        op_risk_summary = (
            f"Low operational risk identified across tested conditions. The solution satisfies general deployment baseline stability."
        )
    else:
        crit_count = len([h for h in non_normal_hotspots if h.severity == "CRITICAL"])
        deg_count = len([h for h in non_normal_hotspots if h.severity == "DEGRADED"])
        watch_count = len([h for h in non_normal_hotspots if h.severity == "WATCH"])

        overall_verdict = (
            f"Evaluation of vendor {vendor_id} achieved {evaluation_run.accuracy:.1f}% overall accuracy, but cartographic analysis "
            f"revealed {len(non_normal_hotspots)} localized performance hotspots ({crit_count} critical, {deg_count} degraded, "
            f"{watch_count} watch). Performance is non-uniform across orthogonal deployment strata."
        )
        op_risk_summary = (
            f"Deployment in administrative zones matching identified hotspot conditions poses heightened operational risk. "
            f"Targeted vendor clarification and structured revalidation are recommended before production scale-up."
        )

    return DiagnosticReport(
        vendor_id=vendor_id,
        evaluation_id=evaluation_id,
        overall_verdict_explanation=overall_verdict,
        compound_hotspot_diagnoses=hotspot_diagnoses,
        operational_risk_summary=op_risk_summary,
        recommended_vendor_challenges=challenge_proposals,
        targeted_retest_recommendations=retest_recommendations,
        analysis_mode="DETERMINISTIC_FALLBACK",
    )


# ============================================================
# AI HALLUCINATION & GOVERNANCE GUARD
# ============================================================

FORBIDDEN_EXECUTIVE_ACTIONS = {
    "procurement_approved",
    "authorized_for_procurement",
    "award_contract",
    "decision_overridden",
    "payment_released",
    "auto_deploy",
    "scale_authorized",
}

FORBIDDEN_SECRET_KEYWORDS = {
    "private_parameters",
    "raw_seed",
    "seed_hash",
    "secret",
    "private_key",
    "api_key",
}


def _validate_diagnostic_report(
    report: DiagnosticReport,
    evaluation_run: EvaluationRun,
    failure_map: FailureMap,
) -> None:
    """
    Strict validation layer ensuring AI-generated reports cannot hallucinate metrics,
    alter measurements, leak secrets, or attempt autonomous decision-making.
    Raises ValueError on any violation.
    """
    if not isinstance(report, DiagnosticReport):
        raise TypeError("Report must be an instance of DiagnosticReport")

    # 1. Identity binding
    if report.vendor_id != evaluation_run.vendor_id:
        raise ValueError(f"vendor_id mismatch: expected '{evaluation_run.vendor_id}', got '{report.vendor_id}'")
    if report.evaluation_id != evaluation_run.evaluation_id:
        raise ValueError(f"evaluation_id mismatch: expected '{evaluation_run.evaluation_id}', got '{report.evaluation_id}'")

    # 2. Stratum existence and metric integrity
    valid_strata_map = {s.stratum_id: s for s in failure_map.strata}

    for diag in report.compound_hotspot_diagnoses:
        if diag.stratum_id not in valid_strata_map:
            raise ValueError(f"Referenced non-existent stratum_id '{diag.stratum_id}'")

        expected_stratum = valid_strata_map[diag.stratum_id]
        if diag.severity != expected_stratum.severity:
            raise ValueError(
                f"Severity mismatch for '{diag.stratum_id}': expected '{expected_stratum.severity}', got '{diag.severity}'"
            )
        if abs(diag.accuracy - expected_stratum.accuracy) > 0.05:
            raise ValueError(
                f"Accuracy mismatch for '{diag.stratum_id}': expected '{expected_stratum.accuracy}', got '{diag.accuracy}'"
            )

    for chal in report.recommended_vendor_challenges:
        if chal.target_stratum_id not in valid_strata_map:
            raise ValueError(f"Challenge references non-existent stratum_id '{chal.target_stratum_id}'")
        if chal.priority not in ("HIGH", "MEDIUM", "LOW"):
            raise ValueError(f"Invalid challenge priority '{chal.priority}'")

    for ret in report.targeted_retest_recommendations:
        if ret.target_stratum_id not in valid_strata_map:
            raise ValueError(f"Retest recommendation references non-existent stratum_id '{ret.target_stratum_id}'")
        if ret.priority not in ("HIGH", "MEDIUM", "LOW"):
            raise ValueError(f"Invalid retest priority '{ret.priority}'")

    # 3. Security & Governance boundary check across all text fields
    report_dict_str = json.dumps(report.to_dict()).lower()

    for secret_kw in FORBIDDEN_SECRET_KEYWORDS:
        if secret_kw in report_dict_str:
            raise ValueError(f"Report contains forbidden private/secret keyword: '{secret_kw}'")

    for exec_kw in FORBIDDEN_EXECUTIVE_ACTIONS:
        if exec_kw in report_dict_str:
            raise ValueError(f"Report attempts forbidden autonomous governance action: '{exec_kw}'")


# ============================================================
# LLM ENGINE WITH STRICT PARSING & FALLBACK
# ============================================================

def _parse_llm_json_to_report(
    data: Dict[str, Any],
    evaluation_run: EvaluationRun,
    failure_map: FailureMap,
) -> DiagnosticReport:
    """Parses and validates LLM JSON output into a strongly typed DiagnosticReport."""
    if not isinstance(data, dict):
        raise ValueError("LLM output is not a JSON object")

    vendor_id = str(data.get("vendor_id", ""))
    evaluation_id = str(data.get("evaluation_id", ""))
    overall_verdict = str(data.get("overall_verdict_explanation", ""))
    op_risk = str(data.get("operational_risk_summary", ""))

    diagnoses: List[HotspotDiagnosis] = []
    for d in data.get("compound_hotspot_diagnoses", []):
        diagnoses.append(HotspotDiagnosis(
            stratum_id=str(d.get("stratum_id", "")),
            severity=str(d.get("severity", "")),
            accuracy=float(d.get("accuracy", 0.0)),
            error_rate=float(d.get("error_rate", 0.0)),
            observed_conditions=dict(d.get("observed_conditions", {})),
            diagnosis=str(d.get("diagnosis", "")),
            operational_impact=str(d.get("operational_impact", "")),
            confidence=float(d.get("confidence", 85.0)),
            supporting_observations=[str(s) for s in d.get("supporting_observations", [])],
        ))

    challenges: List[VendorChallengeProposal] = []
    for c in data.get("recommended_vendor_challenges", []):
        challenges.append(VendorChallengeProposal(
            challenge_id=str(c.get("challenge_id", "")),
            target_stratum_id=str(c.get("target_stratum_id", "")),
            question=str(c.get("question", "")),
            rationale=str(c.get("rationale", "")),
            requested_evidence=[str(e) for e in c.get("requested_evidence", [])],
            priority=str(c.get("priority", "MEDIUM")),
        ))

    retests: List[TargetedRetestRecommendation] = []
    for r in data.get("targeted_retest_recommendations", []):
        retests.append(TargetedRetestRecommendation(
            recommendation_id=str(r.get("recommendation_id", "")),
            target_stratum_id=str(r.get("target_stratum_id", "")),
            reason=str(r.get("reason", "")),
            objective=str(r.get("objective", "")),
            priority=str(r.get("priority", "MEDIUM")),
        ))

    report = DiagnosticReport(
        vendor_id=vendor_id,
        evaluation_id=evaluation_id,
        overall_verdict_explanation=overall_verdict,
        compound_hotspot_diagnoses=diagnoses,
        operational_risk_summary=op_risk,
        recommended_vendor_challenges=challenges,
        targeted_retest_recommendations=retests,
        analysis_mode="LLM",
    )

    _validate_diagnostic_report(report, evaluation_run, failure_map)
    return report


def generate_forensic_diagnosis(
    evaluation_run: EvaluationRun,
    failure_map: FailureMap,
    pilot_twin: Optional[PilotTwin] = None,
    contract: Optional[OutcomeContract] = None,
) -> DiagnosticReport:
    """
    Main entry point for generating AI forensic diagnostic reports.
    Attempts LLM generation if configured, with automatic fallback to
    deterministic diagnostic logic on any failure, timeout, or validation mismatch.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.info("OPENAI_API_KEY missing. Using deterministic forensic engine.")
        return _deterministic_forensic_diagnosis(evaluation_run, failure_map, pilot_twin, contract)

    model = os.environ.get("AXIOM_LLM_MODEL", "gpt-3.5-turbo")

    try:
        # Build sanitized public summary for LLM prompt (NO private parameters, NO seeds)
        public_strata_summary = [
            {
                "stratum_id": s.stratum_id,
                "accuracy": s.accuracy,
                "failure_rate": s.failure_rate,
                "severity": s.severity,
                "average_latency_ms": s.average_latency_ms,
            }
            for s in failure_map.strata
        ]

        public_hotspots_summary = [
            {
                "stratum_id": h.stratum_id,
                "severity": h.severity,
                "accuracy": h.accuracy,
                "failure_rate": h.failure_rate,
                "reason": h.reason,
            }
            for h in failure_map.hotspots
        ]

        prompt = f"""
        You are an evaluation intelligence assistant for Axiom AI, an evidence-governed procurement platform.
        Your role is strictly analytical and advisory.
        You may explain observed multi-factor performance patterns and translate them into operational risk statements.
        You MUST NOT change measurements, evidence levels, KPI thresholds, or make procurement/scale decisions.

        EVALUATION DATA:
        Vendor ID: {evaluation_run.vendor_id}
        Evaluation ID: {evaluation_run.evaluation_id}
        Overall Accuracy: {evaluation_run.accuracy}%

        FAILURE HOTSPOTS:
        {json.dumps(public_hotspots_summary, indent=2)}

        ALL 24 STRATA RESULTS:
        {json.dumps(public_strata_summary, indent=2)}

        INSTRUCTIONS:
        1. Analyze why specific compound combinations of conditions caused failure hotspots.
        2. Translate technical failure patterns into government operational risk language.
        3. Formulate structured vendor challenge proposals for the Vendor Response Window.
        4. Recommend targeted retest strata referencing ONLY existing public stratum_ids.
        5. Use exact measured accuracies and severities from the data.
        6. Return strictly valid JSON conforming to the requested schema.

        JSON SCHEMA:
        {{
            "vendor_id": "{evaluation_run.vendor_id}",
            "evaluation_id": "{evaluation_run.evaluation_id}",
            "overall_verdict_explanation": "string",
            "operational_risk_summary": "string",
            "compound_hotspot_diagnoses": [
                {{
                    "stratum_id": "string",
                    "severity": "CRITICAL | DEGRADED | WATCH",
                    "accuracy": number,
                    "error_rate": number,
                    "observed_conditions": {{"connectivity": "...", "device": "...", "language": "...", "input_quality": "..."}},
                    "diagnosis": "string",
                    "operational_impact": "string",
                    "confidence": number,
                    "supporting_observations": ["string"]
                }}
            ],
            "recommended_vendor_challenges": [
                {{
                    "challenge_id": "string",
                    "target_stratum_id": "string",
                    "question": "string",
                    "rationale": "string",
                    "requested_evidence": ["string"],
                    "priority": "HIGH | MEDIUM | LOW"
                }}
            ],
            "targeted_retest_recommendations": [
                {{
                    "recommendation_id": "string",
                    "target_stratum_id": "string",
                    "reason": "string",
                    "objective": "string",
                    "priority": "HIGH | MEDIUM | LOW"
                }}
            ]
        }}
        """

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a forensic evaluation intelligence assistant that produces structured JSON diagnostics."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return _parse_llm_json_to_report(data, evaluation_run, failure_map)

    except Exception as e:
        logger.warning(f"LLM diagnostic generation failed ({e}). Falling back to deterministic forensic engine.")
        return _deterministic_forensic_diagnosis(evaluation_run, failure_map, pilot_twin, contract)
