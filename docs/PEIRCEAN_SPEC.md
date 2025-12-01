# Peircean Abduction Specification

## 1. Theoretical Background

This system implements **Abductive Inference**, a form of logical reasoning formulated by Charles Sanders Peirce. Unlike deduction (guaranteed conclusion) or induction (statistical probability), abduction is the process of forming explanatory hypotheses.

### The Logical Form
Peirce defined abduction with this syllogism:

> 1.  The surprising fact, **C**, is observed.
> 2.  But if **A** were true, **C** would be a matter of course.
> 3.  Hence, there is reason to suspect that **A** is true.

### The Goal
The goal of this system is not to just "guess" the answer, but to:
1.  **Formalize Surprise**: Quantify exactly why an observation deviates from the expected baseline.
2.  **Separate Explanations**: Distinctly articulate separate causal chains ($A_1, A_2, A_3$) rather than conflating them.
3.  **Maximize Testability**: Ensure every hypothesis produces falsifiable predictions.

---

## 2. The 3-Phase Loop

The system operates in a strict three-phase loop to enforce this logic.

### Phase 1: Observation (Formalizing C)
**Tool:** `peircean_observe_anomaly`

The agent takes a raw observation and converts it into a structured "Anomaly" object. This forces the agent to define the *expected baseline* that was violated, which is crucial for identifying the specific "surprise."

### Phase 2: Hypothesis Generation (Generating A's)
**Tool:** `peircean_generate_hypotheses`

The agent takes the structured Anomaly and generates a set of mutually exclusive (or at least distinct) hypotheses. Each hypothesis MUST explain the anomaly if it were true.

### Phase 3: Evaluation (Inference to Best Explanation)
**Tool:** `peircean_evaluate_via_ibe`

The agent evaluates the hypotheses using **Inference to the Best Explanation (IBE)** criteria:
*   **Explanatory Power**: How well does it cover all the facts?
*   **Parsimony**: How simple is the explanation? (Occam's Razor)
*   **Prior Probability**: How likely is it given background knowledge?
*   **Testability**: Can it be easily proven/disproven?

Optionally, a **Council of Critics** (simulated personas) can debate the hypotheses before a verdict is reached.

---

## 3. JSON Data Schemas

The system relies on strict JSON structures to pass data between phases.

### 3.1. Anomaly Schema (Phase 1 Output)

```json
{
  "anomaly": {
    "fact": "string - The concise observation",
    "surprise_level": "string - low|medium|high",
    "surprise_score": "float - 0.0 to 1.0",
    "expected_baseline": "string - What should have happened",
    "domain": "string - technical|medical|financial|etc",
    "context": ["string - relevant background facts"],
    "key_features": ["string - specific data points"],
    "surprise_source": "string - why this is weird"
  }
}
```

### 3.2. Hypothesis Schema (Phase 2 Output)

```json
{
  "hypotheses": [
    {
      "id": "string - H1, H2, etc.",
      "statement": "string - The core hypothesis",
      "explains_anomaly": "string - The causal link (If H is true, C follows)",
      "prior_probability": "float - 0.0 to 1.0",
      "assumptions": [
        {
          "statement": "string",
          "testable": "boolean"
        }
      ],
      "testable_predictions": [
        {
          "prediction": "string - What else must be true?",
          "test_method": "string - How to check it",
          "if_true": "string - Impact on H if confirmed",
          "if_false": "string - Impact on H if refuted"
        }
      ]
    }
  ]
}
```

### 3.3. Evaluation/Verdict Schema (Phase 3 Output)

```json
{
  "evaluation": {
    "rankings": [
      {
        "rank": "integer - 1 is best",
        "hypothesis_id": "string",
        "score": "float - 0.0 to 1.0",
        "rationale": "string"
      }
    ],
    "best_explanation": "string - ID of the winner",
    "recommended_action": "string - Next step (e.g., Run test for H1)",
    "confidence": "float - 0.0 to 1.0"
  }
}
```
