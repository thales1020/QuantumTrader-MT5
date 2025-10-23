import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Tuple

class BacktestEngine:
    def __init__(self, bot, initial_balance=10000):
        """
        Initialize backtest engine
        Args:
            bot: SuperTrendBot instance
            initial_balance: Starting balance for backtest
        """
        self.bot = bot
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.trades = []
        self.open_position = None
        self.logger = logging.getLogger('BacktestEngine')
        
    def run_backtest(self, symbol: str, start_date: datetime, end_date: datetime, timeframe: int):
        """
        Run backtest on historical data
        """
        self.logger.info("="*60)
        self.logger.info("STARTING BACKTEST")
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
        self.logger.info("Processing data...")
        
        # Calculate indicators for full dataset
        df = self._prepare_data(df)
        
        equity_curve = []
        
        # Simulate trading bar by bar
        for i in range(100, len(df)):  # Start after warmup period
            current_bar = df.iloc[i]
            current_time = current_bar['time']
            
            # Update existing position if any
            if self.open_position:
                self._update_position(current_bar, i)
            
            # Check for new signals if no open position
            if not self.open_position:
                signal = self._generate_signal(df.iloc[:i+1])
                if signal:
                    self._open_position(signal, current_bar, i)
            
            # Record equity
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
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        import talib
        
        df['hl2'] = (df['high'] + df['low']) / 2
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.bot.config.atr_period)
        df['volume_ma'] = df['tick_volume'].rolling(window=self.bot.config.volume_ma_period).mean()
        df['volatility'] = df['close'].rolling(window=self.bot.config.atr_period).std()
        df['norm_volatility'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
        # Fill NaN
        df['norm_volatility'].fillna(1.0, inplace=True)
        df['atr'].bfill(inplace=True)
        df['volume_ma'].fillna(df['tick_volume'].mean(), inplace=True)
        
        # Calculate SuperTrends for different factors
        factors = np.arange(self.bot.config.min_factor, 
                           self.bot.config.max_factor + self.bot.config.factor_step, 
                           self.bot.config.factor_step)
        
        for factor in factors:
            df[f'st_{factor:.1f}'] = self._calculate_supertrend(df, factor)
        
        return df
    
    def _calculate_supertrend(self, df: pd.DataFrame, factor: float) -> pd.Series:
        """Calculate SuperTrend indicator"""
        hl2 = df['hl2'].values
        atr = df['atr'].values
        close = df['close'].values
        
        upper_band = hl2 + (factor * atr)
        lower_band = hl2 - (factor * atr)
        
        supertrend = np.zeros(len(df))
        direction = np.ones(len(df))  # 1 = uptrend, -1 = downtrend
        
        for i in range(1, len(df)):
            # Adjust bands
            if close[i-1] <= upper_band[i-1]:
                upper_band[i] = min(upper_band[i], upper_band[i-1])
            if close[i-1] >= lower_band[i-1]:
                lower_band[i] = max(lower_band[i], lower_band[i-1])
            
            # Determine trend
            if close[i] <= lower_band[i]:
                direction[i] = -1
                supertrend[i] = upper_band[i]
            elif close[i] >= upper_band[i]:
                direction[i] = 1
                supertrend[i] = lower_band[i]
            else:
                direction[i] = direction[i-1]
                supertrend[i] = upper_band[i] if direction[i] == -1 else lower_band[i]
        
        return pd.Series(direction, index=df.index)
    
    def _generate_signal(self, df: pd.DataFrame) -> Dict:
        """Generate trading signal based on SuperTrend consensus"""
        if len(df) < 100:
            return None
        
        current_bar = df.iloc[-1]
        prev_bar = df.iloc[-2]
        
        # Get all SuperTrend signals
        factors = np.arange(self.bot.config.min_factor, 
                           self.bot.config.max_factor + self.bot.config.factor_step, 
                           self.bot.config.factor_step)
        
        buy_signals = 0
        sell_signals = 0
        
        for factor in factors:
            col = f'st_{factor:.1f}'
            if col in df.columns:
                current_st = current_bar[col]
                prev_st = prev_bar[col]
                
                # Check for trend change
                if prev_st <= 0 and current_st > 0:  # Bullish crossover
                    buy_signals += 1
                elif prev_st >= 0 and current_st < 0:  # Bearish crossover
                    sell_signals += 1
        
        # Volume filter
        volume_ok = current_bar['tick_volume'] > current_bar['volume_ma'] * self.bot.config.volume_multiplier
        
        # Generate signal if consensus reached
        total_factors = len(factors)
        consensus_threshold = total_factors * 0.6  # 60% agreement
        
        if buy_signals >= consensus_threshold and volume_ok:
            return {
                'type': 'BUY',
                'price': current_bar['close'],
                'atr': current_bar['atr'],
                'time': current_bar['time']
            }
        elif sell_signals >= consensus_threshold and volume_ok:
            return {
                'type': 'SELL',
                'price': current_bar['close'],
                'atr': current_bar['atr'],
                'time': current_bar['time']
            }
        
        return None
    
    def _open_position(self, signal: Dict, bar: pd.Series, bar_index: int):
        """Open dual positions - RR 1:1 + Main RR with proper crypto support"""
        entry_price = signal['price']
        atr = signal['atr']
        
        # Calculate SL and TPs
        if signal['type'] == 'BUY':
            sl = entry_price - (atr * self.bot.config.sl_multiplier)
            risk = entry_price - sl
            tp1 = entry_price + (risk * 1.0)  # RR 1:1 (quick profit)
            tp2 = entry_price + (atr * self.bot.config.tp_multiplier)  # Main RR
            direction = 1
        else:  # SELL
            sl = entry_price + (atr * self.bot.config.sl_multiplier)
            risk = sl - entry_price
            tp1 = entry_price - (risk * 1.0)  # RR 1:1 (quick profit)
            tp2 = entry_price - (atr * self.bot.config.tp_multiplier)  # Main RR
            direction = -1
        
        # Calculate position size based on risk (per order)
        risk_amount = self.balance * (self.bot.config.risk_percent / 100)
        sl_distance = abs(entry_price - sl)
        
        # Check if this is crypto
        is_crypto = any(crypto in self.bot.config.symbol.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA'])
        
        if is_crypto:
            # For crypto: Direct USD calculation
            # Assume 1 lot = 1 BTC/ETH (contract_size = 1.0)
            # Risk per lot = SL distance in USD × contract_size
            contract_size = 1.0  # Standard for most crypto brokers
            risk_per_lot = sl_distance * contract_size
            
            if risk_per_lot > 0:
                lot_size = risk_amount / risk_per_lot
            else:
                lot_size = 0.01
            
            self.logger.debug(f"[CRYPTO] {self.bot.config.symbol}: SL=${sl_distance:.2f}, Risk/lot=${risk_per_lot:.2f}, Lot={lot_size:.4f}")
        else:
            # For forex: Use point-based calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                point = 0.01
                pip_value = 1.0  # $1 per pip per lot for gold
            elif 'JPY' in self.bot.config.symbol:
                point = 0.01
                pip_value = 10.0  # $10 per pip per lot for JPY
            else:
                point = 0.0001
                pip_value = 10.0  # $10 per pip per lot for standard forex
            
            pips = sl_distance / point
            lot_size = risk_amount / (pips * pip_value)
            
            self.logger.debug(f"[FOREX] {self.bot.config.symbol}: SL pips={pips:.1f}, Pip value=${pip_value:.2f}, Lot={lot_size:.2f}")
        
        # Round and limit lot size
        lot_size = round(lot_size, 4)  # More precision for crypto
        lot_size = max(0.01, min(lot_size, 100.0))  # Limit to 0.01 - 100 lots
        
        # Store DUAL orders (both active initially)
        self.open_position = {
            'type': signal['type'],
            'entry_price': entry_price,
            'entry_time': signal['time'],
            'entry_bar': bar_index,
            'sl': sl,
            'direction': direction,
            'lot_size': lot_size,
            # Order 1: RR 1:1 (quick profit)
            'order1': {
                'active': True,
                'tp': tp1,
                'lot_size': lot_size
            },
            # Order 2: Main RR
            'order2': {
                'active': True,
                'tp': tp2,
                'lot_size': lot_size
            }
        }
        
        # Log with bar timestamp
        bar_time = signal['time'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(signal['time'], pd.Timestamp) else signal['time']
        main_rr = self.bot.config.tp_multiplier / self.bot.config.sl_multiplier
        total_risk = self.bot.config.risk_percent * 2
        
        # Calculate actual risk per lot for verification
        actual_risk_per_lot = sl_distance if is_crypto else (sl_distance / point) * pip_value
        actual_total_risk = actual_risk_per_lot * lot_size * 2
        
        self.logger.info(f"[{bar_time}] [DUAL OPEN] {signal['type']} at {entry_price:.5f}, SL: {sl:.5f}")
        self.logger.info(f"  Order 1: TP1={tp1:.5f} (RR 1:1), Size={lot_size:.4f}")
        self.logger.info(f"  Order 2: TP2={tp2:.5f} (RR {main_rr:.1f}:1), Size={lot_size:.4f}")
        self.logger.info(f"  Balance: ${self.balance:.2f}, Risk: ${risk_amount:.2f} per order, Actual: ${actual_total_risk:.2f} total")
    
    def _update_position(self, bar: pd.Series, bar_index: int):
        """Update open position - check for SL/TP hit on dual orders"""
        if not self.open_position:
            return
        
        pos = self.open_position
        current_price = bar['close']
        high = bar['high']
        low = bar['low']
        
        # Check Order 1 (RR 1:1)
        if pos['order1']['active']:
            if pos['type'] == 'BUY':
                if low <= pos['sl']:
                    self._close_single_order('order1', pos['sl'], bar['time'], bar_index, "Stop Loss - Order 1")
                elif high >= pos['order1']['tp']:
                    self._close_single_order('order1', pos['order1']['tp'], bar['time'], bar_index, "Take Profit - Order 1 (RR 1:1)")
            else:  # SELL
                if high >= pos['sl']:
                    self._close_single_order('order1', pos['sl'], bar['time'], bar_index, "Stop Loss - Order 1")
                elif low <= pos['order1']['tp']:
                    self._close_single_order('order1', pos['order1']['tp'], bar['time'], bar_index, "Take Profit - Order 1 (RR 1:1)")
        
        # Check Order 2 (Main RR)
        if pos['order2']['active']:
            if pos['type'] == 'BUY':
                if low <= pos['sl']:
                    self._close_single_order('order2', pos['sl'], bar['time'], bar_index, "Stop Loss - Order 2")
                elif high >= pos['order2']['tp']:
                    self._close_single_order('order2', pos['order2']['tp'], bar['time'], bar_index, "Take Profit - Order 2 (Main RR)")
            else:  # SELL
                if high >= pos['sl']:
                    self._close_single_order('order2', pos['sl'], bar['time'], bar_index, "Stop Loss - Order 2")
                elif low <= pos['order2']['tp']:
                    self._close_single_order('order2', pos['order2']['tp'], bar['time'], bar_index, "Take Profit - Order 2 (Main RR)")
        
        # Close position entirely if both orders closed
        if not pos['order1']['active'] and not pos['order2']['active']:
            self.open_position = None
    
    def _close_position(self, bar: pd.Series, bar_index: int, reason: str):
        """Close all remaining active orders at current bar close"""
        if not self.open_position:
            return
        
        pos = self.open_position
        
        # Close Order 1 if still active
        if pos['order1']['active']:
            self._close_single_order('order1', bar['close'], bar['time'], bar_index, f"{reason} - Order 1")
        
        # Close Order 2 if still active
        if pos['order2']['active']:
            self._close_single_order('order2', bar['close'], bar['time'], bar_index, f"{reason} - Order 2")
        
        self.open_position = None
    
    def _close_single_order(self, order_key: str, exit_price: float, exit_time, bar_index: int, reason: str):
        """Close a single order from dual position with crypto support"""
        if not self.open_position:
            return
        
        pos = self.open_position
        order = pos[order_key]
        
        if not order['active']:
            return
        
        # Calculate P&L based on symbol type
        price_diff = (exit_price - pos['entry_price']) * pos['direction']
        
        # Check if crypto
        is_crypto = any(crypto in self.bot.config.symbol.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA'])
        
        if is_crypto:
            # For crypto: Direct USD calculation
            # 1 lot = 1 BTC/ETH, so P&L = price_diff × lot_size
            contract_size = 1.0
            profit = price_diff * contract_size * order['lot_size']
            pips = price_diff  # For crypto, "pips" = USD change
            
            self.logger.debug(f"[CRYPTO P&L] Price diff=${price_diff:.2f}, Lot={order['lot_size']:.4f}, Profit=${profit:.2f}")
        else:
            # For forex/commodities: Pip-based calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                point = 0.01
                pip_value = 1.0
            elif 'JPY' in self.bot.config.symbol:
                point = 0.01
                pip_value = 10.0
            else:
                point = 0.0001
                pip_value = 10.0
            
            pips = price_diff / point
            profit = pips * pip_value * order['lot_size']
        
        self.balance += profit
        
        # Record trade
        trade = {
            'entry_time': pos['entry_time'],
            'exit_time': exit_time,
            'type': pos['type'],
            'entry_price': pos['entry_price'],
            'exit_price': exit_price,
            'sl': pos['sl'],
            'tp': order['tp'],
            'lot_size': order['lot_size'],
            'pips': pips,
            'profit': profit,
            'balance': self.balance,
            'reason': reason,
            'bars_held': bar_index - pos['entry_bar'],
            'order_type': 'RR_1:1' if order_key == 'order1' else 'Main_RR'
        }
        
        self.trades.append(trade)
        
        # Log with bar timestamp and balance
        exit_time_str = exit_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(exit_time, pd.Timestamp) else exit_time
        pip_label = "USD" if is_crypto else "pips"
        self.logger.info(f"[{exit_time_str}] [CLOSE] {pos['type']} {trade['order_type']} at {exit_price:.5f}, P&L: ${profit:.2f} ({pips:.1f} {pip_label}) - {reason} | Balance: ${self.balance:,.2f}")
        
        # Mark order as closed
        order['active'] = False
    
    def _calculate_equity(self, bar: pd.Series) -> float:
        """Calculate current equity including unrealized P&L from both active orders with crypto support"""
        if not self.open_position:
            return self.balance
        
        pos = self.open_position
        current_price = bar['close']
        
        # Calculate unrealized P&L
        price_diff = (current_price - pos['entry_price']) * pos['direction']
        
        # Check if crypto
        is_crypto = any(crypto in self.bot.config.symbol.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA'])
        
        # Calculate unrealized P&L for each active order
        unrealized_profit = 0
        
        if is_crypto:
            # For crypto: Direct USD calculation
            contract_size = 1.0
            if pos['order1']['active']:
                unrealized_profit += price_diff * contract_size * pos['order1']['lot_size']
            if pos['order2']['active']:
                unrealized_profit += price_diff * contract_size * pos['order2']['lot_size']
        else:
            # For forex/commodities: Pip-based calculation
            if 'XAU' in self.bot.config.symbol or 'GOLD' in self.bot.config.symbol:
                point = 0.01
                pip_value = 1.0
            elif 'JPY' in self.bot.config.symbol:
                point = 0.01
                pip_value = 10.0
            else:
                point = 0.0001
                pip_value = 10.0
            
            pips = price_diff / point
            
            if pos['order1']['active']:
                unrealized_profit += pips * pip_value * pos['order1']['lot_size']
            if pos['order2']['active']:
                unrealized_profit += pips * pip_value * pos['order2']['lot_size']
        
        return self.balance + unrealized_profit
    
    def _generate_report(self, equity_curve: List[Dict], df: pd.DataFrame) -> Dict:
        """Generate comprehensive backtest report with dual order statistics"""
        self.logger.info("="*60)
        self.logger.info("BACKTEST RESULTS")
        self.logger.info("="*60)
        
        if not self.trades:
            self.logger.info("No trades executed during backtest period")
            return None
        
        # Calculate statistics
        trades_df = pd.DataFrame(self.trades)
        
        # Separate RR 1:1 and Main RR orders
        rr1_trades = trades_df[trades_df['order_type'] == 'RR_1:1']
        main_trades = trades_df[trades_df['order_type'] == 'Main_RR']
        
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
        
        # RR 1:1 statistics
        rr1_wins = len(rr1_trades[rr1_trades['profit'] > 0])
        rr1_losses = len(rr1_trades[rr1_trades['profit'] < 0])
        rr1_win_rate = (rr1_wins / len(rr1_trades) * 100) if len(rr1_trades) > 0 else 0
        rr1_profit = rr1_trades['profit'].sum() if len(rr1_trades) > 0 else 0
        
        # Main RR statistics
        main_wins = len(main_trades[main_trades['profit'] > 0])
        main_losses = len(main_trades[main_trades['profit'] < 0])
        main_win_rate = (main_wins / len(main_trades) * 100) if len(main_trades) > 0 else 0
        main_profit = main_trades['profit'].sum() if len(main_trades) > 0 else 0
        
        # Calculate max drawdown
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # Calculate Sharpe ratio
        equity_pct_change = equity_series.pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * equity_pct_change.mean() / equity_pct_change.std() if len(equity_pct_change) > 0 else 0
        
        # Print results
        self.logger.info(f"Total Trades: {total_trades} (Dual Orders Strategy)")
        self.logger.info(f"  - RR 1:1 Orders: {len(rr1_trades)}")
        self.logger.info(f"  - Main RR Orders: {len(main_trades)}")
        self.logger.info(f"Winning Trades: {winning_trades}")
        self.logger.info(f"Losing Trades: {losing_trades}")
        self.logger.info(f"Win Rate: {win_rate:.2f}%")
        self.logger.info(f"")
        self.logger.info(f"--- RR 1:1 Orders Performance ---")
        self.logger.info(f"Wins/Losses: {rr1_wins}/{rr1_losses}")
        self.logger.info(f"Win Rate: {rr1_win_rate:.2f}%")
        self.logger.info(f"Total P&L: ${rr1_profit:,.2f}")
        self.logger.info(f"")
        self.logger.info(f"--- Main RR Orders Performance ---")
        self.logger.info(f"Wins/Losses: {main_wins}/{main_losses}")
        self.logger.info(f"Win Rate: {main_win_rate:.2f}%")
        self.logger.info(f"Total P&L: ${main_profit:,.2f}")
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
            'rr1_trades': len(rr1_trades),
            'rr1_win_rate': rr1_win_rate,
            'rr1_profit': rr1_profit,
            'main_trades': len(main_trades),
            'main_win_rate': main_win_rate,
            'main_profit': main_profit,
            'trades': self.trades,
            'equity_curve': equity_curve
        }
