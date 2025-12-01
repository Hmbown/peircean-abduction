"""
Peircean Abduction: Quickstart Example

This script demonstrates the "Single-Shot" abduction capability by generating
the prompt that would be sent to an LLM.

NOTE: This script does NOT call an LLM directly. It verifies that the
Peircean logic harness is functioning and generating valid prompts.

To use this with an LLM:
1. Install the MCP server: `peircean --install`
2. Use Claude Desktop or Cursor to chat with "peircean".
"""

import json
import sys

from peircean.mcp.server import peircean_abduce_single_shot


def main() -> None:
    print("🔍 Peircean Abduction: Quickstart Demo")
    print("======================================")
    print("This script simulates a single-shot abduction request.")

    # 1. Define the Observation
    observation = "Customer churn rate doubled in Q3"
    context = "No price changes, NPS stable, no competitor launches"
    domain = "financial"

    print(f"\n[1] Observation: {observation}")
    print(f"    Context: {context}")
    print(f"    Domain: {domain}")

    print("\n[2] Generating prompt via Peircean Logic Harness...")

    # 2. Call the Tool
    # In a real MCP client, this tool call is intercepted by the LLM,
    # which executes the prompt and returns the result.
    try:
        response_json = peircean_abduce_single_shot(
            observation=observation, context=context, domain=domain, num_hypotheses=3
        )
    except Exception as e:
        print(f"\n❌ Error generating prompt: {e}")
        sys.exit(1)

    # 3. Parse and Display Result
    data = json.loads(response_json)
    prompt = data["prompt"]

    print("\n✅ Success! Generated structured prompt:")
    print("-" * 60)
    # Show a preview of the prompt
    preview_lines = prompt.split("\n")[:15]
    print("\n".join(preview_lines))
    print("... [Rest of prompt] ...")
    print("-" * 60)

    print("\n👉 Next Steps:")
    print("1. Run 'peircean --install' to configure Claude Desktop.")
    print("2. Open Claude and ask: 'Analyze this anomaly: Customer churn doubled...'")
    print("3. The Peircean tools will activate automatically.")


if __name__ == "__main__":
    main()
