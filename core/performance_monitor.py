import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

class PerformanceMonitor:
    def __init__(self, trade_history_file='trades.json'):
        self.trade_file = trade_history_file
        self.trades = self.load_trades()
        
    def load_trades(self):
        try:
            with open(self.trade_file, 'r') as f:
                return json.load(f)
        except:
            return []
            
    def generate_report(self, days=30):
        df = pd.DataFrame(self.trades)
        if df.empty:
            print("No trades to analyze")
            return
            
        df['entry_time'] = pd.to_datetime(df['entry_time'])
        df['exit_time'] = pd.to_datetime(df['exit_time'])
        df['duration'] = (df['exit_time'] - df['entry_time']).dt.total_seconds() / 3600
        df['profit_pips'] = df['profit'] / df['volume'] / 10
        
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[df['entry_time'] > cutoff_date]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Equity Curve
        df['cumulative_profit'] = df['profit'].cumsum()
        axes[0, 0].plot(df['exit_time'], df['cumulative_profit'])
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_xlabel('Date')
        axes[0, 0].set_ylabel('Cumulative Profit ($)')
        
        # Win Rate by Hour
        df['hour'] = df['entry_time'].dt.hour
        hourly_stats = df.groupby('hour').agg({
            'profit': lambda x: (x > 0).mean() * 100
        })
        axes[0, 1].bar(hourly_stats.index, hourly_stats['profit'])
        axes[0, 1].set_title('Win Rate by Hour')
        axes[0, 1].set_xlabel('Hour of Day')
        axes[0, 1].set_ylabel('Win Rate (%)')
        
        # Profit Distribution
        axes[1, 0].hist(df['profit_pips'], bins=30, alpha=0.7)
        axes[1, 0].axvline(x=0, color='red', linestyle='--')
        axes[1, 0].set_title('Profit Distribution (Pips)')
        axes[1, 0].set_xlabel('Profit (Pips)')
        axes[1, 0].set_ylabel('Frequency')
        
        # Trade Duration vs Profit
        axes[1, 1].scatter(df['duration'], df['profit_pips'], 
                          c=df['profit'] > 0, cmap='RdYlGn', alpha=0.6)
        axes[1, 1].set_title('Trade Duration vs Profit')
        axes[1, 1].set_xlabel('Duration (Hours)')
        axes[1, 1].set_ylabel('Profit (Pips)')
        
        plt.tight_layout()
        plt.savefig(f'performance_report_{datetime.now().strftime("%Y%m%d")}.png')
        plt.show()
        
        # Statistics
        total_trades = len(df)
        winning_trades = len(df[df['profit'] > 0])
        losing_trades = len(df[df['profit'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_profit = df[df['profit'] > 0]['profit'].sum()
        total_loss = abs(df[df['profit'] < 0]['profit'].sum())
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        avg_win = df[df['profit'] > 0]['profit_pips'].mean()
        avg_loss = abs(df[df['profit'] < 0]['profit_pips'].mean())
        
        max_consecutive_wins = self.max_consecutive(df['profit'] > 0)
        max_consecutive_losses = self.max_consecutive(df['profit'] < 0)
        
        print(f"\n{'='*50}")
        print(f"Performance Report - Last {days} Days")
        print(f"{'='*50}")
        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Average Win: {avg_win:.1f} pips")
        print(f"Average Loss: {avg_loss:.1f} pips")
        print(f"Risk/Reward Ratio: 1:{avg_win/avg_loss:.2f}")
        print(f"Max Consecutive Wins: {max_consecutive_wins}")
        print(f"Max Consecutive Losses: {max_consecutive_losses}")
        print(f"Total Net Profit: ${df['profit'].sum():.2f}")
        print(f"{'='*50}")
        
    @staticmethod
    def max_consecutive(series):
        max_count = 0
        current_count = 0
        for value in series:
            if value:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        return max_count