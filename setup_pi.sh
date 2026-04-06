#!/bin/bash
# Setup script for Raspberry Pi 4B with PCA9685
# Run once after fresh OS install

set -e

echo "=== InMoov Right Hand - Pi Setup ==="

# Enable I2C
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Install system dependencies
echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv i2c-tools

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify I2C
echo ""
echo "=== Checking I2C bus ==="
echo "PCA9685 should appear at address 0x40:"
i2cdetect -y 1

echo ""
echo "Setup complete. Activate with: source venv/bin/activate"
echo "Run with: python main.py"
echo "Test without hardware: python main.py --simulate"
