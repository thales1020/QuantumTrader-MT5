"""
Performance Analyzer - Báo cáo và Đánh giá Hiệu suất
====================================================

Module này phân tích và báo cáo hiệu suất của thuật toán giao dịch:
- Tính toán các chỉ số đánh giá quan trọng
- Vẽ đường equity curve
- Phân tích rủi ro (drawdown, volatility)
- Xuất báo cáo Excel chi tiết

Author: QuantumTrader Team
Version: 1.0.0
Date: November 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import logging


@dataclass
class TradeRecord:
    """Bản ghi giao dịch"""
    trade_id: int
    symbol: str
    direction: str                  # LONG/SHORT
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    lot_size: float
    
    # P&L
    gross_pnl: float
    commission: float
    swap: float
    spread_cost: float
    slippage: float
    net_pnl: float
    
    # Additional
    pips: float
    duration_hours: float
    exit_reason: str
    
    # Running totals
    balance_after: float
    equity_after: float
    drawdown_pct: float


@dataclass
class PerformanceMetrics:
    """Chỉ số hiệu suất"""
    
    # === TỔNG QUAN ===
    initial_balance: float
    final_balance: float
    final_equity: float
    total_net_profit: float
    total_return_pct: float
    
    # === GIAO DỊCH ===
    total_trades: int
    winning_trades: int
    losing_trades: int
    break_even_trades: int
    
    # === TỶ LỆ ===
    win_rate: float                     # Tỷ lệ thắng
    loss_rate: float                    # Tỷ lệ thua
    
    # === GIÁ TRỊ KỲ VỌNG ===
    avg_win: float                      # Giá trị kỳ vọng khi thắng
    avg_loss: float                     # Giá trị kỳ vọng khi thua
    largest_win: float
    largest_loss: float
    
    # === PROFIT FACTOR ===
    gross_profit: float
    gross_loss: float
    profit_factor: float                # Gross profit / Gross loss
    
    # === CHUỖI GIAO DỊCH ===
    max_consecutive_wins: int           # Chuỗi thắng dài nhất
    max_consecutive_losses: int         # Chuỗi thua dài nhất
    current_streak: int
    
    # === DRAWDOWN ===
    max_drawdown: float                 # Maximum drawdown (USD)
    max_drawdown_pct: float             # Maximum drawdown (%)
    max_drawdown_duration: int          # Số ngày drawdown
    
    # === SHARPE RATIO ===
    sharpe_ratio: float                 # Tỷ lệ Sharpe (annualized)
    sortino_ratio: float                # Tỷ lệ Sortino
    
    # === CHI PHÍ ===
    total_commission: float
    total_swap: float
    total_spread_cost: float
    total_slippage: float
    total_costs: float
    costs_pct_of_profit: float
    
    # === THỜI GIAN ===
    backtest_start: datetime
    backtest_end: datetime
    backtest_duration_days: int
    avg_trade_duration_hours: float
    
    # === RỦI RO ===
    volatility: float                   # Standard deviation of returns
    var_95: float                       # Value at Risk (95%)
    calmar_ratio: float                 # Return / Max Drawdown


class PerformanceAnalyzer:
    """
    Phân tích hiệu suất giao dịch
    
    Chức năng:
    1. Tính toán các chỉ số đánh giá
    2. Phân tích drawdown
    3. Tính Sharpe ratio
    4. Xuất báo cáo Excel
    5. Vẽ equity curve
    """
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.trade_records: List[TradeRecord] = []
        self.equity_curve: List[Dict] = []
        self.logger = logging.getLogger('PerformanceAnalyzer')
        
    def add_trade(self, trade: TradeRecord):
        """Thêm giao dịch vào phân tích"""
        self.trade_records.append(trade)
        
    def add_equity_point(self, timestamp: datetime, balance: float, equity: float,
                        positions: int = 0, margin_level: float = 0):
        """Thêm điểm vào equity curve"""
        self.equity_curve.append({
            'timestamp': timestamp,
            'balance': balance,
            'equity': equity,
            'positions': positions,
            'margin_level': margin_level
        })
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """
        Tính toán tất cả chỉ số hiệu suất
        """
        if not self.trade_records:
            self.logger.warning("No trades to analyze")
            return self._empty_metrics()
        
        df_trades = pd.DataFrame([asdict(t) for t in self.trade_records])
        
        # === BASIC METRICS ===
        total_trades = len(self.trade_records)
        final_balance = self.trade_records[-1].balance_after
        final_equity = self.trade_records[-1].equity_after
        total_net_profit = final_balance - self.initial_balance
        total_return_pct = (total_net_profit / self.initial_balance) * 100
        
        # === WIN/LOSS ANALYSIS ===
        winning_trades = len(df_trades[df_trades['net_pnl'] > 0])
        losing_trades = len(df_trades[df_trades['net_pnl'] < 0])
        break_even_trades = len(df_trades[df_trades['net_pnl'] == 0])
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        loss_rate = (losing_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # === EXPECTANCY ===
        wins = df_trades[df_trades['net_pnl'] > 0]['net_pnl']
        losses = df_trades[df_trades['net_pnl'] < 0]['net_pnl']
        
        avg_win = wins.mean() if len(wins) > 0 else 0
        avg_loss = losses.mean() if len(losses) > 0 else 0
        largest_win = wins.max() if len(wins) > 0 else 0
        largest_loss = losses.min() if len(losses) > 0 else 0
        
        # === PROFIT FACTOR ===
        gross_profit = wins.sum() if len(wins) > 0 else 0
        gross_loss = abs(losses.sum()) if len(losses) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # === CONSECUTIVE STREAKS ===
        max_consec_wins, max_consec_losses, current_streak = self._calculate_streaks(df_trades)
        
        # === DRAWDOWN ===
        max_dd, max_dd_pct, max_dd_duration = self._calculate_drawdown()
        
        # === SHARPE RATIO ===
        sharpe, sortino = self._calculate_risk_metrics(df_trades)
        
        # === COSTS ===
        total_commission = df_trades['commission'].sum()
        total_swap = df_trades['swap'].sum()
        total_spread = df_trades['spread_cost'].sum()
        total_slip = df_trades['slippage'].sum()
        total_costs = total_commission + total_swap + total_spread + total_slip
        
        costs_pct = (total_costs / gross_profit * 100) if gross_profit > 0 else 0
        
        # === TIME ===
        backtest_start = df_trades['entry_time'].min()
        backtest_end = df_trades['exit_time'].max()
        duration_days = (backtest_end - backtest_start).days
        avg_duration = df_trades['duration_hours'].mean()
        
        # === RISK METRICS ===
        returns = df_trades['net_pnl'] / self.initial_balance
        volatility = returns.std() * np.sqrt(252)  # Annualized
        var_95 = returns.quantile(0.05) * self.initial_balance
        calmar = (total_return_pct / max_dd_pct) if max_dd_pct > 0 else 0
        
        return PerformanceMetrics(
            initial_balance=self.initial_balance,
            final_balance=final_balance,
            final_equity=final_equity,
            total_net_profit=total_net_profit,
            total_return_pct=total_return_pct,
            
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            break_even_trades=break_even_trades,
            
            win_rate=win_rate,
            loss_rate=loss_rate,
            
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            
            max_consecutive_wins=max_consec_wins,
            max_consecutive_losses=max_consec_losses,
            current_streak=current_streak,
            
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd_pct,
            max_drawdown_duration=max_dd_duration,
            
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            
            total_commission=total_commission,
            total_swap=total_swap,
            total_spread_cost=total_spread,
            total_slippage=total_slip,
            total_costs=total_costs,
            costs_pct_of_profit=costs_pct,
            
            backtest_start=backtest_start,
            backtest_end=backtest_end,
            backtest_duration_days=duration_days,
            avg_trade_duration_hours=avg_duration,
            
            volatility=volatility,
            var_95=var_95,
            calmar_ratio=calmar
        )
    
    def _calculate_streaks(self, df: pd.DataFrame) -> Tuple[int, int, int]:
        """Tính chuỗi thắng/thua liên tiếp"""
        results = (df['net_pnl'] > 0).astype(int).tolist()
        
        max_wins = 0
        max_losses = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for result in results:
            if result == 1:  # Win
                current_win_streak += 1
                current_loss_streak = 0
                max_wins = max(max_wins, current_win_streak)
            else:  # Loss
                current_loss_streak += 1
                current_win_streak = 0
                max_losses = max(max_losses, current_loss_streak)
        
        # Current streak
        current_streak = current_win_streak if current_win_streak > 0 else -current_loss_streak
        
        return max_wins, max_losses, current_streak
    
    def _calculate_drawdown(self) -> Tuple[float, float, int]:
        """
        Tính Maximum Drawdown
        """
        if not self.equity_curve:
            return 0.0, 0.0, 0
        
        df_equity = pd.DataFrame(self.equity_curve)
        
        # Running maximum
        df_equity['running_max'] = df_equity['equity'].cummax()
        
        # Drawdown in USD
        df_equity['drawdown'] = df_equity['running_max'] - df_equity['equity']
        
        # Drawdown in %
        df_equity['drawdown_pct'] = (df_equity['drawdown'] / df_equity['running_max']) * 100
        
        max_dd = df_equity['drawdown'].max()
        max_dd_pct = df_equity['drawdown_pct'].max()
        
        # Calculate drawdown duration
        df_equity['is_drawdown'] = df_equity['drawdown'] > 0
        
        # Find longest drawdown period
        drawdown_periods = []
        current_dd_days = 0
        
        for is_dd in df_equity['is_drawdown']:
            if is_dd:
                current_dd_days += 1
            else:
                if current_dd_days > 0:
                    drawdown_periods.append(current_dd_days)
                current_dd_days = 0
        
        max_dd_duration = max(drawdown_periods) if drawdown_periods else 0
        
        return max_dd, max_dd_pct, max_dd_duration
    
    def _calculate_risk_metrics(self, df: pd.DataFrame) -> Tuple[float, float]:
        """Tính Sharpe và Sortino ratios"""
        if len(df) < 2:
            return 0.0, 0.0
        
        # Daily returns
        returns = df['net_pnl'] / self.initial_balance
        
        # Risk-free rate (assume 2% annual)
        risk_free_daily = 0.02 / 252
        
        # Sharpe Ratio
        excess_returns = returns - risk_free_daily
        if excess_returns.std() > 0:
            sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Sortino Ratio (only downside volatility)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
        else:
            sortino = 0.0
        
        return sharpe, sortino
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Return empty metrics when no trades"""
        return PerformanceMetrics(
            initial_balance=self.initial_balance,
            final_balance=self.initial_balance,
            final_equity=self.initial_balance,
            total_net_profit=0,
            total_return_pct=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            break_even_trades=0,
            win_rate=0,
            loss_rate=0,
            avg_win=0,
            avg_loss=0,
            largest_win=0,
            largest_loss=0,
            gross_profit=0,
            gross_loss=0,
            profit_factor=0,
            max_consecutive_wins=0,
            max_consecutive_losses=0,
            current_streak=0,
            max_drawdown=0,
            max_drawdown_pct=0,
            max_drawdown_duration=0,
            sharpe_ratio=0,
            sortino_ratio=0,
            total_commission=0,
            total_swap=0,
            total_spread_cost=0,
            total_slippage=0,
            total_costs=0,
            costs_pct_of_profit=0,
            backtest_start=datetime.now(),
            backtest_end=datetime.now(),
            backtest_duration_days=0,
            avg_trade_duration_hours=0,
            volatility=0,
            var_95=0,
            calmar_ratio=0
        )
    
    def export_to_excel(self, filepath: str, metrics: PerformanceMetrics):
        """
        Xuất báo cáo đầy đủ ra Excel
        
        Sheet 1: Summary - Tóm tắt hiệu suất
        Sheet 2: Trades - Lịch sử giao dịch
        Sheet 3: Equity Curve - Đường vốn
        Sheet 4: Monthly Returns - Lợi nhuận theo tháng
        """
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # === SHEET 1: SUMMARY ===
                summary_data = {
                    'Metric': [],
                    'Value': []
                }
                
                # Overview
                summary_data['Metric'].extend([
                    '=== OVERVIEW ===',
                    'Initial Balance',
                    'Final Balance',
                    'Final Equity',
                    'Total Net Profit',
                    'Total Return %',
                    '',
                    '=== TRADES ===',
                    'Total Trades',
                    'Winning Trades',
                    'Losing Trades',
                    'Break Even Trades',
                    'Win Rate %',
                    'Loss Rate %',
                    '',
                    '=== EXPECTANCY ===',
                    'Average Win',
                    'Average Loss',
                    'Largest Win',
                    'Largest Loss',
                    'Profit Factor',
                    '',
                    '=== STREAKS ===',
                    'Max Consecutive Wins',
                    'Max Consecutive Losses',
                    'Current Streak',
                    '',
                    '=== DRAWDOWN ===',
                    'Max Drawdown (USD)',
                    'Max Drawdown %',
                    'Max DD Duration (days)',
                    '',
                    '=== RISK METRICS ===',
                    'Sharpe Ratio',
                    'Sortino Ratio',
                    'Volatility',
                    'VaR 95%',
                    'Calmar Ratio',
                    '',
                    '=== COSTS ===',
                    'Total Commission',
                    'Total Swap',
                    'Total Spread',
                    'Total Slippage',
                    'Total Costs',
                    'Costs % of Profit',
                    '',
                    '=== TIME ===',
                    'Backtest Start',
                    'Backtest End',
                    'Duration (days)',
                    'Avg Trade Duration (hours)'
                ])
                
                summary_data['Value'].extend([
                    '',
                    f"${metrics.initial_balance:,.2f}",
                    f"${metrics.final_balance:,.2f}",
                    f"${metrics.final_equity:,.2f}",
                    f"${metrics.total_net_profit:,.2f}",
                    f"{metrics.total_return_pct:.2f}%",
                    '',
                    '',
                    metrics.total_trades,
                    metrics.winning_trades,
                    metrics.losing_trades,
                    metrics.break_even_trades,
                    f"{metrics.win_rate:.2f}%",
                    f"{metrics.loss_rate:.2f}%",
                    '',
                    '',
                    f"${metrics.avg_win:,.2f}",
                    f"${metrics.avg_loss:,.2f}",
                    f"${metrics.largest_win:,.2f}",
                    f"${metrics.largest_loss:,.2f}",
                    f"{metrics.profit_factor:.2f}",
                    '',
                    '',
                    metrics.max_consecutive_wins,
                    metrics.max_consecutive_losses,
                    metrics.current_streak,
                    '',
                    '',
                    f"${metrics.max_drawdown:,.2f}",
                    f"{metrics.max_drawdown_pct:.2f}%",
                    metrics.max_drawdown_duration,
                    '',
                    '',
                    f"{metrics.sharpe_ratio:.3f}",
                    f"{metrics.sortino_ratio:.3f}",
                    f"{metrics.volatility:.3f}",
                    f"${metrics.var_95:,.2f}",
                    f"{metrics.calmar_ratio:.3f}",
                    '',
                    '',
                    f"${metrics.total_commission:,.2f}",
                    f"${metrics.total_swap:,.2f}",
                    f"${metrics.total_spread_cost:,.2f}",
                    f"${metrics.total_slippage:,.2f}",
                    f"${metrics.total_costs:,.2f}",
                    f"{metrics.costs_pct_of_profit:.2f}%",
                    '',
                    '',
                    metrics.backtest_start.strftime('%Y-%m-%d %H:%M'),
                    metrics.backtest_end.strftime('%Y-%m-%d %H:%M'),
                    metrics.backtest_duration_days,
                    f"{metrics.avg_trade_duration_hours:.2f}"
                ])
                
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # === SHEET 2: TRADE HISTORY ===
                if self.trade_records:
                    df_trades = pd.DataFrame([asdict(t) for t in self.trade_records])
                    df_trades.to_excel(writer, sheet_name='Trades', index=False)
                
                # === SHEET 3: EQUITY CURVE ===
                if self.equity_curve:
                    df_equity = pd.DataFrame(self.equity_curve)
                    df_equity.to_excel(writer, sheet_name='Equity Curve', index=False)
                
                # === SHEET 4: MONTHLY RETURNS ===
                if self.trade_records:
                    df_trades = pd.DataFrame([asdict(t) for t in self.trade_records])
                    df_trades['month'] = pd.to_datetime(df_trades['exit_time']).dt.to_period('M')
                    monthly = df_trades.groupby('month')['net_pnl'].sum().reset_index()
                    monthly['month'] = monthly['month'].astype(str)
                    monthly.to_excel(writer, sheet_name='Monthly Returns', index=False)
            
            self.logger.info(f"✅ Exported backtest report to: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to export Excel: {e}")
    
    def print_summary(self, metrics: PerformanceMetrics):
        """In báo cáo tóm tắt ra console"""
        print("\n" + "="*70)
        print("BACKTEST PERFORMANCE SUMMARY")
        print("="*70)
        
        print("\n📊 OVERVIEW")
        print(f"  Initial Balance:        ${metrics.initial_balance:,.2f}")
        print(f"  Final Balance:          ${metrics.final_balance:,.2f}")
        print(f"  Total Net Profit:       ${metrics.total_net_profit:,.2f}")
        print(f"  Total Return:           {metrics.total_return_pct:.2f}%")
        
        print("\n📈 TRADES")
        print(f"  Total Trades:           {metrics.total_trades}")
        print(f"  Winning Trades:         {metrics.winning_trades} ({metrics.win_rate:.1f}%)")
        print(f"  Losing Trades:          {metrics.losing_trades} ({metrics.loss_rate:.1f}%)")
        
        print("\n💰 EXPECTANCY")
        print(f"  Average Win:            ${metrics.avg_win:,.2f}")
        print(f"  Average Loss:           ${metrics.avg_loss:,.2f}")
        print(f"  Profit Factor:          {metrics.profit_factor:.2f}")
        
        print("\n📉 RISK")
        print(f"  Max Drawdown:           ${metrics.max_drawdown:,.2f} ({metrics.max_drawdown_pct:.2f}%)")
        print(f"  Sharpe Ratio:           {metrics.sharpe_ratio:.3f}")
        print(f"  Sortino Ratio:          {metrics.sortino_ratio:.3f}")
        
        print("\n💸 COSTS")
        print(f"  Total Costs:            ${metrics.total_costs:,.2f}")
        print(f"    - Commission:         ${metrics.total_commission:,.2f}")
        print(f"    - Swap:               ${metrics.total_swap:,.2f}")
        print(f"    - Spread:             ${metrics.total_spread_cost:,.2f}")
        print(f"    - Slippage:           ${metrics.total_slippage:,.2f}")
        print(f"  Costs % of Profit:      {metrics.costs_pct_of_profit:.2f}%")
        
        print("\n" + "="*70 + "\n")
