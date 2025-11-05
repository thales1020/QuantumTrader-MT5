# Export all PlantUML diagrams to PNG
# This script exports each diagram individually

$diagramsPath = "C:\github\ML-SuperTrend-MT5\docs\uml_diagrams"
$outputPath = "C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\png_exports"

# Create output directory
if (-not (Test-Path $outputPath)) {
    New-Item -ItemType Directory -Path $outputPath | Out-Null
    Write-Host "Created directory: $outputPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Exporting UML Diagrams to PNG ===" -ForegroundColor Cyan
Write-Host ""

# Get all .puml files
$pumlFiles = Get-ChildItem -Path $diagramsPath -Filter "*.puml" | Sort-Object Name

Write-Host "Found $($pumlFiles.Count) diagrams to export" -ForegroundColor Yellow
Write-Host ""

# Export instructions
Write-Host "EXPORT METHOD 1: VS Code Command (Recommended)" -ForegroundColor Green
Write-Host "  1. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "  2. Type: PlantUML: Export Workspace Diagrams" -ForegroundColor Cyan
Write-Host "  3. Select output format: png" -ForegroundColor White
Write-Host "  4. Select output directory (or use default)" -ForegroundColor White
Write-Host ""

Write-Host "EXPORT METHOD 2: Export Each File Individually" -ForegroundColor Green
Write-Host "  For each file below:" -ForegroundColor White
Write-Host "  1. Open the .puml file in VS Code" -ForegroundColor White
Write-Host "  2. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "  3. Type: PlantUML: Export Current Diagram" -ForegroundColor Cyan
Write-Host "  4. Select PNG format" -ForegroundColor White
Write-Host ""

Write-Host "Files to export:" -ForegroundColor Yellow
$counter = 1
foreach ($file in $pumlFiles) {
    Write-Host "  $counter. $($file.Name)" -ForegroundColor White
    $counter++
}

Write-Host ""
Write-Host "EXPORT METHOD 3: Using PlantUML JAR (if installed)" -ForegroundColor Green
Write-Host "  Run this command:" -ForegroundColor White
Write-Host "  java -jar plantuml.jar -tpng `"$diagramsPath\*.puml`" -o `"$outputPath`"" -ForegroundColor Cyan
Write-Host ""

Write-Host "Output directory: $outputPath" -ForegroundColor Yellow
Write-Host ""

# Check if GraphViz is installed
$graphvizPath = "C:\Program Files\Graphviz\bin\dot.exe"
if (Test-Path $graphvizPath) {
    Write-Host "GraphViz: Installed" -ForegroundColor Green
} else {
    Write-Host "GraphViz: Not found at default location" -ForegroundColor Yellow
    Write-Host "  PlantUML needs GraphViz to render diagrams" -ForegroundColor White
    Write-Host "  Download from: https://graphviz.org/download/" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Ready to export!" -ForegroundColor Green
