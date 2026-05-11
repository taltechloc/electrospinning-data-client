#!/bin/bash
set -e

# build.sh
# Builds the electrospinning-data-client package into wheel and sdist.

# Move to the project root (one level up from scripts/)
cd "$(dirname "$0")/.."

echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "Building package in $(pwd)..."
# Ensure hatch is installed
if ! command -v hatch &> /dev/null
then
    echo "hatch could not be found. Please install it (pip install hatch)."
    exit 1
fi

hatch build

echo "Build complete. Artifacts are in dist/"
ls -lh dist/
