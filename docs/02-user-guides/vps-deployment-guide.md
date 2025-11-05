#  HƯỚNG DẪN DEPLOY BOT LÊN VPS/SERVER

## 📋 MỤC LỤC
1. [Tại Sao Cần VPS?](#tại-sao-cần-vps)
2. [Chọn VPS](#chọn-vps)
3. [Setup Windows VPS](#setup-windows-vps)
4. [Setup Linux VPS với Wine](#setup-linux-vps-với-wine)
5. [Auto-Restart Khi Crash](#auto-restart-khi-crash)
6. [Monitoring & Alerts](#monitoring--alerts)
7. [Best Practices](#best-practices)

---

## 🤔 TẠI SAO CẦN VPS?

###  **Máy Cá Nhân:**
- Phải bật 24/7
- Mất điện = bot dừng
- Chi phí điện cao
- Không ổn định

###  **VPS (Virtual Private Server):**
- Chạy 24/7 không gián đoạn
- Uptime 99.9%
- Internet tốc độ cao
- Chi phí thấp ($5-20/tháng)
- Backup tự động

---

##  CHỌN VPS

### **Option 1: Windows VPS** (Khuyến Nghị - Dễ Nhất)

#### **Providers Tốt:**

| Provider | Giá/tháng | RAM | CPU | Ưu Điểm |
|----------|-----------|-----|-----|---------|
| **Vultr** | $10-20 | 2-4GB | 1-2 vCPU | Dễ dùng, nhiều location |
| **Digital Ocean** | $12-24 | 2-4GB | 1-2 vCPU | Stable, docs tốt |
| **Contabo** | €8-15 | 8GB | 4 vCPU | Rẻ, powerful |
| **AWS EC2** | $10-30 | 2-4GB | 1-2 vCPU | Enterprise-grade |

#### **Cấu Hình Khuyến Nghị:**
```
OS: Windows Server 2019/2022
RAM: 4GB minimum (8GB recommended)
CPU: 2 vCPU
Storage: 40GB SSD
Bandwidth: 1TB+
Location: Singapore/US (gần broker server)
```

### **Option 2: Linux VPS + Wine** (Rẻ Hơn)

```
OS: Ubuntu 20.04/22.04
RAM: 2GB minimum
CPU: 1 vCPU
Storage: 20GB SSD
Giá: $5-10/tháng
```

---

## 🪟 SETUP WINDOWS VPS

### **Bước 1: Mua & Kết Nối VPS**

1. **Đăng ký VPS** (ví dụ: Vultr)
   ```
   - Chọn: Cloud Compute
   - Location: Singapore
   - OS: Windows Server 2022
   - Plan: 4GB RAM, 2 vCPU
   - Deploy: Click Deploy Now
   ```

2. **Lấy Thông Tin Đăng Nhập**
   ```
   IP Address: 123.45.67.89
   Username: Administrator
   Password: YourPassword123
   ```

3. **Kết Nối Remote Desktop**
   - Windows: Mở "Remote Desktop Connection"
   - Nhập IP address
   - Login với username/password

### **Bước 2: Setup MT5 trên VPS**

```powershell
# 1. Download MT5
Invoke-WebRequest -Uri "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe" -OutFile "mt5setup.exe"

# 2. Install MT5
.\mt5setup.exe

# 3. Login vào MT5 với account demo/live
```

### **Bước 3: Install Python & Dependencies**

```powershell
# 1. Download Python 3.11
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe" -OutFile "python-installer.exe"

# 2. Install Python
.\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1

# 3. Restart PowerShell, verify
python --version

# 4. Install dependencies
pip install MetaTrader5 pandas numpy scikit-learn ta-lib
```

### **Bước 4: Upload Project Code**

**Option A: Git Clone** (Khuyến Nghị)
```powershell
# Install Git
winget install Git.Git

# Clone project
cd C:\
git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
cd ML-SuperTrend-MT5

# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Option B: Manual Upload**
- Dùng WinSCP hoặc FileZilla
- Copy toàn bộ folder project
- Upload lên `C:\ML-SuperTrend-MT5`

### **Bước 5: Configure Bot**

```powershell
# Edit config
notepad config\config.json

# Update credentials cho VPS
{
    "accounts": {
        "demo": {
            "login": YOUR_DEMO_LOGIN,
            "password": "YOUR_PASSWORD",
            "server": "YOUR_BROKER_SERVER"
        }
    }
}
```

### **Bước 6: Test Run**

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Test SuperTrend Bot
python run_bot.py --account demo --symbol BTCUSDm --interval 60

# Test ICT Bot
python run_ict_bot.py --account demo --symbol BTCUSDm --interval 60

# Nếu chạy OK, Ctrl+C để dừng
```

---

## 🤖 AUTO-RESTART KHI CRASH

### **Windows Task Scheduler** (Tự động khởi động khi VPS restart)

#### **Tạo Batch Script:**

```batch
@echo off
:: run_bot.bat
title ML-SuperTrend Trading Bot

cd C:\ML-SuperTrend-MT5
call venv\Scripts\activate.bat

:loop
echo Starting bot at %date% %time%
python run_bot.py --account demo --symbol BTCUSDm --interval 60

echo Bot crashed or stopped at %date% %time%
echo Restarting in 10 seconds...
timeout /t 10

goto loop
```

#### **Setup Task Scheduler:**

1. **Open Task Scheduler**
   ```
   Win + R  taskschd.msc
   ```

2. **Create Basic Task**
   ```
   Name: ML-SuperTrend Bot
   Description: Auto-start trading bot
   Trigger: At startup
   Action: Start a program
   Program: C:\ML-SuperTrend-MT5\run_bot.bat
   ```

3. **Advanced Settings**
   ```
    Run whether user is logged on or not
    Run with highest privileges
    If task fails, restart every: 1 minute
    Attempt to restart up to: 999 times
   ```

### **PowerShell Auto-Restart Script** (Advanced)

```powershell
# auto_restart_bot.ps1

$botPath = "C:\ML-SuperTrend-MT5"
$pythonExe = "$botPath\venv\Scripts\python.exe"
$botScript = "$botPath\run_bot.py"
$logFile = "$botPath\logs\auto_restart.log"

function Write-Log {
    param($message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Out-File -Append -FilePath $logFile
    Write-Host $message
}

while ($true) {
    Write-Log "Starting bot..."
    
    $process = Start-Process -FilePath $pythonExe `
                              -ArgumentList $botScript, "--account", "demo", "--symbol", "BTCUSDm" `
                              -PassThru `
                              -NoNewWindow
    
    # Wait for process to exit
    $process.WaitForExit()
    
    Write-Log "Bot stopped with exit code: $($process.ExitCode)"
    
    if ($process.ExitCode -eq 0) {
        Write-Log "Clean exit. Not restarting."
        break
    }
    
    Write-Log "Restarting in 30 seconds..."
    Start-Sleep -Seconds 30
}
```

**Run Script:**
```powershell
powershell -ExecutionPolicy Bypass -File C:\ML-SuperTrend-MT5\auto_restart_bot.ps1
```

---

## 🐧 SETUP LINUX VPS VỚI WINE

### **Bước 1: Setup Ubuntu VPS**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Wine (để chạy MT5)
sudo dpkg --add-architecture i386
sudo wget -nc https://dl.winehq.org/wine-builds/winehq.key
sudo apt-key add winehq.key
sudo add-apt-repository 'deb https://dl.winehq.org/wine-builds/ubuntu/ focal main'
sudo apt update
sudo apt install --install-recommends winehq-stable -y

# Install Xvfb (virtual display)
sudo apt install xvfb -y
```

### **Bước 2: Install MT5 trên Wine**

```bash
# Download MT5
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

# Install MT5 với Xvfb
Xvfb :1 -screen 0 1024x768x16 &
export DISPLAY=:1
wine mt5setup.exe

# Configure MT5
wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 5/terminal64.exe
```

### **Bước 3: Install Python**

```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone project
git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
cd ML-SuperTrend-MT5

# Setup venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Bước 4: Systemd Service (Auto-Restart)**

```bash
# Create service file
sudo nano /etc/systemd/system/supertrend-bot.service
```

```ini
[Unit]
Description=ML-SuperTrend Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ML-SuperTrend-MT5
ExecStart=/root/ML-SuperTrend-MT5/venv/bin/python run_bot.py --account demo --symbol BTCUSDm
Restart=always
RestartSec=30
StandardOutput=append:/root/ML-SuperTrend-MT5/logs/bot.log
StandardError=append:/root/ML-SuperTrend-MT5/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Enable & start service
sudo systemctl daemon-reload
sudo systemctl enable supertrend-bot
sudo systemctl start supertrend-bot

# Check status
sudo systemctl status supertrend-bot

# View logs
sudo journalctl -u supertrend-bot -f
```

---

##  MONITORING & ALERTS

### **Option 1: Telegram Bot Alerts**

Tạo file `utils/telegram_alert.py`:

```python
import requests
import json
from datetime import datetime

class TelegramAlert:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Send message to Telegram"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"Telegram alert failed: {e}")
    
    def send_trade_alert(self, trade_info):
        """Send trade notification"""
        message = f"""
🤖 <b>ML-SuperTrend Bot Alert</b>

 Symbol: {trade_info['symbol']}
{' BUY' if trade_info['type'] == 'BUY' else ' SELL'}

 Entry: ${trade_info['entry']:.2f}
🛡️ Stop Loss: ${trade_info['sl']:.2f}
 Take Profit: ${trade_info['tp']:.2f}
 Lot Size: {trade_info['lot_size']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.send_message(message)
    
    def send_error_alert(self, error_msg):
        """Send error notification"""
        message = f"""
 <b>BOT ERROR</b>

{error_msg}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.send_message(message)
    
    def send_daily_report(self, stats):
        """Send daily performance report"""
        message = f"""
 <b>Daily Performance Report</b>

 P&L: ${stats['pnl']:.2f}
 Win Rate: {stats['win_rate']:.1f}%
 Trades: {stats['total_trades']}
 Wins: {stats['wins']}
 Losses: {stats['losses']}

⏰ {datetime.now().strftime('%Y-%m-%d')}
        """
        self.send_message(message)
```

**Setup Telegram Bot:**
```
1. Chat với @BotFather trên Telegram
2. Tạo bot: /newbot
3. Lấy bot token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
4. Chat với bot của bạn
5. Get chat ID: https://api.telegram.org/bot<TOKEN>/getUpdates
```

**Sử dụng trong bot:**
```python
from utils.telegram_alert import TelegramAlert

# Initialize
alert = TelegramAlert(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

# Send trade alert
alert.send_trade_alert({
    'symbol': 'BTCUSDm',
    'type': 'BUY',
    'entry': 67000,
    'sl': 66000,
    'tp': 69000,
    'lot_size': 0.05
})

# Send error alert
alert.send_error_alert("MT5 connection lost!")

# Send daily report
alert.send_daily_report({
    'pnl': 450.50,
    'win_rate': 65.5,
    'total_trades': 10,
    'wins': 6,
    'losses': 4
})
```

### **Option 2: Discord Webhook**

```python
import requests
from datetime import datetime

def send_discord_alert(webhook_url, message):
    """Send alert to Discord"""
    data = {
        "content": message,
        "username": "ML-SuperTrend Bot"
    }
    requests.post(webhook_url, json=data)

# Usage
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
send_discord_alert(DISCORD_WEBHOOK, "🤖 Bot started successfully!")
```

### **Option 3: Email Alerts**

```python
import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body):
    """Send email alert"""
    sender = "your_email@gmail.com"
    receiver = "your_email@gmail.com"
    password = "your_app_password"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# Usage
send_email_alert(
    "Trade Alert", 
    "BUY BTCUSDm at $67,000"
)
```

---

## 🔐 BEST PRACTICES

### **1. Security**

```bash
# Firewall - chỉ mở port cần thiết
# Windows
New-NetFirewallRule -DisplayName "RDP" -Direction Inbound -LocalPort 3389 -Protocol TCP -Action Allow

# Linux
sudo ufw allow ssh
sudo ufw allow from YOUR_IP to any port 22
sudo ufw enable
```

### **2. Backup Tự Động**

```powershell
# Windows - Backup script
$source = "C:\ML-SuperTrend-MT5"
$destination = "D:\Backups\ML-SuperTrend-$(Get-Date -Format 'yyyyMMdd').zip"
Compress-Archive -Path $source -DestinationPath $destination

# Schedule: Daily at 2 AM
```

```bash
# Linux - Cron backup
0 2 * * * tar -czf /backup/ml-supertrend-$(date +\%Y\%m\%d).tar.gz /root/ML-SuperTrend-MT5
```

### **3. Update Code Tự Động**

```bash
# Auto-update script
cd /root/ML-SuperTrend-MT5
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart supertrend-bot
```

### **4. Log Rotation**

```bash
# Linux - logrotate config
sudo nano /etc/logrotate.d/supertrend-bot

/root/ML-SuperTrend-MT5/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

### **5. Health Check Script**

```python
# health_check.py
import psutil
import requests
from datetime import datetime

def check_bot_health():
    """Check if bot is running and healthy"""
    
    # Check if Python process running
    bot_running = False
    for proc in psutil.process_iter(['name', 'cmdline']):
        if 'python' in proc.info['name'].lower():
            cmdline = ' '.join(proc.info['cmdline'])
            if 'run_bot.py' in cmdline:
                bot_running = True
                break
    
    # Check CPU & RAM
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    
    # Send alert if issues
    if not bot_running:
        send_alert(" Bot is NOT running!")
    elif cpu_percent > 90:
        send_alert(f" High CPU usage: {cpu_percent}%")
    elif ram_percent > 90:
        send_alert(f" High RAM usage: {ram_percent}%")
    else:
        print(f" Bot healthy - CPU: {cpu_percent}%, RAM: {ram_percent}%")

if __name__ == "__main__":
    check_bot_health()
```

**Schedule health check every 5 minutes:**
```bash
# Linux cron
*/5 * * * * /root/ML-SuperTrend-MT5/venv/bin/python /root/ML-SuperTrend-MT5/health_check.py
```

---

##  CHI PHÍ DỰ KIẾN

| Item | Giá/Tháng | Ghi Chú |
|------|-----------|---------|
| **Windows VPS** | $10-20 | Vultr, DigitalOcean |
| **Linux VPS** | $5-10 | Rẻ hơn nhưng setup phức tạp |
| **Backup Storage** | $2-5 | Optional |
| **Monitoring Service** | Free-$5 | UptimeRobot, Pingdom |
| **Domain (optional)** | $10/năm | Cho dashboard |
| **TỔNG** | **$10-25/tháng** | |

**So với chi phí điện máy cá nhân chạy 24/7: ~$30-50/tháng**  VPS rẻ hơn!

---

## 📋 CHECKLIST TRIỂN KHAI

### **Pre-Deploy:**
- [ ] Test bot trên máy local
- [ ] Backup code & config
- [ ] Chuẩn bị credentials (MT5 login, API keys)
- [ ] Chọn VPS provider
- [ ] Đăng ký & payment

### **Deployment:**
- [ ] Setup VPS
- [ ] Install MT5
- [ ] Install Python & dependencies
- [ ] Upload code
- [ ] Configure bot
- [ ] Test run
- [ ] Setup auto-restart
- [ ] Configure monitoring

### **Post-Deploy:**
- [ ] Test alerts (Telegram/Discord)
- [ ] Monitor first 24h
- [ ] Schedule backups
- [ ] Document VPS credentials
- [ ] Setup log rotation

---

##  KẾT LUẬN

**Khuyến Nghị:**
1. **Newbie**: Dùng **Windows VPS** - dễ nhất
2. **Advanced**: Dùng **Linux VPS + Systemd** - rẻ & stable
3. **Essential**: Setup **Telegram alerts** - biết bot đang làm gì
4. **Critical**: **Auto-restart** - bot không bao giờ chết

**Next Steps:**
1. Mua VPS (Vultr $10/tháng)
2. Follow hướng dẫn setup Windows VPS
3. Test bot chạy 24h
4. Setup Telegram alerts
5. Enjoy passive trading! 

---

**Tác giả:** AI Assistant  
**Cập nhật:** 18/10/2025  
**Version:** 1.0
