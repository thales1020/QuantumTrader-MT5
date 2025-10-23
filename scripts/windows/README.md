# 🖥️ Windows Scripts

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
