#!/bin/bash

APP_NAME="BlueSync"
APP_EXEC="bluesync"
APP_DIR=$(pwd)
VENV_DIR="$APP_DIR/venv"
DESKTOP_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"

echo "Starting uninstallation of $APP_NAME..."

# Step 1: Remove the virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Removing virtual environment..."
    rm -rf "$VENV_DIR"
else
    echo "Virtual environment not found. Skipping..."
fi

# Step 2: Remove the symbolic link for terminal execution
if [ -L "/usr/local/bin/$APP_EXEC" ]; then
    echo "Removing symbolic link..."
    sudo rm "/usr/local/bin/$APP_EXEC"
else
    echo "Symbolic link not found or not a valid link. Skipping..."
fi

# Step 3: Remove the desktop entry
if [ -f "$DESKTOP_ENTRY" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_ENTRY"
else
    echo "Desktop entry not found. Skipping..."
fi

# Step 4: Notify the user of successful uninstallation
echo "$APP_NAME has been uninstalled successfully!"