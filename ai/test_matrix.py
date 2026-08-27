import hashlib
import random
import secrets
import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

CONNECTIVITY_LEVELS = ["GOOD", "INTERMITTENT"]
DEVICE_LEVELS = ["HIGH_END", "LOW_END"]
LANGUAGE_LEVELS = ["STANDARD", "REGIONAL"]
INPUT_QUALITY_LEVELS = ["CLEAN", "DEGRADED", "NOISY"]

@dataclass
class TestCondition:
    __test__ = False
    stratum_id: str
    connectivity: str
    device: str
    language: str
    input_quality: str
    test_case_id: str
    private_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    __test__ = False
    suite_id: str
    pilot_twin_id: str
    version: str
    seed_hash: str
    conditions: List[TestCondition]
    locked: bool

def generate_test_suite(
    suite_id: str,
    pilot_twin_id: str,
    seed: Optional[int] = None
) -> TestSuite:
    if seed is None:
        seed = secrets.randbits(64)
    
    rng = random.Random(seed)
    seed_hash = hashlib.sha256(str(seed).encode('utf-8')).hexdigest()
    
    conditions = []
    
    combinations = list(itertools.product(
        CONNECTIVITY_LEVELS,
        DEVICE_LEVELS,
        LANGUAGE_LEVELS,
        INPUT_QUALITY_LEVELS
    ))
    
    rng.shuffle(combinations)
    
    for i, (conn, dev, lang, qual) in enumerate(combinations, start=1):
        stratum_id = f"{conn}_{dev}_{lang}_{qual}"
        test_case_id = f"TC-{i:03d}"
        
        priv = {}
        
        if conn == "GOOD":
            priv["latency_ms"] = rng.randint(50, 150)
            priv["packet_loss_percent"] = round(rng.uniform(0.0, 1.0), 2)
        else:
            priv["latency_ms"] = rng.randint(500, 1500)
            priv["packet_loss_percent"] = round(rng.uniform(3.0, 15.0), 2)
            
        if dev == "HIGH_END":
            priv["memory_gb"] = rng.randint(6, 12)
            priv["cpu_class"] = "HIGH"
        else:
            priv["memory_gb"] = rng.randint(2, 4)
            priv["cpu_class"] = "LOW"
            
        if lang == "STANDARD":
            priv["language_code"] = "en"
        else:
            priv["language_code"] = rng.choice(["ta", "hi", "te", "kn"])
            
        if qual == "CLEAN":
            priv["compression_quality"] = rng.randint(90, 100)
        elif qual == "DEGRADED":
            priv["compression_quality"] = rng.randint(50, 75)
        else:
            priv["compression_quality"] = rng.randint(20, 49)
            priv["noise_level"] = round(rng.uniform(0.10, 0.30), 2)
            
        conditions.append(TestCondition(
            stratum_id=stratum_id,
            connectivity=conn,
            device=dev,
            language=lang,
            input_quality=qual,
            test_case_id=test_case_id,
            private_parameters=priv
        ))
        
    return TestSuite(
        suite_id=suite_id,
        pilot_twin_id=pilot_twin_id,
        version="1.0",
        seed_hash=seed_hash,
        conditions=conditions,
        locked=False
    )

def get_public_methodology(test_suite: TestSuite) -> dict:
    return {
        "connectivity": CONNECTIVITY_LEVELS,
        "device": DEVICE_LEVELS,
        "language": LANGUAGE_LEVELS,
        "input_quality": INPUT_QUALITY_LEVELS,
        "total_strata": 24
    }

def lock_test_suite(test_suite: TestSuite) -> TestSuite:
    test_suite.locked = True
    return test_suite

def validate_test_suite(test_suite: TestSuite) -> bool:
    if not test_suite.suite_id:
        raise ValueError("suite_id is missing")
    if not test_suite.pilot_twin_id:
        raise ValueError("pilot_twin_id is missing")
    if not test_suite.version:
        raise ValueError("version is missing")
    if not test_suite.seed_hash or len(test_suite.seed_hash) != 64:
        raise ValueError("seed_hash is invalid")
    try:
        int(test_suite.seed_hash, 16)
    except ValueError:
        raise ValueError("seed_hash is not hex")
        
    if len(test_suite.conditions) != 24:
        raise ValueError(f"Expected 24 conditions, got {len(test_suite.conditions)}")
        
    strata = set()
    test_ids = set()
    
    for c in test_suite.conditions:
        if c.stratum_id in strata:
            raise ValueError(f"Duplicate stratum_id: {c.stratum_id}")
        strata.add(c.stratum_id)
        
        if c.test_case_id in test_ids:
            raise ValueError(f"Duplicate test_case_id: {c.test_case_id}")
        test_ids.add(c.test_case_id)
        
        if not c.private_parameters:
            raise ValueError(f"Private parameters empty for {c.test_case_id}")
            
    valid_combos = set(
        f"{conn}_{dev}_{lang}_{qual}" 
        for conn in CONNECTIVITY_LEVELS
        for dev in DEVICE_LEVELS
        for lang in LANGUAGE_LEVELS
        for qual in INPUT_QUALITY_LEVELS
    )
    
    if strata != valid_combos:
        raise ValueError("Missing or invalid stratum combinations")
        
    return True
