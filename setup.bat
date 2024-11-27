@echo off
echo ===========================
echo   PlexStreamBot Installer
echo ===========================

:: Step 1: Check for Python Installation
echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python3 is not installed. Please install Python 3.8 or higher and try again.
    pause
    exit /b
) else (
    echo ✅ Python3 is installed.
)

:: Step 2: Check for Pip Installation
echo Checking if pip is installed...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pip is not installed. Installing Pip...
    python -m ensurepip --upgrade
) else (
    echo ✅ Pip is installed.
)

:: Step 3: Check for FFmpeg Installation
echo Checking if FFmpeg is installed...
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FFmpeg is not installed. Installing FFmpeg...
    set "FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n5.1.2-latest-win64-lgpl.zip"
    set "FFMPEG_DIR=%cd%\ffmpeg"

    :: Download FFmpeg (requires PowerShell)
    powershell -Command "Invoke-WebRequest -Uri %FFMPEG_URL% -OutFile ffmpeg.zip"
    if exist ffmpeg.zip (
        echo ✅ FFmpeg downloaded successfully.
        mkdir %FFMPEG_DIR%
        powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath %FFMPEG_DIR% -Force"
        del ffmpeg.zip
        setx PATH "%FFMPEG_DIR%\ffmpeg-n5.1.2-latest-win64-lgpl\bin;%PATH%"
        echo ✅ FFmpeg installed and added to PATH.
    ) else (
        echo ❌ Failed to download FFmpeg. Please check your internet connection.
        pause
        exit /b
    )
) else (
    echo ✅ FFmpeg is installed.
)

:: Step 4: Create a Virtual Environment
echo Creating a Python virtual environment...
if not exist plex_bot_env (
    python -m venv plex_bot_env
    echo ✅ Virtual environment created.
) else (
    echo ✅ Virtual environment already exists.
)

:: Step 5: Activate the Virtual Environment and Install Dependencies
echo Activating the virtual environment and installing dependencies...
call plex_bot_env\Scripts\activate
pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✅ Dependencies installed.
) else (
    echo ❌ requirements.txt not found. Please ensure it exists in the same directory as this script.
    pause
    exit /b
)

:: Step 6: Configure Environment Variables
echo Checking for configuration.env file...
if not exist configuration.env (
    copy configuration.env.example configuration.env >nul
    echo ✅ configuration.env file created. Please edit it to add your Plex and Discord credentials.
) else (
    echo ✅ configuration.env file already exists.
)

:: Step 7: Test the Bot
echo Testing the bot setup...
python plex_discord_bot.py --help >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ There seems to be an issue with the bot script. Please check the logs or your configuration.
) else (
    echo ✅ Bot script is ready to run.
)

:: Step 8: Run the Bot
set /p start_bot=Do you want to start the PlexStreamBot now? (y/n): 
if /i "%start_bot%"=="y" (
    echo Starting the bot...
    python plex_discord_bot.py
) else (
    echo You can start the bot later by activating the virtual environment and running:
    echo   call plex_bot_env\Scripts\activate
    echo   python plex_discord_bot.py
)

echo ===========================
echo   PlexStreamBot Installed
echo ===========================
pause