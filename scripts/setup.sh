#!/bin/bash

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
source "$SCRIPT_DIR/config.env"

# Ensure the results directory exists
if [ ! -d "$RESULTS_DIR" ]; then
    echo "Creating results directory at $RESULTS_DIR..."
    mkdir -p "$RESULTS_DIR"
else
    echo "Results directory already exists."
fi

# Create tools directory if not exists
if [ ! -d "$TOOLS_DIR" ]; then
    echo "Creating tools directory at $TOOLS_DIR..."
    mkdir -p "$TOOLS_DIR"
else
    echo "Tools directory already exists."
fi

# Install Minimap2 in tools directory
if [ ! -d "$MINIMAP_DIR" ]; then
    echo "Cloning Minimap2 repository into $MINIMAP_DIR..."
    git clone https://github.com/lh3/minimap2.git "$MINIMAP_DIR"
    echo "Building Minimap2..."
    (cd "$MINIMAP_DIR" && make)
else
    echo "Minimap2 is already installed in $MINIMAP_DIR."
fi

# Install Samtools in tools directory
SAMTOOLS_DIR="$TOOLS_DIR/samtools"
if [ ! -f "$SAMTOOLS_DIR/samtools" ]; then
    echo "Samtools not found. Installing in $TOOLS_DIR..."
    SAMTOOLS_VERSION="1.19.2"
    SAMTOOLS_TAR="samtools-$SAMTOOLS_VERSION.tar.bz2"
    SAMTOOLS_SRC_DIR="samtools-$SAMTOOLS_VERSION"

    # Download the tar.bz2 file
    if [ ! -f "$SAMTOOLS_TAR" ]; then
        echo "Downloading Samtools..."
        wget "https://github.com/samtools/samtools/releases/download/$SAMTOOLS_VERSION/$SAMTOOLS_TAR"
    fi

    # Extract, compile, and install locally in tools directory
    tar -xvjf "$SAMTOOLS_TAR"
    mv "$SAMTOOLS_SRC_DIR" "$SAMTOOLS_DIR"
    cd "$SAMTOOLS_DIR" || exit
    ./configure --prefix="$SAMTOOLS_DIR"
    make
    make install
    cd "$SCRIPT_DIR"

    # Clean up
    rm -f "$SAMTOOLS_TAR"
    echo "Samtools installed successfully in $SAMTOOLS_DIR."
else
    echo "Samtools is already installed in $TOOLS_DIR."
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip and install required Python packages
echo "Upgrading pip and installing required packages..."
pip install --upgrade pip

# Check for the requirements file
if [ -f "$SCRIPTS_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPTS_DIR/requirements.txt"
    echo "Python packages installed from requirements.txt."
else
    echo "Warning: requirements.txt not found in $SCRIPTS_DIR. No Python packages installed."
fi

# Deactivate the virtual environment after setup
deactivate

echo "Setup completed successfully."
