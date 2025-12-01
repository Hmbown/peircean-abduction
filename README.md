# Peircean Abduction

[![CI](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml/badge.svg)](https://github.com/Hmbown/peircean-abduction/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/peircean-abduction.svg)](https://pypi.org/project/peircean-abduction/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A Logic Harness for Abductive Inference - Provider-Agnostic Configuration**

Peircean Abduction forces LLMs to stop guessing and start investigating. It implements Charles Sanders Peirce's logical framework to make uncertainty visible and hypotheses testable, with seamless support for multiple LLM providers.

> **Anomaly in → Hypothesis out.**

```
"The surprising fact, C, is observed.
But if A were true, C would be a matter of course.
Hence, there is reason to suspect that A is true."
— Charles Sanders Peirce, Collected Papers 5.189
```

---

## 🚀 Quick Start

### Installation

```bash
# Install with optional dependencies for your preferred provider
pip install peircean-abduction[all]  # All providers
# OR
pip install peircean-abduction           # Core only, add providers as needed

# Optional: Install specific providers
pip install peircean-abduction[anthropic]  # Anthropic Claude
pip install peircean-abduction[openai]      # OpenAI GPT
pip install peircean-abduction[gemini]     # Google Gemini
pip install peircean-abduction[ollama]     # Local Ollama
```

### Verify Installation

```bash
# Comprehensive system check
peircean --verify
```

### First Run

```bash
# Interactive configuration wizard
peircean config wizard

# Or start with prompt generation (no API key required)
peircean "The stock market dropped 5% on good economic news"
```

---

## 🔌 MCP Integration

Peircean Abduction works best with Model Context Protocol (MCP) integration in Claude Desktop, Cursor, and other IDEs.

### Automatic Setup

```bash
# Automatically configure Claude Desktop / Cursor
peircean --install
```

### Manual Setup

```bash
# View current configuration
peircean config show

# List available providers
peircean config providers

# Validate setup
peircean config validate
```

### Usage in Claude Desktop

1. After installation, restart Claude Desktop
2. Look for the 🔌 icon indicating active tools
3. Try it out:
   > "Analyze this anomaly: Server latency spiked 10x but CPU usage is flat"

---

## 🤖 Provider Configuration

Peircean Abduction supports multiple LLM providers with seamless switching via environment variables.

### Quick Configuration

```bash
# Interactive setup (recommended)
peircean config wizard

# Manual setup - create .env file
cp .env.example .env
# Edit .env with your provider settings
```

### Supported Providers

| Provider | Environment Variable | Models | Installation |
|----------|----------------------|--------|--------------|
| **Anthropic Claude** | `PEIRCEAN_PROVIDER=anthropic` | claude-3-sonnet-20241022, claude-3-haiku-20241022 | `[anthropic]` |
| **OpenAI GPT** | `PEIRCEAN_PROVIDER=openai` | gpt-4, gpt-4-turbo, gpt-3.5-turbo | `[openai]` |
| **Google Gemini** | `PEIRCEAN_PROVIDER=gemini` | gemini-pro, gemini-pro-vision | `[gemini]` |
| **Ollama (Local)** | `PEIRCEAN_PROVIDER=ollama` | llama2, codellama, mistral | `[ollama]` |

### Environment Variables

```bash
# Provider selection
export PEIRCEAN_PROVIDER=anthropic
export PEIRCEAN_MODEL=claude-3-sonnet-20241022

# API keys (or use provider-specific env vars)
export PEIRCEAN_API_KEY=your_api_key_here
# OR
export ANTHROPIC_API_KEY=your_anthropic_key

# Feature toggles
export PEIRCEAN_ENABLE_COUNCIL=true
export PEIRCEAN_INTERACTIVE_MODE=false  # Default: prompt-only like Hegelion
export PEIRCEAN_DEBUG_MODE=false

# Performance settings
export PEIRCEAN_TEMPERATURE=0.7
export PEIRCEAN_TIMEOUT_SECONDS=60
```

---

## 🐍 Python API

### Basic Usage

```python
from peircean import PeirceanAbduction

# Initialize with default configuration
abduction = PeirceanAbduction()

# Analyze an observation
result = abduction.analyze(
    observation="Server latency spiked 10x but CPU usage is flat",
    domain="technical",
    num_hypotheses=5
)

print(result.best_hypothesis)
print(result.recommended_actions)
```

### Advanced Configuration

```python
from peircean import PeirceanAbduction, Provider
from peircean.config import PeirceanConfig

# Custom configuration
config = PeirceanConfig(
    provider=Provider.OPENAI,
    model="gpt-4",
    temperature=0.8,
    enable_council=True
)

abduction = PeirceanAbduction(config=config)
result = abduction.analyze("Customer churn doubled while NPS remained stable")
```

### Prompt Generation (Hegelion-style)

```python
from peircean import generate_prompt

# Generate prompt for external LLM use
prompt = generate_prompt(
    observation="Sales increased while customer satisfaction decreased",
    domain="business",
    use_council=True
)

print(prompt)  # Copy to any LLM
```

---

## 📚 CLI Reference

### Core Commands

```bash
# Abductive analysis (default: prompt-only)
peircean "Your observation here"

# Specify domain and options
peircean --domain financial "Market anomaly detected"
peircean --num-hypotheses 3 --council "System behavior unexpected"

# Output formats
peircean --format json "Observation" | jq .
peircean --prompt "Generate abductive prompt"
```

### Configuration Commands

```bash
# View current configuration
peircean config show

# Validate setup
peircean config validate

# List available providers
peircean config providers

# Interactive configuration wizard
peircean config wizard
```

### Management Commands

```bash
# System verification
peircean --verify

# MCP integration setup
peircean --install

# JSON output for automation
peircean --install --json
```

### Benchmark Commands

```bash
# Run all benchmark scenarios
peircean-bench

# Run quick scenarios for fast testing
peircean-bench --quick

# Test specific domain scenarios
peircean-bench --domain financial

# Test provider availability and configuration
peircean-bench --providers

# Export benchmark results to JSON
peircean-bench --export-json results.json

# Test specific scenario
peircean-bench --scenario simple_financial
```

---

## 🧠 How It Works

Peircean Abduction implements Charles Sanders Peirce's three-phase logical framework:

### Phase 1: Observe (`peircean_observe_anomaly`)
- **Input**: Raw observation (e.g., "Server latency spiked 10x but CPU is normal")
- **Output**: Structured analysis defining *why* this is surprising and expected baseline

### Phase 2: Hypothesize (`peircean_generate_hypotheses`)
- **Input**: Anomaly analysis from Phase 1
- **Output**: Distinct, falsifiable hypotheses with testable predictions

### Phase 3: Evaluate (`peircean_evaluate_via_ibe`)
- **Input**: Hypotheses from Phase 2
- **Output**: Best explanation selected via **Inference to Best Explanation (IBE)**
- **Optional**: Council of Critics evaluation (5 specialist perspectives)

### Single-Shot Mode

```bash
# Complete analysis in one step
peircean --council "Anomalous system behavior detected"
```

---

## ⚙️ Configuration

### Configuration Files

Peircean Abduction automatically loads configuration from:

1. **Environment variables** (highest priority)
2. **.env file** (current directory and parent directories)
3. **Default values** (lowest priority)

### Configuration Wizard

```bash
# Interactive setup for new users
peircean config wizard
```

The wizard guides you through:
- Provider selection and setup
- API key configuration
- Feature toggle preferences
- MCP integration setup

### Feature Toggles

| Feature | Environment Variable | Default | Description |
|---------|----------------------|---------|-------------|
| Council of Critics | `PEIRCEAN_ENABLE_COUNCIL` | `true` | Enable multi-perspective evaluation |
| Interactive Mode | `PEIRCEAN_INTERACTIVE_MODE` | `false` | Direct LLM API calls (vs prompt-only) |
| Debug Mode | `PEIRCEAN_DEBUG_MODE` | `false` | Verbose logging and output |
| Default Domain | `PEIRCEAN_DEFAULT_DOMAIN` | `general` | Domain for abductive analysis |
| Hypotheses Count | `PEIRCEAN_DEFAULT_NUM_HYPOTHESES` | `5` | Number of hypotheses to generate |

---

## 🎯 Use Cases

### Software Engineering
```bash
# Debugging performance anomalies
peircean --domain technical "Database queries slowed down after deployment"

# Investigating system behavior
peircean "User engagement metrics dropped after feature release"
```

### Business Analysis
```bash
# Market analysis
peircean --domain financial "Stock price moved opposite to earnings news"

# Customer behavior
peircean --domain general "Customer retention improved while support tickets increased"
```

### Research & Investigation
```bash
# Scientific anomalies
peircean --domain scientific "Experimental results contradict established theory"

# Legal analysis
peircean --domain legal "Contract terms seem to create unintended obligations"
```

---

## 📖 Documentation

### User Guides
- [**Installation Guide**](docs/getting-started/installation.md) - Detailed setup instructions
- [**Quick Start**](docs/getting-started/quickstart.md) - Get up and running in 5 minutes
- [**Configuration Guide**](docs/guides/configuration.md) - Complete configuration reference
- [**User Guide**](docs/guides/user-guide.md) - Comprehensive usage examples

### Technical Documentation
- [**API Reference**](docs/reference/api.md) - Complete Python API documentation
- [**MCP Integration Guide**](docs/guides/mcp-integration.md) - IDE setup and usage
- [**Peircean Specification**](docs/PEIRCEAN_SPEC.md) - Detailed technical specification

### Concepts
- [**Abductive Reasoning**](docs/concepts/abductive-reasoning.md) - Peirce's logical framework
- [**Council of Critics**](docs/concepts/council-of-critics.md) - Multi-perspective evaluation

### Examples
- [**Quick Examples**](docs/examples/) - Basic usage patterns
- [**API Latency Anomaly**](docs/examples/api-latency-anomaly.md) - Performance debugging example
- [**Kubernetes Anomaly**](docs/examples/kubernetes-anomaly.md) - Infrastructure investigation example

### Benchmarking
- [**Performance Benchmarks**](#cli-reference) - Built-in performance testing with `peircean-bench`

---

## 🤝 Contributing

We welcome contributions! See [**Contributing Guidelines**](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check
ruff format
```

---

- [**Code of Conduct**](CODE_OF_CONDUCT.md)
