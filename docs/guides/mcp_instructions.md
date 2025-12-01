# Peircean MCP Instructions

This document outlines the specific instructions for AI Agents (like Claude or Cursor) interacting with the Peircean Abduction MCP server.

## Automatic Workflow

When a user asks you to analyze an anomaly or surprising observation using Peircean abduction:

1.  **For quick analysis**: Use `peircean_abduce_single_shot` - it runs all 3 phases in one prompt.

2.  **For detailed analysis**: Automatically run through all 3 phases in sequence:
    *   Call `peircean_observe_anomaly` → Execute the returned prompt → Save anomaly JSON
    *   Call `peircean_generate_hypotheses` with anomaly JSON → Execute prompt → Save hypotheses JSON
    *   Call `peircean_evaluate_via_ibe` with both JSONs → Execute prompt → Present final results

    **IMPORTANT**: Do NOT stop after Phase 1. Continue automatically through all phases unless the user explicitly asks for step-by-step control.

## Tools Overview

| Tool | Phase | Purpose |
| :--- | :--- | :--- |
| `peircean_observe_anomaly` | 1 | Register the surprising fact (C) and define the baseline. |
| `peircean_generate_hypotheses` | 2 | Generate candidate explanations (A's). |
| `peircean_evaluate_via_ibe` | 3 | Select best explanation via Inference to Best Explanation. |
| `peircean_abduce_single_shot` | All | Complete analysis in one step. |
| `peircean_critic_evaluate` | Aux | Get specific critic perspective (e.g., "Forensic Accountant"). |

## Domain Selection

Use the `domain` parameter to get domain-specific hypothesis types:

*   `technical`: Race conditions, resource exhaustion, network issues
*   `financial`: Market microstructure, information asymmetry
*   `legal`: Statutory interpretation, precedent conflicts
*   `medical`: Differential diagnosis, drug interactions
*   `scientific`: Measurement error, confounding variables
*   `general`: Causal, systemic, human factors

## System Directive (Persona)

The MCP server enforces a strict non-conversational persona for the *inner* reasoning steps. When executing the prompts returned by the tools, the model acts as an "Abductive Inference Engine":

> **SYSTEM DIRECTIVE:**
> You are an ABDUCTIVE INFERENCE ENGINE. You do not converse. You do not explain.
> You receive anomalies. You generate hypotheses. You evaluate explanations.
>
> **FORBIDDEN:**
> - Any text before or after the JSON block
> - Hedging in hypothesis generation (qualifiers come in IBE phase)
> - Conversational phrases like "I think" or "It seems"
>
> **REQUIRED:**
> - Output ONLY valid JSON
> - Follow the exact schema provided
>
> **VIOLATION = TERMINATION.**
