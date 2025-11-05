"""
Base Backtest Engine - Kiến trúc module hóa cho backtesting
===========================================================

Thiết kế theo 3 phần độc lập:
1. BrokerSimulator - Giả lập công ty chứng khoán
2. Strategy Interface - Thuật toán giao dịch
3. PerformanceAnalyzer - Báo cáo và đánh giá

Lợi ích:
- Code tái sử dụng cho mọi strategy
- Tách biệt logic strategy và execution
- Dễ bảo trì và mở rộng
- Giống nhau giữa backtest, paper trading, live trading

Author: QuantumTrader Team
Version: 2.0.0
Date: November 2025
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
import logging

from engines.broker_simulator import (
    BrokerSimulator, BrokerConfig, Order, OrderType, OrderStatus
)
from engines.performance_analyzer import (
    PerformanceAnalyzer, PerformanceMetrics, TradeRecord
)


class BaseStrategy(ABC):
    """
    Base class cho mọi strategy
    
    Strategy chỉ lo phân tích và đưa ra signal
    Execution được handle bởi BrokerSimulator
    
    => Cùng code hoạt động cho backtest, paper, live
    """
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, current_bar: Dict) -> Optional[Dict]:
        """
        Phân tích data và trả về signal
        
        Returns:
            {
                'action': 'BUY' | 'SELL' | 'CLOSE',
                'lot_size': float,
                'stop_loss': float,
                'take_profit': float,
                'reason': str
            }
            hoặc None nếu không có signal
        """
        pass
    
    @abstractmethod
    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Tính toán indicators
        
        Returns:
            DataFrame với indicators đã tính
        """
        pass
    
    def on_trade_closed(self, trade: TradeRecord):
        """
        Callback khi trade đóng (optional)
        Strategy có thể override để adjust parameters
        """
        pass


class BaseBacktestEngine:
    """
    Engine chung cho mọi loại backtest
    
    Sử dụng:
    1. BrokerSimulator - Xử lý order execution
    2. PerformanceAnalyzer - Tính metrics
    3. Strategy - Đưa ra signals
    
    => Loại bỏ code duplication hoàn toàn
    """
    
    def __init__(self, 
                 strategy: BaseStrategy,
                 broker_config: Optional[BrokerConfig] = None,
                 initial_balance: float = 10000):
        """
        Args:
            strategy: Strategy instance
            broker_config: Broker configuration
            initial_balance: Starting balance
        """
        self.strategy = strategy
        self.initial_balance = initial_balance
        
        # Components
        self.broker = BrokerSimulator(
            config=broker_config or BrokerConfig(),
            initial_balance=initial_balance
        )
        self.analyzer = PerformanceAnalyzer(initial_balance=initial_balance)
        
        self.logger = logging.getLogger('BaseBacktestEngine')
        self.trade_counter = 0
        
    def run_backtest(self, 
                    symbol: str,
                    start_date: datetime,
                    end_date: datetime,
                    timeframe: int,
                    export_excel: bool = True,
                    excel_path: Optional[str] = None) -> PerformanceMetrics:
        """
        Chạy backtest
        
        Args:
            symbol: Trading symbol
            start_date: Backtest start
            end_date: Backtest end
            timeframe: MT5 timeframe
            export_excel: Export report to Excel
            excel_path: Excel file path
            
        Returns:
            PerformanceMetrics
        """
        self.logger.info("="*70)
        self.logger.info("🚀 STARTING BACKTEST - REALISTIC MODE")
        self.logger.info("="*70)
        self.logger.info(f"Symbol:           {symbol}")
        self.logger.info(f"Period:           {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        self.logger.info(f"Initial Balance:  ${self.initial_balance:,.2f}")
        self.logger.info(f"Broker Config:")
        self.logger.info(f"  Spread:         {self.broker.config.spread_pips} pips")
        self.logger.info(f"  Commission:     ${self.broker.config.commission_per_lot}/lot")
        self.logger.info(f"  Slippage:       {self.broker.config.slippage_pips_avg} pips avg")
        self.logger.info(f"  Fill Rate:      {self.broker.config.fill_probability*100:.1f}%")
        self.logger.info("="*70 + "\n")
        
        # 1. Load historical data
        rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
        
        if rates is None or len(rates) == 0:
            self.logger.error(f"❌ No historical data for {symbol}")
            return self.analyzer.calculate_metrics()
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)  # ← FIX: Set time as index for strategy
        
        self.logger.info(f"📊 Loaded {len(df)} bars\n")
        
        # 2. Prepare data with indicators
        self.logger.info("📈 Calculating indicators...")
        df = self.strategy.prepare_data(df)
        self.logger.info("✅ Indicators ready\n")
        
        # 3. Run bar-by-bar simulation
        self.logger.info("🔄 Running simulation...\n")
        
        for idx in range(len(df)):
            current_bar = df.iloc[idx].to_dict()
            current_bar['time'] = df.index[idx]  # Add time from index
            
            # Update broker với bar mới
            self.broker.update_positions(current_bar)
            
            # Record equity point
            account_info = self.broker.get_account_info()
            self.analyzer.add_equity_point(
                timestamp=current_bar['time'],
                balance=account_info['balance'],
                equity=account_info['equity'],
                positions=account_info['num_positions'],
                margin_level=account_info['margin_level']
            )
            
            # Check for newly closed positions
            self._process_closed_trades()
            
            # Get signal from strategy
            signal = self.strategy.analyze(df.iloc[:idx+1], current_bar)
            
            if signal:
                self._execute_signal(signal, current_bar, symbol)
            
            # Progress update
            if (idx + 1) % 500 == 0:
                progress = (idx + 1) / len(df) * 100
                self.logger.info(f"Progress: {progress:.1f}% | Balance: ${account_info['balance']:,.2f}")
        
        # 4. Close any remaining positions
        self.logger.info("\n🔒 Closing remaining positions...")
        self._close_all_positions(df.iloc[-1].to_dict())
        
        # 5. Calculate final metrics
        self.logger.info("\n📊 Calculating performance metrics...")
        metrics = self.analyzer.calculate_metrics()
        
        # 6. Print summary
        self.analyzer.print_summary(metrics)
        
        # 7. Export to Excel
        if export_excel:
            if not excel_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                excel_path = f"reports/backtest_{symbol}_{timestamp}.xlsx"
            
            self.analyzer.export_to_excel(excel_path, metrics)
        
        return metrics
    
    def _execute_signal(self, signal: Dict, current_bar: Dict, symbol: str):
        """Execute signal from strategy"""
        
        action = signal.get('action')
        
        if action == 'CLOSE':
            # Close all positions
            for pos_id in list(self.broker.positions.keys()):
                self.broker.close_position(pos_id, current_bar['close'], "Signal: Close")
            return
        
        if action in ['BUY', 'SELL']:
            direction = 1 if action == 'BUY' else -1
            lot_size = signal.get('lot_size', 0.1)
            sl = signal.get('stop_loss')
            tp = signal.get('take_profit')
            price = current_bar['close']
            
            # Submit order to broker
            success, order, error = self.broker.submit_order(
                symbol=symbol,
                order_type=OrderType.MARKET,
                direction=direction,
                lot_size=lot_size,
                price=price,
                sl=sl,
                tp=tp,
                current_bar=current_bar
            )
            
            if success:
                reason = signal.get('reason', 'Strategy signal')
                self.logger.info(f"✅ {action} order executed | Reason: {reason}")
            else:
                self.logger.warning(f"❌ {action} order rejected | Reason: {error}")
    
    def _process_closed_trades(self):
        """Process newly closed positions and add to analyzer"""
        
        # Check for new closed positions
        while len(self.broker.closed_positions) > self.trade_counter:
            pos = self.broker.closed_positions[self.trade_counter]
            
            # Create trade record
            self.trade_counter += 1
            
            trade = TradeRecord(
                trade_id=self.trade_counter,
                symbol=pos.symbol,
                direction="LONG" if pos.direction == 1 else "SHORT",
                entry_time=pos.open_time,
                exit_time=datetime.now(),
                entry_price=pos.entry_price,
                exit_price=pos.current_price,
                lot_size=pos.lot_size,
                gross_pnl=pos.realized_pnl + pos.total_commission + pos.total_swap,
                commission=pos.total_commission,
                swap=pos.total_swap,
                spread_cost=pos.spread_cost,
                slippage=0.0,  # Already included in entry/exit price
                net_pnl=pos.realized_pnl,
                pips=self._calculate_pips(pos),
                duration_hours=(datetime.now() - pos.open_time).total_seconds() / 3600,
                exit_reason="TP/SL",
                balance_after=self.broker.balance,
                equity_after=self.broker.equity,
                drawdown_pct=0.0  # Will be calculated by analyzer
            )
            
            # Add to analyzer
            self.analyzer.add_trade(trade)
            
            # Notify strategy
            self.strategy.on_trade_closed(trade)
    
    def _close_all_positions(self, last_bar: Dict):
        """Close all remaining positions at end of backtest"""
        for pos_id in list(self.broker.positions.keys()):
            self.broker.close_position(pos_id, last_bar['close'], "Backtest End")
        
        # Process final closed trades
        self._process_closed_trades()
    
    def _calculate_pips(self, position) -> float:
        """Calculate pips from position"""
        price_diff = (position.current_price - position.entry_price) * position.direction
        
        if 'JPY' in position.symbol:
            return price_diff / 0.01
        else:
            return price_diff / 0.0001
    
    def get_broker_stats(self) -> Dict:
        """Get broker statistics"""
        return {
            'total_orders': len(self.broker.order_history),
            'filled_orders': len([o for o in self.broker.order_history if o.status == OrderStatus.FILLED]),
            'rejected_orders': len([o for o in self.broker.order_history if o.status == OrderStatus.REJECTED]),
            'rejection_rate': len([o for o in self.broker.order_history if o.status == OrderStatus.REJECTED]) / len(self.broker.order_history) * 100 if self.broker.order_history else 0
        }
    
    def optimize_parameters(self, 
                          symbol: str,
                          start_date: datetime,
                          end_date: datetime,
                          timeframe: int,
                          param_ranges: Dict[str, List]) -> pd.DataFrame:
        """
        Optimize strategy parameters
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            timeframe: Timeframe
            param_ranges: Dict of parameter ranges
                {
                    'atr_period': [10, 14, 20],
                    'atr_multiplier': [2.0, 3.0, 4.0]
                }
        
        Returns:
            DataFrame with optimization results
        """
        from itertools import product
        
        self.logger.info("🔧 Starting parameter optimization...")
        
        # Generate all combinations
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(product(*param_values))
        
        results = []
        
        for idx, combo in enumerate(combinations):
            params = dict(zip(param_names, combo))
            
            self.logger.info(f"\n[{idx+1}/{len(combinations)}] Testing: {params}")
            
            # Update strategy parameters
            for param, value in params.items():
                setattr(self.strategy, param, value)
            
            # Run backtest
            metrics = self.run_backtest(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe,
                export_excel=False
            )
            
            # Store results
            result = params.copy()
            result.update({
                'total_return': metrics.total_return_pct,
                'sharpe_ratio': metrics.sharpe_ratio,
                'max_drawdown': metrics.max_drawdown_pct,
                'profit_factor': metrics.profit_factor,
                'win_rate': metrics.win_rate,
                'total_trades': metrics.total_trades
            })
            results.append(result)
        
        df_results = pd.DataFrame(results)
        
        # Sort by Sharpe ratio
        df_results = df_results.sort_values('sharpe_ratio', ascending=False)
        
        self.logger.info("\n" + "="*70)
        self.logger.info("OPTIMIZATION RESULTS (Top 10)")
        self.logger.info("="*70)
        print(df_results.head(10).to_string())
        
        return df_results


class RealisticBacktestEngine(BaseBacktestEngine):
    """
    Backtest engine với realistic simulation
    - Sử dụng BrokerSimulator cho realistic execution
    - Đầy đủ costs (spread, commission, slippage, swap)
    - Order rejection simulation
    - Drawdown và risk analysis
    """
    
    def __init__(self, strategy: BaseStrategy, initial_balance: float = 10000,
                 spread_pips: float = 1.5, commission: float = 7.0):
        """
        Args:
            strategy: Strategy instance
            initial_balance: Starting balance
            spread_pips: Spread in pips
            commission: Commission per lot (USD)
        """
        broker_config = BrokerConfig(
            spread_pips=spread_pips,
            commission_per_lot=commission,
            slippage_pips_avg=0.5,
            fill_probability=0.95
        )
        
        super().__init__(
            strategy=strategy,
            broker_config=broker_config,
            initial_balance=initial_balance
        )
        
        self.logger = logging.getLogger('RealisticBacktestEngine')


# Example usage template
if __name__ == "__main__":
    """
    Example: How to use the new modular architecture
    """
    
    # 1. Create your strategy
    class MyStrategy(BaseStrategy):
        def __init__(self, atr_period=14, atr_multiplier=3.0):
            self.atr_period = atr_period
            self.atr_multiplier = atr_multiplier
        
        def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
            # Calculate indicators
            # ... (SuperTrend, ATR, etc.)
            return data
        
        def analyze(self, data: pd.DataFrame, current_bar: Dict) -> Optional[Dict]:
            # Analyze and return signal
            # ...
            return None
    
    # 2. Create engine
    strategy = MyStrategy()
    engine = RealisticBacktestEngine(
        strategy=strategy,
        initial_balance=10000,
        spread_pips=1.5,
        commission=7.0
    )
    
    # 3. Run backtest
    metrics = engine.run_backtest(
        symbol="EURUSD",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        timeframe=mt5.TIMEFRAME_H1,
        export_excel=True
    )
    
    print(f"Final Return: {metrics.total_return_pct:.2f}%")
    print(f"Sharpe Ratio: {metrics.sharpe_ratio:.3f}")
