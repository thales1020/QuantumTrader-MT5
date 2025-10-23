@echo off
:: =========================================
:: AUTO-RESTART BOT SCRIPT FOR WINDOWS VPS
:: =========================================
title ML-SuperTrend Auto-Restart Bot

:: Configuration
set BOT_DIR=C:\ML-SuperTrend-MT5
set PYTHON_EXE=%BOT_DIR%\venv\Scripts\python.exe
set BOT_SCRIPT=scripts\runners\run_bot.py
set ACCOUNT=demo
set SYMBOL=BTCUSDm
set INTERVAL=60
set LOG_FILE=%BOT_DIR%\logs\auto_restart.log

:: Change to bot directory
cd /d %BOT_DIR%

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Log startup
echo ============================================ >> %LOG_FILE%
echo Bot Started: %DATE% %TIME% >> %LOG_FILE%
echo ============================================ >> %LOG_FILE%

:loop
    echo.
    echo ========================================
    echo Starting ML-SuperTrend Bot
    echo Time: %DATE% %TIME%
    echo Account: %ACCOUNT%
    echo Symbol: %SYMBOL%
    echo ========================================
    echo.
    
    :: Log to file
    echo [%DATE% %TIME%] Starting bot... >> %LOG_FILE%
    
    :: Run bot
    %PYTHON_EXE% %BOT_SCRIPT% --account %ACCOUNT% --symbol %SYMBOL% --interval %INTERVAL%
    
    :: Get exit code
    set EXIT_CODE=%ERRORLEVEL%
    
    :: Log exit
    echo [%DATE% %TIME%] Bot stopped with exit code: %EXIT_CODE% >> %LOG_FILE%
    
    :: If clean exit (0), don't restart
    if %EXIT_CODE%==0 (
        echo Clean exit detected. Not restarting.
        echo [%DATE% %TIME%] Clean exit - not restarting >> %LOG_FILE%
        pause
        exit /b 0
    )
    
    :: Otherwise, restart after delay
    echo.
    echo ========================================
    echo Bot crashed or stopped unexpectedly!
    echo Exit Code: %EXIT_CODE%
    echo Restarting in 30 seconds...
    echo ========================================
    echo.
    
    timeout /t 30 /nobreak
    
    echo Restarting bot now...
    goto loop
