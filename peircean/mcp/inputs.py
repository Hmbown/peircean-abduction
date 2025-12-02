"""
Peircean MCP Server: Input Models

Pydantic v2 models for validating MCP tool inputs.
These models ensure type safety, provide clear error messages,
and generate JSON Schema for tool descriptions.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    JSON = "json"
    MARKDOWN = "markdown"


class Domain(str, Enum):
    """Pre-defined domains with hypothesis templates."""

    GENERAL = "general"
    FINANCIAL = "financial"
    LEGAL = "legal"
    MEDICAL = "medical"
    TECHNICAL = "technical"
    SCIENTIFIC = "scientific"


# =============================================================================
# PHASE 1: OBSERVE ANOMALY INPUT
# =============================================================================
class ObserveAnomalyInput(BaseModel):
    """Input model for peircean_observe_anomaly tool.

    Validates the observation input for Phase 1 of abductive reasoning.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    observation: str = Field(
        ...,
        description=(
            "The surprising/anomalous fact observed. "
            "Examples: 'Server latency spiked 10x but CPU/memory normal', "
            "'Customer churn doubled but NPS unchanged', "
            "'Stock dropped 5% after positive earnings'"
        ),
        min_length=1,
        max_length=5000,
    )
    context: Optional[str] = Field(
        default=None,
        description=(
            "Additional background information. "
            "Examples: 'No recent deployments, traffic is steady', "
            "'No price changes in last quarter'"
        ),
        max_length=5000,
    )
    domain: Domain = Field(
        default=Domain.GENERAL,
        description=(
            "Domain context for hypothesis generation. "
            "Options: general, financial, legal, medical, technical, scientific"
        ),
    )

    @field_validator("observation")
    @classmethod
    def validate_observation(cls, v: str) -> str:
        """Ensure observation is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError(
                "Observation cannot be empty. Provide a description of the surprising fact."
            )
        return v.strip()


# =============================================================================
# PHASE 2: GENERATE HYPOTHESES INPUT
# =============================================================================
class GenerateHypothesesInput(BaseModel):
    """Input model for peircean_generate_hypotheses tool.

    Validates the anomaly JSON and generation parameters for Phase 2.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    anomaly_json: str = Field(
        ...,
        description=(
            "The JSON output from peircean_observe_anomaly (Phase 1). "
            "Must contain an 'anomaly' object with at least 'fact' field. "
            "Example: '{\"anomaly\": {\"fact\": \"Server latency spiked\", \"domain\": \"technical\"}}'"
        ),
        min_length=2,
        max_length=50000,
    )
    num_hypotheses: int = Field(
        default=5,
        description=(
            "Number of distinct hypotheses to generate. "
            "Higher values provide more diverse explanations but increase response size. "
            "Recommended: 3-5 for most use cases."
        ),
        ge=1,
        le=20,
    )


# =============================================================================
# PHASE 3: EVALUATE VIA IBE INPUT
# =============================================================================
class EvaluateViaIBEInput(BaseModel):
    """Input model for peircean_evaluate_via_ibe tool.

    Validates inputs for Phase 3 Inference to Best Explanation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    anomaly_json: str = Field(
        ...,
        description=(
            "The JSON output from peircean_observe_anomaly (Phase 1). "
            "Example: '{\"anomaly\": {\"fact\": \"...\", \"surprise_level\": \"high\"}}'"
        ),
        min_length=2,
        max_length=50000,
    )
    hypotheses_json: str = Field(
        ...,
        description=(
            "The JSON output from peircean_generate_hypotheses (Phase 2). "
            "Example: '{\"hypotheses\": [{\"id\": \"H1\", \"statement\": \"...\"}]}'"
        ),
        min_length=2,
        max_length=100000,
    )
    use_council: bool = Field(
        default=False,
        description=(
            "Include Council of Critics evaluation (Empiricist, Logician, Pragmatist, "
            "Economist, Skeptic). Provides multi-perspective analysis but increases output."
        ),
    )
    custom_council: Optional[list[str]] = Field(
        default=None,
        description=(
            "Custom list of specialist roles for the Council. "
            "Overrides default council if provided. "
            "Examples: ['Forensic Accountant', 'Security Engineer', 'Domain Expert']"
        ),
        max_length=10,
    )


# =============================================================================
# SINGLE-SHOT ABDUCTION INPUT
# =============================================================================
class AbduceSingleShotInput(BaseModel):
    """Input model for peircean_abduce_single_shot tool.

    Validates inputs for complete abductive reasoning in one call.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    observation: str = Field(
        ...,
        description=(
            "The surprising/anomalous fact to explain. "
            "Examples: 'Customer churn rate doubled in Q3', "
            "'API latency spiked with no deployment'"
        ),
        min_length=1,
        max_length=5000,
    )
    context: Optional[str] = Field(
        default=None,
        description=(
            "Additional background information. "
            "Examples: 'No price changes, NPS stable, no competitor launches'"
        ),
        max_length=5000,
    )
    domain: Domain = Field(
        default=Domain.GENERAL,
        description=(
            "Domain context for hypothesis generation. "
            "Options: general, financial, legal, medical, technical, scientific"
        ),
    )
    num_hypotheses: int = Field(
        default=5,
        description="Number of hypotheses to generate (1-20). Recommended: 3-5.",
        ge=1,
        le=20,
    )

    @field_validator("observation")
    @classmethod
    def validate_observation(cls, v: str) -> str:
        """Ensure observation is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError(
                "Observation cannot be empty. Provide a description of the surprising fact."
            )
        return v.strip()


# =============================================================================
# CRITIC EVALUATION INPUT
# =============================================================================
class CriticEvaluateInput(BaseModel):
    """Input model for peircean_critic_evaluate tool.

    Validates inputs for single-critic perspective evaluation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    critic: str = Field(
        ...,
        description=(
            "The critic role/perspective to adopt. "
            "Built-in options: empiricist, logician, pragmatist, economist, skeptic. "
            "Custom roles also supported: 'forensic_accountant', 'security_engineer', etc."
        ),
        min_length=1,
        max_length=100,
    )
    anomaly_json: str = Field(
        ...,
        description="The JSON output from peircean_observe_anomaly (Phase 1).",
        min_length=2,
        max_length=50000,
    )
    hypotheses_json: str = Field(
        ...,
        description="The JSON output from peircean_generate_hypotheses (Phase 2).",
        min_length=2,
        max_length=100000,
    )

    @field_validator("critic")
    @classmethod
    def validate_critic(cls, v: str) -> str:
        """Ensure critic is not empty, default to general_critic if needed."""
        if not v or not v.strip():
            return "general_critic"
        return v.strip()


# =============================================================================
# EXPORTS
# =============================================================================
__all__ = [
    "ResponseFormat",
    "Domain",
    "ObserveAnomalyInput",
    "GenerateHypothesesInput",
    "EvaluateViaIBEInput",
    "AbduceSingleShotInput",
    "CriticEvaluateInput",
]
