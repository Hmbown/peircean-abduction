"""
Peircean Abduction: Quickstart Example

This script demonstrates the "Single-Shot" abduction capability.
It runs the entire Peircean loop (Observe -> Hypothesize -> Evaluate) in one call.
"""

import json
import sys
from peircean.mcp.server import peircean_abduce_single_shot

def main():
    print("🔍 Peircean Abduction: Quickstart Demo")
    print("======================================")

    # 1. Define the Observation
    observation = "Customer churn rate doubled in Q3"
    context = "No price changes, NPS stable, no competitor launches"
    domain = "financial"
    
    print(f"\nObservation: {observation}")
    print(f"Context: {context}")
    print(f"Domain: {domain}")
    print("\nThinking... (Generating Prompt)")

    # 2. Call the Tool
    # Note: In a real MCP client, this would be sent to the LLM.
    # Here, we generate the prompt that WOULD be sent.
    response_json = peircean_abduce_single_shot(
        observation=observation,
        context=context,
        domain=domain,
        num_hypotheses=3
    )

    # 3. Parse and Display Result
    data = json.loads(response_json)
    prompt = data["prompt"]
    
    print("\n✅ Generated Prompt for LLM:")
    print("-" * 40)
    print(prompt[:500] + "...\n[Truncated for brevity]")
    print("-" * 40)
    
    print("\n💡 What just happened?")
    print("1. We called 'peircean_abduce_single_shot'.")
    print("2. It constructed a structured prompt enforcing Peirce's schema.")
    print("3. An LLM would receive this prompt and return a JSON analysis.")
    print("\nTo see the full prompt, run this script and inspect the output.")

if __name__ == "__main__":
    main()
