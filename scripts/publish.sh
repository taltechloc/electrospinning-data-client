#!/bin/bash
set -e

# Move to project root
cd "$(dirname "$0")/.."

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "Building package..."
hatch build

echo "Verifying package..."
twine check dist/*

echo ""
echo "Ready to upload to PyPI."
echo ""

# Prompt for PyPI API token securely
read -s -p "Enter your PyPI API token: " PYPI_TOKEN
echo ""

# Export credentials for Twine
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="$PYPI_TOKEN"

echo ""
echo "Uploading package to PyPI..."
twine upload dist/*

echo ""
echo "Package uploaded successfully!"