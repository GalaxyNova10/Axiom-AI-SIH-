from dataclasses import dataclass
from typing import Protocol, Dict, Any, List
from ai.test_matrix import TestSuite, validate_test_suite
import uuid

class EvaluationAdapter(Protocol):
    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        ...

@dataclass
class EvaluationCaseResult:
    __test__ = False
    test_case_id: str
    stratum_id: str
    expected_output: Any
    actual_output: Any
    correct: bool
    latency_ms: float
    error: bool

@dataclass
class EvaluationRun:
    __test__ = False
    evaluation_id: str
    vendor_id: str
    artifact_id: str
    evaluator_version: str
    test_suite_id: str
    test_suite_version: str
    test_suite_hash: str
    results: List[EvaluationCaseResult]
    total_cases: int
    correct_cases: int
    accuracy: float
    average_latency_ms: float
    error_count: int
    status: str

def evaluate_vendor(
    vendor_id: str,
    artifact_id: str,
    adapter: EvaluationAdapter,
    test_suite: TestSuite,
    evaluator_version: str,
    evaluator_authorized: bool,
    expected_outputs: Dict[str, Any],
) -> EvaluationRun:
    
    if not vendor_id:
        raise ValueError("vendor_id cannot be empty")
    if not artifact_id:
        raise ValueError("artifact_id cannot be empty")
    if not evaluator_version:
        raise ValueError("evaluator_version cannot be empty")
    if not evaluator_authorized:
        raise ValueError("Evaluator must be authorized")
        
    validate_test_suite(test_suite)
    
    results = []
    error_count = 0
    correct_cases = 0
    total_latency_ms = 0.0
    successful_cases = 0
    
    for condition in test_suite.conditions:
        if condition.test_case_id not in expected_outputs:
            raise ValueError(f"Missing expected output for {condition.test_case_id}")
            
        expected_output = expected_outputs[condition.test_case_id]
        
        input_data = {
            "test_case_id": condition.test_case_id,
            "stratum_id": condition.stratum_id,
            "conditions": {
                "connectivity": condition.connectivity,
                "device": condition.device,
                "language": condition.language,
                "input_quality": condition.input_quality
            },
            "private_parameters": condition.private_parameters,
            "expected_output": expected_output
        }
        
        prediction = None
        latency_ms = 0.0
        error = False
        correct = False
        
        try:
            adapter_res = adapter.evaluate(input_data)
            
            if not isinstance(adapter_res, dict) or \
               "prediction" not in adapter_res or \
               "latency_ms" not in adapter_res or \
               "error" not in adapter_res:
                error = True
            else:
                prediction = adapter_res["prediction"]
                latency_ms = float(adapter_res["latency_ms"])
                error = bool(adapter_res["error"])
                
                if not error:
                    correct = (prediction == expected_output)
                    if correct:
                        correct_cases += 1
                    total_latency_ms += latency_ms
                    successful_cases += 1
                    
        except Exception:
            error = True
            
        if error:
            error_count += 1
            
        results.append(EvaluationCaseResult(
            test_case_id=condition.test_case_id,
            stratum_id=condition.stratum_id,
            expected_output=expected_output,
            actual_output=prediction,
            correct=correct,
            latency_ms=latency_ms,
            error=error
        ))

    total_cases = len(test_suite.conditions)
    accuracy = round((correct_cases / total_cases * 100) if total_cases > 0 else 0.0, 2)
    average_latency_ms = round((total_latency_ms / successful_cases) if successful_cases > 0 else 0.0, 2)
    
    return EvaluationRun(
        evaluation_id=str(uuid.uuid4()),
        vendor_id=vendor_id,
        artifact_id=artifact_id,
        evaluator_version=evaluator_version,
        test_suite_id=test_suite.suite_id,
        test_suite_version=test_suite.version,
        test_suite_hash=test_suite.seed_hash,
        results=results,
        total_cases=total_cases,
        correct_cases=correct_cases,
        accuracy=accuracy,
        average_latency_ms=average_latency_ms,
        error_count=error_count,
        status="COMPLETED"
    )
