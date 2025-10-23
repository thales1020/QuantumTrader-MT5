@echo off
REM ========================================
REM Auto-Start Trading Bot with Restart
REM ========================================

echo.
echo ========================================
echo Starting ML-SuperTrend MT5 Bot
echo ========================================
echo.

REM Configuration
set BOT_NAME=ML-SuperTrend Bot
set PYTHON_PATH=python
set BOT_SCRIPT=scripts\runners\run_bot.py
set ACCOUNT=demo
set SYMBOL=BTCUSDm
set INTERVAL=60
set ROOT_DIR=%~dp0..\..

REM Change to project root directory
cd /d %ROOT_DIR%

REM Check if Python is available
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Create logs directory if not exists
if not exist logs mkdir logs

REM Start bot with auto-restart
:start
echo.
echo [%date% %time%] Starting %BOT_NAME%...
echo Account: %ACCOUNT%
echo Symbol: %SYMBOL%
echo Interval: %INTERVAL% seconds
echo.

REM Run bot and capture exit code
%PYTHON_PATH% %BOT_SCRIPT% --account %ACCOUNT% --symbol %SYMBOL% --interval %INTERVAL% >> logs\bot_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

REM Check if stopped by user (Ctrl+C) or crashed
if errorlevel 1 (
    echo.
    echo [%date% %time%] Bot stopped with error code %errorlevel%
    echo Restarting in 30 seconds...
    timeout /t 30 /nobreak
    goto start
) else (
    echo.
    echo [%date% %time%] Bot stopped normally
    choice /C YN /T 10 /D Y /M "Restart bot? (Y/N, auto-yes in 10s)"
    if errorlevel 2 goto end
    goto start
)

:end
echo.
echo ========================================
echo Bot stopped by user
echo ========================================
pause
