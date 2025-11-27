# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-27

### Added
- Custom council support for domain-specific anomalies
- `custom_council` parameter in `peircean_evaluate_via_ibe`
- `recommended_council` field in Phase 1 output
- Automated PyPI publishing via GitHub Actions with OIDC Trusted Publishing
- Comprehensive documentation reorganization

### Changed
- Reorganized docs into `getting-started/`, `guides/`, `concepts/`, `examples/` structure
- Improved test robustness via dependency injection
- Updated tool function annotations for FastMCP compatibility

### Fixed
- Resolved ruff B010 and I001 linting errors
- Fixed mypy type errors in test suite
- Corrected tool annotation attachment in FastMCP

## [0.1.0] - Initial Release

### Added
- Core `AbductionAgent` with 3-phase workflow (Observe, Generate, Evaluate)
- MCP server integration via FastMCP
- 5 MCP tools:
  - `peircean_observe_anomaly` - Phase 1: Register surprising facts
  - `peircean_generate_hypotheses` - Phase 2: Generate explanatory hypotheses
  - `peircean_evaluate_via_ibe` - Phase 3: Inference to Best Explanation
  - `peircean_abduce_single_shot` - All phases in one call
  - `peircean_critic_evaluate` - Individual critic perspective
- Council of Critics evaluation (Empiricist, Logician, Pragmatist, Economist, Skeptic)
- 6 domain templates: general, financial, legal, medical, technical, scientific
- IBE selection criteria with configurable weights
- CLI interface (`peircean` command)
- Auto-configuration for Claude Desktop, Cursor, VS Code, Claude Code CLI
- Prompt-only mode for use with any LLM
- JSON and Markdown output formats
