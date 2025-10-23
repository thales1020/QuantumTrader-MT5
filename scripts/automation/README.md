# 🤖 Automation Scripts

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
