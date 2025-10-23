# 🚀 Deploy Bot lên MT5 VPS

## Tổng Quan

MT5 cung cấp **Virtual Private Server (VPS)** tích hợp ngay trong platform, cho phép bot chạy 24/7 kể cả khi tắt máy tính cá nhân.

---

## 📋 Ưu & Nhược Điểm MT5 VPS

### ✅ **Ưu Điểm:**
- 🚀 **Setup dễ dàng** - 1-click deployment từ MT5 terminal
- 🌍 **Latency cực thấp** - 96% brokers <10ms, 84% <3ms
- 💰 **Giá rẻ** - $10-15/tháng (có 24h FREE trial)
- 🔒 **Bảo mật cao** - Môi trường cách ly
- ⚡ **Uptime 99.99%** - Ổn định tuyệt đối
- 🔧 **Không cần quản lý** - MQL5 lo toàn bộ
- 🌐 **30+ locations** - Worldwide coverage

### ⚠️ **Nhược Điểm:**
- 🖥️ **Chỉ Windows** - RDP desktop environment
- 📦 **Tài nguyên giới hạn** - RAM up to 3GB, CPU chia sẻ
- 🔧 **Ít tùy chỉnh** - Không có root access
- 💾 **Storage nhỏ** - Up to 16GB
- ⚠️ **Phụ thuộc broker** - Tied to broker account

---

## 🎯 Phương Án Deploy

### **Option 1: MT5 VPS (Khuyến Nghị Cho Beginners)** ⭐⭐⭐⭐⭐

**Phù hợp khi:**
- ✅ Bạn mới bắt đầu
- ✅ Không muốn quản lý server
- ✅ Broker hỗ trợ VPS (Exness, XM, IC Markets)
- ✅ Chỉ chạy 1-2 bots

**Giá:**
- Mini (1 tháng): **$15/month**
- Optimal (3 tháng): **$13/month**
- Long (6 tháng): **$10.83/month**
- Max (12 tháng): **$10/month** ⭐ Best value
- **24-hour FREE trial** - Test trước khi mua!

**Specs:**
- RAM: Up to **3 GB**
- Disk: Up to **16 GB**
- CPU: Multiple CPUs allocated on demand
- Latency: 96% <10ms, 84% <3ms
- Uptime: **99.99%**

**Setup Time:** 5-10 phút

---

### **Option 2: Cloud VPS (AWS, Google Cloud, Azure)** ⭐⭐⭐⭐

**Phù hợp khi:**
- ✅ Chạy nhiều bots/strategies
- ✅ Cần tùy chỉnh cao
- ✅ Muốn control hoàn toàn
- ✅ Có kiến thức Linux/DevOps

**Giá:** $5-50/tháng tùy cấu hình

**Setup Time:** 1-2 giờ

---

### **Option 3: VPS Providers (Vultr, DigitalOcean, Contabo)** ⭐⭐⭐⭐

**Phù hợp khi:**
- ✅ Muốn giá rẻ nhất
- ✅ Chấp nhận quản lý server
- ✅ Chạy multi-strategy portfolio

**Giá:** $3-20/tháng

**Setup Time:** 30-60 phút

---

## 🔧 HƯỚNG DẪN: Deploy lên MT5 VPS

### **Bước 1: Activate 24-Hour FREE Trial**

MT5 VPS cung cấp **24 giờ miễn phí** để test:
- 🆓 Không cần thẻ tín dụng
- ✅ Full features như bản trả phí
- 🔄 Sau 24h tự động chuyển sang paid plan (hoặc hủy)

**Lưu ý:** Một số broker có thể cung cấp FREE VPS với điều kiện:
- 💰 Balance ≥ $500 (hoặc $300 tùy broker)
- 📊 Trading volume ≥ 2 lots/tháng
- 🏦 Tài khoản active liên tục
- ⚠️ **Check với broker của bạn** - không có trên trang chính thức MQL5

---

### **Bước 2: Đăng Ký VPS Từ MT5 Terminal**

#### **2.1. Mở VPS Settings**
```
MT5 Terminal → Tools → Options → VPS Tab
```

Hoặc click icon VPS trên toolbar (hình cloud ☁️)

#### **2.2. Chọn Service Plan**
- **Mini (1 month)**: $15/month - Test ngắn hạn
- **Optimal (3 months)**: $13/month - Good balance
- **Long (6 months)**: $10.83/month - Save $25/year
- **Max (12 months)**: $10/month - Best value, save $60/year ⭐

#### **2.3. One-Click Deployment**
```
Click "Rent" → Select plan → Confirm
→ MT5 tự động transfer environment lên cloud
```

**Process:**
1. MT5 uploads your settings, EAs, indicators
2. System allocates resources (3GB RAM, 16GB disk, CPUs)
3. Auto-selects nearest hosting point (30+ locations)
4. Bot starts running within 2-3 minutes

#### **2.4. Technical Support**
- ✉️ Included với tất cả plans
- 📞 Contact qua MQL5.com support portal
- 📚 Documentation: https://www.mql5.com/en/vps

---

### **Bước 3: Verify VPS Connection**
```
Status: Connected ✅
Latency: <10ms ✅ (96% brokers achieve this)
Migration: Completed ✅
Resources: 3GB RAM, 16GB Disk ✅
```

**Test latency:**
```
Right-click VPS icon → Show Journal
→ Check "Ping to trade server: X ms"
```

---

### **Bước 4: Chuẩn Bị Bot Cho VPS**

#### **4.1. Package Project**

Tạo folder deploy:
```powershell
# Tạo folder deploy clean
mkdir deploy_package
cd deploy_package

# Copy essential files
Copy-Item ..\core -Recurse
Copy-Item ..\engines -Recurse
Copy-Item ..\utils -Recurse
Copy-Item ..\config -Recurse
Copy-Item ..\requirements.txt

# Copy run scripts
Copy-Item ..\run_bot.py
Copy-Item ..\run_ict_bot.py
Copy-Item ..\run_ict_bot_smc.py

# Create logs folder
mkdir logs
```

#### **4.2. Tạo Startup Script**

**File: `start_bot.bat`**
```batch
@echo off
echo ========================================
echo Starting ML-SuperTrend MT5 Bot
echo ========================================

REM Set Python path (adjust for VPS Python location)
set PYTHON=C:\Python311\python.exe

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start the bot with auto-restart
:start
echo [%date% %time%] Starting bot...
%PYTHON% run_bot.py --account demo --symbol BTCUSDm --interval 60 >> logs\bot_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log 2>&1

REM If bot crashes, wait 30 seconds and restart
echo [%date% %time%] Bot stopped. Restarting in 30 seconds...
timeout /t 30 /nobreak
goto start
```

#### **4.3. Tạo Config Cho VPS**

**File: `config/config.vps.json`**
```json
{
    "accounts": {
        "demo": {
            "login": YOUR_ACCOUNT_NUMBER,
            "password": "YOUR_PASSWORD",
            "server": "YOUR_SERVER"
        }
    },
    "symbols": {
        "BTCUSDm": {
            "enabled": true,
            "timeframe": "M5",
            "risk_percent": 0.5,
            "sl_multiplier": 2.0,
            "tp_multiplier": 8.0
        }
    },
    "global_settings": {
        "max_daily_loss_percent": 5.0,
        "max_positions_per_symbol": 1,
        "use_trailing_stop": true
    }
}
```

---

### **Bước 5: Upload Files lên VPS**

#### **5.1. Connect RDP to VPS**

**⚠️ Lưu ý:** MT5 VPS không cung cấp RDP access mặc định. Bạn chỉ cần:
1. ✅ MT5 tự động sync environment (EAs, settings)
2. ✅ Bot Python cần chạy **trên máy local** hoặc **VPS riêng**
3. ✅ MT5 VPS chỉ dành cho **Expert Advisors (EAs)** viết bằng MQL5

**Nếu muốn chạy Python bot 24/7:**
- Option A: Convert Python logic sang EA (MQL5)
- Option B: Thuê Windows VPS riêng (xem Option 3 phía trên)
- Option C: Dùng AWS/GCP/Azure (xem Option 2 phía trên)

#### **5.2. Transfer Files (Nếu dùng VPS riêng)**

**Option A: Copy/Paste trong RDP**
```
1. Connect RDP với "Local Resources" enabled
2. Copy folder từ máy local
3. Paste vào VPS Desktop
```

**Option B: Upload qua OneDrive/Google Drive**
```
1. Upload project lên cloud drive
2. Download trong VPS
3. Extract to C:\TradingBot
```

#### **5.2. Transfer Files (Nếu dùng VPS riêng)**

**Option A: Copy/Paste trong RDP**
```
1. Connect RDP với "Local Resources" enabled
2. Copy folder từ máy local
3. Paste vào VPS Desktop
```

**Option B: Upload qua OneDrive/Google Drive**
```
1. Upload project lên cloud drive
2. Download trong VPS
3. Extract to C:\TradingBot
```

#### **5.3. Cài Đặt Python Trên VPS (Windows VPS riêng)**

**Download Python:**
```
1. Trong VPS, mở Edge browser
2. Download: https://www.python.org/downloads/
3. Chọn Python 3.11+ Windows installer
4. Install với option "Add to PATH"
```

**Install Dependencies:**
```batch
cd C:\TradingBot
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Install TA-Lib:**
```batch
# Copy TA-Lib wheel vào VPS
pip install data\ta_lib-0.6.7-cp311-cp311-win_amd64.whl
```

---

### **Bước 6: Test Bot Trên VPS**

#### **6.1. Manual Test**
```batch
cd C:\TradingBot
python run_bot.py --account demo --symbol BTCUSDm
```

**Verify:**
- ✅ MT5 connection successful
- ✅ Data loading OK
- ✅ Bot running without errors
- ✅ Ctrl+C để dừng

#### **6.2. Test Auto-Restart**
```batch
start_bot.bat
```

**Verify:**
- ✅ Bot starts automatically
- ✅ Logs được ghi vào file
- ✅ Bot restart sau khi crash

---

### **Bước 7: Chạy Bot 24/7 (Windows VPS riêng)**

**⚠️ Lưu ý:** Phần này chỉ áp dụng nếu bạn dùng Windows VPS riêng (không phải MT5 VPS).

#### **7.1. Tạo Windows Task Scheduler**

**Run as Scheduled Task:**
```
1. VPS → Search "Task Scheduler"
2. Create Basic Task
3. Name: "TradingBot-AutoStart"
4. Trigger: "When computer starts"
5. Action: "Start a program"
6. Program: C:\TradingBot\start_bot.bat
7. Finish
```

**Test:**
```
Right-click task → Run
→ Check logs\bot_*.log
```

#### **7.2. Tạo Watchdog Script** (Advanced)

**File: `watchdog.py`**
```python
"""
Watchdog script to monitor and restart bot if crashed
"""
import subprocess
import time
import os
from datetime import datetime

BOT_SCRIPT = "run_bot.py"
CHECK_INTERVAL = 60  # Check every 60 seconds
LOG_FILE = "logs/watchdog.log"

def is_bot_running():
    """Check if bot process is running"""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq python.exe'],
            capture_output=True,
            text=True
        )
        return BOT_SCRIPT in result.stdout
    except:
        return False

def log_message(msg):
    """Write message to log file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def start_bot():
    """Start the bot process"""
    try:
        subprocess.Popen(
            ['python', BOT_SCRIPT, '--account', 'demo', '--symbol', 'BTCUSDm'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        log_message("✅ Bot started successfully")
        return True
    except Exception as e:
        log_message(f"❌ Failed to start bot: {e}")
        return False

def main():
    log_message("🚀 Watchdog started")
    
    while True:
        try:
            if not is_bot_running():
                log_message("⚠️ Bot not running! Attempting to restart...")
                start_bot()
            else:
                log_message("✅ Bot is running")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log_message("🛑 Watchdog stopped by user")
            break
        except Exception as e:
            log_message(f"❌ Watchdog error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    main()
```

**Run Watchdog:**
```batch
python watchdog.py
```

---

### **Bước 7: Monitoring & Maintenance**

#### **7.1. Check Bot Status**

**Via RDP:**
```
1. Connect RDP to VPS
2. Check Task Manager → Python processes
3. Check logs\bot_*.log
```

**Via Telegram (Recommended - see setup below):**
```
/status - Check bot status
/balance - Check account balance
/positions - View open positions
/stats - Trading statistics
```

#### **7.2. Log Rotation**

**File: `scripts/rotate_logs.py`**
```python
"""
Rotate log files to prevent disk full
"""
import os
import shutil
from datetime import datetime, timedelta

LOG_DIR = "logs"
MAX_LOG_AGE_DAYS = 30
MAX_LOG_SIZE_MB = 100

def rotate_logs():
    """Delete old logs and compress large logs"""
    cutoff_date = datetime.now() - timedelta(days=MAX_LOG_AGE_DAYS)
    
    for filename in os.listdir(LOG_DIR):
        filepath = os.path.join(LOG_DIR, filename)
        
        # Skip if not a file
        if not os.path.isfile(filepath):
            continue
        
        # Get file stats
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        # Delete old logs
        if file_time < cutoff_date:
            os.remove(filepath)
            print(f"Deleted old log: {filename}")
        
        # Archive large logs
        elif file_size_mb > MAX_LOG_SIZE_MB:
            archive_name = f"{filepath}.{datetime.now().strftime('%Y%m%d')}.archive"
            shutil.move(filepath, archive_name)
            print(f"Archived large log: {filename} → {archive_name}")

if __name__ == "__main__":
    rotate_logs()
```

**Schedule Daily:**
```
Task Scheduler → Daily 3:00 AM
Program: python scripts/rotate_logs.py
```

#### **7.3. Health Checks**

**File: `scripts/health_check.py`**
```python
"""
Health check script to verify bot is working
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime

def check_mt5_connection():
    """Check MT5 connection"""
    if not mt5.initialize():
        return False, "MT5 initialization failed"
    
    account_info = mt5.account_info()
    if account_info is None:
        return False, "Cannot get account info"
    
    return True, f"Connected: {account_info.login}"

def check_positions():
    """Check if positions are being managed"""
    positions = mt5.positions_total()
    return True, f"Open positions: {positions}"

def check_balance():
    """Check account balance"""
    account_info = mt5.account_info()
    if account_info:
        balance = account_info.balance
        equity = account_info.equity
        return True, f"Balance: ${balance:.2f}, Equity: ${equity:.2f}"
    return False, "Cannot get balance"

def main():
    """Run all health checks"""
    print("="*50)
    print(f"Health Check: {datetime.now()}")
    print("="*50)
    
    checks = [
        ("MT5 Connection", check_mt5_connection),
        ("Positions", check_positions),
        ("Account Balance", check_balance),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {check_name}: {message}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ FAIL - {check_name}: {e}")
            all_passed = False
    
    mt5.shutdown()
    
    print("="*50)
    if all_passed:
        print("✅ All checks passed")
        sys.exit(0)
    else:
        print("❌ Some checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Schedule Every Hour:**
```
Task Scheduler → Every 1 hour
Program: python scripts/health_check.py >> logs/health_check.log
```

---

## 📱 Setup Telegram Alerts (Optional)

### **Bước 1: Tạo Telegram Bot**

1. Mở Telegram → Search **@BotFather**
2. Send `/newbot`
3. Name: "My Trading Bot"
4. Username: "my_trading_bot" (unique)
5. Copy **Bot Token**: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

### **Bước 2: Get Chat ID**

1. Search **@userinfobot**
2. Start conversation
3. Copy **Chat ID**: `123456789`

### **Bước 3: Tạo Telegram Notifier**

**File: `utils/telegram_notifier.py`**
```python
"""
Telegram notification for trading bot
"""
import requests
import json
from datetime import datetime

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, message):
        """Send text message"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Failed to send Telegram: {e}")
            return None
    
    def notify_trade(self, signal_type, symbol, entry, sl, tp, lot_size):
        """Notify new trade"""
        message = f"""
🤖 *New Trade Alert*

📊 Symbol: `{symbol}`
🔔 Signal: *{signal_type}*
💰 Entry: `{entry:.5f}`
🛑 SL: `{sl:.5f}`
🎯 TP: `{tp:.5f}`
📦 Lot Size: `{lot_size:.2f}`

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def notify_closed(self, symbol, profit, duration):
        """Notify trade closed"""
        emoji = "✅" if profit > 0 else "❌"
        message = f"""
{emoji} *Trade Closed*

📊 Symbol: `{symbol}`
💵 P&L: `${profit:.2f}`
⏱ Duration: `{duration}`

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def notify_error(self, error_msg):
        """Notify error"""
        message = f"""
⚠️ *Bot Error*

```
{error_msg}
```

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def notify_status(self, balance, equity, positions):
        """Send status update"""
        message = f"""
📊 *Bot Status*

💰 Balance: `${balance:.2f}`
💎 Equity: `${equity:.2f}`
📈 Open Positions: `{positions}`

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)

# Usage Example:
if __name__ == "__main__":
    # Configuration
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    
    notifier = TelegramNotifier(BOT_TOKEN, CHAT_ID)
    notifier.notify_status(balance=10000, equity=10050, positions=2)
```

### **Bước 4: Tích Hợp Vào Bot**

Add vào `run_bot.py`:
```python
from utils.telegram_notifier import TelegramNotifier

# Initialize
telegram = TelegramNotifier(
    bot_token=config['telegram']['bot_token'],
    chat_id=config['telegram']['chat_id']
)

# On trade open
telegram.notify_trade('BUY', 'BTCUSD', 67000, 65000, 69000, 0.05)

# On trade close
telegram.notify_closed('BTCUSD', profit=+150.50, duration='2h 30m')

# On error
telegram.notify_error(str(exception))
```

---

## 💰 Chi Phí Ước Tính

### **MT5 VPS Pricing**

| Provider | Free Conditions | Paid Price | Specs |
|----------|----------------|------------|-------|
| **Exness** | Balance ≥$500 + 2 lots/mo | $10/month | 1 CPU, 1.5GB RAM, 20GB SSD |
| **XM** | Balance ≥$500 + 0.5 lots/mo | $12/month | 1 CPU, 1GB RAM, 15GB SSD |
| **IC Markets** | Balance ≥$2000 | $15/month | 2 CPU, 2GB RAM, 30GB SSD |
| **FBS** | Balance ≥$450 + 3 lots/mo | $8/month | 1 CPU, 1GB RAM, 10GB SSD |

### **Alternative VPS Providers**

| Provider | Price | Specs | Best For |
|----------|-------|-------|----------|
| **Vultr** | $6/mo | 1 CPU, 1GB RAM, 25GB SSD | Budget |
| **DigitalOcean** | $12/mo | 1 CPU, 2GB RAM, 50GB SSD | Balanced |
| **AWS Lightsail** | $5/mo | 512MB RAM (limited) | Testing |
| **Contabo** | $4/mo | 4 CPU, 8GB RAM, 200GB SSD | Best Value |
| **Google Cloud** | $10-30/mo | Scalable | Advanced |

---

## ✅ Checklist Trước Khi Deploy

### **Pre-Deployment**
- [ ] Test bot hoàn toàn trên local
- [ ] Backtest cho kết quả realistic
- [ ] All unit tests pass
- [ ] Config file đã điều chỉnh cho VPS
- [ ] Credentials secure (không hardcode)

### **VPS Setup**
- [ ] VPS đã provision và connect
- [ ] Python đã cài đặt (3.8+)
- [ ] Dependencies đã install
- [ ] TA-Lib đã cài
- [ ] MT5 terminal đã cài và login

### **Bot Configuration**
- [ ] Config file uploaded
- [ ] Secrets/passwords an toàn
- [ ] Log rotation configured
- [ ] Health check scheduled
- [ ] Auto-restart enabled

### **Monitoring**
- [ ] Telegram alerts setup (optional)
- [ ] Log files được monitor
- [ ] Health checks running
- [ ] Có cách kiểm tra từ xa (RDP/SSH)

---

## 🆘 Troubleshooting

### **Issue: Bot không start trên VPS**
```
Solution:
1. Check Python path trong startup script
2. Verify dependencies: pip list
3. Check logs\bot_*.log cho errors
4. Test manually: python run_bot.py
```

### **Issue: MT5 connection failed**
```
Solution:
1. Verify MT5 terminal đã login
2. Check account credentials trong config
3. Test: python -c "import MetaTrader5 as mt5; print(mt5.initialize())"
4. Restart MT5 terminal
```

### **Issue: VPS disconnect often**
```
Solution:
1. Check VPS balance/payment
2. Verify trading volume đủ điều kiện FREE
3. Contact broker support
4. Consider alternative VPS provider
```

### **Issue: High latency/slow execution**
```
Solution:
1. Choose VPS server gần broker
2. Upgrade VPS plan (more RAM/CPU)
3. Optimize bot code (reduce indicators)
4. Close unnecessary programs trên VPS
```

---

## 📝 Best Practices

### **Security**
1. ✅ Không share VPS credentials
2. ✅ Use strong passwords
3. ✅ Enable Windows Firewall
4. ✅ Regular backup config files
5. ✅ Monitor login attempts

### **Performance**
1. ✅ Keep VPS clean (no unnecessary software)
2. ✅ Regular updates (Windows, Python)
3. ✅ Monitor CPU/RAM usage
4. ✅ Optimize bot settings
5. ✅ Use efficient indicators

### **Reliability**
1. ✅ Auto-restart mechanism
2. ✅ Health checks scheduled
3. ✅ Log rotation
4. ✅ Telegram alerts for critical events
5. ✅ Daily manual verification

### **Risk Management**
1. ✅ Start với demo account
2. ✅ Test 1-2 tuần trước khi live
3. ✅ Set daily loss limits
4. ✅ Monitor drawdown
5. ✅ Have emergency stop plan

---

## 🎯 Kết Luận

**MT5 VPS** là lựa chọn tốt nhất cho **beginners** vì:
- ✅ Setup đơn giản (< 15 phút)
- ✅ Không cần kiến thức DevOps
- ✅ Có thể FREE nếu đủ điều kiện
- ✅ Support từ broker
- ✅ Low latency

**Recommend:**
1. Dùng **MT5 VPS** cho 1-2 bots
2. Setup **Telegram alerts** để monitor
3. Test **demo 1 tuần** trước live
4. Backup **config** thường xuyên
5. Monitor **hàng ngày** ban đầu

**Good luck với bot 24/7!** 🚀
