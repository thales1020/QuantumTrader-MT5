"""
Advanced Risk Manager Plugin Example

This plugin demonstrates advanced risk management techniques including:
- Dynamic position sizing based on volatility
- Maximum daily loss limits
- Correlation-based exposure limits
- Time-based risk adjustments (avoid high-risk hours)
- Equity curve-based risk scaling

Hook Usage:
- before_trade: Validate risk before opening position
- after_trade: Update risk metrics after trade
- on_position_close: Recalculate available risk
- daily_start: Reset daily risk counters

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

from core.plugin_system import BasePlugin
from typing import Dict, Optional
from datetime import datetime, time
import logging


class AdvancedRiskManager(BasePlugin):
    """
    Advanced Risk Manager Plugin
    
    Features:
    - Daily loss limits (stop trading when limit hit)
    - Volatility-adjusted position sizing
    - Maximum drawdown protection
    - Time-based risk filters
    - Winning/losing streak adjustments
    
    Configuration:
        {
            'max_daily_loss_percent': 2.0,  # Stop trading at 2% daily loss
            'max_drawdown_percent': 10.0,   # Max drawdown from peak
            'volatility_multiplier': 1.5,   # Adjust size by volatility
            'avoid_news_hours': True,       # Reduce risk during news
            'scale_on_streak': True,        # Adjust size based on streak
            'max_correlated_exposure': 5.0  # Max exposure to correlated pairs
        }
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Risk limits
        self.max_daily_loss_percent = config.get('max_daily_loss_percent', 2.0)
        self.max_drawdown_percent = config.get('max_drawdown_percent', 10.0)
        self.max_correlated_exposure = config.get('max_correlated_exposure', 5.0)
        
        # Risk adjustments
        self.volatility_multiplier = config.get('volatility_multiplier', 1.5)
        self.avoid_news_hours = config.get('avoid_news_hours', True)
        self.scale_on_streak = config.get('scale_on_streak', True)
        
        # Tracking
        self.daily_pnl = 0.0
        self.peak_equity = 0.0
        self.current_equity = 0.0
        self.winning_streak = 0
        self.losing_streak = 0
        self.trades_today = 0
        self.last_reset_date = None
        
        # High-risk hours (major news events typically)
        self.high_risk_hours = [
            (time(8, 30), time(9, 30)),   # London open
            (time(13, 30), time(14, 30)), # US open
        ]
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Advanced Risk Manager initialized")
        self.logger.info(f"Daily loss limit: {self.max_daily_loss_percent}%")
        self.logger.info(f"Max drawdown: {self.max_drawdown_percent}%")
    
    def get_name(self) -> str:
        return "AdvancedRiskManager"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def reset_daily_metrics(self):
        """Reset daily tracking metrics"""
        today = datetime.now().date()
        
        if self.last_reset_date != today:
            self.logger.info(f"Resetting daily metrics for {today}")
            self.daily_pnl = 0.0
            self.trades_today = 0
            self.last_reset_date = today
    
    def is_high_risk_hour(self) -> bool:
        """Check if current time is in high-risk period"""
        if not self.avoid_news_hours:
            return False
        
        current_time = datetime.now().time()
        
        for start, end in self.high_risk_hours:
            if start <= current_time <= end:
                return True
        
        return False
    
    def calculate_volatility_adjustment(self, context: Dict) -> float:
        """
        Calculate position size adjustment based on volatility
        
        Args:
            context: Trade context with ATR and price data
            
        Returns:
            Multiplier for position size (0.5 to 1.5)
        """
        # Get current volatility (ATR as percentage of price)
        atr = context.get('atr', 0)
        price = context.get('price', 1)
        
        if atr == 0 or price == 0:
            return 1.0
        
        volatility_pct = (atr / price) * 100
        
        # Normal volatility: 0.5-1.5%
        # Low volatility (< 0.5%): Increase size
        # High volatility (> 1.5%): Decrease size
        
        if volatility_pct < 0.5:
            adjustment = 1.2  # Increase by 20%
        elif volatility_pct > 1.5:
            adjustment = 0.7  # Decrease by 30%
        else:
            adjustment = 1.0  # Normal
        
        return adjustment
    
    def calculate_streak_adjustment(self) -> float:
        """
        Adjust position size based on winning/losing streak
        
        Returns:
            Multiplier for position size
        """
        if not self.scale_on_streak:
            return 1.0
        
        # Winning streak: Gradually increase size (max 1.5x)
        if self.winning_streak > 0:
            adjustment = min(1.5, 1.0 + (self.winning_streak * 0.1))
            return adjustment
        
        # Losing streak: Decrease size (min 0.5x)
        if self.losing_streak > 0:
            adjustment = max(0.5, 1.0 - (self.losing_streak * 0.1))
            return adjustment
        
        return 1.0
    
    def check_daily_loss_limit(self) -> bool:
        """
        Check if daily loss limit has been exceeded
        
        Returns:
            True if trading should stop
        """
        if self.current_equity == 0:
            return False
        
        daily_loss_pct = (self.daily_pnl / self.current_equity) * 100
        
        if daily_loss_pct <= -self.max_daily_loss_percent:
            self.logger.warning(
                f"Daily loss limit hit: {daily_loss_pct:.2f}% "
                f"(limit: {self.max_daily_loss_percent}%)"
            )
            return True
        
        return False
    
    def check_max_drawdown(self) -> bool:
        """
        Check if maximum drawdown has been exceeded
        
        Returns:
            True if trading should stop
        """
        if self.peak_equity == 0 or self.current_equity == 0:
            return False
        
        # Update peak if current is higher
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity
        
        # Calculate drawdown from peak
        drawdown_pct = ((self.peak_equity - self.current_equity) / self.peak_equity) * 100
        
        if drawdown_pct >= self.max_drawdown_percent:
            self.logger.warning(
                f"Max drawdown exceeded: {drawdown_pct:.2f}% "
                f"(limit: {self.max_drawdown_percent}%)"
            )
            return True
        
        return False
    
    def validate_trade_risk(self, context: Dict) -> Dict:
        """
        Validate if trade meets risk requirements
        
        Args:
            context: Trade context from before_trade hook
            
        Returns:
            Dict with 'approved' boolean and optional 'reason' for rejection
        """
        # Reset daily metrics if needed
        self.reset_daily_metrics()
        
        # Check 1: Daily loss limit
        if self.check_daily_loss_limit():
            return {
                'approved': False,
                'reason': f'Daily loss limit hit ({self.max_daily_loss_percent}%)',
                'original_size': context.get('position_size', 0),
                'adjusted_size': 0
            }
        
        # Check 2: Maximum drawdown
        if self.check_max_drawdown():
            return {
                'approved': False,
                'reason': f'Max drawdown exceeded ({self.max_drawdown_percent}%)',
                'original_size': context.get('position_size', 0),
                'adjusted_size': 0
            }
        
        # Check 3: High-risk hours
        if self.is_high_risk_hour():
            self.logger.info("High-risk hour detected - reducing position size by 50%")
            original_size = context.get('position_size', 0)
            adjusted_size = original_size * 0.5
            
            return {
                'approved': True,
                'reason': 'High-risk hour - size reduced',
                'original_size': original_size,
                'adjusted_size': adjusted_size
            }
        
        # Calculate adjustments
        original_size = context.get('position_size', 0)
        
        # Volatility adjustment
        vol_adj = self.calculate_volatility_adjustment(context)
        
        # Streak adjustment
        streak_adj = self.calculate_streak_adjustment()
        
        # Combined adjustment
        total_adjustment = vol_adj * streak_adj
        adjusted_size = original_size * total_adjustment
        
        self.logger.info(
            f"Position size adjusted: {original_size:.2f} → {adjusted_size:.2f} "
            f"(Vol: {vol_adj:.2f}x, Streak: {streak_adj:.2f}x)"
        )
        
        return {
            'approved': True,
            'original_size': original_size,
            'adjusted_size': adjusted_size,
            'volatility_adjustment': vol_adj,
            'streak_adjustment': streak_adj
        }
    
    def update_metrics_after_trade(self, context: Dict):
        """Update tracking metrics after trade opens"""
        self.trades_today += 1
        
        # Update equity tracking
        self.current_equity = context.get('account_balance', self.current_equity)
        
        if self.peak_equity == 0:
            self.peak_equity = self.current_equity
    
    def update_streak(self, profit: float):
        """Update winning/losing streak"""
        if profit > 0:
            self.winning_streak += 1
            self.losing_streak = 0
            self.logger.info(f"Winning streak: {self.winning_streak}")
        elif profit < 0:
            self.losing_streak += 1
            self.winning_streak = 0
            self.logger.info(f"Losing streak: {self.losing_streak}")
    
    def on_position_close(self, context: Dict):
        """Hook: Called when position closes"""
        profit = context.get('profit', 0)
        
        # Update daily P&L
        self.daily_pnl += profit
        
        # Update equity
        self.current_equity = context.get('account_balance', self.current_equity)
        
        # Update streak
        self.update_streak(profit)
        
        self.logger.info(
            f"Position closed. Profit: ${profit:.2f}, "
            f"Daily P&L: ${self.daily_pnl:.2f}, "
            f"Trades today: {self.trades_today}"
        )
    
    def before_trade(self, context: Dict) -> Dict:
        """Hook: Validate trade before execution"""
        self.logger.info("Validating trade risk...")
        
        result = self.validate_trade_risk(context)
        
        # Update context with adjusted size if approved
        if result['approved'] and result.get('adjusted_size'):
            context['position_size'] = result['adjusted_size']
        
        return context
    
    def after_trade(self, context: Dict) -> Dict:
        """Hook: Update metrics after trade"""
        self.update_metrics_after_trade(context)
        return context
    
    def daily_start(self, context: Dict) -> Dict:
        """Hook: Called at start of trading day"""
        self.reset_daily_metrics()
        
        self.logger.info("=" * 60)
        self.logger.info("NEW TRADING DAY")
        self.logger.info(f"Account Equity: ${self.current_equity:.2f}")
        self.logger.info(f"Peak Equity: ${self.peak_equity:.2f}")
        self.logger.info(f"Daily Loss Limit: {self.max_daily_loss_percent}%")
        self.logger.info("=" * 60)
        
        return context
    
    def get_status(self) -> Dict:
        """Get current risk manager status"""
        if self.current_equity > 0:
            daily_pnl_pct = (self.daily_pnl / self.current_equity) * 100
        else:
            daily_pnl_pct = 0
        
        if self.peak_equity > 0 and self.current_equity > 0:
            drawdown_pct = ((self.peak_equity - self.current_equity) / self.peak_equity) * 100
        else:
            drawdown_pct = 0
        
        return {
            'daily_pnl': self.daily_pnl,
            'daily_pnl_percent': daily_pnl_pct,
            'trades_today': self.trades_today,
            'current_equity': self.current_equity,
            'peak_equity': self.peak_equity,
            'drawdown_percent': drawdown_pct,
            'winning_streak': self.winning_streak,
            'losing_streak': self.losing_streak,
            'daily_limit_hit': self.check_daily_loss_limit(),
            'drawdown_limit_hit': self.check_max_drawdown(),
        }


# Example usage
if __name__ == '__main__':
    # Configuration
    config = {
        'max_daily_loss_percent': 2.0,
        'max_drawdown_percent': 10.0,
        'volatility_multiplier': 1.5,
        'avoid_news_hours': True,
        'scale_on_streak': True,
        'max_correlated_exposure': 5.0,
    }
    
    # Initialize plugin
    risk_manager = AdvancedRiskManager(config)
    
    print("\n" + "=" * 60)
    print(f"Plugin: {risk_manager.get_name()} v{risk_manager.get_version()}")
    print("=" * 60)
    
    # Simulate daily start
    risk_manager.daily_start({'account_balance': 10000})
    risk_manager.current_equity = 10000
    risk_manager.peak_equity = 10000
    
    # Simulate trade validation
    trade_context = {
        'symbol': 'EURUSD',
        'position_size': 0.1,
        'atr': 0.0015,
        'price': 1.1000,
        'account_balance': 10000,
    }
    
    print("\nValidating trade...")
    result = risk_manager.validate_trade_risk(trade_context)
    
    print(f"\nTrade Approval: {'✅ APPROVED' if result['approved'] else '❌ REJECTED'}")
    if result.get('reason'):
        print(f"Reason: {result['reason']}")
    print(f"Original Size: {result['original_size']:.2f} lots")
    print(f"Adjusted Size: {result['adjusted_size']:.2f} lots")
    
    # Get status
    print("\nRisk Manager Status:")
    print("-" * 60)
    status = risk_manager.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("=" * 60 + "\n")
