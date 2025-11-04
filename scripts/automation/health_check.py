"""
Health Check Script - Verify Bot and MT5 Status
Checks: MT5 connection, account balance, open positions, bot logs
Can be scheduled to run periodically (e.g., every hour)
"""

import MetaTrader5 as mt5
import os
import sys
import json
from datetime import datetime, timedelta
import glob

# Get project root directory (2 levels up from this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))

# Add project root to Python path for imports
sys.path.insert(0, PROJECT_ROOT)


class HealthChecker:
    def __init__(self, send_alerts=False):
        self.send_alerts = send_alerts
        self.health_status = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'UNKNOWN'
        }
        
        # Try to import telegram notifier if alerts enabled
        if send_alerts:
            try:
                from utils.telegram_notifier import TelegramNotifier
                self.telegram = TelegramNotifier()
            except:
                print(" Could not import TelegramNotifier - alerts disabled")
                self.send_alerts = False
    
    def log(self, message, status="INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{status}] {message}")
    
    def check_mt5_connection(self):
        """Check if MT5 is connected"""
        self.log("Checking MT5 connection...", "INFO")
        
        try:
            # Initialize MT5
            if not mt5.initialize():
                error = mt5.last_error()
                self.health_status['checks']['mt5_connection'] = {
                    'status': 'FAIL',
                    'message': f"MT5 initialization failed: {error}"
                }
                return False
            
            # Check terminal info
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                self.health_status['checks']['mt5_connection'] = {
                    'status': 'FAIL',
                    'message': "Cannot get terminal info"
                }
                return False
            
            # Connected successfully
            self.health_status['checks']['mt5_connection'] = {
                'status': 'PASS',
                'message': 'MT5 connected',
                'connected': terminal_info.connected,
                'trade_allowed': terminal_info.trade_allowed,
                'build': terminal_info.build
            }
            
            self.log(f" MT5 Connected (Build: {terminal_info.build})", "SUCCESS")
            return True
            
        except Exception as e:
            self.health_status['checks']['mt5_connection'] = {
                'status': 'FAIL',
                'message': f"Exception: {str(e)}"
            }
            self.log(f" MT5 Connection Error: {e}", "ERROR")
            return False
    
    def check_account_status(self):
        """Check account balance and equity"""
        self.log("Checking account status...", "INFO")
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                self.health_status['checks']['account_status'] = {
                    'status': 'FAIL',
                    'message': "Cannot get account info"
                }
                return False
            
            # Get account details
            balance = account_info.balance
            equity = account_info.equity
            margin = account_info.margin
            free_margin = account_info.margin_free
            margin_level = account_info.margin_level if account_info.margin > 0 else 0
            
            # Check if account is in danger (margin level < 100%)
            status = 'PASS'
            if margin > 0 and margin_level < 100:
                status = 'WARNING'
            
            self.health_status['checks']['account_status'] = {
                'status': status,
                'balance': balance,
                'equity': equity,
                'margin': margin,
                'free_margin': free_margin,
                'margin_level': f"{margin_level:.2f}%",
                'login': account_info.login,
                'server': account_info.server
            }
            
            self.log(
                f" Account: Login={account_info.login}, "
                f"Balance=${balance:.2f}, "
                f"Equity=${equity:.2f}, "
                f"Margin Level={margin_level:.2f}%",
                "SUCCESS" if status == 'PASS' else "WARNING"
            )
            return True
            
        except Exception as e:
            self.health_status['checks']['account_status'] = {
                'status': 'FAIL',
                'message': f"Exception: {str(e)}"
            }
            self.log(f" Account Status Error: {e}", "ERROR")
            return False
    
    def check_open_positions(self):
        """Check open positions"""
        self.log("Checking open positions...", "INFO")
        
        try:
            positions = mt5.positions_get()
            
            if positions is None:
                self.health_status['checks']['open_positions'] = {
                    'status': 'FAIL',
                    'message': "Cannot get positions"
                }
                return False
            
            # Analyze positions
            total_positions = len(positions)
            total_profit = sum([p.profit for p in positions])
            
            position_details = []
            for pos in positions:
                position_details.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'time': datetime.fromtimestamp(pos.time).isoformat()
                })
            
            self.health_status['checks']['open_positions'] = {
                'status': 'PASS',
                'count': total_positions,
                'total_profit': total_profit,
                'positions': position_details
            }
            
            self.log(
                f" Positions: {total_positions} open, "
                f"Total P&L: ${total_profit:.2f}",
                "SUCCESS"
            )
            return True
            
        except Exception as e:
            self.health_status['checks']['open_positions'] = {
                'status': 'FAIL',
                'message': f"Exception: {str(e)}"
            }
            self.log(f" Positions Check Error: {e}", "ERROR")
            return False
    
    def check_recent_logs(self):
        """Check recent bot logs for errors"""
        self.log("Checking recent logs...", "INFO")
        
        try:
            # Find latest log file
            log_pattern = os.path.join(PROJECT_ROOT, 'logs', 'bot_*.log')
            log_files = glob.glob(log_pattern)
            if not log_files:
                self.health_status['checks']['recent_logs'] = {
                    'status': 'WARNING',
                    'message': 'No log files found'
                }
                self.log(" No log files found", "WARNING")
                return True  # Not critical
            
            # Get most recent log
            latest_log = max(log_files, key=os.path.getctime)
            
            # Read last 50 lines
            with open(latest_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
            
            # Count errors and warnings
            errors = [line for line in recent_lines if 'ERROR' in line]
            warnings = [line for line in recent_lines if 'WARNING' in line]
            
            # Determine status
            status = 'PASS'
            if len(errors) > 10:
                status = 'FAIL'
            elif len(errors) > 0 or len(warnings) > 5:
                status = 'WARNING'
            
            self.health_status['checks']['recent_logs'] = {
                'status': status,
                'latest_log': latest_log,
                'error_count': len(errors),
                'warning_count': len(warnings),
                'recent_errors': [e.strip() for e in errors[-3:]]  # Last 3 errors
            }
            
            self.log(
                f" Logs: {len(errors)} errors, {len(warnings)} warnings",
                "SUCCESS" if status == 'PASS' else status
            )
            return status != 'FAIL'
            
        except Exception as e:
            self.health_status['checks']['recent_logs'] = {
                'status': 'WARNING',
                'message': f"Exception: {str(e)}"
            }
            self.log(f" Log Check Error: {e}", "WARNING")
            return True  # Not critical
    
    def check_disk_space(self):
        """Check available disk space"""
        self.log("Checking disk space...", "INFO")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            
            free_gb = free / (1024**3)
            percent_free = (free / total) * 100
            
            # Warning if < 1GB free
            status = 'PASS'
            if free_gb < 1:
                status = 'WARNING'
            
            self.health_status['checks']['disk_space'] = {
                'status': status,
                'free_gb': f"{free_gb:.2f}",
                'percent_free': f"{percent_free:.1f}%"
            }
            
            self.log(
                f" Disk: {free_gb:.2f}GB free ({percent_free:.1f}%)",
                "SUCCESS" if status == 'PASS' else "WARNING"
            )
            return True
            
        except Exception as e:
            self.health_status['checks']['disk_space'] = {
                'status': 'WARNING',
                'message': f"Exception: {str(e)}"
            }
            self.log(f" Disk Check Error: {e}", "WARNING")
            return True  # Not critical
    
    def determine_overall_status(self):
        """Determine overall health status"""
        checks = self.health_status['checks']
        
        # If any critical check failed
        critical_checks = ['mt5_connection', 'account_status']
        for check in critical_checks:
            if check in checks and checks[check]['status'] == 'FAIL':
                self.health_status['overall_status'] = 'FAIL'
                return 'FAIL'
        
        # If any check has warning
        for check_name, check_data in checks.items():
            if check_data['status'] == 'WARNING':
                self.health_status['overall_status'] = 'WARNING'
                return 'WARNING'
        
        # All passed
        self.health_status['overall_status'] = 'PASS'
        return 'PASS'
    
    def send_alert(self, status):
        """Send alert via Telegram if enabled"""
        if not self.send_alerts:
            return
        
        try:
            if status == 'FAIL':
                message = " *CRITICAL: Health Check Failed*\n\n"
            elif status == 'WARNING':
                message = " *WARNING: Health Check Issues*\n\n"
            else:
                return  # Don't send alerts for PASS
            
            # Add details
            for check_name, check_data in self.health_status['checks'].items():
                if check_data['status'] != 'PASS':
                    message += f"• {check_name}: {check_data.get('message', 'Issue detected')}\n"
            
            self.telegram.send_message(message)
            self.log("Alert sent via Telegram", "INFO")
            
        except Exception as e:
            self.log(f"Failed to send alert: {e}", "ERROR")
    
    def save_report(self):
        """Save health check report to file"""
        try:
            log_dir = os.path.join(PROJECT_ROOT, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            report_file = os.path.join(log_dir, f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.health_status, f, indent=2)
            
            self.log(f"Report saved: {report_file}", "INFO")
            
        except Exception as e:
            self.log(f"Failed to save report: {e}", "ERROR")
    
    def run_all_checks(self):
        """Run all health checks"""
        self.log("="*60, "INFO")
        self.log("Starting Health Check", "INFO")
        self.log("="*60, "INFO")
        
        # Run checks
        self.check_mt5_connection()
        self.check_account_status()
        self.check_open_positions()
        self.check_recent_logs()
        self.check_disk_space()
        
        # Shutdown MT5
        mt5.shutdown()
        
        # Determine overall status
        overall = self.determine_overall_status()
        
        # Print summary
        self.log("="*60, "INFO")
        self.log(f"Health Check Complete: {overall}", 
                "SUCCESS" if overall == 'PASS' else overall)
        self.log("="*60, "INFO")
        
        # Send alert if needed
        self.send_alert(overall)
        
        # Save report
        self.save_report()
        
        return overall


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MT5 Bot Health Checker')
    parser.add_argument('--alerts', action='store_true', 
                       help='Send Telegram alerts on failure')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    # Run health check
    checker = HealthChecker(send_alerts=args.alerts)
    status = checker.run_all_checks()
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(checker.health_status, indent=2))
    
    # Exit code: 0 = PASS, 1 = WARNING, 2 = FAIL
    exit_code = {'PASS': 0, 'WARNING': 1, 'FAIL': 2}.get(status, 2)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
