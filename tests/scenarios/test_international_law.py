import pytest
import json
from peircean.mcp.server import observe_anomaly, generate_hypotheses, evaluate_via_ibe

class TestInternationalLawScenario:
    """Integration tests for the International Law scenario."""

    @pytest.fixture
    def anomaly_input(self):
        return {
            "observation": "A collision occurred in Low Earth Orbit between a commercial station (Country B) and a defunct military satellite (Country A). Country A officially claimed the satellite had been 'uncontrollable space debris' for 5 years, shielding them from fault-based liability under the 1972 Liability Convention. However, recovered flight logs reveal the satellite fired its thrusters for a 2-second 'station-keeping' burn 10 seconds before impact.",
            "context": "The 1972 Liability Convention requires proof of 'fault' for accidents occurring in space. 'Debris' implies no active control. The thruster firing suggests active control, yet the maneuver steered the satellite *into* the collision path rather than away from it.",
            "domain": "Legal / International Space Law"
        }

    def test_full_scenario_flow(self, anomaly_input):
        # Phase 1: Observe Anomaly
        phase1_output = observe_anomaly(
            observation=anomaly_input["observation"],
            context=anomaly_input["context"],
            domain=anomaly_input["domain"]
        )
        phase1_data = json.loads(phase1_output)
        
        assert phase1_data["phase"] == 1
        assert "prompt" in phase1_data
        assert "Legal / International Space Law" in phase1_data["prompt"]
        
        # Simulate LLM response for Phase 1
        # In a real integration test with LLM, we would execute the prompt.
        # Here we mock the expected JSON structure that would be returned.
        anomaly_json = json.dumps({
            "anomaly": {
                "fact": "Defunct 'debris' satellite executed a controlled burn 10s before collision, steering into the target.",
                "surprise_level": "anomalous",
                "surprise_score": 0.95,
                "expected_baseline": "Space debris follows ballistic trajectories and does not execute maneuvers.",
                "domain": "Legal / International Space Law",
                "context": [
                    "1972 Liability Convention requires fault for space accidents",
                    "Country A claimed satellite was uncontrollable debris to avoid liability",
                    "Maneuver actively caused the collision rather than avoiding it"
                ],
                "key_features": [
                    "Active thruster burn from 'defunct' satellite",
                    "Timing: 10 seconds before impact",
                    "Vector: Steered into collision path",
                    "Contradiction: Legal classification vs. Physical behavior"
                ],
                "surprise_source": "Violates the definition of space debris and the expectation of rational actor behavior (avoiding collision)."
            }
        })

        # Phase 2: Generate Hypotheses
        phase2_output = generate_hypotheses(
            anomaly_json=anomaly_json,
            num_hypotheses=3
        )
        phase2_data = json.loads(phase2_output)
        
        assert phase2_data["phase"] == 2
        assert "prompt" in phase2_data
        
        # Simulate LLM response for Phase 2
        hypotheses_json = json.dumps({
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "The satellite was never defunct; it was a dormant 'sleeper' weapon activated for a kinetic strike.",
                    "explains_anomaly": "Explains the thruster capability, the precise timing, and the intentional steering into the target.",
                    "prior_probability": 0.2,
                    "assumptions": [
                        {"statement": "Country A has a covert space weapon program", "testable": True},
                        {"statement": "Satellite retained fuel and command link", "testable": True}
                    ],
                    "testable_predictions": [
                        {
                            "prediction": "Encrypted uplink signal detected shortly before burn",
                            "test_method": "Review RF spectrum logs from ground stations",
                            "if_true": "Strongly supports H1 (command received)",
                            "if_false": "Weakens H1 (implies autonomous trigger)"
                        }
                    ]
                },
                {
                    "id": "H2",
                    "statement": "A cyber-intrusion by a third party (Country C or non-state actor) hijacked the satellite's command link.",
                    "explains_anomaly": "Explains why Country A claimed it was debris (they lost control) but it still maneuvered.",
                    "prior_probability": 0.3,
                    "assumptions": [
                        {"statement": "Satellite command link was vulnerable/unpatched", "testable": True},
                        {"statement": "Attacker had knowledge of legacy protocols", "testable": True}
                    ],
                    "testable_predictions": [
                        {
                            "prediction": "Command logs show unauthorized IP or anomalous signal origin",
                            "test_method": "Forensic analysis of Country A's ground control logs",
                            "if_true": "Supports H2",
                            "if_false": "Weakens H2"
                        }
                    ]
                },
                {
                    "id": "H3",
                    "statement": "An automated 'fail-safe' or 'end-of-life' deorbit script triggered erroneously due to sensor malfunction.",
                    "explains_anomaly": "Explains the burn without requiring malicious intent; the collision was an accidental result of a blind maneuver.",
                    "prior_probability": 0.4,
                    "assumptions": [
                        {"statement": "Satellite had legacy automation code enabled", "testable": True},
                        {"statement": "Proximity sensors or timers malfunctioned", "testable": True}
                    ],
                    "testable_predictions": [
                        {
                            "prediction": "Code review reveals 'dead man switch' logic",
                            "test_method": "Audit of satellite firmware source code",
                            "if_true": "Supports H3",
                            "if_false": "Weakens H3"
                        }
                    ]
                }
            ]
        })

        # Phase 3: Evaluate via IBE with Custom Council
        custom_council = ["Space Law Specialist", "Orbital Mechanics Expert", "Military Strategy Analyst"]
        phase3_output = evaluate_via_ibe(
            anomaly_json=anomaly_json,
            hypotheses_json=hypotheses_json,
            custom_council=custom_council
        )
        phase3_data = json.loads(phase3_output)
        
        assert phase3_data["phase"] == 3
        assert "prompt" in phase3_data
        
        # Verify custom council is in the prompt
        for role in custom_council:
            assert role in phase3_data["prompt"]
