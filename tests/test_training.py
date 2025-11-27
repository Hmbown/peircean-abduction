"""
Tests for Peircean Training Data Generator.
"""

import json

from peircean.core.models import Domain
from peircean.training.generator import AbductiveDataGenerator, AbductiveExample


class TestAbductiveDataGenerator:
    """Test data generator functionality."""

    def test_generator_initialization(self):
        generator = AbductiveDataGenerator(seed=42)
        assert len(generator.domains) == len(Domain)

        generator = AbductiveDataGenerator(domains=[Domain.FINANCIAL])
        assert len(generator.domains) == 1
        assert generator.domains[0] == Domain.FINANCIAL

    def test_generate_example(self):
        generator = AbductiveDataGenerator(seed=42)
        example = generator.generate_example(Domain.FINANCIAL)

        assert isinstance(example, AbductiveExample)
        assert example.domain == Domain.FINANCIAL
        assert example.surprise_level == "high"
        assert len(example.hypotheses) > 0
        assert example.selected in [h["statement"] for h in example.hypotheses]
        assert example.confidence > 0

    def test_generate_batch(self):
        generator = AbductiveDataGenerator(seed=42)
        examples = list(generator.generate_batch(n=10))

        assert len(examples) == 10
        assert all(isinstance(ex, AbductiveExample) for ex in examples)

    def test_generate_jsonl(self):
        generator = AbductiveDataGenerator(seed=42)
        jsonl_output = generator.generate_jsonl(n=5)

        lines = jsonl_output.strip().split("\n")
        assert len(lines) == 5

        for line in lines:
            data = json.loads(line)
            assert "observation" in data
            assert "domain" in data
            assert "hypotheses" in data
            assert "selected" in data
            assert "thought_format" in data

    def test_thought_format(self):
        generator = AbductiveDataGenerator(seed=42)
        example = generator.generate_example(Domain.TECHNICAL)
        thought = example.to_thought_format()

        assert "<thought>" in thought
        assert "</thought>" in thought
        assert "OBSERVATION:" in thought
        assert "HYPOTHESES:" in thought
        assert "EVALUATION" in thought
        assert "SELECTION:" in thought
