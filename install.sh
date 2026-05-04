#!/bin/bash

# Fcitx5 Niri DMS - Easy Installer
echo "--- Fcitx5 Niri DMS Installer ---"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it first."
    exit 1
fi

# Run the generator
python3 "$(dirname "$0")/generate.py"
