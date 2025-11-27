"""
Peircean Abduction: Core Agent

The AbductionAgent orchestrates the three-phase abductive reasoning process:
1. Observation Analysis - Identify and characterize the surprising fact
2. Hypothesis Generation - Generate multiple explanatory hypotheses (retroduction)
3. Selection - Infer the best explanation using IBE criteria

"Abduction is the process of forming explanatory hypotheses.
It is the only logical operation which introduces any new idea."
— C.S. Peirce, CP 5.172
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any, cast

from .models import (
    AbductionResult,
    Assumption,
    CouncilEvaluation,
    CriticEvaluation,
    CriticPerspective,
    Domain,
    Hypothesis,
    HypothesisScores,
    Observation,
    ReasoningStep,
    SurpriseLevel,
    TestablePrediction,
)
from .prompts import (
    format_critic_prompt,
    format_evaluation_prompt,
    format_generation_prompt,
    format_observation_prompt,
    format_selection_prompt,
    format_single_shot_prompt,
)

logger = logging.getLogger(__name__)


class AbductionAgent:
    """
    Agent for performing Peircean abductive reasoning.

    Wraps any LLM backend to perform structured abduction:
    Observation → Hypothesis Generation → Inference to Best Explanation

    Example:
        agent = AbductionAgent(domain="financial")
        result = await agent.abduce(
            "NVIDIA dropped 8% on record earnings announcement"
        )
        print(result.selected_hypothesis)
    """

    def __init__(
        self,
        *,
        llm_call: Callable[[str], str] | None = None,
        llm_call_async: Callable[[str], Any] | None = None,
        domain: Domain | str = Domain.GENERAL,
        max_hypotheses: int = 5,
        selection_weights: dict[str, float] | None = None,
        use_council: bool = False,
        timeout: float = 60.0,
    ):
        """
        Initialize the AbductionAgent.

        Args:
            llm_call: Synchronous function that takes a prompt and returns response
            llm_call_async: Async function that takes a prompt and returns response
            domain: Domain context for hypothesis templates
            max_hypotheses: Number of hypotheses to generate (default 5)
            selection_weights: Custom IBE criterion weights
            use_council: Whether to use the Council of Critics
            timeout: Timeout for LLM calls in seconds
        """
        self.llm_call = llm_call
        self.llm_call_async = llm_call_async
        self.domain = Domain(domain) if isinstance(domain, str) else domain
        self.max_hypotheses = max_hypotheses
        self.use_council = use_council
        self.timeout = timeout

        # Default IBE weights following Peirce's economy of research
        self.selection_weights = selection_weights or {
            "explanatory_scope": 0.15,
            "explanatory_power": 0.25,
            "parsimony": 0.20,
            "testability": 0.15,
            "consilience": 0.10,
            "analogy": 0.05,
            "fertility": 0.10,
        }

    # =========================================================================
    # MAIN ENTRY POINTS
    # =========================================================================

    async def abduce(
        self,
        observation: str | Observation,
        context: dict[str, Any] | None = None,
        use_council: bool | None = None,
    ) -> AbductionResult:
        """
        Perform complete abductive reasoning on an observation.

        This is the main async entry point that runs all three phases:
        1. Observation analysis
        2. Hypothesis generation
        3. Evaluation and selection

        Args:
            observation: The surprising fact (string or Observation object)
            context: Additional context for reasoning
            use_council: Override instance setting for Council of Critics

        Returns:
            AbductionResult with full reasoning trace
        """
        start_time = time.time()
        reasoning_trace = []

        # Phase 1: Analyze the observation
        if isinstance(observation, str):
            obs = await self._analyze_observation(observation, context)
        else:
            obs = observation

        reasoning_trace.append(
            ReasoningStep(
                phase="observation",
                description=f"Analyzed observation: {obs.surprise_level.value} (score: {obs.surprise_score:.2f})",
                output_data={"surprise_score": obs.surprise_score},
            )
        )

        # Phase 2: Generate hypotheses
        hypotheses = await self._generate_hypotheses(obs, context)

        reasoning_trace.append(
            ReasoningStep(
                phase="generation",
                description=f"Generated {len(hypotheses)} hypotheses",
                output_data={"hypothesis_count": len(hypotheses)},
            )
        )

        # Phase 3a: Evaluate hypotheses
        evaluated = await self._evaluate_hypotheses(obs, hypotheses)

        reasoning_trace.append(
            ReasoningStep(
                phase="evaluation",
                description="Evaluated hypotheses using IBE criteria",
                output_data={h.id: h.composite_score for h in evaluated},
            )
        )

        # Phase 3b: Council evaluation (optional)
        council_eval = None
        should_use_council = use_council if use_council is not None else self.use_council
        if should_use_council:
            council_eval = await self._run_council(obs, evaluated)
            reasoning_trace.append(
                ReasoningStep(
                    phase="council",
                    description="Council of Critics evaluation complete",
                    output_data={"recommended": council_eval.recommended_hypothesis},
                )
            )

        # Phase 3c: Select best hypothesis
        selection = await self._select_best(obs, evaluated)

        reasoning_trace.append(
            ReasoningStep(
                phase="selection",
                description=f"Selected {selection['selected']} (confidence: {selection['confidence']:.2f})",
                output_data=selection,
            )
        )

        # Build result
        duration_ms = int((time.time() - start_time) * 1000)

        return AbductionResult(
            observation=obs,
            hypotheses=evaluated,
            selected_hypothesis=selection["selected"],
            selection_rationale=selection["rationale"],
            council_evaluation=council_eval,
            reasoning_trace=reasoning_trace,
            recommended_actions=selection.get("actions", []),
            confidence=selection["confidence"],
            metadata={
                "domain": self.domain.value,
                "duration_ms": duration_ms,
                "num_hypotheses": len(hypotheses),
                "used_council": should_use_council,
            },
        )

    def abduce_sync(
        self,
        observation: str | Observation,
        context: dict[str, Any] | None = None,
        use_council: bool | None = None,
    ) -> AbductionResult:
        """Synchronous wrapper for abduce()."""
        return asyncio.run(self.abduce(observation, context, use_council))

    async def single_shot(
        self,
        observation: str,
        context: dict[str, Any] | None = None,
    ) -> AbductionResult:
        """
        Perform abduction in a single LLM call.

        More efficient but less structured than the full pipeline.
        Good for simpler cases or when latency matters.
        """
        prompt = format_single_shot_prompt(
            observation=observation,
            context=context,
            domain=self.domain,
            num_hypotheses=self.max_hypotheses,
        )

        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        # Build result from single-shot response
        obs_data = data.get("observation_analysis", {})
        obs = Observation(
            fact=obs_data.get("fact", observation),
            surprise_score=obs_data.get("surprise_score", 0.5),
            expected_state=obs_data.get("expected_state"),
            domain=self.domain,
        )

        hypotheses: list[Hypothesis] = []
        for h_data in data.get("hypotheses", []):
            scores_data = h_data.get("scores", {})
            hypotheses.append(
                Hypothesis(
                    id=h_data.get("id", f"H{len(hypotheses) + 1}"),
                    statement=h_data.get("statement", ""),
                    explanation=h_data.get("explanation", ""),
                    prior_probability=h_data.get("prior_probability", 0.5),
                    assumptions=[Assumption(statement=a) for a in h_data.get("assumptions", [])],
                    testable_predictions=[
                        TestablePrediction(
                            prediction=p,
                            test_method="To be determined",
                            expected_outcome_if_true="Hypothesis supported",
                            expected_outcome_if_false="Hypothesis refuted",
                        )
                        for p in h_data.get("testable_predictions", [])
                    ],
                    scores=HypothesisScores(
                        explanatory_scope=scores_data.get("explanatory_scope", 0.5),
                        explanatory_power=scores_data.get("explanatory_power", 0.5),
                        parsimony=scores_data.get("parsimony", 0.5),
                        testability=scores_data.get("testability", 0.5),
                        consilience=scores_data.get("consilience", 0.5),
                    ),
                )
            )

        selection = data.get("selection", {})

        return AbductionResult(
            observation=obs,
            hypotheses=hypotheses,
            selected_hypothesis=selection.get("best_hypothesis"),
            selection_rationale=selection.get("rationale"),
            recommended_actions=selection.get("recommended_actions", []),
            confidence=selection.get("confidence", 0.5),
            metadata={
                "domain": self.domain.value,
                "mode": "single_shot",
            },
        )

    # =========================================================================
    # PHASE 1: OBSERVATION ANALYSIS
    # =========================================================================

    async def _analyze_observation(
        self,
        observation: str,
        context: dict[str, Any] | None = None,
    ) -> Observation:
        """Analyze an observation to determine surprise level and characteristics."""
        prompt = format_observation_prompt(observation, context)
        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        # Map string to enum
        surprise_map = {
            "expected": SurpriseLevel.EXPECTED,
            "mild": SurpriseLevel.MILDLY_SURPRISING,
            "surprising": SurpriseLevel.SURPRISING,
            "high": SurpriseLevel.HIGHLY_SURPRISING,
            "anomalous": SurpriseLevel.ANOMALOUS,
        }

        return Observation(
            fact=observation,
            context=context or {},
            expected_state=data.get("expected_state"),
            surprise_level=surprise_map.get(
                data.get("surprise_level", "surprising"), SurpriseLevel.SURPRISING
            ),
            surprise_score=data.get("surprise_score", 0.5),
            domain=self.domain,
        )

    # =========================================================================
    # PHASE 2: HYPOTHESIS GENERATION
    # =========================================================================

    async def _generate_hypotheses(
        self,
        observation: Observation,
        context: dict[str, Any] | None = None,
    ) -> list[Hypothesis]:
        """Generate explanatory hypotheses for the observation."""
        prompt = format_generation_prompt(
            observation=observation, num_hypotheses=self.max_hypotheses, context=context
        )

        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        hypotheses: list[Hypothesis] = []
        for h_data in data.get("hypotheses", []):
            assumptions = [
                Assumption(
                    statement=a.get("statement", a) if isinstance(a, dict) else a,
                    testable=a.get("testable", True) if isinstance(a, dict) else True,
                )
                for a in h_data.get("assumptions", [])
            ]

            predictions = []
            for p_data in h_data.get("testable_predictions", []):
                if isinstance(p_data, dict):
                    predictions.append(
                        TestablePrediction(
                            prediction=p_data.get("prediction", ""),
                            test_method=p_data.get("test_method", ""),
                            expected_outcome_if_true=p_data.get("if_true", ""),
                            expected_outcome_if_false=p_data.get("if_false", ""),
                        )
                    )
                else:
                    predictions.append(
                        TestablePrediction(
                            prediction=str(p_data),
                            test_method="To be determined",
                            expected_outcome_if_true="Hypothesis supported",
                            expected_outcome_if_false="Hypothesis refuted",
                        )
                    )

            hypotheses.append(
                Hypothesis(
                    id=h_data.get("id", f"H{len(hypotheses) + 1}"),
                    statement=h_data.get("statement", ""),
                    explanation=h_data.get("explanation", ""),
                    prior_probability=h_data.get("prior_probability", 0.5),
                    assumptions=assumptions,
                    testable_predictions=predictions,
                    analogous_cases=h_data.get("analogous_cases", []),
                )
            )

        return hypotheses

    # =========================================================================
    # PHASE 3: EVALUATION AND SELECTION
    # =========================================================================

    async def _evaluate_hypotheses(
        self,
        observation: Observation,
        hypotheses: list[Hypothesis],
    ) -> list[Hypothesis]:
        """Evaluate hypotheses using IBE criteria."""
        prompt = format_evaluation_prompt(observation, hypotheses)
        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        # Update hypotheses with evaluation scores
        eval_map = {e["hypothesis_id"]: e for e in data.get("evaluations", [])}

        for h in hypotheses:
            if h.id in eval_map:
                scores_data = eval_map[h.id].get("scores", {})
                h.scores = HypothesisScores(
                    explanatory_scope=scores_data.get("explanatory_scope", 0.5),
                    explanatory_power=scores_data.get("explanatory_power", 0.5),
                    parsimony=scores_data.get("parsimony", 0.5),
                    testability=scores_data.get("testability", 0.5),
                    consilience=scores_data.get("consilience", 0.5),
                    analogy=scores_data.get("analogy", 0.5),
                    fertility=scores_data.get("fertility", 0.5),
                )

        return hypotheses

    async def _select_best(
        self,
        observation: Observation,
        hypotheses: list[Hypothesis],
    ) -> dict[str, Any]:
        """Select the best hypothesis using IBE."""
        prompt = format_selection_prompt(
            observation=observation, evaluated_hypotheses=hypotheses, weights=self.selection_weights
        )

        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        return {
            "selected": data.get("selected_hypothesis"),
            "rationale": data.get("selection_rationale"),
            "confidence": data.get("confidence", 0.5),
            "actions": data.get("recommended_actions", []),
            "alternative": data.get("alternative_if_wrong"),
        }

    # =========================================================================
    # COUNCIL OF CRITICS
    # =========================================================================

    async def _run_council(
        self,
        observation: Observation,
        hypotheses: list[Hypothesis],
    ) -> CouncilEvaluation:
        """Run the Council of Critics evaluation."""
        critics = ["empiricist", "logician", "pragmatist", "economist", "skeptic"]

        # Run all critics in parallel
        tasks = [self._run_critic(critic, observation, hypotheses) for critic in critics]

        evaluations = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out any errors
        valid_evals = [e for e in evaluations if isinstance(e, CriticEvaluation)]

        # Synthesize council verdict
        # (In production, this would be another LLM call)
        # For now, simple aggregation
        recommended = None
        if valid_evals:
            # Find consensus by counting recommendations
            recommendations: dict[str, int] = {}
            for e in valid_evals:
                if hasattr(e, "recommended_hypothesis") and e.recommended_hypothesis:
                    recommendations[e.recommended_hypothesis] = (
                        recommendations.get(e.recommended_hypothesis, 0) + 1
                    )

            if recommendations:
                recommended = max(recommendations.keys(), key=lambda k: recommendations[k])

        return CouncilEvaluation(
            evaluations=valid_evals,
            recommended_hypothesis=recommended,
        )

    async def _run_critic(
        self,
        critic: str,
        observation: Observation,
        hypotheses: list[Hypothesis],
    ) -> CriticEvaluation:
        """Run a single critic evaluation."""
        prompt = format_critic_prompt(critic, observation, hypotheses)
        response = await self._call_llm(prompt)
        data = self._parse_json(response)

        perspective_map = {
            "empiricist": CriticPerspective.EMPIRICIST,
            "logician": CriticPerspective.LOGICIAN,
            "pragmatist": CriticPerspective.PRAGMATIST,
            "economist": CriticPerspective.ECONOMIST,
            "skeptic": CriticPerspective.SKEPTIC,
        }

        return CriticEvaluation(
            perspective=perspective_map[critic],
            evaluation=data.get("evaluation", ""),
            concerns=data.get("concerns", data.get("logical_concerns", [])),
            strengths=[],  # Extract from per_hypothesis if needed
            recommended_tests=data.get("recommended_tests", []),
        )

    # =========================================================================
    # LLM INTERACTION
    # =========================================================================

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if self.llm_call_async:
            return cast(str, await self.llm_call_async(prompt))
        elif self.llm_call:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.llm_call, prompt)
        else:
            raise RuntimeError(
                "No LLM function provided. Initialize with llm_call or llm_call_async."
            )

    def _parse_json(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        # Remove markdown code blocks if present
        text = response.strip()
        if text.startswith("```"):
            # Find the end of the opening fence
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline + 1 :]
            # Remove closing fence
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        try:
            return cast(dict[str, Any], json.loads(text))
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            logger.debug(f"Raw response: {response[:500]}...")
            return {}

    # =========================================================================
    # PROMPT GENERATION (for external use)
    # =========================================================================

    def get_observation_prompt(
        self,
        observation: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Get the observation analysis prompt without executing."""
        return format_observation_prompt(observation, context)

    def get_generation_prompt(
        self,
        observation: Observation,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Get the hypothesis generation prompt without executing."""
        return format_generation_prompt(
            observation=observation, num_hypotheses=self.max_hypotheses, context=context
        )

    def get_single_shot_prompt(
        self,
        observation: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Get the single-shot abduction prompt without executing."""
        return format_single_shot_prompt(
            observation=observation,
            context=context,
            domain=self.domain,
            num_hypotheses=self.max_hypotheses,
        )


# Convenience functions for prompt-only mode (like Hegelion)


def abduction_prompt(
    observation: str,
    context: dict[str, Any] | None = None,
    domain: Domain | str = Domain.GENERAL,
    num_hypotheses: int = 5,
) -> str:
    """
    Generate a complete abduction prompt for any LLM.

    Use this for "prompt-only" mode where you want to run
    abduction through your own LLM setup.

    Example:
        prompt = abduction_prompt("Stock dropped on good news")
        response = my_llm(prompt)
    """
    d = Domain(domain) if isinstance(domain, str) else domain
    return format_single_shot_prompt(
        observation=observation, context=context, domain=d, num_hypotheses=num_hypotheses
    )


def observation_prompt(
    observation: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Generate just the observation analysis prompt."""
    return format_observation_prompt(observation, context)


def hypothesis_prompt(
    observation: Observation,
    num_hypotheses: int = 5,
    context: dict[str, Any] | None = None,
) -> str:
    """Generate just the hypothesis generation prompt."""
    return format_generation_prompt(
        observation=observation, num_hypotheses=num_hypotheses, context=context
    )


__all__ = [
    "AbductionAgent",
    "abduction_prompt",
    "observation_prompt",
    "hypothesis_prompt",
]
