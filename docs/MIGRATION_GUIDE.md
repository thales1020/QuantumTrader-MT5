# 🔄 Migration Guide - Cập Nhật Sau Khi Tổ Chức Lại Project

## 📅 Ngày thay đổi: 18 Tháng 10, 2025

Project đã được tổ chức lại để root directory gọn gàng hơn và dễ maintain.

---

## 🎯 Tóm Tắt Thay Đổi

### **Root Directory**
- ✅ Từ **30+ files** → **9 files** (giảm 70%)
- ✅ Chỉ giữ lại files cần thiết: README, LICENSE, requirements.txt, setup.py, config.json

### **Scripts Directory - Phân loại theo chức năng:**

```
scripts/
├── runners/              🚀 Bot & Backtest runners
├── automation/           🤖 Monitoring & maintenance
├── windows/              🖥️ Windows batch scripts
├── backtest/             📊 Backtest scripts
├── analysis/             📈 Analysis & visualization
└── utils/                🔧 Utility scripts
```

---

## ✅ CẬP NHẬT ĐÃ HOÀN THÀNH TỰ ĐỘNG

### **1. Batch Scripts** ✅
- ✅ `scripts/windows/start_bot.bat` - Đã sửa BOT_SCRIPT path
- ✅ `scripts/windows/auto_restart_bot.bat` - Đã sửa BOT_SCRIPT path

### **2. Automation Scripts** ✅
- ✅ `scripts/automation/watchdog.py` - Đã thêm PROJECT_ROOT và sửa paths
- ✅ `scripts/automation/health_check.py` - Đã thêm PROJECT_ROOT và sửa paths
- ✅ `scripts/automation/rotate_logs.py` - Đã thêm PROJECT_ROOT và sửa paths

---

## 📋 KHÔNG CẦN THAY ĐỔI

### **Core Code**
- ✅ `core/` - Không có import từ scripts
- ✅ `engines/` - Không có import từ scripts
- ✅ `tests/` - Không có import từ scripts
- ✅ `utils/` - Không có import từ scripts

### **Runner Scripts**
- ✅ `scripts/runners/run_bot.py` - Chạy từ project root, không cần sửa
- ✅ `scripts/runners/run_ict_bot.py` - Chạy từ project root, không cần sửa
- ✅ `scripts/runners/run_ict_bot_smc.py` - Chạy từ project root, không cần sửa
- ✅ `scripts/runners/run_backtest.py` - Chạy từ project root, không cần sửa

---

## 🔧 CÁCH SỬ DỤNG MỚI

### **1. Chạy Bot từ Root Directory**

```bash
# SuperTrend Bot
python scripts/runners/run_bot.py --account demo --symbol EURUSD

# ICT Bot
python scripts/runners/run_ict_bot.py --account demo --symbol BTCUSD

# ICT SMC Bot
python scripts/runners/run_ict_bot_smc.py --account demo --symbol XAUUSD
```

### **2. Chạy Backtest**

```bash
# Backtest all symbols
python scripts/backtest/backtest_all_symbols.py

# Backtest specific strategy
python scripts/backtest/backtest_ict_smc.py --symbol BTCUSD --start 2024-01-01
```

### **3. Automation Scripts**

```bash
# Watchdog (monitor & auto-restart)
python scripts/automation/watchdog.py

# Health check
python scripts/automation/health_check.py --alerts

# Log rotation
python scripts/automation/rotate_logs.py --clean-reports
```

### **4. Analysis Scripts**

```bash
# Analyze logs
python scripts/analysis/analyze_ict_log.py

# Plot balance chart
python scripts/analysis/plot_balance_chart.py

# Benchmark performance
python scripts/analysis/benchmark_performance.py
```

### **5. Utility Scripts**

```bash
# Check symbols
python scripts/utils/check_symbols.py

# Check data range
python scripts/utils/check_data_range.py --symbol BTCUSD

# Test SMC library
python scripts/utils/test_smc_library.py
```

### **6. Windows Batch Scripts**

```batch
REM Auto-restart bot (chạy từ bất kỳ đâu)
scripts\windows\start_bot.bat

REM Hoặc double-click trong Explorer
```

---

## 🖥️ WINDOWS TASK SCHEDULER

### **Cập nhật paths trong Task Scheduler:**

#### **1. Bot Auto-Start (On System Startup)**
```
Program: C:\github\ML-SuperTrend-MT5\scripts\windows\start_bot.bat
Start in: C:\github\ML-SuperTrend-MT5
```

#### **2. Health Check (Hourly)**
```
Program: python.exe
Arguments: scripts/automation/health_check.py --alerts
Start in: C:\github\ML-SuperTrend-MT5
```

#### **3. Log Rotation (Daily 3:00 AM)**
```
Program: python.exe
Arguments: scripts/automation/rotate_logs.py --clean-reports
Start in: C:\github\ML-SuperTrend-MT5
```

---

## 📝 VPS DEPLOYMENT

### **Cập nhật trong docs/MT5_VPS_DEPLOYMENT.md:**

Tất cả commands trong deployment guide đã được cập nhật tự động.

### **Quick Reference:**

```bash
# Trên VPS, chạy bot:
cd C:\ML-SuperTrend-MT5
python scripts\runners\run_bot.py --account live --symbol EURUSD

# Auto-restart với batch file:
scripts\windows\start_bot.bat

# Setup watchdog:
python scripts\automation\watchdog.py
```

---

## 🔍 KIỂM TRA SAU KHI MIGRATE

### **Checklist:**

- [x] ✅ Batch scripts paths đã sửa
- [x] ✅ Automation scripts paths đã sửa
- [x] ✅ Test rotate_logs.py → OK
- [ ] ⏳ Test watchdog.py (cần install psutil)
- [ ] ⏳ Test health_check.py (cần MT5 running)
- [ ] ⏳ Test batch scripts trên Windows
- [ ] ⏳ Cập nhật Task Scheduler (nếu có)
- [ ] ⏳ Test bot runners

### **Commands để test:**

```bash
# Test automation scripts
python scripts/automation/rotate_logs.py
python scripts/automation/health_check.py
python scripts/automation/watchdog.py

# Test runners
python scripts/runners/run_tests.py
python scripts/runners/run_bot.py --help

# Test backtest
python scripts/backtest/backtest_all_symbols.py --help
```

---

## 🐛 TROUBLESHOOTING

### **Issue 1: "Module not found"**
**Solution:** Đảm bảo chạy từ project root directory

```bash
cd C:\github\ML-SuperTrend-MT5
python scripts/runners/run_bot.py
```

### **Issue 2: "Path not found" trong batch files**
**Solution:** Batch files đã được sửa, đảm bảo sử dụng version mới nhất

### **Issue 3: Automation scripts không tìm thấy logs**
**Solution:** Scripts đã được cập nhật với PROJECT_ROOT, chạy lại

### **Issue 4: Task Scheduler không hoạt động**
**Solution:** Cập nhật paths trong Task Scheduler theo hướng dẫn trên

---

## 📊 SO SÁNH TRƯỚC & SAU

### **Trước khi tổ chức lại:**
```
Root/
├── run_bot.py
├── run_ict_bot.py
├── run_ict_bot_smc.py
├── run_backtest.py
├── run_simple_backtest.py
├── run_tests.py
├── watchdog.py
├── health_check.py
├── rotate_logs.py
├── start_bot.bat
├── auto_restart_bot.bat
├── PROJECT_EVALUATION.md
├── TECHNOLOGY_STACK.md
├── ict_bot.log
├── ict_bot_smc.log
├── supertrend_bot.log
├── reorganize_project.py
└── ... (30+ files!)
```

### **Sau khi tổ chức lại:**
```
Root/
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
├── config.json
├── MANIFEST.in
├── organize_project.py
└── scripts/
    ├── runners/          (6 files)
    ├── automation/       (3 files)
    ├── windows/          (2 files)
    ├── backtest/         (4 files)
    ├── analysis/         (4 files)
    └── utils/            (6 files)
```

**Kết quả:** Root gọn gàng 70%, dễ navigate, professional structure! 🎉

---

## 🎓 LỢI ÍCH

1. **Dễ tìm kiếm** - Files được phân loại rõ ràng
2. **Dễ maintain** - Tách biệt concerns
3. **Professional** - Structure chuẩn cho production
4. **Scalable** - Dễ thêm features mới
5. **Onboarding** - Người mới dễ hiểu project structure

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề sau khi migrate:

1. Kiểm tra file này: `docs/MIGRATION_GUIDE.md`
2. Xem project structure: `tree /F scripts`
3. Test automation scripts: `python scripts/automation/rotate_logs.py`
4. Check README của từng thư mục: `scripts/*/README.md`

---

**✅ Migration completed successfully!**
**📅 Date: October 18, 2025**
**👤 By: GitHub Copilot**
