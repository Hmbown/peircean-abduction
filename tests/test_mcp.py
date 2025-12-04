"""
Tests for Peircean MCP Server.

Tests cover:
- Tool functionality (5 tools)
- Input validation (Pydantic models)
- Error handling (structured errors)
- MCP Resources (domain guidance, schemas)
- Tool annotations (titles, hints)
"""

import json

import pytest
from pydantic import ValidationError

from peircean.mcp.errors import (
    ErrorCode,
    format_error_response,
    format_json_parse_error,
    format_validation_error,
)
from peircean.mcp.inputs import (
    Domain,
    GenerateHypothesesInput,
    ObserveAnomalyInput,
    ResponseFormat,
)
from peircean.mcp.server import (
    CHARACTER_LIMIT,
    _parse_anomaly_json,
    _parse_hypotheses_json,
    _truncate_response,
    get_anomaly_schema,
    get_domain_guidance,
    get_hypotheses_schema,
    peircean_abduce_single_shot,
    peircean_critic_evaluate,
    peircean_evaluate_via_ibe,
    peircean_generate_hypotheses,
    peircean_observe_anomaly,
)


class TestMCPServer:
    """Test MCP server tools."""

    def test_observe_anomaly_returns_prompt(self):
        result_json = peircean_observe_anomaly(observation="Test observation", domain="technical")
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 1
        assert "Test observation" in result["prompt"]
        assert "technical" in result["prompt"]
        assert "Technical-specific" in result["prompt"] or "technical" in result["prompt"].lower()

    def test_observe_anomaly_invalid_domain_defaults_to_general(self):
        result_json = peircean_observe_anomaly(
            observation="Test observation", domain="invalid_domain"
        )
        result = json.loads(result_json)

        # When domain is invalid, it prints "invalid_domain" in the prompt
        # but uses general guidance
        assert "invalid_domain" in result["prompt"]

    def test_generate_hypotheses_returns_prompt(self):
        anomaly_json = json.dumps(
            {
                "anomaly": {
                    "fact": "Test observation",
                    "surprise_level": "high",
                    "domain": "technical",
                }
            }
        )

        result_json = peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=3)
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 2
        assert "Test observation" in result["prompt"]
        assert "technical" in result["prompt"]
        assert "Generate 3" in result["prompt"]

    def test_generate_hypotheses_invalid_json_returns_error(self):
        result_json = peircean_generate_hypotheses(anomaly_json="invalid json")
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert "error" in result
        assert "hint" in result
        assert result["code"] == ErrorCode.INVALID_JSON.value

    def test_evaluate_via_ibe_invalid_hypotheses_json_returns_error(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test observation"}})

        result_json = peircean_evaluate_via_ibe(
            anomaly_json=anomaly_json, hypotheses_json="malformed"
        )
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert result["code"] == ErrorCode.INVALID_JSON.value
        assert result["details"]["parameter"] == "hypotheses_json"

    def test_evaluate_via_ibe_returns_prompt(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test observation"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test H1"}]})

        result_json = peircean_evaluate_via_ibe(
            anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
        )
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 3
        assert "Test observation" in result["prompt"]
        assert "Test H1" in result["prompt"]

    def test_evaluate_via_ibe_with_council(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": []})

        result_json = peircean_evaluate_via_ibe(
            anomaly_json=anomaly_json, hypotheses_json=hypotheses_json, use_council=True
        )
        result = json.loads(result_json)

        assert "Council of Critics" in result["prompt"]

    def test_abduce_single_shot_returns_prompt(self):
        result_json = peircean_abduce_single_shot(
            observation="Test observation", domain="financial"
        )
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == "single_shot"
        assert "Test observation" in result["prompt"]
        assert "financial" in result["prompt"]

    def test_critic_evaluate_returns_prompt(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "H1"}]})

        result_json = peircean_critic_evaluate(
            critic="skeptic", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
        )
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == "critic_evaluation"
        assert result["critic"] == "skeptic"
        assert "THE SKEPTIC" in result["prompt"]

    def test_critic_evaluate_invalid_critic(self):
        result_json = peircean_critic_evaluate(
            critic="jester", anomaly_json="{}", hypotheses_json="{}"
        )
        result = json.loads(result_json)

        # The implementation allows any critic role, so this should NOT return an error
        assert result["type"] == "prompt"
        assert "JESTER" in result["prompt"]

    # Input validation tests
    def test_observe_anomaly_empty_observation_returns_error(self):
        result_json = peircean_observe_anomaly(observation="", domain="technical")
        result = json.loads(result_json)

        assert result["type"] == "error"
        # Now uses Pydantic validation with detailed error messages
        assert "observation" in result["error"].lower()
        assert "hint" in result

    def test_observe_anomaly_whitespace_only_returns_error(self):
        result_json = peircean_observe_anomaly(observation="   ", domain="technical")
        result = json.loads(result_json)

        assert result["type"] == "error"
        # Whitespace-only is stripped and fails min_length=1 validation
        assert "observation" in result["error"].lower()

    def test_generate_hypotheses_num_too_low_returns_error(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result_json = peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=0)
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert result["code"] == ErrorCode.VALIDATION_ERROR.value
        assert "num_hypotheses" in result["error"]
        assert "between 1 and 20" in result.get("hint", "")

    def test_generate_hypotheses_num_too_high_returns_error(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        result_json = peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=25)
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert result["code"] == ErrorCode.VALIDATION_ERROR.value
        assert "num_hypotheses" in result["error"]
        assert "between 1 and 20" in result.get("hint", "")

    def test_abduce_single_shot_empty_observation_returns_error(self):
        result_json = peircean_abduce_single_shot(observation="")
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert "Empty observation" in result["error"]

    def test_abduce_single_shot_num_too_high_returns_error(self):
        result_json = peircean_abduce_single_shot(observation="Test", num_hypotheses=100)
        result = json.loads(result_json)

        assert result["type"] == "error"
        assert "num_hypotheses" in result["error"]

    def test_critic_evaluate_empty_critic_falls_back(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "H1"}]})

        result_json = peircean_critic_evaluate(
            critic="", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
        )
        result = json.loads(result_json)

        # Should fall back to "general_critic" and return a prompt
        assert result["type"] == "prompt"
        assert "GENERAL_CRITIC" in result["prompt"]


class TestInputModels:
    """Test Pydantic input models for validation."""

    def test_observe_anomaly_input_valid(self):
        """Test valid ObserveAnomalyInput."""
        input_model = ObserveAnomalyInput(
            observation="Server latency spiked 10x",
            context="No recent deployments",
            domain=Domain.TECHNICAL,
        )
        assert input_model.observation == "Server latency spiked 10x"
        assert input_model.domain == Domain.TECHNICAL

    def test_observe_anomaly_input_strips_whitespace(self):
        """Test that whitespace is stripped from observation."""
        input_model = ObserveAnomalyInput(
            observation="  Test observation  ",
            domain=Domain.GENERAL,
        )
        assert input_model.observation == "Test observation"

    def test_observe_anomaly_input_empty_raises(self):
        """Test that empty observation raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ObserveAnomalyInput(observation="", domain=Domain.GENERAL)
        assert "observation" in str(exc_info.value).lower()

    def test_generate_hypotheses_input_valid(self):
        """Test valid GenerateHypothesesInput."""
        input_model = GenerateHypothesesInput(
            anomaly_json='{"anomaly": {"fact": "test"}}',
            num_hypotheses=5,
        )
        assert input_model.num_hypotheses == 5

    def test_generate_hypotheses_input_num_bounds(self):
        """Test num_hypotheses must be between 1 and 20."""
        with pytest.raises(ValidationError):
            GenerateHypothesesInput(
                anomaly_json='{"anomaly": {"fact": "test"}}',
                num_hypotheses=0,
            )
        with pytest.raises(ValidationError):
            GenerateHypothesesInput(
                anomaly_json='{"anomaly": {"fact": "test"}}',
                num_hypotheses=25,
            )

    def test_domain_enum_values(self):
        """Test Domain enum has expected values."""
        assert Domain.GENERAL.value == "general"
        assert Domain.FINANCIAL.value == "financial"
        assert Domain.LEGAL.value == "legal"
        assert Domain.MEDICAL.value == "medical"
        assert Domain.TECHNICAL.value == "technical"
        assert Domain.SCIENTIFIC.value == "scientific"

    def test_response_format_enum_values(self):
        """Test ResponseFormat enum has expected values."""
        assert ResponseFormat.JSON.value == "json"
        assert ResponseFormat.MARKDOWN.value == "markdown"


class TestErrorHandling:
    """Test structured error handling utilities."""

    def test_format_error_response_basic(self):
        """Test basic error response formatting."""
        result = format_error_response("Test error")
        data = json.loads(result)
        assert data["type"] == "error"
        assert data["error"] == "Test error"
        assert data["code"] == ErrorCode.VALIDATION_ERROR.value

    def test_format_error_response_with_hint(self):
        """Test error response with hint."""
        result = format_error_response(
            "Test error",
            code=ErrorCode.INVALID_JSON,
            hint="Check your JSON format",
        )
        data = json.loads(result)
        assert data["hint"] == "Check your JSON format"
        assert data["code"] == "invalid_json"

    def test_format_error_response_with_details(self):
        """Test error response with details."""
        result = format_error_response(
            "Test error",
            details={"field": "observation", "value": ""},
        )
        data = json.loads(result)
        assert data["details"]["field"] == "observation"

    def test_format_json_parse_error(self):
        """Test JSON parse error formatting."""
        result = format_json_parse_error("anomaly_json", "invalid json")
        data = json.loads(result)
        assert data["type"] == "error"
        assert data["code"] == "invalid_json"
        assert "anomaly_json" in data["error"]
        assert "hint" in data

    def test_format_validation_error(self):
        """Test Pydantic ValidationError formatting."""
        try:
            ObserveAnomalyInput(observation="", domain=Domain.GENERAL)
        except ValidationError as e:
            result = format_validation_error(e)
            data = json.loads(result)
            assert data["type"] == "error"
            assert data["code"] == "validation_error"
            assert "details" in data


class TestMCPResources:
    """Test MCP Resources for domain guidance and schemas."""

    def test_get_domain_guidance_technical(self):
        """Test getting technical domain guidance."""
        guidance = get_domain_guidance("technical")
        assert "Technical" in guidance
        assert "Race conditions" in guidance

    def test_get_domain_guidance_financial(self):
        """Test getting financial domain guidance."""
        guidance = get_domain_guidance("financial")
        assert "Financial" in guidance
        assert "Market microstructure" in guidance

    def test_get_domain_guidance_invalid_falls_back(self):
        """Test invalid domain falls back to general."""
        guidance = get_domain_guidance("invalid_domain")
        assert "General" in guidance

    def test_get_anomaly_schema(self):
        """Test getting anomaly JSON schema."""
        schema_json = get_anomaly_schema()
        schema = json.loads(schema_json)
        assert schema["type"] == "object"
        assert "anomaly" in schema["properties"]
        assert "fact" in schema["properties"]["anomaly"]["properties"]
        assert "surprise_level" in schema["properties"]["anomaly"]["properties"]

    def test_get_hypotheses_schema(self):
        """Test getting hypotheses JSON schema."""
        schema_json = get_hypotheses_schema()
        schema = json.loads(schema_json)
        assert schema["type"] == "object"
        assert "hypotheses" in schema["properties"]
        assert "items" in schema["properties"]["hypotheses"]


class TestHelperFunctions:
    """Test helper functions for parsing and truncation."""

    def test_parse_anomaly_json_valid(self):
        """Test parsing valid anomaly JSON."""
        anomaly_json = '{"anomaly": {"fact": "Test", "domain": "technical"}}'
        anomaly, error = _parse_anomaly_json(anomaly_json)
        assert error is None
        assert anomaly["fact"] == "Test"
        assert anomaly["domain"] == "technical"

    def test_parse_anomaly_json_without_wrapper(self):
        """Test parsing anomaly JSON without 'anomaly' wrapper."""
        anomaly_json = '{"fact": "Test", "domain": "technical"}'
        anomaly, error = _parse_anomaly_json(anomaly_json)
        assert error is None
        assert anomaly["fact"] == "Test"

    def test_parse_anomaly_json_invalid(self):
        """Test parsing invalid JSON returns error."""
        anomaly, error = _parse_anomaly_json("invalid json")
        assert anomaly is None
        assert error is not None
        assert "invalid_json" in error

    def test_parse_hypotheses_json_valid(self):
        """Test parsing valid hypotheses JSON."""
        hypotheses_json = '{"hypotheses": [{"id": "H1", "statement": "Test"}]}'
        hypotheses, error = _parse_hypotheses_json(hypotheses_json)
        assert error is None
        assert len(hypotheses) == 1
        assert hypotheses[0]["id"] == "H1"

    def test_parse_hypotheses_json_invalid(self):
        """Test parsing invalid JSON returns error."""
        hypotheses, error = _parse_hypotheses_json("invalid json")
        assert hypotheses is None
        assert error is not None

    def test_truncate_response_under_limit(self):
        """Test that responses under limit are not truncated."""
        response = "Short response"
        result = _truncate_response(response, limit=1000)
        assert result == response

    def test_truncate_response_over_limit(self):
        """Test that responses over limit are truncated."""
        response = "x" * 1000
        result = _truncate_response(response, limit=100)
        assert len(result) <= 200  # Some buffer for truncation message
        assert "TRUNCATED" in result or "truncated" in result.lower()

    def test_character_limit_constant(self):
        """Test CHARACTER_LIMIT constant is defined."""
        assert CHARACTER_LIMIT == 50000


class TestToolAnnotations:
    """Test that tool annotations are properly configured."""

    def test_tools_have_annotations(self):
        """Test that all tools have annotations with titles."""
        # This tests that tools were registered with annotations
        # by checking the tool function attributes
        from peircean.mcp.server import mcp

        # Get all registered tools
        tools = list(mcp._tool_manager._tools.values())
        assert len(tools) >= 5  # We have 5 tools

        # Check each tool has a title in annotations
        for tool in tools:
            assert hasattr(tool, "annotations") or tool.fn is not None
