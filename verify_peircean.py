#!/usr/bin/env python3
"""
Peircean Verification Script

Tests that the Peircean Logic Harness MCP server is correctly configured:
- All tools are registered
- Each phase returns valid prompt structure
- Error handling works
- Tool descriptions contain examples

Usage:
    python verify_peircean.py
    python -m verify_peircean
"""

from __future__ import annotations

import json
import sys
from typing import Any

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

REQUIRED_TOOLS = [
    "observe_anomaly",
    "generate_hypotheses",
    "evaluate_via_ibe",
    "abduce_single_shot",
    "critic_evaluate",
]

REQUIRED_DOCSTRING_ELEMENTS = [
    "Example:",
    "Args:",
    "Returns:",
]

EXAMPLE_ANOMALY = {
    "anomaly": {
        "fact": "Server latency spiked 10x but CPU/memory normal",
        "surprise_level": "high",
        "surprise_score": 0.85,
        "expected_baseline": "Latency correlates with resource usage",
        "domain": "technical",
        "context": ["No recent deployments", "Traffic is steady"],
        "key_features": ["Latency spike", "Normal CPU", "Normal memory"],
        "surprise_source": "Violates expected correlation"
    }
}

EXAMPLE_HYPOTHESES = {
    "hypotheses": [
        {
            "id": "H1",
            "statement": "Database connection pool exhaustion",
            "explains_anomaly": "If DB connections are exhausted, requests queue causing latency",
            "prior_probability": 0.35,
            "assumptions": [{"statement": "DB is bottleneck", "testable": True}],
            "testable_predictions": [
                {
                    "prediction": "DB connection count at max",
                    "test_method": "Check connection pool metrics",
                    "if_true": "Supports H1",
                    "if_false": "Weakens H1"
                }
            ]
        },
        {
            "id": "H2",
            "statement": "Network partition to dependent service",
            "explains_anomaly": "Network issues cause timeouts without CPU load",
            "prior_probability": 0.25,
            "assumptions": [{"statement": "Dependent service exists", "testable": True}],
            "testable_predictions": [
                {
                    "prediction": "Network errors in logs",
                    "test_method": "Check application logs",
                    "if_true": "Supports H2",
                    "if_false": "Weakens H2"
                }
            ]
        }
    ]
}


# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestResult:
    """Container for test results."""

    def __init__(self, name: str):
        self.name = name
        self.passed = True
        self.messages: list[str] = []

    def fail(self, message: str) -> None:
        self.passed = False
        self.messages.append(f"FAIL: {message}")

    def ok(self, message: str) -> None:
        self.messages.append(f"OK: {message}")

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        result = f"\n[{status}] {self.name}\n"
        for msg in self.messages:
            result += f"  {msg}\n"
        return result


def print_header(text: str) -> None:
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")


# =============================================================================
# TESTS
# =============================================================================

def test_imports() -> TestResult:
    """Test that all modules can be imported."""
    result = TestResult("Module Imports")

    try:
        from peircean.mcp.server import mcp, SYSTEM_DIRECTIVE
        result.ok("peircean.mcp.server imports successfully")
    except ImportError as e:
        result.fail(f"Cannot import peircean.mcp.server: {e}")
        return result

    try:
        from peircean.core.models import Domain, SurpriseLevel, Hypothesis
        result.ok("peircean.core.models imports successfully")
    except ImportError as e:
        result.fail(f"Cannot import peircean.core.models: {e}")

    try:
        from peircean.core.prompts import DOMAIN_GUIDANCE
        result.ok("peircean.core.prompts imports successfully")
    except ImportError as e:
        result.fail(f"Cannot import peircean.core.prompts: {e}")

    return result


def test_tool_registration() -> TestResult:
    """Test that all required tools are registered."""
    result = TestResult("Tool Registration")

    try:
        from peircean.mcp.server import mcp

        # Get registered tools
        # FastMCP stores tools in _tool_manager
        if hasattr(mcp, '_tool_manager'):
            tools = mcp._tool_manager._tools
            registered = list(tools.keys())
        elif hasattr(mcp, 'tools'):
            registered = list(mcp.tools.keys())
        else:
            # Try to get tools via list_tools
            result.fail("Cannot access registered tools - FastMCP API may have changed")
            return result

        result.ok(f"Found {len(registered)} registered tools: {registered}")

        for tool_name in REQUIRED_TOOLS:
            if tool_name in registered:
                result.ok(f"Tool '{tool_name}' is registered")
            else:
                result.fail(f"Required tool '{tool_name}' is NOT registered")

    except Exception as e:
        result.fail(f"Error checking tool registration: {e}")

    return result


def test_tool_docstrings() -> TestResult:
    """Test that tool docstrings contain required elements."""
    result = TestResult("Tool Docstrings")

    try:
        from peircean.mcp import server

        tools_to_check = [
            ("observe_anomaly", server.observe_anomaly),
            ("generate_hypotheses", server.generate_hypotheses),
            ("evaluate_via_ibe", server.evaluate_via_ibe),
            ("abduce_single_shot", server.abduce_single_shot),
            ("critic_evaluate", server.critic_evaluate),
        ]

        for tool_name, tool_func in tools_to_check:
            docstring = tool_func.__doc__ or ""

            for element in REQUIRED_DOCSTRING_ELEMENTS:
                if element in docstring:
                    result.ok(f"'{tool_name}' contains '{element}'")
                else:
                    result.fail(f"'{tool_name}' missing '{element}' in docstring")

            # Check for phase flow indication
            if "Phase" in docstring or "PHASE" in docstring or "phase" in docstring:
                result.ok(f"'{tool_name}' documents phase flow")
            elif tool_name == "critic_evaluate":
                result.ok(f"'{tool_name}' is council tool (no phase required)")
            else:
                result.fail(f"'{tool_name}' missing phase flow documentation")

    except Exception as e:
        result.fail(f"Error checking docstrings: {e}")

    return result


def test_observe_anomaly() -> TestResult:
    """Test the observe_anomaly tool."""
    result = TestResult("observe_anomaly Tool")

    try:
        from peircean.mcp.server import observe_anomaly

        # Test basic call
        output = observe_anomaly(
            observation="Server latency spiked 10x but CPU/memory normal",
            context="No recent deployments",
            domain="technical"
        )

        # Parse output
        data = json.loads(output)

        if "type" in data and data["type"] == "prompt":
            result.ok("Returns prompt type")
        else:
            result.fail("Does not return prompt type")

        if "phase" in data and data["phase"] == 1:
            result.ok("Indicates phase 1")
        else:
            result.fail("Does not indicate phase 1")

        if "prompt" in data and len(data["prompt"]) > 100:
            result.ok(f"Contains prompt text ({len(data['prompt'])} chars)")
        else:
            result.fail("Missing or short prompt text")

        if "next_tool" in data and data["next_tool"] == "generate_hypotheses":
            result.ok("Indicates next tool")
        else:
            result.fail("Does not indicate next tool")

        # Check prompt contains SYSTEM DIRECTIVE
        if "SYSTEM DIRECTIVE" in data.get("prompt", ""):
            result.ok("Prompt contains SYSTEM DIRECTIVE")
        else:
            result.fail("Prompt missing SYSTEM DIRECTIVE")

        # Check prompt contains JSON schema
        if "```json" in data.get("prompt", ""):
            result.ok("Prompt contains JSON schema")
        else:
            result.fail("Prompt missing JSON schema")

    except Exception as e:
        result.fail(f"Error testing observe_anomaly: {e}")

    return result


def test_generate_hypotheses() -> TestResult:
    """Test the generate_hypotheses tool."""
    result = TestResult("generate_hypotheses Tool")

    try:
        from peircean.mcp.server import generate_hypotheses

        # Test with valid anomaly JSON
        anomaly_json = json.dumps(EXAMPLE_ANOMALY)
        output = generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=3)

        data = json.loads(output)

        if "type" in data and data["type"] == "prompt":
            result.ok("Returns prompt type")
        else:
            result.fail("Does not return prompt type")

        if "phase" in data and data["phase"] == 2:
            result.ok("Indicates phase 2")
        else:
            result.fail("Does not indicate phase 2")

        if "next_tool" in data and data["next_tool"] == "evaluate_via_ibe":
            result.ok("Indicates next tool")
        else:
            result.fail("Does not indicate next tool")

        # Test error handling with invalid JSON
        error_output = generate_hypotheses(anomaly_json="not valid json", num_hypotheses=3)
        error_data = json.loads(error_output)

        if "error" in error_data:
            result.ok("Handles invalid JSON gracefully")
        else:
            result.fail("Does not handle invalid JSON")

    except Exception as e:
        result.fail(f"Error testing generate_hypotheses: {e}")

    return result


def test_evaluate_via_ibe() -> TestResult:
    """Test the evaluate_via_ibe tool."""
    result = TestResult("evaluate_via_ibe Tool")

    try:
        from peircean.mcp.server import evaluate_via_ibe

        anomaly_json = json.dumps(EXAMPLE_ANOMALY)
        hypotheses_json = json.dumps(EXAMPLE_HYPOTHESES)

        # Test without council
        output = evaluate_via_ibe(
            anomaly_json=anomaly_json,
            hypotheses_json=hypotheses_json,
            use_council=False
        )

        data = json.loads(output)

        if "type" in data and data["type"] == "prompt":
            result.ok("Returns prompt type")
        else:
            result.fail("Does not return prompt type")

        if "phase" in data and data["phase"] == 3:
            result.ok("Indicates phase 3 (final)")
        else:
            result.fail("Does not indicate phase 3")

        if "next_tool" in data and data["next_tool"] is None:
            result.ok("Indicates no next tool (terminal)")
        else:
            result.fail("Does not indicate terminal phase")

        # Test with council
        council_output = evaluate_via_ibe(
            anomaly_json=anomaly_json,
            hypotheses_json=hypotheses_json,
            use_council=True
        )

        council_data = json.loads(council_output)
        prompt = council_data.get("prompt", "")

        if "Council of Critics" in prompt:
            result.ok("Council mode includes critic evaluation")
        else:
            result.fail("Council mode missing critic evaluation")

    except Exception as e:
        result.fail(f"Error testing evaluate_via_ibe: {e}")

    return result


def test_critic_evaluate() -> TestResult:
    """Test the critic_evaluate tool."""
    result = TestResult("critic_evaluate Tool")

    try:
        from peircean.mcp.server import critic_evaluate

        anomaly_json = json.dumps(EXAMPLE_ANOMALY)
        hypotheses_json = json.dumps(EXAMPLE_HYPOTHESES)

        valid_critics = ["empiricist", "logician", "pragmatist", "economist", "skeptic"]

        for critic in valid_critics:
            output = critic_evaluate(
                critic=critic,
                anomaly_json=anomaly_json,
                hypotheses_json=hypotheses_json
            )

            data = json.loads(output)

            if "type" in data and data["type"] == "prompt":
                result.ok(f"Critic '{critic}' returns prompt")
            else:
                result.fail(f"Critic '{critic}' does not return prompt")

            if "critic" in data and data["critic"] == critic:
                result.ok(f"Critic '{critic}' identified correctly")
            else:
                result.fail(f"Critic '{critic}' not identified")

        # Test invalid critic
        invalid_output = critic_evaluate(
            critic="invalid_critic",
            anomaly_json=anomaly_json,
            hypotheses_json=hypotheses_json
        )

        invalid_data = json.loads(invalid_output)
        if "error" in invalid_data:
            result.ok("Invalid critic handled gracefully")
        else:
            result.fail("Invalid critic not handled")

    except Exception as e:
        result.fail(f"Error testing critic_evaluate: {e}")

    return result


def test_single_shot() -> TestResult:
    """Test the abduce_single_shot tool."""
    result = TestResult("abduce_single_shot Tool")

    try:
        from peircean.mcp.server import abduce_single_shot

        output = abduce_single_shot(
            observation="Customer churn rate doubled in Q3",
            context="No price changes, NPS stable",
            domain="financial",
            num_hypotheses=3
        )

        data = json.loads(output)

        if "type" in data and data["type"] == "prompt":
            result.ok("Returns prompt type")
        else:
            result.fail("Does not return prompt type")

        if "phase" in data and data["phase"] == "single_shot":
            result.ok("Indicates single-shot mode")
        else:
            result.fail("Does not indicate single-shot mode")

        prompt = data.get("prompt", "")

        if "Phase 1" in prompt and "Phase 2" in prompt and "Phase 3" in prompt:
            result.ok("Prompt covers all three phases")
        else:
            result.fail("Prompt missing phase coverage")

        if "SYSTEM DIRECTIVE" in prompt:
            result.ok("Prompt contains SYSTEM DIRECTIVE")
        else:
            result.fail("Prompt missing SYSTEM DIRECTIVE")

    except Exception as e:
        result.fail(f"Error testing abduce_single_shot: {e}")

    return result


def test_logging_configuration() -> TestResult:
    """Test that logging is configured for stderr."""
    result = TestResult("Logging Configuration")

    try:
        from peircean.mcp.server import logger
        import logging

        # Check logger exists
        if logger:
            result.ok("Logger is configured")
        else:
            result.fail("Logger not found")

        # Check handler outputs to stderr
        handlers = logger.handlers or logging.getLogger().handlers

        stderr_handler_found = False
        for handler in handlers:
            if isinstance(handler, logging.StreamHandler):
                if handler.stream == sys.stderr:
                    stderr_handler_found = True
                    result.ok("Logger outputs to stderr")
                elif handler.stream == sys.stdout:
                    result.fail("Logger outputs to stdout (CRITICAL: will break MCP)")

        if not stderr_handler_found and not handlers:
            # Check root logger
            root_handlers = logging.root.handlers
            for handler in root_handlers:
                if isinstance(handler, logging.StreamHandler):
                    if handler.stream == sys.stderr:
                        stderr_handler_found = True
                        result.ok("Root logger outputs to stderr")

        if not stderr_handler_found:
            result.fail("No stderr handler found")

    except Exception as e:
        result.fail(f"Error checking logging: {e}")

    return result


def test_system_directive() -> TestResult:
    """Test that SYSTEM_DIRECTIVE is properly defined."""
    result = TestResult("SYSTEM_DIRECTIVE")

    try:
        from peircean.mcp.server import SYSTEM_DIRECTIVE

        if SYSTEM_DIRECTIVE and len(SYSTEM_DIRECTIVE) > 100:
            result.ok(f"SYSTEM_DIRECTIVE defined ({len(SYSTEM_DIRECTIVE)} chars)")
        else:
            result.fail("SYSTEM_DIRECTIVE not properly defined")

        if "FORBIDDEN" in SYSTEM_DIRECTIVE:
            result.ok("Contains FORBIDDEN section")
        else:
            result.fail("Missing FORBIDDEN section")

        if "REQUIRED" in SYSTEM_DIRECTIVE:
            result.ok("Contains REQUIRED section")
        else:
            result.fail("Missing REQUIRED section")

        if "JSON" in SYSTEM_DIRECTIVE:
            result.ok("Mentions JSON output requirement")
        else:
            result.fail("Does not mention JSON output requirement")

    except ImportError:
        result.fail("Cannot import SYSTEM_DIRECTIVE")
    except Exception as e:
        result.fail(f"Error checking SYSTEM_DIRECTIVE: {e}")

    return result


# =============================================================================
# MAIN
# =============================================================================

def main() -> int:
    """Run all verification tests."""
    print_header("Peircean Logic Harness Verification")
    print("A Logic Harness for abductive inference. Anomaly in → Hypothesis out.")

    tests = [
        test_imports,
        test_tool_registration,
        test_tool_docstrings,
        test_observe_anomaly,
        test_generate_hypotheses,
        test_evaluate_via_ibe,
        test_critic_evaluate,
        test_single_shot,
        test_logging_configuration,
        test_system_directive,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print(result)

    # Summary
    print_header("Summary")

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n[SUCCESS] All verification tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
