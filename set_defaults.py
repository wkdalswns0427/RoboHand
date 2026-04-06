#!/usr/bin/env python3
"""Set all servos to their default positions and detach."""

import sys
from lib.hand import Hand

simulate = "--simulate" in sys.argv or "--sim" in sys.argv
hand = Hand(simulate=simulate)

print("Setting all servos to defaults...")
hand.home()

for name, angle in hand.get_all_positions().items():
    print(f"  {name:8s}: {angle}°")

hand.detach()
print("Done. Servos detached.")
