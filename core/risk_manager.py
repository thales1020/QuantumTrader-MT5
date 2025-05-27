class RiskManager:
    def __init__(self, max_daily_loss_percent=5.0, max_correlation=0.7):
        self.max_daily_loss_percent = max_daily_loss_percent
        self.max_correlation = max_correlation
        self.daily_trades = []
        self.last_reset = datetime.now().date()
        
    def check_daily_loss_limit(self, account_balance):
        if datetime.now().date() > self.last_reset:
            self.daily_trades = []
            self.last_reset = datetime.now().date()
            
        daily_loss = sum(t['profit'] for t in self.daily_trades if t['profit'] < 0)
        max_allowed_loss = account_balance * (self.max_daily_loss_percent / 100)
        
        return abs(daily_loss) < max_allowed_loss
        
    def check_correlation(self, symbols_in_trade):
        # Simplified correlation check
        correlated_pairs = {
            'EURUSD': ['GBPUSD', 'EURGBP'],
            'GBPUSD': ['EURUSD', 'EURGBP'],
            'USDJPY': ['EURJPY', 'GBPJPY'],
            'AUDUSD': ['NZDUSD'],
            'NZDUSD': ['AUDUSD']
        }
        
        for symbol in symbols_in_trade:
            if symbol in correlated_pairs:
                for corr_symbol in correlated_pairs[symbol]:
                    if corr_symbol in symbols_in_trade:
                        return False
        return True
        
    def calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        if avg_loss == 0:
            return 0.01
        
        b = avg_win / avg_loss
        p = win_rate / 100
        q = 1 - p
        
        kelly = (p * b - q) / b
        
        # Use fractional Kelly (25%) for safety
        return max(0.01, min(kelly * 0.25, 0.02))