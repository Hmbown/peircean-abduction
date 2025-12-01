# Peircean Abduction
### A Logic Harness for Abductive Inference

> "Abduction is the process of forming an explanatory hypothesis. It is the only logical operation which introduces any new idea."
> — Charles Sanders Peirce

**Peircean Abduction** is a Model Context Protocol (MCP) server that implements a rigorous framework for abductive reasoning in Large Language Models.

While standard LLM inference relies heavily on pattern matching (induction) and rule application (deduction), this system enforces a structured logic loop designed specifically for **abduction**: the inference to the best explanation for anomalous observations. The architecture compels the model to adhere to a strict three-phase process: **Observation → Hypothesize → Evaluate**.

[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/Hmbown/peircean-abduction/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Hmbown/peircean-abduction/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-v1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-156%20passing-brightgreen.svg)](https://github.com/Hmbown/peircean-abduction/actions)

---

## Case Study: Orbital Anomaly Analysis

**Input Data**
> **Observation:** A satellite designated as "defunct" and classified as space debris by Country A executed a controlled burn 10 seconds prior to a collision trajectory with a space station.
> **Context:** Country A claims accidental collision. Recovered flight logs indicate intentional thruster activation.

**System Output**

### Phase 1: Observation
**Anomaly Detection:** "Debris follows Keplerian orbits; controlled propulsion contradicts debris classification."
**Surprise Score:** 0.99 (Critical Anomaly)

### Phase 2: Hypothesis Generation
The system generates probabilistic explanations based on available evidence:

*   **H1 (Kinetic Weaponry):** The satellite was a dormant Kinetic Anti-Satellite (ASAT) weapon, activated for a targeted strike.
*   **H2 (Automated Failure):** An "end-of-life" deorbit script triggered erroneously, resulting in a coincidental collision course.
*   **H3 (Signal Intrusion):** A third-party actor compromised the command link to engineer a false flag event.

### Phase 3: Inference to Best Explanation (IBE)
A dialectical evaluation via the **Council of Critics** (Logician, Empiricist, Scientist) assesses the hypotheses.

> **Verdict:** **H1 (Kinetic Weaponry)**
> **Reasoning:** The precise timing and vector of the burn render H2 statistically negligible. H3 requires unproven assumptions regarding signal compromise. H1 offers the most parsimonious explanation consistent with all observed data points (burn timing, trajectory, flight logs).

---

## Quick Start

```bash
# Install
pip install peircean-abduction

# Initialize (Claude Desktop / Cursor)
peircean --install
```

---

## Methodology

The system operates on a strict three-phase logical loop.

### Phase 1: Observation
Registers the anomalous fact and quantifies the deviation from expected baselines.

```python
from peircean.mcp.server import peircean_observe_anomaly

result = peircean_observe_anomaly(
    observation="API latency spiked 10x; CPU/Memory utilization nominal.",
    context="No active deployments; steady state traffic.",
    domain="technical"
)
```

### Phase 2: Hypothesis Generation
Generates competing explanations with associated prior probabilities and falsifiable predictions.

```python
from peircean.mcp.server import peircean_generate_hypotheses

result = peircean_generate_hypotheses(
    anomaly_json='{"anomaly": {...}}',
    num_hypotheses=3
)
```

### Phase 3: Evaluation
Selects the best explanation using multi-perspective critique.

```python
from peircean.mcp.server import peircean_evaluate_via_ibe

result = peircean_evaluate_via_ibe(
    anomaly_json='{"anomaly": {...}}',
    hypotheses_json='{"hypotheses": [...]}',
    use_council=True
)
```

### Single-Shot Execution
Executes the full abductive loop in a single call.

```python
from peircean.mcp.server import peircean_abduce_single_shot

result = peircean_abduce_single_shot(
    observation="Q3 Churn rate doubled.",
    context="Pricing invariant; NPS stable; market competition constant.",
    domain="financial",
    num_hypotheses=3
)
```

---

## Applications

### Technical Systems
**Anomaly:** Server CPU 100% utilization; 0 active user sessions.
*   **H1:** Cryptojacking malware [P: 0.15]
*   **H2:** Zombie background process [P: 0.60]
*   **H3:** Denial of Service attack [P: 0.10]
**Verdict:** H2. Action: Audit process tree.

### Financial Markets
**Anomaly:** Equity value -5% following positive earnings report.
*   **H1:** Market priced in higher expectations.
*   **H2:** Negative forward guidance.
*   **H3:** Algorithmic liquidation.
**Verdict:** H2. Action: Analyze earnings call transcript.

### Security Operations
**Anomaly:** 500 Error rate spike at 03:00 UTC; no deployment activity.
*   **H1:** Database connection pool exhaustion.
*   **H2:** Upstream API rate limiting.
*   **H3:** SSL Certificate expiration.
**Verdict:** H1. Action: Review connection pool metrics.

---

## Tool Reference

| Tool | Phase | Function | Output |
|------|-------|----------|--------|
| `peircean_observe_anomaly` | 1 | Anomaly Registration | Anomaly JSON |
| `peircean_generate_hypotheses` | 2 | Explanation Generation | Hypotheses JSON |
| `peircean_evaluate_via_ibe` | 3 | Explanation Selection | Evaluation JSON |
| `peircean_abduce_single_shot` | All | Full Cycle Analysis | Analysis Object |
| `peircean_critic_evaluate` | Aux | Domain Review | Critic JSON |

**Supported Domains:** `technical`, `financial`, `legal`, `medical`, `scientific`, `general`

---

## Features

*   **MCP Architecture:** Native integration with Model Context Protocol.
*   **Dialectical Evaluation:** Hypothesis critique via simulated expert perspectives (Council of Critics).
*   **Provider Agnostic:** Compatible with Anthropic, OpenAI, Gemini, and Ollama runtimes.
*   **Falsifiability:** Enforced generation of testable predictions for all hypotheses.

---

## Supported Runtimes

*   **Anthropic** (Claude)
*   **OpenAI** (GPT)
*   **Google DeepMind** (Gemini)
*   **Ollama** (Local Inference)

---

## Reliability

*   **Test Coverage:** 156/156 passing.
*   **Compliance:** MCP v1.0.0.
*   **Dependencies:** Minimal runtime footprint.

```bash
# Execute Test Suite
make test

# Verify Compliance
make verify
```

---

## Documentation

- **Quick Start:** [examples/quickstart.py](examples/quickstart.py)
- **Full Walkthrough:** [examples/international_law.py](examples/international_law.py)
- **Installation:** [docs/getting-started/installation.md](docs/getting-started/installation.md)
- **API Reference:** [docs/api/reference.md](docs/api/reference.md)

---

## Contributing

Refer to [CONTRIBUTING.md](CONTRIBUTING.md) for development standards.

```bash
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction
make dev
make check
```

---

## License

MIT License.

---

<div align="center">

**Version**: 1.2.3 | **Status**: Production Ready | **MCP Compliant**: v1.0.0

</div>