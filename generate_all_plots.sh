#!/bin/bash

# Exit on error
set -e

# Set up Python virtual environment
echo "[INFO] Creating virtual environment..."
python3.12 -m venv .venv

# Activate the virtual environment
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "[INFO] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the main script
echo "[INFO] Running spectral analysis..."
python src/Main.py

echo "[INFO] Done. All plots generated."
