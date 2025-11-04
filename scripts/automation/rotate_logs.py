"""
Log Rotation Script - Clean and Archive Old Logs
Prevents disk from filling up with log files
Can be scheduled to run daily (e.g., 3:00 AM)
"""

import os
import glob
import gzip
import shutil
from datetime import datetime, timedelta

# Get project root directory (2 levels up from this script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))


class LogRotator:
    def __init__(self, 
                 log_dir=None,
                 max_age_days=30,
                 max_size_mb=100,
                 compress_age_days=7):
        """
        Initialize log rotator
        
        Args:
            log_dir: Directory containing log files (default: PROJECT_ROOT/logs)
            max_age_days: Delete logs older than this (days)
            max_size_mb: Compress logs larger than this (MB)
            compress_age_days: Compress logs older than this (days)
        """
        if log_dir is None:
            log_dir = os.path.join(PROJECT_ROOT, 'logs')
        self.log_dir = log_dir
        self.max_age_days = max_age_days
        self.max_size_mb = max_size_mb
        self.compress_age_days = compress_age_days
        
        self.stats = {
            'deleted': 0,
            'compressed': 0,
            'space_freed_mb': 0,
            'errors': []
        }
    
    def log(self, message, level="INFO"):
        """Print log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def get_file_age_days(self, filepath):
        """Get file age in days"""
        file_time = os.path.getmtime(filepath)
        file_date = datetime.fromtimestamp(file_time)
        age = datetime.now() - file_date
        return age.days
    
    def get_file_size_mb(self, filepath):
        """Get file size in MB"""
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    
    def compress_file(self, filepath):
        """Compress file with gzip"""
        try:
            output_path = filepath + '.gz'
            
            # Check if already compressed
            if os.path.exists(output_path):
                self.log(f"Skipping {filepath} - already compressed", "INFO")
                return False
            
            # Compress
            with open(filepath, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Get sizes
            original_size = self.get_file_size_mb(filepath)
            compressed_size = self.get_file_size_mb(output_path)
            saved = original_size - compressed_size
            
            # Delete original
            os.remove(filepath)
            
            self.log(
                f" Compressed: {os.path.basename(filepath)} "
                f"({original_size:.2f}MB  {compressed_size:.2f}MB, "
                f"saved {saved:.2f}MB)",
                "SUCCESS"
            )
            
            self.stats['compressed'] += 1
            self.stats['space_freed_mb'] += saved
            return True
            
        except Exception as e:
            error_msg = f"Failed to compress {filepath}: {e}"
            self.log(error_msg, "ERROR")
            self.stats['errors'].append(error_msg)
            return False
    
    def delete_file(self, filepath):
        """Delete file"""
        try:
            size_mb = self.get_file_size_mb(filepath)
            os.remove(filepath)
            
            self.log(
                f"🗑️ Deleted: {os.path.basename(filepath)} ({size_mb:.2f}MB)",
                "INFO"
            )
            
            self.stats['deleted'] += 1
            self.stats['space_freed_mb'] += size_mb
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete {filepath}: {e}"
            self.log(error_msg, "ERROR")
            self.stats['errors'].append(error_msg)
            return False
    
    def rotate_logs(self):
        """Main log rotation logic"""
        self.log("="*60, "INFO")
        self.log("Starting Log Rotation", "INFO")
        self.log("="*60, "INFO")
        
        # Check if log directory exists
        if not os.path.exists(self.log_dir):
            self.log(f"Log directory '{self.log_dir}' not found", "WARNING")
            return
        
        # Get all log files (including .gz)
        log_patterns = [
            os.path.join(self.log_dir, 'bot_*.log'),
            os.path.join(self.log_dir, 'watchdog.log'),
            os.path.join(self.log_dir, 'health_check_*.json'),
            os.path.join(self.log_dir, '*.log.gz')
        ]
        
        all_files = []
        for pattern in log_patterns:
            all_files.extend(glob.glob(pattern))
        
        if not all_files:
            self.log("No log files found", "INFO")
            return
        
        self.log(f"Found {len(all_files)} log files", "INFO")
        
        # Process each file
        for filepath in all_files:
            filename = os.path.basename(filepath)
            age_days = self.get_file_age_days(filepath)
            size_mb = self.get_file_size_mb(filepath)
            
            # Skip today's files
            if age_days == 0:
                self.log(f"Skipping {filename} - current file", "INFO")
                continue
            
            # Delete very old files
            if age_days > self.max_age_days:
                self.log(f"Deleting {filename} - {age_days} days old", "INFO")
                self.delete_file(filepath)
                continue
            
            # Compress old uncompressed files
            if not filepath.endswith('.gz'):
                # Compress if old enough
                if age_days >= self.compress_age_days:
                    self.log(f"Compressing {filename} - {age_days} days old", "INFO")
                    self.compress_file(filepath)
                # Compress if too large
                elif size_mb >= self.max_size_mb:
                    self.log(f"Compressing {filename} - {size_mb:.2f}MB", "INFO")
                    self.compress_file(filepath)
        
        # Print summary
        self.log("="*60, "INFO")
        self.log("Log Rotation Complete", "SUCCESS")
        self.log(f"Files deleted: {self.stats['deleted']}", "INFO")
        self.log(f"Files compressed: {self.stats['compressed']}", "INFO")
        self.log(f"Space freed: {self.stats['space_freed_mb']:.2f}MB", "INFO")
        if self.stats['errors']:
            self.log(f"Errors: {len(self.stats['errors'])}", "ERROR")
            for error in self.stats['errors']:
                self.log(f"  - {error}", "ERROR")
        self.log("="*60, "INFO")
    
    def clean_old_reports(self):
        """Clean old backtest reports"""
        self.log("Cleaning old backtest reports...", "INFO")
        
        report_dir = os.path.join(PROJECT_ROOT, 'reports')
        if not os.path.exists(report_dir):
            return
        
        # Get all report files
        report_files = glob.glob(os.path.join(report_dir, '*.csv'))
        report_files.extend(glob.glob(os.path.join(report_dir, '*.json')))
        
        deleted = 0
        for filepath in report_files:
            age_days = self.get_file_age_days(filepath)
            
            # Delete reports older than max_age_days
            if age_days > self.max_age_days:
                if self.delete_file(filepath):
                    deleted += 1
        
        if deleted > 0:
            self.log(f"Deleted {deleted} old report files", "INFO")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MT5 Bot Log Rotator')
    parser.add_argument('--log-dir', default='logs',
                       help='Log directory path (default: logs)')
    parser.add_argument('--max-age', type=int, default=30,
                       help='Delete logs older than X days (default: 30)')
    parser.add_argument('--compress-age', type=int, default=7,
                       help='Compress logs older than X days (default: 7)')
    parser.add_argument('--max-size', type=int, default=100,
                       help='Compress logs larger than X MB (default: 100)')
    parser.add_argument('--clean-reports', action='store_true',
                       help='Also clean old backtest reports')
    
    args = parser.parse_args()
    
    # Create rotator
    rotator = LogRotator(
        log_dir=args.log_dir,
        max_age_days=args.max_age,
        max_size_mb=args.max_size,
        compress_age_days=args.compress_age
    )
    
    # Run rotation
    rotator.rotate_logs()
    
    # Clean reports if requested
    if args.clean_reports:
        rotator.clean_old_reports()


if __name__ == "__main__":
    main()
