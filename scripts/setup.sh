#!/bin/bash

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
source "$SCRIPT_DIR/config.env"

# Ensure Minimap2 is installed (cloning and building if not present)
if [ ! -d "$MINIMAP_DIR" ]; then
    echo "Cloning Minimap2 repository..."
    git clone https://github.com/lh3/minimap2.git "$MINIMAP_DIR"
    echo "Building Minimap2..."
    (cd "$MINIMAP_DIR" && make)
else
    echo "Minimap2 is already installed."
fi

# Ensure pip is installed
if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed. Please install pip and try again."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment and install Python dependencies
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing required packages..."
pip install --upgrade pip --break-system-packages
pip install -r "$SCRIPTS_DIR/requirements.txt" --break-system-packages

# Deactivate virtual environment
deactivate

# Copy the reference file to the Minimap2 test folder
echo "Copying reference file to Minimap2 test folder..."
cp "$REFERENCE_FILE" "$MINIMAP_DIR/test/template.fasta"

echo "Setup completed successfully. You can now run 'run_analysis.sh' without any parameters."
