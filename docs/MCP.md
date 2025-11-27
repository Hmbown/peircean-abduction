# MCP Integration Guide

A **Logic Harness** for abductive inference. Anomaly in → Hypothesis out.

## Quick Reference

| Client | Command |
|--------|---------|
| Claude Desktop | `peircean-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"` |
| Claude Code | `claude mcp add peircean -- python -m peircean.mcp.server` |
| Cursor | Settings → Features → MCP → paste config |
| VS Code | MCP extension settings |

---

## Claude Desktop

### macOS

```bash
peircean-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

### Windows

```bash
peircean-setup-mcp --write "%APPDATA%\Claude\claude_desktop_config.json"
```

### Linux

```bash
peircean-setup-mcp --write "$HOME/.config/Claude/claude_desktop_config.json"
```

### Manual Configuration

Add to your `claude_desktop_config.json`:

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

**Restart Claude Desktop** (Cmd+Q / Ctrl+Q and reopen).

**Verify:** Ask *"What Peircean tools are available?"*

---

## Claude Code (CLI)

```bash
claude mcp add peircean -- python -m peircean.mcp.server
```

Verify installation:

```bash
claude mcp list
```

You should see `peircean` in the output. Restart your terminal.

---

## Cursor

1. Run `peircean-setup-mcp` (without `--write`) to get the JSON config
2. Copy the JSON output
3. Open **Settings → Features → MCP**
4. Paste the configuration
5. Restart Cursor

---

## VS Code (MCP Extension)

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

## Gemini CLI

```bash
gemini extensions install https://github.com/Hmbown/peircean-abduction --branch main --path peircean-mcp-node
```

---

## Windsurf / Other MCP Clients

Use these settings:

| Setting | Value |
|---------|-------|
| Command | `python` |
| Args | `["-m", "peircean.mcp.server"]` |

Or if installed globally via pip:

| Setting | Value |
|---------|-------|
| Command | `peircean-server` |
| Args | `[]` |

---

## Python Path Issues

If you get "command not found" errors, use the full Python path.

**Find your Python:**

```bash
which python3
# or
python -c "import sys; print(sys.executable)"
```

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

**Conda:**

```json
{
  "mcpServers": {
    "peircean": {
      "command": "/Users/you/anaconda3/envs/myenv/bin/python",
      "args": ["-m", "peircean.mcp.server"]
    }
  }
}
```

---

## Available Tools

### The 3-Phase Abductive Loop

| Phase | Tool | Purpose |
|-------|------|---------|
| 1 | `observe_anomaly` | Register the surprising fact (C) |
| 2 | `generate_hypotheses` | Generate candidate explanations (A's) |
| 3 | `evaluate_via_ibe` | Select best explanation via IBE |

### Additional Tools

| Tool | Purpose |
|------|---------|
| `abduce_single_shot` | All 3 phases in one prompt |
| `critic_evaluate` | Council of Critics perspective |

---

### `observe_anomaly`

**Phase 1:** Register the surprising fact.

```
observe_anomaly(
  observation: "Server latency spiked 10x but CPU/memory normal",
  context: "No recent deployments, traffic is steady",
  domain: "technical"
)
```

**Parameters:**
- `observation` (required): The surprising fact
- `context` (optional): Background information
- `domain` (optional): `general`, `financial`, `legal`, `medical`, `technical`, `scientific`

**Output:** JSON with `anomaly` object containing `fact`, `surprise_level`, `surprise_score`, etc.

---

### `generate_hypotheses`

**Phase 2:** Generate candidate explanations.

```
generate_hypotheses(
  anomaly_json: '{"anomaly": {...}}',  // Output from Phase 1
  num_hypotheses: 5
)
```

**Parameters:**
- `anomaly_json` (required): JSON from `observe_anomaly`
- `num_hypotheses` (optional): Number to generate (default: 5)

**Output:** JSON with `hypotheses` array containing `id`, `statement`, `explains_anomaly`, `testable_predictions`, etc.

---

### `evaluate_via_ibe`

**Phase 3:** Inference to Best Explanation.

```
evaluate_via_ibe(
  anomaly_json: '{"anomaly": {...}}',
  hypotheses_json: '{"hypotheses": [...]}',
  use_council: true
)
```

**Parameters:**
- `anomaly_json` (required): JSON from Phase 1
- `hypotheses_json` (required): JSON from Phase 2
- `use_council` (optional): Include Council of Critics (default: false)

**Output:** JSON with `evaluation` containing `best_hypothesis`, `scores`, `ranking`, `verdict`, `next_steps`.

---

### `abduce_single_shot`

Complete abduction in one step.

```
abduce_single_shot(
  observation: "Customer churn rate doubled in Q3",
  context: "No price changes, NPS stable",
  domain: "financial",
  num_hypotheses: 5
)
```

**Output:** Combined JSON with `observation_analysis`, `hypotheses`, and `selection`.

---

### `critic_evaluate`

Get perspective from a specific critic.

```
critic_evaluate(
  critic: "skeptic",
  anomaly_json: '{"anomaly": {...}}',
  hypotheses_json: '{"hypotheses": [...]}'
)
```

**Critics:**
- `empiricist` - Evidence & testability
- `logician` - Consistency & parsimony
- `pragmatist` - Actionability
- `economist` - Cost-benefit analysis
- `skeptic` - Falsification & alternatives

---

## Usage Examples

### Natural Language (Claude Desktop)

```
"Use Peircean abduction to analyze why our database queries
are suddenly 3x slower despite no code changes"
```

```
"Run abductive analysis on this anomaly:
trading volume spiked 500% with no news"
```

### Step-by-Step Workflow

1. Call `observe_anomaly` with your observation
2. Execute returned prompt → get `anomaly` JSON
3. Call `generate_hypotheses` with anomaly JSON
4. Execute returned prompt → get `hypotheses` JSON
5. Call `evaluate_via_ibe` with both JSONs
6. Execute returned prompt → get `evaluation` with best hypothesis

### With Council of Critics

```
evaluate_via_ibe(
  anomaly_json: "...",
  hypotheses_json: "...",
  use_council: true
)
```

Or consult critics individually:

```
critic_evaluate(critic: "skeptic", anomaly_json: "...", hypotheses_json: "...")
critic_evaluate(critic: "empiricist", anomaly_json: "...", hypotheses_json: "...")
```

---

## Troubleshooting

### Server Not Starting

1. Verify installation: `pip show peircean-abduction`
2. Check Python path: `which python3`
3. Try manual start: `python -m peircean.mcp.server`
4. Check logs (output goes to stderr)

### Tools Not Appearing

1. **Restart the MCP host** (Claude Desktop, etc.)
2. Verify config file syntax (valid JSON)
3. Check server name matches (`peircean`)

### "Module not found" Error

The `peircean` package isn't in your Python path. Either:
- Use full Python path in config
- Install in the same Python that MCP calls

### Logging

The server logs to stderr. Set debug level:

```bash
PEIRCEAN_LOG_LEVEL=DEBUG python -m peircean.mcp.server
```

### Verify Installation

```bash
python verify_peircean.py
```

All 10 tests should pass:
- Module imports
- Tool registration
- Tool docstrings
- Phase flow
- Error handling
- Logging configuration
- SYSTEM_DIRECTIVE

---

## Architecture

```
MCP Client (Claude Desktop, Cursor, etc.)
     │
     │ calls tool
     ▼
┌─────────────────────────────────────┐
│  Peircean MCP Server (FastMCP)      │
│                                     │
│  observe_anomaly → prompt           │
│  generate_hypotheses → prompt       │
│  evaluate_via_ibe → prompt          │
└─────────────────────────────────────┘
     │
     │ returns prompt (JSON)
     ▼
MCP Client executes prompt with LLM
     │
     │ LLM generates JSON response
     ▼
Structured hypothesis with next steps
```

**Key insight:** The MCP server generates **prompts**, not LLM responses. The prompts enforce JSON-only output with the SYSTEM_DIRECTIVE. Your MCP client's LLM executes these prompts.

---

## No API Keys Needed

Peircean generates prompts. Your MCP client's model runs them.

- Claude Desktop → uses your Claude subscription
- Cursor → uses your configured model
- VS Code → uses your MCP extension's model

The server itself requires no API keys or external calls.
