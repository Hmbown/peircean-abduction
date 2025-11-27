import json
import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from peircean.mcp.server import evaluate_via_ibe

# Simulated output from Phase 1
anomaly_json = json.dumps(
    {
        "anomaly": {
            "fact": "Defunct 'debris' satellite executed a controlled burn 10s before collision, steering into the target.",
            "surprise_level": "anomalous",
            "surprise_score": 0.95,
            "expected_baseline": "Space debris follows ballistic trajectories and does not execute maneuvers.",
            "domain": "Legal / International Space Law",
            "context": [
                "1972 Liability Convention requires fault for space accidents",
                "Country A claimed satellite was uncontrollable debris to avoid liability",
                "Maneuver actively caused the collision rather than avoiding it",
            ],
            "key_features": [
                "Active thruster burn from 'defunct' satellite",
                "Timing: 10 seconds before impact",
                "Vector: Steered into collision path",
                "Contradiction: Legal classification vs. Physical behavior",
            ],
            "surprise_source": "Violates the definition of space debris and the expectation of rational actor behavior (avoiding collision).",
        }
    }
)

# Simulated output from Phase 2
hypotheses_json = json.dumps(
    {
        "hypotheses": [
            {
                "id": "H1",
                "statement": "The satellite was never defunct; it was a dormant 'sleeper' weapon activated for a kinetic strike.",
                "explains_anomaly": "Explains the thruster capability, the precise timing, and the intentional steering into the target.",
                "prior_probability": 0.2,
                "assumptions": [
                    {"statement": "Country A has a covert space weapon program", "testable": True},
                    {"statement": "Satellite retained fuel and command link", "testable": True},
                ],
                "testable_predictions": [
                    {
                        "prediction": "Encrypted uplink signal detected shortly before burn",
                        "test_method": "Review RF spectrum logs from ground stations",
                        "if_true": "Strongly supports H1 (command received)",
                        "if_false": "Weakens H1 (implies autonomous trigger)",
                    }
                ],
            },
            {
                "id": "H2",
                "statement": "A cyber-intrusion by a third party (Country C or non-state actor) hijacked the satellite's command link.",
                "explains_anomaly": "Explains why Country A claimed it was debris (they lost control) but it still maneuvered.",
                "prior_probability": 0.3,
                "assumptions": [
                    {
                        "statement": "Satellite command link was vulnerable/unpatched",
                        "testable": True,
                    },
                    {"statement": "Attacker had knowledge of legacy protocols", "testable": True},
                ],
                "testable_predictions": [
                    {
                        "prediction": "Command logs show unauthorized IP or anomalous signal origin",
                        "test_method": "Forensic analysis of Country A's ground control logs",
                        "if_true": "Supports H2",
                        "if_false": "Weakens H2",
                    }
                ],
            },
            {
                "id": "H3",
                "statement": "An automated 'fail-safe' or 'end-of-life' deorbit script triggered erroneously due to sensor malfunction.",
                "explains_anomaly": "Explains the burn without requiring malicious intent; the collision was an accidental result of a blind maneuver.",
                "prior_probability": 0.4,
                "assumptions": [
                    {"statement": "Satellite had legacy automation code enabled", "testable": True},
                    {"statement": "Proximity sensors or timers malfunctioned", "testable": True},
                ],
                "testable_predictions": [
                    {
                        "prediction": "Code review reveals 'dead man switch' logic",
                        "test_method": "Audit of satellite firmware source code",
                        "if_true": "Supports H3",
                        "if_false": "Weakens H3",
                    }
                ],
            },
        ]
    }
)

# Phase 3: Evaluate via IBE with Dynamic Council
# We use the specialists nominated in Phase 1
custom_council = ["Space Law Specialist", "Orbital Mechanics Expert", "Military Strategy Analyst"]

print(f"\n[INFO] Calling evaluate_via_ibe with custom council: {custom_council}...")
prompt = evaluate_via_ibe(
    anomaly_json=anomaly_json, hypotheses_json=hypotheses_json, custom_council=custom_council
)

print("\n" + "=" * 80)
print(" PHASE 3 PROMPT (EVALUATE) ")
print("=" * 80 + "\n")
print(prompt)
