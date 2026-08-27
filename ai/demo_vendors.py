from typing import Dict, Any

class VendorAAdapter:
    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        cond = input_data.get("conditions", {})
        expected = input_data.get("expected_output")
        
        score = 10
        if cond.get("connectivity") != "GOOD": score -= 3
        if cond.get("device") != "HIGH_END": score -= 3
        if cond.get("language") != "STANDARD": score -= 2
        if cond.get("input_quality") != "CLEAN": score -= 2
        
        prediction = expected if score > 3 else ("FAIL" if expected == "PASS" else "PASS")
        
        return {
            "prediction": prediction,
            "latency_ms": 120.0,
            "error": False
        }

class VendorBAdapter:
    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        cond = input_data.get("conditions", {})
        expected = input_data.get("expected_output")
        
        score = 8
        if cond.get("connectivity") == "INTERMITTENT": score += 2
        if cond.get("device") == "LOW_END": score -= 1
        if cond.get("input_quality") == "NOISY": score -= 2
        
        prediction = expected if score >= 7 else ("FAIL" if expected == "PASS" else "PASS")
        
        return {
            "prediction": prediction,
            "latency_ms": 180.0,
            "error": False
        }

class VendorCAdapter:
    def evaluate(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        cond = input_data.get("conditions", {})
        expected = input_data.get("expected_output")
        
        prediction = expected
        if cond.get("input_quality") == "NOISY" and cond.get("device") == "LOW_END" and cond.get("language") == "REGIONAL":
            prediction = "FAIL" if expected == "PASS" else "PASS"
            
        return {
            "prediction": prediction,
            "latency_ms": 95.0,
            "error": False
        }
