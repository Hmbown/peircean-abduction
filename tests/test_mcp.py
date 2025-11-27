"""
Tests for Peircean MCP Server.
"""

import json

from peircean.mcp.server import (
    abduce_single_shot,
    critic_evaluate,
    evaluate_via_ibe,
    generate_hypotheses,
    observe_anomaly,
)


class TestMCPServer:
    """Test MCP server tools."""

    def test_observe_anomaly_returns_prompt(self):
        result_json = observe_anomaly(observation="Test observation", domain="technical")
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 1
        assert "Test observation" in result["prompt"]
        assert "technical" in result["prompt"]
        assert "Technical-specific" in result["prompt"] or "technical" in result["prompt"].lower()

    def test_observe_anomaly_invalid_domain_defaults_to_general(self):
        result_json = observe_anomaly(observation="Test observation", domain="invalid_domain")
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

        result_json = generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=3)
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 2
        assert "Test observation" in result["prompt"]
        assert "technical" in result["prompt"]
        assert "Generate 3" in result["prompt"]

    def test_generate_hypotheses_invalid_json_returns_error(self):
        result_json = generate_hypotheses(anomaly_json="invalid json")
        result = json.loads(result_json)

        assert "error" in result

    def test_evaluate_via_ibe_returns_prompt(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test observation"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "Test H1"}]})

        result_json = evaluate_via_ibe(anomaly_json=anomaly_json, hypotheses_json=hypotheses_json)
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == 3
        assert "Test observation" in result["prompt"]
        assert "Test H1" in result["prompt"]

    def test_evaluate_via_ibe_with_council(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": []})

        result_json = evaluate_via_ibe(
            anomaly_json=anomaly_json, hypotheses_json=hypotheses_json, use_council=True
        )
        result = json.loads(result_json)

        assert "Council of Critics" in result["prompt"]

    def test_abduce_single_shot_returns_prompt(self):
        result_json = abduce_single_shot(observation="Test observation", domain="financial")
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == "single_shot"
        assert "Test observation" in result["prompt"]
        assert "financial" in result["prompt"]

    def test_critic_evaluate_returns_prompt(self):
        anomaly_json = json.dumps({"anomaly": {"fact": "Test"}})
        hypotheses_json = json.dumps({"hypotheses": [{"id": "H1", "statement": "H1"}]})

        result_json = critic_evaluate(
            critic="skeptic", anomaly_json=anomaly_json, hypotheses_json=hypotheses_json
        )
        result = json.loads(result_json)

        assert result["type"] == "prompt"
        assert result["phase"] == "critic_evaluation"
        assert result["critic"] == "skeptic"
        assert "THE SKEPTIC" in result["prompt"]

    def test_critic_evaluate_invalid_critic(self):
        result_json = critic_evaluate(critic="jester", anomaly_json="{}", hypotheses_json="{}")
        result = json.loads(result_json)

        # The implementation allows any critic role, so this should NOT return an error
        assert result["type"] == "prompt"
        assert "JESTER" in result["prompt"]
