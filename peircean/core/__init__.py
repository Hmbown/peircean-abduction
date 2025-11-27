"""
Peircean Abduction: Core Module

Abductive reasoning harness for LLMs following Charles Sanders Peirce's
three-stage scientific inquiry: Observation → Hypothesis → Selection
"""

from .agent import (
    AbductionAgent,
    abduction_prompt,
    hypothesis_prompt,
    observation_prompt,
)
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
    SelectionCriterion,
    SurpriseLevel,
    TestablePrediction,
)
from .prompts import (
    ABDUCTION_SINGLE_SHOT_PROMPT,
    CRITIC_PROMPTS,
    DOMAIN_GUIDANCE,
    HYPOTHESIS_EVALUATION_PROMPT,
    HYPOTHESIS_GENERATION_PROMPT,
    OBSERVATION_ANALYSIS_PROMPT,
    SELECTION_PROMPT,
)

__all__ = [
    # Agent
    "AbductionAgent",
    "abduction_prompt",
    "observation_prompt",
    "hypothesis_prompt",
    # Models
    "SurpriseLevel",
    "Domain",
    "SelectionCriterion",
    "Observation",
    "Assumption",
    "TestablePrediction",
    "HypothesisScores",
    "Hypothesis",
    "CriticPerspective",
    "CriticEvaluation",
    "CouncilEvaluation",
    "ReasoningStep",
    "AbductionResult",
    # Prompts
    "OBSERVATION_ANALYSIS_PROMPT",
    "HYPOTHESIS_GENERATION_PROMPT",
    "HYPOTHESIS_EVALUATION_PROMPT",
    "SELECTION_PROMPT",
    "CRITIC_PROMPTS",
    "ABDUCTION_SINGLE_SHOT_PROMPT",
    "DOMAIN_GUIDANCE",
]
