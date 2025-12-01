# Peircean Abduction

[![CI](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml/badge.svg)](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/peircean-abduction.svg)](https://pypi.org/project/peircean-abduction/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A Logic Harness for Abductive Inference.**

Peircean Abduction forces LLMs to stop guessing and start investigating. It implements Charles Sanders Peirce's logical framework to make uncertainty visible and hypotheses testable.

> **Anomaly in → Hypothesis out.**

```
"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."
— Charles Sanders Peirce, Collected Papers 5.189
```

---

## 🔍 What is this?

Most LLMs act like a **Jury**: they weigh the evidence they have and give you a verdict (probability-based). They tend to "lump" distinct possibilities into a single, safe conclusion.

**Peircean Abduction** acts like a **Detective**: it doesn't just decide; it *investigates*. It splits anomalies into distinct, testable hypotheses and tells you *how* to find the truth.

### Key Features

*   **Explicit Uncertainty**: Forces the model to quantify "surprise" (0.0 - 1.0).
*   **Structured Hypotheses**: Every explanation comes with specific, testable predictions.
*   **Inference to Best Explanation (IBE)**: A rigorous selection process based on Explanatory Power, Parsimony, and Testability.
*   **Council of Critics**: Automatically simulates 5 specialist perspectives (Empiricist, Logician, Pragmatist, Economist, Skeptic) to stress-test ideas.
*   **MCP Ready**: Built as a Model Context Protocol (MCP) server, ready to plug into Claude Desktop, Cursor, or any MCP client.

---

## 🚀 Quick Start

### 1. Install
```bash
pip install peircean-abduction
```

### 2. Run an Example
We provide runnable Python scripts to demonstrate the logic harness.

**Simple Demo (Single-Shot):**
```bash
# Clone the repo first if you haven't
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction

# Run the quickstart
python examples/quickstart.py
```

### 3. Verify Installation
Ensure the MCP server is correctly configured by running the validation script:
```bash
python scripts/validate_mcp.py
```

**Full Scenario (International Law):**
```bash
python examples/international_law.py
```

---

## 🔌 MCP Server Setup

Connect Peircean Abduction to your AI assistant (Claude, Cursor, etc.) to give it abductive reasoning superpowers.

### Claude Desktop

**Automatic (recommended):**
```bash
# macOS
peircean-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Windows
peircean-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"
```

**Manual Configuration:**
```json
{
  "mcpServers": {
    "peircean": {
      "command": "python",
      "args": ["-m", "peircean.mcp.server"]
    }
  }
}
```

### Cursor / VS Code
1.  Run `peircean-setup-mcp` to generate the config JSON.
2.  Paste it into your editor's MCP settings.

---

## 🧠 How It Works (The 3-Phase Loop)

The harness enforces a strict 3-step logical flow:

### Phase 1: Observe (`peircean_observe_anomaly`)
*   **Input**: A raw observation (e.g., "Server latency spiked 10x but CPU is normal").
*   **Output**: A structured "Anomaly" object defining *why* this is surprising and what baseline was violated.

### Phase 2: Hypothesize (`peircean_generate_hypotheses`)
*   **Input**: The Anomaly from Phase 1.
*   **Output**: A list of distinct, falsifiable hypotheses (A's). Each must explain the anomaly if true.

### Phase 3: Evaluate (`peircean_evaluate_via_ibe`)
*   **Input**: The Hypotheses from Phase 2.
*   **Output**: A final Verdict selected via **Inference to Best Explanation (IBE)**. This phase can optionally convene a "Council of Critics" to debate the options.

---

## ⚡ Case Study: The "Lumping" Problem

**Scenario**: A "defunct" military satellite collides with a commercial station. Flight logs show a controlled burn 10s before impact.

*   **Standard LLM**: "It was likely a malfunction or a hidden military test." (Lumps distinct ideas together, vague).
*   **Peircean Harness**:
    1.  **H1 (Attack)**: "Sleeper weapon activated." -> **Prediction**: Check for uplink signals at T-10s.
    2.  **H2 (Glitch)**: "Deorbit script misfire." -> **Prediction**: Check code for specific trigger conditions.
    *   **Verdict**: Investigate H1 first because it explains the *vector* (steering into target), whereas H2 only explains the *burn*.

---

## Documentation

- [**Peircean Specification**](docs/PEIRCEAN_SPEC.md) - Detailed breakdown of the 3-Phase Loop and JSON Schemas.
- [**MCP Agent Instructions**](docs/guides/mcp_instructions.md) - Guide for AI Agents using the tools.
- [Quick Start Guide](docs/getting-started/quickstart.md)
- [User Guide](docs/guides/user-guide.md)
- [MCP Integration](docs/guides/mcp-integration.md)
- [Abductive Reasoning Concepts](docs/concepts/abductive-reasoning.md)

## Contributing

- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## License

MIT License. See [LICENSE](LICENSE).
