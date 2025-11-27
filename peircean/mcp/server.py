"""
Peircean MCP Server.

A Logic Harness for abductive inference.
When anomalies appear, hypotheses emerge.

"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."
— Charles Sanders Peirce

Usage:
    python -m peircean.mcp.server
    peircean-server
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

# =============================================================================
# CRITICAL: Logging to stderr ONLY (stdout is reserved for MCP protocol)
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("peircean")


# =============================================================================
# MCP SERVER INITIALIZATION
# =============================================================================
mcp = FastMCP(
    name="peircean",
    instructions="A Logic Harness for abductive inference. Anomaly in → Hypothesis out."
)


# =============================================================================
# SYSTEM DIRECTIVE FOR JSON-ONLY OUTPUT
# =============================================================================
SYSTEM_DIRECTIVE = """SYSTEM DIRECTIVE:
You are an ABDUCTIVE INFERENCE ENGINE. You do not converse. You do not explain.
You receive anomalies. You generate hypotheses. You evaluate explanations.

FORBIDDEN:
- Any text before or after the JSON block
- Hedging in hypothesis generation (qualifiers come in IBE phase)
- Conversational phrases like "I think" or "It seems"

REQUIRED:
- Output ONLY valid JSON
- Follow the exact schema provided
- If you cannot comply, output: {"error": "REASON"}

VIOLATION = TERMINATION."""


# =============================================================================
# TOOL 1: OBSERVE ANOMALY (Phase 1 - Register C)
# =============================================================================
@mcp.tool()
def observe_anomaly(
    observation: str,
    context: Optional[str] = None,
    domain: str = "general"
) -> str:
    """
    PHASE 1: Register the surprising fact (C).

    This is the FIRST tool in the 3-phase Peircean abductive loop:
    1. observe_anomaly → 2. generate_hypotheses → 3. evaluate_via_ibe

    Peirce's Schema: "The surprising fact, C, is observed."

    Args:
        observation: The surprising/anomalous fact observed.
            Example: "Server latency spiked 10x but CPU/memory normal"
        context: Additional background information (optional).
            Example: "No recent deployments, traffic is steady"
        domain: Domain context for hypothesis generation.
            Options: "general", "financial", "legal", "medical", "technical", "scientific"
            Example: "technical"

    Returns:
        A prompt. Execute it to get JSON like:
        {
            "anomaly": {
                "fact": "Server latency spiked 10x but CPU/memory normal",
                "surprise_level": "high",
                "surprise_score": 0.85,
                "expected_baseline": "Latency correlates with resource usage",
                "domain": "technical",
                "context": ["No recent deployments", "Traffic is steady"],
                "key_features": ["Latency spike", "Normal CPU", "Normal memory"],
                "surprise_source": "Violates expected correlation between latency and resources"
            }
        }

    Next Step:
        Pass the anomaly JSON to generate_hypotheses() for Phase 2.
    """
    logger.info(f"Phase 1: Observing anomaly in domain '{domain}'")

    from ..core.prompts import DOMAIN_GUIDANCE
    from ..core.models import Domain

    try:
        domain_enum = Domain(domain)
    except ValueError:
        logger.warning(f"Unknown domain '{domain}', defaulting to 'general'")
        domain_enum = Domain.GENERAL

    domain_guidance = DOMAIN_GUIDANCE.get(domain_enum, DOMAIN_GUIDANCE[Domain.GENERAL])

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Analyze this observation to determine if it constitutes a "surprising fact" (C) in the Peircean sense.

## The Observation
{observation}

## Context
{context or "No additional context provided."}

## Domain
{domain}

{domain_guidance}

## Analysis Requirements

A fact is SURPRISING when it violates expectations based on:
- Prior probability (statistically unlikely)
- Causal expectations (effect without expected cause)
- Pattern violations (breaks established regularities)
- Category violations (thing behaves unlike its type)

## Output Schema

Respond with ONLY this JSON structure:
```json
{{
    "anomaly": {{
        "fact": "restatement of the observation",
        "surprise_level": "expected|mild|surprising|high|anomalous",
        "surprise_score": 0.0-1.0,
        "expected_baseline": "what would normally be expected",
        "domain": "{domain}",
        "context": ["context item 1", "context item 2"],
        "key_features": ["surprising feature 1", "surprising feature 2"],
        "surprise_source": "why this violates expectations"
    }}
}}
```
"""

    return json.dumps({
        "type": "prompt",
        "phase": 1,
        "phase_name": "observation",
        "prompt": prompt,
        "next_tool": "generate_hypotheses",
        "usage": "Execute this prompt with an LLM, then pass the anomaly JSON to generate_hypotheses()"
    }, indent=2)


# =============================================================================
# TOOL 2: GENERATE HYPOTHESES (Phase 2 - Generate A's)
# =============================================================================
@mcp.tool()
def generate_hypotheses(
    anomaly_json: str,
    num_hypotheses: int = 5
) -> str:
    """
    PHASE 2: Generate candidate hypotheses (A's) that would explain the anomaly.

    This is the SECOND tool in the 3-phase Peircean abductive loop:
    1. observe_anomaly → 2. generate_hypotheses → 3. evaluate_via_ibe

    Peirce's Schema: "But if A were true, C would be a matter of course."

    Args:
        anomaly_json: The JSON output from observe_anomaly (Phase 1).
            Example: '{"anomaly": {"fact": "...", "surprise_level": "high", ...}}'
        num_hypotheses: Number of distinct hypotheses to generate (default: 5).
            Example: 5

    Returns:
        A prompt. Execute it to get JSON like:
        {
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "Hidden service degradation causing silent dissatisfaction",
                    "explains_anomaly": "If service quality dropped, churn would increase despite stable NPS",
                    "prior_probability": 0.35,
                    "assumptions": [
                        {"statement": "NPS lags actual satisfaction", "testable": true}
                    ],
                    "testable_predictions": [
                        {
                            "prediction": "Support tickets increased pre-churn",
                            "test_method": "Query support ticket volume by churned users",
                            "if_true": "Supports H1",
                            "if_false": "Weakens H1"
                        }
                    ]
                }
            ]
        }

    Next Step:
        Pass the hypotheses JSON to evaluate_via_ibe() for Phase 3.
    """
    logger.info(f"Phase 2: Generating {num_hypotheses} hypotheses")

    # Parse the anomaly JSON
    try:
        anomaly_data = json.loads(anomaly_json)
        if "anomaly" in anomaly_data:
            anomaly = anomaly_data["anomaly"]
        else:
            anomaly = anomaly_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in anomaly_json parameter")
        return json.dumps({
            "error": "Invalid JSON in anomaly_json parameter",
            "hint": "Pass the raw JSON output from observe_anomaly"
        }, indent=2)

    fact = anomaly.get("fact", str(anomaly))
    surprise_level = anomaly.get("surprise_level", "surprising")
    domain = anomaly.get("domain", "general")
    context = anomaly.get("context", [])

    from ..core.prompts import DOMAIN_GUIDANCE
    from ..core.models import Domain

    try:
        domain_enum = Domain(domain)
    except ValueError:
        domain_enum = Domain.GENERAL

    domain_guidance = DOMAIN_GUIDANCE.get(domain_enum, DOMAIN_GUIDANCE[Domain.GENERAL])

    context_str = "\n".join(f"- {c}" for c in context) if context else "None provided"

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Generate {num_hypotheses} explanatory hypotheses through ABDUCTION.

## The Surprising Fact (C)
{fact}

## Surprise Level
{surprise_level}

## Context
{context_str}

## Domain
{domain}

{domain_guidance}

## Abduction Requirement

For each hypothesis A, it must be true that:
"If A were true, then {fact} would be a matter of course."

## Generation Guidelines

- Hypotheses must be DIVERSE (not variations of the same idea)
- Include at least one "surprising" hypothesis (unlikely but high explanatory power)
- Each must be independently testable/falsifiable
- Consider multiple causal pathways

## Output Schema

Respond with ONLY this JSON structure:
```json
{{
    "hypotheses": [
        {{
            "id": "H1",
            "statement": "clear, falsifiable hypothesis statement",
            "explains_anomaly": "how this hypothesis makes the observation expected",
            "prior_probability": 0.0-1.0,
            "assumptions": [
                {{"statement": "assumption required", "testable": true}}
            ],
            "testable_predictions": [
                {{
                    "prediction": "observable consequence if true",
                    "test_method": "how to test this",
                    "if_true": "what this result means",
                    "if_false": "what this result means"
                }}
            ]
        }}
    ]
}}
```

Generate exactly {num_hypotheses} hypotheses.
"""

    return json.dumps({
        "type": "prompt",
        "phase": 2,
        "phase_name": "hypothesis_generation",
        "prompt": prompt,
        "next_tool": "evaluate_via_ibe",
        "usage": "Execute this prompt with an LLM, then pass the hypotheses JSON to evaluate_via_ibe()"
    }, indent=2)


# =============================================================================
# TOOL 3: EVALUATE VIA IBE (Phase 3 - Inference to Best Explanation)
# =============================================================================
@mcp.tool()
def evaluate_via_ibe(
    anomaly_json: str,
    hypotheses_json: str,
    use_council: bool = False
) -> str:
    """
    PHASE 3: Select the best explanation using Inference to Best Explanation (IBE).

    This is the FINAL tool in the 3-phase Peircean abductive loop:
    1. observe_anomaly → 2. generate_hypotheses → 3. evaluate_via_ibe

    Peirce's Schema: "Hence, there is reason to suspect that A is true."

    Args:
        anomaly_json: The JSON output from observe_anomaly (Phase 1).
            Example: '{"anomaly": {"fact": "...", "surprise_level": "high", ...}}'
        hypotheses_json: The JSON output from generate_hypotheses (Phase 2).
            Example: '{"hypotheses": [{"id": "H1", "statement": "...", ...}]}'
        use_council: Include Council of Critics multi-perspective evaluation (default: false).
            When true, hypotheses are evaluated by 5 critics:
            - Empiricist: testability, evidence
            - Logician: consistency, parsimony
            - Pragmatist: actionability, consequences
            - Economist: cost-benefit of investigation
            - Skeptic: alternative explanations, edge cases

    Returns:
        A prompt. Execute it to get JSON like:
        {
            "evaluation": {
                "best_hypothesis": "H1",
                "scores": {
                    "H1": {
                        "explanatory_power": 0.85,
                        "parsimony": 0.70,
                        "testability": 0.90,
                        "consilience": 0.75,
                        "composite": 0.80
                    },
                    "H2": {...}
                },
                "ranking": ["H1", "H3", "H2"],
                "verdict": "investigate",
                "confidence": 0.78,
                "rationale": "H1 provides the strongest explanation with lowest test cost",
                "next_steps": [
                    "Pull support ticket trends for churned users",
                    "Analyze usage patterns 30 days pre-churn"
                ],
                "alternative_if_wrong": "If H1 falsified, H3 becomes most probable"
            }
        }

    Termination:
        This is the final phase. The output contains the selected hypothesis
        and recommended next steps for testing/validation.
    """
    logger.info(f"Phase 3: Evaluating hypotheses via IBE (council={use_council})")

    # Parse inputs
    try:
        anomaly_data = json.loads(anomaly_json)
        if "anomaly" in anomaly_data:
            anomaly = anomaly_data["anomaly"]
        else:
            anomaly = anomaly_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in anomaly_json parameter")
        return json.dumps({
            "error": "Invalid JSON in anomaly_json parameter"
        }, indent=2)

    try:
        hypotheses_data = json.loads(hypotheses_json)
        if "hypotheses" in hypotheses_data:
            hypotheses = hypotheses_data["hypotheses"]
        else:
            hypotheses = hypotheses_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in hypotheses_json parameter")
        return json.dumps({
            "error": "Invalid JSON in hypotheses_json parameter"
        }, indent=2)

    fact = anomaly.get("fact", str(anomaly))
    hypotheses_formatted = json.dumps(hypotheses, indent=2)

    council_section = ""
    if use_council:
        council_section = """
## Council of Critics Evaluation

Before scoring, evaluate each hypothesis from these 5 perspectives:

### The Empiricist
- What empirical evidence supports or refutes each hypothesis?
- What observations would we expect if each were true?
- What data is missing that would be decisive?

### The Logician
- Is each hypothesis internally consistent?
- Does it contradict any known facts?
- Does the explanation actually follow from the hypothesis?

### The Pragmatist
- What practical difference does each hypothesis make?
- If true, what should we DO differently?
- Which hypothesis is most actionable?

### The Economist
- Which hypothesis is cheapest to test?
- Which would be most informative if confirmed or refuted?
- What's the expected value of investigating each?

### The Skeptic
- What would DISPROVE each hypothesis?
- What are we assuming without justification?
- Could this be explained more simply?

Include a "council" section in your output with each critic's verdict.
"""

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Select the BEST EXPLANATION using Inference to Best Explanation (IBE).

## The Surprising Fact (C)
{fact}

## Candidate Hypotheses
{hypotheses_formatted}

{council_section}

## IBE Evaluation Criteria

Score each hypothesis (0.0-1.0) on:

1. **Explanatory Power**: How well does it make C "a matter of course"?
   - 1.0: Makes the observation completely expected
   - 0.5: Partially explains
   - 0.0: Leaves observation just as surprising

2. **Parsimony**: How few assumptions are required? (Occam's Razor)
   - 1.0: Minimal assumptions, all well-established
   - 0.5: Moderate assumptions
   - 0.0: Many extraordinary assumptions

3. **Testability**: How easy is it to verify/falsify?
   - 1.0: Immediately testable with available resources
   - 0.5: Testable with effort
   - 0.0: Very difficult to test

4. **Consilience**: How well does it fit with other knowledge?
   - 1.0: Perfectly consistent with established knowledge
   - 0.5: Compatible but requires adjustment
   - 0.0: Contradicts established knowledge

5. **Fertility**: Does it generate new predictions/insights?
   - 1.0: Rich implications, many testable predictions
   - 0.5: Some additional predictions
   - 0.0: Explains only this observation

## Verdict Options

- "accept": High confidence, proceed as if true
- "investigate": Promising, needs testing
- "defer": Insufficient information, gather more data
- "reject": Low confidence, unlikely to be true

## Output Schema

Respond with ONLY this JSON structure:
```json
{{
    "evaluation": {{
        "best_hypothesis": "H1",
        "scores": {{
            "H1": {{
                "explanatory_power": 0.0-1.0,
                "parsimony": 0.0-1.0,
                "testability": 0.0-1.0,
                "consilience": 0.0-1.0,
                "fertility": 0.0-1.0,
                "composite": 0.0-1.0
            }}
        }},
        "ranking": ["H1", "H3", "H2"],
        "verdict": "investigate|accept|defer|reject",
        "confidence": 0.0-1.0,
        "rationale": "why this hypothesis was selected",
        "next_steps": ["action 1", "action 2"],
        "alternative_if_wrong": "fallback hypothesis and why"
    }}
}}
```
"""

    return json.dumps({
        "type": "prompt",
        "phase": 3,
        "phase_name": "inference_to_best_explanation",
        "prompt": prompt,
        "next_tool": None,
        "usage": "Execute this prompt with an LLM. This is the final phase - output contains the selected hypothesis and recommended actions."
    }, indent=2)


# =============================================================================
# BONUS TOOL: SINGLE-SHOT ABDUCTION
# =============================================================================
@mcp.tool()
def abduce_single_shot(
    observation: str,
    context: Optional[str] = None,
    domain: str = "general",
    num_hypotheses: int = 5
) -> str:
    """
    SINGLE-SHOT: Complete abductive reasoning in one prompt.

    Combines all 3 phases (observe → generate → evaluate) into a single operation.
    Use this for quick analysis when you don't need intermediate results.

    For step-by-step control, use the 3-phase flow instead:
    1. observe_anomaly → 2. generate_hypotheses → 3. evaluate_via_ibe

    Args:
        observation: The surprising/anomalous fact to explain.
            Example: "Customer churn rate doubled in Q3"
        context: Additional background information (optional).
            Example: "No price changes, NPS stable, no competitor launches"
        domain: Domain context for hypothesis generation.
            Options: "general", "financial", "legal", "medical", "technical", "scientific"
        num_hypotheses: Number of hypotheses to generate (default: 5).

    Returns:
        A prompt. Execute it to get JSON like:
        {
            "observation_analysis": {
                "fact": "Customer churn rate doubled in Q3",
                "surprise_level": "high",
                "expected_baseline": "5% quarterly churn"
            },
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "...",
                    "scores": {...}
                }
            ],
            "selection": {
                "best_hypothesis": "H1",
                "confidence": 0.78,
                "next_steps": [...]
            }
        }
    """
    logger.info(f"Single-shot abduction in domain '{domain}'")

    from ..core.prompts import DOMAIN_GUIDANCE
    from ..core.models import Domain

    try:
        domain_enum = Domain(domain)
    except ValueError:
        domain_enum = Domain.GENERAL

    domain_guidance = DOMAIN_GUIDANCE.get(domain_enum, DOMAIN_GUIDANCE[Domain.GENERAL])

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Perform COMPLETE abductive reasoning on this observation.

## The Observation
{observation}

## Context
{context or "No additional context provided."}

## Domain
{domain}

{domain_guidance}

## Peirce's Abductive Schema

1. "The surprising fact, C, is observed."
2. "But if A were true, C would be a matter of course."
3. "Hence, there is reason to suspect that A is true."

## Your Task

### Phase 1: Analyze the Surprise
- What makes this surprising?
- What would have been expected?
- How surprising is it? (0.0-1.0)

### Phase 2: Generate {num_hypotheses} Hypotheses
For each hypothesis:
- Clear, falsifiable statement
- How it explains the observation
- Prior probability
- Testable predictions

### Phase 3: Select Best Explanation (IBE)
Evaluate on: explanatory power, parsimony, testability, consilience
Select the best and justify.

## Output Schema

Respond with ONLY this JSON structure:
```json
{{
    "observation_analysis": {{
        "fact": "restated observation",
        "surprise_level": "expected|mild|surprising|high|anomalous",
        "surprise_score": 0.0-1.0,
        "expected_baseline": "what was expected",
        "surprise_source": "why surprising"
    }},
    "hypotheses": [
        {{
            "id": "H1",
            "statement": "hypothesis statement",
            "explains_anomaly": "how it explains",
            "prior_probability": 0.0-1.0,
            "testable_predictions": ["prediction 1"],
            "scores": {{
                "explanatory_power": 0.0-1.0,
                "parsimony": 0.0-1.0,
                "testability": 0.0-1.0,
                "consilience": 0.0-1.0,
                "composite": 0.0-1.0
            }}
        }}
    ],
    "selection": {{
        "best_hypothesis": "H1",
        "confidence": 0.0-1.0,
        "rationale": "why selected",
        "next_steps": ["action 1", "action 2"]
    }}
}}
```
"""

    return json.dumps({
        "type": "prompt",
        "phase": "single_shot",
        "phase_name": "complete_abduction",
        "prompt": prompt,
        "usage": "Execute this prompt with an LLM for complete abductive analysis in one step."
    }, indent=2)


# =============================================================================
# TOOL: CRITIC EVALUATION (Council of Critics)
# =============================================================================
@mcp.tool()
def critic_evaluate(
    critic: str,
    anomaly_json: str,
    hypotheses_json: str
) -> str:
    """
    COUNCIL: Get evaluation from a specific critic perspective.

    The Council of Critics provides multi-perspective hypothesis evaluation.
    Use this when you want detailed analysis from a specific viewpoint.

    Available Critics:
        - empiricist: Evaluates testability and evidence
        - logician: Evaluates consistency and parsimony
        - pragmatist: Evaluates actionability and consequences
        - economist: Evaluates cost-benefit of investigation
        - skeptic: Challenges assumptions, proposes alternatives

    Args:
        critic: Which critic to consult.
            Options: "empiricist", "logician", "pragmatist", "economist", "skeptic"
            Example: "skeptic"
        anomaly_json: The JSON output from observe_anomaly (Phase 1).
            Example: '{"anomaly": {"fact": "...", "surprise_level": "high"}}'
        hypotheses_json: The JSON output from generate_hypotheses (Phase 2).
            Example: '{"hypotheses": [{"id": "H1", "statement": "..."}]}'

    Returns:
        A prompt for the specified critic's evaluation. Execute to get JSON like:
        {
            "perspective": "skeptic",
            "evaluation": "overall skeptical assessment",
            "per_hypothesis": {
                "H1": {
                    "falsification_criteria": ["how to disprove"],
                    "unjustified_assumptions": ["assumption 1"],
                    "skepticism_score": 0.75
                }
            },
            "strongest_objections": {"H1": "main objection"}
        }
    """
    logger.info(f"Council: Consulting the {critic}")

    valid_critics = ["empiricist", "logician", "pragmatist", "economist", "skeptic"]
    if critic not in valid_critics:
        logger.error(f"Invalid critic: {critic}")
        return json.dumps({
            "error": f"Invalid critic: {critic}",
            "valid_options": valid_critics
        }, indent=2)

    # Parse inputs
    try:
        anomaly_data = json.loads(anomaly_json)
        anomaly = anomaly_data.get("anomaly", anomaly_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid anomaly_json"}, indent=2)

    try:
        hypotheses_data = json.loads(hypotheses_json)
        hypotheses = hypotheses_data.get("hypotheses", hypotheses_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid hypotheses_json"}, indent=2)

    fact = anomaly.get("fact", str(anomaly))
    hypotheses_formatted = json.dumps(hypotheses, indent=2)

    critic_prompts = {
        "empiricist": f"""You are THE EMPIRICIST on the Council of Critics.

Your role: Evaluate hypotheses based on EVIDENCE and OBSERVATION.

Questions you must answer:
- What empirical evidence supports or refutes each hypothesis?
- What observations would we expect if each hypothesis were true?
- Have similar situations produced similar explanations historically?
- What data is missing that would be decisive?

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

Output ONLY this JSON:
```json
{{
    "perspective": "empiricist",
    "evaluation": "overall empirical assessment",
    "per_hypothesis": {{
        "H1": {{
            "supporting_evidence": ["evidence 1"],
            "contradicting_evidence": ["evidence 1"],
            "missing_evidence": ["evidence 1"],
            "empirical_score": 0.0-1.0
        }}
    }},
    "recommended_tests": ["test 1", "test 2"],
    "strongest_hypothesis": "H1",
    "concerns": ["concern 1"]
}}
```""",

        "logician": f"""You are THE LOGICIAN on the Council of Critics.

Your role: Evaluate hypotheses based on LOGICAL CONSISTENCY.

Questions you must answer:
- Is each hypothesis internally consistent?
- Does it contradict any known facts?
- Are the assumptions compatible with each other?
- Does the explanation actually follow from the hypothesis?

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

Output ONLY this JSON:
```json
{{
    "perspective": "logician",
    "evaluation": "overall logical assessment",
    "per_hypothesis": {{
        "H1": {{
            "internal_consistency": true,
            "logical_gaps": ["gap 1"],
            "contradictions": ["contradiction 1"],
            "validity_score": 0.0-1.0
        }}
    }},
    "strongest_hypothesis": "H1",
    "logical_concerns": ["concern 1"]
}}
```""",

        "pragmatist": f"""You are THE PRAGMATIST on the Council of Critics.

Your role: Evaluate hypotheses based on PRACTICAL CONSEQUENCES.

Peirce's Pragmatic Maxim: "Consider what effects, that might conceivably have practical bearings, we conceive the object of our conception to have."

Questions you must answer:
- What practical difference does each hypothesis make?
- If true, what should we DO differently?
- What are the real-world implications?
- Which hypothesis is most actionable?

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

Output ONLY this JSON:
```json
{{
    "perspective": "pragmatist",
    "evaluation": "overall pragmatic assessment",
    "per_hypothesis": {{
        "H1": {{
            "practical_implications": ["implication 1"],
            "recommended_actions": ["action 1"],
            "actionability_score": 0.0-1.0
        }}
    }},
    "most_actionable": "H1",
    "pragmatic_concerns": ["concern 1"]
}}
```""",

        "economist": f"""You are THE ECONOMIST OF RESEARCH on the Council of Critics.

Your role: Evaluate hypotheses based on ECONOMY OF INQUIRY.

Peirce emphasized the "economy of research" - test hypotheses in an order that maximizes expected information gain per unit cost.

Questions you must answer:
- Which hypothesis is cheapest to test?
- Which would be most informative if confirmed or refuted?
- What's the expected value of investigating each?
- What's the opportunity cost of pursuing each path?

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

Output ONLY this JSON:
```json
{{
    "perspective": "economist",
    "evaluation": "overall economic assessment",
    "per_hypothesis": {{
        "H1": {{
            "test_cost": "low|medium|high",
            "information_value": 0.0-1.0,
            "expected_value": 0.0-1.0,
            "time_to_test": "estimate"
        }}
    }},
    "optimal_test_order": ["H1", "H3", "H2"],
    "best_roi_hypothesis": "H1",
    "recommended_first_test": "description"
}}
```""",

        "skeptic": f"""You are THE SKEPTIC on the Council of Critics.

Your role: Challenge hypotheses and identify potential flaws.

Questions you must answer:
- What would DISPROVE each hypothesis?
- What are we assuming without justification?
- Could this be explained more simply?
- Are we falling for any cognitive biases?

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

Output ONLY this JSON:
```json
{{
    "perspective": "skeptic",
    "evaluation": "overall skeptical assessment",
    "per_hypothesis": {{
        "H1": {{
            "falsification_criteria": ["how to disprove"],
            "unjustified_assumptions": ["assumption 1"],
            "potential_biases": ["bias 1"],
            "simpler_alternatives": ["alternative 1"],
            "skepticism_score": 0.0-1.0
        }}
    }},
    "most_vulnerable_hypothesis": "H1",
    "strongest_objections": {{
        "H1": "main objection"
    }},
    "devil_advocate_tests": ["test 1"]
}}
```"""
    }

    prompt = f"{SYSTEM_DIRECTIVE}\n\n{critic_prompts[critic]}"

    return json.dumps({
        "type": "prompt",
        "phase": "council",
        "critic": critic,
        "prompt": prompt,
        "usage": f"Execute this prompt to get the {critic}'s evaluation of the hypotheses."
    }, indent=2)


# =============================================================================
# ENTRY POINT
# =============================================================================
def main() -> None:
    """Entry point for the Peircean Logic Harness MCP server."""
    logger.info("Peircean Logic Harness starting...")
    logger.info("A Logic Harness for abductive inference. Anomaly in → Hypothesis out.")
    mcp.run()


if __name__ == "__main__":
    main()
