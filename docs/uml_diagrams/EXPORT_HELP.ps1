# Simple instruction to export PlantUML diagrams to PNG

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HUONG DAN EXPORT PLANTUML DIAGRAMS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "HIEN TAI: File PNG chua duoc tao" -ForegroundColor Yellow
Write-Host ""

Write-Host "CACH 1: Export bang VS Code (De nhat)" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "File dang mo: QuantumTrader_Main_UseCase.puml" -ForegroundColor White
Write-Host ""
Write-Host "Buoc 1: Right-click vao file trong editor" -ForegroundColor Yellow
Write-Host "Buoc 2: Tim menu 'PlantUML' hoac 'Export'" -ForegroundColor Yellow  
Write-Host "Buoc 3: Chon 'Export Current Diagram'" -ForegroundColor Yellow
Write-Host "Buoc 4: File PNG se xuat hien!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Hoac:" -ForegroundColor White
Write-Host "Buoc 1: Nhan Alt+D de preview" -ForegroundColor Yellow
Write-Host "Buoc 2: Trong preview window, tim nut Export/Save" -ForegroundColor Yellow
Write-Host "Buoc 3: Click de luu PNG" -ForegroundColor Yellow
Write-Host ""

Write-Host "CACH 2: Export bang PlantUML Server (Online)" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "1. Mo trinh duyet web" -ForegroundColor Yellow
Write-Host "2. Vao: http://www.plantuml.com/plantuml/uml/" -ForegroundColor Cyan
Write-Host "3. Copy noi dung file .puml" -ForegroundColor Yellow
Write-Host "4. Paste vao trang web" -ForegroundColor Yellow
Write-Host "5. Diagram se render tu dong" -ForegroundColor Yellow
Write-Host "6. Click nut PNG de download" -ForegroundColor Yellow
Write-Host ""

Write-Host "CACH 3: Export tat ca bang Command Line" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Tai PlantUML JAR tu: https://plantuml.com/download" -ForegroundColor Cyan
Write-Host "Sau do chay:" -ForegroundColor Yellow
Write-Host ""
Write-Host "java -jar plantuml.jar -tpng *.puml" -ForegroundColor White
Write-Host ""

Write-Host "VI TRI FILE PNG SAU KHI EXPORT:" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "- Default: Cung thu muc voi file .puml" -ForegroundColor White
Write-Host "  C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\" -ForegroundColor Cyan
Write-Host ""
Write-Host "- Hoac: Thu muc 'out'" -ForegroundColor White  
Write-Host "  C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\out\" -ForegroundColor Cyan
Write-Host ""

Write-Host "SAU KHI EXPORT, CHAY LENH NAY DE TIM:" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Get-ChildItem . -Filter *.png -Recurse" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "THU NGAY BAY GIO:" -ForegroundColor Yellow
Write-Host "1. Right-click trong editor" -ForegroundColor White
Write-Host "2. Tim menu PlantUML" -ForegroundColor White
Write-Host "3. Export Current Diagram" -ForegroundColor White
Write-Host ""
