# 🕵️ Peircean Abduction
### A Production-Ready MCP Server for Structured Abductive Reasoning

> *"Abduction is the process of forming an explanatory hypothesis. It is the only logical operation which introduces any new idea."*  
> — Charles Sanders Peirce

**Peircean Abduction** is a Model Context Protocol (MCP) server that transforms your LLM from a pattern-matching autocomplete into a rigorous, hypothesis-driven reasoning engine. It enforces a strict 3-phase scientific method: **Observe → Hypothesize → Evaluate**.

[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](https://github.com/Hmbown/peircean-abduction/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Hmbown/peircean-abduction/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compliant](https://img.shields.io/badge/MCP-v1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![Tests](https://img.shields.io/badge/tests-156%20passing-brightgreen.svg)](https://github.com/Hmbown/peircean-abduction/actions)

**🎬 See it in action**: [Satellite Mystery Walkthrough](#-the-satellite-mystery-a-walkthrough)

---

## 📊 The Problem: LLMs Guess Instead of Reasoning

### Traditional Approach
> *"Hmm, that's strange. It could be X, Y, or Z. I think it's probably X because..."*

**Problems:**
- ❌ No structured process
- ❌ No competing hypotheses  
- ❌ No testable predictions
- ❌ No uncertainty quantification
- ❌ No clear action items

### Peircean Abduction Approach
```json
{
  "observation_analysis": {
    "fact": "Satellite maneuvered before collision",
    "surprise_level": "anomalous",
    "surprise_score": 0.95,
    "expected_baseline": "Debris cannot maneuver"
  },
  "hypotheses": [
    {"id": "H1", "statement": "Weapon system", "prior_probability": 0.10},
    {"id": "H2", "statement": "Software glitch", "prior_probability": 0.40},
    {"id": "H3", "statement": "Third-party hack", "prior_probability": 0.05}
  ],
  "verdict": {
    "best_hypothesis": "H1",
    "confidence": 0.78,
    "verdict": "investigate",
    "next_steps": [
      "Check RF logs for command signals",
      "Analyze thruster precision data"
    ]
  }
}
```

**Benefits:**
- ✅ Explicit hypothesis generation
- ✅ Prior probability assignments
- ✅ Testable predictions
- ✅ Multi-perspective evaluation
- ✅ Clear, actionable recommendations

---

## 🚀 Quick Start

```bash
# Install
pip install peircean-abduction

# Auto-configure for Claude Desktop
peircean --install

# Use in Claude Desktop
# "Analyze with peircean: My API latency spiked 10x but CPU is normal"
```

That's it. The tools automatically activate during your conversation.

---

## 🎯 How It Works

### The 3-Phase Scientific Method

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Phase 1       │      │   Phase 2       │      │   Phase 3       │
│   OBSERVE       │─────▶│   HYPOTHESIZE   │─────▶│   EVALUATE      │
│                 │      │                 │      │                 │
│ • What violates │      │ • Generate      │      │ • Council of    │
│   expectations? │      │   explanations  │      │   Critics       │
│ • How surprised?│      │ • Assign priors │      │ • Score & rank  │
│                 │      │ • Make testable │      │ • Recommend     │
│                 │      │   predictions   │      │   actions       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
    Anomaly JSON          Hypotheses JSON         Evaluation JSON
```

### Walkthrough: The Satellite Mystery

**Input:**
```
"Defunct 'debris' satellite executed controlled burn 10s before collision.
Country A claimed uncontrollable debris. Flight logs show thrusters fired."
```

**Process:**

1. **Phase 1:** Analyzes the surprise level (0.95 = extremely anomalous)
2. **Phase 2:** Generates 3 competing hypotheses with prior probabilities
3. **Phase 3:** Council of Critics evaluates and selects best explanation

**Output:**
- **Best Hypothesis**: H1 (ASAT weapon)
- **Confidence**: 78%
- **Verdict**: Investigate
- **Actions**: Check RF logs, analyze thruster data

---

## 🛠️ Available Tools

### Core Tools (5)

| Tool | Phase | Purpose | Output |
|------|-------|---------|--------|
| `peircean_observe_anomaly` | 1 | Register surprising facts | Anomaly JSON |
| `peircean_generate_hypotheses` | 2 | Generate explanations | Hypotheses JSON |
| `peircean_evaluate_via_ibe` | 3 | Select best explanation | Evaluation JSON |
| `peircean_abduce_single_shot` | All | Complete analysis | Full analysis |
| `peircean_critic_evaluate` | Aux | Domain-specific review | Critic evaluation |

### Domain-Specific Guidance

Use the `domain` parameter for tailored hypothesis generation:

| Domain | Use Cases |
|--------|-----------|
| **technical** | API latency, system bugs, performance issues |
| **financial** | Market movements, trading anomalies, earnings |
| **legal** | Liability, statutory interpretation, compliance |
| **medical** | Differential diagnosis, symptom analysis |
| **scientific** | Experimental anomalies, measurement errors |
| **general** | Default for any domain |

---

## 📊 Real-World Use Cases

### 1. Technical Debugging

**Anomaly:** *"API latency spiked 10x, but CPU and memory are normal"*

```
H1: Network bandwidth throttling
H2: Third-party API timeout cascade  
H3: Database connection pool exhaustion

Verdict: H1 best explains pattern
Action: Check load balancer logs, network metrics
```

### 2. Financial Analysis

**Anomaly:** *"Stock dropped 5% on good earnings news"*

```
H1: Market expected even better results
H2: Forward guidance disappointed
H3: Algorithmic stop-loss cascade

Verdict: H2 most likely
Action: Check management Q&A transcript
```

### 3. Security Incident

**Anomaly:** *"Server CPU at 100% but no logged users"*

```
H1: Cryptojacking malware
H2: Runaway background process
H3: Resource exhaustion attack

Verdict: H1 explains stealth + usage
Action: Check process tree, network connections
```

---

## 🧪 Performance & Reliability

- ✅ **156/156** tests passing
- ✅ **100%** MCP protocol compliance  
- ✅ **5** specialized domains
- ✅ **4** LLM providers supported
- ✅ **Zero** runtime dependencies beyond MCP spec

### Test Coverage

```bash
# Run full test suite
make test

# Run MCP-specific tests
pytest tests/test_mcp.py -v

# Validate MCP compliance
make verify
```

---

## 📖 Examples

### Example 1: Quick Single-Shot

```python
from peircean.mcp.server import peircean_abduce_single_shot

result = peircean_abduce_single_shot(
    observation="Customer churn rate doubled in Q3",
    context="No price changes, NPS stable, no competitor launches",
    domain="financial",
    num_hypotheses=3
)

# Returns complete analysis prompt
```

See [examples/quickstart.py](examples/quickstart.py)

### Example 2: International Law - Full 3-Phase

See [examples/international_law.py](examples/international_law.py) for a complete walkthrough of the satellite collision scenario.

---

## 🔧 Advanced Features

### Council of Critics

Enable multi-perspective evaluation:

```python
peircean_evaluate_via_ibe(
    anomaly_json="...",
    hypotheses_json="...",
    use_council=True,
    custom_council=["Forensic Accountant", "Security Engineer"]
)
```

**Default Critics:**
- Empiricist (evidence-based)
- Logician (consistency checks)
- Pragmatist (action-oriented)
- Economist (cost-benefit)
- Skeptic (challenges assumptions)

### Custom Weights

Adjust scoring criteria weights for domain-specific needs.

---

## 📚 Documentation

- [Installation Guide](docs/getting-started/installation.md)
- [Configuration Guide](docs/guides/configuration.md)
- [Architecture Specification](docs/PEIRCEAN_SPEC.md)
- [API Reference](docs/api/reference.md)

---

## 🤝 Contributing

We value rigor, logic, and testability. See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Architectural standards  
- Pull request process
- Testing requirements

```bash
# Quick start
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction
make dev      # Install dependencies
make check    # Run all checks
```

---

## 🔒 Model Context Protocol Compliance

Fully compliant with MCP v1.0.0:

- ✅ Tool discovery & registration
- ✅ JSON-RPC transport
- ✅ Stdio communication
- ✅ Resource management
- ✅ Logging to stderr
- ✅ Read-only tool annotations

---

## 👥 Community

- **GitHub Issues**: Bug reports & feature requests
- **Discussions**: Questions & ideas
- **Pull Requests**: Contributions welcome

---

## 📄 License

MIT License. Use it to solve crimes, debug code, or understand the universe.

---

## 📞 Support

- **Documentation**: [Full docs](https://github.com/Hmbown/peircean-abduction/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/Hmbown/peircean-abduction/issues)
- **Email**: hunter@shannonlabs.dev

---

<div align="center">

**Version**: 1.2.3  
**Status**: 🟢 Production Ready  
**MCP Compliant**: ✅ Yes  
**Last Updated**: December 2025

</div>