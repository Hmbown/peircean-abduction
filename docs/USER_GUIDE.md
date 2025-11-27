# User Guide

Comprehensive guide to Peircean Abduction: the abductive reasoning harness for LLMs.

## Table of Contents

1. [Philosophy: Why Abduction?](#philosophy-why-abduction)
2. [The Three Phases](#the-three-phases)
3. [Using the Agent](#using-the-agent)
4. [Prompt-Only Mode](#prompt-only-mode)
5. [The Council of Critics](#the-council-of-critics)
6. [Domain Configuration](#domain-configuration)
7. [IBE Selection Criteria](#ibe-selection-criteria)
8. [Output Formats](#output-formats)
9. [Best Practices](#best-practices)

---

## Philosophy: Why Abduction?

Charles Sanders Peirce (1839-1914) identified three fundamental modes of logical inference:

| Mode | Direction | Question Answered | Example |
|------|-----------|-------------------|---------|
| **Deduction** | General → Specific | What follows from this? | "All humans are mortal; Socrates is human; therefore Socrates is mortal" |
| **Induction** | Specific → General | What pattern do we see? | "These 1000 ravens are black; probably all ravens are black" |
| **Abduction** | Effect → Cause | What explains this? | "The grass is wet; probably it rained" |

**Abduction is the only logical operation that introduces new ideas.** It's how we handle *surprise*—when reality doesn't match expectations.

### When Standard LLMs Fail

Standard LLMs optimize for probability—they retrieve the most likely "normal" answer. When faced with anomalous data, they:

1. **Hallucinate normalcy**: Force-fit conventional explanations
2. **Refuse uncertainty**: Produce vague, non-committal responses  
3. **Miss the signal**: Treat the anomaly as noise

Peircean Abduction forces models to:

1. **Recognize surprise**: Explicitly identify what's anomalous
2. **Generate alternatives**: Produce multiple competing hypotheses
3. **Evaluate systematically**: Score hypotheses on objective criteria
4. **Commit with calibration**: Select with appropriate confidence

---

## The Three Phases

### Phase 1: Observation Analysis

The first step is identifying and characterizing the surprising fact.

```
INPUT: "NVIDIA stock dropped 8% on record earnings"

ANALYSIS:
- Fact: 8% price drop concurrent with positive earnings
- Expected: Price increase on earnings beat
- Surprise Level: High (0.85)
- Source of Surprise: Violates strong positive correlation between earnings and price
```

The surprise score (0.0-1.0) quantifies how anomalous the observation is:
- 0.0-0.3: Expected (probably not worth abductive analysis)
- 0.3-0.6: Mildly surprising
- 0.6-0.8: Surprising (good candidate for abduction)
- 0.8-1.0: Highly anomalous (definitely needs explanation)

### Phase 2: Hypothesis Generation (Retroduction)

Generate multiple explanatory hypotheses, each with:
- **Statement**: Clear, falsifiable claim
- **Explanation**: How it makes the observation "a matter of course"
- **Prior Probability**: Likelihood before considering this observation
- **Assumptions**: What must be true for this hypothesis to hold
- **Testable Predictions**: Observable consequences if true/false

```
HYPOTHESES:

H1: Expectations were higher than reported beat
    Prior: 0.35
    Explanation: Whisper numbers exceeded the 15% beat
    Assumptions: Efficient market hypothesis, whisper numbers exist
    Test: Check options flow and analyst whisper numbers

H2: Forward guidance disappointed
    Prior: 0.30
    Explanation: Next quarter outlook was below consensus
    Test: Compare guidance to consensus estimates

H3: Unrelated institutional selling
    Prior: 0.20
    Explanation: Index rebalancing forced sales
    Test: Check index changes and fund flows
```

### Phase 3: Selection (Inference to the Best Explanation)

Evaluate each hypothesis on IBE criteria and select the best explanation:

```
EVALUATION:

              | Scope | Power | Parsimony | Testability | Composite
--------------|-------|-------|-----------|-------------|----------
H1: Whispers  | 0.85  | 0.80  | 0.75      | 0.70        | 0.78
H2: Guidance  | 0.90  | 0.85  | 0.80      | 0.85        | 0.85
H3: Rebalance | 0.60  | 0.65  | 0.90      | 0.80        | 0.74

SELECTED: H2 (Forward guidance disappointed)
Confidence: 0.85
```

---

## Using the Agent

### Basic Usage

```python
from peircean import AbductionAgent

# With synchronous LLM function
agent = AbductionAgent(
    llm_call=my_llm_function,
    domain="financial"
)

result = agent.abduce_sync("Stock dropped 5% on good news")
```

### Async Usage

```python
agent = AbductionAgent(
    llm_call_async=my_async_llm_function,
    domain="technical"
)

result = await agent.abduce("CPU dropped but latency increased")
```

### Configuration Options

```python
agent = AbductionAgent(
    llm_call=my_llm,
    domain="medical",           # Domain context
    max_hypotheses=7,           # Generate more hypotheses
    use_council=True,           # Enable Council of Critics
    selection_weights={         # Custom IBE weights
        "explanatory_scope": 0.20,
        "explanatory_power": 0.30,
        "parsimony": 0.15,
        "testability": 0.20,
        "consilience": 0.10,
        "fertility": 0.05,
    }
)
```

---

## Prompt-Only Mode

For use with any LLM without the agent wrapper:

```python
from peircean import abduction_prompt

# Generate complete prompt
prompt = abduction_prompt(
    observation="The anomaly to explain",
    domain="general",
    num_hypotheses=5
)

# Send to your LLM
response = my_llm(prompt)
```

### Step-by-Step Prompts

```python
from peircean import observation_prompt, hypothesis_prompt

# Step 1: Analyze observation
obs_prompt = observation_prompt("Your observation here")
obs_response = my_llm(obs_prompt)

# Step 2: Generate hypotheses
hyp_prompt = hypothesis_prompt(
    observation=parsed_observation,  # From step 1
    num_hypotheses=5
)
hyp_response = my_llm(hyp_prompt)

# Continue with evaluation and selection...
```

---

## The Council of Critics

The Council provides multi-perspective evaluation of hypotheses:

| Critic | Perspective | Key Questions |
|--------|-------------|---------------|
| **Empiricist** | Evidence | What data supports/refutes this? |
| **Logician** | Consistency | Is this internally coherent? |
| **Pragmatist** | Action | What should we DO if this is true? |
| **Economist** | Efficiency | Which is cheapest to test? |
| **Skeptic** | Falsification | What would DISPROVE this? |

### Enable Council

```python
agent = AbductionAgent(
    llm_call=my_llm,
    use_council=True
)

result = await agent.abduce(observation)
print(result.council_evaluation)
```

---

## Domain Configuration

### Available Domains

- `general` - Universal hypothesis templates
- `financial` - Market microstructure, information asymmetry, behavioral factors
- `legal` - Statutory gaps, precedent conflicts, jurisdictional issues
- `medical` - Differential diagnosis, drug interactions, rare conditions
- `technical` - Race conditions, resource exhaustion, cascade failures
- `scientific` - Measurement error, confounding, publication bias

### Custom Domain Guidance

```python
from peircean.core.prompts import DOMAIN_GUIDANCE, Domain

# View existing guidance
print(DOMAIN_GUIDANCE[Domain.FINANCIAL])

# Extend with custom domain (advanced)
DOMAIN_GUIDANCE["custom"] = """
Consider custom-specific hypothesis types:
- Type A considerations
- Type B considerations
"""
```

---

## IBE Selection Criteria

Inference to the Best Explanation uses these criteria (default weights shown):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Explanatory Scope** | 0.15 | How much of the observation does it explain? |
| **Explanatory Power** | 0.25 | How WELL does it explain? |
| **Parsimony** | 0.20 | How few assumptions required? (Occam's Razor) |
| **Testability** | 0.15 | How easily can we verify/falsify? |
| **Consilience** | 0.10 | How well does it fit other knowledge? |
| **Analogy** | 0.05 | How similar to known patterns? |
| **Fertility** | 0.10 | Does it generate new predictions? |

### Customize Weights

```python
# Emphasize testability for debugging scenarios
agent = AbductionAgent(
    llm_call=my_llm,
    selection_weights={
        "explanatory_scope": 0.10,
        "explanatory_power": 0.20,
        "parsimony": 0.15,
        "testability": 0.30,  # Higher weight
        "consilience": 0.10,
        "analogy": 0.05,
        "fertility": 0.10,
    }
)
```

---

## Output Formats

### AbductionResult Object

```python
result = agent.abduce_sync(observation)

# Key attributes
result.observation          # Observation object
result.hypotheses           # List of Hypothesis objects
result.selected_hypothesis  # ID of best hypothesis
result.selection_rationale  # Why it was selected
result.confidence           # 0.0-1.0
result.recommended_actions  # Suggested next steps
result.reasoning_trace      # Full trace of reasoning steps
result.council_evaluation   # Council results (if enabled)
```

### Markdown Output

```python
print(result.to_markdown())
```

### JSON Output

```python
import json
print(json.dumps(result.to_json_trace(), indent=2))
```

---

## Best Practices

### 1. Recognize When to Use Abduction

✅ **Good candidates**:
- Anomalous data (out of distribution)
- Root cause analysis
- Diagnostic reasoning
- Edge cases

❌ **Not suited for**:
- Standard Q&A
- Creative writing
- Fact retrieval

### 2. Provide Rich Context

```python
result = await agent.abduce(
    observation="Server latency spiked 200%",
    context={
        "time": "2024-01-15 14:30 UTC",
        "recent_changes": ["Deployed v2.3.1", "Updated config"],
        "affected_services": ["api-gateway", "auth-service"],
        "metrics_available": ["CPU", "memory", "connections"]
    }
)
```

### 3. Iterate on Surprising Results

If the selected hypothesis seems wrong:

1. Check assumptions in the selected hypothesis
2. Review hypotheses that scored close
3. Run with Council enabled for more perspectives
4. Adjust IBE weights for your domain

### 4. Test Before Acting

Always use the `recommended_actions` to validate before committing:

```python
for action in result.recommended_actions:
    print(f"TODO: {action}")
```

The abductive conclusion is a *hypothesis*, not a certainty.
