import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class Trade:
    entry_price: float
    stop_loss: float
    take_profit: float
    direction: int  # 1 for BUY, -1 for SELL
    volume: float
    ticket: int = 0
    entry_time: datetime = None
    order_block_price: float = 0.0
    fvg_price: float = 0.0
    ticket1: int = 0  # Quick profit order (RR 1:1)
    ticket2: int = 0  # Main RR order
    tp1_hit: bool = False  # Track if Order 1 hit TP
    sl_moved_to_breakeven: bool = False  # Track if SL moved to BE

@dataclass
class Config:
    symbol: str = "EURUSD"
    timeframe: int = mt5.TIMEFRAME_M15
    risk_percent: float = 1.0
    lookback_candles: int = 20  # For Order Blocks
    fvg_min_size: float = 0.0005  # Minimum FVG size
    liquidity_sweep_pips: float = 5.0  # Pips for liquidity sweep detection
    rr_ratio: float = 2.0  # Risk/Reward ratio
    max_positions: int = 1
    magic_number: int = 123457
    use_market_structure: bool = True  # Use BOS/CHoCH
    use_order_blocks: bool = True
    use_fvg: bool = True
    use_liquidity_sweeps: bool = True
    move_sl_to_breakeven: bool = True  # Move SL to BE when Order 1 hits TP

@dataclass
class OrderBlock:
    price_high: float
    price_low: float
    direction: str  # 'bullish' or 'bearish'
    time: datetime
    strength: float  # 0-100
    
@dataclass
class FairValueGap:
    top: float
    bottom: float
    direction: str  # 'bullish' or 'bearish'
    time: datetime
    filled: bool = False

class ICTBot:
    def __init__(self, config: Config):
        self.config = config
        self.current_trade = None
        self.trade_history = []
        self.logger = self._setup_logger()
        self.is_connected = False
        self.order_blocks = []
        self.fair_value_gaps = []
        self.market_structure = {'highs': [], 'lows': [], 'trend': 'neutral'}
        
    def _setup_logger(self):
        logger = logging.getLogger('ICTBot')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('ict_bot.log')
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
        
    def get_data(self, bars: int = 500) -> pd.DataFrame:
        """Get market data"""
        rates = mt5.copy_rates_from_pos(self.config.symbol, self.config.timeframe, 0, bars)
        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            self.logger.error(f"[ERROR] Failed to get rates for {self.config.symbol}: {error}")
            
            if not mt5.symbol_select(self.config.symbol, True):
                self.logger.error(f"   Cannot enable symbol {self.config.symbol}")
            else:
                self.logger.info(f"   Symbol {self.config.symbol} enabled, retry...")
                rates = mt5.copy_rates_from_pos(self.config.symbol, self.config.timeframe, 0, bars)
                if rates is None or len(rates) == 0:
                    self.logger.error(f"   Still no data after enabling symbol")
                    return None
        
        self.logger.info(f"[OK] Loaded {len(rates)} bars for {self.config.symbol}")
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        return df
    
    def identify_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Identify Higher Highs (HH), Higher Lows (HL), Lower Highs (LH), Lower Lows (LL)
        BOS (Break of Structure) and CHoCH (Change of Character)
        """
        if len(df) < 20:
            return self.market_structure
        
        # Only analyze recent data for performance
        recent_df = df.tail(100) if len(df) > 100 else df
        
        # Find swing highs and lows (use .loc to avoid SettingWithCopyWarning)
        swing_high = recent_df['high'][(recent_df['high'] > recent_df['high'].shift(1)) & 
                                       (recent_df['high'] > recent_df['high'].shift(-1)) &
                                       (recent_df['high'] > recent_df['high'].shift(2)) &
                                       (recent_df['high'] > recent_df['high'].shift(-2))]
        
        swing_low = recent_df['low'][(recent_df['low'] < recent_df['low'].shift(1)) & 
                                      (recent_df['low'] < recent_df['low'].shift(-1)) &
                                      (recent_df['low'] < recent_df['low'].shift(2)) &
                                      (recent_df['low'] < recent_df['low'].shift(-2))]
        
        # Get recent swing points
        recent_highs = swing_high.dropna().tail(5).tolist()
        recent_lows = swing_low.dropna().tail(5).tolist()
        
        # Determine trend
        trend = 'neutral'
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            # Bullish: Higher Highs and Higher Lows
            if recent_highs[-1] > recent_highs[-2] and recent_lows[-1] > recent_lows[-2]:
                trend = 'bullish'
            # Bearish: Lower Highs and Lower Lows
            elif recent_highs[-1] < recent_highs[-2] and recent_lows[-1] < recent_lows[-2]:
                trend = 'bearish'
        
        self.market_structure = {
            'highs': recent_highs,
            'lows': recent_lows,
            'trend': trend,
            'last_high': recent_highs[-1] if recent_highs else None,
            'last_low': recent_lows[-1] if recent_lows else None
        }
        
        return self.market_structure
    
    def identify_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """
        Identify Order Blocks (OB)
        Bullish OB: Last down candle before strong up move
        Bearish OB: Last up candle before strong down move
        """
        if len(df) < self.config.lookback_candles:
            return []
        
        order_blocks = []
        
        # Only scan recent data for performance (last 50 candles)
        scan_range = min(50, len(df) - 3)
        start_idx = len(df) - scan_range - 3
        
        for i in range(start_idx, len(df) - 3):
            # Bullish Order Block
            if (df['close'].iloc[i] < df['open'].iloc[i] and  # Down candle
                df['close'].iloc[i+1] > df['open'].iloc[i+1] and  # Up candle
                df['close'].iloc[i+2] > df['open'].iloc[i+2] and  # Up candle
                df['close'].iloc[i+2] > df['high'].iloc[i]):  # Strong move up
                
                ob = OrderBlock(
                    price_high=df['high'].iloc[i],
                    price_low=df['low'].iloc[i],
                    direction='bullish',
                    time=df.index[i],
                    strength=((df['close'].iloc[i+2] - df['low'].iloc[i]) / df['low'].iloc[i]) * 100
                )
                order_blocks.append(ob)
            
            # Bearish Order Block
            elif (df['close'].iloc[i] > df['open'].iloc[i] and  # Up candle
                  df['close'].iloc[i+1] < df['open'].iloc[i+1] and  # Down candle
                  df['close'].iloc[i+2] < df['open'].iloc[i+2] and  # Down candle
                  df['close'].iloc[i+2] < df['low'].iloc[i]):  # Strong move down
                
                ob = OrderBlock(
                    price_high=df['high'].iloc[i],
                    price_low=df['low'].iloc[i],
                    direction='bearish',
                    time=df.index[i],
                    strength=((df['high'].iloc[i] - df['close'].iloc[i+2]) / df['high'].iloc[i]) * 100
                )
                order_blocks.append(ob)
        
        # Keep only recent and strong order blocks
        order_blocks = sorted(order_blocks, key=lambda x: x.strength, reverse=True)[:5]
        self.order_blocks = order_blocks
        
        return order_blocks
    
    def identify_fair_value_gaps(self, df: pd.DataFrame) -> List[FairValueGap]:
        """
        Identify Fair Value Gaps (FVG/Imbalance)
        Bullish FVG: Gap between candle[i-2].high and candle[i].low
        Bearish FVG: Gap between candle[i-2].low and candle[i].high
        """
        if len(df) < 3:
            return []
        
        fvgs = []
        
        for i in range(2, len(df)):
            # Bullish FVG
            if df['low'].iloc[i] > df['high'].iloc[i-2]:
                gap_size = df['low'].iloc[i] - df['high'].iloc[i-2]
                if gap_size >= self.config.fvg_min_size:
                    fvg = FairValueGap(
                        top=df['low'].iloc[i],
                        bottom=df['high'].iloc[i-2],
                        direction='bullish',
                        time=df.index[i]
                    )
                    fvgs.append(fvg)
            
            # Bearish FVG
            elif df['high'].iloc[i] < df['low'].iloc[i-2]:
                gap_size = df['low'].iloc[i-2] - df['high'].iloc[i]
                if gap_size >= self.config.fvg_min_size:
                    fvg = FairValueGap(
                        top=df['low'].iloc[i-2],
                        bottom=df['high'].iloc[i],
                        direction='bearish',
                        time=df.index[i]
                    )
                    fvgs.append(fvg)
        
        # Keep only recent unfilled FVGs
        fvgs = [fvg for fvg in fvgs if not fvg.filled][-10:]
        self.fair_value_gaps = fvgs
        
        return fvgs
    
    def detect_liquidity_sweep(self, df: pd.DataFrame) -> Optional[str]:
        """
        Detect liquidity sweep (stop hunt)
        Buy Side Liquidity (BSL): Recent highs
        Sell Side Liquidity (SSL): Recent lows
        """
        if len(df) < 20:
            return None
        
        recent_df = df.tail(20)
        current_price = df['close'].iloc[-1]
        
        # Find recent swing high/low
        recent_high = recent_df['high'].max()
        recent_low = recent_df['low'].min()
        
        pip_size = 0.0001 if 'JPY' not in self.config.symbol else 0.01
        sweep_distance = self.config.liquidity_sweep_pips * pip_size
        
        # Check if price swept recent high then reversed (bearish sweep)
        if (df['high'].iloc[-2] >= recent_high and 
            df['close'].iloc[-1] < recent_high - sweep_distance):
            return 'bearish_sweep'
        
        # Check if price swept recent low then reversed (bullish sweep)
        if (df['low'].iloc[-2] <= recent_low and 
            df['close'].iloc[-1] > recent_low + sweep_distance):
            return 'bullish_sweep'
        
        return None
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signal based on ICT concepts
        Optimized for performance
        """
        if len(df) < 50:
            return None
        
        # Work with last N candles only for efficiency
        recent_df = df.tail(100) if len(df) > 100 else df
        current_price = recent_df['close'].iloc[-1]
        
        # Identify market components (only on recent data)
        if self.config.use_market_structure:
            market_structure = self.identify_market_structure(recent_df)
        
        if self.config.use_order_blocks:
            order_blocks = self.identify_order_blocks(recent_df)
        
        if self.config.use_fvg:
            fvgs = self.identify_fair_value_gaps(recent_df)
        
        if self.config.use_liquidity_sweeps:
            liquidity_sweep = self.detect_liquidity_sweep(recent_df)
        
        # BULLISH SIGNAL CONDITIONS
        bullish_conditions = 0
        bullish_ob = None
        
        # 1. Market structure is bullish
        if self.config.use_market_structure and market_structure.get('trend') == 'bullish':
            bullish_conditions += 1
        
        # 2. Price touched bullish order block
        if self.config.use_order_blocks:
            for ob in order_blocks:
                if (ob.direction == 'bullish' and 
                    ob.price_low <= current_price <= ob.price_high * 1.002):
                    bullish_conditions += 1
                    bullish_ob = ob
                    break
        
        # 3. Bullish FVG present
        if self.config.use_fvg:
            for fvg in fvgs:
                if fvg.direction == 'bullish' and fvg.bottom <= current_price <= fvg.top:
                    bullish_conditions += 1
                    break
        
        # 4. Bullish liquidity sweep occurred
        if self.config.use_liquidity_sweeps and liquidity_sweep == 'bullish_sweep':
            bullish_conditions += 2  # Higher weight
        
        # BEARISH SIGNAL CONDITIONS
        bearish_conditions = 0
        bearish_ob = None
        
        # 1. Market structure is bearish
        if self.config.use_market_structure and market_structure.get('trend') == 'bearish':
            bearish_conditions += 1
        
        # 2. Price touched bearish order block
        if self.config.use_order_blocks:
            for ob in order_blocks:
                if (ob.direction == 'bearish' and 
                    ob.price_low * 0.998 <= current_price <= ob.price_high):
                    bearish_conditions += 1
                    bearish_ob = ob
                    break
        
        # 3. Bearish FVG present
        if self.config.use_fvg:
            for fvg in fvgs:
                if fvg.direction == 'bearish' and fvg.bottom <= current_price <= fvg.top:
                    bearish_conditions += 1
                    break
        
        # 4. Bearish liquidity sweep occurred
        if self.config.use_liquidity_sweeps and liquidity_sweep == 'bearish_sweep':
            bearish_conditions += 2  # Higher weight
        
        # Generate signal if conditions met
        if bullish_conditions >= 2:
            atr = self.calculate_atr(recent_df)
            return {
                'type': 'BUY',
                'price': current_price,
                'atr': atr,
                'order_block': bullish_ob,
                'conditions': bullish_conditions,
                'time': recent_df.index[-1]
            }
        
        elif bearish_conditions >= 2:
            atr = self.calculate_atr(recent_df)
            return {
                'type': 'SELL',
                'price': current_price,
                'atr': atr,
                'order_block': bearish_ob,
                'conditions': bearish_conditions,
                'time': recent_df.index[-1]
            }
        
        return None
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk - ensures exactly risk_percent per trade with crypto support"""
        account_info = mt5.account_info()
        if account_info is None:
            self.logger.warning("Account info not available, using minimum lot")
            return 0.01
        
        balance = account_info.balance
        risk_amount = balance * (self.config.risk_percent / 100)
        
        # Get symbol info for accurate calculation
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.warning(f"Cannot get symbol info for {self.config.symbol}, using default")
            return 0.01
        
        # Calculate stop loss distance in price
        sl_distance = abs(entry_price - stop_loss)
        
        if sl_distance == 0:
            self.logger.warning("Stop loss distance is zero")
            return 0.01
        
        # Check if this is a crypto pair
        is_crypto = any(crypto in self.config.symbol.upper() for crypto in ['BTC', 'ETH', 'LTC', 'XRP', 'ADA'])
        
        if is_crypto:
            # For crypto: Calculate based on contract size and actual USD value
            contract_size = symbol_info.trade_contract_size
            
            # Risk per lot = SL distance (in USD) × contract size
            # For BTC: if SL = $500 and contract = 1, risk = $500
            risk_per_lot = sl_distance * contract_size
            
            if risk_per_lot > 0:
                lot_size = risk_amount / risk_per_lot
            else:
                self.logger.warning(f"Invalid risk_per_lot: {risk_per_lot}")
                lot_size = symbol_info.volume_min
            
            self.logger.info(f"[CRYPTO] {self.config.symbol}: Entry=${entry_price:.2f}, SL=${stop_loss:.2f}, Distance=${sl_distance:.2f}, Contract={contract_size}, Risk/lot=${risk_per_lot:.2f}, Lot={lot_size:.4f}")
        else:
            # For forex/commodities: Use standard tick value calculation
            # Calculate tick value (profit/loss per 1 tick for 1 lot)
            tick_value = symbol_info.trade_tick_value
            tick_size = symbol_info.trade_tick_size
            
            # Calculate how many ticks in our SL distance
            ticks_at_risk = sl_distance / tick_size
            
            # Calculate lot size: risk_amount / (ticks_at_risk * tick_value)
            # This ensures that if SL is hit, loss = exactly risk_amount
            lot_size = risk_amount / (ticks_at_risk * tick_value)
            
            self.logger.debug(f"[FOREX] {self.config.symbol}: SL distance={sl_distance:.5f}, Ticks={ticks_at_risk:.2f}, Tick value={tick_value:.2f}, Lot={lot_size:.2f}")
        
        # Round to symbol's volume step
        volume_step = symbol_info.volume_step
        lot_size = round(lot_size / volume_step) * volume_step
        
        # Apply min/max limits
        lot_size = max(symbol_info.volume_min, min(lot_size, symbol_info.volume_max))
        
        self.logger.info(f"[POSITION SIZE] Symbol: {self.config.symbol}, Balance: ${balance:.2f}, Risk: ${risk_amount:.2f} ({self.config.risk_percent}%), Final lot: {lot_size:.4f}")
        
        return lot_size
    
    def open_position(self, signal: Dict) -> bool:
        """Open dual positions - RR 1:1 + Main RR"""
        if self.current_trade is not None:
            self.logger.info("[WARNING] Already have open position")
            return False
        
        entry_price = signal['price']
        atr = signal['atr']
        
        # Calculate SL and TPs based on order block or ATR
        if signal['type'] == 'BUY':
            if signal.get('order_block'):
                sl = signal['order_block'].price_low * 0.999  # Below OB
            else:
                sl = entry_price - (atr * 1.5)
            
            risk = abs(entry_price - sl)
            tp1 = entry_price + (risk * 1.0)  # RR 1:1 (quick profit)
            tp2 = entry_price + (risk * self.config.rr_ratio)  # Main RR
            direction = 1
        else:  # SELL
            if signal.get('order_block'):
                sl = signal['order_block'].price_high * 1.001  # Above OB
            else:
                sl = entry_price + (atr * 1.5)
            
            risk = abs(entry_price - sl)
            tp1 = entry_price - (risk * 1.0)  # RR 1:1 (quick profit)
            tp2 = entry_price - (risk * self.config.rr_ratio)  # Main RR
            direction = -1
        
        # Calculate position size (per order)
        lot_size = self.calculate_position_size(entry_price, sl)
        
        # Log risk calculation for verification
        account_info = mt5.account_info()
        if account_info:
            expected_risk = account_info.balance * (self.config.risk_percent / 100)
            sl_distance = abs(entry_price - sl)
            symbol_info = mt5.symbol_info(self.config.symbol)
            if symbol_info:
                ticks_at_risk = sl_distance / symbol_info.trade_tick_size
                actual_risk = lot_size * ticks_at_risk * symbol_info.trade_tick_value
                total_risk = actual_risk * 2  # Dual orders
                self.logger.info(f"[RISK] Balance: ${account_info.balance:.2f}, Expected Risk per order: ${expected_risk:.2f} ({self.config.risk_percent}%), Actual Risk per order: ${actual_risk:.2f}, Total Risk: ${total_risk:.2f} ({self.config.risk_percent * 2}%), Lot Size per order: {lot_size}")
        
        # Place DUAL orders
        symbol_info = mt5.symbol_info(self.config.symbol)
        if symbol_info is None:
            self.logger.error(f"Symbol {self.config.symbol} not found")
            return False
        
        if not symbol_info.visible:
            if not mt5.symbol_select(self.config.symbol, True):
                self.logger.error(f"Failed to select {self.config.symbol}")
                return False
        
        # Get prices
        order_type = mt5.ORDER_TYPE_BUY if signal['type'] == 'BUY' else mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(self.config.symbol).ask if signal['type'] == 'BUY' else mt5.symbol_info_tick(self.config.symbol).bid
        
        # ORDER 1: Quick Profit (RR 1:1)
        request1 = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp1,  # RR 1:1
            "deviation": 20,
            "magic": self.config.magic_number,
            "comment": f"ICT_{signal['type']}_RR1",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result1 = mt5.order_send(request1)
        
        if result1.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order 1 failed: {result1.retcode} - {result1.comment}")
            return False
        
        # ORDER 2: Main RR
        request2 = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.config.symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp2,  # Main RR
            "deviation": 20,
            "magic": self.config.magic_number,
            "comment": f"ICT_{signal['type']}_RR2",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result2 = mt5.order_send(request2)
        
        if result2.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error(f"Order 2 failed: {result2.retcode} - {result2.comment}")
            # Close Order 1 if Order 2 fails
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": result1.order,
                "symbol": self.config.symbol,
                "volume": lot_size,
                "type": mt5.ORDER_TYPE_SELL if signal['type'] == 'BUY' else mt5.ORDER_TYPE_BUY,
                "price": mt5.symbol_info_tick(self.config.symbol).bid if signal['type'] == 'BUY' else mt5.symbol_info_tick(self.config.symbol).ask,
                "deviation": 20,
                "magic": self.config.magic_number,
                "comment": "Rollback",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            mt5.order_send(close_request)
            return False
        
        # Store trade with total volume (both orders)
        self.current_trade = Trade(
            entry_price=price,
            stop_loss=sl,
            take_profit=tp2,  # Main RR for tracking
            direction=direction,
            volume=lot_size * 2,  # Total volume
            ticket=result1.order,  # Track first order ticket (for backward compatibility)
            ticket1=result1.order,  # Quick profit order
            ticket2=result2.order,  # Main RR order
            entry_time=datetime.now(),
            order_block_price=signal.get('order_block').price_low if signal.get('order_block') else 0,
            tp1_hit=False,
            sl_moved_to_breakeven=False
        )
        
        self.logger.info(f"[DUAL OPEN] {signal['type']} at {price:.5f}, SL: {sl:.5f}, Conditions: {signal.get('conditions', 0)}")
        self.logger.info(f"  Order 1: TP1={tp1:.5f} (RR 1:1), Size={lot_size}, Ticket={result1.order}")
        self.logger.info(f"  Order 2: TP2={tp2:.5f} (RR {self.config.rr_ratio:.1f}:1), Size={lot_size}, Ticket={result2.order}")
        self.logger.info(f"  Total Risk: {self.config.risk_percent * 2:.2f}% (2 orders)")
        
        return True
    
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
    
    def check_position_status(self) -> Optional[str]:
        """Check if position hit SL or TP"""
        if self.current_trade is None:
            return None
        
        # Get current position
        positions = mt5.positions_get(ticket=self.current_trade.ticket)
        
        if positions is None or len(positions) == 0:
            # Position closed
            # Check history to see if it was TP or SL
            from_date = self.current_trade.entry_time - timedelta(hours=1)
            deals = mt5.history_deals_get(from_date, datetime.now(), position=self.current_trade.ticket)
            
            if deals and len(deals) > 0:
                last_deal = deals[-1]
                profit = last_deal.profit
                
                # Get account balance after close
                account_info = mt5.account_info()
                balance = account_info.balance if account_info else 0
                equity = account_info.equity if account_info else 0
                
                if profit > 0:
                    reason = "Take Profit"
                elif profit < 0:
                    reason = "Stop Loss"
                else:
                    reason = "Break Even"
                
                # Add to history first
                self.trade_history.append({
                    'ticket': self.current_trade.ticket,
                    'entry_price': self.current_trade.entry_price,
                    'exit_price': last_deal.price,
                    'profit': profit,
                    'reason': reason,
                    'balance': balance,
                    'equity': equity,
                    'entry_time': self.current_trade.entry_time,
                    'exit_time': datetime.now()
                })
                
                # Calculate updated stats
                stats = self.get_stats()
                
                # Log with full stats
                self.logger.info(f"[CLOSE] Position #{self.current_trade.ticket} - {reason}")
                self.logger.info(f"        Profit: ${profit:.2f} | Balance: ${balance:.2f} | Equity: ${equity:.2f}")
                self.logger.info(f"        Total: {stats['total_trades']} trades | Win: {stats['winning_trades']} | Loss: {stats['losing_trades']} | Win Rate: {stats['win_rate']:.2f}%")
                
                self.current_trade = None
                return reason
        
        return None
    
    def get_stats(self) -> Dict:
        """Get trading statistics"""
        if not self.trade_history:
            return {'total_trades': 0, 'win_rate': 0.0, 'profit_factor': 0.0, 'total_profit': 0.0}
        
        total_trades = len(self.trade_history)
        winning_trades = [t for t in self.trade_history if t['profit'] > 0]
        losing_trades = [t for t in self.trade_history if t['profit'] < 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        gross_profit = sum(t['profit'] for t in winning_trades)
        gross_loss = abs(sum(t['profit'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        total_profit = sum(t['profit'] for t in self.trade_history)
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_profit': total_profit,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss
        }
    
    def run_cycle(self):
        """Run one trading cycle"""
        df = self.get_data(500)
        
        if df is None or len(df) < 50:
            self.logger.warning("[WARNING] Not enough data")
            return
        
        # Check existing position status
        if self.current_trade is not None:
            # Check if Order 1 hit TP and move SL to breakeven
            self.check_and_move_sl_to_breakeven()
            
            # Check overall position status
            self.check_position_status()
        
        # Try to open new position if none exists
        if self.current_trade is None:
            signal = self.generate_signal(df)
            
            if signal:
                self.logger.info(f"[ANALYZING] Signal detected: {signal['type']}, Conditions: {signal.get('conditions', 0)}")
                self.open_position(signal)
        else:
            # Monitor existing position
            self.logger.debug(f"Monitoring position {self.current_trade.ticket}")
    
    def run(self, interval_seconds: int = 60):
        """Main trading loop"""
        import time
        
        self.logger.info("Starting ICT Bot...")
        
        # Display stats periodically
        stats_display_counter = 0
        stats_interval = 10  # Display stats every 10 cycles
        
        try:
            while True:
                self.run_cycle()
                
                # Display stats periodically
                stats_display_counter += 1
                if stats_display_counter >= stats_interval:
                    stats = self.get_stats()
                    if stats['total_trades'] > 0:
                        self.logger.info("="*60)
                        self.logger.info(f"CURRENT STATS - Total: {stats['total_trades']} | Win: {stats['winning_trades']} | Loss: {stats['losing_trades']}")
                        self.logger.info(f"Win Rate: {stats['win_rate']:.2f}% | PF: {stats['profit_factor']:.2f} | Total P/L: ${stats['total_profit']:.2f}")
                        self.logger.info("="*60)
                    stats_display_counter = 0
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
            # Print final stats
            stats = self.get_stats()
            self.logger.info("="*60)
            self.logger.info("FINAL STATISTICS")
            self.logger.info("="*60)
            self.logger.info(f"Total Trades: {stats['total_trades']}")
            self.logger.info(f"Winning Trades: {stats['winning_trades']} ({stats['win_rate']:.2f}%)")
            self.logger.info(f"Losing Trades: {stats['losing_trades']} ({100-stats['win_rate']:.2f}%)")
            self.logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
            self.logger.info(f"Profit Factor: {stats['profit_factor']:.2f}")
            self.logger.info(f"Gross Profit: ${stats['gross_profit']:.2f}")
            self.logger.info(f"Gross Loss: ${stats['gross_loss']:.2f}")
            self.logger.info(f"Net P/L: ${stats['total_profit']:.2f}")
            
            # Get current account info
            account_info = mt5.account_info()
            if account_info:
                self.logger.info(f"Current Balance: ${account_info.balance:.2f}")
                self.logger.info(f"Current Equity: ${account_info.equity:.2f}")
            
            self.logger.info("="*60)
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}", exc_info=True)
