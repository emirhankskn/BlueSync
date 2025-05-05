#!/bin/bash
# filepath: /home/fade/Desktop/GitHub/BlueSync/install.sh

APP_NAME="BlueSync"
APP_EXEC="bluesync"
APP_DIR=$(pwd)
VENV_DIR="$APP_DIR/venv"
DESKTOP_ENTRY="$HOME/.local/share/applications/$APP_NAME.desktop"

echo "Starting installation of $APP_NAME..."

# Step 1: Check and install Python3 and pip if not installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing..."
    sudo apt update && sudo apt install -y python3 python3-pip
fi

# Step 1.1: Install system dependencies for dbus-python
if ! dpkg -s libdbus-1-dev &> /dev/null; then
    echo "Installing system dependencies for dbus-python..."
    sudo apt update && sudo apt install -y libdbus-1-dev
fi

# Step 2: Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Step 3: Activate the virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

# Step 4: Create a wrapper script for terminal execution
if [ -f "$VENV_DIR/bin/python3" ]; then
    echo "Creating executable launcher script for terminal execution..."
    sudo tee /usr/local/bin/$APP_EXEC > /dev/null <<EOL
#!/bin/bash
"$VENV_DIR/bin/python3" "$APP_DIR/main.py" "\$@"
EOL
    sudo chmod +x /usr/local/bin/$APP_EXEC
    echo "Launcher script created successfully."
else
    echo "Error: Virtual environment Python interpreter not found at $VENV_DIR/bin/python3. Please ensure the virtual environment is created correctly."
    exit 1
fi

# Step 4.1: Verify the launcher script
if [ -f "/usr/local/bin/$APP_EXEC" ]; then
    echo "Launcher script exists: /usr/local/bin/$APP_EXEC"
    if [ -x "/usr/local/bin/$APP_EXEC" ]; then
        echo "Launcher script verification successful."
    else
        echo "Warning: Script exists but is not executable. Fixing permissions..."
        sudo chmod +x "/usr/local/bin/$APP_EXEC"
        echo "Permissions fixed."
    fi
else
    echo "Error: Launcher script was not created successfully."
    echo "Debugging Information:"
    echo "- Current User: $(whoami)"
    echo "- Script Path: /usr/local/bin/$APP_EXEC"
    echo "- Directory Permissions: $(ls -ld /usr/local/bin)"
    exit 1
fi

# Step 5: Create a desktop entry for the application
echo "Creating desktop entry..."
cat > "$DESKTOP_ENTRY" <<EOL
[Desktop Entry]
Name=$APP_NAME
Exec=$APP_EXEC
Type=Application
Terminal=false
Icon=$APP_DIR/components/assets/bluetooth.png
Categories=Utility;
EOL

# Step 6: Make the desktop entry executable
chmod +x "$DESKTOP_ENTRY"

# Step 7: Notify the user of successful installation
echo "$APP_NAME has been installed successfully!"
echo "You can now run the application from the application menu or by typing '$APP_EXEC' in the terminal."
