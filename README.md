# Peircean Abduction

**A Logic Harness for Abductive Inference.**

> "Abduction is the process of forming an explanatory hypothesis. It is the only logical operation which introduces any new idea." — Charles Sanders Peirce

Peircean Abduction is a **Model Context Protocol (MCP)** server that gives LLMs the ability to perform rigorous abductive reasoning. It forces models to generate multiple competing hypotheses for an observation and evaluate them using **Inference to the Best Explanation (IBE)**.

## ✨ Features

*   **MCP-First Design:** Built to be used directly within Claude Desktop, Cursor, or any MCP-compliant client.
*   **Provider Agnostic:** Works with **Anthropic**, **OpenAI**, **Gemini**, and **Ollama**.
*   **No API Key Required (Default):** By default, it generates *prompts* for you to run. You only need an API key if you want the tool to execute the reasoning loop autonomously.
*   **Council of Critics:** Simulates a debate between a Logician, Empiricist, and Scientist to refine hypotheses.

## 🚀 Quick Start

### 1. Install

```bash
pip install peircean-abduction
```

### 2. Connect to Claude Desktop

Run the installer to automatically configure Claude Desktop:

```bash
peircean --install
```

### 3. Use it!

Open Claude and ask:

> "Use the `peircean_observe_anomaly` tool to analyze why my server latency spiked but CPU usage is flat."

## 🛠️ Configuration

You can configure the provider and other settings via the interactive wizard:

```bash
peircean config wizard
```

Or by setting environment variables in a `.env` file:

```bash
# Provider Selection
PEIRCEAN_PROVIDER=anthropic  # anthropic, openai, gemini, ollama
PEIRCEAN_MODEL=claude-3-5-sonnet-20241022

# API Keys (Only needed for interactive/autonomous mode)
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...

# Feature Toggles
PEIRCEAN_ENABLE_COUNCIL=true
PEIRCEAN_INTERACTIVE_MODE=false # Set to true to let the tool call the LLM directly
```

## 📦 Supported Models

*   **Anthropic:** Claude 3.5 Sonnet (Recommended), Claude 3 Opus, Claude 3 Haiku
*   **OpenAI:** GPT-4o, GPT-4 Turbo
*   **Gemini:** Gemini 1.5 Pro
*   **Ollama:** Llama 3, Mistral

## 📚 Documentation

*   [Installation Guide](docs/getting-started/installation.md)
*   [Configuration Guide](docs/guides/configuration.md)
*   [API Reference](docs/reference/api.md)

## 📄 License

MIT
