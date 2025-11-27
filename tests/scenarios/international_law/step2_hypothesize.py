import json
import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from peircean.mcp.server import peircean_generate_hypotheses

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

output = peircean_generate_hypotheses(anomaly_json=anomaly_json, num_hypotheses=3)

data = json.loads(output)
print(data["prompt"])
