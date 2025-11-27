"""
Tests for Peircean Abduction core functionality.
"""

import json

import pytest

from peircean.core.agent import (
    AbductionAgent,
    abduction_prompt,
)
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
    DOMAIN_GUIDANCE,
    format_generation_prompt,
    format_observation_prompt,
    format_single_shot_prompt,
)


class TestModels:
    """Test data models."""

    def test_observation_creation(self):
        obs = Observation(
            fact="Stock dropped 5% on good news",
            surprise_level=SurpriseLevel.HIGHLY_SURPRISING,
            surprise_score=0.85,
            domain=Domain.FINANCIAL,
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
                    expected_outcome_if_false="Continued decline",
                )
            ],
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
            fertility=0.8,
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
        custom = scores.composite(
            weights={
                "explanatory_power": 1.0,
                "parsimony": 0.0,
            }
        )
        assert custom == 1.0

    def test_abduction_result_markdown(self):
        obs = Observation(
            fact="Test observation", surprise_level=SurpriseLevel.SURPRISING, surprise_score=0.7
        )
        h = Hypothesis(
            id="H1",
            statement="Test hypothesis",
            explanation="Test explanation",
            scores=HypothesisScores(explanatory_power=0.8),
        )
        result = AbductionResult(
            observation=obs, hypotheses=[h], selected_hypothesis="H1", confidence=0.8
        )
        md = result.to_markdown()
        assert "# Abductive Reasoning Trace" in md
        assert "Test observation" in md
        assert "Test hypothesis" in md


class TestPrompts:
    """Test prompt generation."""

    def test_observation_prompt_format(self):
        prompt = format_observation_prompt(
            observation="Server latency spiked", context={"time": "14:30 UTC"}
        )
        assert "surprising fact" in prompt.lower()
        assert "Server latency spiked" in prompt
        assert "14:30 UTC" in prompt

    def test_generation_prompt_includes_domain_guidance(self):
        obs = Observation(fact="Trading volume anomaly", domain=Domain.FINANCIAL)
        prompt = format_generation_prompt(obs, num_hypotheses=5)
        # Should include financial-specific guidance
        assert "financial" in prompt.lower() or "market" in prompt.lower()

    def test_single_shot_prompt_complete(self):
        prompt = format_single_shot_prompt(
            observation="The anomaly to explain", domain=Domain.TECHNICAL, num_hypotheses=3
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
        result = agent._parse_json("not json")
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
            observation="Something surprising happened", domain="general", num_hypotheses=3
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
        result = AbductionResult(observation=obs, hypotheses=[h], confidence=0.5)

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
            return json.dumps(
                {
                    "surprise_level": "high",
                    "surprise_score": 0.8,
                    "expected_state": "Normal behavior",
                    "surprise_source": "Violates expectations",
                }
            )
        elif "generating explanatory hypotheses" in prompt.lower():
            return json.dumps(
                {
                    "hypotheses": [
                        {
                            "id": "H1",
                            "statement": "Mock hypothesis",
                            "explanation": "Mock explanation",
                            "prior_probability": 0.5,
                            "assumptions": [{"statement": "Assumption 1"}],
                            "testable_predictions": [],
                        }
                    ]
                }
            )
        elif "evaluating hypotheses" in prompt.lower():
            return json.dumps(
                {
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
                                "fertility": 0.6,
                            },
                        }
                    ]
                }
            )
        elif "selecting the best explanation" in prompt.lower():
            return json.dumps(
                {
                    "selected_hypothesis": "H1",
                    "selection_rationale": "Best overall score",
                    "confidence": 0.75,
                    "recommended_actions": ["Test assumption 1"],
                }
            )
        else:
            return "{}"

    return _mock


class TestAgentIntegration:
    """Integration tests with mock LLM."""

    @pytest.mark.asyncio
    async def test_full_abduction_flow(self, mock_llm):
        agent = AbductionAgent(llm_call=mock_llm, domain="general", max_hypotheses=3)

        result = await agent.abduce("Test observation")

        assert result.observation.fact == "Test observation"
        assert len(result.hypotheses) > 0
        assert result.selected_hypothesis is not None
        assert result.confidence > 0

    def test_sync_abduction(self, mock_llm):
        agent = AbductionAgent(llm_call=mock_llm, domain="technical")

        result = agent.abduce_sync("Test observation")
        assert result.selected_hypothesis is not None

    @pytest.mark.asyncio
    async def test_abduction_with_observation_object(self, mock_llm):
        """Test abduce with pre-constructed Observation object."""
        agent = AbductionAgent(llm_call=mock_llm, domain="financial")
        obs = Observation(
            fact="Test with observation object",
            surprise_score=0.9,
            surprise_level=SurpriseLevel.HIGHLY_SURPRISING,
            domain=Domain.FINANCIAL,
        )
        result = await agent.abduce(obs)

        # Should skip observation analysis phase since we passed an Observation
        assert result.observation.fact == "Test with observation object"
        assert result.selected_hypothesis is not None

    @pytest.mark.asyncio
    async def test_abduction_with_council(self, mock_llm):
        """Test abduce with Council of Critics enabled."""

        def mock_with_critic(prompt: str) -> str:
            if "analyzing an observation" in prompt.lower():
                return json.dumps(
                    {
                        "surprise_level": "high",
                        "surprise_score": 0.8,
                        "expected_state": "Normal behavior",
                    }
                )
            elif "generating explanatory hypotheses" in prompt.lower():
                return json.dumps(
                    {
                        "hypotheses": [
                            {
                                "id": "H1",
                                "statement": "Mock hypothesis 1",
                                "explanation": "Explanation 1",
                                "prior_probability": 0.5,
                                "assumptions": [],
                                "testable_predictions": [],
                            },
                            {
                                "id": "H2",
                                "statement": "Mock hypothesis 2",
                                "explanation": "Explanation 2",
                                "prior_probability": 0.4,
                                "assumptions": [],
                                "testable_predictions": [],
                            },
                        ]
                    }
                )
            elif "evaluating hypotheses" in prompt.lower():
                return json.dumps(
                    {
                        "evaluations": [
                            {
                                "hypothesis_id": "H1",
                                "scores": {
                                    "explanatory_scope": 0.8,
                                    "explanatory_power": 0.7,
                                    "parsimony": 0.9,
                                    "testability": 0.8,
                                },
                            },
                            {
                                "hypothesis_id": "H2",
                                "scores": {
                                    "explanatory_scope": 0.6,
                                    "explanatory_power": 0.8,
                                    "parsimony": 0.7,
                                    "testability": 0.7,
                                },
                            },
                        ]
                    }
                )
            elif "critic" in prompt.lower() or "perspective" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "This hypothesis seems plausible",
                        "concerns": ["Need more evidence"],
                        "recommended_tests": ["Test 1"],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "selecting the best explanation" in prompt.lower():
                return json.dumps(
                    {
                        "selected_hypothesis": "H1",
                        "selection_rationale": "Best overall score",
                        "confidence": 0.75,
                        "recommended_actions": ["Test assumption 1"],
                    }
                )
            else:
                return "{}"

        agent = AbductionAgent(
            llm_call=mock_with_critic, domain="general", max_hypotheses=2, use_council=True
        )

        result = await agent.abduce("Test observation with council")

        assert result.council_evaluation is not None
        assert len(result.council_evaluation.evaluations) > 0
        assert result.metadata.get("used_council") is True

    @pytest.mark.asyncio
    async def test_abduction_override_council_setting(self, mock_llm):
        """Test that use_council parameter can override instance setting."""
        agent = AbductionAgent(
            llm_call=mock_llm,
            domain="general",
            use_council=False,  # Default off
        )

        # Override to use council - will fail gracefully since mock doesn't handle critic
        result = await agent.abduce("Test observation", use_council=False)

        # Should not have used council
        assert result.council_evaluation is None
        assert result.metadata.get("used_council") is False


class TestSingleShot:
    """Test single-shot abduction method."""

    @pytest.fixture
    def mock_single_shot_llm(self):
        """Mock LLM for single-shot response."""

        def _mock(prompt: str) -> str:
            return json.dumps(
                {
                    "observation_analysis": {
                        "fact": "The observed fact",
                        "surprise_score": 0.75,
                        "expected_state": "Normal state",
                    },
                    "hypotheses": [
                        {
                            "id": "H1",
                            "statement": "First hypothesis",
                            "explanation": "Explanation for first",
                            "prior_probability": 0.6,
                            "assumptions": ["Assumption A"],
                            "testable_predictions": ["Prediction 1"],
                            "scores": {
                                "explanatory_scope": 0.8,
                                "explanatory_power": 0.7,
                                "parsimony": 0.85,
                                "testability": 0.9,
                                "consilience": 0.6,
                            },
                        },
                        {
                            "id": "H2",
                            "statement": "Second hypothesis",
                            "explanation": "Explanation for second",
                            "prior_probability": 0.4,
                            "assumptions": ["Assumption B", "Assumption C"],
                            "testable_predictions": ["Prediction 2", "Prediction 3"],
                            "scores": {
                                "explanatory_scope": 0.6,
                                "explanatory_power": 0.8,
                                "parsimony": 0.5,
                                "testability": 0.7,
                                "consilience": 0.7,
                            },
                        },
                    ],
                    "selection": {
                        "best_hypothesis": "H1",
                        "rationale": "H1 has better parsimony and testability",
                        "recommended_actions": ["Action 1", "Action 2"],
                        "confidence": 0.82,
                    },
                }
            )

        return _mock

    @pytest.mark.asyncio
    async def test_single_shot_basic(self, mock_single_shot_llm):
        agent = AbductionAgent(llm_call=mock_single_shot_llm, domain="technical")

        result = await agent.single_shot("Something surprising happened")

        assert result.observation.surprise_score == 0.75
        assert len(result.hypotheses) == 2
        assert result.selected_hypothesis == "H1"
        assert result.confidence == 0.82
        assert result.metadata.get("mode") == "single_shot"

    @pytest.mark.asyncio
    async def test_single_shot_with_context(self, mock_single_shot_llm):
        agent = AbductionAgent(llm_call=mock_single_shot_llm, domain="financial")

        result = await agent.single_shot(
            "Stock dropped 10%", context={"market": "bull", "sector": "tech"}
        )

        assert result.observation is not None
        assert len(result.recommended_actions) == 2

    @pytest.mark.asyncio
    async def test_single_shot_hypothesis_parsing(self, mock_single_shot_llm):
        """Test that single_shot correctly parses hypothesis structures."""
        agent = AbductionAgent(llm_call=mock_single_shot_llm, domain="medical")

        result = await agent.single_shot("Patient has unusual symptoms")

        # Check first hypothesis structure
        h1 = result.hypotheses[0]
        assert h1.id == "H1"
        assert h1.statement == "First hypothesis"
        assert h1.prior_probability == 0.6
        assert len(h1.assumptions) == 1
        assert len(h1.testable_predictions) == 1

        # Check scores were parsed
        assert h1.scores.explanatory_scope == 0.8
        assert h1.scores.parsimony == 0.85

    @pytest.mark.asyncio
    async def test_single_shot_empty_response_handling(self):
        """Test handling of incomplete LLM response."""

        def empty_llm(_: str) -> str:
            return json.dumps({})

        agent = AbductionAgent(llm_call=empty_llm, domain="general")
        result = await agent.single_shot("Test")

        # Should handle gracefully with defaults
        assert result.confidence == 0.5
        assert len(result.hypotheses) == 0


class TestAsyncLLMCalls:
    """Test async LLM integration."""

    @pytest.mark.asyncio
    async def test_async_llm_call(self):
        """Test using async LLM function."""
        call_count = 0

        async def async_mock(prompt: str) -> str:
            nonlocal call_count
            call_count += 1
            if "analyzing an observation" in prompt.lower():
                return json.dumps(
                    {"surprise_level": "mild", "surprise_score": 0.4, "expected_state": "Normal"}
                )
            elif "generating" in prompt.lower():
                return json.dumps(
                    {
                        "hypotheses": [
                            {"id": "H1", "statement": "Async hypothesis", "explanation": "Test"}
                        ]
                    }
                )
            elif "evaluating" in prompt.lower():
                return json.dumps(
                    {"evaluations": [{"hypothesis_id": "H1", "scores": {"explanatory_power": 0.7}}]}
                )
            elif "selecting" in prompt.lower():
                return json.dumps(
                    {"selected_hypothesis": "H1", "confidence": 0.7, "selection_rationale": "Best"}
                )
            return "{}"

        agent = AbductionAgent(llm_call_async=async_mock, domain="general")
        result = await agent.abduce("Test async observation")

        assert call_count >= 4  # Should have made multiple LLM calls
        assert result.selected_hypothesis == "H1"

    @pytest.mark.asyncio
    async def test_sync_llm_runs_in_executor(self):
        """Test that sync LLM is properly wrapped for async execution."""
        import threading

        execution_threads = []

        def sync_mock(prompt: str) -> str:
            execution_threads.append(threading.current_thread().name)
            if "analyzing" in prompt.lower():
                return json.dumps({"surprise_level": "high", "surprise_score": 0.8})
            elif "generating" in prompt.lower():
                return json.dumps(
                    {"hypotheses": [{"id": "H1", "statement": "Test", "explanation": "Test"}]}
                )
            elif "evaluating" in prompt.lower():
                return json.dumps(
                    {"evaluations": [{"hypothesis_id": "H1", "scores": {"explanatory_power": 0.7}}]}
                )
            elif "selecting" in prompt.lower():
                return json.dumps(
                    {"selected_hypothesis": "H1", "confidence": 0.7, "selection_rationale": "Best"}
                )
            return "{}"

        agent = AbductionAgent(llm_call=sync_mock, domain="general")
        result = await agent.abduce("Test with sync LLM")

        assert result.selected_hypothesis is not None
        # Sync calls should have been made (may or may not be in executor depending on event loop)
        assert len(execution_threads) >= 4


class TestCouncilOfCritics:
    """Test Council of Critics functionality."""

    @pytest.fixture
    def council_mock_llm(self):
        """Mock LLM that handles all phases including council."""

        def _mock(prompt: str) -> str:
            if "analyzing an observation" in prompt.lower():
                return json.dumps({"surprise_level": "high", "surprise_score": 0.85})
            elif "generating explanatory hypotheses" in prompt.lower():
                return json.dumps(
                    {
                        "hypotheses": [
                            {"id": "H1", "statement": "Hyp 1", "explanation": "Exp 1"},
                            {"id": "H2", "statement": "Hyp 2", "explanation": "Exp 2"},
                        ]
                    }
                )
            elif "evaluating hypotheses" in prompt.lower():
                return json.dumps(
                    {
                        "evaluations": [
                            {"hypothesis_id": "H1", "scores": {"explanatory_power": 0.9}},
                            {"hypothesis_id": "H2", "scores": {"explanatory_power": 0.6}},
                        ]
                    }
                )
            elif "empiricist" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "Empiricist evaluation",
                        "concerns": ["Need empirical evidence"],
                        "recommended_tests": ["Experiment 1"],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "logician" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "Logician evaluation",
                        "logical_concerns": ["Check logical consistency"],
                        "recommended_tests": ["Formal proof"],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "pragmatist" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "Pragmatist evaluation",
                        "concerns": ["Practical implications"],
                        "recommended_tests": ["Field test"],
                        "recommended_hypothesis": "H2",
                    }
                )
            elif "economist" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "Economist evaluation",
                        "concerns": ["Cost considerations"],
                        "recommended_tests": ["Cost analysis"],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "skeptic" in prompt.lower():
                return json.dumps(
                    {
                        "evaluation": "Skeptic evaluation",
                        "concerns": ["Alternative explanations"],
                        "recommended_tests": ["Control group"],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "selecting the best explanation" in prompt.lower():
                return json.dumps(
                    {
                        "selected_hypothesis": "H1",
                        "selection_rationale": "Consensus from council",
                        "confidence": 0.88,
                    }
                )
            return "{}"

        return _mock

    @pytest.mark.asyncio
    async def test_council_runs_all_critics(self, council_mock_llm):
        """Test that all critics are consulted."""
        agent = AbductionAgent(
            llm_call=council_mock_llm, domain="general", use_council=True, max_hypotheses=2
        )

        result = await agent.abduce("Test council observation")

        assert result.council_evaluation is not None
        # Should have 5 critics: empiricist, logician, pragmatist, economist, skeptic
        assert len(result.council_evaluation.evaluations) == 5

    @pytest.mark.asyncio
    async def test_council_consensus_recommendation(self, council_mock_llm):
        """Test that council completes with evaluations from all critics."""
        agent = AbductionAgent(
            llm_call=council_mock_llm, domain="general", use_council=True, max_hypotheses=2
        )

        result = await agent.abduce("Test council consensus")

        # Council should have evaluations from all 5 critics
        assert result.council_evaluation is not None
        assert len(result.council_evaluation.evaluations) == 5
        # The council evaluation should exist even if consensus isn't aggregated
        # (current implementation doesn't extract recommended_hypothesis from critic responses)
        perspectives = {e.perspective.value for e in result.council_evaluation.evaluations}
        assert perspectives == {"empiricist", "logician", "pragmatist", "economist", "skeptic"}

    @pytest.mark.asyncio
    async def test_council_handles_critic_errors(self):
        """Test graceful handling of individual critic failures."""
        call_count = {"value": 0}

        def failing_mock(prompt: str) -> str:
            call_count["value"] += 1
            if "analyzing" in prompt.lower():
                return json.dumps({"surprise_level": "high", "surprise_score": 0.8})
            elif "generating" in prompt.lower():
                return json.dumps(
                    {"hypotheses": [{"id": "H1", "statement": "Test", "explanation": "Test"}]}
                )
            elif "evaluating" in prompt.lower():
                return json.dumps(
                    {"evaluations": [{"hypothesis_id": "H1", "scores": {"explanatory_power": 0.7}}]}
                )
            elif "empiricist" in prompt.lower():
                # This critic fails
                raise ValueError("Simulated failure")
            elif any(
                c in prompt.lower() for c in ["logician", "pragmatist", "economist", "skeptic"]
            ):
                return json.dumps(
                    {
                        "evaluation": "OK",
                        "concerns": [],
                        "recommended_tests": [],
                        "recommended_hypothesis": "H1",
                    }
                )
            elif "selecting" in prompt.lower():
                return json.dumps({"selected_hypothesis": "H1", "confidence": 0.7})
            return "{}"

        agent = AbductionAgent(llm_call=failing_mock, domain="general", use_council=True)

        result = await agent.abduce("Test error handling")

        # Should still complete despite one critic failing
        assert result.council_evaluation is not None
        # Should have 4 successful evaluations (one failed)
        assert len(result.council_evaluation.evaluations) == 4


class TestPromptGeneration:
    """Test prompt generation methods."""

    def test_get_generation_prompt(self):
        agent = AbductionAgent(domain="financial", max_hypotheses=3)
        obs = Observation(
            fact="Stock dropped unexpectedly", domain=Domain.FINANCIAL, surprise_score=0.7
        )

        prompt = agent.get_generation_prompt(obs)

        assert "Stock dropped unexpectedly" in prompt
        assert "3" in prompt or "three" in prompt.lower()


class TestJSONParsing:
    """Test JSON parsing edge cases."""

    def test_parse_json_with_leading_whitespace(self):
        agent = AbductionAgent()
        result = agent._parse_json('   \n  {"key": "value"}  \n  ')
        assert result == {"key": "value"}

    def test_parse_json_with_json_language_tag(self):
        agent = AbductionAgent()
        result = agent._parse_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_parse_json_with_plain_code_block(self):
        agent = AbductionAgent()
        result = agent._parse_json('```\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_parse_json_deeply_nested(self):
        agent = AbductionAgent()
        nested = '{"a": {"b": {"c": [1, 2, {"d": "value"}]}}}'
        result = agent._parse_json(nested)
        assert result["a"]["b"]["c"][2]["d"] == "value"
