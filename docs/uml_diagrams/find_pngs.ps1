# Script to find PNG files after PlantUML export

Write-Host "=== TIM FILE PNG SAU KHI EXPORT ===" -ForegroundColor Cyan
Write-Host ""

$baseDir = "C:\github\ML-SuperTrend-MT5"

Write-Host "Searching for PNG files in project..." -ForegroundColor Yellow
Write-Host ""

# Tim tat ca PNG files
$allPngs = Get-ChildItem $baseDir -Filter "*.png" -Recurse -ErrorAction SilentlyContinue

if ($allPngs.Count -eq 0) {
    Write-Host "KHONG TIM THAY FILE PNG NAO!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Cac file PNG chua duoc tao." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "DE EXPORT:" -ForegroundColor Green
    Write-Host "1. Mo file .puml trong VS Code" -ForegroundColor White
    Write-Host "2. Nhan Ctrl+Shift+P" -ForegroundColor White
    Write-Host "3. Go: PlantUML: Export Current Diagram" -ForegroundColor Cyan
    Write-Host "4. Chon format: png" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "TIM THAY $($allPngs.Count) FILE PNG:" -ForegroundColor Green
    Write-Host ""
    
    # Nhom theo thu muc
    $grouped = $allPngs | Group-Object DirectoryName
    
    foreach ($group in $grouped) {
        Write-Host "Thu muc: $($group.Name)" -ForegroundColor Yellow
        foreach ($file in $group.Group) {
            $size = [math]::Round($file.Length / 1KB, 2)
            Write-Host "  - $($file.Name) ($size KB) - $($file.LastWriteTime)" -ForegroundColor White
        }
        Write-Host ""
    }
}

Write-Host "=== VI TRI CO THE CO PNG FILES ===" -ForegroundColor Cyan
Write-Host ""

$possibleLocations = @(
    "$baseDir\docs\uml_diagrams",
    "$baseDir\docs\uml_diagrams\png_exports",
    "$baseDir\out",
    "$baseDir\out\docs\uml_diagrams"
)

foreach ($loc in $possibleLocations) {
    if (Test-Path $loc) {
        $pngCount = (Get-ChildItem $loc -Filter "*.png" -Recurse -ErrorAction SilentlyContinue).Count
        if ($pngCount -gt 0) {
            Write-Host "[X] $loc - $pngCount files" -ForegroundColor Green
        } else {
            Write-Host "[ ] $loc - Empty" -ForegroundColor Gray
        }
    } else {
        Write-Host "[ ] $loc - Not exists" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=== HUONG DAN EXPORT ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "CACH 1: Export 1 file" -ForegroundColor Yellow
Write-Host "  Ctrl+Shift+P -> PlantUML: Export Current Diagram -> png" -ForegroundColor White
Write-Host ""
Write-Host "CACH 2: Export tat ca" -ForegroundColor Yellow  
Write-Host "  Ctrl+Shift+P -> PlantUML: Export Workspace Diagrams -> png" -ForegroundColor White
Write-Host ""
