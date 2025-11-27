# Peircean Abduction: Evaluation Questions

This document contains 10 evaluation questions to assess the quality and correctness of the Peircean Abduction MCP server implementation. These questions cover tool functionality, error handling, schema compliance, and integration behavior.

## Question 1: Tool Discovery
**Category**: MCP Protocol

When connecting to the Peircean MCP server, the LLM should discover exactly 5 tools with the `peircean_` prefix:
1. `peircean_observe_anomaly` - Phase 1: Register surprising facts
2. `peircean_generate_hypotheses` - Phase 2: Generate explanatory hypotheses
3. `peircean_evaluate_via_ibe` - Phase 3: Evaluate via Inference to Best Explanation
4. `peircean_abduce_single_shot` - Complete abduction in one step
5. `peircean_critic_evaluate` - Get evaluation from a specific critic perspective

**Validation**: Call `tools/list` and verify all 5 tools are present with correct names and descriptions.

---

## Question 2: Phase Flow
**Category**: Abductive Reasoning

The 3-phase Peircean abductive flow should work correctly:
1. Phase 1 output should include `"next_tool": "peircean_generate_hypotheses"`
2. Phase 2 output should include `"next_tool": "peircean_evaluate_via_ibe"`
3. Phase 3 output should include `"next_tool": null`

**Validation**: Execute each phase and verify the `next_tool` field guides correctly to the next step.

---

## Question 3: Input Validation - Empty Observation
**Category**: Error Handling

When calling `peircean_observe_anomaly` with an empty observation:
- Should return `{"type": "error", "error": "...", "hint": "..."}`
- Error message should mention "Empty observation"
- Should NOT crash or return a malformed response

**Validation**: Call with `observation=""` and verify standardized error response.

---

## Question 4: Input Validation - num_hypotheses Bounds
**Category**: Error Handling

When calling `peircean_generate_hypotheses` with invalid `num_hypotheses`:
- Values < 1 should return an error
- Values > 20 should return an error
- Valid range is 1-20

**Validation**:
- Call with `num_hypotheses=0` -> error
- Call with `num_hypotheses=25` -> error
- Call with `num_hypotheses=5` -> success

---

## Question 5: JSON Schema Compliance
**Category**: Output Format

All tool outputs should be valid JSON with consistent structure:
- Success responses: `{"type": "prompt", "phase": N, "prompt": "...", "next_tool": "..."}`
- Error responses: `{"type": "error", "error": "...", "hint": "..."}`

**Validation**: Parse all tool outputs and verify they conform to the expected schema.

---

## Question 6: Domain-Specific Guidance
**Category**: Prompt Quality

The server should include domain-specific guidance in prompts:
- `domain="financial"` should include financial reasoning guidance
- `domain="legal"` should include legal analysis guidance
- `domain="technical"` should include technical debugging guidance
- Unknown domains should fall back to "general"

**Validation**: Call `peircean_observe_anomaly` with each domain and verify appropriate guidance appears in the prompt.

---

## Question 7: Council of Critics
**Category**: IBE Evaluation

The `peircean_evaluate_via_ibe` tool should support multiple council modes:
1. `use_council=False` -> Standard IBE criteria (explanatory_power, parsimony, etc.)
2. `use_council=True` -> Default 5 critics (Empiricist, Logician, Pragmatist, Economist, Skeptic)
3. `custom_council=["Role1", "Role2"]` -> Custom specialist roles

**Validation**: Call with each mode and verify the prompt includes the appropriate evaluation framework.

---

## Question 8: Tool Annotations
**Category**: MCP Best Practices

All tools should have proper annotations:
- `readOnlyHint: true` - Tools don't modify state
- `idempotentHint: true` - Same inputs produce same outputs

**Validation**: Check tool metadata for correct annotations.

---

## Question 9: Invalid JSON Handling
**Category**: Error Handling

When passing invalid JSON to Phase 2 or Phase 3 tools:
- `peircean_generate_hypotheses(anomaly_json="not json")` -> error with hint
- `peircean_evaluate_via_ibe(anomaly_json="{}", hypotheses_json="not json")` -> error with hint
- `peircean_critic_evaluate(critic="skeptic", anomaly_json="bad", hypotheses_json="{}")` -> error with hint

**Validation**: Call each tool with malformed JSON and verify helpful error responses.

---

## Question 10: Critic Fallback
**Category**: Robustness

The `peircean_critic_evaluate` tool should handle empty critic gracefully:
- Empty critic (`critic=""`) should fall back to "general_critic"
- Whitespace-only critic should also fall back
- Should NOT return an error for empty critic

**Validation**: Call with `critic=""` and verify the output uses "GENERAL_CRITIC" in the prompt.

---

## Automated Testing

For automated validation of these questions, see `tests/test_evaluation.py` which contains executable tests for all questions that don't require LLM execution.
