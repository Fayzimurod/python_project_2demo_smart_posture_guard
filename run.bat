@echo off
chcp 65001 > nul
echo ===================================================
echo [1/3] Checking and preparing portable Python...
echo ===================================================

if not exist "python_portable" (
    echo Downloading portable Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip' -OutFile 'python_embed.zip'"
    if errorlevel 1 (
        echo [ERROR] Failed to download Python. Check your internet connection.
        pause
        exit /b 1
    )

    echo Extracting...
    powershell -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python_portable'"
    if errorlevel 1 (
        echo [ERROR] Failed to extract Python archive.
        pause
        exit /b 1
    )
    del python_embed.zip

    echo Configuring pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_portable\get-pip.py'"
    if errorlevel 1 (
        echo [ERROR] Failed to download get-pip.py.
        pause
        exit /b 1
    )

    :: Allow third-party package imports in the embedded distribution
    :: Quotes prevent redirect ambiguity on older Windows versions
    echo python311.zip> "python_portable\python311._pth"
    echo .>> "python_portable\python311._pth"
    echo import site>> "python_portable\python311._pth"

    python_portable\python.exe python_portable\get-pip.py --no-warn-script-location
    if errorlevel 1 (
        echo [ERROR] pip installation failed.
        pause
        exit /b 1
    )
)

echo ===================================================
echo [2/3] Installing required libraries...
echo ===================================================
python_portable\python.exe -m pip install -r requirements.txt --no-warn-script-location
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check requirements.txt and your connection.
    pause
    exit /b 1
)

echo ===================================================
echo [3/3] Starting Smart Posture Guard...
echo ===================================================
python_portable\python.exe main.py

pause
