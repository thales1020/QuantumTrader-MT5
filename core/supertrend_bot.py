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
        if rates is None:
            self.logger.error("Failed to get rates")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        df['hl2'] = (df['high'] + df['low']) / 2
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.config.atr_period)
        df['volume_ma'] = df['tick_volume'].rolling(window=self.config.volume_ma_period).mean()
        df['volatility'] = df['close'].rolling(window=self.config.atr_period).std()
        df['norm_volatility'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
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
            performances.append(perf)
            factors.append(factor)
            
        performances = np.array(performances).reshape(-1, 1)
        
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
        account_info = mt5.account_info()
        if account_info is None:
            return 0.01
            
        balance = account_info.balance
        risk_amount = balance * (self.config.risk_percent / 100)
        
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            return 0.01
            
        point_value = symbol_info.trade_tick_value / symbol_info.trade_tick_size
        position_size = risk_amount / (stop_loss_points * point_value)
        
        position_size = max(symbol_info.volume_min, min(position_size, symbol_info.volume_max))
        position_size = round(position_size / symbol_info.volume_step) * symbol_info.volume_step
        
        return position_size
        
    def check_volume_condition(self, df: pd.DataFrame) -> bool:
        current_volume = df['tick_volume'].iloc[-1]
        avg_volume = df['volume_ma'].iloc[-1]
        return current_volume > avg_volume * self.config.volume_multiplier
        
    def place_order(self, order_type: int, volume: float, price: float, sl: float, tp: float) -> int:
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
            "comment": "SuperTrend Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order failed: {result.comment}")
            return None
            
        self.logger.info(f"Order placed: {result.order}")
        return result.order
        
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
            return
            
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
            tp = current_price + current_atr * self.config.tp_multiplier
            sl_points = (current_price - sl) / mt5.symbol_info(self.config.symbol).point
            volume = self.calculate_position_size(sl_points)
            
            ticket = self.place_order(mt5.ORDER_TYPE_BUY, volume, current_price, sl, tp)
            if ticket:
                self.current_trade = Trade(
                    entry_price=current_price,
                    stop_loss=sl,
                    take_profit=tp,
                    direction=1,
                    volume=volume,
                    ticket=ticket,
                    entry_time=datetime.now()
                )
                self.logger.info(f"BUY signal executed at {current_price}, SL: {sl}, TP: {tp}")
                
        elif sell_signal and open_positions < self.config.max_positions:
            sl = current_price + current_atr * self.config.sl_multiplier
            tp = current_price - current_atr * self.config.tp_multiplier
            sl_points = (sl - current_price) / mt5.symbol_info(self.config.symbol).point
            volume = self.calculate_position_size(sl_points)
            
            ticket = self.place_order(mt5.ORDER_TYPE_SELL, volume, current_price, sl, tp)
            if ticket:
                self.current_trade = Trade(
                    entry_price=current_price,
                    stop_loss=sl,
                    take_profit=tp,
                    direction=-1,
                    volume=volume,
                    ticket=ticket,
                    entry_time=datetime.now()
                )
                self.logger.info(f"SELL signal executed at {current_price}, SL: {sl}, TP: {tp}")
                
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