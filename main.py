#!/usr/bin/env python3
"""InMoov Right Hand — main entry point.

Run directly on the Raspberry Pi 4B with PCA9685 connected via I2C.
Provides an interactive CLI for testing servo movements and gestures.
"""

import sys
import time
from lib.hand import Hand


def print_help():
    print("""
InMoov Right Hand Controller
─────────────────────────────
Commands:
  gesture <name>         Execute a gesture (open, fist, point, peace, thumbs_up, grab, pinch, rock)
  move <servo> <angle>   Move a servo to angle (0-180)
  smooth <servo> <angle> Move a servo slowly (0-180)
  fingers <T I M R P>    Set all 5 fingers at once (0-180 each, - to skip)
  wrist <angle>          Set wrist angle (0-180)
  home                   Return to default positions
  detach                 Release all servos
  status                 Show current positions
  demo                   Run a demo sequence
  help                   Show this help
  quit                   Exit
""")


def run_demo(hand):
    print("Running demo sequence...")
    delay = 0.5

    hand.open_hand()
    time.sleep(delay)

    for name in ["fist", "open", "point", "peace", "thumbs_up", "rock", "pinch", "grab", "open"]:
        print(f"  -> {name}")
        hand.gesture(name, speed=0.005)
        time.sleep(delay)

    print("Demo complete.")


def main():
    simulate = "--simulate" in sys.argv or "--sim" in sys.argv
    hand = Hand(simulate=simulate)

    print("InMoov Right Hand Controller")
    if simulate:
        print("(Simulation mode — no hardware required)")
    print('Type "help" for commands, "quit" to exit.\n')

    hand.home()

    while True:
        try:
            raw = input("hand> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        try:
            if cmd in ("quit", "exit", "q"):
                break

            elif cmd == "help":
                print_help()

            elif cmd == "gesture":
                if len(parts) < 2:
                    print("Usage: gesture <name>")
                    continue
                hand.gesture(parts[1])

            elif cmd == "move":
                if len(parts) < 3:
                    print("Usage: move <servo> <angle>")
                    continue
                hand.move(parts[1], float(parts[2]))

            elif cmd == "smooth":
                if len(parts) < 3:
                    print("Usage: smooth <servo> <angle>")
                    continue
                hand.move(parts[1], float(parts[2]), speed=0.005)

            elif cmd == "fingers":
                if len(parts) < 6:
                    print("Usage: fingers <thumb> <index> <middle> <ring> <pinky>  (use - to skip)")
                    continue
                vals = {}
                for i, name in enumerate(["thumb", "index", "middle", "ring", "pinky"]):
                    if parts[i + 1] != "-":
                        vals[name] = float(parts[i + 1])
                hand.set_fingers(**vals)

            elif cmd == "wrist":
                if len(parts) < 2:
                    print("Usage: wrist <angle>")
                    continue
                hand.set_wrist(float(parts[1]))

            elif cmd == "home":
                hand.home()
                print("Returned to home position.")

            elif cmd == "detach":
                hand.detach()
                print("Servos detached.")

            elif cmd == "status":
                for name, angle in hand.get_all_positions().items():
                    print(f"  {name:8s}: {angle}°")

            elif cmd == "demo":
                run_demo(hand)

            else:
                print(f"Unknown command: {cmd}. Type 'help' for commands.")

        except Exception as e:
            print(f"Error: {e}")

    hand.detach()
    print("Goodbye.")


if __name__ == "__main__":
    main()
