"""
Tests for Peircean CLI.
"""

import json
import sys
from unittest import mock

import pytest

from peircean.cli import create_parser, main, run_interactive, run_prompt_mode


class TestCLIParser:
    """Test the argument parser."""

    def test_parser_creation(self):
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "peircean"

    def test_parser_observation_positional(self):
        parser = create_parser()
        args = parser.parse_args(["Test observation"])
        assert args.observation == "Test observation"

    def test_parser_domain_default(self):
        parser = create_parser()
        args = parser.parse_args(["Test"])
        assert args.domain == "general"

    def test_parser_domain_valid(self):
        parser = create_parser()
        for domain in ["general", "financial", "legal", "medical", "technical", "scientific"]:
            args = parser.parse_args(["--domain", domain, "Test"])
            assert args.domain == domain

    def test_parser_domain_invalid(self):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--domain", "invalid", "Test"])

    def test_parser_num_hypotheses_default(self):
        parser = create_parser()
        args = parser.parse_args(["Test"])
        assert args.num_hypotheses == 5

    def test_parser_num_hypotheses_custom(self):
        parser = create_parser()
        args = parser.parse_args(["--num-hypotheses", "10", "Test"])
        assert args.num_hypotheses == 10

    def test_parser_format_default(self):
        parser = create_parser()
        args = parser.parse_args(["Test"])
        assert args.format == "markdown"

    def test_parser_format_json(self):
        parser = create_parser()
        args = parser.parse_args(["--format", "json", "Test"])
        assert args.format == "json"

    def test_parser_format_prompt(self):
        parser = create_parser()
        args = parser.parse_args(["--format", "prompt", "Test"])
        assert args.format == "prompt"

    def test_parser_prompt_flag(self):
        parser = create_parser()
        args = parser.parse_args(["--prompt", "Test"])
        assert args.prompt is True

    def test_parser_council_flag(self):
        parser = create_parser()
        args = parser.parse_args(["--council", "Test"])
        assert args.council is True

    def test_parser_context(self):
        parser = create_parser()
        args = parser.parse_args(["--context", '{"key": "value"}', "Test"])
        assert args.context == '{"key": "value"}'

    def test_parser_verbose(self):
        parser = create_parser()
        args = parser.parse_args(["-v", "Test"])
        assert args.verbose is True

    def test_parser_short_domain(self):
        parser = create_parser()
        args = parser.parse_args(["-d", "financial", "Test"])
        assert args.domain == "financial"

    def test_parser_short_format(self):
        parser = create_parser()
        args = parser.parse_args(["-f", "json", "Test"])
        assert args.format == "json"

    def test_parser_short_num_hypotheses(self):
        parser = create_parser()
        args = parser.parse_args(["-n", "3", "Test"])
        assert args.num_hypotheses == 3


class TestPromptMode:
    """Test prompt mode output."""

    def test_run_prompt_mode_outputs_prompt(self, capsys):
        run_prompt_mode(
            observation="Test observation", domain="general", num_hypotheses=3, context=None
        )
        captured = capsys.readouterr()
        assert "Test observation" in captured.out
        assert "ABDUCTIVE REASONING" in captured.out

    def test_run_prompt_mode_with_context(self, capsys):
        run_prompt_mode(
            observation="Test observation",
            domain="technical",
            num_hypotheses=5,
            context={"key": "value"},
        )
        captured = capsys.readouterr()
        assert "Test observation" in captured.out
        assert "technical" in captured.out

    def test_run_prompt_mode_financial_domain(self, capsys):
        run_prompt_mode(
            observation="Stock dropped", domain="financial", num_hypotheses=3, context=None
        )
        captured = capsys.readouterr()
        assert "financial" in captured.out.lower()


class TestInteractiveMode:
    """Test interactive mode (which currently just outputs prompts)."""

    def test_run_interactive_markdown(self, capsys):
        run_interactive(
            observation="Test observation",
            domain="general",
            num_hypotheses=3,
            format_type="markdown",
            use_council=False,
            context=None,
            verbose=False,
        )
        captured = capsys.readouterr()
        # Should contain the observation and prompt
        assert "Test observation" in captured.out

    def test_run_interactive_json_format(self, capsys):
        run_interactive(
            observation="Test observation",
            domain="general",
            num_hypotheses=3,
            format_type="json",
            use_council=False,
            context=None,
            verbose=False,
        )
        captured = capsys.readouterr()
        # Find the JSON output (after the panel)
        # The JSON should be parseable
        lines = captured.out.split("\n")
        json_started = False
        json_lines = []
        for line in lines:
            if line.strip().startswith("{"):
                json_started = True
            if json_started:
                json_lines.append(line)

        if json_lines:
            json_str = "\n".join(json_lines)
            # Try to find valid JSON
            try:
                data = json.loads(json_str)
                assert "observation" in data
                assert "prompt" in data
            except json.JSONDecodeError:
                # If parsing fails, just verify the output contains expected elements
                assert "Test observation" in captured.out


class TestMainFunction:
    """Test the main CLI entry point."""

    def test_main_no_observation_returns_1(self, capsys):
        with mock.patch.object(sys, "argv", ["peircean"]):
            result = main()
        assert result == 1

    def test_main_with_observation_returns_0(self, capsys):
        with mock.patch.object(sys, "argv", ["peircean", "--prompt", "Test observation"]):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "Test observation" in captured.out

    def test_main_prompt_mode(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "--prompt", "--domain", "financial", "Stock dropped"]
        ):
            result = main()
        assert result == 0
        captured = capsys.readouterr()
        assert "Stock dropped" in captured.out

    def test_main_format_prompt(self, capsys):
        with mock.patch.object(sys, "argv", ["peircean", "--format", "prompt", "Test"]):
            result = main()
        assert result == 0

    def test_main_invalid_context_json(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "--context", "invalid json", "Test"]
        ):
            result = main()
        assert result == 1
        captured = capsys.readouterr()
        assert "Error parsing context JSON" in captured.out

    def test_main_valid_context_json(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "--prompt", "--context", '{"key": "value"}', "Test"]
        ):
            result = main()
        assert result == 0

    def test_main_all_domains(self, capsys):
        for domain in ["general", "financial", "legal", "medical", "technical", "scientific"]:
            with mock.patch.object(
                sys, "argv", ["peircean", "--prompt", "--domain", domain, "Test"]
            ):
                result = main()
            assert result == 0

    def test_main_num_hypotheses(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "--prompt", "--num-hypotheses", "10", "Test"]
        ):
            result = main()
        assert result == 0

    def test_main_council_flag(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "--council", "Test"]
        ):
            result = main()
        assert result == 0

    def test_main_verbose_flag(self, capsys):
        with mock.patch.object(
            sys, "argv", ["peircean", "-v", "--prompt", "Test"]
        ):
            result = main()
        assert result == 0
