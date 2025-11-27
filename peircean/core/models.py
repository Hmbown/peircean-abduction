"""
Peircean Abduction: Core Data Models

Data structures for abductive reasoning following Peirce's logical framework:
- Observation: The surprising fact
- Hypothesis: A potential explanation
- AbductionResult: Complete reasoning trace
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SurpriseLevel(str, Enum):
    """Classification of how surprising an observation is."""
    
    EXPECTED = "expected"           # Within normal distribution
    MILDLY_SURPRISING = "mild"      # 1-2 standard deviations
    SURPRISING = "surprising"       # 2-3 standard deviations
    HIGHLY_SURPRISING = "high"      # 3+ standard deviations
    ANOMALOUS = "anomalous"         # Seemingly impossible given priors


class Domain(str, Enum):
    """Pre-defined domains with hypothesis templates."""
    
    GENERAL = "general"
    FINANCIAL = "financial"
    LEGAL = "legal"
    MEDICAL = "medical"
    TECHNICAL = "technical"
    SCIENTIFIC = "scientific"


class SelectionCriterion(str, Enum):
    """Criteria for Inference to the Best Explanation (IBE)."""
    
    EXPLANATORY_SCOPE = "explanatory_scope"      # How much does it explain?
    EXPLANATORY_POWER = "explanatory_power"      # How well does it explain?
    PARSIMONY = "parsimony"                      # Fewest assumptions (Occam)
    TESTABILITY = "testability"                  # Can we verify/falsify?
    CONSILIENCE = "consilience"                  # Fits with other knowledge
    ANALOGY = "analogy"                          # Similar to known patterns
    FERTILITY = "fertility"                      # Generates new predictions


class Observation(BaseModel):
    """
    The surprising fact that triggers abductive reasoning.
    
    In Peirce's schema: "The surprising fact, C, is observed."
    """
    
    fact: str = Field(
        description="The observed fact or phenomenon"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Relevant background information"
    )
    expected_state: Optional[str] = Field(
        default=None,
        description="What would have been expected instead"
    )
    surprise_level: SurpriseLevel = Field(
        default=SurpriseLevel.SURPRISING,
        description="How surprising is this observation?"
    )
    surprise_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Quantified surprise (0=expected, 1=anomalous)"
    )
    domain: Domain = Field(
        default=Domain.GENERAL,
        description="Domain context for hypothesis generation"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the observation was made"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source of the observation (sensor, report, etc.)"
    )
    
    def to_peirce_premise(self) -> str:
        """Format as Peirce's first premise."""
        return f"The surprising fact is observed: {self.fact}"


class Assumption(BaseModel):
    """An assumption required for a hypothesis to hold."""
    
    statement: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    testable: bool = True
    test_method: Optional[str] = None


class TestablePrediction(BaseModel):
    """A falsifiable prediction derived from a hypothesis."""
    
    prediction: str
    test_method: str
    expected_outcome_if_true: str
    expected_outcome_if_false: str
    estimated_test_cost: Optional[str] = None  # Low/Medium/High or dollar amount


class HypothesisScores(BaseModel):
    """IBE evaluation scores for a hypothesis."""
    
    explanatory_scope: float = Field(ge=0.0, le=1.0, default=0.5)
    explanatory_power: float = Field(ge=0.0, le=1.0, default=0.5)
    parsimony: float = Field(ge=0.0, le=1.0, default=0.5)
    testability: float = Field(ge=0.0, le=1.0, default=0.5)
    consilience: float = Field(ge=0.0, le=1.0, default=0.5)
    analogy: float = Field(ge=0.0, le=1.0, default=0.5)
    fertility: float = Field(ge=0.0, le=1.0, default=0.5)
    
    def composite(self, weights: Optional[dict[str, float]] = None) -> float:
        """
        Calculate weighted composite score.
        
        Default weights emphasize explanatory power and parsimony,
        following Peirce's economy of research.
        """
        default_weights = {
            "explanatory_scope": 0.15,
            "explanatory_power": 0.25,
            "parsimony": 0.20,
            "testability": 0.15,
            "consilience": 0.10,
            "analogy": 0.05,
            "fertility": 0.10,
        }
        w = weights or default_weights
        
        return (
            w.get("explanatory_scope", 0) * self.explanatory_scope +
            w.get("explanatory_power", 0) * self.explanatory_power +
            w.get("parsimony", 0) * self.parsimony +
            w.get("testability", 0) * self.testability +
            w.get("consilience", 0) * self.consilience +
            w.get("analogy", 0) * self.analogy +
            w.get("fertility", 0) * self.fertility
        )


class Hypothesis(BaseModel):
    """
    An explanatory hypothesis generated through abduction.
    
    In Peirce's schema: "But if A were true, C would be a matter of course."
    """
    
    id: str = Field(description="Unique identifier (H1, H2, etc.)")
    statement: str = Field(description="The hypothesis statement")
    explanation: str = Field(
        description="How this hypothesis explains the observation"
    )
    assumptions: list[Assumption] = Field(
        default_factory=list,
        description="Assumptions required for this hypothesis"
    )
    prior_probability: float = Field(
        ge=0.0,
        le=1.0,
        default=0.5,
        description="Prior probability before considering this observation"
    )
    posterior_probability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Posterior probability after abductive inference"
    )
    testable_predictions: list[TestablePrediction] = Field(
        default_factory=list,
        description="Falsifiable predictions derived from this hypothesis"
    )
    scores: HypothesisScores = Field(
        default_factory=HypothesisScores,
        description="IBE evaluation scores"
    )
    analogous_cases: list[str] = Field(
        default_factory=list,
        description="Similar historical cases or patterns"
    )
    
    @property
    def composite_score(self) -> float:
        """Get weighted composite IBE score."""
        return self.scores.composite()
    
    def to_peirce_premise(self, observation: str) -> str:
        """Format as Peirce's second premise."""
        return f"But if {self.statement} were true, then {observation} would be a matter of course."
    
    def to_peirce_conclusion(self) -> str:
        """Format as Peirce's abductive conclusion."""
        return f"Hence, there is reason to suspect that {self.statement} is true."


class CriticPerspective(str, Enum):
    """The Council of Critics - different evaluative perspectives."""
    
    EMPIRICIST = "empiricist"    # What evidence supports/refutes?
    LOGICIAN = "logician"        # Is it internally consistent?
    PRAGMATIST = "pragmatist"    # What practical difference does it make?
    ECONOMIST = "economist"      # Which is most economical to test?
    SKEPTIC = "skeptic"          # What could prove it wrong?


class CriticEvaluation(BaseModel):
    """Evaluation from a single critic perspective."""
    
    perspective: CriticPerspective
    evaluation: str
    concerns: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommended_tests: list[str] = Field(default_factory=list)


class CouncilEvaluation(BaseModel):
    """Combined evaluation from the Council of Critics."""
    
    evaluations: list[CriticEvaluation]
    consensus: Optional[str] = None
    dissent: Optional[str] = None
    recommended_hypothesis: Optional[str] = None


class ReasoningStep(BaseModel):
    """A single step in the reasoning trace."""
    
    phase: str  # "observation", "generation", "evaluation", "selection"
    description: str
    input_data: Optional[dict[str, Any]] = None
    output_data: Optional[dict[str, Any]] = None
    duration_ms: Optional[int] = None


class AbductionResult(BaseModel):
    """
    Complete result of an abductive reasoning process.
    
    Contains the full trace from observation through hypothesis
    generation to inference to the best explanation.
    """
    
    observation: Observation
    hypotheses: list[Hypothesis]
    selected_hypothesis: Optional[str] = Field(
        default=None,
        description="ID of the selected best hypothesis"
    )
    selection_rationale: Optional[str] = Field(
        default=None,
        description="Why this hypothesis was selected"
    )
    council_evaluation: Optional[CouncilEvaluation] = None
    reasoning_trace: list[ReasoningStep] = Field(default_factory=list)
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Suggested next steps to test the hypothesis"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        default=0.5,
        description="Overall confidence in the selected explanation"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (model, timing, etc.)"
    )
    
    @property
    def best_hypothesis(self) -> Optional[Hypothesis]:
        """Get the selected hypothesis object."""
        if not self.selected_hypothesis:
            return None
        for h in self.hypotheses:
            if h.id == self.selected_hypothesis:
                return h
        return None
    
    def to_json_trace(self) -> dict[str, Any]:
        """Export as JSON-serializable trace for agents."""
        return self.model_dump(mode="json")
    
    def to_markdown(self) -> str:
        """Format as human-readable markdown."""
        lines = [
            "# Abductive Reasoning Trace",
            "",
            "## Observation (The Surprising Fact)",
            f"**Fact**: {self.observation.fact}",
            f"**Surprise Level**: {self.observation.surprise_level.value} ({self.observation.surprise_score:.2f})",
            "",
        ]
        
        if self.observation.expected_state:
            lines.append(f"**Expected**: {self.observation.expected_state}")
            lines.append("")
        
        lines.extend([
            "## Generated Hypotheses",
            "",
        ])
        
        for h in sorted(self.hypotheses, key=lambda x: x.composite_score, reverse=True):
            lines.extend([
                f"### {h.id}: {h.statement}",
                f"*Prior probability*: {h.prior_probability:.2f}",
                f"*Composite score*: {h.composite_score:.2f}",
                "",
                f"**Explanation**: {h.explanation}",
                "",
            ])
            
            if h.assumptions:
                lines.append("**Assumptions**:")
                for a in h.assumptions:
                    lines.append(f"- {a.statement}")
                lines.append("")
            
            if h.testable_predictions:
                lines.append("**Testable Predictions**:")
                for p in h.testable_predictions:
                    lines.append(f"- {p.prediction}")
                lines.append("")
        
        if self.selected_hypothesis:
            best = self.best_hypothesis
            lines.extend([
                "## Selected Hypothesis (Inference to the Best Explanation)",
                "",
                f"**Selected**: {self.selected_hypothesis}",
                f"**Confidence**: {self.confidence:.2f}",
                "",
            ])
            if self.selection_rationale:
                lines.append(f"**Rationale**: {self.selection_rationale}")
                lines.append("")
        
        if self.recommended_actions:
            lines.extend([
                "## Recommended Next Steps",
                "",
            ])
            for i, action in enumerate(self.recommended_actions, 1):
                lines.append(f"{i}. {action}")
            lines.append("")
        
        return "\n".join(lines)


# Export all models
__all__ = [
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
]
