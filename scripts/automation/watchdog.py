"""
Watchdog Script - Monitor and Auto-Restart Bot
Ensures bot is always running, restarts if crashed
"""

import subprocess
import time
import os
import sys
from datetime import datetime
import psutil

# Get project root directory (2 levels up from this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# Configuration
BOT_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "runners", "run_bot.py")
BOT_ARGS = ["--account", "demo", "--symbol", "BTCUSDm", "--interval", "60"]
CHECK_INTERVAL = 60  # Check every 60 seconds
MAX_RESTART_ATTEMPTS = 5
RESTART_COOLDOWN = 300  # Wait 5 minutes after max restarts
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "watchdog.log")

class BotWatchdog:
    def __init__(self):
        self.bot_process = None
        self.restart_count = 0
        self.last_restart_time = None
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Create logs directory if not exists"""
        log_dir = os.path.join(PROJECT_ROOT, 'logs')
        os.makedirs(log_dir, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Write message to log file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # Print to console
        print(log_message)
        
        # Write to file
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Failed to write log: {e}")
    
    def is_bot_running(self):
        """Check if bot process is running"""
        if self.bot_process is None:
            return False
        
        try:
            # Check if process still exists
            return self.bot_process.poll() is None
        except:
            return False
    
    def get_bot_info(self):
        """Get bot process information"""
        if not self.is_bot_running():
            return None
        
        try:
            process = psutil.Process(self.bot_process.pid)
            return {
                'pid': process.pid,
                'cpu_percent': process.cpu_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'status': process.status(),
                'uptime': time.time() - process.create_time()
            }
        except:
            return None
    
    def start_bot(self):
        """Start the bot process"""
        try:
            self.log("Starting bot...", "INFO")
            
            # Start bot as subprocess
            self.bot_process = subprocess.Popen(
                [sys.executable, BOT_SCRIPT] + BOT_ARGS,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait a bit to see if it starts successfully
            time.sleep(5)
            
            if self.is_bot_running():
                self.log(f" Bot started successfully (PID: {self.bot_process.pid})", "SUCCESS")
                self.restart_count += 1
                self.last_restart_time = datetime.now()
                return True
            else:
                self.log(" Bot failed to start", "ERROR")
                return False
                
        except Exception as e:
            self.log(f" Failed to start bot: {e}", "ERROR")
            return False
    
    def stop_bot(self):
        """Stop the bot process"""
        if not self.is_bot_running():
            return
        
        try:
            self.log("Stopping bot...", "INFO")
            self.bot_process.terminate()
            
            # Wait up to 10 seconds for graceful shutdown
            try:
                self.bot_process.wait(timeout=10)
                self.log("Bot stopped gracefully", "INFO")
            except subprocess.TimeoutExpired:
                self.log("Bot didn't stop gracefully, forcing...", "WARNING")
                self.bot_process.kill()
                self.bot_process.wait()
                self.log("Bot force-stopped", "WARNING")
                
        except Exception as e:
            self.log(f"Error stopping bot: {e}", "ERROR")
    
    def check_restart_limit(self):
        """Check if restart limit exceeded"""
        if self.restart_count >= MAX_RESTART_ATTEMPTS:
            if self.last_restart_time:
                time_since_restart = (datetime.now() - self.last_restart_time).total_seconds()
                if time_since_restart < RESTART_COOLDOWN:
                    remaining = RESTART_COOLDOWN - time_since_restart
                    self.log(f" Max restart attempts reached. Cooldown: {remaining:.0f}s", "WARNING")
                    return False
                else:
                    # Reset counter after cooldown
                    self.log("Cooldown period passed, resetting restart counter", "INFO")
                    self.restart_count = 0
        return True
    
    def monitor_health(self):
        """Monitor bot health and log statistics"""
        info = self.get_bot_info()
        if info:
            uptime_str = f"{info['uptime']/3600:.1f}h"
            self.log(
                f" Bot Status: "
                f"PID={info['pid']}, "
                f"CPU={info['cpu_percent']:.1f}%, "
                f"RAM={info['memory_mb']:.1f}MB, "
                f"Uptime={uptime_str}",
                "INFO"
            )
        else:
            self.log(" Cannot get bot info", "WARNING")
    
    def run(self):
        """Main watchdog loop"""
        self.log(" Watchdog started", "INFO")
        self.log(f"Monitoring: {BOT_SCRIPT} {' '.join(BOT_ARGS)}", "INFO")
        
        # Start bot initially
        self.start_bot()
        
        try:
            while True:
                # Check if bot is running
                if not self.is_bot_running():
                    self.log(" Bot not running!", "WARNING")
                    
                    # Check restart limits
                    if self.check_restart_limit():
                        self.log("Attempting to restart bot...", "INFO")
                        if not self.start_bot():
                            self.log("Failed to restart. Waiting before retry...", "ERROR")
                            time.sleep(30)
                    else:
                        # Wait during cooldown
                        time.sleep(60)
                else:
                    # Bot is running - monitor health every 5 minutes
                    if int(time.time()) % 300 == 0:
                        self.monitor_health()
                
                # Wait before next check
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            self.log("\n🛑 Watchdog stopped by user", "INFO")
            self.stop_bot()
        except Exception as e:
            self.log(f" Watchdog error: {e}", "ERROR")
            self.stop_bot()
        finally:
            self.log("Watchdog shut down", "INFO")


def main():
    """Entry point"""
    print("="*60)
    print("BOT WATCHDOG - Auto-Restart Service")
    print("="*60)
    print()
    
    # Check if bot script exists
    if not os.path.exists(BOT_SCRIPT):
        print(f"ERROR: Bot script '{BOT_SCRIPT}' not found!")
        sys.exit(1)
    
    # Start watchdog
    watchdog = BotWatchdog()
    watchdog.run()


if __name__ == "__main__":
    main()
