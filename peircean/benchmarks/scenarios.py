"""
Benchmark scenarios for testing Peircean Abduction performance.

Standard scenarios covering different domains, complexity levels, and usage patterns.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class BenchmarkScenario:
    """A benchmark scenario with test parameters and expected outputs."""

    name: str
    description: str
    domain: str
    observation: str
    context: Optional[Dict[str, Any]] = None
    num_hypotheses: int = 5
    use_council: bool = True
    expected_min_prompt_length: int = 1000
    expected_max_time_seconds: float = 5.0
    tags: List[str] = None

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []


def get_standard_scenarios() -> List[BenchmarkScenario]:
    """Get standard benchmark scenarios covering various use cases."""

    scenarios = [
        # Simple scenarios
        BenchmarkScenario(
            name="simple_financial",
            description="Simple financial market anomaly",
            domain="financial",
            observation="Stock price dropped 5% on positive earnings news",
            expected_min_prompt_length=800,
            expected_max_time_seconds=2.0,
            tags=["simple", "financial", "quick"]
        ),

        BenchmarkScenario(
            name="simple_technical",
            description="Simple technical system anomaly",
            domain="technical",
            observation="Server latency increased 10x but CPU usage is normal",
            expected_min_prompt_length=800,
            expected_max_time_seconds=2.0,
            tags=["simple", "technical", "quick"]
        ),

        # Medium complexity scenarios
        BenchmarkScenario(
            name="medium_business",
            description="Medium complexity business anomaly",
            domain="general",
            observation="Customer retention improved while support tickets increased",
            context={"industry": "SaaS", "time_period": "Q3 2024"},
            expected_min_prompt_length=1200,
            expected_max_time_seconds=3.0,
            tags=["medium", "business", "context"]
        ),

        BenchmarkScenario(
            name="medium_medical",
            description="Medium complexity medical diagnostic scenario",
            domain="medical",
            observation="Patient's fever resolved but inflammatory markers increased",
            context={"patient_age": 45, "symptoms_duration": "3 days"},
            expected_min_prompt_length=1200,
            expected_max_time_seconds=3.0,
            tags=["medium", "medical", "context"]
        ),

        # Complex scenarios
        BenchmarkScenario(
            name="complex_scientific",
            description="Complex scientific experimental anomaly",
            domain="scientific",
            observation="Experimental results consistently contradict established theoretical predictions",
            context={
                "field": "quantum_physics",
                "experiment_type": "double_slit",
                "reproducibility": "high"
            },
            expected_min_prompt_length=1500,
            expected_max_time_seconds=4.0,
            tags=["complex", "scientific", "research"]
        ),

        BenchmarkScenario(
            name="complex_legal",
            description="Complex legal interpretation scenario",
            domain="legal",
            observation="Statutory language creates apparent conflict between two established legal principles",
            context={
                "jurisdiction": "federal",
                "case_type": "constitutional_law",
                "precedent_level": "supreme_court"
            },
            expected_min_prompt_length=1500,
            expected_max_time_seconds=4.0,
            tags=["complex", "legal", "precedent"]
        ),

        # Council evaluation scenarios
        BenchmarkScenario(
            name="council_financial",
            description="Financial scenario with Council of Critics evaluation",
            domain="financial",
            observation="Cryptocurrency price moved opposite to traditional market correlation",
            use_council=True,
            num_hypotheses=5,
            expected_min_prompt_length=2000,
            expected_max_time_seconds=6.0,
            tags=["council", "financial", "evaluation"]
        ),

        BenchmarkScenario(
            name="council_technical",
            description="Technical scenario with Council of Critics evaluation",
            domain="technical",
            observation="System performance improved after removing optimizations",
            use_council=True,
            context={"optimization_type": "caching", "system_type": "database"},
            expected_min_prompt_length=2000,
            expected_max_time_seconds=6.0,
            tags=["council", "technical", "evaluation"]
        ),

        # Edge cases
        BenchmarkScenario(
            name="minimal",
            description="Minimal scenario for baseline testing",
            domain="general",
            observation="Unexpected event occurred",
            num_hypotheses=3,
            use_council=False,
            expected_min_prompt_length=500,
            expected_max_time_seconds=1.0,
            tags=["minimal", "baseline", "quick"]
        ),

        BenchmarkScenario(
            name="maximal",
            description="Maximal scenario for stress testing",
            domain="scientific",
            observation="Multiple conflicting experimental observations across different methodologies",
            context={
                "methodologies": ["experimental", "observational", "computational"],
                "disciplines": ["physics", "chemistry", "biology"],
                "sample_size": 10000
            },
            num_hypotheses=8,
            use_council=True,
            expected_min_prompt_length=3000,
            expected_max_time_seconds=10.0,
            tags=["maximal", "stress", "council"]
        ),
    ]

    return scenarios


def get_scenario_by_name(name: str) -> Optional[BenchmarkScenario]:
    """Get a specific scenario by name."""
    scenarios = get_standard_scenarios()
    for scenario in scenarios:
        if scenario.name == name:
            return scenario
    return None


def get_scenarios_by_tag(tag: str) -> List[BenchmarkScenario]:
    """Get all scenarios with a specific tag."""
    scenarios = get_standard_scenarios()
    return [s for s in scenarios if tag in s.tags]


def get_scenarios_by_domain(domain: str) -> List[BenchmarkScenario]:
    """Get all scenarios for a specific domain."""
    scenarios = get_standard_scenarios()
    return [s for s in scenarios if s.domain == domain]


def get_quick_scenarios() -> List[BenchmarkScenario]:
    """Get quick scenarios for rapid testing."""
    scenarios = get_standard_scenarios()
    return [s for s in scenarios if "quick" in s.tags]


def get_complex_scenarios() -> List[BenchmarkScenario]:
    """Get complex scenarios for thorough testing."""
    scenarios = get_standard_scenarios()
    return [s for s in scenarios if "complex" in s.tags or "maximal" in s.tags]


def get_council_scenarios() -> List[BenchmarkScenario]:
    """Get scenarios that use Council of Critics."""
    scenarios = get_standard_scenarios()
    return [s for s in scenarios if s.use_council]