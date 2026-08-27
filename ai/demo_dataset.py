from typing import Dict, Any
from ai.test_matrix import TestSuite

def get_demo_expected_outputs(test_suite: TestSuite) -> Dict[str, Any]:
    outputs = {}
    for condition in test_suite.conditions:
        h = sum(ord(c) for c in condition.stratum_id)
        outputs[condition.test_case_id] = "PASS" if h % 2 == 0 else "FAIL"
    return outputs
