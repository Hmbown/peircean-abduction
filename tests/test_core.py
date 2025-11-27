"""
Tests for Peircean Abduction core functionality.
"""

import json
import pytest

from peircean.core.models import (
    AbductionResult,
    Assumption,
    Domain,
    Hypothesis,
    HypothesisScores,
    Observation,
    SurpriseLevel,
    TestablePrediction,
)
from peircean.core.prompts import (
    format_observation_prompt,
    format_generation_prompt,
    format_single_shot_prompt,
    DOMAIN_GUIDANCE,
)
from peircean.core.agent import (
    AbductionAgent,
    abduction_prompt,
)


class TestModels:
    """Test data models."""
    
    def test_observation_creation(self):
        obs = Observation(
            fact="Stock dropped 5% on good news",
            surprise_level=SurpriseLevel.HIGHLY_SURPRISING,
            surprise_score=0.85,
            domain=Domain.FINANCIAL
        )
        assert obs.fact == "Stock dropped 5% on good news"
        assert obs.surprise_score == 0.85
        assert obs.domain == Domain.FINANCIAL
    
    def test_observation_to_peirce_premise(self):
        obs = Observation(fact="The data is anomalous")
        premise = obs.to_peirce_premise()
        assert "surprising fact is observed" in premise.lower()
        assert "anomalous" in premise.lower()
    
    def test_hypothesis_creation(self):
        h = Hypothesis(
            id="H1",
            statement="The market overreacted",
            explanation="Emotional selling dominated rational analysis",
            prior_probability=0.3,
            assumptions=[
                Assumption(statement="Markets can be irrational"),
            ],
            testable_predictions=[
                TestablePrediction(
                    prediction="Price will recover within 5 days",
                    test_method="Monitor price",
                    expected_outcome_if_true="Recovery to prior level",
                    expected_outcome_if_false="Continued decline"
                )
            ]
        )
        assert h.id == "H1"
        assert h.prior_probability == 0.3
        assert len(h.assumptions) == 1
        assert len(h.testable_predictions) == 1
    
    def test_hypothesis_scores_composite(self):
        scores = HypothesisScores(
            explanatory_scope=0.8,
            explanatory_power=0.9,
            parsimony=0.7,
            testability=0.85,
            consilience=0.75,
            analogy=0.6,
            fertility=0.8
        )
        composite = scores.composite()
        assert 0 <= composite <= 1
        # With default weights, should be reasonable
        assert 0.7 <= composite <= 0.9
    
    def test_hypothesis_scores_custom_weights(self):
        scores = HypothesisScores(
            explanatory_power=1.0,
            parsimony=0.0,
        )
        # Weight only explanatory power
        custom = scores.composite(weights={
            "explanatory_power": 1.0,
            "parsimony": 0.0,
        })
        assert custom == 1.0
    
    def test_abduction_result_markdown(self):
        obs = Observation(
            fact="Test observation",
            surprise_level=SurpriseLevel.SURPRISING,
            surprise_score=0.7
        )
        h = Hypothesis(
            id="H1",
            statement="Test hypothesis",
            explanation="Test explanation",
            scores=HypothesisScores(explanatory_power=0.8)
        )
        result = AbductionResult(
            observation=obs,
            hypotheses=[h],
            selected_hypothesis="H1",
            confidence=0.8
        )
        md = result.to_markdown()
        assert "# Abductive Reasoning Trace" in md
        assert "Test observation" in md
        assert "Test hypothesis" in md


class TestPrompts:
    """Test prompt generation."""
    
    def test_observation_prompt_format(self):
        prompt = format_observation_prompt(
            observation="Server latency spiked",
            context={"time": "14:30 UTC"}
        )
        assert "surprising fact" in prompt.lower()
        assert "Server latency spiked" in prompt
        assert "14:30 UTC" in prompt
    
    def test_generation_prompt_includes_domain_guidance(self):
        obs = Observation(
            fact="Trading volume anomaly",
            domain=Domain.FINANCIAL
        )
        prompt = format_generation_prompt(obs, num_hypotheses=5)
        # Should include financial-specific guidance
        assert "financial" in prompt.lower() or "market" in prompt.lower()
    
    def test_single_shot_prompt_complete(self):
        prompt = format_single_shot_prompt(
            observation="The anomaly to explain",
            domain=Domain.TECHNICAL,
            num_hypotheses=3
        )
        # Should include all phases
        assert "Phase 1" in prompt or "observation" in prompt.lower()
        assert "hypothes" in prompt.lower()
        assert "select" in prompt.lower()
    
    def test_domain_guidance_exists_for_all_domains(self):
        for domain in Domain:
            assert domain in DOMAIN_GUIDANCE or domain == Domain.GENERAL


class TestAgent:
    """Test the AbductionAgent."""
    
    def test_agent_creation(self):
        agent = AbductionAgent(domain="financial", max_hypotheses=5)
        assert agent.domain == Domain.FINANCIAL
        assert agent.max_hypotheses == 5
    
    def test_agent_creation_string_domain(self):
        agent = AbductionAgent(domain="medical")
        assert agent.domain == Domain.MEDICAL
    
    def test_agent_no_llm_raises_error(self):
        agent = AbductionAgent()
        with pytest.raises(RuntimeError, match="No LLM function"):
            import asyncio
            asyncio.run(agent._call_llm("test"))
    
    def test_agent_json_parsing(self):
        agent = AbductionAgent()
        
        # Test clean JSON
        result = agent._parse_json('{"key": "value"}')
        assert result == {"key": "value"}
        
        # Test markdown-wrapped JSON
        result = agent._parse_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}
        
        # Test invalid JSON
        result = agent._parse_json('not json')
        assert result == {}
    
    def test_get_prompts_without_execution(self):
        agent = AbductionAgent(domain="technical")
        
        obs_prompt = agent.get_observation_prompt("Test observation")
        assert "Test observation" in obs_prompt
        
        ss_prompt = agent.get_single_shot_prompt("Test observation")
        assert "Test observation" in ss_prompt


class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    def test_abduction_prompt(self):
        prompt = abduction_prompt(
            observation="Something surprising happened",
            domain="general",
            num_hypotheses=3
        )
        assert "surprising" in prompt.lower()
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be substantial


class TestJSONOutput:
    """Test JSON serialization."""
    
    def test_abduction_result_json_serializable(self):
        obs = Observation(fact="Test")
        h = Hypothesis(
            id="H1",
            statement="Test",
            explanation="Test",
        )
        result = AbductionResult(
            observation=obs,
            hypotheses=[h],
            confidence=0.5
        )
        
        # Should not raise
        json_data = result.to_json_trace()
        json_str = json.dumps(json_data)
        assert isinstance(json_str, str)
        
        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed["observation"]["fact"] == "Test"


# Fixtures for integration tests

@pytest.fixture
def mock_llm():
    """Mock LLM that returns valid JSON responses."""
    def _mock(prompt: str) -> str:
        if "analyzing an observation" in prompt.lower():
            return json.dumps({
                "surprise_level": "high",
                "surprise_score": 0.8,
                "expected_state": "Normal behavior",
                "surprise_source": "Violates expectations"
            })
        elif "generating explanatory hypotheses" in prompt.lower():
            return json.dumps({
                "hypotheses": [
                    {
                        "id": "H1",
                        "statement": "Mock hypothesis",
                        "explanation": "Mock explanation",
                        "prior_probability": 0.5,
                        "assumptions": [{"statement": "Assumption 1"}],
                        "testable_predictions": []
                    }
                ]
            })
        elif "evaluating hypotheses" in prompt.lower():
            return json.dumps({
                "evaluations": [
                    {
                        "hypothesis_id": "H1",
                        "scores": {
                            "explanatory_scope": 0.8,
                            "explanatory_power": 0.7,
                            "parsimony": 0.9,
                            "testability": 0.8,
                            "consilience": 0.7,
                            "analogy": 0.5,
                            "fertility": 0.6
                        }
                    }
                ]
            })
        elif "selecting the best explanation" in prompt.lower():
            return json.dumps({
                "selected_hypothesis": "H1",
                "selection_rationale": "Best overall score",
                "confidence": 0.75,
                "recommended_actions": ["Test assumption 1"]
            })
        else:
            return "{}"
    return _mock


class TestAgentIntegration:
    """Integration tests with mock LLM."""
    
    @pytest.mark.asyncio
    async def test_full_abduction_flow(self, mock_llm):
        agent = AbductionAgent(
            llm_call=mock_llm,
            domain="general",
            max_hypotheses=3
        )
        
        result = await agent.abduce("Test observation")
        
        assert result.observation.fact == "Test observation"
        assert len(result.hypotheses) > 0
        assert result.selected_hypothesis is not None
        assert result.confidence > 0
    
    def test_sync_abduction(self, mock_llm):
        agent = AbductionAgent(
            llm_call=mock_llm,
            domain="technical"
        )
        
        result = agent.abduce_sync("Test observation")
        assert result.selected_hypothesis is not None
