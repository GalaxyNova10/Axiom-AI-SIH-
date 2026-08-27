EVIDENCE_LEVELS = [
    "CLAIMED",
    "DECLARED",
    "OBSERVED",
    "ESTIMATED",
    "INDEPENDENTLY_VALIDATED",
]

SUPPORTED_SOURCE_TYPES = {
    "vendor_claim",
    "department_declaration",
    "pilot_measurement",
    "model_estimate",
    "evaluator_result",
}

def classify_evidence(
    source_type: str,
    verification_method: str = "",
    evaluator_version: str = "",
    methodology: str = ""
) -> str:
    if not source_type or source_type not in SUPPORTED_SOURCE_TYPES:
        raise ValueError(
            f"Unsupported or empty source type: '{source_type}'. "
            f"Supported types are: {', '.join(SUPPORTED_SOURCE_TYPES)}"
        )

    if source_type == "vendor_claim":
        return "CLAIMED"
        
    elif source_type == "department_declaration":
        return "DECLARED"
        
    elif source_type == "pilot_measurement":
        return "OBSERVED"
        
    elif source_type == "model_estimate":
        return "ESTIMATED"
        
    elif source_type == "evaluator_result":
        if evaluator_version and methodology:
            return "INDEPENDENTLY_VALIDATED"
        else:
            return "OBSERVED"
