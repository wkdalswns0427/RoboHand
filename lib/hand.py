"""InMoov right hand controller using PCA9685 servo driver."""

import time
import yaml
from pathlib import Path

try:
    from adafruit_servokit import ServoKit
except ImportError:
    ServoKit = None


FINGER_NAMES = ["thumb", "index", "middle", "ring", "pinky"]
ALL_SERVOS = FINGER_NAMES + ["wrist"]


class Hand:
    """Controls 6 servos (5 fingers + wrist) on an InMoov right hand."""

    def __init__(self, config_path=None, simulate=False):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "hand_config.yaml"
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.simulate = simulate or ServoKit is None
        self.servo_config = self.config["servos"]
        self.gestures = self.config.get("gestures", {})
        self._positions = {}

        if not self.simulate:
            self.kit = ServoKit(
                channels=16,
                address=self.config["i2c"]["address"],
                frequency=self.config["pca9685"]["frequency"],
            )
            # Configure each servo's pulse range
            for name, cfg in self.servo_config.items():
                ch = cfg["channel"]
                self.kit.servo[ch].set_pulse_width_range(
                    cfg["pulse_min"], cfg["pulse_max"]
                )
        else:
            self.kit = None
            print("[SIMULATE] Hand controller running in simulation mode")

        # Move to default positions
        for name, cfg in self.servo_config.items():
            self._positions[name] = cfg["default"]

    def move(self, servo_name, angle, speed=None):
        """Move a single servo to the given angle.

        Args:
            servo_name: One of thumb, index, middle, ring, pinky, wrist.
            angle: Target angle in degrees.
            speed: If set, move incrementally with this delay (seconds) per degree.
        """
        if servo_name not in self.servo_config:
            raise ValueError(f"Unknown servo: {servo_name}")

        cfg = self.servo_config[servo_name]
        angle = max(0, min(180, angle))

        if speed and speed > 0:
            self._move_smooth(servo_name, angle, speed)
        else:
            self._set_angle(servo_name, angle)

        self._positions[servo_name] = angle

    def _set_angle(self, servo_name, angle):
        ch = self.servo_config[servo_name]["channel"]
        if self.simulate:
            print(f"[SIMULATE] {servo_name} (ch{ch}) -> {angle}°")
        else:
            self.kit.servo[ch].angle = angle

    def _move_smooth(self, servo_name, target, delay_per_deg):
        """Incrementally move servo for smoother motion."""
        current = self._positions.get(servo_name, 0)
        step = 1 if target > current else -1
        for a in range(int(current), int(target) + step, step):
            self._set_angle(servo_name, a)
            time.sleep(delay_per_deg)

    def gesture(self, name, speed=None):
        """Execute a named gesture from config.

        Args:
            name: Gesture name (e.g. 'fist', 'open', 'point').
            speed: Optional smooth movement delay per degree.
        """
        if name not in self.gestures:
            available = ", ".join(self.gestures.keys())
            raise ValueError(f"Unknown gesture '{name}'. Available: {available}")

        targets = self.gestures[name]
        for servo_name, angle in targets.items():
            self.move(servo_name, angle, speed=speed)

    def open_hand(self, speed=None):
        """Fully open all fingers."""
        self.gesture("open", speed=speed)

    def close_hand(self, speed=None):
        """Close all fingers into a fist."""
        self.gesture("fist", speed=speed)

    def set_fingers(self, thumb=None, index=None, middle=None, ring=None, pinky=None, speed=None):
        """Set individual finger positions. None = don't change."""
        for name, angle in [("thumb", thumb), ("index", index), ("middle", middle),
                            ("ring", ring), ("pinky", pinky)]:
            if angle is not None:
                self.move(name, angle, speed=speed)

    def set_wrist(self, angle, speed=None):
        """Set wrist rotation angle."""
        self.move("wrist", angle, speed=speed)

    def get_position(self, servo_name):
        """Return the current position of a servo."""
        return self._positions.get(servo_name)

    def get_all_positions(self):
        """Return dict of all current servo positions."""
        return dict(self._positions)

    def detach(self):
        """Release all servos (set to None/no signal)."""
        if self.simulate:
            print("[SIMULATE] All servos detached")
            return
        for name, cfg in self.servo_config.items():
            self.kit.servo[cfg["channel"]].angle = None

    def home(self):
        """Move all servos to their default positions."""
        for name, cfg in self.servo_config.items():
            self.move(name, cfg["default"])
