"""
Peircean Abduction: International Law Scenario

This script demonstrates the full 3-Phase Abduction Loop:
1. Observe Anomaly (Register the surprising fact)
2. Generate Hypotheses (Brainstorm explanations)
3. Evaluate via IBE (Select the best explanation)

Scenario: A "defunct" satellite collides with a station.
"""

import json
import sys
from peircean.mcp.server import (
    peircean_observe_anomaly,
    peircean_generate_hypotheses,
    peircean_evaluate_via_ibe
)

def print_step(title, content):
    print(f"\n👉 {title}")
    print("-" * 40)
    print(content)

def main():
    print("🕵️  Peircean Abduction: Deep Dive (International Law)")
    print("===================================================")

    # =========================================================================
    # PHASE 1: OBSERVE
    # =========================================================================
    observation = "Defunct 'debris' satellite executed a controlled burn 10s before collision, steering into the target."
    context = "Country A claimed it was uncontrollable debris. Flight logs recovered later."
    domain = "legal"

    print_step("PHASE 1: Observe Anomaly", f"Fact: {observation}\nDomain: {domain}")

    # Call Tool 1
    p1_output = peircean_observe_anomaly(
        observation=observation,
        context=context,
        domain=domain
    )
    p1_data = json.loads(p1_output)
    
    # Simulate the LLM's response (The "Anomaly JSON")
    # In a real flow, the LLM would generate this based on the prompt.
    anomaly_json = json.dumps({
        "anomaly": {
            "fact": observation,
            "surprise_level": "anomalous",
            "surprise_score": 0.95,
            "expected_baseline": "Debris follows Keplerian orbits without maneuvering",
            "domain": domain,
            "context": [context],
            "surprise_source": "Violates definition of space debris AND expectation of rational state actor behavior"
        }
    })
    print(f"✅ Generated Prompt. Simulating LLM Output:\n{anomaly_json}")


    # =========================================================================
    # PHASE 2: HYPOTHESIZE
    # =========================================================================
    print_step("PHASE 2: Generate Hypotheses", "Generating 3 distinct explanations...")

    # Call Tool 2
    p2_output = peircean_generate_hypotheses(
        anomaly_json=anomaly_json,
        num_hypotheses=3
    )
    
    # Simulate the LLM's response (The "Hypotheses JSON")
    hypotheses_json = json.dumps({
        "hypotheses": [
            {
                "id": "H1",
                "statement": "The satellite was a dormant 'sleeper' weapon activated for a kinetic strike.",
                "explains_anomaly": "Explains the maneuver (steering INTO collision) which debris cannot do.",
                "prior_probability": 0.10,
                "testable_predictions": [{"prediction": "Uplink signals at T-10s", "test_method": "Check RF logs"}]
            },
            {
                "id": "H2",
                "statement": "An automated 'end-of-life' deorbit script triggered erroneously.",
                "explains_anomaly": "Explains the burn, but the vector (into target) is a coincidence.",
                "prior_probability": 0.40,
                "testable_predictions": [{"prediction": "Code review shows deorbit trigger conditions met", "test_method": "Audit source code"}]
            },
            {
                "id": "H3",
                "statement": "Hacking by third party to frame Country A.",
                "explains_anomaly": "Explains burn and vector, plus Country A's denial.",
                "prior_probability": 0.05,
                "testable_predictions": [{"prediction": "Unusual IP traffic to ground station", "test_method": "Network forensics"}]
            }
        ]
    })
    print(f"✅ Generated Prompt. Simulating LLM Output:\n{hypotheses_json}")


    # =========================================================================
    # PHASE 3: EVALUATE (IBE)
    # =========================================================================
    print_step("PHASE 3: Inference to Best Explanation", "Evaluating via Council of Critics...")

    # Call Tool 3
    p3_output = peircean_evaluate_via_ibe(
        anomaly_json=anomaly_json,
        hypotheses_json=hypotheses_json,
        use_council=True
    )
    
    p3_data = json.loads(p3_output)
    prompt = p3_data["prompt"]
    
    print("✅ Generated Final Evaluation Prompt:")
    print("-" * 40)
    # Print the Council section of the prompt to show it's working
    start_idx = prompt.find("## Council of Critics Evaluation")
    end_idx = prompt.find("## Verdict Options")
    print(prompt[start_idx:end_idx])
    print("-" * 40)
    
    print("\n🎉 Demo Complete! The LLM would now return the final Verdict.")

if __name__ == "__main__":
    main()
