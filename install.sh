#!/bin/bash

# PlexStreamBot Automated Installer for Linux
echo "==========================="
echo "  PlexStreamBot Installer"
echo "==========================="

# Step 1: Check for Python Installation
echo "Checking if Python is installed..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Installing Python3..."
    sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
else
    echo "✅ Python3 is installed."
fi

# Step 2: Check for Pip Installation
echo "Checking if pip is installed..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Installing pip3..."
    sudo apt-get update && sudo apt-get install -y python3-pip
else
    echo "✅ pip3 is installed."
fi

# Step 3: Check for FFmpeg Installation
echo "Checking if FFmpeg is installed..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Installing FFmpeg..."
    sudo apt-get update && sudo apt-get install -y ffmpeg
else
    echo "✅ FFmpeg is installed."
fi

# Step 4: Create a Virtual Environment
echo "Creating a Python virtual environment..."
if [ ! -d "plex_bot_env" ]; then
    python3 -m venv plex_bot_env
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment already exists."
fi

# Activate the virtual environment
source plex_bot_env/bin/activate

# Step 5: Install Dependencies
echo "Installing required Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Configure Environment Variables
echo "Checking for configuration.env file..."
if [ ! -f configuration.env ]; then
    echo "Creating configuration.env file..."
    cp configuration.env.example configuration.env
    echo "✅ configuration.env file created. Please edit it to add your Plex and Discord credentials."
else
    echo "✅ configuration.env file already exists."
fi

# Step 7: Test the Bot
echo "Testing the bot setup..."
if python plex_discord_bot.py --help &> /dev/null; then
    echo "✅ Bot script is ready to run."
else
    echo "❌ There seems to be an issue with the bot script. Please check the logs."
fi

# Step 8: Run the Bot
read -p "Do you want to start the PlexStreamBot now? (y/n): " start_bot
if [[ "$start_bot" =~ ^[Yy]$ ]]; then
    echo "Starting the bot..."
    python plex_discord_bot.py
else
    echo "You can start the bot later by activating the virtual environment and running:"
    echo "  source plex_bot_env/bin/activate"
    echo "  python plex_discord_bot.py"
fi

echo "==========================="
echo "  PlexStreamBot Installed"
echo "==========================="