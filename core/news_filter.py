import requests
from datetime import datetime, timedelta

class NewsFilter:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.high_impact_events = []
        self.last_update = None
        
    def update_calendar(self):
        # This is a placeholder - implement with actual news API
        # ForexFactory, Investing.com, or Economic Calendar API
        if datetime.now() - self.last_update > timedelta(hours=1):
            try:
                # Fetch economic calendar data
                # self.high_impact_events = fetch_from_api()
                self.last_update = datetime.now()
            except:
                pass
                
    def is_news_time(self, symbol, minutes_before=30, minutes_after=30):
        current_time = datetime.now()
        
        for event in self.high_impact_events:
            if self.affects_symbol(event, symbol):
                event_time = event['datetime']
                if (event_time - timedelta(minutes=minutes_before) <= current_time <= 
                    event_time + timedelta(minutes=minutes_after)):
                    return True
        return False
        
    def affects_symbol(self, event, symbol):
        currency_map = {
            'USD': ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'NZDUSD', 'USDCAD'],
            'EUR': ['EURUSD', 'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD'],
            'GBP': ['GBPUSD', 'EURGBP', 'GBPJPY', 'GBPCHF'],
            'JPY': ['USDJPY', 'EURJPY', 'GBPJPY', 'AUDJPY'],
            'CHF': ['USDCHF', 'EURCHF', 'GBPCHF'],
            'AUD': ['AUDUSD', 'EURAUD', 'AUDJPY'],
            'NZD': ['NZDUSD'],
            'CAD': ['USDCAD']
        }
        
        event_currency = event.get('currency', '')
        return symbol in currency_map.get(event_currency, [])