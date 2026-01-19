@echo off
REM Human-like Typing Tool Launcher for Windows
REM Automatically sets up virtual environment and runs the tool
REM Requires Python 3.10 or higher

setlocal enabledelayedexpansion

echo === Human-like Typing Tool ===

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv_human_typer"
set "PYTHON_SCRIPT=%SCRIPT_DIR%human_typer.py"

REM Try to find Python 3.10+ in order of preference
set "PYTHON_CMD="

REM Check py launcher first (most reliable on Windows)
where py >nul 2>&1
if %errorlevel% equ 0 (
    REM Try specific versions with py launcher
    py -3.12 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=py -3.12"
        goto :found_python
    )
    py -3.11 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=py -3.11"
        goto :found_python
    )
    py -3.10 --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=py -3.10"
        goto :found_python
    )
)

REM Check direct python commands
where python3.12 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3.12"
    goto :found_python
)

where python3.11 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3.11"
    goto :found_python
)

where python3.10 >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python3.10"
    goto :found_python
)

REM Check default python and verify version
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
    for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do (
        set "PY_MAJOR=%%a"
        set "PY_MINOR=%%b"
    )
    if !PY_MAJOR! geq 3 if !PY_MINOR! geq 10 (
        set "PYTHON_CMD=python"
        goto :found_python
    )
)

REM No suitable Python found
echo Error: Python 3.10 or higher is required
echo.
echo Please install Python 3.10+ from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:found_python
REM Get and display Python version
for /f "tokens=*" %%v in ('!PYTHON_CMD! --version 2^>^&1') do set "PYTHON_VERSION=%%v"
echo Using: !PYTHON_VERSION!

REM Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    !PYTHON_CMD! -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Check and install dependencies
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    set DEPS_INSTALLED=false
) else (
    python -c "import pyautogui" >nul 2>&1
    if %errorlevel% neq 0 (
        set DEPS_INSTALLED=false
    ) else (
        python -c "import pyperclip" >nul 2>&1
        if %errorlevel% neq 0 (
            set DEPS_INSTALLED=false
        ) else (
            set DEPS_INSTALLED=true
        )
    )
)

if "!DEPS_INSTALLED!"=="false" (
    echo Installing dependencies...
    pip install --upgrade pip -q
    pip install PyQt5 pyautogui pyperclip -q
    if !errorlevel! neq 0 (
        echo Error: Failed to install dependencies
        call deactivate
        pause
        exit /b 1
    )
    echo Dependencies installed
)

REM Run the tool
echo Starting Human-like Typing Tool...
echo.
python "%PYTHON_SCRIPT%"

REM Deactivate virtual environment
call deactivate

endlocal
