"""Basic tests for Hand controller (simulation mode)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.hand import Hand, ALL_SERVOS


def test_init():
    hand = Hand(simulate=True)
    positions = hand.get_all_positions()
    assert len(positions) == 6
    for name in ALL_SERVOS:
        assert name in positions


def test_move():
    hand = Hand(simulate=True)
    hand.move("index", 90)
    assert hand.get_position("index") == 90


def test_move_clamps():
    hand = Hand(simulate=True)
    hand.move("thumb", 999)
    assert hand.get_position("thumb") == 180
    hand.move("thumb", -50)
    assert hand.get_position("thumb") == 0


def test_gesture():
    hand = Hand(simulate=True)
    hand.gesture("fist")
    for finger in ["thumb", "index", "middle", "ring", "pinky"]:
        assert hand.get_position(finger) == 180


def test_open_hand():
    hand = Hand(simulate=True)
    hand.gesture("fist")
    hand.open_hand()
    for finger in ["thumb", "index", "middle", "ring", "pinky"]:
        assert hand.get_position(finger) == 0


def test_set_fingers_partial():
    hand = Hand(simulate=True)
    hand.set_fingers(index=45, ring=100)
    assert hand.get_position("index") == 45
    assert hand.get_position("ring") == 100


def test_wrist():
    hand = Hand(simulate=True)
    hand.set_wrist(45)
    assert hand.get_position("wrist") == 45


def test_home():
    hand = Hand(simulate=True)
    hand.gesture("fist")
    hand.home()
    assert hand.get_position("wrist") == 90
    assert hand.get_position("thumb") == 0


def test_unknown_servo_raises():
    hand = Hand(simulate=True)
    try:
        hand.move("elbow", 90)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_unknown_gesture_raises():
    hand = Hand(simulate=True)
    try:
        hand.gesture("dab")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"  PASS: {name}")
    print("\nAll tests passed.")
