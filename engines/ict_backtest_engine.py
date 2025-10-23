import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple

class ICTBacktestEngine:
    def __init__(self, bot, initial_balance=10000):
        """
        Initialize ICT backtest engine
        Args:
            bot: ICTBot instance
            initial_balance: Starting balance for backtest
        """
        self.bot = bot
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.trades = []
        self.open_position = None
        self.logger = logging.getLogger('ICTBacktestEngine')
        
    def run_backtest(self, symbol: str, start_date: datetime, end_date: datetime, timeframe: int):
        """
        Run backtest on historical data
        """
        self.logger.info("="*60)
        self.logger.info("STARTING ICT BACKTEST")
        self.logger.info("="*60)
        self.logger.info(f"Symbol: {symbol}")
        self.logger.info(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        self.logger.info(f"Initial Balance: ${self.initial_balance:,.2f}")
        
        # Load historical data
        rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
        
        if rates is None or len(rates) == 0:
            self.logger.error(f"No historical data available for {symbol}")
            self.logger.error(f"Error: {mt5.last_error()}")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        self.logger.info(f"Loaded {len(df)} bars")
        self.logger.info("Processing ICT strategy...")
        
        # Pre-process: Set index once for better performance
        df_indexed = df.set_index('time')
        
        equity_curve = []
        
        # Progress tracking
        total_bars = len(df) - 100
        last_progress_report = 0
        
        # Optimize: Only record equity periodically (every 100 bars) instead of every bar
        equity_record_interval = 100
        
        # Optimize: Reduce progress logging to 20% intervals for better performance
        progress_report_interval = 20
        
        # Simulate trading bar by bar
        for i in range(100, len(df)):  # Start after warmup period
            current_bar = df.iloc[i]
            current_time = current_bar['time']
            
            # Progress report every 20%
            progress = ((i - 100) / total_bars) * 100
            if progress - last_progress_report >= progress_report_interval:
                self.logger.info(f"Progress: {progress:.0f}% ({i}/{len(df)} bars) | Trades: {len(self.trades)} | Balance: ${self.balance:,.2f}")
                last_progress_report = progress
            
            # Update existing position if any
            if self.open_position:
                self._update_position(current_bar, i)
            
            # Check for new signals if no open position
            if not self.open_position:
                # Optimize: Only pass last N bars instead of entire history
                # ICT analysis typically uses last 200-500 bars
                lookback = min(500, i)
                current_df = df_indexed.iloc[i-lookback:i+1].copy()
                
                signal = self.bot.generate_signal(current_df)
                if signal:
                    self._open_position(signal, current_bar, i)
            
            # Record equity periodically or on trade events
            if i % equity_record_interval == 0 or self.open_position:
                current_equity = self._calculate_equity(current_bar)
                equity_curve.append({
                    'time': current_time,
                    'equity': current_equity,
                    'balance': self.balance
                })
        
        # Close any remaining position
        if self.open_position:
            self._close_position(df.iloc[-1], len(df)-1, "End of backtest")
        
        # Generate report
        return self._generate_report(equity_curve, df)
    
    def _open_position(self, signal: Dict, bar: pd.Series, bar_index: int):
        """Open a new position"""
        entry_price = signal['price']
        atr = signal['atr']
        
        # Calculate SL and TP based on order block or ATR
        if signal['type'] == 'BUY':
            if signal.get('order_block'):
                sl = signal['order_block'].price_low * 0.999  # Below OB
            else:
                sl = entry_price - (atr * 1.5)
            
            tp = entry_price + (abs(entry_price - sl) * self.bot.config.rr_ratio)
            direction = 1
        else:  # SELL
            if signal.get('order_block'):
                sl = signal['order_block'].price_high * 1.001  # Above OB
            else:
                sl = entry_price + (atr * 1.5)
            
            tp = entry_price - (abs(entry_price - sl) * self.bot.config.rr_ratio)
            direction = -1
        
        # Calculate position size based on risk
        risk_amount = self.balance * (self.bot.config.risk_percent / 100)
        sl_distance = abs(entry_price - sl)
        
        # Get symbol info for accurate calculation
        symbol_info = mt5.symbol_info(self.bot.config.symbol)
        
        if symbol_info is None:
            # Fallback to manual calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                # Gold: 1 lot = 100 oz, 1 pip = $0.01, so 1 pip movement = 100 oz × $0.01 = $1
                tick_size = 0.01
                tick_value = 1.0  # $1 per tick for 1 lot
            elif 'JPY' in self.bot.config.symbol:
                tick_size = 0.01
                tick_value = 10.0
            else:
                tick_size = 0.0001
                tick_value = 10.0
        else:
            # Use actual MT5 symbol info (most accurate)
            tick_size = symbol_info.trade_tick_size
            tick_value = symbol_info.trade_tick_value
        
        # Calculate lot size
        ticks_at_risk = sl_distance / tick_size
        
        if ticks_at_risk == 0:
            lot_size = 0.01
        else:
            # This ensures: actual_risk = lot_size × ticks_at_risk × tick_value = risk_amount
            lot_size = risk_amount / (ticks_at_risk * tick_value)
        
        # Round and limit
        if symbol_info:
            volume_step = symbol_info.volume_step
            lot_size = round(lot_size / volume_step) * volume_step
            lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        else:
            lot_size = round(lot_size, 2)
            lot_size = max(0.01, min(lot_size, 10.0))
        
        # Calculate actual risk for logging
        actual_risk = lot_size * ticks_at_risk * tick_value
        
        self.open_position = {
            'type': signal['type'],
            'entry_price': entry_price,
            'entry_time': signal['time'],
            'entry_bar': bar_index,
            'sl': sl,
            'tp': tp,
            'lot_size': lot_size,
            'direction': direction,
            'conditions': signal.get('conditions', 0),
            'has_ob': signal.get('order_block') is not None
        }
        
        # Log with bar timestamp
        bar_time = signal['time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(signal['time'], pd.Timestamp) else signal['time']
        self.logger.info(f"[{bar_time}] [OPEN] {signal['type']} at {entry_price:.5f}, SL: {sl:.5f}, TP: {tp:.5f}, Size: {lot_size}")
        self.logger.info(f"[RISK] Balance: ${self.balance:.2f}, Target Risk: ${risk_amount:.2f} ({self.bot.config.risk_percent}%), Actual Risk: ${actual_risk:.2f}, SL Distance: {sl_distance:.5f}")
    
    def _update_position(self, bar: pd.Series, bar_index: int):
        """Update open position - check for SL/TP hit"""
        if not self.open_position:
            return
        
        pos = self.open_position
        high = bar['high']
        low = bar['low']
        
        # Check SL/TP
        if pos['type'] == 'BUY':
            if low <= pos['sl']:
                self._close_position_at_price(pos['sl'], bar['time'], bar_index, "Stop Loss")
            elif high >= pos['tp']:
                self._close_position_at_price(pos['tp'], bar['time'], bar_index, "Take Profit")
        else:  # SELL
            if high >= pos['sl']:
                self._close_position_at_price(pos['sl'], bar['time'], bar_index, "Stop Loss")
            elif low <= pos['tp']:
                self._close_position_at_price(pos['tp'], bar['time'], bar_index, "Take Profit")
    
    def _close_position(self, bar: pd.Series, bar_index: int, reason: str):
        """Close position at current bar close"""
        self._close_position_at_price(bar['close'], bar['time'], bar_index, reason)
    
    def _close_position_at_price(self, exit_price: float, exit_time, bar_index: int, reason: str):
        """Close position at specific price"""
        if not self.open_position:
            return
        
        pos = self.open_position
        
        # Calculate P&L with proper pip calculation for different symbols
        price_diff = (exit_price - pos['entry_price']) * pos['direction']
        
        # Get symbol info for accurate calculation
        symbol_info = mt5.symbol_info(self.bot.config.symbol)
        
        if symbol_info is None:
            # Fallback to manual calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                tick_size = 0.01
                tick_value = 1.0  # $1 per tick for 1 lot
            elif 'JPY' in self.bot.config.symbol:
                tick_size = 0.01
                tick_value = 10.0
            else:
                tick_size = 0.0001
                tick_value = 10.0
        else:
            tick_size = symbol_info.trade_tick_size
            tick_value = symbol_info.trade_tick_value
        
        # Calculate profit in ticks and then in dollars
        ticks = price_diff / tick_size
        profit = ticks * tick_value * pos['lot_size']
        
        self.balance += profit
        
        # Record trade
        trade = {
            'entry_time': pos['entry_time'],
            'exit_time': exit_time,
            'type': pos['type'],
            'entry_price': pos['entry_price'],
            'exit_price': exit_price,
            'sl': pos['sl'],
            'tp': pos['tp'],
            'lot_size': pos['lot_size'],
            'pips': ticks,  # Store as ticks (equivalent to pips in display)
            'profit': profit,
            'balance': self.balance,
            'reason': reason,
            'bars_held': bar_index - pos['entry_bar'],
            'conditions': pos.get('conditions', 0),
            'has_order_block': pos.get('has_ob', False)
        }
        
        self.trades.append(trade)
        
        # Log with bar timestamp and balance
        exit_time_str = exit_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(exit_time, pd.Timestamp) else exit_time
        self.logger.info(f"[{exit_time_str}] [CLOSE] {pos['type']} at {exit_price:.5f}, P&L: ${profit:.2f} ({ticks:.1f} pips) - {reason} | Balance: ${self.balance:,.2f}")
        
        self.open_position = None
    
    def _calculate_equity(self, bar: pd.Series) -> float:
        """Calculate current equity including unrealized P&L"""
        if not self.open_position:
            return self.balance
        
        pos = self.open_position
        current_price = bar['close']
        
        # Calculate unrealized P&L with proper calculation
        price_diff = (current_price - pos['entry_price']) * pos['direction']
        
        # Get symbol info for accurate calculation
        symbol_info = mt5.symbol_info(self.bot.config.symbol)
        
        if symbol_info is None:
            # Fallback to manual calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                tick_size = 0.01
                tick_value = 1.0  # $1 per tick for 1 lot
            elif 'JPY' in self.bot.config.symbol:
                tick_size = 0.01
                tick_value = 10.0
            else:
                tick_size = 0.0001
                tick_value = 10.0
        else:
            tick_size = symbol_info.trade_tick_size
            tick_value = symbol_info.trade_tick_value
        
        ticks = price_diff / tick_size
        unrealized_profit = ticks * tick_value * pos['lot_size']
        
        return self.balance + unrealized_profit
    
    def _generate_report(self, equity_curve: List[Dict], df: pd.DataFrame) -> Dict:
        """Generate comprehensive backtest report"""
        self.logger.info("="*60)
        self.logger.info("ICT BACKTEST RESULTS")
        self.logger.info("="*60)
        
        if not self.trades:
            self.logger.info("No trades executed during backtest period")
            return None
        
        # Calculate statistics
        trades_df = pd.DataFrame(self.trades)
        
        total_trades = len(self.trades)
        winning_trades = len(trades_df[trades_df['profit'] > 0])
        losing_trades = len(trades_df[trades_df['profit'] < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_profit = trades_df['profit'].sum()
        gross_profit = trades_df[trades_df['profit'] > 0]['profit'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[trades_df['profit'] < 0]['profit'].sum()) if losing_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        avg_win = trades_df[trades_df['profit'] > 0]['profit'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['profit'] < 0]['profit'].mean() if losing_trades > 0 else 0
        
        # Calculate max drawdown
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Calculate Sharpe ratio
        equity_pct_change = equity_series.pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * equity_pct_change.mean() / equity_pct_change.std() if len(equity_pct_change) > 0 and equity_pct_change.std() > 0 else 0
        
        # ICT-specific stats
        ob_trades = len(trades_df[trades_df['has_order_block'] == True])
        avg_conditions = trades_df['conditions'].mean()
        
        # Print results
        self.logger.info(f"Total Trades: {total_trades}")
        self.logger.info(f"Winning Trades: {winning_trades}")
        self.logger.info(f"Losing Trades: {losing_trades}")
        self.logger.info(f"Win Rate: {win_rate:.2f}%")
        self.logger.info(f"")
        self.logger.info(f"Initial Balance: ${self.initial_balance:,.2f}")
        self.logger.info(f"Final Balance: ${self.balance:,.2f}")
        self.logger.info(f"Net Profit: ${total_profit:,.2f} ({(total_profit/self.initial_balance*100):.2f}%)")
        self.logger.info(f"")
        self.logger.info(f"Gross Profit: ${gross_profit:,.2f}")
        self.logger.info(f"Gross Loss: ${gross_loss:,.2f}")
        self.logger.info(f"Profit Factor: {profit_factor:.2f}")
        self.logger.info(f"")
        self.logger.info(f"Average Win: ${avg_win:.2f}")
        self.logger.info(f"Average Loss: ${avg_loss:.2f}")
        self.logger.info(f"Avg Win/Loss Ratio: {abs(avg_win/avg_loss):.2f}" if avg_loss != 0 else "N/A")
        self.logger.info(f"")
        self.logger.info(f"Max Drawdown: {max_drawdown:.2f}%")
        self.logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        self.logger.info(f"")
        self.logger.info("ICT STRATEGY METRICS:")
        self.logger.info(f"Trades with Order Block: {ob_trades}/{total_trades} ({ob_trades/total_trades*100:.1f}%)")
        self.logger.info(f"Average Conditions per Trade: {avg_conditions:.1f}/4")
        self.logger.info("="*60)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'net_profit': total_profit,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trades_with_ob': ob_trades,
            'avg_conditions': avg_conditions,
            'trades': self.trades,
            'equity_curve': equity_curve
        }
