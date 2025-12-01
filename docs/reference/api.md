# Peircean Abduction: API Reference

Complete API reference for Peircean Abduction, covering all public functions, classes, and configuration management.

## Table of Contents

- [Core API](#core-api)
  - [Main Classes](#main-classes)
  - [Prompt Functions](#prompt-functions)
  - [Data Models](#data-models)
- [Configuration API](#configuration-api)
  - [Configuration Classes](#configuration-classes)
  - [Provider Management](#provider-management)
  - [Environment Utilities](#environment-utilities)
- [Provider API](#provider-api)
  - [Provider Registry](#provider-registry)
  - [Provider Interface](#provider-interface)
- [MCP Integration API](#mcp-integration-api)
- [CLI API](#cli-api)
- [Validation API](#validation-api)

## Core API

### Main Classes

#### `AbductionAgent`

Primary agent class for abductive reasoning with LLM integration.

```python
from peircean import AbductionAgent, Domain

# Initialize with custom LLM function
agent = AbductionAgent(
    llm_call=your_llm_function,
    domain=Domain.FINANCIAL,
    enable_council=True
)

# Perform abductive reasoning
result = await agent.abduce(
    "Stock dropped 5% on good earnings news"
)
```

**Parameters:**
- `llm_call` (Callable): Async function for LLM calls
- `domain` (Domain): Analysis domain (default: `Domain.GENERAL`)
- `enable_council` (bool): Enable Council of Critics evaluation
- `num_hypotheses` (int): Number of hypotheses to generate (default: 5)

**Methods:**
- `abduce(observation: str) -> AbductionResult`: Perform complete abductive analysis
- `observe_anomaly(observation: str) -> Observation`: Analyze surprising fact
- `generate_hypotheses(anomaly: Observation) -> List[Hypothesis]`: Generate candidate explanations
- `evaluate_hypotheses(hypotheses: List[Hypothesis]) -> AbductionResult`: Select best explanation

### Prompt Functions

#### `abduction_prompt()`

Generate complete abductive reasoning prompt for external LLM use.

```python
from peircean import abduction_prompt

prompt = abduction_prompt(
    observation="Server latency spiked 10x but CPU usage is flat",
    domain="technical",
    num_hypotheses=5,
    context={"recent_deployment": True}
)
```

**Parameters:**
- `observation` (str): The surprising fact to analyze
- `domain` (str): Analysis domain (default: "general")
- `num_hypotheses` (int): Number of hypotheses to generate (default: 5)
- `context` (dict, optional): Additional context information

**Returns:** `str` - Complete prompt for LLM

#### `observation_prompt()`

Generate Phase 1 observation analysis prompt.

```python
from peircean import observation_prompt

prompt = observation_prompt(
    observation="Customer churn doubled while NPS remained stable",
    domain="business"
)
```

**Parameters:**
- `observation` (str): The anomalous observation
- `domain` (str): Analysis domain (default: "general")

**Returns:** `str` - Observation analysis prompt

#### `hypothesis_prompt()`

Generate Phase 2 hypothesis generation prompt.

```python
from peircean import hypothesis_prompt

# Use with anomaly from Phase 1
anomaly = {"observation": "...", "analysis": "..."}
prompt = hypothesis_prompt(
    anomaly_json=json.dumps(anomaly),
    num_hypotheses=5
)
```

**Parameters:**
- `anomaly_json` (str): JSON-structured anomaly analysis from Phase 1
- `num_hypotheses` (int): Number of hypotheses to generate

**Returns:** `str` - Hypothesis generation prompt

### Data Models

#### `Observation`

Structured analysis of a surprising fact.

```python
from peircean import Observation

observation = Observation(
    fact="Server latency increased 10x",
    surprise_level=SurpriseLevel.HIGH,
    expected_baseline="Latency correlates with CPU usage",
    domain="technical",
    key_features=["Latency spike", "Normal CPU usage"],
    surprise_source="Violates expected performance correlation"
)
```

**Attributes:**
- `fact` (str): The observed surprising fact
- `surprise_level` (SurpriseLevel): Degree of surprise (LOW, MEDIUM, HIGH)
- `expected_baseline` (str): What was expected to happen
- `domain` (str): Analysis domain
- `key_features` (List[str]): Notable features of the observation
- `surprise_source` (str): Why this is surprising

#### `Hypothesis`

Candidate explanation with testable predictions.

```python
from peircean import Hypothesis, TestablePrediction, Assumption

hypothesis = Hypothesis(
    id="H1",
    statement="Database connection pool exhaustion",
    explains_anomaly="If pool exhausted, queries queue, causing latency spike",
    prior_probability=0.7,
    assumptions=[
        Assumption(
            statement="Connection pool has fixed size",
            testable=True
        )
    ],
    testable_predictions=[
        TestablePrediction(
            prediction="Database connection timeout errors increased",
            test_method="Check database logs for timeout errors",
            if_true="Supports H1",
            if_false="Weakens H1"
        )
    ]
)
```

**Attributes:**
- `id` (str): Hypothesis identifier (H1, H2, etc.)
- `statement` (str): Explanatory statement
- `explains_anomaly` (str): How this explains the observation
- `prior_probability` (float): Initial probability (0.0-1.0)
- `assumptions` (List[Assumption]): Underlying assumptions
- `testable_predictions` (List[TestablePrediction]): Testable predictions

#### `AbductionResult`

Complete abductive reasoning result with selected best explanation.

```python
result = AbductionResult(
    observation=observation,
    hypotheses=[hypothesis1, hypothesis2, hypothesis3],
    selected_hypothesis=hypothesis1,
    confidence=0.85,
    council_evaluation=council_eval,
    reasoning_steps=reasoning_trace
)
```

**Attributes:**
- `observation` (Observation): The analyzed observation
- `hypotheses` (List[Hypothesis]): All generated hypotheses
- `selected_hypothesis` (Hypothesis): Best explanation via IBE
- `confidence` (float): Confidence in selected hypothesis (0.0-1.0)
- `council_evaluation` (CouncilEvaluation, optional): Council of Critics evaluation
- `reasoning_steps` (List[ReasoningStep]): Step-by-step reasoning trace

## Configuration API

### Configuration Classes

#### `PeirceanConfig`

Main configuration class using Pydantic Settings.

```python
from peircean.config import PeirceanConfig, Provider

# Load from environment (default behavior)
config = PeirceanConfig()

# Or create with explicit values
config = PeirceanConfig(
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20241022",
    temperature=0.7,
    enable_council=True,
    interactive_mode=False  # Default: prompt-only like Hegelion
)
```

**Environment Variables:**
- `PEIRCEAN_PROVIDER`: LLM provider (anthropic, openai, gemini, ollama)
- `PEIRCEAN_MODEL`: Model name for selected provider
- `PEIRCEAN_API_KEY`: API key (or provider-specific env var)
- `PEIRCEAN_TEMPERATURE`: Generation temperature (0.0-1.0, default: 0.7)
- `PEIRCEAN_ENABLE_COUNCIL`: Enable Council of Critics (true/false, default: true)
- `PEIRCEAN_INTERACTIVE_MODE`: Direct LLM calls (true/false, default: false)
- `PEIRCEAN_DEBUG_MODE`: Verbose logging (true/false, default: false)

**Methods:**
- `validate_config() -> List[str]`: Validate configuration and return issues
- `get_provider_config() -> dict`: Get provider-specific configuration
- `to_dict() -> dict`: Convert to dictionary representation

#### `Provider`

Enum of supported LLM providers.

```python
from peircean.config import Provider

# Available providers
Provider.ANTHROPIC  # Anthropic Claude
Provider.OPENAI     # OpenAI GPT
Provider.GEMINI     # Google Gemini
Provider.OLLAMA     # Local Ollama models
```

### Provider Management

#### `get_config()`

Get current configuration instance.

```python
from peircean.config import get_config

config = get_config()
print(f"Provider: {config.provider.value}")
print(f"Model: {config.model}")
print(f"Interactive Mode: {config.interactive_mode}")
```

**Returns:** `PeirceanConfig` - Current configuration

#### `reload_config()`

Reload configuration from environment.

```python
from peircean.config import reload_config

# After changing environment variables
config = reload_config()
```

**Returns:** `PeirceanConfig` - Fresh configuration instance

### Environment Utilities

#### `validate_environment()`

Validate environment configuration and dependencies.

```python
from peircean.utils.env import validate_environment

validation = validate_environment()

if validation["valid"]:
    print("✅ Environment is valid")
else:
    print("❌ Issues found:")
    for issue in validation["issues"]:
        print(f"  • {issue}")

for warning in validation["warnings"]:
    print(f"⚠️  {warning}")
```

**Returns:** `dict` with keys:
- `valid` (bool): Overall environment validity
- `issues` (List[str]): Critical issues
- `warnings` (List[str]): Non-critical warnings
- `loaded_env_file` (str, optional): Path to loaded .env file

#### `get_provider_info()`

Get provider-specific configuration requirements.

```python
from peircean.utils.env import get_provider_info

anthropic_info = get_provider_info("anthropic")
print(f"API key env var: {anthropic_info['api_key_env']}")
print(f"Base URL: {anthropic_info['base_url']}")
print(f"Available models: {anthropic_info['models']}")
```

**Parameters:**
- `provider_name` (str): Provider name (anthropic, openai, gemini, ollama)

**Returns:** `dict` - Provider information

## Provider API

### Provider Registry

#### `get_provider_registry()`

Access the global provider registry.

```python
from peircean.providers import get_provider_registry

registry = get_provider_registry()

# List available providers
providers = registry.get_available_providers()
print(f"Available providers: {providers}")

# Get provider information
provider_info = registry.get_provider_info("anthropic")
print(f"Provider: {provider_info.display_name}")
print(f"Description: {provider_info.description}")
```

**Returns:** `ProviderRegistry` - Global registry instance

#### `get_provider_client()`

Get configured provider client instance.

```python
from peircean.providers import get_provider_client
from peircean.config import get_config

config = get_config()
client = get_provider_client(
    provider_name=config.provider.value,
    provider_config=config.get_provider_config()
)

if client and client.is_available():
    print(f"✅ {config.provider.value} client available")

    # Generate prompt (always available)
    prompt = client.generate_prompt(
        observation="System behavior anomaly",
        domain="technical"
    )

    # Generate completion (only in interactive mode)
    if config.interactive_mode:
        completion = client.generate_completion(prompt)
        print(completion)
else:
    print("❌ Provider not configured")
```

**Parameters:**
- `provider_name` (str): Provider name
- `provider_config` (dict): Provider configuration

**Returns:** `BaseProvider | None` - Provider instance or None

### Provider Interface

#### `BaseProvider`

Abstract base class for all provider implementations.

```python
from peircean.providers.registry import BaseProvider

class CustomProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        self.setup_client()

    def is_available(self) -> bool:
        return self.client is not None

    def generate_prompt(
        self,
        observation: str,
        domain: str = "general",
        num_hypotheses: int = 5,
        context: Optional[Dict[str, Any]] = None,
        use_council: bool = True
    ) -> str:
        from ..core import abduction_prompt
        return abduction_prompt(
            observation=observation,
            context=context,
            domain=domain,
            num_hypotheses=num_hypotheses
        )

    def generate_completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        # Custom implementation
        return self.client.generate(prompt)
```

**Required Methods:**
- `is_available() -> bool`: Check if provider is properly configured
- `generate_prompt() -> str`: Generate abductive reasoning prompt
- `generate_completion() -> Optional[str]`: Generate LLM completion

## MCP Integration API

### Server Setup

#### `main()` (MCP Server)

Start the Peircean Abduction MCP server.

```python
from peircean.mcp.server import main

# Start server (usually called via peircean-server CLI)
main()
```

**Environment Variables:**
- `PEIRCEAN_MCP_SERVER_HOST`: Server host (default: localhost)
- `PEIRCEAN_MCP_SERVER_PORT`: Server port (default: auto-assigned)

### Setup Utilities

#### `setup_mcp_config()`

Configure MCP server for IDEs.

```python
from peircean.mcp.setup import setup_mcp_config

# Setup for Claude Desktop (default)
success = setup_mcp_config(
    ide="claude-desktop",
    server_path="/path/to/peircean-server",
    write_config=True
)

# Setup for Cursor
success = setup_mcp_config(
    ide="cursor",
    server_path="/path/to/peircean-server"
)
```

**Parameters:**
- `ide` (str): Target IDE (claude-desktop, cursor, continue-dev)
- `server_path` (str): Path to peircean-server executable
- `write_config` (bool): Whether to write configuration file

**Returns:** `bool` - Success status

## CLI API

### Main Entry Point

#### `main()` (CLI)

Main CLI entry point.

```python
from peircean.cli import main
import sys

# Direct call (equivalent to peircean command)
exit_code = main()
sys.exit(exit_code)
```

**Command Line Interface:**

```bash
# Abductive analysis (prompt-only mode)
peircean "Server latency spiked but CPU is flat"

# With options
peircean --domain technical --council "Database slowdown after deployment"

# Configuration commands
peircean config show          # Show current configuration
peircean config validate      # Validate setup
peircean config providers     # List available providers
peircean config wizard        # Interactive setup

# Management commands
peircean --verify             # System verification
peircean --install            # MCP setup
```

### Configuration Commands

#### `cmd_config_show()`

Display current configuration.

```python
from peircean.cli import cmd_config_show

exit_code = cmd_config_show()  # Returns 0 on success
```

#### `cmd_config_validate()`

Validate configuration and environment.

```python
from peircean.cli import cmd_config_validate

exit_code = cmd_config_validate()  # Returns 0 if valid, 1 if issues found
```

## Validation API

### System Validation

#### `main()` (Validation)

Main validation entry point.

```python
from peircean.validate import main
import sys

# Run comprehensive validation (equivalent to peircean --verify)
exit_code = main()
sys.exit(exit_code)
```

**Validation Checks:**
- Python version compatibility
- Required dependencies availability
- Provider configuration validation
- MCP server setup verification
- System information display

#### `validate_dependencies()`

Validate required package dependencies.

```python
from peircean.validate import validate_dependencies

missing_deps = validate_dependencies()

if missing_deps:
    print("Missing dependencies:")
    for dep in missing_deps:
        print(f"  • {dep}")
else:
    print("✅ All dependencies available")
```

**Returns:** `List[str]` - List of missing dependencies

#### `validate_provider_config()`

Validate specific provider configuration.

```python
from peircean.validate import validate_provider_config

issues = validate_provider_config(
    provider="anthropic",
    config={"api_key": "sk-ant-..."}
)

if issues:
    print("Provider configuration issues:")
    for issue in issues:
        print(f"  • {issue}")
else:
    print("✅ Provider configuration valid")
```

**Parameters:**
- `provider` (str): Provider name
- `config` (dict): Provider configuration

**Returns:** `List[str]` - List of configuration issues

## Error Handling

### Common Exceptions

#### `ConfigurationError`

Raised for configuration-related issues.

```python
from peircean.config import PeirceanConfig, ConfigurationError

try:
    config = PeirceanConfig()
    issues = config.validate_config()
    if issues:
        raise ConfigurationError(f"Configuration invalid: {', '.join(issues)}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

#### `ProviderError`

Raised for provider-related issues.

```python
from peircean.providers import get_provider_client
from peircean.config import get_config

try:
    config = get_config()
    client = get_provider_client(config.provider.value, config.get_provider_config())

    if not client or not client.is_available():
        raise ProviderError(f"Provider {config.provider.value} not available")

except ProviderError as e:
    print(f"Provider error: {e}")
```

### Validation Patterns

#### Configuration Validation

```python
from peircean.config import get_config
from peircean.utils.env import validate_environment

def validate_setup():
    """Validate complete setup."""
    config = get_config()

    # Validate configuration
    config_issues = config.validate_config()
    if config_issues:
        print("❌ Configuration issues:")
        for issue in config_issues:
            print(f"  • {issue}")
        return False

    # Validate environment
    env_validation = validate_environment()
    if not env_validation["valid"]:
        print("❌ Environment issues:")
        for issue in env_validation["issues"]:
            print(f"  • {issue}")
        return False

    print("✅ Setup is valid")
    return True
```

#### Provider Validation

```python
from peircean.providers import get_provider_client, get_provider_registry
from peircean.config import get_config

def validate_provider():
    """Validate provider setup."""
    config = get_config()
    registry = get_provider_registry()

    # Check provider support
    provider_info = registry.get_provider_info(config.provider.value)
    if not provider_info:
        print(f"❌ Unknown provider: {config.provider.value}")
        return False

    # Check provider availability
    provider_config = config.get_provider_config()
    client = get_provider_client(config.provider.value, provider_config)

    if not client:
        print("❌ Provider client not available")
        return False

    if not client.is_available():
        print("❌ Provider not properly configured")
        return False

    print(f"✅ Provider {config.provider.value} is available")
    return True
```

## Integration Examples

### Python API Usage

```python
from peircean import PeirceanAbduction, PeirceanConfig, Provider

# Custom configuration
config = PeirceanConfig(
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20241022",
    temperature=0.8,
    enable_council=True
)

# Initialize abduction
abduction = PeirceanAbduction(config=config)

# Perform analysis
result = abduction.analyze(
    observation="Customer churn increased while satisfaction scores improved",
    domain="business",
    num_hypotheses=5,
    use_council=True
)

print(f"Best hypothesis: {result.best_hypothesis}")
print(f"Confidence: {result.confidence}")
print(f"Recommended actions: {result.recommended_actions}")
```

### Configuration Management

```python
from peircean.config import get_config, reload_config
from peircean.utils.env import validate_environment
import os

def setup_provider(provider_name: str, api_key: str):
    """Setup and validate provider configuration."""

    # Set environment variables
    os.environ["PEIRCEAN_PROVIDER"] = provider_name
    os.environ["PEIRCEAN_API_KEY"] = api_key

    # Reload configuration
    config = reload_config()

    # Validate setup
    env_validation = validate_environment()

    if env_validation["valid"]:
        print(f"✅ {provider_name} provider configured successfully")
        print(f"Model: {config.model}")
        print(f"Council enabled: {config.enable_council}")
        return True
    else:
        print("❌ Configuration issues found:")
        for issue in env_validation["issues"]:
            print(f"  • {issue}")
        return False
```

### Provider Integration

```python
from peircean.providers import get_provider_client, get_provider_registry
from peircean.config import get_config

def test_provider_functionality():
    """Test provider functionality."""

    config = get_config()
    registry = get_provider_registry()

    # List all available providers
    providers = registry.get_available_providers()
    print(f"Available providers: {providers}")

    # Test current provider
    if config.provider.value in providers:
        provider_config = config.get_provider_config()
        client = get_provider_client(config.provider.value, provider_config)

        if client and client.is_available():
            print(f"✅ {config.provider.value} is working")

            # Test prompt generation (always works)
            prompt = client.generate_prompt(
                observation="Test observation",
                domain="general"
            )
            print(f"Generated prompt length: {len(prompt)} characters")

            # Test completion (only if interactive mode enabled)
            if config.interactive_mode:
                completion = client.generate_completion(prompt)
                if completion:
                    print(f"✅ Completion generated successfully")
                else:
                    print("❌ Failed to generate completion")
            else:
                print("ℹ️  Interactive mode disabled - no completion generated")
        else:
            print(f"❌ {config.provider.value} not available")
    else:
        print(f"❌ {config.provider.value} not supported")
```

## Related Documentation

- [**Configuration Guide**](../guides/configuration.md) - Environment variables and setup
- [**Installation Guide**](../getting-started/installation.md) - Platform-specific installation
- [**Quick Start**](../getting-started/quickstart.md) - Get up and running in 5 minutes
- [**MCP Integration Guide**](../guides/mcp-integration.md) - IDE setup and usage
- [**User Guide**](../guides/user-guide.md) - Comprehensive usage examples

## Performance Testing

For performance testing and benchmarking, use the built-in benchmark suite:

```bash
# Run all standard benchmarks
peircean-bench

# Run quick scenarios only
peircean-bench --quick

# Test specific domain
peircean-bench --domain financial

# Test provider availability
peircean-bench --providers

# Export results
peircean-bench --export-json benchmark-results.json
```

See [CLI Reference](../README.md#cli-reference) for complete benchmark command options.

---

**Pro Tip**: The API is designed to work seamlessly in both prompt-only mode (default, like Hegelion) and interactive mode. All provider clients can generate prompts without requiring API keys or network access. Interactive features are only enabled when explicitly configured via `PEIRCEAN_INTERACTIVE_MODE=true`.