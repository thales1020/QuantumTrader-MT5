#  PHÂN TÍCH FILES DƯ THỪA TRONG PROJECT

## 📅 Ngày phân tích: 18 Tháng 10, 2025

---

##  FILES DƯ THỪA CẦN XÓA

### 1. **DUPLICATE FILES** 

#### `config.json` (root) - **DƯ THỪA**
- **Vị trí**: `C:\github\ML-SuperTrend-MT5\config.json` (1.14 KB)
- **Duplicate of**: `config/config.json` (5.72 KB)
- **Lý do xóa**: Đã có config.json trong `config/` folder
- **Action**:  **XÓA**

#### `reorganize_project.py` (root) - **DƯ THỪA**
- **Vị trí**: `C:\github\ML-SuperTrend-MT5\reorganize_project.py` (9.01 KB)
- **Duplicate of**: `organize_project.py` (16.37 KB - newer version)
- **Lý do xóa**: Đã có `organize_project.py` mới hơn và tốt hơn
- **Action**:  **XÓA**

---

### 2. **OLD LOG FILES** 🗑️

#### Log files trong root (đã di chuyển vào `logs/`)
-  **KHÔNG CÒN** - Đã được clean khi reorganize

#### Large log files cần clean
- `logs/ict_bot_smc.log` - **8,868 KB** 😱
- `logs/ict_bot_20251016.log` - **632.81 KB**
- `logs/supertrend_bot.log` - **162.82 KB**
- **Lý do**: Quá cũ, chiếm dung lượng
- **Action**:  **NÊN XÓA** (hoặc compress với rotate_logs.py)

---

### 3. **OLD REPORTS** 

#### Backtest reports cũ (3-7 ngày trước)
```
reports/backtest_summary_20251016_*.json          (x3 files)
reports/ict_backtest_*_20251016_*.csv             (x2 files) 
reports/ict_equity_*_20251016_*.csv               (x2 files - LARGE: 3MB, 2.8MB)
reports/ict_smc_backtest_*_20251017_*.csv         (x10 files)
reports/ict_smc_equity_*_20251017_*.csv           (x10 files - LARGE: 3.3MB each)
```

- **Tổng kích thước**: ~20+ MB
- **Lý do**: Reports cũ, không cần thiết cho development
- **Action**:  **CÂN NHẮC XÓA** (backup nếu cần)

---

### 4. **DUPLICATE DOCS** 

#### `docs/VPS_DEPLOYMENT_GUIDE.md` - **CÓ THỂ DƯ THỪA**
- **Vị trí**: `C:\github\ML-SuperTrend-MT5\docs\VPS_DEPLOYMENT_GUIDE.md` (16.17 KB)
- **Duplicate of**: `docs/MT5_VPS_DEPLOYMENT.md` (19.91 KB - comprehensive hơn)
- **Lý do**: Có 2 files guide giống nhau về VPS
- **Action**:  **KIỂM TRA & MERGE** hoặc XÓA nếu duplicate

---

### 5. **STATISTIC IMAGES** 

#### PNG charts cũ
```
statistic/balance_chart_20251016_201336.png    (860.64 KB)
statistic/balance_chart_20251016_201418.png    (846.79 KB)
statistic/balance_chart_20251016_201630.png    (863.14 KB)
```

- **Tổng kích thước**: ~2.5 MB
- **Lý do**: Charts cũ từ 2 ngày trước
- **Action**:  **NÊN XÓA** (hoặc move to archive)

---

##  FILES CẦN GIỮ (KHÔNG DƯ THỪA)

### **Documentation** 
- All markdown files in `docs/` (trừ VPS_DEPLOYMENT_GUIDE.md nếu duplicate)
- README files in subdirectories
- Migration guides, technology stack docs

### **Core Code** 
- `core/*.py` - Bot logic
- `engines/*.py` - Backtest engines
- `utils/*.py` - Utilities
- `scripts/**/*.py` - All scripts (đã organize tốt)

### **Config & Setup** 
- `config/config.json` - Main config
- `config/config.example.json` - Example
- `setup.py`, `requirements.txt`, `MANIFEST.in`
- `.gitignore` (nếu có)

### **Tests** 
- `tests/*.py` - All test files
- Test documentation

### **Data** 
- `data/ta_lib-0.6.7-cp311-cp311-win_amd64.whl` - TA-Lib wheel (898 KB)

---

##  TỔNG HỢP

| Category | Files | Total Size | Action |
|----------|-------|------------|--------|
| **Duplicate configs** | 1 | 1.14 KB |  XÓA |
| **Duplicate scripts** | 1 | 9.01 KB |  XÓA |
| **Old logs** | 3 | 9.6 MB |  Clean |
| **Old reports** | 25+ | ~20 MB |  Clean |
| **Old charts** | 3 | 2.5 MB |  Xóa |
| **Duplicate docs** | 1? | 16.17 KB |  Kiểm tra |
| **TOTAL** | **30+** | **~32 MB** | 🧹 Cleanup |

---

##  KHUYẾN NGHỊ CLEANUP

### **Priority 1: XÓA NGAY** 

```bash
# 1. Duplicate config
Remove-Item config.json

# 2. Old reorganize script
Remove-Item reorganize_project.py

# 3. Old charts
Remove-Item -Recurse statistic/*.png
```

### **Priority 2: CLEAN LOGS** 🗑️

```bash
# Sử dụng rotate_logs.py
python scripts/automation/rotate_logs.py --max-age 7 --clean-reports

# Hoặc manual
Remove-Item logs/ict_bot_20251016.log
Remove-Item logs/ict_bot_smc.log
Remove-Item logs/supertrend_bot.log
```

### **Priority 3: CLEAN REPORTS** 

```bash
# Xóa reports cũ hơn 7 ngày
python scripts/automation/rotate_logs.py --clean-reports

# Hoặc manual
Remove-Item reports/*_20251016_*.csv
Remove-Item reports/*_20251016_*.json
Remove-Item reports/*_20251017_*.csv  # Nếu không cần
```

### **Priority 4: KIỂM TRA DOCS** 

```bash
# So sánh 2 files VPS deployment
code --diff docs/VPS_DEPLOYMENT_GUIDE.md docs/MT5_VPS_DEPLOYMENT.md

# Nếu duplicate  xóa file cũ hơn
```

---

## 📋 CLEANUP SCRIPT

```powershell
# cleanup_project.ps1

Write-Host "🧹 CLEANING UP PROJECT..." -ForegroundColor Yellow

# 1. Remove duplicate config
if (Test-Path "config.json") {
    Remove-Item "config.json" -Force
    Write-Host " Removed: config.json (duplicate)" -ForegroundColor Green
}

# 2. Remove old reorganize script
if (Test-Path "reorganize_project.py") {
    Remove-Item "reorganize_project.py" -Force
    Write-Host " Removed: reorganize_project.py (duplicate)" -ForegroundColor Green
}

# 3. Clean old charts
$charts = Get-ChildItem "statistic/*.png" -ErrorAction SilentlyContinue
if ($charts) {
    $charts | Remove-Item -Force
    Write-Host " Removed: $($charts.Count) old chart images" -ForegroundColor Green
}

# 4. Clean large old logs
$oldLogs = @(
    "logs/ict_bot_20251016.log",
    "logs/ict_bot_smc.log",
    "logs/supertrend_bot.log"
)
foreach ($log in $oldLogs) {
    if (Test-Path $log) {
        $size = (Get-Item $log).Length / 1MB
        Remove-Item $log -Force
        Write-Host " Removed: $log ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    }
}

# 5. Clean old reports (older than 7 days)
$cutoffDate = (Get-Date).AddDays(-7)
$oldReports = Get-ChildItem "reports/*" | Where-Object { $_.LastWriteTime -lt $cutoffDate }
if ($oldReports) {
    $totalSize = ($oldReports | Measure-Object -Property Length -Sum).Sum / 1MB
    $oldReports | Remove-Item -Force
    Write-Host " Removed: $($oldReports.Count) old reports ($([math]::Round($totalSize, 2)) MB)" -ForegroundColor Green
}

Write-Host ""
Write-Host " CLEANUP COMPLETED!" -ForegroundColor Green
Write-Host ""

# Show space saved
$spaceSaved = 32  # Approximate MB
Write-Host " Estimated space saved: ~$spaceSaved MB" -ForegroundColor Cyan
```

---

##  KIỂM TRA DUPLICATE DOCS

```bash
# So sánh 2 VPS guides
diff docs/VPS_DEPLOYMENT_GUIDE.md docs/MT5_VPS_DEPLOYMENT.md

# Nếu giống nhau  giữ file mới hơn (MT5_VPS_DEPLOYMENT.md)
```

---

##  SAU KHI CLEANUP

### **Space Saved**
- Duplicate files: ~10 KB
- Old logs: ~9.6 MB
- Old reports: ~20 MB
- Old charts: ~2.5 MB
- **TOTAL**: ~**32 MB**

### **Benefits**
 Root directory cleaner
 Faster Git operations
 Less confusion
 Better organization
 Reduced disk usage

---

##  NEXT STEPS

1.  Chạy cleanup script
2.  Test project vẫn hoạt động
3.  Commit changes
4.  Setup log rotation schedule
5.  Setup report cleanup schedule

---

**📅 Created: October 18, 2025**
**👤 Analyzed by: GitHub Copilot**
** Project: ML-SuperTrend-MT5**
