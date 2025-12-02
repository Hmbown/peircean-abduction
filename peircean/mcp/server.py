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

from pydantic import ValidationError

from .errors import (
    ErrorCode,
    format_error_response,
    format_json_parse_error,
    format_validation_error,
)
from .fastmcp import FastMCP
from .inputs import (
    AbduceSingleShotInput,
    CriticEvaluateInput,
    Domain,
    EvaluateViaIBEInput,
    GenerateHypothesesInput,
    ObserveAnomalyInput,
)
from .types import ToolAnnotations

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
# CONSTANTS
# =============================================================================
CHARACTER_LIMIT = 50000  # Maximum response size in characters
"""
Character limit for responses to prevent overwhelming context windows.
Responses exceeding this limit will be truncated with guidance on filtering.
"""


# =============================================================================
# MCP SERVER INITIALIZATION
# =============================================================================
MCP_INSTRUCTIONS = """A Logic Harness for abductive inference. Anomaly in → Hypothesis out.

## AUTOMATIC WORKFLOW

When a user asks you to analyze an anomaly or surprising observation using Peircean abduction:

1. **For quick analysis**: Use `peircean_abduce_single_shot` - it runs all 3 phases in one prompt.

2. **For detailed analysis**: Automatically run through all 3 phases in sequence:
   - Call `peircean_observe_anomaly` → Execute the returned prompt → Save anomaly JSON
   - Call `peircean_generate_hypotheses` with anomaly JSON → Execute prompt → Save hypotheses JSON
   - Call `peircean_evaluate_via_ibe` with both JSONs → Execute prompt → Present final results

   **IMPORTANT**: Do NOT stop after Phase 1. Continue automatically through all phases unless the user explicitly asks for step-by-step control.

## TOOLS

| Tool | Phase | Purpose |
|------|-------|---------|
| `peircean_observe_anomaly` | 1 | Register the surprising fact |
| `peircean_generate_hypotheses` | 2 | Generate candidate explanations |
| `peircean_evaluate_via_ibe` | 3 | Select best explanation via IBE |
| `peircean_abduce_single_shot` | All | Complete analysis in one step |
| `peircean_critic_evaluate` | Aux | Get specific critic perspective |

## DOMAINS

Use the `domain` parameter to get domain-specific hypothesis types:
- `technical`: Race conditions, resource exhaustion, network issues
- `financial`: Market microstructure, information asymmetry
- `legal`: Statutory interpretation, precedent conflicts
- `medical`: Differential diagnosis, drug interactions
- `scientific`: Measurement error, confounding variables
- `general`: Causal, systemic, human factors
"""

mcp = FastMCP(
    name="peircean",
    instructions=MCP_INSTRUCTIONS,
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
# DOMAIN GUIDANCE (also exposed as resources)
# =============================================================================
DOMAIN_GUIDANCE = {
    Domain.GENERAL: """
## Domain Guidance: General

Consider hypotheses from multiple categories:
- Causal (direct cause-effect)
- Systemic (emergent from system interactions)
- Human factors (error, intention, miscommunication)
- External factors (environment, third parties)
- Measurement/observation error
""",
    Domain.FINANCIAL: """
## Domain Guidance: Financial

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
## Domain Guidance: Legal

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
## Domain Guidance: Medical

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
## Domain Guidance: Technical

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
## Domain Guidance: Scientific

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
# MCP RESOURCES: Domain Guidance
# =============================================================================
@mcp.resource("peircean://domain/{domain_name}")
def get_domain_guidance(domain_name: str) -> str:
    """
    Get domain-specific guidance for hypothesis generation.

    This resource provides specialized guidance for generating
    hypotheses in different domains (technical, financial, etc.).
    """
    try:
        domain = Domain(domain_name)
        return DOMAIN_GUIDANCE.get(domain, DOMAIN_GUIDANCE[Domain.GENERAL])
    except ValueError:
        return DOMAIN_GUIDANCE[Domain.GENERAL]


@mcp.resource("peircean://schema/anomaly")
def get_anomaly_schema() -> str:
    """
    Get the JSON schema for anomaly analysis output.

    Use this resource to understand the expected output format
    from Phase 1 (peircean_observe_anomaly).
    """
    schema = {
        "type": "object",
        "required": ["anomaly"],
        "properties": {
            "anomaly": {
                "type": "object",
                "required": ["fact", "surprise_level", "surprise_score"],
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "Restatement of the observation",
                    },
                    "surprise_level": {
                        "type": "string",
                        "enum": ["expected", "mild", "surprising", "high", "anomalous"],
                    },
                    "surprise_score": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                    },
                    "expected_baseline": {
                        "type": "string",
                        "description": "What would normally be expected",
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain context",
                    },
                    "context": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "key_features": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "surprise_source": {
                        "type": "string",
                        "description": "Why this violates expectations",
                    },
                    "recommended_council": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Suggested specialist roles for evaluation",
                    },
                },
            }
        },
    }
    return json.dumps(schema, indent=2)


@mcp.resource("peircean://schema/hypotheses")
def get_hypotheses_schema() -> str:
    """
    Get the JSON schema for hypotheses generation output.

    Use this resource to understand the expected output format
    from Phase 2 (peircean_generate_hypotheses).
    """
    schema = {
        "type": "object",
        "required": ["hypotheses"],
        "properties": {
            "hypotheses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "statement", "explains_anomaly", "prior_probability"],
                    "properties": {
                        "id": {"type": "string", "description": "Unique ID (H1, H2, etc.)"},
                        "statement": {"type": "string", "description": "Clear hypothesis"},
                        "explains_anomaly": {"type": "string"},
                        "prior_probability": {"type": "number", "minimum": 0, "maximum": 1},
                        "assumptions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "statement": {"type": "string"},
                                    "testable": {"type": "boolean"},
                                },
                            },
                        },
                        "testable_predictions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "prediction": {"type": "string"},
                                    "test_method": {"type": "string"},
                                    "if_true": {"type": "string"},
                                    "if_false": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            }
        },
    }
    return json.dumps(schema, indent=2)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def _parse_anomaly_json(anomaly_json: str) -> tuple[dict | None, str | None]:
    """
    Parse and extract anomaly data from JSON string.

    Returns:
        Tuple of (anomaly_dict, error_response).
        If successful, error_response is None.
        If failed, anomaly_dict is None and error_response contains the error.
    """
    try:
        anomaly_data = json.loads(anomaly_json)
        if "anomaly" in anomaly_data:
            return anomaly_data["anomaly"], None
        return anomaly_data, None
    except json.JSONDecodeError:
        return None, format_json_parse_error("anomaly_json", anomaly_json[:200])


def _parse_hypotheses_json(hypotheses_json: str) -> tuple[list | None, str | None]:
    """
    Parse and extract hypotheses data from JSON string.

    Returns:
        Tuple of (hypotheses_list, error_response).
        If successful, error_response is None.
        If failed, hypotheses_list is None and error_response contains the error.
    """
    try:
        hypotheses_data = json.loads(hypotheses_json)
        if "hypotheses" in hypotheses_data:
            return hypotheses_data["hypotheses"], None
        return hypotheses_data, None
    except json.JSONDecodeError:
        return None, format_json_parse_error("hypotheses_json", hypotheses_json[:200])


def _truncate_response(response: str, limit: int = CHARACTER_LIMIT) -> str:
    """
    Truncate response if it exceeds the character limit.

    Adds truncation notice with guidance on how to get complete results.
    """
    if len(response) <= limit:
        return response

    # Try to parse and truncate intelligently
    try:
        data = json.loads(response)
        truncated_notice = {
            "truncated": True,
            "truncation_message": (
                f"Response truncated from {len(response)} to ~{limit} characters. "
                "Use pagination or add filters to see more results."
            ),
            "original_size": len(response),
        }
        # Merge notice into response
        if isinstance(data, dict):
            data["_truncation"] = truncated_notice
            return json.dumps(data, indent=2)[:limit]
    except json.JSONDecodeError:
        pass

    # Fallback: simple truncation
    return response[:limit] + f"\n\n[TRUNCATED: Response exceeded {limit} characters]"


# =============================================================================
# TOOL 1: OBSERVE ANOMALY (Phase 1 - Register C)
# =============================================================================
@mcp.tool(
    annotations=ToolAnnotations(
        title="Observe Anomaly (Phase 1)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def peircean_observe_anomaly(
    observation: str,
    context: str | None = None,
    domain: str = "general",
) -> str:
    """
    PHASE 1: Register the surprising fact (C) for abductive analysis.

    This is the FIRST tool in the 3-phase Peircean abductive loop:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

    Peirce's Schema: "The surprising fact, C, is observed."

    Use this tool when you encounter an anomaly or surprising observation that
    needs explanation. The tool analyzes the observation and prepares it for
    hypothesis generation.

    Args:
        observation: The surprising/anomalous fact observed.
            Examples:
            - "Server latency spiked 10x but CPU/memory normal"
            - "Customer churn doubled but NPS scores unchanged"
            - "Stock dropped 5% after positive earnings report"

        context: Additional background information (optional).
            Examples:
            - "No recent deployments, traffic is steady"
            - "No price changes in the last quarter"

        domain: Domain context for hypothesis generation.
            Options: general, financial, legal, medical, technical, scientific
            Default: general

    Returns:
        str: JSON containing a prompt to execute. The prompt output will be:

        Success response schema:
        {
            "anomaly": {
                "fact": "restatement of the observation",
                "surprise_level": "expected|mild|surprising|high|anomalous",
                "surprise_score": 0.0-1.0,
                "expected_baseline": "what would normally be expected",
                "domain": "technical",
                "context": ["context item 1", "context item 2"],
                "key_features": ["surprising feature 1", "surprising feature 2"],
                "surprise_source": "why this violates expectations",
                "recommended_council": ["Specialist Role 1", "Specialist Role 2"]
            }
        }

        Error response schema:
        {
            "type": "error",
            "error": "description of what went wrong",
            "code": "validation_error|invalid_json|...",
            "hint": "how to fix the error"
        }

    Examples:
        Use when: "Something unexpected happened and I need to understand why"
        Don't use when: You already know the cause and just need confirmation

    Next Step:
        Pass the anomaly JSON output to peircean_generate_hypotheses() for Phase 2.
    """
    logger.info(f"Phase 1: Observing anomaly in domain '{domain}'")

    # Validate input using Pydantic model
    try:
        params = ObserveAnomalyInput(
            observation=observation,
            context=context,
            domain=Domain(domain) if domain in [d.value for d in Domain] else Domain.GENERAL,
        )
    except ValidationError as e:
        logger.warning(f"Input validation failed: {e}")
        return format_validation_error(e)

    # Handle invalid domain gracefully
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
{params.observation}

## Context
{params.context or "No additional context provided."}

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

    response = json.dumps(
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

    return _truncate_response(response)


# =============================================================================
# TOOL 2: GENERATE HYPOTHESES (Phase 2 - Generate A's)
# =============================================================================
@mcp.tool(
    annotations=ToolAnnotations(
        title="Generate Hypotheses (Phase 2)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def peircean_generate_hypotheses(
    anomaly_json: str,
    num_hypotheses: int = 5,
) -> str:
    """
    PHASE 2: Generate candidate hypotheses (A's) that would explain the anomaly.

    This is the SECOND tool in the 3-phase Peircean abductive loop:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

    Peirce's Schema: "But if A were true, C would be a matter of course."

    Use this tool after Phase 1 to generate multiple competing explanations
    for the observed anomaly. Each hypothesis includes testable predictions
    for verification.

    Args:
        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).
            Must contain an 'anomaly' object with at least a 'fact' field.
            Example: '{"anomaly": {"fact": "...", "surprise_level": "high", "domain": "technical"}}'

        num_hypotheses: Number of distinct hypotheses to generate (1-20).
            Default: 5. Recommended: 3-5 for most use cases.
            Higher values provide more diverse explanations but increase response size.

    Returns:
        str: JSON containing a prompt to execute. The prompt output will be:

        Success response schema:
        {
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "clear, falsifiable hypothesis statement",
                    "explains_anomaly": "how this hypothesis makes the observation expected",
                    "prior_probability": 0.0-1.0,
                    "assumptions": [
                        {"statement": "assumption required", "testable": true}
                    ],
                    "testable_predictions": [
                        {
                            "prediction": "observable consequence if true",
                            "test_method": "how to test this",
                            "if_true": "what this result means",
                            "if_false": "what this result means"
                        }
                    ]
                }
            ]
        }

    Examples:
        Use when: You have analyzed an anomaly (Phase 1) and need candidate explanations
        Don't use when: You haven't run Phase 1 yet

    Next Step:
        Pass the hypotheses JSON output to peircean_evaluate_via_ibe() for Phase 3.
    """
    logger.info(f"Phase 2: Generating {num_hypotheses} hypotheses")

    # Validate num_hypotheses
    if num_hypotheses < 1 or num_hypotheses > 20:
        return format_error_response(
            f"num_hypotheses must be between 1 and 20, got {num_hypotheses}",
            code=ErrorCode.INVALID_VALUE,
            hint="Use a value between 1 and 20 for num_hypotheses",
        )

    # Parse the anomaly JSON
    anomaly, error = _parse_anomaly_json(anomaly_json)
    if error:
        logger.error("Invalid JSON in anomaly_json parameter")
        return error

    fact = anomaly.get("fact", str(anomaly))
    surprise_level = anomaly.get("surprise_level", "surprising")
    domain = anomaly.get("domain", "general")
    context = anomaly.get("context", [])

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

    response = json.dumps(
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

    return _truncate_response(response)


# =============================================================================
# TOOL 3: EVALUATE VIA IBE (Phase 3 - Inference to Best Explanation)
# =============================================================================
@mcp.tool(
    annotations=ToolAnnotations(
        title="Evaluate via IBE (Phase 3)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
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

    Use this tool after Phase 2 to evaluate and rank the generated hypotheses,
    selecting the one that provides the best explanation for the anomaly.

    Args:
        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).
            Example: '{"anomaly": {"fact": "...", "surprise_level": "high"}}'

        hypotheses_json: The JSON output from peircean_generate_hypotheses (Phase 2).
            Example: '{"hypotheses": [{"id": "H1", "statement": "..."}]}'

        use_council: Include Council of Critics evaluation (default: False).
            When True, evaluates hypotheses from 5 perspectives:
            Empiricist, Logician, Pragmatist, Economist, Skeptic.
            Provides richer analysis but increases output size.

        custom_council: Custom list of specialist roles for the Council (optional).
            Overrides the default council if provided.
            Examples: ["Forensic Accountant", "Security Engineer", "Domain Expert"]
            Maximum 10 roles.

    Returns:
        str: JSON containing a prompt to execute. The prompt output will be:

        Success response schema:
        {
            "evaluation": {
                "best_hypothesis": "H1",
                "scores": {
                    "H1": {
                        "explanatory_power": 0.0-1.0,
                        "parsimony": 0.0-1.0,
                        "testability": 0.0-1.0,
                        "consilience": 0.0-1.0,
                        "composite": 0.0-1.0,
                        "rationale": "explanation for these scores"
                    }
                },
                "ranking": ["H1", "H3", "H2"],
                "verdict": "investigate|accept|defer|reject",
                "confidence": 0.0-1.0,
                "rationale": "why this hypothesis was selected",
                "next_steps": ["action 1", "action 2"],
                "alternative_if_wrong": "fallback hypothesis and why"
            }
        }

    Examples:
        Use when: You have generated hypotheses (Phase 2) and need to select the best one
        Don't use when: You haven't run Phase 1 and 2 yet
    """
    logger.info(
        f"Phase 3: Evaluating hypotheses via IBE (council={use_council}, custom={custom_council})"
    )

    # Parse inputs
    anomaly, error = _parse_anomaly_json(anomaly_json)
    if error:
        logger.error("Invalid JSON in anomaly_json parameter")
        return error

    hypotheses, error = _parse_hypotheses_json(hypotheses_json)
    if error:
        logger.error("Invalid JSON in hypotheses_json parameter")
        return error

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

    response = json.dumps(
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

    return _truncate_response(response)


# =============================================================================
# BONUS TOOL: SINGLE-SHOT ABDUCTION
# =============================================================================
@mcp.tool(
    annotations=ToolAnnotations(
        title="Single-Shot Abduction (All Phases)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
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

    For step-by-step control and inspection of each phase, use the 3-phase flow:
    1. peircean_observe_anomaly → 2. peircean_generate_hypotheses → 3. peircean_evaluate_via_ibe

    Args:
        observation: The surprising/anomalous fact to explain.
            Examples:
            - "Customer churn rate doubled in Q3"
            - "API latency spiked with no deployment"
            - "Revenue dropped despite increased traffic"

        context: Additional background information (optional).
            Examples:
            - "No price changes, NPS stable, no competitor launches"
            - "No configuration changes in the last week"

        domain: Domain context for hypothesis generation.
            Options: general, financial, legal, medical, technical, scientific
            Default: general

        num_hypotheses: Number of hypotheses to generate (1-20).
            Default: 5. Recommended: 3-5 for most use cases.

    Returns:
        str: JSON containing a prompt to execute. The prompt output will be:

        Success response schema:
        {
            "observation_analysis": {
                "fact": "restated observation",
                "surprise_level": "expected|mild|surprising|high|anomalous",
                "surprise_score": 0.0-1.0,
                "expected_baseline": "what was expected",
                "surprise_source": "why surprising"
            },
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "hypothesis statement",
                    "explains_anomaly": "how it explains",
                    "prior_probability": 0.0-1.0,
                    "testable_predictions": ["prediction 1"],
                    "scores": {
                        "explanatory_power": 0.0-1.0,
                        "parsimony": 0.0-1.0,
                        "testability": 0.0-1.0,
                        "consilience": 0.0-1.0,
                        "composite": 0.0-1.0
                    }
                }
            ],
            "selection": {
                "best_hypothesis": "H1",
                "confidence": 0.0-1.0,
                "rationale": "why selected",
                "next_steps": ["action 1", "action 2"]
            }
        }

    Examples:
        Use when: Quick analysis needed, intermediate results not required
        Don't use when: You need to inspect/modify Phase 1 or 2 outputs
    """
    logger.info(f"Single-shot abduction in domain '{domain}'")

    # Validate observation
    if not observation or not observation.strip():
        return format_error_response(
            "Empty observation provided",
            code=ErrorCode.VALIDATION_ERROR,
            hint="Provide a non-empty observation describing the surprising fact",
        )

    # Validate num_hypotheses
    if num_hypotheses < 1 or num_hypotheses > 20:
        return format_error_response(
            f"num_hypotheses must be between 1 and 20, got {num_hypotheses}",
            code=ErrorCode.INVALID_VALUE,
            hint="Use a value between 1 and 20 for num_hypotheses",
        )

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
        "rationale": "why this is the best explanation",
        "confidence": 0.0-1.0,
        "next_steps": ["action 1", "action 2"]
    }}
}}
```
"""

    response = json.dumps(
        {
            "type": "prompt",
            "phase": "single_shot",
            "phase_name": "complete_abduction",
            "prompt": prompt,
            "usage": "Execute this prompt with an LLM for complete abductive analysis in one step.",
        },
        indent=2,
    )

    return _truncate_response(response)


# =============================================================================
# TOOL: CRITIC EVALUATION (Council of Critics)
# =============================================================================
@mcp.tool(
    annotations=ToolAnnotations(
        title="Critic Evaluation (Council)",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def peircean_critic_evaluate(
    critic: str,
    anomaly_json: str,
    hypotheses_json: str,
) -> str:
    """
    COUNCIL: Get evaluation from a specific critic perspective.

    The Council of Critics provides multi-perspective hypothesis evaluation.
    Use this to get a detailed evaluation from a single specialist viewpoint.

    Built-in critic roles:
    - empiricist: Evaluates based on evidence and observation
    - logician: Evaluates logical consistency and validity
    - pragmatist: Evaluates practical consequences and actionability
    - economist: Evaluates cost-effectiveness of testing
    - skeptic: Challenges assumptions and seeks falsification

    You can also specify ANY custom specialist role (e.g., "forensic_accountant",
    "security_engineer", "domain_expert").

    Args:
        critic: The critic role/perspective to adopt.
            Built-in: empiricist, logician, pragmatist, economist, skeptic
            Custom: Any specialist role (e.g., "forensic_accountant", "security_engineer")

        anomaly_json: The JSON output from peircean_observe_anomaly (Phase 1).

        hypotheses_json: The JSON output from peircean_generate_hypotheses (Phase 2).

    Returns:
        str: JSON containing a prompt to execute. The prompt output will be:

        Success response schema:
        {
            "perspective": "critic_role",
            "evaluation": "overall assessment from this perspective",
            "per_hypothesis": {
                "H1": {
                    "strengths": ["point 1"],
                    "weaknesses": ["point 1"],
                    "score": 0.0-1.0
                }
            },
            "strongest_hypothesis": "H1",
            "concerns": ["concern 1"]
        }

    Examples:
        Use when: You want a specific perspective on the hypotheses
        Use when: You need domain expertise not covered by standard council
        Don't use when: You want all perspectives at once (use use_council=True in Phase 3)
    """
    # Validate critic - fallback to general_critic if empty
    if not critic or not critic.strip():
        logger.warning("Empty critic provided, falling back to 'general_critic'")
        critic = "general_critic"

    logger.info(f"Council: Consulting the {critic}")

    # Parse inputs
    anomaly, error = _parse_anomaly_json(anomaly_json)
    if error:
        return error

    hypotheses, error = _parse_hypotheses_json(hypotheses_json)
    if error:
        return error

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

    response = json.dumps(
        {
            "type": "prompt",
            "phase": "critic_evaluation",
            "critic": critic,
            "prompt": prompt,
            "usage": f"Execute this prompt to get the {critic}'s perspective.",
        },
        indent=2,
    )

    return _truncate_response(response)


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
