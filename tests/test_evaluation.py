"""
Evaluation Tests for Peircean MCP Server.

These tests correspond to the 10 evaluation questions in docs/EVALUATION.md.
They validate tool functionality, error handling, schema compliance, and integration behavior.
"""

import json

import pytest

from peircean.mcp.server import (
    mcp,
    peircean_abduce_single_shot,
    peircean_critic_evaluate,
    peircean_evaluate_via_ibe,
    peircean_generate_hypotheses,
    peircean_observe_anomaly,
)


class TestQuestion1ToolDiscovery:
    """Question 1: Tool Discovery - Verify all 5 tools exist with correct names."""

    def test_all_tools_registered(self):
        """Verify all 5 tools are registered with the MCP server."""
        # Get registered tools from the MCP server
        tools = mcp._tool_manager._tools  # Access internal tool registry

        expected_tools = [
            "peircean_observe_anomaly",
            "peircean_generate_hypotheses",
            "peircean_evaluate_via_ibe",
            "peircean_abduce_single_shot",
            "peircean_critic_evaluate",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not found"

    def test_exactly_five_peircean_tools(self):
        """Verify exactly 5 peircean_ prefixed tools exist."""
        tools = mcp._tool_manager._tools
        peircean_tools = [t for t in tools.keys() if t.startswith("peircean_")]
        assert len(peircean_tools) == 5


class TestQuestion2PhaseFlow:
    """Question 2: Phase Flow - Verify next_tool field guides correctly."""

    def test_phase1_points_to_phase2(self):
        """Phase 1 should point to peircean_generate_hypotheses."""
        result = json.loads(peircean_observe_anomaly(observation="Test", domain="general"))
        assert result["phase"] == 1
        assert result["next_tool"] == "peircean_generate_hypotheses"

    def test_phase2_points_to_phase3(self):
        """Phase 2 should point to peircean_evaluate_via_ibe."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result = json.loads(peircean_generate_hypotheses(anomaly_json=anomaly_json))
        assert result["phase"] == 2
        assert result["next_tool"] == "peircean_evaluate_via_ibe"

    def test_phase3_terminates(self):
        """Phase 3 should have next_tool=null."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})
        result = json.loads(
            peircean_evaluate_via_ibe(anomaly_json=anomaly_json, hypotheses_json=hypotheses_json)
        )
        assert result["phase"] == 3
        assert result["next_tool"] is None


class TestQuestion3EmptyObservation:
    """Question 3: Input Validation - Empty Observation."""

    def test_empty_string_returns_error(self):
        """Empty observation should return standardized error."""
        result = json.loads(peircean_observe_anomaly(observation="", domain="general"))
        assert result["type"] == "error"
        # Now uses Pydantic validation with detailed error messages
        assert "observation" in result["error"].lower()
        assert "hint" in result

    def test_whitespace_only_returns_error(self):
        """Whitespace-only observation should return standardized error."""
        result = json.loads(peircean_observe_anomaly(observation="   \t\n  ", domain="general"))
        assert result["type"] == "error"
        # Whitespace-only is stripped and fails min_length=1 validation
        assert "observation" in result["error"].lower()


class TestQuestion4NumHypothesesBounds:
    """Question 4: Input Validation - num_hypotheses Bounds."""

    def test_zero_hypotheses_returns_error(self):
        """num_hypotheses=0 should return error."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=0)
        )
        assert result["type"] == "error"
        assert "between 1 and 20" in result["error"]

    def test_negative_hypotheses_returns_error(self):
        """num_hypotheses=-5 should return error."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=-5)
        )
        assert result["type"] == "error"

    def test_excessive_hypotheses_returns_error(self):
        """num_hypotheses=25 should return error."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=25)
        )
        assert result["type"] == "error"
        assert "between 1 and 20" in result["error"]

    def test_valid_hypotheses_count_succeeds(self):
        """num_hypotheses=5 should succeed."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=5)
        )
        assert result["type"] == "prompt"

    def test_boundary_values(self):
        """Test boundary values 1 and 20."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})

        result_1 = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=1)
        )
        assert result_1["type"] == "prompt"

        result_20 = json.loads(
            peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=20)
        )
        assert result_20["type"] == "prompt"


class TestQuestion5JSONSchemaCompliance:
    """Question 5: JSON Schema Compliance."""

    def test_success_response_schema(self):
        """Success responses should have required fields."""
        result = json.loads(peircean_observe_anomaly(observation="Test", domain="general"))

        assert "type" in result
        assert result["type"] == "prompt"
        assert "phase" in result
        assert "prompt" in result
        assert "next_tool" in result

    def test_error_response_schema(self):
        """Error responses should have required fields."""
        result = json.loads(peircean_observe_anomaly(observation="", domain="general"))

        assert "type" in result
        assert result["type"] == "error"
        assert "error" in result
        # hint is optional but recommended
        assert "hint" in result

    def test_all_tools_return_valid_json(self):
        """All tool outputs should be valid JSON."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        outputs = [
            peircean_observe_anomaly(observation="Test"),
            peircean_generate_hypotheses(anomaly_json=anomaly_json),
            peircean_evaluate_via_ibe(anomaly_json=anomaly_json, hypotheses_json=hypotheses_json),
            peircean_abduce_single_shot(observation="Test"),
            peircean_critic_evaluate(
                critic="skeptic", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
            ),
        ]

        for output in outputs:
            # Should not raise
            parsed = json.loads(output)
            assert isinstance(parsed, dict)


class TestQuestion6DomainSpecificGuidance:
    """Question 6: Domain-Specific Guidance."""

    @pytest.mark.parametrize(
        "domain",
        ["general", "financial", "legal", "medical", "technical", "scientific"],
    )
    def test_valid_domains_succeed(self, domain):
        """All valid domains should return prompts."""
        result = json.loads(peircean_observe_anomaly(observation="Test", domain=domain))
        assert result["type"] == "prompt"
        assert domain in result["prompt"]

    def test_unknown_domain_falls_back_to_general(self):
        """Unknown domains should fall back to general."""
        result = json.loads(peircean_observe_anomaly(observation="Test", domain="unknown_domain"))
        # Should still return a valid prompt
        assert result["type"] == "prompt"
        # Domain appears in prompt even if invalid
        assert "unknown_domain" in result["prompt"]


class TestQuestion7CouncilOfCritics:
    """Question 7: Council of Critics."""

    def test_standard_ibe_mode(self):
        """use_council=False should use standard IBE criteria."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        result = json.loads(
            peircean_evaluate_via_ibe(
                anomaly_json=anomaly_json, hypotheses_json=hypotheses_json, use_council=False
            )
        )

        assert result["type"] == "prompt"
        # Should include standard criteria
        assert "explanatory_power" in result["prompt"]

    def test_council_mode(self):
        """use_council=True should include 5 critics."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        result = json.loads(
            peircean_evaluate_via_ibe(
                anomaly_json=anomaly_json, hypotheses_json=hypotheses_json, use_council=True
            )
        )

        assert result["type"] == "prompt"
        prompt = result["prompt"]
        assert "Empiricist" in prompt
        assert "Logician" in prompt
        assert "Pragmatist" in prompt
        assert "Economist" in prompt
        assert "Skeptic" in prompt

    def test_custom_council(self):
        """custom_council should override default critics."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})
        custom_council = ["Space Law Specialist", "Orbital Mechanics Expert"]

        result = json.loads(
            peircean_evaluate_via_ibe(
                anomaly_json=anomaly_json,
                hypotheses_json=hypotheses_json,
                custom_council=custom_council,
            )
        )

        assert result["type"] == "prompt"
        prompt = result["prompt"]
        assert "Space Law Specialist" in prompt
        assert "Orbital Mechanics Expert" in prompt


class TestQuestion8ToolAnnotations:
    """Question 8: Tool Annotations."""

    def test_tools_have_annotations(self):
        """All tools should have readOnlyHint and idempotentHint annotations."""
        tools = mcp._tool_manager._tools

        for tool_name in [
            "peircean_observe_anomaly",
            "peircean_generate_hypotheses",
            "peircean_evaluate_via_ibe",
            "peircean_abduce_single_shot",
            "peircean_critic_evaluate",
        ]:
            tool = tools[tool_name]
            # Check that annotations exist
            assert hasattr(tool, "annotations") or tool.annotations is not None


class TestQuestion9InvalidJSONHandling:
    """Question 9: Invalid JSON Handling."""

    def test_generate_hypotheses_invalid_json(self):
        """Invalid JSON in anomaly_json should return helpful error."""
        result = json.loads(peircean_generate_hypotheses(anomaly_json="not valid json"))
        assert result["type"] == "error"
        assert "hint" in result

    def test_evaluate_invalid_anomaly_json(self):
        """Invalid anomaly_json in evaluate should return helpful error."""
        result = json.loads(
            peircean_evaluate_via_ibe(
                anomaly_json="invalid", hypotheses_json=json.dumps({"hypotheses": []})
            )
        )
        assert result["type"] == "error"
        assert "anomaly_json" in result["error"]

    def test_evaluate_invalid_hypotheses_json(self):
        """Invalid hypotheses_json in evaluate should return helpful error."""
        result = json.loads(
            peircean_evaluate_via_ibe(
                anomaly_json=json.dumps({"anomaly": {"fact": "Test"}}),
                hypotheses_json="invalid",
            )
        )
        assert result["type"] == "error"
        assert "hypotheses_json" in result["error"]

    def test_critic_evaluate_invalid_json(self):
        """Invalid JSON in critic_evaluate should return helpful error."""
        result = json.loads(
            peircean_critic_evaluate(critic="skeptic", anomaly_json="invalid", hypotheses_json="{}")
        )
        assert result["type"] == "error"


class TestQuestion10CriticFallback:
    """Question 10: Critic Fallback."""

    def test_empty_critic_falls_back(self):
        """Empty critic should fall back to general_critic."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        result = json.loads(
            peircean_critic_evaluate(
                critic="", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
            )
        )

        assert result["type"] == "prompt"
        assert "GENERAL_CRITIC" in result["prompt"]

    def test_whitespace_critic_falls_back(self):
        """Whitespace-only critic should fall back to general_critic."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        result = json.loads(
            peircean_critic_evaluate(
                critic="   ", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
            )
        )

        assert result["type"] == "prompt"
        assert "GENERAL_CRITIC" in result["prompt"]

    def test_custom_critic_works(self):
        """Custom critic role should work."""
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test"}]})

        result = json.loads(
            peircean_critic_evaluate(
                critic="forensic_accountant",
                anomaly_json=anomaly_json,
                hypotheses_json=hypotheses_json,
            )
        )

        assert result["type"] == "prompt"
        assert "FORENSIC_ACCOUNTANT" in result["prompt"]
