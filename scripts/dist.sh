#!/bin/bash
set -e

# dist.sh
# Uploads the built electrospinning_data_client artifacts to PyPI using twine.

# Move to the project root (one level up from scripts/)
cd "$(dirname "$0")/.."

DIST_DIR="dist"

if [ ! -d "$DIST_DIR" ]; then
    echo "Error: Directory '$DIST_DIR' does not exist. Run ./scripts/build.sh first from any location."
    exit 1
fi

echo "Verifying artifacts with twine..."
# Ensure twine is installed
if ! command -v twine &> /dev/null
then
    echo "twine could not be found. Please install it (pip install twine)."
    exit 1
fi

twine check dist/*

echo "Ready to upload to PyPI."
echo "Note: This script will prompt for PyPI credentials unless configured in ~/.pypirc"

# Uncomment the following line to actually upload
# twine upload dist/*

echo "Upload dry-run complete. Uncomment the twine upload line in scripts/dist.sh to publish."
