"""
Risk Manager Module (Educational Example)
==========================================

This module demonstrates advanced risk management techniques for Forex trading:
- Daily loss limits
- Correlation checks between currency pairs
- Kelly Criterion position sizing

Status: EXAMPLE ONLY - Not integrated with production bots
Note: Production bots have built-in risk management in their core logic

Author: ML-SuperTrend-MT5 Project
"""

from datetime import datetime

class RiskManager:
    def __init__(self, max_daily_loss_percent=5.0, max_correlation=0.7):
        """
        Initialize risk manager
        
        Args:
            max_daily_loss_percent: Maximum allowed daily loss as percentage (default 5%)
            max_correlation: Maximum correlation threshold (0-1, default 0.7)
        """
        self.max_daily_loss_percent = max_daily_loss_percent
        self.max_correlation = max_correlation
        self.daily_trades = []
        self.last_reset = datetime.now().date()
        
    def check_daily_loss_limit(self, account_balance):
        """
        Check if daily loss limit has been reached
        
        Args:
            account_balance: Current account balance
            
        Returns:
            bool: True if can continue trading, False if limit reached
        """
        # Reset daily trades at start of new day
        if datetime.now().date() > self.last_reset:
            self.daily_trades = []
            self.last_reset = datetime.now().date()
            
        # Calculate total daily loss
        daily_loss = sum(t['profit'] for t in self.daily_trades if t['profit'] < 0)
        max_allowed_loss = account_balance * (self.max_daily_loss_percent / 100)
        
        return abs(daily_loss) < max_allowed_loss
        
    def check_correlation(self, symbols_in_trade):
        """
        Check if symbols have high correlation
        Prevents over-exposure to same market direction
        
        Args:
            symbols_in_trade: List of symbols currently in positions
            
        Returns:
            bool: True if correlation is acceptable, False if too high
        """
        # Simplified correlation mapping
        # In production, use actual correlation coefficients
        correlated_pairs = {
            'EURUSD': ['GBPUSD', 'EURGBP'],
            'GBPUSD': ['EURUSD', 'EURGBP'],
            'USDJPY': ['EURJPY', 'GBPJPY'],
            'AUDUSD': ['NZDUSD'],
            'NZDUSD': ['AUDUSD']
        }
        
        # Check each symbol against others
        for symbol in symbols_in_trade:
            if symbol in correlated_pairs:
                for corr_symbol in correlated_pairs[symbol]:
                    if corr_symbol in symbols_in_trade:
                        return False  # High correlation detected
        return True  # Correlation acceptable
        
    def calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        """
        Calculate optimal position size using Kelly Criterion
        
        Formula: Kelly% = (p*b - q) / b
        where:
        - p = probability of win (win_rate / 100)
        - q = probability of loss (1 - p)
        - b = ratio of win to loss (avg_win / avg_loss)
        
        Args:
            win_rate: Win rate percentage (0-100)
            avg_win: Average win amount
            avg_loss: Average loss amount
            
        Returns:
            float: Recommended risk percentage (fractional Kelly for safety)
        """
        if avg_loss == 0:
            return 0.01  # Minimum risk
        
        # Calculate Kelly percentage
        b = avg_win / avg_loss  # Win/loss ratio
        p = win_rate / 100      # Win probability
        q = 1 - p               # Loss probability
        
        kelly = (p * b - q) / b
        
        # Use fractional Kelly (25%) for safety
        # Full Kelly can be too aggressive
        fractional_kelly = kelly * 0.25
        
        # Clamp between 1% and 2% for safety
        return max(0.01, min(fractional_kelly, 0.02))


# Example Usage
if __name__ == "__main__":
    print("Risk Manager Example")
    print("=" * 50)
    
    # Initialize risk manager
    risk_manager = RiskManager(
        max_daily_loss_percent=3.0,  # 3% max daily loss
        max_correlation=0.7
    )
    
    # Example 1: Check daily loss limit
    print("\n1. Daily Loss Limit Check")
    account_balance = 10000
    if risk_manager.check_daily_loss_limit(account_balance):
        print(" Daily loss limit OK - Can continue trading")
    else:
        print("⛔ Daily loss limit reached - Stop trading for today")
    
    # Example 2: Check correlation
    print("\n2. Correlation Check")
    symbols_in_trade = ['EURUSD', 'GBPUSD']  # Highly correlated
    if risk_manager.check_correlation(symbols_in_trade):
        print(" Correlation acceptable")
    else:
        print("  High correlation detected - Avoid new position")
    
    # Example 3: Kelly Criterion
    print("\n3. Kelly Criterion Position Sizing")
    win_rate = 55    # 55% win rate
    avg_win = 50     # Average win: 50 pips
    avg_loss = 30    # Average loss: 30 pips
    
    kelly_percent = risk_manager.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    print(f"Win Rate: {win_rate}%")
    print(f"Avg Win: {avg_win} pips")
    print(f"Avg Loss: {avg_loss} pips")
    print(f"Recommended Risk: {kelly_percent*100:.2f}% per trade")
    print(f"Position Size: ${account_balance * kelly_percent:.2f}")
