# Continuation: Improve Test Coverage

## Current State
- 106 tests passing, 73% overall coverage
- Last commit: `feat!: add peircean_ prefix to all MCP tools`

## Priority Coverage Gaps

### 1. peircean/mcp/setup.py (18% → 80%+)
- Test `create_parser()` argument parsing
- Test `get_config()` JSON generation
- Test `write_config()` file operations (use tmp_path fixture)
- Test `main()` entry point with mocked file system
- Lines needing coverage: 24-35, 40, 47-55, 70-99, 104-138

### 2. peircean/core/agent.py (67% → 80%+)
- Mock LLM calls to test `AbductiveAgent` flows
- Test `_parse_llm_response()` with various inputs
- Test async methods with pytest-asyncio
- Lines needing coverage: 234-284, 456-482, 494-506

### 3. peircean/training/generator.py (75% → 85%+)
- Test `main()` CLI entry point
- Test edge cases in batch generation
- Lines needing coverage: 310-337

## Files to Create/Extend
- `tests/test_setup.py` (new - for mcp/setup.py)
- `tests/test_core.py` (extend - for agent.py)
- `tests/test_training.py` (extend - for generator.py)

## Target
80%+ overall coverage

## Verification Commands
```bash
python -m pytest tests/ --cov --cov-report=term-missing
python -m ruff check .
python -m mypy peircean/
```
