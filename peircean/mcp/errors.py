"""
Peircean MCP Server: Error Handling

Structured error responses following MCP best practices.
Errors are returned within result objects (not protocol-level)
to allow LLMs to see and potentially handle them.
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from pydantic import ValidationError


class ErrorCode(str, Enum):
    """Standardized error codes for MCP tools."""

    # Input validation errors
    VALIDATION_ERROR = "validation_error"
    INVALID_JSON = "invalid_json"
    MISSING_FIELD = "missing_field"
    INVALID_VALUE = "invalid_value"

    # Processing errors
    PROCESSING_ERROR = "processing_error"
    TIMEOUT = "timeout"

    # Configuration errors
    CONFIGURATION_ERROR = "configuration_error"


def format_error_response(
    error: str,
    code: ErrorCode = ErrorCode.VALIDATION_ERROR,
    hint: str | None = None,
    details: dict[str, Any] | None = None,
) -> str:
    """
    Format a standardized error response for MCP tools.

    Error responses are returned as JSON within the tool result,
    allowing LLMs to understand and potentially recover from errors.

    Args:
        error: Human-readable error message describing what went wrong.
        code: Error code for categorization.
        hint: Actionable suggestion for how to fix the error.
        details: Additional structured details about the error.

    Returns:
        JSON string with standardized error format.

    Example:
        >>> format_error_response(
        ...     "Invalid JSON in anomaly_json parameter",
        ...     code=ErrorCode.INVALID_JSON,
        ...     hint="Pass the raw JSON output from peircean_observe_anomaly",
        ...     details={"parameter": "anomaly_json"}
        ... )
    """
    response: dict[str, Any] = {
        "type": "error",
        "error": error,
        "code": code.value,
    }
    if hint:
        response["hint"] = hint
    if details:
        response["details"] = details
    return json.dumps(response, indent=2)


def format_validation_error(validation_error: ValidationError) -> str:
    """
    Format a Pydantic ValidationError into a user-friendly MCP error response.

    Extracts field-specific errors and provides actionable hints.

    Args:
        validation_error: The Pydantic validation exception.

    Returns:
        JSON string with detailed validation error information.
    """
    errors = validation_error.errors()

    # Build a summary of what went wrong
    error_messages = []
    field_hints = []

    for err in errors:
        loc = ".".join(str(x) for x in err["loc"])
        msg = err["msg"]
        error_messages.append(f"{loc}: {msg}")

        # Generate field-specific hints
        if "observation" in loc:
            field_hints.append(
                "Provide a non-empty observation describing the surprising fact"
            )
        elif "anomaly_json" in loc:
            field_hints.append(
                "Pass the JSON output from peircean_observe_anomaly (Phase 1)"
            )
        elif "hypotheses_json" in loc:
            field_hints.append(
                "Pass the JSON output from peircean_generate_hypotheses (Phase 2)"
            )
        elif "num_hypotheses" in loc:
            field_hints.append("Use a value between 1 and 20 for num_hypotheses")
        elif "domain" in loc:
            field_hints.append(
                "Use one of: general, financial, legal, medical, technical, scientific"
            )

    # Deduplicate hints
    unique_hints = list(dict.fromkeys(field_hints))

    return format_error_response(
        error=f"Input validation failed: {'; '.join(error_messages)}",
        code=ErrorCode.VALIDATION_ERROR,
        hint=" | ".join(unique_hints) if unique_hints else None,
        details={
            "validation_errors": [
                {"field": ".".join(str(x) for x in e["loc"]), "message": e["msg"]}
                for e in errors
            ]
        },
    )


def format_json_parse_error(
    parameter_name: str, raw_value: str | None = None
) -> str:
    """
    Format a JSON parsing error with helpful context.

    Args:
        parameter_name: Name of the parameter that couldn't be parsed.
        raw_value: The raw value that failed to parse (truncated for safety).

    Returns:
        JSON string with error details and recovery hints.
    """
    hint_map = {
        "anomaly_json": "Pass the raw JSON output from peircean_observe_anomaly (Phase 1)",
        "hypotheses_json": "Pass the raw JSON output from peircean_generate_hypotheses (Phase 2)",
    }

    details: dict[str, Any] = {"parameter": parameter_name}
    if raw_value:
        # Truncate for safety and readability
        preview = raw_value[:100] + "..." if len(raw_value) > 100 else raw_value
        details["received_preview"] = preview

    return format_error_response(
        error=f"Invalid JSON in {parameter_name} parameter",
        code=ErrorCode.INVALID_JSON,
        hint=hint_map.get(parameter_name, f"Ensure {parameter_name} contains valid JSON"),
        details=details,
    )


def format_missing_field_error(
    field_name: str, expected_in: str, example: str | None = None
) -> str:
    """
    Format an error for missing required fields in JSON input.

    Args:
        field_name: The name of the missing field.
        expected_in: Where the field was expected (e.g., "anomaly_json").
        example: Example of correct format.

    Returns:
        JSON string with error details.
    """
    hint = f"Ensure {expected_in} contains a '{field_name}' field"
    if example:
        hint += f". Example: {example}"

    return format_error_response(
        error=f"Missing required field '{field_name}' in {expected_in}",
        code=ErrorCode.MISSING_FIELD,
        hint=hint,
        details={"missing_field": field_name, "expected_in": expected_in},
    )


__all__ = [
    "ErrorCode",
    "format_error_response",
    "format_validation_error",
    "format_json_parse_error",
    "format_missing_field_error",
]
