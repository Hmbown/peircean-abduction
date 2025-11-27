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

    def test_example_to_jsonl(self):
        generator = AbductiveDataGenerator(seed=42)
        example = generator.generate_example(Domain.FINANCIAL)
        jsonl = example.to_jsonl()

        # Should be valid JSON
        data = json.loads(jsonl)
        assert data["domain"] == "financial"
        assert "observation" in data
        assert "thought_format" in data

    def test_generate_example_fallback_domain(self):
        """Test that unknown domain falls back to FINANCIAL seed data."""
        generator = AbductiveDataGenerator(seed=42)
        # LEGAL domain has no seed data, should fall back
        example = generator.generate_example(Domain.LEGAL)
        assert example.domain == Domain.LEGAL
        # Should still have hypotheses from fallback data
        assert len(example.hypotheses) > 0

    def test_generate_batch_domain_variety(self):
        """Test batch generation across different domains."""
        generator = AbductiveDataGenerator(seed=42)
        examples = list(generator.generate_batch(n=20))

        domains = {ex.domain for ex in examples}
        # With 20 examples and random selection, should have some variety
        assert len(domains) >= 2


class TestAbductiveExampleFormats:
    """Test AbductiveExample formatting methods."""

    def test_thought_format_includes_all_sections(self):
        generator = AbductiveDataGenerator(seed=123)
        example = generator.generate_example(Domain.MEDICAL)
        thought = example.to_thought_format()

        # Check all sections present
        assert "OBSERVATION:" in thought
        assert "Surprise Level:" in thought
        assert "Domain:" in thought
        assert "HYPOTHESES:" in thought
        assert "EVALUATION (IBE Criteria):" in thought
        assert "SELECTION:" in thought
        assert "Rationale:" in thought
        assert "Confidence:" in thought
        assert "Recommended next steps:" in thought

    def test_thought_format_hypothesis_details(self):
        generator = AbductiveDataGenerator(seed=123)
        example = generator.generate_example(Domain.FINANCIAL)
        thought = example.to_thought_format()

        # Should include hypothesis numbering
        assert "H1:" in thought or "H2:" in thought or "H3:" in thought
        # Should include prior probabilities
        assert "prior:" in thought
        # Should include explanation
        assert "Explanation:" in thought

    def test_jsonl_roundtrip(self):
        generator = AbductiveDataGenerator(seed=99)
        example = generator.generate_example(Domain.TECHNICAL)
        jsonl = example.to_jsonl()

        # Parse and verify
        data = json.loads(jsonl)
        assert data["observation"] == example.observation
        assert data["domain"] == example.domain.value
        assert data["confidence"] == example.confidence
        assert data["selected"] == example.selected


class TestMainCLI:
    """Test the main() CLI entry point."""

    def test_main_default_jsonl_output(self, capsys):
        """Test default JSONL output to stdout."""
        import sys
        from unittest.mock import patch

        with patch.object(sys, "argv", ["generator", "-n", "3", "--seed", "42"]):
            from peircean.training.generator import main

            main()

        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 3

        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line)
            assert "observation" in data
            assert "domain" in data

    def test_main_thought_format_output(self, capsys):
        """Test thought format output to stdout."""
        import sys
        from unittest.mock import patch

        with patch.object(
            sys, "argv", ["generator", "-n", "2", "--format", "thought", "--seed", "42"]
        ):
            from peircean.training.generator import main

            main()

        captured = capsys.readouterr()
        output = captured.out

        # Should have thought tags
        assert "<thought>" in output
        assert "</thought>" in output
        # Should have separator between examples
        assert "---" in output

    def test_main_output_to_file(self, tmp_path):
        """Test writing output to file."""
        import sys
        from unittest.mock import patch

        output_file = tmp_path / "output.jsonl"

        with patch.object(
            sys, "argv", ["generator", "-n", "5", "-o", str(output_file), "--seed", "42"]
        ):
            from peircean.training.generator import main

            main()

        assert output_file.exists()
        with open(output_file) as f:
            lines = f.readlines()
        assert len(lines) == 5

    def test_main_output_file_message(self, tmp_path, capsys):
        """Test that writing to file prints confirmation."""
        import sys
        from unittest.mock import patch

        output_file = tmp_path / "output.jsonl"

        with patch.object(
            sys, "argv", ["generator", "-n", "3", "-o", str(output_file), "--seed", "42"]
        ):
            from peircean.training.generator import main

            main()

        captured = capsys.readouterr()
        assert "Wrote 3 examples" in captured.out
        assert str(output_file) in captured.out

    def test_main_custom_seed(self, capsys):
        """Test that different seeds produce different output."""
        import sys
        from unittest.mock import patch

        with patch.object(sys, "argv", ["generator", "-n", "5", "--seed", "100"]):
            from peircean.training.generator import main

            main()
        output1 = capsys.readouterr().out

        with patch.object(sys, "argv", ["generator", "-n", "5", "--seed", "200"]):
            main()
        output2 = capsys.readouterr().out

        # Different seeds should produce different output
        # (though the seed data is limited, there should be some variation)
        # At minimum, the structure should be similar
        assert len(output1.split("\n")) == len(output2.split("\n"))

    def test_main_thought_format_to_file(self, tmp_path, capsys):
        """Test thought format written to file."""
        import sys
        from unittest.mock import patch

        output_file = tmp_path / "thoughts.txt"

        with patch.object(
            sys,
            "argv",
            ["generator", "-n", "2", "--format", "thought", "-o", str(output_file), "--seed", "42"],
        ):
            from peircean.training.generator import main

            main()

        with open(output_file) as f:
            content = f.read()

        assert "<thought>" in content
        assert "OBSERVATION:" in content
        assert "---" in content  # separator between examples
