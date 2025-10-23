import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import talib
from sklearn.cluster import KMeans
import logging
import json
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Trade:
    entry_price: float
    stop_loss: float
    take_profit: float
    direction: int
    volume: float
    ticket: int = 0
    entry_time: datetime = None
    ticket1: int = 0  # Quick profit order (RR 1:1)
    ticket2: int = 0  # Main RR order
    tp1_hit: bool = False  # Track if Order 1 hit TP
    sl_moved_to_breakeven: bool = False  # Track if SL moved to BE
    
@dataclass
class Config:
    symbol: str = "EURUSD"
    timeframe: int = mt5.TIMEFRAME_M30
    atr_period: int = 10
    min_factor: float = 1.0
    max_factor: float = 5.0
    factor_step: float = 0.5
    perf_alpha: float = 10.0
    cluster_choice: str = "Best"
    volume_ma_period: int = 20
    volume_multiplier: float = 1.2
    sl_multiplier: float = 2.0
    tp_multiplier: float = 3.0
    use_trailing: bool = True
    trail_activation: float = 1.5
    risk_percent: float = 1.0
    max_positions: int = 1
    magic_number: int = 123456
    move_sl_to_breakeven: bool = True  # Move SL to BE when Order 1 hits TP
    
class SuperTrendBot:
    def __init__(self, config: Config):
        self.config = config
        self.current_trade = None
        self.trade_history = []
        self.logger = self._setup_logger()
        self.is_connected = False
        
    def _setup_logger(self):
        logger = logging.getLogger('SuperTrendBot')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('supertrend_bot.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger
        
    def connect(self, login: int, password: str, server: str) -> bool:
        if not mt5.initialize():
            self.logger.error("MT5 initialization failed")
            return False
            
        if not mt5.login(login, password=password, server=server):
            self.logger.error(f"Login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
            
        self.is_connected = True
        self.logger.info(f"Connected to MT5: {mt5.account_info().server}")
        return True
        
    def get_data(self, bars: int = 1000) -> pd.DataFrame:
        rates = mt5.copy_rates_from_pos(self.config.symbol, self.config.timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            self.logger.error(f"[ERROR] Failed to get rates for {self.config.symbol}: {error}")
            self.logger.error(f"   Symbol info: {mt5.symbol_info(self.config.symbol)}")
            
            # Try to enable symbol in Market Watch
            if not mt5.symbol_select(self.config.symbol, True):
                self.logger.error(f"   Cannot enable symbol {self.config.symbol}")
            else:
                self.logger.info(f"   Symbol {self.config.symbol} enabled in Market Watch, retry...")
                rates = mt5.copy_rates_from_pos(self.config.symbol, self.config.timeframe, 0, bars)
                if rates is None or len(rates) == 0:
                    self.logger.error(f"   Still no data after enabling symbol")
                    return None
        
        self.logger.info(f"[OK] Loaded {len(rates)} bars for {self.config.symbol}")
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        df['hl2'] = (df['high'] + df['low']) / 2
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.config.atr_period)
        df['volume_ma'] = df['tick_volume'].rolling(window=self.config.volume_ma_period).mean()
        df['volatility'] = df['close'].rolling(window=self.config.atr_period).std()
        df['norm_volatility'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
        # Fill NaN values
        df['norm_volatility'].fillna(1.0, inplace=True)  # Default to 1.0 if NaN
        df['atr'].fillna(method='bfill', inplace=True)  # Backfill ATR
        df['volume_ma'].fillna(df['tick_volume'].mean(), inplace=True)  # Use average volume
        
        # Log NaN count for debugging
        nan_count = df.isna().sum().sum()
        if nan_count > 0:
            self.logger.debug(f"[WARNING] Filled {nan_count} NaN values in indicators")
        
        return df
        
    def calculate_supertrends(self, df: pd.DataFrame) -> dict:
        factors = np.arange(self.config.min_factor, self.config.max_factor + self.config.factor_step, self.config.factor_step)
        supertrends = {}
        
        for factor in factors:
            st = pd.DataFrame(index=df.index)
            st['upper'] = df['hl2'] + (df['atr'] * factor)
            st['lower'] = df['hl2'] - (df['atr'] * factor)
            st['trend'] = 0
            st['output'] = 0.0
            st['perf'] = 0.0
            st['vol_adj_perf'] = 0.0
            
            for i in range(1, len(df)):
                if df['close'].iloc[i] > st['upper'].iloc[i-1]:
                    st.loc[st.index[i], 'trend'] = 1
                elif df['close'].iloc[i] < st['lower'].iloc[i-1]:
                    st.loc[st.index[i], 'trend'] = 0
                else:
                    st.loc[st.index[i], 'trend'] = st['trend'].iloc[i-1]
                
                if st['trend'].iloc[i] == 1:
                    st.loc[st.index[i], 'lower'] = max(st['lower'].iloc[i], st['lower'].iloc[i-1]) if st['trend'].iloc[i-1] == 1 else st['lower'].iloc[i]
                    st.loc[st.index[i], 'output'] = st['lower'].iloc[i]
                else:
                    st.loc[st.index[i], 'upper'] = min(st['upper'].iloc[i], st['upper'].iloc[i-1]) if st['trend'].iloc[i-1] == 0 else st['upper'].iloc[i]
                    st.loc[st.index[i], 'output'] = st['upper'].iloc[i]
                
                price_change = df['close'].iloc[i] - df['close'].iloc[i-1]
                direction = np.sign(df['close'].iloc[i-1] - st['output'].iloc[i-1])
                raw_perf = price_change * direction
                
                alpha = 2 / (self.config.perf_alpha + 1)
                st.loc[st.index[i], 'perf'] = alpha * raw_perf + (1 - alpha) * st['perf'].iloc[i-1]
                
                vol_adj = raw_perf / (1 + df['norm_volatility'].iloc[i])
                st.loc[st.index[i], 'vol_adj_perf'] = alpha * vol_adj + (1 - alpha) * st['vol_adj_perf'].iloc[i-1]
            
            supertrends[factor] = st
            
        return supertrends
        
    def perform_clustering(self, supertrends: dict) -> Tuple[float, float]:
        performances = []
        factors = []
        
        for factor, st in supertrends.items():
            perf = st['vol_adj_perf'].iloc[-100:].mean()
            # Skip if NaN
            if not np.isnan(perf) and not np.isinf(perf):
                performances.append(perf)
                factors.append(factor)
        
        # Check if we have valid performances
        if len(performances) == 0:
            self.logger.error("No valid performance data - all NaN values")
            # Return first factor as fallback
            first_factor = list(supertrends.keys())[0]
            return first_factor, 0.0
            
        performances = np.array(performances).reshape(-1, 1)
        
        # Remove any remaining NaN values
        valid_mask = ~np.isnan(performances).any(axis=1)
        performances = performances[valid_mask]
        factors = [f for i, f in enumerate(factors) if valid_mask[i]]
        
        if len(performances) == 0:
            self.logger.error("No valid performance data after NaN removal")
            first_factor = list(supertrends.keys())[0]
            return first_factor, 0.0
        
        if len(set(performances.flatten())) < 3:
            self.logger.warning("Not enough variation for clustering")
            return factors[np.argmax(performances)], performances.max()
            
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(performances)
        
        cluster_centers = kmeans.cluster_centers_.flatten()
        sorted_indices = np.argsort(cluster_centers)
        
        cluster_map = {"Worst": 0, "Average": 1, "Best": 2}
        target_cluster = cluster_map[self.config.cluster_choice]
        target_label = sorted_indices[target_cluster]
        
        cluster_factors = [factors[i] for i, label in enumerate(kmeans.labels_) if label == target_label]
        
        if not cluster_factors:
            self.logger.warning("No factors in target cluster")
            return factors[np.argmax(performances)], performances.max()
            
        return np.mean(cluster_factors), cluster_centers[target_label]
        
    def calculate_position_size(self, stop_loss_points: float) -> float:
        """Calculate position size based on risk management with crypto support"""
        account_info = mt5.account_info()
        if account_info is None:
            self.logger.warning("Account info not available, using minimum lot")
            return 0.01
            
        balance = account_info.balance
        risk_amount = balance * (self.config.risk_percent / 100)
        
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.warning(f"Symbol {self.config.symbol} info not available")
            return 0.01
        
        # Get current price for crypto calculation
        tick = mt5.symbol_info_tick(self.config.symbol)
        if tick is None:
            self.logger.warning("Tick info not available")
            return 0.01
        
        current_price = (tick.ask + tick.bid) / 2
        
        # Check if this is a crypto pair (BTC, ETH, etc.)
        is_crypto = any(crypto in self.config.symbol.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA'])
        
        if is_crypto:
            # For crypto: Calculate based on contract size and actual USD value
            # Most crypto: 1 lot = 1 BTC or 1 ETH, but check trade_contract_size
            contract_size = symbol_info.trade_contract_size
            
            # Calculate risk in USD per lot
            # stop_loss_points is in price units (e.g., $500 for BTC)
            risk_per_lot = stop_loss_points * contract_size
            
            # Calculate lot size based on risk
            if risk_per_lot > 0:
                position_size = risk_amount / risk_per_lot
            else:
                self.logger.warning(f"Invalid risk_per_lot: {risk_per_lot}")
                position_size = symbol_info.volume_min
            
            self.logger.info(f"[CRYPTO] {self.config.symbol}: SL={stop_loss_points:.2f} USD, Contract={contract_size}, Risk/lot=${risk_per_lot:.2f}, Calculated={position_size:.4f} lots")
        else:
            # For forex: Use standard point value calculation
            point_value = symbol_info.trade_tick_value / symbol_info.trade_tick_size
            position_size = risk_amount / (stop_loss_points * point_value)
            
            self.logger.debug(f"[FOREX] {self.config.symbol}: SL points={stop_loss_points:.5f}, Point value={point_value:.2f}, Calculated={position_size:.2f} lots")
        
        # Apply min/max limits
        position_size = max(symbol_info.volume_min, min(position_size, symbol_info.volume_max))
        
        # Round to volume step
        position_size = round(position_size / symbol_info.volume_step) * symbol_info.volume_step
        
        self.logger.info(f"[POSITION SIZE] Symbol: {self.config.symbol}, Balance: ${balance:.2f}, Risk: ${risk_amount:.2f} ({self.config.risk_percent}%), Final lot: {position_size:.4f}")
        
        return position_size
        
    def check_volume_condition(self, df: pd.DataFrame) -> bool:
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = df['volume_ma'].iloc[-1]
        return current_volume > avg_volume * self.config.volume_multiplier
        
    def place_order(self, order_type: int, volume: float, price: float, sl: float, tp: float, comment: str = "SuperTrend Bot") -> int:
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.error("Symbol info not found")
            return None
            
        point = symbol_info.point
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.config.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order failed: {result.comment}")
            return None
            
        self.logger.info(f"Order placed: {result.order}")
        return result.order
    
    def place_dual_orders(self, order_type: int, volume: float, price: float, sl: float, atr: float) -> Tuple[Optional[int], Optional[int]]:
        """
        Place dual orders for SuperTrend strategy
        Order 1: RR 1:1 (quick profit)
        Order 2: Main RR (from config tp_multiplier)
        
        Returns:
            Tuple of (ticket1, ticket2) or (None, None) if failed
        """
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.error("Symbol info not found for dual orders")
            return None, None
        
        # Calculate risk distance (SL distance)
        if order_type == mt5.ORDER_TYPE_BUY:
            risk = price - sl
            # Order 1: RR 1:1 (quick profit)
            tp1 = price + risk * 1.0
            # Order 2: Main RR
            tp2 = price + risk * (self.config.tp_multiplier / self.config.sl_multiplier)
            direction_str = "BUY"
        else:  # SELL
            risk = sl - price
            # Order 1: RR 1:1 (quick profit)
            tp1 = price - risk * 1.0
            # Order 2: Main RR
            tp2 = price - risk * (self.config.tp_multiplier / self.config.sl_multiplier)
            direction_str = "SELL"
        
        # Place Order 1 (RR 1:1 - Quick Profit)
        comment1 = f"ST_{direction_str}_RR1"
        ticket1 = self.place_order(order_type, volume, price, sl, tp1, comment1)
        
        if ticket1 is None:
            self.logger.error("Failed to place Order 1 (RR 1:1)")
            return None, None
        
        # Place Order 2 (Main RR)
        comment2 = f"ST_{direction_str}_RR2"
        ticket2 = self.place_order(order_type, volume, price, sl, tp2, comment2)
        
        if ticket2 is None:
            self.logger.error("Failed to place Order 2 (Main RR)")
            # Close Order 1 if Order 2 fails
            self.logger.warning("Closing Order 1 due to Order 2 failure")
            # Note: In production, you might want to close Order 1 here
            return ticket1, None
        
        self.logger.info(f"DUAL ORDERS placed: Ticket1={ticket1} (RR 1:1 @ {tp1:.5f}), Ticket2={ticket2} (Main RR @ {tp2:.5f})")
        
        return ticket1, ticket2
    
    def modify_sl(self, ticket: int, new_sl: float) -> bool:
        """Modify stop loss of an open position"""
        position = mt5.positions_get(ticket=ticket)
        
        if not position or len(position) == 0:
            self.logger.warning(f"Position {ticket} not found for SL modification")
            return False
        
        position = position[0]
        
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.config.symbol,
            "position": ticket,
            "sl": new_sl,
            "tp": position.tp,
            "magic": self.config.magic_number,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Failed to modify SL for ticket {ticket}: {result.retcode} - {result.comment}")
            return False
        
        self.logger.info(f"✅ SL modified for ticket {ticket}: {position.sl:.5f} → {new_sl:.5f}")
        return True
    
    def check_and_move_sl_to_breakeven(self):
        """Check if Order 1 hit TP and move Order 2's SL to breakeven"""
        if self.current_trade is None:
            return
        
        # Skip if already moved to breakeven
        if self.current_trade.sl_moved_to_breakeven:
            return
        
        # Skip if feature disabled
        if not self.config.move_sl_to_breakeven:
            return
        
        # Check if Order 1 (Quick Profit) still exists
        position1 = mt5.positions_get(ticket=self.current_trade.ticket1)
        
        # If Order 1 closed (hit TP), move Order 2's SL to breakeven
        if not position1 or len(position1) == 0:
            if not self.current_trade.tp1_hit:
                self.current_trade.tp1_hit = True
                self.logger.info(f"🎯 Order 1 (RR 1:1) closed! Moving Order 2's SL to breakeven...")
                
                # Check if Order 2 still exists
                position2 = mt5.positions_get(ticket=self.current_trade.ticket2)
                
                if position2 and len(position2) > 0:
                    # Move SL to entry price (breakeven)
                    breakeven_sl = self.current_trade.entry_price
                    
                    if self.modify_sl(self.current_trade.ticket2, breakeven_sl):
                        self.current_trade.sl_moved_to_breakeven = True
                        self.current_trade.stop_loss = breakeven_sl
                        self.logger.info(f"✅ Order 2 now at BREAKEVEN (SL = Entry = {breakeven_sl:.5f})")
                        self.logger.info(f"🔒 Trade is now RISK-FREE! Letting profits run to TP2={self.current_trade.take_profit:.5f}")
                else:
                    self.logger.info("⚠️ Order 2 already closed")
        
    def update_trailing_stop(self, position, current_price: float, atr: float) -> bool:
        if not self.config.use_trailing:
            return False
            
        symbol_info = mt5.symbol_info(self.config.symbol)
        point = symbol_info.point
        
        if position.type == mt5.ORDER_TYPE_BUY:
            if current_price - position.price_open > atr * self.config.trail_activation:
                new_sl = current_price - atr * self.config.sl_multiplier
                if new_sl > position.sl:
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "sl": new_sl,
                        "tp": position.tp,
                        "symbol": self.config.symbol,
                        "magic": self.config.magic_number,
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        self.logger.info(f"Trailing stop updated for position {position.ticket}")
                        return True
                        
        elif position.type == mt5.ORDER_TYPE_SELL:
            if position.price_open - current_price > atr * self.config.trail_activation:
                new_sl = current_price + atr * self.config.sl_multiplier
                if new_sl < position.sl:
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "sl": new_sl,
                        "tp": position.tp,
                        "symbol": self.config.symbol,
                        "magic": self.config.magic_number,
                    }
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        self.logger.info(f"Trailing stop updated for position {position.ticket}")
                        return True
                        
        return False
        
    def run_cycle(self):
        if not self.is_connected:
            self.logger.error("Not connected to MT5")
            return
            
        df = self.get_data()
        if df is None or len(df) < 200:
            self.logger.warning(f"[WARNING] Not enough data: {len(df) if df is not None else 0} bars (need 200+)")
            return
        
        self.logger.debug(f"[ANALYZING] Processing {len(df)} bars...")
        
        # Check if Order 1 hit TP and move SL to breakeven
        if self.current_trade is not None:
            self.check_and_move_sl_to_breakeven()
            
        supertrends = self.calculate_supertrends(df)
        optimal_factor, perf_score = self.perform_clustering(supertrends)
        
        current_st = supertrends[min(supertrends.keys(), key=lambda x: abs(x - optimal_factor))]
        current_trend = current_st['trend'].iloc[-1]
        prev_trend = current_st['trend'].iloc[-2]
        current_price = df['close'].iloc[-1]
        current_atr = df['atr'].iloc[-1]
        
        positions = mt5.positions_get(symbol=self.config.symbol)
        if positions:
            for position in positions:
                if position.magic == self.config.magic_number:
                    self.update_trailing_stop(position, current_price, current_atr)
                    
        buy_signal = current_trend > prev_trend and self.check_volume_condition(df)
        sell_signal = current_trend < prev_trend and self.check_volume_condition(df)
        
        open_positions = len([p for p in positions if p.magic == self.config.magic_number]) if positions else 0
        
        if buy_signal and open_positions < self.config.max_positions:
            sl = current_price - current_atr * self.config.sl_multiplier
            sl_points = (current_price - sl) / mt5.symbol_info(self.config.symbol).point
            volume = self.calculate_position_size(sl_points)
            
            # Place dual orders (RR 1:1 + Main RR)
            ticket1, ticket2 = self.place_dual_orders(mt5.ORDER_TYPE_BUY, volume, current_price, sl, current_atr)
            
            if ticket1 and ticket2:
                # Calculate TPs for logging
                risk = current_price - sl
                tp1 = current_price + risk * 1.0
                tp2 = current_price + risk * (self.config.tp_multiplier / self.config.sl_multiplier)
                
                self.current_trade = Trade(
                    entry_price=current_price,
                    stop_loss=sl,
                    take_profit=tp2,  # Store main TP
                    direction=1,
                    volume=volume * 2,  # Total volume (2 orders)
                    ticket=ticket1,  # Primary ticket (for backward compatibility)
                    ticket1=ticket1,  # Quick profit order
                    ticket2=ticket2,  # Main RR order
                    entry_time=datetime.now(),
                    tp1_hit=False,
                    sl_moved_to_breakeven=False
                )
                self.logger.info(f"BUY DUAL ORDERS executed at {current_price:.5f}")
                self.logger.info(f"  Order 1 (RR 1:1): SL={sl:.5f}, TP={tp1:.5f}, Vol={volume:.2f}, Ticket={ticket1}")
                self.logger.info(f"  Order 2 (Main RR): SL={sl:.5f}, TP={tp2:.5f}, Vol={volume:.2f}, Ticket={ticket2}")
                self.logger.info(f"  Total Risk: {self.config.risk_percent * 2:.2f}% (2 orders)")
            elif ticket1:
                # Only first order placed (fallback)
                tp = current_price + current_atr * self.config.tp_multiplier
                self.logger.warning("Only Order 1 placed, Order 2 failed")
                
        elif sell_signal and open_positions < self.config.max_positions:
            sl = current_price + current_atr * self.config.sl_multiplier
            sl_points = (sl - current_price) / mt5.symbol_info(self.config.symbol).point
            volume = self.calculate_position_size(sl_points)
            
            # Place dual orders (RR 1:1 + Main RR)
            ticket1, ticket2 = self.place_dual_orders(mt5.ORDER_TYPE_SELL, volume, current_price, sl, current_atr)
            
            if ticket1 and ticket2:
                # Calculate TPs for logging
                risk = sl - current_price
                tp1 = current_price - risk * 1.0
                tp2 = current_price - risk * (self.config.tp_multiplier / self.config.sl_multiplier)
                
                self.current_trade = Trade(
                    entry_price=current_price,
                    stop_loss=sl,
                    take_profit=tp2,  # Store main TP
                    direction=-1,
                    volume=volume * 2,  # Total volume (2 orders)
                    ticket=ticket1,  # Primary ticket (for backward compatibility)
                    ticket1=ticket1,  # Quick profit order
                    ticket2=ticket2,  # Main RR order
                    entry_time=datetime.now(),
                    tp1_hit=False,
                    sl_moved_to_breakeven=False
                )
                self.logger.info(f"SELL DUAL ORDERS executed at {current_price:.5f}")
                self.logger.info(f"  Order 1 (RR 1:1): SL={sl:.5f}, TP={tp1:.5f}, Vol={volume:.2f}, Ticket={ticket1}")
                self.logger.info(f"  Order 2 (Main RR): SL={sl:.5f}, TP={tp2:.5f}, Vol={volume:.2f}, Ticket={ticket2}")
                self.logger.info(f"  Total Risk: {self.config.risk_percent * 2:.2f}% (2 orders)")
            elif ticket1:
                # Only first order placed (fallback)
                tp = current_price - current_atr * self.config.tp_multiplier
                self.logger.warning("Only Order 1 placed, Order 2 failed")
                
    def calculate_statistics(self) -> dict:
        if not self.trade_history:
            return {"total_trades": 0, "win_rate": 0, "profit_factor": 0}
            
        wins = sum(1 for t in self.trade_history if t['profit'] > 0)
        losses = sum(1 for t in self.trade_history if t['profit'] < 0)
        total_profit = sum(t['profit'] for t in self.trade_history if t['profit'] > 0)
        total_loss = abs(sum(t['profit'] for t in self.trade_history if t['profit'] < 0))
        
        win_rate = (wins / len(self.trade_history)) * 100 if self.trade_history else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            "total_trades": len(self.trade_history),
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "avg_win": total_profit / wins if wins > 0 else 0,
            "avg_loss": total_loss / losses if losses > 0 else 0
        }
        
    def run(self, interval_seconds: int = 60):
        self.logger.info("Starting SuperTrend Bot...")
        
        try:
            while True:
                self.run_cycle()
                
                stats = self.calculate_statistics()
                self.logger.info(f"Stats: Win Rate: {stats['win_rate']:.2f}%, PF: {stats['profit_factor']:.2f}")
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.shutdown()
            
    def shutdown(self):
        if self.is_connected:
            positions = mt5.positions_get(symbol=self.config.symbol)
            if positions:
                for position in positions:
                    if position.magic == self.config.magic_number:
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": self.config.symbol,
                            "volume": position.volume,
                            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                            "position": position.ticket,
                            "price": mt5.symbol_info_tick(self.config.symbol).bid if position.type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(self.config.symbol).ask,
                            "deviation": 20,
                            "magic": self.config.magic_number,
                            "comment": "Bot shutdown",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }
                        mt5.order_send(request)
                        
            mt5.shutdown()
            self.logger.info("MT5 connection closed")

def main():
    config = Config(
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_M30,
        risk_percent=1.0,
        max_positions=1
    )
    
    bot = SuperTrendBot(config)
    
    login = 12345678
    password = "your_password"
    server = "your_broker_server"
    
    if bot.connect(login, password, server):
        bot.run(interval_seconds=30)

if __name__ == "__main__":
    main()