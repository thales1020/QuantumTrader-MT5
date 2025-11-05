@echo off
REM Export all PlantUML diagrams to PNG using PlantUML CLI

echo ========================================
echo Exporting All UML Diagrams to PNG
echo ========================================
echo.

set DIAGRAMS_DIR=C:\github\ML-SuperTrend-MT5\docs\uml_diagrams
set OUTPUT_DIR=%DIAGRAMS_DIR%\png_exports

REM Create output directory if not exists
if not exist "%OUTPUT_DIR%" (
    mkdir "%OUTPUT_DIR%"
    echo Created output directory: %OUTPUT_DIR%
    echo.
)

echo Diagrams directory: %DIAGRAMS_DIR%
echo Output directory: %OUTPUT_DIR%
echo.

REM Check if PlantUML JAR exists
set PLANTUML_JAR=C:\plantuml\plantuml.jar

if exist "%PLANTUML_JAR%" (
    echo Found PlantUML JAR: %PLANTUML_JAR%
    echo.
    echo Exporting diagrams...
    echo.
    
    REM Export all .puml files
    java -jar "%PLANTUML_JAR%" -tpng "%DIAGRAMS_DIR%\*.puml" -o "%OUTPUT_DIR%"
    
    echo.
    echo Export complete!
    echo Check: %OUTPUT_DIR%
) else (
    echo PlantUML JAR not found at: %PLANTUML_JAR%
    echo.
    echo Alternative method:
    echo 1. In VS Code, press Ctrl+Shift+P
    echo 2. Type: PlantUML: Export Workspace Diagrams
    echo 3. Select PNG format
    echo 4. Choose output directory
    echo.
    echo Or download PlantUML JAR from:
    echo https://plantuml.com/download
)

echo.
echo ========================================
echo Available Diagrams:
echo ========================================
dir /b "%DIAGRAMS_DIR%\*.puml"

echo.
echo Press any key to exit...
pause >nul
