# RoboHand

Python-based controller for a 3D-printed **InMoov** robotic right hand, running on a **Raspberry Pi 4B** with a **PCA9685** servo driver. Features an interactive CLI for real-time servo control, predefined gestures, and smooth motion.

## Hardware

| Component | Spec |
|---|---|
| Hand model | [InMoov](http://inmoov.fr/) right hand (3D printed) |
| Computer | Raspberry Pi 4B |
| Servo driver | PCA9685 16-channel (I2C, default `0x40`) |
| Finger servos | 5x MG996R (one per finger) |
| Wrist servo | 1x high-torque servo |
| Power supply | 5-6V DC, 10A+ recommended (external, **not** from Pi) |

### Wiring Overview

```
Raspberry Pi 4B            PCA9685 Servo Driver
 Pin 1 (3.3V)  ────────►  VCC  (logic power)
 Pin 3 (SDA)   ────────►  SDA
 Pin 5 (SCL)   ────────►  SCL
 Pin 6 (GND)   ────────►  GND
                           V+  ◄──── External PSU (+)
                           GND ◄──── External PSU (-)
```

| PCA9685 Channel | Servo |
|---|---|
| CH0 | Thumb |
| CH1 | Index |
| CH2 | Middle |
| CH3 | Ring |
| CH4 | Pinky |
| CH5 | Wrist |

> **Important:** Never power the servos from the Pi's 5V pin. Six MG996R servos can draw 10A+ under load. Use a dedicated external power supply. See [docs/wiring.txt](docs/wiring.txt) for the full wiring diagram and critical notes.

## Setup

### 1. Raspberry Pi Setup (one-time)

```bash
git clone <repo-url> && cd RoboHand
chmod +x setup_pi.sh
./setup_pi.sh
```

This enables I2C, installs system dependencies, creates a Python virtual environment, installs packages, and verifies the PCA9685 is visible on the I2C bus.

### 2. Manual Setup

```bash
sudo raspi-config nonint do_i2c 0          # enable I2C
sudo apt-get install -y python3-pip python3-venv i2c-tools

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Verify the PCA9685 is detected:

```bash
i2cdetect -y 1
# Should show device at address 0x40
```

## Usage

```bash
source venv/bin/activate
python main.py
```

Run without hardware (simulation mode):

```bash
python main.py --simulate
```

### CLI Commands

| Command | Description |
|---|---|
| `gesture <name>` | Execute a gesture: `open`, `fist`, `point`, `peace`, `thumbs_up`, `grab`, `pinch`, `rock` |
| `move <servo> <angle>` | Move a servo to an angle (0-180) |
| `smooth <servo> <angle>` | Move a servo slowly to an angle |
| `fingers <T I M R P>` | Set all 5 fingers at once (use `-` to skip) |
| `wrist <angle>` | Set wrist angle (0-180) |
| `home` | Return all servos to default positions |
| `detach` | Release all servos (no signal) |
| `status` | Show current servo positions |
| `demo` | Run through all gestures sequentially |
| `help` | Show available commands |
| `quit` | Exit |

### Examples

```bash
hand> gesture fist        # close all fingers
hand> gesture peace       # peace sign
hand> move index 90       # move index finger to 90 degrees
hand> smooth thumb 180    # slowly curl the thumb
hand> fingers 0 180 180 180 180   # thumbs up (manual)
hand> fingers - 45 - - -  # move only the index finger to 45
hand> wrist 45            # rotate wrist
hand> demo                # cycle through all gestures
```

## Project Structure

```
RoboHand/
├── main.py                 # CLI entry point
├── lib/
│   └── hand.py             # Hand controller class (servo + gesture logic)
├── config/
│   └── hand_config.yaml    # Servo channels, calibration, and gesture definitions
├── docs/
│   └── wiring.txt          # Full wiring diagram with pin-level detail
├── tests/
│   └── test_hand.py        # Unit tests (simulation mode)
├── setup_pi.sh             # One-time Raspberry Pi setup script
└── requirements.txt        # Python dependencies
```

## Configuration

All servo calibration and gesture definitions live in [config/hand_config.yaml](config/hand_config.yaml). You can adjust:

- **Servo pulse ranges** (`pulse_min` / `pulse_max`) to match your specific MG996R units
- **Default positions** for each servo
- **Gestures** by defining target angles per servo

## Tests

```bash
python -m pytest tests/ -v
# or without pytest:
python tests/test_hand.py
```

Tests run in simulation mode and do not require hardware.

## Dependencies

- `adafruit-circuitpython-servokit` - PCA9685 servo control
- `adafruit-circuitpython-pca9685` - PCA9685 driver
- `pyyaml` - YAML config parsing
- `RPi.GPIO` - Raspberry Pi GPIO access

## License

[MIT](LICENSE) - MinJun
