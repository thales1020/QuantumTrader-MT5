"""
Script tự động tổ chức lại cấu trúc project
Dọn dẹp root directory, di chuyển files vào thư mục phù hợp
"""

import os
import shutil
from datetime import datetime

class ProjectOrganizer:
    def __init__(self):
        self.root = os.getcwd()
        self.moves = []
        self.deletes = []
        self.created_dirs = []
        
    def create_directory(self, path):
        """Tạo thư mục nếu chưa tồn tại"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            self.created_dirs.append(path)
            print(f"✅ Tạo thư mục: {path}")
    
    def move_file(self, source, destination):
        """Di chuyển file"""
        if os.path.exists(source):
            # Tạo thư mục đích nếu chưa có
            dest_dir = os.path.dirname(destination)
            self.create_directory(dest_dir)
            
            # Di chuyển file
            shutil.move(source, destination)
            self.moves.append((source, destination))
            print(f"📦 Di chuyển: {source} → {destination}")
        else:
            print(f"⚠️ File không tồn tại: {source}")
    
    def delete_file(self, filepath):
        """Xóa file"""
        if os.path.exists(filepath):
            os.remove(filepath)
            self.deletes.append(filepath)
            print(f"🗑️ Xóa: {filepath}")
        else:
            print(f"⚠️ File không tồn tại: {filepath}")
    
    def organize(self):
        """Tổ chức lại toàn bộ project"""
        print("="*60)
        print("🧹 BẮT ĐẦU TỔ CHỨC LẠI PROJECT")
        print("="*60)
        print()
        
        # 1. Tạo các thư mục mới
        print("📁 BƯỚC 1: Tạo cấu trúc thư mục mới")
        print("-"*60)
        self.create_directory("scripts/runners")
        self.create_directory("scripts/automation")
        self.create_directory("scripts/windows")
        self.create_directory("scripts/backtest")
        self.create_directory("scripts/analysis")
        self.create_directory("scripts/utils")
        print()
        
        # 2. Di chuyển runner scripts
        print("📦 BƯỚC 2: Di chuyển runner scripts")
        print("-"*60)
        runners = [
            "run_bot.py",
            "run_ict_bot.py",
            "run_ict_bot_smc.py",
            "run_backtest.py",
            "run_simple_backtest.py",
            "run_tests.py"
        ]
        for runner in runners:
            self.move_file(runner, f"scripts/runners/{runner}")
        print()
        
        # 3. Di chuyển automation scripts
        print("🤖 BƯỚC 3: Di chuyển automation scripts")
        print("-"*60)
        automation = [
            "watchdog.py",
            "health_check.py",
            "rotate_logs.py"
        ]
        for script in automation:
            self.move_file(script, f"scripts/automation/{script}")
        print()
        
        # 4. Di chuyển batch files
        print("🖥️ BƯỚC 4: Di chuyển batch files")
        print("-"*60)
        batch_files = [
            "start_bot.bat",
            "auto_restart_bot.bat"
        ]
        for bat in batch_files:
            self.move_file(bat, f"scripts/windows/{bat}")
        print()
        
        # 5. Di chuyển documentation
        print("📝 BƯỚC 5: Di chuyển documentation")
        print("-"*60)
        docs = [
            "PROJECT_EVALUATION.md",
            "TECHNOLOGY_STACK.md"
        ]
        for doc in docs:
            self.move_file(doc, f"docs/{doc}")
        print()
        
        # 6. Di chuyển utility scripts
        print("🔧 BƯỚC 6: Di chuyển utility scripts")
        print("-"*60)
        # Giữ reorganize_project.py ở root để có thể chạy lại
        # self.move_file("reorganize_project.py", "scripts/utils/reorganize_project.py")
        print("ℹ️ Giữ organize_project.py ở root")
        print()
        
        # 6.1. Di chuyển backtest scripts
        print("📊 BƯỚC 6.1: Di chuyển backtest scripts")
        print("-"*60)
        backtest_scripts = [
            "scripts/backtest_all_symbols.py",
            "scripts/backtest_all_symbols_smc.py",
            "scripts/backtest_all_symbols_supertrend.py",
            "scripts/backtest_ict_smc.py"
        ]
        for script in backtest_scripts:
            filename = os.path.basename(script)
            self.move_file(script, f"scripts/backtest/{filename}")
        print()
        
        # 6.2. Di chuyển analysis scripts
        print("📈 BƯỚC 6.2: Di chuyển analysis scripts")
        print("-"*60)
        analysis_scripts = [
            "scripts/analyze_ict_log.py",
            "scripts/benchmark_performance.py",
            "scripts/plot_balance_chart.py",
            "scripts/plot_balance_from_log.py"
        ]
        for script in analysis_scripts:
            filename = os.path.basename(script)
            self.move_file(script, f"scripts/analysis/{filename}")
        print()
        
        # 6.3. Di chuyển utility scripts trong scripts/
        print("🔧 BƯỚC 6.3: Di chuyển utility scripts")
        print("-"*60)
        util_scripts = [
            "scripts/check_data_range.py",
            "scripts/check_symbols.py",
            "scripts/clear_report.py",
            "scripts/test_historical_data.py",
            "scripts/test_smc_library.py",
            "scripts/test_timeframes.py"
        ]
        for script in util_scripts:
            filename = os.path.basename(script)
            self.move_file(script, f"scripts/utils/{filename}")
        print()
        
        # 7. Xóa log files cũ
        print("🗑️ BƯỚC 7: Xóa log files cũ")
        print("-"*60)
        old_logs = [
            "ict_bot.log",
            "ict_bot_smc.log",
            "supertrend_bot.log"
        ]
        for log in old_logs:
            self.delete_file(log)
        print()
        
        # 8. Tạo file README cho từng thư mục
        print("📄 BƯỚC 8: Tạo README cho từng thư mục")
        print("-"*60)
        self.create_readme_files()
        print()
        
        # 9. Tạo file __init__.py
        print("🐍 BƯỚC 9: Tạo __init__.py files")
        print("-"*60)
        self.create_init_files()
        print()
        
        # 10. Tổng kết
        print("="*60)
        print("✅ HOÀN THÀNH TỔ CHỨC LẠI PROJECT")
        print("="*60)
        print(f"📁 Thư mục đã tạo: {len(self.created_dirs)}")
        print(f"📦 Files đã di chuyển: {len(self.moves)}")
        print(f"🗑️ Files đã xóa: {len(self.deletes)}")
        print()
        
        # In summary
        self.print_summary()
    
    def create_readme_files(self):
        """Tạo README cho các thư mục"""
        readmes = {
            "scripts/runners/README.md": """# 🚀 Runner Scripts

Scripts để chạy các bot và backtest.

## Files

- **run_bot.py** - Chạy SuperTrend Bot
- **run_ict_bot.py** - Chạy ICT Bot
- **run_ict_bot_smc.py** - Chạy ICT Bot SMC
- **run_backtest.py** - Chạy backtest
- **run_simple_backtest.py** - Chạy backtest đơn giản
- **run_tests.py** - Chạy unit tests

## Usage

```bash
# Chạy bot
python scripts/runners/run_bot.py --account demo --symbol EURUSD

# Chạy backtest
python scripts/runners/run_backtest.py --symbol BTCUSD --start 2024-01-01
```
""",
            "scripts/automation/README.md": """# 🤖 Automation Scripts

Scripts tự động hóa monitoring và maintenance.

## Files

- **watchdog.py** - Monitor và auto-restart bot
- **health_check.py** - Kiểm tra health của bot và MT5
- **rotate_logs.py** - Quản lý và nén log files

## Usage

```bash
# Watchdog
python scripts/automation/watchdog.py

# Health check
python scripts/automation/health_check.py --alerts

# Log rotation
python scripts/automation/rotate_logs.py --clean-reports
```

## Task Scheduler

Đặt lịch chạy:
- health_check.py - Mỗi giờ
- rotate_logs.py - Mỗi ngày 3 AM
""",
            "scripts/windows/README.md": """# 🖥️ Windows Scripts

Batch scripts cho Windows automation.

## Files

- **start_bot.bat** - Auto-restart bot script
- **auto_restart_bot.bat** - Alternative restart script

## Usage

```batch
REM Chạy bot với auto-restart
start_bot.bat

REM Hoặc double-click file trong Explorer
```

## Task Scheduler Setup

1. Mở Task Scheduler
2. Create Task
3. Trigger: At startup
4. Action: Start a program → `start_bot.bat`
5. Settings: Run whether user logged on or not
""",
            "scripts/backtest/README.md": """# 📊 Backtest Scripts

Scripts để chạy backtest cho các chiến lược khác nhau.

## Files

- **backtest_all_symbols.py** - Backtest tất cả symbols
- **backtest_all_symbols_smc.py** - Backtest SMC strategy
- **backtest_all_symbols_supertrend.py** - Backtest SuperTrend strategy
- **backtest_ict_smc.py** - Backtest ICT SMC strategy

## Usage

```bash
# Backtest all symbols
python scripts/backtest/backtest_all_symbols.py

# Backtest specific strategy
python scripts/backtest/backtest_ict_smc.py --symbol BTCUSD --start 2024-01-01
```

## Output

Results saved to `reports/` folder:
- CSV files với trade history
- JSON files với summary statistics
- Equity curves
""",
            "scripts/analysis/README.md": """# 📈 Analysis Scripts

Scripts để phân tích performance và visualize kết quả.

## Files

- **analyze_ict_log.py** - Phân tích ICT bot logs
- **benchmark_performance.py** - So sánh performance
- **plot_balance_chart.py** - Vẽ biểu đồ balance
- **plot_balance_from_log.py** - Vẽ biểu đồ từ log files

## Usage

```bash
# Analyze logs
python scripts/analysis/analyze_ict_log.py

# Plot balance
python scripts/analysis/plot_balance_chart.py

# Benchmark
python scripts/analysis/benchmark_performance.py
```

## Output

- PNG/HTML charts
- Performance statistics
- Comparative analysis
""",
            "scripts/utils/README.md": """# 🔧 Utility Scripts

Scripts tiện ích cho testing và maintenance.

## Files

- **check_data_range.py** - Kiểm tra data availability
- **check_symbols.py** - Kiểm tra symbols trên MT5
- **clear_report.py** - Xóa old reports
- **test_historical_data.py** - Test historical data
- **test_smc_library.py** - Test SMC library
- **test_timeframes.py** - Test timeframes

## Usage

```bash
# Check symbols
python scripts/utils/check_symbols.py

# Check data range
python scripts/utils/check_data_range.py --symbol BTCUSD

# Clear reports
python scripts/utils/clear_report.py
```
"""
        }
        
        for path, content in readmes.items():
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Tạo: {path}")
    
    def create_init_files(self):
        """Tạo __init__.py cho Python packages"""
        init_files = [
            "scripts/__init__.py",
            "scripts/runners/__init__.py",
            "scripts/automation/__init__.py",
            "scripts/backtest/__init__.py",
            "scripts/analysis/__init__.py",
            "scripts/utils/__init__.py"
        ]
        
        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Python package marker"""\n')
                print(f"✅ Tạo: {init_file}")
    
    def print_summary(self):
        """In tổng kết chi tiết"""
        print("📊 CHI TIẾT THAY ĐỔI")
        print("="*60)
        
        if self.moves:
            print("\n📦 Files đã di chuyển:")
            for source, dest in self.moves:
                print(f"  • {source} → {dest}")
        
        if self.deletes:
            print("\n🗑️ Files đã xóa:")
            for file in self.deletes:
                print(f"  • {file}")
        
        if self.created_dirs:
            print("\n📁 Thư mục đã tạo:")
            for dir in self.created_dirs:
                print(f"  • {dir}")
        
        print("\n" + "="*60)
        print("📂 CẤU TRÚC MỚI:")
        print("="*60)
        print("""
Root/
├── README.md                 ✅ Giữ nguyên
├── LICENSE                   ✅ Giữ nguyên
├── requirements.txt          ✅ Giữ nguyên
├── setup.py                  ✅ Giữ nguyên
├── config.json               ✅ Giữ nguyên
│
├── scripts/
│   ├── runners/              📦 Runner scripts
│   │   ├── run_bot.py
│   │   ├── run_ict_bot.py
│   │   ├── run_ict_bot_smc.py
│   │   ├── run_backtest.py
│   │   ├── run_simple_backtest.py
│   │   └── run_tests.py
│   │
│   ├── automation/           🤖 Automation scripts
│   │   ├── watchdog.py
│   │   ├── health_check.py
│   │   └── rotate_logs.py
│   │
│   ├── windows/              🖥️ Windows batch scripts
│   │   ├── start_bot.bat
│   │   └── auto_restart_bot.bat
│   │
│   ├── backtest/             📊 Backtest scripts
│   │   ├── backtest_all_symbols.py
│   │   ├── backtest_all_symbols_smc.py
│   │   ├── backtest_all_symbols_supertrend.py
│   │   └── backtest_ict_smc.py
│   │
│   ├── analysis/             📈 Analysis & visualization
│   │   ├── analyze_ict_log.py
│   │   ├── benchmark_performance.py
│   │   ├── plot_balance_chart.py
│   │   └── plot_balance_from_log.py
│   │
│   └── utils/                🔧 Utility scripts
│       ├── check_data_range.py
│       ├── check_symbols.py
│       ├── clear_report.py
│       ├── test_historical_data.py
│       ├── test_smc_library.py
│       └── test_timeframes.py
│
├── docs/                     📝 Documentation
│   ├── PROJECT_EVALUATION.md
│   └── TECHNOLOGY_STACK.md
│
├── core/                     ✅ Không đổi
├── engines/                  ✅ Không đổi
├── tests/                    ✅ Không đổi
├── utils/                    ✅ Không đổi
└── logs/                     ✅ Không đổi
        """)
        
        print("="*60)
        print("📝 LƯU Ý QUAN TRỌNG")
        print("="*60)
        print("""
⚠️ Sau khi tổ chức lại, bạn cần:

1. Cập nhật các import paths trong code nếu cần
2. Cập nhật scripts/batch files với paths mới
3. Cập nhật Task Scheduler với paths mới
4. Cập nhật documentation với paths mới

✅ Paths mới để chạy:

   # Chạy bot
   python scripts/runners/run_bot.py

   # Watchdog
   python scripts/automation/watchdog.py

   # Health check
   python scripts/automation/health_check.py

   # Log rotation
   python scripts/automation/rotate_logs.py

🔄 Nếu muốn hoàn tác:
   Giữ nguyên file reorganize_project.py này, có thể tạo script
   restore để hoàn tác các thay đổi.
        """)
        print("="*60)


def main():
    """Entry point"""
    print("\n" + "="*60)
    print("🧹 TỔ CHỨC LẠI PROJECT STRUCTURE")
    print("="*60)
    print("\nScript này sẽ di chuyển files để root directory gọn gàng hơn.")
    print("\n⚠️ CẢNH BÁO: Script này sẽ di chuyển và xóa files!")
    print("Đảm bảo bạn đã commit code hoặc backup trước khi chạy.")
    print()
    
    # Confirm
    confirm = input("Bạn có chắc muốn tiếp tục? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Đã hủy bỏ.")
        return
    
    print()
    
    # Run organization
    organizer = ProjectOrganizer()
    organizer.organize()
    
    print("\n✅ Hoàn tất! Project đã được tổ chức lại.")
    print("📝 Kiểm tra lại cấu trúc mới và cập nhật paths nếu cần.\n")


if __name__ == "__main__":
    main()
