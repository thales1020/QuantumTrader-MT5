@echo off
REM ========================================
REM CLEANUP PROJECT - Remove Redundant Files
REM ========================================

echo.
echo ========================================
echo CLEANING UP PROJECT
echo ========================================
echo.

set TOTAL_FILES=0
set TOTAL_SIZE=0

REM 1. Remove duplicate config.json in root
if exist "config.json" (
    echo [1/5] Removing duplicate config.json...
    del /F /Q "config.json"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ Removed: config.json ^(duplicate, use config/config.json^)
        set /A TOTAL_FILES+=1
    )
) else (
    echo    ℹ️ config.json not found ^(already removed^)
)

echo.

REM 2. Remove old reorganize_project.py
if exist "reorganize_project.py" (
    echo [2/5] Removing old reorganize_project.py...
    del /F /Q "reorganize_project.py"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ Removed: reorganize_project.py ^(duplicate, use organize_project.py^)
        set /A TOTAL_FILES+=1
    )
) else (
    echo    ℹ️ reorganize_project.py not found ^(already removed^)
)

echo.

REM 3. Clean old chart images
echo [3/5] Cleaning old chart images in statistic/...
if exist "statistic\*.png" (
    for %%F in (statistic\*.png) do (
        del /F /Q "%%F"
        echo    ✅ Removed: %%~nxF
        set /A TOTAL_FILES+=1
    )
) else (
    echo    ℹ️ No PNG files found in statistic/
)

echo.

REM 4. Clean large old log files
echo [4/5] Cleaning large old log files...
if exist "logs\ict_bot_20251016.log" (
    del /F /Q "logs\ict_bot_20251016.log"
    echo    ✅ Removed: logs\ict_bot_20251016.log ^(632 KB^)
    set /A TOTAL_FILES+=1
)
if exist "logs\ict_bot_smc.log" (
    del /F /Q "logs\ict_bot_smc.log"
    echo    ✅ Removed: logs\ict_bot_smc.log ^(8.8 MB^)
    set /A TOTAL_FILES+=1
)
if exist "logs\supertrend_bot.log" (
    del /F /Q "logs\supertrend_bot.log"
    echo    ✅ Removed: logs\supertrend_bot.log ^(162 KB^)
    set /A TOTAL_FILES+=1
)

if %TOTAL_FILES% EQU 0 (
    echo    ℹ️ No large log files found
)

echo.

REM 5. Clean old reports (older than 7 days)
echo [5/5] Cleaning old reports...
python scripts/automation/rotate_logs.py --clean-reports --max-age 7 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    ✅ Old reports cleaned via rotate_logs.py
) else (
    echo    ⚠️ Could not run rotate_logs.py, cleaning manually...
    
    REM Manual cleanup of old reports
    if exist "reports\*_20251016_*.csv" del /F /Q "reports\*_20251016_*.csv"
    if exist "reports\*_20251016_*.json" del /F /Q "reports\*_20251016_*.json"
    echo    ✅ Cleaned old reports from 2024-10-16
)

echo.
echo ========================================
echo CLEANUP COMPLETE
echo ========================================
echo.
echo Files removed: %TOTAL_FILES%+
echo Estimated space saved: ~32 MB
echo.
echo ℹ️ Note: Some reports may have been kept if less than 7 days old
echo.

pause
