from dataclasses import dataclass
from typing import List, Dict, Any

SEVERITY_THRESHOLDS = {
    "CRITICAL": 70.0,
    "DEGRADED": 85.0,
    "WATCH": 95.0,
}
ERROR_RATE_CRITICAL_THRESHOLD = 30.0

@dataclass
class StratumResult:
    stratum_id: str
    total_cases: int
    correct_cases: int
    error_count: int
    accuracy: float
    average_latency_ms: float
    failure_rate: float
    severity: str

@dataclass
class FailureHotspot:
    stratum_id: str
    severity: str
    accuracy: float
    failure_rate: float
    reason: str

@dataclass
class FailureMap:
    vendor_id: str
    evaluation_id: str
    artifact_id: str
    evaluator_version: str
    
    overall_accuracy: float
    strata: List[StratumResult]
    hotspots: List[FailureHotspot]
    
    critical_strata: int
    degraded_strata: int
    watch_strata: int
    
    status: str

def generate_failure_map(evaluation_run: Any) -> FailureMap:
    if not evaluation_run or not hasattr(evaluation_run, 'results') or not evaluation_run.results:
        raise ValueError("EvaluationRun must not be empty and must have results.")
        
    grouped_cases = {}
    for res in evaluation_run.results:
        if res.stratum_id not in grouped_cases:
            grouped_cases[res.stratum_id] = {
                "total": 0,
                "correct": 0,
                "error": 0,
                "latency_sum": 0.0,
                "successful_cases": 0
            }
        
        grp = grouped_cases[res.stratum_id]
        grp["total"] += 1
        if res.correct:
            grp["correct"] += 1
        if res.error:
            grp["error"] += 1
        if not res.error:
            grp["latency_sum"] += res.latency_ms
            grp["successful_cases"] += 1
            
    strata_results = []
    hotspots = []
    
    crit_count = 0
    deg_count = 0
    watch_count = 0
    
    for stratum_id, grp in grouped_cases.items():
        total = grp["total"]
        accuracy = (grp["correct"] / total * 100) if total > 0 else 0.0
        accuracy = round(accuracy, 2)
        
        failure_rate = round(100.0 - accuracy, 2)
        
        succ = grp["successful_cases"]
        avg_latency = (grp["latency_sum"] / succ) if succ > 0 else 0.0
        avg_latency = round(avg_latency, 2)
        
        error_rate = (grp["error"] / total * 100) if total > 0 else 0.0
        
        severity = "NORMAL"
        reasons = []
        
        if error_rate >= ERROR_RATE_CRITICAL_THRESHOLD:
            severity = "CRITICAL"
            reasons.append("High execution error rate")
            if accuracy < SEVERITY_THRESHOLDS["CRITICAL"]:
                reasons.append("Accuracy below critical threshold")
            elif accuracy < SEVERITY_THRESHOLDS["DEGRADED"]:
                reasons.append("Accuracy below degraded threshold")
            elif accuracy < SEVERITY_THRESHOLDS["WATCH"]:
                reasons.append("Accuracy below watch threshold")
        else:
            if accuracy < SEVERITY_THRESHOLDS["CRITICAL"]:
                severity = "CRITICAL"
                reasons.append("Accuracy below critical threshold")
            elif accuracy < SEVERITY_THRESHOLDS["DEGRADED"]:
                severity = "DEGRADED"
                reasons.append("Accuracy below degraded threshold")
            elif accuracy < SEVERITY_THRESHOLDS["WATCH"]:
                severity = "WATCH"
                reasons.append("Accuracy below watch threshold")
                
        stratum_res = StratumResult(
            stratum_id=stratum_id,
            total_cases=total,
            correct_cases=grp["correct"],
            error_count=grp["error"],
            accuracy=accuracy,
            average_latency_ms=avg_latency,
            failure_rate=failure_rate,
            severity=severity
        )
        strata_results.append(stratum_res)
        
        if severity != "NORMAL":
            hotspots.append(FailureHotspot(
                stratum_id=stratum_id,
                severity=severity,
                accuracy=accuracy,
                failure_rate=failure_rate,
                reason="; ".join(reasons)
            ))
            
            if severity == "CRITICAL":
                crit_count += 1
            elif severity == "DEGRADED":
                deg_count += 1
            elif severity == "WATCH":
                watch_count += 1
                
    sev_rank = {"CRITICAL": 0, "DEGRADED": 1, "WATCH": 2}
    hotspots.sort(key=lambda h: (sev_rank[h.severity], h.accuracy))
    
    if crit_count > 0:
        overall_status = "CRITICAL"
    elif deg_count > 0:
        overall_status = "DEGRADED"
    elif watch_count > 0:
        overall_status = "WATCH"
    else:
        overall_status = "ROBUST"
        
    return FailureMap(
        vendor_id=evaluation_run.vendor_id,
        evaluation_id=evaluation_run.evaluation_id,
        artifact_id=evaluation_run.artifact_id,
        evaluator_version=evaluation_run.evaluator_version,
        overall_accuracy=evaluation_run.accuracy,
        strata=strata_results,
        hotspots=hotspots,
        critical_strata=crit_count,
        degraded_strata=deg_count,
        watch_strata=watch_count,
        status=overall_status
    )

def explain_failure_map(failure_map: FailureMap) -> Dict[str, Any]:
    top_hs = []
    for h in failure_map.hotspots:
        top_hs.append({
            "stratum": h.stratum_id,
            "severity": h.severity,
            "reason": h.reason
        })
        
    return {
        "overall_accuracy": failure_map.overall_accuracy,
        "status": failure_map.status,
        "critical_strata": failure_map.critical_strata,
        "degraded_strata": failure_map.degraded_strata,
        "watch_strata": failure_map.watch_strata,
        "top_hotspots": top_hs
    }
