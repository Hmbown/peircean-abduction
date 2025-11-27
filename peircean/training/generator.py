"""
Peircean Abduction: Training Data Generator

Generates training data that embeds abductive reasoning patterns
into model thinking. The goal is to train models to:

1. Recognize surprising observations
2. Generate diverse explanatory hypotheses
3. Evaluate hypotheses using IBE criteria
4. Select the best explanation with appropriate confidence

Training Format:
    <thought>
    OBSERVATION: [The surprising fact and why it's surprising]
    HYPOTHESES: [Multiple explanatory hypotheses with assumptions]
    EVALUATION: [IBE scoring for each hypothesis]
    SELECTION: [Best explanation with rationale and confidence]
    </thought>
    [Final answer with recommended actions]
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, TypedDict, cast

from ..core.models import Domain


class SeedHypothesis(TypedDict, total=False):
    """Type for seed hypothesis data."""

    statement: str
    explanation: str
    prior_probability: float
    assumptions: list[str]


class SeedObservation(TypedDict):
    """Type for seed observation data."""

    observation: str
    context: dict[str, Any]
    hypotheses: list[SeedHypothesis]


@dataclass
class AbductiveExample:
    """A single abductive reasoning training example."""

    observation: str
    domain: Domain
    context: dict[str, Any]
    surprise_level: str
    hypotheses: list[dict[str, Any]]
    evaluation: dict[str, Any]
    selected: str
    rationale: str
    confidence: float
    recommended_actions: list[str]

    def to_thought_format(self) -> str:
        """Convert to <thought> training format."""
        hypotheses_text = "\n".join(
            [
                f"  H{i + 1}: {h['statement']} (prior: {h['prior_probability']:.2f})\n"
                f"      Explanation: {h['explanation']}\n"
                f"      Assumptions: {', '.join(h.get('assumptions', []))}"
                for i, h in enumerate(self.hypotheses)
            ]
        )

        eval_text = "\n".join(
            [
                f"  {hid}: scope={scores['explanatory_scope']:.2f}, "
                f"power={scores['explanatory_power']:.2f}, "
                f"parsimony={scores['parsimony']:.2f}, "
                f"testability={scores['testability']:.2f}, "
                f"composite={scores['composite']:.2f}"
                for hid, scores in self.evaluation.items()
            ]
        )

        actions_text = "\n".join(
            [f"  {i + 1}. {a}" for i, a in enumerate(self.recommended_actions)]
        )

        thought = f"""<thought>
OBSERVATION: {self.observation}
Surprise Level: {self.surprise_level}
Domain: {self.domain.value}

Why Surprising: This observation violates expectations because...
{self.context.get("surprise_reason", "the expected outcome differs from what was observed.")}

HYPOTHESES:
{hypotheses_text}

EVALUATION (IBE Criteria):
{eval_text}

SELECTION: {self.selected}
Rationale: {self.rationale}
Confidence: {self.confidence:.2f}
</thought>

Based on abductive analysis, the best explanation is: {self.selected}

{self.rationale}

Recommended next steps:
{actions_text}
"""
        return thought.strip()

    def to_jsonl(self) -> str:
        """Convert to JSONL format for training."""
        return json.dumps(
            {
                "observation": self.observation,
                "domain": self.domain.value,
                "context": self.context,
                "surprise_level": self.surprise_level,
                "hypotheses": self.hypotheses,
                "evaluation": self.evaluation,
                "selected": self.selected,
                "rationale": self.rationale,
                "confidence": self.confidence,
                "recommended_actions": self.recommended_actions,
                "thought_format": self.to_thought_format(),
            }
        )


# Example seed data for generating training examples
SEED_OBSERVATIONS: dict[Domain, list[SeedObservation]] = {
    Domain.FINANCIAL: [
        {
            "observation": "Stock price dropped 8% immediately after earnings beat expectations by 15%",
            "context": {
                "surprise_reason": "Positive earnings typically correlate with price increases"
            },
            "hypotheses": [
                {
                    "statement": "Institutional investors had priced in even higher expectations",
                    "explanation": "The 15% beat was below whisper numbers of 20%+",
                    "prior_probability": 0.35,
                    "assumptions": ["Efficient market hypothesis", "Whisper numbers exist"],
                },
                {
                    "statement": "Forward guidance was disappointing",
                    "explanation": "Management's outlook for next quarter was below consensus",
                    "prior_probability": 0.30,
                    "assumptions": ["Market values future over past performance"],
                },
                {
                    "statement": "Large institutional selling unrelated to earnings",
                    "explanation": "Index rebalancing or fund redemptions forced sales",
                    "prior_probability": 0.20,
                    "assumptions": ["Structural market flows can dominate fundamentals"],
                },
            ],
        },
        {
            "observation": "Trading volume spiked 500% with no news or price movement",
            "context": {"surprise_reason": "Volume typically correlates with news or price change"},
            "hypotheses": [
                {
                    "statement": "Dark pool block trade being worked",
                    "explanation": "Large institutional trade split across time to minimize impact",
                    "prior_probability": 0.40,
                    "assumptions": ["Institutional activity visible in volume"],
                },
                {
                    "statement": "Algorithmic trading malfunction",
                    "explanation": "Automated system entered unintended orders",
                    "prior_probability": 0.25,
                    "assumptions": ["Algos can malfunction", "No immediate correction mechanism"],
                },
            ],
        },
    ],
    Domain.TECHNICAL: [
        {
            "observation": "Server CPU utilization dropped 40% while response latency increased 200%",
            "context": {
                "surprise_reason": "Lower CPU should mean more capacity, not worse performance"
            },
            "hypotheses": [
                {
                    "statement": "Database connection pool exhaustion",
                    "explanation": "Requests waiting for DB connections, CPU idle during waits",
                    "prior_probability": 0.35,
                    "assumptions": ["Fixed connection pool size", "DB is bottleneck"],
                },
                {
                    "statement": "Kubernetes autoscaler removed pods too aggressively",
                    "explanation": "HPA scaled down on low CPU, remaining pods overloaded",
                    "prior_probability": 0.30,
                    "assumptions": [
                        "HPA configured for CPU",
                        "Scale-down threshold too aggressive",
                    ],
                },
                {
                    "statement": "Network partition isolating high-CPU pods",
                    "explanation": "Active pods unreachable, traffic routed to idle/slow pods",
                    "prior_probability": 0.20,
                    "assumptions": ["Network can partition", "Health checks not detecting issue"],
                },
            ],
        },
    ],
    Domain.MEDICAL: [
        {
            "observation": "Patient's fever resolved but inflammatory markers increased",
            "context": {"surprise_reason": "Fever and inflammation typically correlate"},
            "hypotheses": [
                {
                    "statement": "Antipyretic medication masking ongoing infection",
                    "explanation": "NSAIDs reducing fever without addressing underlying cause",
                    "prior_probability": 0.35,
                    "assumptions": ["Patient on antipyretics", "Infection still active"],
                },
                {
                    "statement": "Autoimmune flare secondary to infection",
                    "explanation": "Original infection triggered autoimmune response",
                    "prior_probability": 0.30,
                    "assumptions": ["Autoimmune predisposition", "Molecular mimicry"],
                },
            ],
        },
    ],
}


class AbductiveDataGenerator:
    """
    Generator for abductive reasoning training data.

    Creates diverse examples across domains that teach models
    the Peircean abduction pattern.
    """

    def __init__(self, domains: list[Domain] | None = None, seed: int = 42):
        self.domains = domains or list(Domain)
        self.rng = random.Random(seed)

    def generate_example(self, domain: Domain) -> AbductiveExample:
        """Generate a single training example for a domain."""
        seed_data = SEED_OBSERVATIONS.get(domain, SEED_OBSERVATIONS[Domain.FINANCIAL])
        base = self.rng.choice(seed_data)

        # Create evaluation scores
        evaluation = {}
        hypotheses = base["hypotheses"]
        for i, _h in enumerate(hypotheses):
            hid = f"H{i + 1}"
            scores = {
                "explanatory_scope": 0.5 + self.rng.random() * 0.4,
                "explanatory_power": 0.5 + self.rng.random() * 0.4,
                "parsimony": 0.5 + self.rng.random() * 0.4,
                "testability": 0.5 + self.rng.random() * 0.4,
            }
            scores["composite"] = sum(scores.values()) / len(scores)
            evaluation[hid] = scores

        # Select best hypothesis
        best_id = max(evaluation.keys(), key=lambda k: evaluation[k]["composite"])
        best_idx = int(best_id[1:]) - 1
        best_hypothesis = hypotheses[best_idx]

        return AbductiveExample(
            observation=base["observation"],
            domain=domain,
            context=base["context"],
            surprise_level="high",
            hypotheses=cast(list[dict[str, Any]], hypotheses),
            evaluation=evaluation,
            selected=best_hypothesis["statement"],
            rationale=f"This hypothesis has the highest composite IBE score ({evaluation[best_id]['composite']:.2f}) "
            f"and best explains why {base['observation'].lower()}",
            confidence=evaluation[best_id]["composite"],
            recommended_actions=[
                f"Verify assumption: {best_hypothesis['assumptions'][0]}"
                if best_hypothesis.get("assumptions")
                else "Gather more data",
                "Monitor for additional evidence",
                "Consider alternative hypotheses if initial tests fail",
            ],
        )

    def generate_batch(self, n: int = 100) -> Iterator[AbductiveExample]:
        """Generate a batch of training examples."""
        for _ in range(n):
            domain = self.rng.choice(self.domains)
            yield self.generate_example(domain)

    def generate_jsonl(self, n: int = 100) -> str:
        """Generate JSONL training data."""
        lines = [ex.to_jsonl() for ex in self.generate_batch(n)]
        return "\n".join(lines)


def main() -> None:
    """CLI for generating training data."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate abductive reasoning training data")
    parser.add_argument("-n", "--num", type=int, default=100, help="Number of examples")
    parser.add_argument("-o", "--output", type=str, help="Output file (default: stdout)")
    parser.add_argument("--format", choices=["jsonl", "thought"], default="jsonl")
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    generator = AbductiveDataGenerator(seed=args.seed)

    if args.format == "jsonl":
        output = generator.generate_jsonl(args.num)
    else:
        examples = list(generator.generate_batch(args.num))
        output = "\n\n---\n\n".join(ex.to_thought_format() for ex in examples)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Wrote {args.num} examples to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
