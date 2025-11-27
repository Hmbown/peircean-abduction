import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import json

from peircean.mcp.server import observe_anomaly

observation = "A collision occurred in Low Earth Orbit between a commercial station (Country B) and a defunct military satellite (Country A). Country A officially claimed the satellite had been 'uncontrollable space debris' for 5 years, shielding them from fault-based liability under the 1972 Liability Convention. However, recovered flight logs reveal the satellite fired its thrusters for a 2-second 'station-keeping' burn 10 seconds before impact."

context = "The 1972 Liability Convention requires proof of 'fault' for accidents occurring in space. 'Debris' implies no active control. The thruster firing suggests active control, yet the maneuver steered the satellite *into* the collision path rather than away from it."

domain = "Legal / International Space Law"

output = observe_anomaly(observation=observation, context=context, domain=domain)

data = json.loads(output)
print(data["prompt"])
