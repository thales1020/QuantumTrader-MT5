class BacktestEngine:
    def __init__(self, strategy, initial_balance=10000):
        self.strategy = strategy
        self.initial_balance = initial_balance
        self.trades = []
        
    def run_backtest(self, symbol, start_date, end_date, timeframe):
        # Load historical data
        rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
        df = pd.DataFrame(rates)
        
        balance = self.initial_balance
        equity_curve = []
        
        for i in range(100, len(df)):
            # Get data up to current point
            current_df = df.iloc[:i+1].copy()
            
            # Run strategy
            signal = self.strategy.generate_signal(current_df)
            
            if signal and not self.has_open_position():
                # Place trade
                trade = self.place_virtual_trade(signal, current_df.iloc[-1], balance)
                self.trades.append(trade)
                
            # Update open positions
            self.update_positions(current_df.iloc[-1])
            
            # Calculate equity
            equity = self.calculate_equity(balance, current_df.iloc[-1])
            equity_curve.append({
                'time': current_df.iloc[-1]['time'],
                'equity': equity,
                'balance': balance
            })
            
        return self.generate_backtest_report(equity_curve)
        
    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        excess_returns = returns - risk_free_rate/252
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
    def calculate_max_drawdown(self, equity_curve):
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
                
        return max_dd * 100