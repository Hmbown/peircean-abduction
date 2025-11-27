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

## Peirce's Canonical Form

The Peircean Logic Harness enforces Peirce's three-stage abductive inference:

```
C (Surprising Fact) → A (Hypothesis) → "If A, then C would be expected"
```

| Phase | Tool | Peirce's Schema |
|-------|------|-----------------|
| 1. Observation | `observe_anomaly` | "The surprising fact, C, is observed" |
| 2. Hypothesis | `generate_hypotheses` | "But if A were true, C would be a matter of course" |
| 3. Selection | `evaluate_via_ibe` | "Hence, there is reason to suspect that A is true" |

## The 3 Core Tools

### 1. `observe_anomaly`

**Phase 1**: Register the surprising fact (C).

```python
observe_anomaly(
    observation="Server latency spiked 10x but CPU/memory normal",
    context="No recent deployments, traffic is steady",
    domain="technical"
)
```

**Output** (execute the returned prompt to get):
```json
{
    "anomaly": {
        "fact": "Server latency spiked 10x but CPU/memory normal",
        "surprise_level": "high",
        "surprise_score": 0.85,
        "expected_baseline": "Latency correlates with resource usage",
        "domain": "technical",
        "context": ["No recent deployments", "Traffic is steady"],
        "key_features": ["Latency spike", "Normal CPU", "Normal memory"],
        "surprise_source": "Violates expected correlation between latency and resources"
    }
}
```

### 2. `generate_hypotheses`

**Phase 2**: Generate candidate explanations (A's) that would make C expected.

```python
generate_hypotheses(
    anomaly_json='{"anomaly": {...}}',  # Output from Phase 1
    num_hypotheses=5
)
```

**Output** (execute the returned prompt to get):
```json
{
    "hypotheses": [
        {
            "id": "H1",
            "statement": "Database connection pool exhaustion",
            "explains_anomaly": "If DB connections are exhausted, requests queue causing latency without CPU load",
            "prior_probability": 0.35,
            "assumptions": [
                {"statement": "Database is the bottleneck", "testable": true}
            ],
            "testable_predictions": [
                {
                    "prediction": "DB connection count at maximum",
                    "test_method": "Check connection pool metrics",
                    "if_true": "Supports H1",
                    "if_false": "Weakens H1"
                }
            ]
        }
    ]
}
```

### 3. `evaluate_via_ibe`

**Phase 3**: Inference to Best Explanation selection.

```python
evaluate_via_ibe(
    anomaly_json='{"anomaly": {...}}',      # Output from Phase 1
    hypotheses_json='{"hypotheses": [...]}',  # Output from Phase 2
    use_council=True  # Optional: include Council of Critics
)
```

**Output** (execute the returned prompt to get):
```json
{
    "evaluation": {
        "best_hypothesis": "H1",
        "scores": {
            "H1": {
                "explanatory_power": 0.85,
                "parsimony": 0.70,
                "testability": 0.90,
                "consilience": 0.75,
                "composite": 0.80
            }
        },
        "ranking": ["H1", "H3", "H2"],
        "verdict": "investigate",
        "confidence": 0.78,
        "rationale": "H1 provides the strongest explanation with lowest test cost",
        "next_steps": [
            "Check database connection pool metrics",
            "Review application logs for connection timeouts"
        ],
        "alternative_if_wrong": "If H1 falsified, H3 becomes most probable"
    }
}
```

## Council of Critics

When `use_council=True`, hypotheses are evaluated from 5 perspectives:

| Critic | Focus | Key Questions |
|--------|-------|---------------|
| **Empiricist** | Evidence & testability | What data supports/refutes this? |
| **Logician** | Consistency & parsimony | Is it internally consistent? |
| **Pragmatist** | Actionability | What should we DO if true? |
| **Economist** | Cost-benefit | Which is cheapest to test? |
| **Skeptic** | Falsification | How would we disprove this? |

You can also consult critics individually:

```python
critic_evaluate(
    critic="skeptic",
    anomaly_json='{"anomaly": {...}}',
    hypotheses_json='{"hypotheses": [...]}'
)
```

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

Then **restart Claude Desktop** (Cmd+Q / Ctrl+Q and reopen).

**Verify:** Ask *"What Peircean tools are available?"*

---

### Claude Code (CLI)

```bash
claude mcp add peircean -- python -m peircean.mcp.server
```

Verify:

```bash
claude mcp list
```

You should see `peircean` in the list. Restart your terminal session.

---

### Cursor

1. Run `peircean-setup-mcp` (without `--write`) to get the JSON config
2. Copy the output
3. Go to **Settings → Features → MCP**
4. Paste the configuration
5. Restart Cursor

---

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

---

### Gemini CLI

```bash
gemini extensions install https://github.com/Hmbown/peircean-abduction --branch main --path peircean-mcp-node
```

---

### Windsurf / Other MCP Clients

Use these settings:

| Setting | Value |
|---------|-------|
| Command | `python` |
| Args | `["-m", "peircean.mcp.server"]` |

Or if installed globally:

| Setting | Value |
|---------|-------|
| Command | `peircean-server` |
| Args | `[]` |

---

### Python Path Issues?

If you get "command not found" errors, use the full Python path:

**Homebrew (macOS):**
```json
{
  "mcpServers": {
    "peircean": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "peircean.mcp.server"]
    }
  }
}
```

**Pyenv:**
```json
{
  "mcpServers": {
    "peircean": {
      "command": "/Users/you/.pyenv/versions/3.11.9/bin/python",
      "args": ["-m", "peircean.mcp.server"]
    }
  }
}
```

**Find your Python path:**
```bash
which python3
# or
python -c "import sys; print(sys.executable)"
```

---

### Verify Installation

```bash
python verify_peircean.py
```

## Single-Shot Mode

For quick analysis without intermediate results:

```python
abduce_single_shot(
    observation="Customer churn rate doubled in Q3",
    context="No price changes, NPS stable, no competitor launches",
    domain="financial",
    num_hypotheses=5
)
```

## Supported Domains

| Domain | Hypothesis Templates |
|--------|---------------------|
| `general` | Causal, systemic, human factors, external factors |
| `financial` | Market microstructure, information asymmetry, behavioral, macro |
| `legal` | Statutory interpretation, precedent conflicts, jurisdictional |
| `medical` | Differential diagnosis, drug interactions, comorbidity |
| `technical` | Race conditions, resource exhaustion, cascading failures |
| `scientific` | Measurement error, confounding variables, replication issues |

## ⚡ Case Study: The "Lumping" Problem

Why do we need structured abduction? Because standard LLMs tend to "lump" distinct possibilities into a single safe conclusion.

**The Test:**
We fed a scenario to a standard LLM and the Peircean Harness:
* *Scenario:* A "dead" satellite suddenly fired thrusters and hit a station.
* *Key Detail:* The satellite steered *into* the collision path.

**The Standard LLM Output (Induction):**
> "The most likely explanation is that Country A was covertly maintaining an active military satellite... and a specific maneuver (**whether automated failure or intentional command**) directly caused the collision."

* **Result:** It correctly identified the lie ("It's not debris"), but it **lumped** the two most important possibilities (Glitch vs. Attack) into a parenthetical. It stopped at "Liability."

**The Peircean Output (Abduction):**
> **Hypothesis 1 (Intent):** "The precise vector ('into' the collision) implies a targeted strike." (Explains the vector).
> **Hypothesis 3 (Glitch):** "An automated fail-safe triggered erroneously." (Explains the burn, fails to explain the vector).
> **Verdict:** "Investigate H1. Check RF spectrum logs for uplink signals at T-10s."

* **Result:** It **split** the possibilities based on the specific evidence (the vector). It didn't just find "Liability"; it identified **Culpability**.

**The Takeaway:**
Standard LLMs act like a Jury (deciding true/false). Peircean Abduction acts like a Detective (investigating *which* version of the truth is most likely).

## Why Abduction?

| Inference | Direction | Function | Creates New Ideas? |
|-----------|-----------|----------|-------------------|
| **Deduction** | Rule → Result | Tests implications | No |
| **Induction** | Cases → Rule | Confirms patterns | No |
| **Abduction** | Surprise → Hypothesis | Generates explanations | **Yes** |

Abduction is the only logical operation that introduces new ideas. Standard LLMs optimize for probability—they retrieve "normal" answers. When faced with anomalies, they either:

1. **Hallucinate normalcy**: Force-fit conventional explanations
2. **Refuse uncertainty**: Produce vague responses
3. **Miss the signal**: Treat anomalies as noise

The Peircean Logic Harness forces explicit hypothesis generation and evaluation.

## Architecture

```
User / Agent
     │
     ▼
┌─────────────────────────────────────┐
│  Peircean Logic Harness (MCP)       │
│                                     │
│  observe_anomaly (Phase 1)          │
│         │                           │
│         ▼                           │
│  generate_hypotheses (Phase 2)      │
│         │                           │
│         ▼                           │
│  evaluate_via_ibe (Phase 3)         │
│         │                           │
│    [Council of Critics]             │
└─────────────────────────────────────┘
     │
     ▼
LLM Provider (Claude, GPT, etc.)
     │
     ▼
Structured JSON with selected hypothesis + next steps
```

## Example: Full Trace (International Space Law)

**Query**: "A 'defunct' military satellite (Country A) collided with a commercial station (Country B). Country A claimed it was uncontrollable debris, but recovered flight logs show a 2-second thruster burn 10 seconds before impact—steering *into* the collision path."

### Phase 1: Observation
```json
{
    "anomaly": {
        "fact": "Defunct 'debris' satellite executed a controlled burn 10s before collision, steering into the target.",
        "surprise_level": "anomalous",
        "surprise_score": 0.95,
        "expected_baseline": "Space debris follows ballistic trajectories and does not execute maneuvers.",
        "domain": "Legal / International Space Law",
        "key_features": [
            "Active thruster burn from 'defunct' satellite",
            "Timing: 10 seconds before impact",
            "Vector: Steered into collision path",
            "Contradiction: Legal classification vs. Physical behavior"
        ],
        "surprise_source": "Violates the definition of space debris and the expectation of rational actor behavior."
    },
    "recommended_council": ["Space Law Specialist", "Orbital Mechanics Expert", "Military Strategy Analyst"]
}
```

### Phase 2: Hypotheses
```json
{
    "hypotheses": [
        {
            "id": "H1",
            "statement": "The satellite was never defunct; it was a dormant 'sleeper' weapon activated for a kinetic strike.",
            "explains_anomaly": "Explains thruster capability, precise timing, and intentional steering into target.",
            "prior_probability": 0.20,
            "testable_predictions": [
                {"prediction": "Encrypted uplink signal detected shortly before burn", "test_method": "Review RF spectrum logs"}
            ]
        },
        {
            "id": "H2",
            "statement": "A cyber-intrusion by a third party hijacked the satellite's command link.",
            "explains_anomaly": "Explains why Country A claimed debris (they lost control) but it still maneuvered.",
            "prior_probability": 0.30,
            "testable_predictions": [
                {"prediction": "Command logs show unauthorized IP or anomalous signal origin", "test_method": "Forensic analysis of ground control"}
            ]
        },
        {
            "id": "H3",
            "statement": "An automated 'end-of-life' deorbit script triggered erroneously due to sensor malfunction.",
            "explains_anomaly": "Explains the burn without malicious intent; collision was accidental.",
            "prior_probability": 0.40,
            "testable_predictions": [
                {"prediction": "Code review reveals 'dead man switch' logic", "test_method": "Audit satellite firmware"}
            ]
        }
    ]
}
```

### Phase 3: IBE Selection (with Custom Council)
```json
{
    "council": ["Space Law Specialist", "Orbital Mechanics Expert", "Military Strategy Analyst"],
    "evaluation": {
        "best_hypothesis": "H1",
        "scores": {
            "H1": {"explanatory_power": 0.90, "parsimony": 0.60, "testability": 0.85, "composite": 0.83},
            "H2": {"explanatory_power": 0.75, "parsimony": 0.70, "testability": 0.70, "composite": 0.72},
            "H3": {"explanatory_power": 0.50, "parsimony": 0.85, "testability": 0.80, "composite": 0.68}
        },
        "ranking": ["H1", "H2", "H3"],
        "verdict": "investigate",
        "confidence": 0.78,
        "rationale": "H1 uniquely explains the vector (steering INTO collision). H3 explains the burn but not the direction.",
        "next_steps": [
            "Review RF spectrum logs for uplink signals at T-10s",
            "Check satellite command encryption status",
            "Examine trajectory simulation to confirm vector was intentional"
        ]
    }
}
```

**Key Insight**: H3 (automated glitch) has the highest prior probability (0.40), but H1 (intentional strike) scores highest on explanatory power because only intent explains why the satellite steered *into* the collision path rather than away.

## Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [User Guide](docs/USER_GUIDE.md)
- [MCP Reference](docs/MCP.md)

## Contributing

We welcome issues and PRs. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgments

- **Charles Sanders Peirce** (1839-1914) for developing the theory of abduction
- **Hegelion** for architectural inspiration
- **Shannon Labs** for ongoing research support

---

*"Abduction is the process of forming explanatory hypotheses. It is the only logical operation which introduces any new idea."* — C.S. Peirce, CP 5.172
