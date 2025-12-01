# Installation Guide

Complete installation guide for Peircean Abduction with platform-specific setup, virtual environments, and first-run verification.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Setup](#platform-specific-setup)
- [Virtual Environments](#virtual-environments)
- [Provider Dependencies](#provider-dependencies)
- [First-Run Verification](#first-run-verification)
- [MCP Integration Setup](#mcp-integration-setup)
- [Troubleshooting Installation](#troubleshooting-installation)
- [Upgrading](#upgrading)

## System Requirements

### Minimum Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Memory**: 4GB RAM minimum (8GB+ recommended)
- **Storage**: 100MB free disk space

### Supported Platforms

| Platform | Versions Tested | Architecture |
|----------|------------------|--------------|
| **macOS** | 10.15+ (Catalina and newer) | x86-64, Apple Silicon |
| **Linux** | Ubuntu 20.04+, RHEL 8+, Debian 11+ | x86-64, ARM64 |
| **Windows** | Windows 10+ | x86-64 |

### Optional Dependencies

- **Git**: For cloning repository (development)
- **IDE**: Claude Desktop, Cursor, or Continue.dev for MCP integration
- **LLM Provider Account**: Anthropic, OpenAI, Google, or local Ollama

## Installation Methods

### Method 1: PyPI Installation (Recommended)

#### Core Installation

```bash
# Install core package
pip install peircean-abduction
```

#### With Provider Support

```bash
# Install with all providers
pip install peircean-abduction[all]

# Or install specific providers
pip install peircean-abduction[anthropic]  # Anthropic Claude
pip install peircean-abduction[openai]      # OpenAI GPT
pip install peircean-abduction[gemini]     # Google Gemini
pip install peircean-abduction[ollama]     # Local Ollama
```

#### Development Installation

```bash
# Clone repository
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction

# Install in development mode
pip install -e .[dev]
```

### Method 2: Package Managers

#### pipx (Isolated Installation)

```bash
# Install pipx (if not already installed)
pip install --user pipx

# Install peircean-abduction in isolated environment
pipx install peircean-abduction
pipx inject peircean-abduction peircean-abduction[all]

# Run commands
peircean --help
```

#### Conda/Mamba

```bash
# Using conda-forge (if available)
conda install -c conda-forge peircean-abduction

# Or create conda environment with pip
conda create -n peircean python=3.11
conda activate peircean
pip install peircean-abduction[all]
```

## Platform-Specific Setup

### macOS

#### Using Homebrew

```bash
# Install Python (if not already installed)
brew install python@3.11

# Install peircean-abduction
pip3 install peircean-abduction[all]

# Add to PATH (if needed)
echo 'export PATH="$HOME/Library/Python/3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Using MacPorts

```bash
# Install Python
sudo port install python311

# Install peircean-abduction
port select --set python3 python311
pip3 install peircean-abduction[all]
```

### Linux

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install peircean-abduction
pip3 install --user peircean-abduction[all]

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### RHEL/CentOS/Fedora

```bash
# RHEL/CentOS
sudo yum install python3.11 python3.11-pip

# Fedora
sudo dnf install python3.11 python3.11-pip

# Install peircean-abduction
pip3.11 install --user peircean-abduction[all]
```

#### Arch Linux

```bash
# Install Python
sudo pacman -S python python-pip

# Install peircean-abduction
pip install peircean-abduction[all]
```

### Windows

#### Using PowerShell

```powershell
# Check Python installation
python --version
pip --version

# Install peircean-abuction
pip install peircean-abduction[all]

# Add to PATH (if needed)
echo $env:PATH
```

#### Using Chocolatey

```powershell
# Install Python (if not installed)
choco install python

# Install peircean-abduction
pip install peircean-abduction[all]
```

#### Using Windows Subsystem for Linux (WSL)

```bash
# In WSL terminal
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

pip3 install peircean-abduction[all]
```

## Virtual Environments

### Using venv

```bash
# Create virtual environment
python -m venv peircean-env

# Activate environment
# On macOS/Linux:
source peircean-env/bin/activate
# On Windows:
peircean-env\Scripts\activate

# Install peircean-abduction
pip install peircean-abduction[all]

# Deactivate when done
deactivate
```

### Using virtualenv

```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv peircean-env

# Activate
source peircean-env/bin/activate  # macOS/Linux
# or
peircean-env\Scripts\activate     # Windows

# Install
pip install peircean-abduction[all]
```

### Using conda

```bash
# Create conda environment
conda create -n peircean python=3.11

# Activate
conda activate peircean

# Install
pip install peircean-abduction[all]
```

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install peircean-abduction
RUN pip install peircean-abduction[all]

# Copy your application
COPY . .

# Run peircean command
CMD ["peircean", "--help"]
```

```bash
# Build and run
docker build -t peircean-app .
docker run -it --rm peircean-app
```

## Provider Dependencies

### Anthropic Claude

```bash
# Install Anthropic provider
pip install peircean-abduction[anthropic]

# Or separately
pip install anthropic>=0.18

# Set environment variable
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export PEIRCEAN_API_KEY="sk-ant-..."
```

### OpenAI GPT

```bash
# Install OpenAI provider
pip install peircean-abduction[openai]

# Or separately
pip install openai>=1.0

# Set environment variable
export OPENAI_API_KEY="sk-..."
# or
export PEIRCEAN_API_KEY="sk-..."
```

### Google Gemini

```bash
# Install Gemini provider
pip install peircean-abduction[gemini]

# Or separately
pip install google-generativeai>=0.3.0

# Set environment variable
export GEMINI_API_KEY="your_gemini_api_key"
# or
export PEIRCEAN_API_KEY="your_gemini_api_key"
```

### Ollama (Local)

```bash
# Install Ollama provider
pip install peircean-abduction[ollama]

# Or separately
pip install ollama>=0.1.0

# Install and run Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# Pull a model
ollama pull llama2

# Set environment variable
export OLLAMA_HOST="http://localhost:11434"
# or
export PEIRCEAN_BASE_URL="http://localhost:11434"
```

### All Providers

```bash
# Install all provider dependencies
pip install peircean-abduction[all]

# This installs:
# - anthropic>=0.18
# - openai>=1.0
# - google-generativeai>=0.3.0
# - ollama>=0.1.0
# - mcp>=1.0.0 (for MCP integration)
```

## First-Run Verification

### Basic Installation Check

```bash
# Verify installation
peircean --version
# Expected: peircean-abduction 1.2.0

# Check help
peircean --help
```

### System Verification

```bash
# Comprehensive system check
peircean --verify

# JSON output for automation
peircean --verify --json | jq .
```

**Expected Output:**
```
✅ Python version: 3.11.x
✅ Required dependencies installed
✅ Optional dependencies available
⚠️  Provider configuration needed
📝 Environment: .env file not found
```

### Configuration Verification

```bash
# Show current configuration
peircean config show

# Validate configuration
peircean config validate

# List available providers
peircean config providers
```

### Test Prompt Generation

```bash
# Test basic prompt generation (works without API keys)
peircean --prompt "The stock market dropped 5% on good news"

# Test with specific domain
peircean --domain technical --prompt "Server latency increased but CPU is flat"
```

### Test MCP Server

```bash
# Test MCP server installation
peircean-server --help

# Test MCP setup (no writes)
peircean-setup-mcp --json
```

## MCP Integration Setup

### Automatic Setup

```bash
# Auto-configure Claude Desktop
peircean --install

# Auto-configure Cursor
peircean-setup-mcp --ide cursor --write

# Auto-configure Continue.dev
peircean-setup-mcp --ide continue-dev --write
```

### Manual Configuration

#### Claude Desktop

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)
// ~/.config/Claude/claude_desktop_config.json (Linux)

{
  "mcpServers": {
    "peircean-abduction": {
      "command": "peircean-server",
      "args": [],
      "env": {
        "PEIRCEAN_PROVIDER": "anthropic",
        "PEIRCEAN_MODEL": "claude-3-sonnet-20241022"
      }
    }
  }
}
```

#### Cursor

```json
// ~/.cursor/mcp_servers.json

{
  "mcpServers": {
    "peircean-abduction": {
      "command": "peircean-server",
      "args": []
    }
  }
}
```

#### Continue.dev

```json
// ~/.continue/config.json

{
  "experimental": {
    "mcp": true
  },
  "mcpServers": {
    "peircean-abduction": {
      "command": "peircean-server",
      "args": []
    }
  }
}
```

### Verify MCP Integration

1. **Restart your IDE** after configuration
2. **Check for tools**: Look for the 🔌 icon or Peircean tools
3. **Test functionality**: Try a simple abductive analysis

## Troubleshooting Installation

### Common Issues

#### Python Version Incompatibility

```bash
# Check Python version
python --version

# If below 3.10, upgrade Python
# On macOS with Homebrew:
brew install python@3.11

# On Ubuntu:
sudo apt install python3.11
```

#### Permission Denied Errors

```bash
# Use --user flag
pip install --user peircean-abduction[all]

# Or use virtual environment
python -m venv peircean-env
source peircean-env/bin/activate
pip install peircean-abduction[all]
```

#### PATH Issues

```bash
# Check Python script location
python -c "import site; print(site.USER_BASE + '/bin')"

# Add to PATH (macOS/Linux)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# On Windows, add Python Scripts to PATH manually
```

#### Provider Import Errors

```bash
# Install specific provider
pip install peircean-abduction[anthropic]  # or [openai], [gemini], [ollama]

# Or install provider directly
pip install anthropic  # or openai, google-generativeai, ollama
```

#### MCP Server Not Found

```bash
# Check if peircean-server is available
which peircean-server
peircean-server --help

# Reinstall with proper entry points
pip install --force-reinstall peircean-abduction
```

### Platform-Specific Issues

#### macOS: Command Line Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install

# If issues persist, reinstall Python
brew reinstall python@3.11
```

#### Linux: Missing Development Headers

```bash
# Ubuntu/Debian
sudo apt install python3.11-dev build-essential

# RHEL/CentOS
sudo yum install python3.11-devel gcc
sudo dnf install python3.11-devel gcc
```

#### Windows: Long Path Issues

```powershell
# Enable long path support in Windows
# Run as Administrator in PowerShell
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

### Verification Commands

```bash
# Check all installations
python -c "import peircean; print('✅ Core package works')"
python -c "from peircean.providers import get_provider_registry; print('✅ Providers work')"
python -c "from peircean.config import get_config; print('✅ Configuration works')"

# Test entry points
peircean --version
peircean-server --help
peircean-setup-mcp --help

# Validate environment
peircean config validate
peircean --verify
```

## Upgrading

### Upgrade from PyPI

```bash
# Upgrade to latest version
pip install --upgrade peircean-abduction

# Upgrade with all providers
pip install --upgrade peircean-abduction[all]

# Force upgrade
pip install --upgrade --force-reinstall peircean-abduction[all]
```

### Development Version

```bash
# Clone latest source
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction

# Install development version
pip install -e .[dev]
```

### Migration from v1.1.x to v1.2.0

The v1.2.0 release introduced major configuration improvements. See the [Configuration Guide](../guides/configuration.md#migration-from-v11x-to-v120) for migration instructions.

```bash
# Run migration check
peircean config validate

# If issues found, run configuration wizard
peircean config wizard
```

## Next Steps

After successful installation:

1. **Configure Provider**: Set up your preferred LLM provider
   ```bash
   peircean config wizard
   ```

2. **Test Functionality**: Verify prompt generation works
   ```bash
   peircean --prompt "Test observation"
   ```

3. **Setup MCP Integration**: Configure for your IDE
   ```bash
   peircean --install
   ```

4. **Read Documentation**: Explore user guides and examples
   - [User Guide](../guides/user-guide.md) - Complete usage documentation
   - [Configuration Guide](../guides/configuration.md) - Detailed configuration options
   - [MCP Integration](../guides/mcp-integration.md) - IDE setup instructions
   - [API Reference](../reference/api.md) - Complete API documentation

5. **Join Community**: Get help and share experiences
   - [GitHub Issues](https://github.com/Hmbown/peircean-abduction/issues) - Bug reports and feature requests
   - [Discussions](https://github.com/Hmbown/peircean-abduction/discussions) - Community discussions

---

**Pro Tip**: Start with prompt-only mode (default) to get familiar with Peircean Abduction without requiring API keys. You can always enable interactive mode later by setting `PEIRCEAN_INTERACTIVE_MODE=true` or running `peircean config wizard`.