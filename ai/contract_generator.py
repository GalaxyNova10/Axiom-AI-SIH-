import json
import logging
import os
from typing import List, Dict, Any

from openai import OpenAI

from ai.schemas import KPI, OutcomeContract

logger = logging.getLogger(__name__)


def _generate_deterministic_contract(
    contract_id: str,
    problem_statement: str,
) -> OutcomeContract:
    """Deterministic fallback for outcome contract generation."""
    problem_lower = problem_statement.lower()
    kpis: List[KPI] = []

    if any(
        word in problem_lower
        for word in ["delivery", "logistics", "transport", "route"]
    ):
        kpis.extend(
            [
                KPI(
                    name="Delivery Success Rate",
                    threshold=90.0,
                    operator=">=",
                    unit="%",
                ),
                KPI(
                    name="Average Delivery Delay",
                    threshold=15.0,
                    operator="<=",
                    unit="minutes",
                ),
            ]
        )

    if not kpis:
        kpis.append(
            KPI(
                name="Solution Performance",
                threshold=90.0,
                operator=">=",
                unit="%",
            )
        )

    return OutcomeContract(
        contract_id=contract_id,
        version="1.0",
        kpis=kpis,
        minimum_evidence_confidence=70.0,
        evidence_validity_months=12,
        locked=False,
    )


def _validate_llm_output(data: Dict[str, Any]) -> None:
    """Strict validation of the parsed JSON from the LLM."""
    if "kpis" not in data or not isinstance(data["kpis"], list) or not data["kpis"]:
        raise ValueError("kpis must be a non-empty list")

    for kpi in data["kpis"]:
        if "name" not in kpi or not kpi["name"]:
            raise ValueError("KPI name must not be empty")
        if "threshold" not in kpi or not isinstance(kpi["threshold"], (int, float)):
            raise ValueError("KPI threshold must be numeric")
        if "operator" not in kpi or kpi["operator"] not in (">=", "<=", ">", "<", "=="):
            raise ValueError("invalid operator")
        if "unit" not in kpi:
            raise ValueError("KPI unit must be present (can be empty string)")

    conf = data.get("minimum_evidence_confidence")
    if not isinstance(conf, (int, float)) or not (0 <= conf <= 100):
        raise ValueError("minimum_evidence_confidence must be between 0 and 100")

    val = data.get("evidence_validity_months")
    if not isinstance(val, int) or val <= 0:
        raise ValueError("evidence_validity_months must be a positive integer")


def generate_outcome_contract(
    contract_id: str,
    problem_statement: str,
) -> OutcomeContract:
    """
    Generate an Outcome Contract using an LLM.
    Falls back to deterministic generation on failure or if API key is missing.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.info("OPENAI_API_KEY missing. Falling back to deterministic generation.")
        return _generate_deterministic_contract(contract_id, problem_statement)

    model = os.environ.get("AXIOM_LLM_MODEL", "gpt-3.5-turbo")

    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Extract measurable outcomes from the supplied government problem.
        Prefer objective KPIs.
        Avoid inventing highly specific requirements unsupported by the problem.
        Produce only the requested structured fields in JSON format.
        Use conservative defaults when a value genuinely cannot be inferred.
        Never include prose outside the structured output.
        
        The expected JSON structure is:
        {{
            "kpis": [
                {{
                    "name": "string",
                    "threshold": number,
                    "operator": ">=, <=, >, <, or ==",
                    "unit": "string"
                }}
            ],
            "minimum_evidence_confidence": number (0-100),
            "evidence_validity_months": positive integer
        }}
        
        Government Problem Statement:
        {problem_statement}
        """

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a data extraction bot that outputs only valid JSON conforming to the requested schema."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        _validate_llm_output(data)

        kpis = [
            KPI(
                name=k["name"],
                threshold=float(k["threshold"]),
                operator=k["operator"],
                unit=str(k["unit"])
            )
            for k in data["kpis"]
        ]

        return OutcomeContract(
            contract_id=contract_id,
            version="1.0",
            kpis=kpis,
            minimum_evidence_confidence=float(data["minimum_evidence_confidence"]),
            evidence_validity_months=int(data["evidence_validity_months"]),
            locked=False
        )

    except Exception as e:
        logger.warning(f"LLM contract generation failed: {e}. Falling back to deterministic logic.")
        return _generate_deterministic_contract(contract_id, problem_statement)