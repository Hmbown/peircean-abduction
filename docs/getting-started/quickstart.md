# Quick Start Guide

Get up and running with Peircean Abduction in under 5 minutes.

## Installation

```bash
pip install peircean-abduction
```

## Option 1: Prompt Mode (Any LLM)

The simplest way to use Peircean Abduction is to generate prompts for your existing LLM setup:

```python
from peircean import abduction_prompt

# Generate a complete abduction prompt
prompt = abduction_prompt(
    observation="NVIDIA stock dropped 8% despite record earnings",
    domain="financial"
)

# Use with your LLM
response = your_llm(prompt)
print(response)
```

Or from the command line:

```bash
peircean --prompt "Stock dropped 5% on good news"
```

## Option 2: MCP Server (Claude Desktop / Cursor)

For integration with Claude Desktop, Cursor, or other MCP-compatible hosts:

```bash
# Auto-configure Claude Desktop
peircean-setup-mcp --write

# Restart Claude Desktop, then you can use:
# "Use abduction to analyze: [your observation]"
```

Manual configuration:

```json
{
  "mcpServers": {
    "peircean-abduction": {
      "command": "peircean-server",
      "args": []
    }
  }
}
```

## Option 3: Python Agent

For programmatic use with your own LLM backend:

```python
from peircean import AbductionAgent

# Define your LLM function
def my_llm(prompt: str) -> str:
    # Your LLM call here
    return response

# Create agent
agent = AbductionAgent(
    llm_call=my_llm,
    domain="technical",
    max_hypotheses=5
)

# Run abduction
result = agent.abduce_sync(
    "CPU usage dropped 40% but latency increased 200%"
)

print(f"Best explanation: {result.selected_hypothesis}")
print(f"Confidence: {result.confidence}")
print(f"Next steps: {result.recommended_actions}")
```

## Async Usage

```python
import asyncio
from peircean import AbductionAgent

async def my_llm_async(prompt: str) -> str:
    # Your async LLM call
    return response

agent = AbductionAgent(llm_call_async=my_llm_async)

async def main():
    result = await agent.abduce(
        "The surprising observation here"
    )
    return result

asyncio.run(main())
```

## Available Domains

Peircean Abduction includes domain-specific hypothesis templates:

- `general` - Default, covers common anomaly types
- `financial` - Market anomalies, trading patterns
- `legal` - Legal edge cases, precedent gaps
- `medical` - Diagnostic reasoning, symptom analysis
- `technical` - System failures, debugging
- `scientific` - Experimental anomalies

```python
from peircean import abduction_prompt, Domain

prompt = abduction_prompt(
    observation="Patient's fever resolved but CRP increased",
    domain=Domain.MEDICAL
)
```

## Output Formats

### Markdown (Human-Readable)

```python
result = agent.abduce_sync(observation)
print(result.to_markdown())
```

### JSON (Agent Integration)

```python
import json

result = agent.abduce_sync(observation)
print(json.dumps(result.to_json_trace(), indent=2))
```

## Next Steps

- [User Guide](../guides/user-guide.md) - Complete documentation
- [MCP Reference](../guides/mcp-integration.md) - MCP server details
- [Abductive Reasoning Concepts](../concepts/abductive-reasoning.md) - Philosophy and theory
