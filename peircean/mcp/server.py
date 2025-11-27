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

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

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
    instructions="A Logic Harness for abductive inference. Anomaly in → Hypothesis out.",
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
# ERROR RESPONSE HELPER
# =============================================================================
def error_response(error: str, hint: str | None = None) -> str:
    """Standardized error response format for all tools."""
    response: dict[str, str] = {"type": "error", "error": error}
    if hint:
        response["hint"] = hint
    return json.dumps(response, indent=2)


# =============================================================================
# TOOL 1: OBSERVE ANOMALY (Phase 1 - Register C)
# =============================================================================
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def peircean_observe_anomaly(
    observation: str, context: str | None = None, domain: str = "general"
) -> str:
    """
    PHASE 1: Register the surprising fact (C).

    This is the FIRST tool in the 3-phase Peircean abductive loop:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

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
        Pass the anomaly JSON to peircean_generate_hypotheses() for Phase 2.
    """
    logger.info(f"Phase 1: Observing anomaly in domain '{domain}'")

    # Input validation
    if not observation or not observation.strip():
        return error_response(
            "Empty observation provided",
            hint="Provide a non-empty observation describing the surprising fact",
        )

    from ..core.models import Domain
    from ..core.prompts import DOMAIN_GUIDANCE

    try:
        domain_enum = Domain(domain)
    except ValueError:
        logger.warning(f"Unknown domain '{domain}', defaulting to 'general'")
        domain_enum = Domain.GENERAL

    domain_guidance = DOMAIN_GUIDANCE.get(domain_enum, DOMAIN_GUIDANCE[Domain.GENERAL])

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Analyze this observation to determine if it constitutes a "surprising fact" (C) in the Peircean sense.
Also, NOMINATE a "Council of Critics" (3-5 specialist roles) who would be best suited to evaluate hypotheses for this specific anomaly.

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
        "surprise_source": "why this violates expectations",
        "recommended_council": ["Specialist Role 1", "Specialist Role 2", "Specialist Role 3"]
    }}
}}
```
"""

    return json.dumps(
        {
            "type": "prompt",
            "phase": 1,
            "phase_name": "observation",
            "prompt": prompt,
            "next_tool": "peircean_generate_hypotheses",
            "usage": "Execute this prompt with an LLM, then pass the anomaly JSON to peircean_generate_hypotheses()",
        },
        indent=2,
    )


# =============================================================================
# TOOL 2: GENERATE HYPOTHESES (Phase 2 - Generate A's)
# =============================================================================
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def peircean_generate_hypotheses(anomaly_json: str, num_hypotheses: int = 5) -> str:
    """
    PHASE 2: Generate candidate hypotheses (A's) that would explain the anomaly.

    This is the SECOND tool in the 3-phase Peircean abductive loop:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

    Peirce's Schema: "But if A were true, C would be a matter of course."

    Args:
        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).
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
        Pass the hypotheses JSON to peircean_evaluate_via_ibe() for Phase 3.
    """
    logger.info(f"Phase 2: Generating {num_hypotheses} hypotheses")

    # Input validation
    if num_hypotheses < 1 or num_hypotheses > 20:
        return error_response(
            f"num_hypotheses must be between 1 and 20, got {num_hypotheses}",
            hint="Use a value between 1 and 20 for num_hypotheses",
        )

    # Parse the anomaly JSON
    try:
        anomaly_data = json.loads(anomaly_json)
        if "anomaly" in anomaly_data:
            anomaly = anomaly_data["anomaly"]
        else:
            anomaly = anomaly_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in anomaly_json parameter")
        return error_response(
            "Invalid JSON in anomaly_json parameter",
            hint="Pass the raw JSON output from peircean_observe_anomaly",
        )

    fact = anomaly.get("fact", str(anomaly))
    surprise_level = anomaly.get("surprise_level", "surprising")
    domain = anomaly.get("domain", "general")
    context = anomaly.get("context", [])

    from ..core.models import Domain
    from ..core.prompts import DOMAIN_GUIDANCE

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

    return json.dumps(
        {
            "type": "prompt",
            "phase": 2,
            "phase_name": "hypothesis_generation",
            "prompt": prompt,
            "next_tool": "peircean_evaluate_via_ibe",
            "usage": "Execute this prompt with an LLM, then pass the hypotheses JSON to peircean_evaluate_via_ibe()",
        },
        indent=2,
    )


# =============================================================================
# TOOL 3: EVALUATE VIA IBE (Phase 3 - Inference to Best Explanation)
# =============================================================================
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def peircean_evaluate_via_ibe(
    anomaly_json: str,
    hypotheses_json: str,
    use_council: bool = False,
    custom_council: list[str] | None = None,
) -> str:
    """
    PHASE 3: Select the best explanation using Inference to Best Explanation (IBE).

    This is the FINAL tool in the 3-phase Peircean abductive loop:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

    Peirce's Schema: "Hence, there is reason to suspect that A is true."

    Args:
        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).
        hypotheses_json: The JSON output from peircean_generate_hypotheses (Phase 2).
        use_council: Include Council of Critics (default: false).
        custom_council: Optional list of specific critic roles to use.
            Example: ["Forensic Accountant", "Security Engineer", "Legal Counsel"]
            If provided, overrides the default 5 critics.

    Returns:
        A prompt for IBE evaluation with the specified council.
    """
    logger.info(
        f"Phase 3: Evaluating hypotheses via IBE (council={use_council}, custom={custom_council})"
    )

    # Parse inputs
    try:
        anomaly_data = json.loads(anomaly_json)
        if "anomaly" in anomaly_data:
            anomaly = anomaly_data["anomaly"]
        else:
            anomaly = anomaly_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in anomaly_json parameter")
        return error_response(
            "Invalid JSON in anomaly_json parameter",
            hint="Pass the raw JSON output from peircean_observe_anomaly",
        )

    try:
        hypotheses_data = json.loads(hypotheses_json)
        if "hypotheses" in hypotheses_data:
            hypotheses = hypotheses_data["hypotheses"]
        else:
            hypotheses = hypotheses_data
    except json.JSONDecodeError:
        logger.error("Invalid JSON in hypotheses_json parameter")
        return error_response(
            "Invalid JSON in hypotheses_json parameter",
            hint="Pass the raw JSON output from peircean_generate_hypotheses",
        )

    fact = anomaly.get("fact", str(anomaly))
    hypotheses_formatted = json.dumps(hypotheses, indent=2)

    council_section = ""
    scoring_criteria = ""
    score_keys = []

    if custom_council:
        council_section = "## Council of Critics Evaluation\n\nEvaluate each hypothesis from the perspectives of these nominated specialists:\n\n"
        scoring_criteria = "## Council Scoring Criteria\n\nScore each hypothesis (0.0-1.0) based on the Specialist's perspective:\n\n"

        for role in custom_council:
            slug = role.lower().replace(" ", "_")
            score_keys.append(slug)

            council_section += f"### The {role}\n"
            council_section += (
                f"- How does this hypothesis look from the perspective of a {role}?\n"
            )
            council_section += (
                "- What specific evidence or logic supports/refutes it in your domain?\n\n"
            )

            scoring_criteria += (
                f"{len(score_keys)}. **{role} Score**: Endorsement from the {role}.\n"
            )
            scoring_criteria += "   - 1.0: Strongly endorsed by this domain expertise.\n"
            scoring_criteria += "   - 0.0: Rejected by this domain expertise.\n\n"

    elif use_council:
        score_keys = ["empiricist", "logician", "pragmatist", "economist", "skeptic"]
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
        scoring_criteria = """
## Council Scoring Criteria

Score each hypothesis (0.0-1.0) based on the Council's perspectives:

1. **Empiricist Score**: Fit with evidence and testability.
   - 1.0: Strongly supported by evidence, easily testable.
   - 0.0: Contradicted by evidence, unfalsifiable.

2. **Logician Score**: Internal consistency and parsimony.
   - 1.0: Perfectly consistent, minimal assumptions.
   - 0.0: Self-contradictory, relies on ad-hoc assumptions.

3. **Pragmatist Score**: Actionability and utility.
   - 1.0: Clear path to action, high utility if true.
   - 0.0: No clear action, irrelevant if true.

4. **Economist Score**: Cost-effectiveness.
   - 1.0: Cheap/fast to verify, high value of information.
   - 0.0: Prohibitively expensive to verify, low value.

5. **Skeptic Score**: Robustness (Higher is BETTER/HARDER to falsify).
   - 1.0: Withstands strong scrutiny, no obvious alternatives.
   - 0.0: Easily debunked, many simpler alternatives.
"""
    else:
        # No council - fallback to standard IBE criteria if desired,
        # but for now we'll just use the standard 5 criteria as "General" scores
        # or we could enforce council usage. Let's default to the standard 5
        # even if use_council is False, to keep schema consistent,
        # or we can simplify.
        # For this implementation, we will default to the standard 5 criteria
        # but label them as "General Evaluation".
        score_keys = ["explanatory_power", "parsimony", "testability", "consilience", "fertility"]
        scoring_criteria = """
## Evaluation Criteria

Score each hypothesis (0.0-1.0) on:
1. Explanatory Power
2. Parsimony
3. Testability
4. Consilience
5. Fertility
"""

    # Construct the dynamic JSON schema for scores
    score_fields = ",\n                ".join([f'"{k}": 0.0-1.0' for k in score_keys])

    prompt = f"""{SYSTEM_DIRECTIVE}

TASK: Select the BEST EXPLANATION using Inference to Best Explanation (IBE).

## The Surprising Fact (C)
{fact}

## Candidate Hypotheses
{hypotheses_formatted}

{council_section}

{scoring_criteria}

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
                {score_fields},
                "composite": 0.0-1.0,
                "rationale": "explanation for these scores"
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

    return json.dumps(
        {
            "type": "prompt",
            "phase": 3,
            "phase_name": "inference_to_best_explanation",
            "prompt": prompt,
            "next_tool": None,
            "usage": "Execute this prompt with an LLM. This is the final phase - output contains the selected hypothesis and recommended actions.",
        },
        indent=2,
    )


# =============================================================================
# BONUS TOOL: SINGLE-SHOT ABDUCTION
# =============================================================================
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def peircean_abduce_single_shot(
    observation: str,
    context: str | None = None,
    domain: str = "general",
    num_hypotheses: int = 5,
) -> str:
    """
    SINGLE-SHOT: Complete abductive reasoning in one prompt.

    Combines all 3 phases (observe → generate → evaluate) into a single operation.
    Use this for quick analysis when you don't need intermediate results.

    For step-by-step control, use the 3-phase flow instead:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

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

    # Input validation
    if not observation or not observation.strip():
        return error_response(
            "Empty observation provided",
            hint="Provide a non-empty observation describing the surprising fact",
        )

    if num_hypotheses < 1 or num_hypotheses > 20:
        return error_response(
            f"num_hypotheses must be between 1 and 20, got {num_hypotheses}",
            hint="Use a value between 1 and 20 for num_hypotheses",
        )

    from ..core.models import Domain
    from ..core.prompts import DOMAIN_GUIDANCE

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

    return json.dumps(
        {
            "type": "prompt",
            "phase": "single_shot",
            "phase_name": "complete_abduction",
            "prompt": prompt,
            "usage": "Execute this prompt with an LLM for complete abductive analysis in one step.",
        },
        indent=2,
    )


# =============================================================================
# TOOL: CRITIC EVALUATION (Council of Critics)
# =============================================================================
@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def peircean_critic_evaluate(critic: str, anomaly_json: str, hypotheses_json: str) -> str:
    """
    COUNCIL: Get evaluation from a specific critic perspective.

    The Council of Critics provides multi-perspective hypothesis evaluation.
    You can request ANY specialist role.

    Args:
        critic: The role to adopt.
            Examples: "empiricist", "skeptic", "forensic_accountant", "security_engineer"
        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).
        hypotheses_json: The JSON output from peircean_generate_hypotheses (Phase 2).

    Example:
        peircean_critic_evaluate(
            critic="forensic_accountant",
            anomaly_json='{"anomaly": ...}',
            hypotheses_json='{"hypotheses": ...}'
        )

    Returns:
        A prompt for the specified critic's evaluation.
    """
    # Input validation: fallback to general_critic if empty
    if not critic or not critic.strip():
        logger.warning("Empty critic provided, falling back to 'general_critic'")
        critic = "general_critic"

    logger.info(f"Council: Consulting the {critic}")

    # Parse inputs
    try:
        anomaly_data = json.loads(anomaly_json)
        anomaly = anomaly_data.get("anomaly", anomaly_data)
    except json.JSONDecodeError:
        return error_response(
            "Invalid JSON in anomaly_json parameter",
            hint="Pass the raw JSON output from peircean_observe_anomaly",
        )

    try:
        hypotheses_data = json.loads(hypotheses_json)
        hypotheses = hypotheses_data.get("hypotheses", hypotheses_data)
    except json.JSONDecodeError:
        return error_response(
            "Invalid JSON in hypotheses_json parameter",
            hint="Pass the raw JSON output from peircean_generate_hypotheses",
        )

    fact = anomaly.get("fact", str(anomaly))
    hypotheses_formatted = json.dumps(hypotheses, indent=2)

    prompt = f"""You are THE {critic.upper()} on the Council of Critics.

Your role: Evaluate hypotheses based on the specific expertise, concerns, and methodology of a {critic}.

## The Surprising Fact
{fact}

## Hypotheses
{hypotheses_formatted}

## Your Evaluation

1. How does this look from the perspective of a {critic}?
2. What specific evidence or logic supports/refutes each hypothesis in your domain?
3. What would you recommend checking?

Output ONLY this JSON:
```json
{{
    "perspective": "{critic}",
    "evaluation": "overall assessment from this perspective",
    "per_hypothesis": {{
        "H1": {{
            "strengths": ["point 1"],
            "weaknesses": ["point 1"],
            "score": 0.0-1.0
        }}
    }},
    "strongest_hypothesis": "H1",
    "concerns": ["concern 1"]
}}
```"""

    return json.dumps(
        {
            "type": "prompt",
            "phase": "critic_evaluation",
            "critic": critic,
            "prompt": prompt,
            "usage": f"Execute this prompt to get the {critic}'s perspective.",
        },
        indent=2,
    )


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
