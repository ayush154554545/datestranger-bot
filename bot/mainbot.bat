@echo off
title Date Stranger Bot - Main Production
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

echo ===================================================
echo       DATE STRANGER BOT - MAIN (PRODUCTION)
echo ===================================================
echo.

echo [1/3] Checking Python environment...

set "PYTHON_EXEC="
for /f "delims=" %%p in ('where python 2^>nul') do (
    echo %%p | findstr /i "WindowsApps" >nul
    if errorlevel 1 (
        "%%p" -c "import sys" >nul 2>&1
        if not errorlevel 1 (
            set "PYTHON_EXEC=%%p"
            goto :PYTHON_READY
        )
    )
)

py -3 -c "import sys; print('ok')" >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%p in ('py -3 -c "import sys; print(sys.executable)"') do set "PYTHON_EXEC=%%p"
    if not defined PYTHON_EXEC goto :CHECK_MAIN_FALLBACKS
) else (
    goto :CHECK_MAIN_FALLBACKS
)

:CHECK_MAIN_FALLBACKS

:CHECK_MAIN_FALLBACKS
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" set "PYTHON_EXEC=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" & goto :PYTHON_READY
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python311\python.exe" & goto :PYTHON_READY
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python312\python.exe" & goto :PYTHON_READY
if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python310\python.exe" & goto :PYTHON_READY
if exist "C:\Python311\python.exe" set "PYTHON_EXEC=C:\Python311\python.exe" & goto :PYTHON_READY
if exist "C:\Python312\python.exe" set "PYTHON_EXEC=C:\Python312\python.exe" & goto :PYTHON_READY
if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_EXEC=%ProgramFiles%\Python311\python.exe" & goto :PYTHON_READY
if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_EXEC=%ProgramFiles%\Python312\python.exe" & goto :PYTHON_READY

:: Python was not found. Download and install automatically.
echo.
echo ===================================================
echo Python was NOT found on your system!
echo Automatically downloading and installing Python...
echo ===================================================
echo.

winget --version >nul 2>&1
if %errorlevel% neq 0 goto :USE_POWERSHELL_INSTALL

echo Attempting installation via Windows Package Manager (winget)...
winget install --id Python.Python.3.11 -e --silent --accept-source-agreements --accept-package-agreements

:: Re-check standard paths after winget
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python311\python.exe" & goto :PYTHON_READY
if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_EXEC=%ProgramFiles%\Python311\python.exe" & goto :PYTHON_READY
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python312\python.exe" & goto :PYTHON_READY

:USE_POWERSHELL_INSTALL
echo Downloading official Python installer...
set "INSTALLER_PATH=%TEMP%\python_setup_3.11.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Downloading Python 3.11 setup...'; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', '$env:INSTALLER_PATH')"

if not exist "%INSTALLER_PATH%" goto :INSTALL_FAILED

echo Installing Python silently...
"%INSTALLER_PATH%" /quiet PrependPath=1 Include_test=0 SimpleInstall=1
del "%INSTALLER_PATH%" >nul 2>&1

:CHECK_AFTER_INSTALL
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python311\python.exe" & goto :PYTHON_READY
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_EXEC=%LocalAppData%\Programs\Python\Python312\python.exe" & goto :PYTHON_READY
if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_EXEC=%ProgramFiles%\Python311\python.exe" & goto :PYTHON_READY
if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_EXEC=%ProgramFiles%\Python312\python.exe" & goto :PYTHON_READY
if exist "C:\Python311\python.exe" set "PYTHON_EXEC=C:\Python311\python.exe" & goto :PYTHON_READY

python --version >nul 2>&1
if %errorlevel% equ 0 set "PYTHON_EXEC=python" & goto :PYTHON_READY

:INSTALL_FAILED
echo ERROR: Python installation finished, but python executable could not be resolved automatically.
echo Please restart your command prompt window or computer.
pause
exit /b 1

:PYTHON_READY
echo Python environment verified.
echo.

echo [2/3] Inspecting and downloading required libraries...
if not exist "requirements.txt" goto :SKIP_REQUIREMENTS

echo Verifying and installing dependencies from requirements.txt...
"%PYTHON_EXEC%" -m pip install --upgrade pip
"%PYTHON_EXEC%" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Failed to install some dependencies. Attempting to run anyway...
)
goto :START_BOT

:SKIP_REQUIREMENTS
echo WARNING: requirements.txt not found in current directory! Skipping dependency check.

:START_BOT
echo.
echo [3/3] Launching Main Bot with .env environment...
set "ENV_FILE=.env"

if not exist "%ENV_FILE%" (
    echo ERROR: Environment file "%ENV_FILE%" was not found!
    echo Please create "%ENV_FILE%" before starting the main bot.
    echo.
    pause
    exit /b 1
)

echo Using environment file: %ENV_FILE%
echo Starting bot.py...
echo.

"%PYTHON_EXEC%" bot.py

if %errorlevel% neq 0 (
    echo.
    echo Bot process ended with error code %errorlevel%.
    pause
)


