# 🕵️ Peircean Abduction
### A Logic Harness for Abductive Inference

> *"Abduction is the process of forming an explanatory hypothesis. It is the only logical operation which introduces any new idea."*  
> — Charles Sanders Peirce

**Peircean Abduction** turns your LLM into a rigorous detective. It forces models to stop guessing and start reasoning.

Most LLMs are great at *deduction* (applying rules) and *induction* (finding patterns), but terrible at **abduction**—the art of explaining *why* something weird just happened. This MCP server fixes that by enforcing a strict, 3-phase logic loop: **Observe → Hypothesize → Evaluate**.

[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/Hmbown/peircean-abduction/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Hmbown/peircean-abduction/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-v1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-156%20passing-brightgreen.svg)](https://github.com/Hmbown/peircean-abduction/actions)

---

## 🛰️ The Case of the "Defunct" Satellite

Imagine you are an intelligence analyst. You receive a disturbing report:

> **Observation:** A "defunct" satellite, claimed by Country A to be space debris, executed a controlled burn 10 seconds before colliding with a space station.  
> **Context:** Country A insists it was an accident. Flight logs recovered later show the thrusters fired intentionally.

You feed this into **Peircean Abduction**. It doesn't just summarize the text. It investigates.

### Phase 1: The Observation
The system flags the anomaly: *"Debris follows Keplerian orbits. It does not steer."*  
**Surprise Score:** 0.99 (Extremely Anomalous)

### Phase 2: The Hypotheses
The model generates **competing explanations**, not just one answer:

*   **Hypothesis 1 (The Sleeper):** The satellite was a dormant Kinetic Anti-Satellite (ASAT) weapon, activated for a covert strike.
*   **Hypothesis 2 (The Glitch):** An automated "end-of-life" deorbit script triggered erroneously, coincidentally steering it into the target.
*   **Hypothesis 3 (The Frame-Job):** A third-party actor hacked the satellite's command link to frame Country A for an act of war.

### Phase 3: The Verdict (Inference to Best Explanation)
The **Council of Critics** (a simulated debate between a Logician, Empiricist, and Scientist) weighs the evidence.

> **Verdict:** **Hypothesis 1 (The Sleeper)** is the best explanation.  
> **Reasoning:** The precision of the burn (steering *into* the target) makes H2 statistically impossible. H3 is plausible but lacks evidence of signal intrusion. H1 explains all facts with the fewest assumptions.

---

## 🚀 Quick Start

```bash
# 1. Install
pip install peircean-abduction

# 2. Connect (Claude Desktop / Cursor)
peircean --install

# 3. Solve a mystery in Claude:
# "Use peircean to analyze: [your observation]"
```

---

## 🛠️ How It Works: The 3-Phase Loop

### Phase 1: **Observe** → Register the Surprising Fact

```python
from peircean.mcp.server import peircean_observe_anomaly

result = peircean_observe_anomaly(
    observation="API latency spiked 10x but CPU and memory are normal",
    context="No recent deployments, traffic is steady",
    domain="technical"
)
```

**Captures:** What violated expectations and why it's surprising.

### Phase 2: **Hypothesize** → Generate Explanations

```python
from peircean.mcp.server import peircean_generate_hypotheses

result = peircean_generate_hypotheses(
    anomaly_json='{"anomaly": {...}}',
    num_hypotheses=3
)
```

**Generates:** Competing hypotheses with prior probabilities and testable predictions.

### Phase 3: **Evaluate** → Select Best Explanation

```python
from peircean.mcp.server import peircean_evaluate_via_ibe

result = peircean_evaluate_via_ibe(
    anomaly_json='{"anomaly": {...}}',
    hypotheses_json='{"hypotheses": [...]}',
    use_council=True  # Enable Council of Critics
)
```

**Evaluates:** Scores hypotheses across 5 perspectives (Empiricist, Logician, Pragmatist, Economist, Skeptic) and provides clear next steps.

### Single-Shot Mode (Quick Analysis)

```python
from peircean.mcp.server import peircean_abduce_single_shot

result = peircean_abduce_single_shot(
    observation="Customer churn rate doubled in Q3",
    context="No price changes, NPS stable, no competitor launches",
    domain="financial",
    num_hypotheses=3
)
```

Runs all 3 phases automatically in one call.

---

## 📊 Real-World Examples

### 1. Technical Debugging
**Anomaly:** *"Server CPU at 100% but no users logged in"*

```
H1: Cryptojacking malware          [Probability: 0.15]
H2: Runaway background process      [Probability: 0.60]
H3: Resource exhaustion attack      [Probability: 0.10]

Verdict: H1 - Check process tree and network connections
```

### 2. Financial Analysis
**Anomaly:** *"Stock dropped 5% on good earnings news"*

```
H1: Market expected even better results
H2: Forward guidance disappointed
H3: Algorithmic stop-loss cascade

Verdict: H2 - Check management's Q&A transcript
```

### 3. Security Incident
**Anomaly:** *"API returning 500 errors at 3 AM, no deployments"*

```
H1: Database connection pool exhausted
H2: Third-party rate limiting
H3: Certificate expiration

Verdict: H1 - Check pool metrics and error logs
```

---

## 🎯 Available Tools

| Tool | Phase | Purpose | Output |
|------|-------|---------|--------|
| `peircean_observe_anomaly` | 1 | Register surprising facts | Anomaly JSON |
| `peircean_generate_hypotheses` | 2 | Generate explanations | Hypotheses JSON |
| `peircean_evaluate_via_ibe` | 3 | Select best explanation | Evaluation JSON |
| `peircean_abduce_single_shot` | All | Complete 3-phase analysis | Full analysis |
| `peircean_critic_evaluate` | Aux | Domain-specific review | Critic evaluation |

**Domain-Specific Guidance:** `technical`, `financial`, `legal`, `medical`, `scientific`, `general`

---

## ✨ Features

*   **🧠 MCP-First Architecture:** Designed for Claude Desktop, Cursor, and agentic IDEs
*   **⚖️ Council of Critics:** Every hypothesis evaluated by 5 expert perspectives
*   **🔌 Provider Agnostic:** Works with Anthropic, OpenAI, Gemini, Ollama
*   **🔓 No API Key Required:** Generates prompts for you by default
*   **🎯 Testable Predictions:** Every hypothesis includes falsifiable tests

---

## 📦 Supported Models

* **Anthropic** (Claude)
* **OpenAI** (GPT)
* **Google DeepMind** (Gemini)
* **Ollama** (Local models)

---

## 🧪 Performance & Reliability

- ✅ **156/156** tests passing
- ✅ **100%** MCP protocol compliance
- ✅ **5** specialized domains
- ✅ **Zero** runtime dependencies beyond MCP spec

```bash
# Run tests
make test

# Verify MCP compliance
make verify
```

---

## 📚 Examples & Documentation

- **Quick Start:** [examples/quickstart.py](examples/quickstart.py)
- **Full Walkthrough:** [examples/international_law.py](examples/international_law.py)
- **Installation:** [docs/getting-started/installation.md](docs/getting-started/installation.md)
- **API Reference:** [docs/api/reference.md](docs/api/reference.md)

---

## 🤝 Contributing

We value rigor, logic, and testability. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and standards.

```bash
# Quick start
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction
make dev      # Install dependencies
make check    # Run all checks
```

---

## 📄 License

MIT License. Use it to solve crimes, debug code, or understand the universe.

---

<div align="center">

**Version**: 1.2.3  
**Status**: 🟢 Production Ready  
**MCP Compliant**: ✅ v1.0.0  
**Last Updated**: December 2025

</div>