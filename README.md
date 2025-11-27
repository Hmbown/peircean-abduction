# Peircean

[![CI](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml/badge.svg)](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **Logic Harness** for abductive inference. Forces LLMs to make uncertainty visible through explicit hypothesis generation and Inference to Best Explanation.

> **Anomaly in → Hypothesis out.**

```
"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."
— Charles Sanders Peirce, Collected Papers 5.189
```

## ⚡ Case Study: International Space Law

**The Problem:** Standard LLMs act like a **Jury** (deciding true/false based on probability). They tend to "lump" distinct possibilities into a single safe conclusion.

**The Solution:** Peircean Abduction acts like a **Detective** (investigating *which* version of the truth is most likely).

**The Scenario:**
A "defunct" military satellite (Country A) collided with a commercial station (Country B). Country A claimed it was uncontrollable debris, but recovered flight logs show a **2-second thruster burn 10 seconds before impact**—steering *into* the collision path.

### Standard LLM (Induction)
> "The most likely explanation is that Country A was covertly maintaining an active military satellite... and a specific maneuver (**whether automated failure or intentional command**) directly caused the collision."

*   **Result:** It **lumps** the two most important possibilities (Glitch vs. Attack) into a parenthetical. It stops at "Liability."

### Peircean Harness (Abduction)
The harness forces the model to split the anomaly into distinct, testable hypotheses.

**1. Observation (`peircean_observe_anomaly`)**
> **Anomaly:** "Defunct 'debris' satellite executed a controlled burn 10s before collision, steering into the target."
> **Surprise Source:** Violates definition of space debris and expectation of rational actor.

**2. Hypotheses (`peircean_generate_hypotheses`)**
> **H1 (Intent):** "The satellite was a dormant 'sleeper' weapon activated for a kinetic strike." (Explains the vector).
> **H3 (Glitch):** "An automated 'end-of-life' deorbit script triggered erroneously." (Explains the burn, fails to explain the vector).

**3. Selection (`peircean_evaluate_via_ibe`)**
> **Verdict:** "Investigate H1. Check RF spectrum logs for uplink signals at T-10s."
> **Rationale:** H1 uniquely explains the vector (steering INTO collision). H3 explains the burn but not the direction.

**Key Insight:** H3 (glitch) has higher *prior probability* (0.40), but H1 (attack) has higher *explanatory power*. The harness catches this distinction.

---

## 🚀 Quick Start

1.  **[Install the Package](#installation)**
2.  **Connect to your Client:**
    *   [Claude Desktop](#claude-desktop)
    *   [Cursor](#cursor)
    *   [VS Code](#vs-code-with-mcp-extension)
    *   [Claude CLI](#claude-code-cli)

---

## The 3 Core Tools

The harness enforces Peirce's three-stage schema:
`C (Surprising Fact) → A (Hypothesis) → "If A, then C would be expected"`

### 1. `peircean_observe_anomaly`
Registers the surprising fact (C) and establishes a baseline.

```python
peircean_observe_anomaly(
    observation="Satellite executed burn 10s before impact",
    context="Country A claims it was debris",
    domain="legal"
)
```

### 2. `peircean_generate_hypotheses`
Generates candidate explanations (A's) that would make C expected.

```python
peircean_generate_hypotheses(
    anomaly_json='{"anomaly": {...}}',
    num_hypotheses=3
)
```

### 3. `peircean_evaluate_via_ibe`
Selects the best explanation using Inference to Best Explanation (IBE).

```python
peircean_evaluate_via_ibe(
    anomaly_json='{"anomaly": {...}}',
    hypotheses_json='{"hypotheses": [...]}',
    use_council=True
)
```

## Council of Critics

When `use_council=True`, hypotheses are evaluated from 5 perspectives:

| Critic | Focus | Key Question |
|--------|-------|--------------|
| **Empiricist** | Evidence | What data supports/refutes this? |
| **Logician** | Consistency | Is it internally consistent? |
| **Pragmatist** | Actionability | What should we DO if true? |
| **Economist** | Cost | Which is cheapest to test? |
| **Skeptic** | Falsification | How would we disprove this? |

## Installation

```bash
pip install peircean-abduction
```

Or from source:

```bash
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction
pip install -e ".[mcp]"
```

## MCP Client Setup

### Claude Desktop

**Automatic (recommended):**

```bash
# macOS
peircean-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Windows
peircean-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"

# Linux
peircean-setup-mcp --write "$HOME/.config/Claude/claude_desktop_config.json"
```

**Manual:** Add to your config file:

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

### Cursor

1. Run `peircean-setup-mcp` (without `--write`) to get the JSON config.
2. Copy the output.
3. Go to **Settings → Features → MCP**.
4. Paste the configuration.
5. Restart Cursor.

### VS Code (with MCP extension)

Add to your MCP extension settings:

```json
{
  "mcp.servers": {
    "peircean": {
      "command": "python",
      "args": ["-m", "peircean.mcp.server"]
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add peircean -- python -m peircean.mcp.server
```

### Other Clients (Windsurf, Gemini)

Use command `python` and args `["-m", "peircean.mcp.server"]`.

## Supported Domains

| Domain | Hypothesis Templates |
|--------|---------------------|
| `general` | Causal, systemic, human factors |
| `financial` | Market microstructure, information asymmetry |
| `legal` | Statutory interpretation, precedent conflicts |
| `medical` | Differential diagnosis, drug interactions |
| `technical` | Race conditions, resource exhaustion |
| `scientific` | Measurement error, confounding variables |

## Documentation & Contributing

- [Quick Start Guide](docs/QUICKSTART.md)
- [User Guide](docs/USER_GUIDE.md)
- [MCP Reference](docs/MCP.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## License

MIT License. See [LICENSE](LICENSE).

---

*"Abduction is the process of forming explanatory hypotheses. It is the only logical operation which introduces any new idea."* — C.S. Peirce
