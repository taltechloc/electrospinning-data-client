#!/bin/bash

# Electrospinning Data Python Client - Development Installation Script
# This script sets up a local virtual environment and installs the package in editable mode.

set -e

# Get the root directory of the python-client (one level up from this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLIENT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up development environment in: $CLIENT_ROOT"

cd "$CLIENT_ROOT"

# 1. Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# 2. Install package in editable mode
# This allows changes to the source code to be reflected immediately without re-installing.
echo "Installing electrospinning-data in editable mode..."
pip install -e .

# 5. Optional: Install test dependencies if needed
# pip install pytest

echo "--------------------------------------------------"
echo "Development environment setup complete!"
echo "Package 'electrospinning-data' is now installed in editable mode."
echo "--------------------------------------------------"
