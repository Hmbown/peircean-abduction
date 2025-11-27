"""
Peircean Abduction: Abductive Reasoning Harness for LLMs

"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."
— Charles Sanders Peirce, Collected Papers 5.189

This package provides structured abductive reasoning for AI systems,
following Peirce's three-stage scientific inquiry:

1. Observation - Identify and characterize the surprising fact
2. Hypothesis Generation (Retroduction) - Generate explanatory hypotheses
3. Selection (IBE) - Infer the best explanation

Example:
    from peircean import AbductionAgent, abduction_prompt

    # Using with your own LLM
    prompt = abduction_prompt("Stock dropped 5% on good news")
    response = your_llm(prompt)

    # Using the agent
    agent = AbductionAgent(
        llm_call=your_llm_function,
        domain="financial"
    )
    result = await agent.abduce("Stock dropped 5% on good news")
    print(result.selected_hypothesis)
"""

__version__ = "0.2.0"
__author__ = "Hunter Bown"
__email__ = "hunter@shannonlabs.dev"

from .core import (
    # Agent
    AbductionAgent,
    # Models
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
    SelectionCriterion,
    SurpriseLevel,
    TestablePrediction,
    abduction_prompt,
    hypothesis_prompt,
    observation_prompt,
)

__all__ = [
    # Version
    "__version__",
    # Agent
    "AbductionAgent",
    "abduction_prompt",
    "observation_prompt",
    "hypothesis_prompt",
    # Models
    "AbductionResult",
    "Assumption",
    "CouncilEvaluation",
    "CriticEvaluation",
    "CriticPerspective",
    "Domain",
    "Hypothesis",
    "HypothesisScores",
    "Observation",
    "ReasoningStep",
    "SelectionCriterion",
    "SurpriseLevel",
    "TestablePrediction",
]
