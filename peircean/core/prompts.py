"""
Peircean Abduction: Prompt Templates

Structured prompts that guide LLMs through Peirce's abductive reasoning process.
Each phase corresponds to a stage in the scientific method as Peirce conceived it:

1. Observation - Identify and articulate the surprising fact
2. Hypothesis Generation (Retroduction) - Generate explanatory hypotheses
3. Selection (IBE) - Infer the best explanation

"Any inquiry is for Peirce bound to follow this pattern: abduction–deduction–induction."
"""

from __future__ import annotations

from typing import Any

from .models import Domain, Hypothesis, Observation

# =============================================================================
# PHASE 1: OBSERVATION PROMPTS
# =============================================================================

OBSERVATION_ANALYSIS_PROMPT = """You are analyzing an observation to determine if it constitutes a "surprising fact" in the Peircean sense.

Peirce wrote: "The surprising fact, C, is observed."

A fact is SURPRISING when it violates expectations based on:
- Prior probability (statistically unlikely)
- Causal expectations (effect without expected cause, or vice versa)
- Pattern violations (breaks established regularities)
- Category violations (thing behaves unlike its type)

## Observation
{observation}

## Context
{context}

## Your Task

Analyze this observation and provide:

1. **Surprise Classification**: Is this expected, mildly surprising, surprising, highly surprising, or anomalous?

2. **Surprise Score**: Rate from 0.0 (completely expected) to 1.0 (seemingly impossible)

3. **Expected State**: What would have been expected instead?

4. **Surprise Source**: WHY is this surprising? What expectation does it violate?

5. **Key Features**: What specific aspects of the observation are most surprising?

Respond in this JSON format:
```json
{{
    "surprise_level": "expected|mild|surprising|high|anomalous",
    "surprise_score": 0.0-1.0,
    "expected_state": "what would have been expected",
    "surprise_source": "why this is surprising",
    "key_features": ["feature1", "feature2"],
    "analysis": "brief explanation"
}}
```
"""


# =============================================================================
# PHASE 2: HYPOTHESIS GENERATION PROMPTS
# =============================================================================

HYPOTHESIS_GENERATION_PROMPT = """You are generating explanatory hypotheses through ABDUCTION.

Peirce's schema:
"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."

## The Surprising Fact
{observation}

Surprise Level: {surprise_level}
Domain: {domain}

## Context
{context}

## Your Task

Generate {num_hypotheses} distinct explanatory hypotheses. For each:

1. **Statement**: A clear, falsifiable hypothesis
2. **Explanation**: How this hypothesis makes the observation "a matter of course"
3. **Prior Probability**: Estimate before considering this observation (0.0-1.0)
4. **Assumptions**: What must be true for this hypothesis to hold
5. **Testable Predictions**: What we should observe if this is true (and if false)

Guidelines:
- Hypotheses should be DIVERSE (not variations of the same idea)
- Include at least one "surprising" hypothesis that seems unlikely but would explain well
- Consider multiple causal pathways
- Each hypothesis should be independently testable

{domain_guidance}

Respond in this JSON format:
```json
{{
    "hypotheses": [
        {{
            "id": "H1",
            "statement": "clear hypothesis statement",
            "explanation": "how this explains the observation",
            "prior_probability": 0.0-1.0,
            "assumptions": [
                {{"statement": "assumption 1", "testable": true}},
                {{"statement": "assumption 2", "testable": true}}
            ],
            "testable_predictions": [
                {{
                    "prediction": "what we should observe",
                    "test_method": "how to test",
                    "if_true": "expected outcome if hypothesis is true",
                    "if_false": "expected outcome if hypothesis is false"
                }}
            ],
            "analogous_cases": ["similar historical case 1"]
        }}
    ]
}}
```
"""

# Domain-specific guidance for hypothesis generation
DOMAIN_GUIDANCE = {
    Domain.GENERAL: """
Consider hypotheses from multiple categories:
- Causal (direct cause-effect)
- Systemic (emergent from system interactions)
- Human factors (error, intention, miscommunication)
- External factors (environment, third parties)
- Measurement/observation error
""",
    Domain.FINANCIAL: """
Consider financial-specific hypothesis types:
- Market microstructure (liquidity, order flow, market making)
- Information asymmetry (insider knowledge, information leakage)
- Behavioral factors (sentiment, herding, overreaction)
- Macro factors (policy changes, economic indicators)
- Technical factors (algorithmic trading, index rebalancing)
- Manipulation (spoofing, wash trading, pump-and-dump)
- Structural (ETF flows, options gamma, short covering)
""",
    Domain.LEGAL: """
Consider legal-specific hypothesis types:
- Statutory interpretation gaps
- Precedent conflicts or gaps
- Jurisdictional issues
- Procedural irregularities
- Factual ambiguities
- Intent/mens rea questions
- Evidentiary issues
""",
    Domain.MEDICAL: """
Consider medical-specific hypothesis types:
- Differential diagnoses
- Drug interactions
- Comorbidity effects
- Rare conditions (zebras)
- Diagnostic errors (false positives/negatives)
- Atypical presentations
- Environmental/lifestyle factors
- Genetic factors
""",
    Domain.TECHNICAL: """
Consider technical-specific hypothesis types:
- Race conditions and timing issues
- Resource exhaustion (memory, connections, file handles)
- Configuration drift
- Cascading failures
- Network partitions
- Data corruption
- Third-party service failures
- Version incompatibilities
- Security incidents
""",
    Domain.SCIENTIFIC: """
Consider scientific-specific hypothesis types:
- Measurement error
- Confounding variables
- Selection bias
- Publication bias (negative results)
- Replication issues
- Theoretical model limitations
- Novel phenomena
- Instrumentation artifacts
""",
}


# =============================================================================
# PHASE 3: EVALUATION AND SELECTION PROMPTS
# =============================================================================

HYPOTHESIS_EVALUATION_PROMPT = """You are evaluating hypotheses using Inference to the Best Explanation (IBE).

Peirce advocated for the "economy of research" - selecting hypotheses that:
1. Explain the most with the least
2. Are most amenable to testing
3. Would be most informative if confirmed or refuted

## The Surprising Fact
{observation}

## Hypotheses to Evaluate
{hypotheses_json}

## Evaluation Criteria

Score each hypothesis (0.0-1.0) on:

1. **Explanatory Scope**: How much of the observation does it explain?
   - 1.0: Explains all aspects completely
   - 0.5: Explains some aspects
   - 0.0: Barely addresses the observation

2. **Explanatory Power**: How WELL does it explain?
   - 1.0: Makes the observation a "matter of course"
   - 0.5: Makes it less surprising but not expected
   - 0.0: Leaves the observation just as surprising

3. **Parsimony**: How few assumptions are required?
   - 1.0: Minimal assumptions, all well-established
   - 0.5: Moderate assumptions
   - 0.0: Many or extraordinary assumptions

4. **Testability**: How easy is it to test?
   - 1.0: Immediately testable with available resources
   - 0.5: Testable with some effort
   - 0.0: Very difficult or impossible to test

5. **Consilience**: How well does it fit with other knowledge?
   - 1.0: Perfectly consistent with established knowledge
   - 0.5: Compatible but requires some adjustment
   - 0.0: Contradicts established knowledge

6. **Analogy**: How similar to known patterns?
   - 1.0: Exact match to well-documented pattern
   - 0.5: Some similarity to known patterns
   - 0.0: Completely novel, no precedent

7. **Fertility**: Does it generate new predictions/insights?
   - 1.0: Rich implications, many testable predictions
   - 0.5: Some additional predictions
   - 0.0: Explains only this observation, no further implications

Respond in this JSON format:
```json
{{
    "evaluations": [
        {{
            "hypothesis_id": "H1",
            "scores": {{
                "explanatory_scope": 0.0-1.0,
                "explanatory_power": 0.0-1.0,
                "parsimony": 0.0-1.0,
                "testability": 0.0-1.0,
                "consilience": 0.0-1.0,
                "analogy": 0.0-1.0,
                "fertility": 0.0-1.0
            }},
            "strengths": ["strength1", "strength2"],
            "weaknesses": ["weakness1", "weakness2"]
        }}
    ]
}}
```
"""


SELECTION_PROMPT = """You are selecting the BEST EXPLANATION from the evaluated hypotheses.

## The Surprising Fact
{observation}

## Evaluated Hypotheses
{evaluated_hypotheses_json}

## Selection Weights
{weights_json}

## Your Task

Using the evaluation scores and the specified weights, determine which hypothesis provides the BEST EXPLANATION.

Consider:
1. Composite weighted score
2. Critical weaknesses that might disqualify a hypothesis
3. Practical considerations (what can actually be tested first?)
4. Risk of being wrong (what's the cost of each error type?)

Respond in this JSON format:
```json
{{
    "selected_hypothesis": "H1",
    "composite_scores": {{
        "H1": 0.XX,
        "H2": 0.XX,
        ...
    }},
    "selection_rationale": "why this hypothesis was selected",
    "confidence": 0.0-1.0,
    "recommended_actions": [
        "First, test X by doing Y",
        "Second, verify assumption Z"
    ],
    "alternative_if_wrong": "If H1 is falsified, H2 becomes most likely because..."
}}
```
"""


# =============================================================================
# COUNCIL OF CRITICS PROMPTS
# =============================================================================

CRITIC_PROMPTS = {
    "empiricist": """You are THE EMPIRICIST on the Council of Critics.

Your role: Evaluate hypotheses based on EVIDENCE and OBSERVATION.

Questions you ask:
- What empirical evidence supports or refutes each hypothesis?
- What observations would we expect if each hypothesis were true?
- Have similar situations produced similar explanations historically?
- What data is missing that would be decisive?

## Observation
{observation}

## Hypotheses
{hypotheses_json}

Provide your empirical evaluation:
```json
{{
    "perspective": "empiricist",
    "evaluation": "overall empirical assessment",
    "per_hypothesis": {{
        "H1": {{
            "supporting_evidence": ["evidence1"],
            "contradicting_evidence": ["evidence1"],
            "missing_evidence": ["evidence1"],
            "empirical_score": 0.0-1.0
        }}
    }},
    "recommended_tests": ["test1", "test2"],
    "concerns": ["concern1"]
}}
```
""",
    "logician": """You are THE LOGICIAN on the Council of Critics.

Your role: Evaluate hypotheses based on LOGICAL CONSISTENCY.

Questions you ask:
- Is each hypothesis internally consistent?
- Does it contradict any known facts?
- Are the assumptions compatible with each other?
- Does the explanation actually follow from the hypothesis?

## Observation
{observation}

## Hypotheses
{hypotheses_json}

Provide your logical evaluation:
```json
{{
    "perspective": "logician",
    "evaluation": "overall logical assessment",
    "per_hypothesis": {{
        "H1": {{
            "internal_consistency": true/false,
            "logical_gaps": ["gap1"],
            "contradictions": ["contradiction1"],
            "validity_score": 0.0-1.0
        }}
    }},
    "logical_concerns": ["concern1"],
    "recommended_clarifications": ["clarification1"]
}}
```
""",
    "pragmatist": """You are THE PRAGMATIST on the Council of Critics.

Your role: Evaluate hypotheses based on PRACTICAL CONSEQUENCES.

Peirce's Pragmatic Maxim: "Consider what effects, that might conceivably have practical bearings, we conceive the object of our conception to have."

Questions you ask:
- What practical difference does each hypothesis make?
- If true, what should we DO differently?
- What are the real-world implications?
- Which hypothesis is most actionable?

## Observation
{observation}

## Hypotheses
{hypotheses_json}

Provide your pragmatic evaluation:
```json
{{
    "perspective": "pragmatist",
    "evaluation": "overall pragmatic assessment",
    "per_hypothesis": {{
        "H1": {{
            "practical_implications": ["implication1"],
            "recommended_actions": ["action1"],
            "actionability_score": 0.0-1.0
        }}
    }},
    "most_actionable": "H1",
    "pragmatic_concerns": ["concern1"]
}}
```
""",
    "economist": """You are THE ECONOMIST OF RESEARCH on the Council of Critics.

Your role: Evaluate hypotheses based on ECONOMY OF INQUIRY.

Peirce emphasized the "economy of research" - we should test hypotheses in an order that maximizes expected information gain per unit cost.

Questions you ask:
- Which hypothesis is cheapest to test?
- Which would be most informative if confirmed or refuted?
- What's the expected value of investigating each?
- What's the opportunity cost of pursuing each path?

## Observation
{observation}

## Hypotheses
{hypotheses_json}

Provide your economic evaluation:
```json
{{
    "perspective": "economist",
    "evaluation": "overall economic assessment",
    "per_hypothesis": {{
        "H1": {{
            "test_cost": "low/medium/high",
            "information_value": 0.0-1.0,
            "expected_value": 0.0-1.0,
            "time_to_test": "estimate"
        }}
    }},
    "optimal_test_order": ["H1", "H3", "H2"],
    "recommended_first_test": "description of most economical first test"
}}
```
""",
    "skeptic": """You are THE SKEPTIC on the Council of Critics.

Your role: Challenge hypotheses and identify potential flaws.

Questions you ask:
- What would DISPROVE each hypothesis?
- What are we assuming without justification?
- Could this be explained more simply?
- Are we falling for any cognitive biases?

## Observation
{observation}

## Hypotheses
{hypotheses_json}

Provide your skeptical evaluation:
```json
{{
    "perspective": "skeptic",
    "evaluation": "overall skeptical assessment",
    "per_hypothesis": {{
        "H1": {{
            "falsification_criteria": ["how to disprove"],
            "unjustified_assumptions": ["assumption1"],
            "potential_biases": ["bias1"],
            "simpler_alternatives": ["alternative1"],
            "skepticism_score": 0.0-1.0
        }}
    }},
    "strongest_objection_per_hypothesis": {{
        "H1": "main objection"
    }},
    "recommended_devil_advocate_tests": ["test1"]
}}
```
""",
}


COUNCIL_SYNTHESIS_PROMPT = """You are synthesizing the Council of Critics' evaluations into a final recommendation.

## Observation
{observation}

## Critic Evaluations
{critics_json}

## Your Task

Synthesize the diverse perspectives into:
1. A consensus view (where critics agree)
2. Points of dissent (where critics disagree)
3. A final recommendation that weighs all perspectives

Respond in this JSON format:
```json
{{
    "consensus": "what all critics agree on",
    "dissent": "where critics disagree and why",
    "synthesis": "integrated conclusion",
    "recommended_hypothesis": "H1",
    "confidence": 0.0-1.0,
    "key_uncertainties": ["uncertainty1"],
    "recommended_next_steps": ["step1", "step2"]
}}
```
"""


# =============================================================================
# SINGLE-SHOT COMPREHENSIVE PROMPT
# =============================================================================

ABDUCTION_SINGLE_SHOT_PROMPT = """You are performing ABDUCTIVE REASONING in the tradition of Charles Sanders Peirce.

Peirce's schema for abduction:
"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."

## Your Observation
{observation}

## Context
{context}

## Your Task

Perform a complete abductive analysis:

### Phase 1: Analyze the Surprise
- What makes this surprising?
- What would have been expected?
- How surprising is it? (Score 0-1)

### Phase 2: Generate Hypotheses
Generate {num_hypotheses} explanatory hypotheses. For each:
- Clear statement
- How it explains the observation
- Prior probability
- Key assumptions
- Testable predictions

### Phase 3: Evaluate and Select
Using Inference to the Best Explanation (IBE), evaluate each hypothesis on:
- Explanatory scope and power
- Parsimony (fewer assumptions = better)
- Testability
- Consilience with other knowledge

Select the BEST EXPLANATION and justify your choice.

{domain_guidance}

Respond in this JSON format:
```json
{{
    "observation_analysis": {{
        "fact": "restated observation",
        "surprise_score": 0.0-1.0,
        "expected_state": "what was expected",
        "surprise_source": "why it's surprising"
    }},
    "hypotheses": [
        {{
            "id": "H1",
            "statement": "hypothesis",
            "explanation": "how it explains",
            "prior_probability": 0.0-1.0,
            "assumptions": ["assumption1"],
            "testable_predictions": ["prediction1"],
            "scores": {{
                "explanatory_scope": 0.0-1.0,
                "explanatory_power": 0.0-1.0,
                "parsimony": 0.0-1.0,
                "testability": 0.0-1.0,
                "consilience": 0.0-1.0
            }}
        }}
    ],
    "selection": {{
        "best_hypothesis": "H1",
        "rationale": "why this is the best explanation",
        "confidence": 0.0-1.0,
        "recommended_actions": ["action1", "action2"]
    }}
}}
```
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def format_observation_prompt(observation: str, context: dict[str, Any] | None = None) -> str:
    """Format the observation analysis prompt."""
    return OBSERVATION_ANALYSIS_PROMPT.format(observation=observation, context=context or {})


def format_generation_prompt(
    observation: Observation, num_hypotheses: int = 5, context: dict[str, Any] | None = None
) -> str:
    """Format the hypothesis generation prompt."""
    domain_guidance = DOMAIN_GUIDANCE.get(observation.domain, DOMAIN_GUIDANCE[Domain.GENERAL])

    return HYPOTHESIS_GENERATION_PROMPT.format(
        observation=observation.fact,
        surprise_level=observation.surprise_level.value,
        domain=observation.domain.value,
        context=context or observation.context,
        num_hypotheses=num_hypotheses,
        domain_guidance=domain_guidance,
    )


def format_evaluation_prompt(observation: Observation, hypotheses: list[Hypothesis]) -> str:
    """Format the hypothesis evaluation prompt."""
    hypotheses_json = [
        {
            "id": h.id,
            "statement": h.statement,
            "explanation": h.explanation,
            "prior_probability": h.prior_probability,
            "assumptions": [a.statement for a in h.assumptions],
            "testable_predictions": [p.prediction for p in h.testable_predictions],
        }
        for h in hypotheses
    ]

    import json

    return HYPOTHESIS_EVALUATION_PROMPT.format(
        observation=observation.fact, hypotheses_json=json.dumps(hypotheses_json, indent=2)
    )


def format_selection_prompt(
    observation: Observation,
    evaluated_hypotheses: list[Hypothesis],
    weights: dict[str, float] | None = None,
) -> str:
    """Format the selection prompt."""
    import json

    default_weights = {
        "explanatory_scope": 0.15,
        "explanatory_power": 0.25,
        "parsimony": 0.20,
        "testability": 0.15,
        "consilience": 0.10,
        "analogy": 0.05,
        "fertility": 0.10,
    }

    hypotheses_json = [
        {
            "id": h.id,
            "statement": h.statement,
            "scores": h.scores.model_dump(),
            "composite_score": h.composite_score,
        }
        for h in evaluated_hypotheses
    ]

    return SELECTION_PROMPT.format(
        observation=observation.fact,
        evaluated_hypotheses_json=json.dumps(hypotheses_json, indent=2),
        weights_json=json.dumps(weights or default_weights, indent=2),
    )


def format_single_shot_prompt(
    observation: str,
    context: dict[str, Any] | None = None,
    domain: Domain = Domain.GENERAL,
    num_hypotheses: int = 5,
) -> str:
    """Format the comprehensive single-shot abduction prompt."""
    domain_guidance = DOMAIN_GUIDANCE.get(domain, DOMAIN_GUIDANCE[Domain.GENERAL])

    return ABDUCTION_SINGLE_SHOT_PROMPT.format(
        observation=observation,
        context=context or {},
        num_hypotheses=num_hypotheses,
        domain_guidance=domain_guidance,
    )


def format_critic_prompt(
    critic: str, observation: Observation, hypotheses: list[Hypothesis]
) -> str:
    """Format a critic evaluation prompt."""
    import json

    if critic not in CRITIC_PROMPTS:
        raise ValueError(f"Unknown critic: {critic}. Available: {list(CRITIC_PROMPTS.keys())}")

    hypotheses_json = [
        {
            "id": h.id,
            "statement": h.statement,
            "explanation": h.explanation,
            "assumptions": [a.statement for a in h.assumptions],
            "testable_predictions": [p.prediction for p in h.testable_predictions],
        }
        for h in hypotheses
    ]

    return CRITIC_PROMPTS[critic].format(
        observation=observation.fact, hypotheses_json=json.dumps(hypotheses_json, indent=2)
    )


__all__ = [
    "OBSERVATION_ANALYSIS_PROMPT",
    "HYPOTHESIS_GENERATION_PROMPT",
    "HYPOTHESIS_EVALUATION_PROMPT",
    "SELECTION_PROMPT",
    "CRITIC_PROMPTS",
    "COUNCIL_SYNTHESIS_PROMPT",
    "ABDUCTION_SINGLE_SHOT_PROMPT",
    "DOMAIN_GUIDANCE",
    "format_observation_prompt",
    "format_generation_prompt",
    "format_evaluation_prompt",
    "format_selection_prompt",
    "format_single_shot_prompt",
    "format_critic_prompt",
]
