#  Phase 1.5: SuperTrendBot Refactoring Plan

**Date**: October 23, 2025  
**Status**: Planning  
**Estimated Time**: 6-8 hours

---

##  Objective

Refactor SuperTrendBot to inherit from BaseTradingBot while maintaining all ML optimization features (K-means clustering, multi-factor SuperTrend).

---

##  Current SuperTrendBot Analysis

### File: `core/supertrend_bot.py` (670 lines)

### Structure:
```python
@dataclass Trade (24 lines)
@dataclass Config (20 lines)

class SuperTrendBot:
    - __init__()
    - _setup_logger()                      Will inherit from base
    - connect()                            Will inherit from base
    - get_data()                           Will inherit from base
    - calculate_supertrends()              Keep (SuperTrend specific)
    - perform_clustering()                 Keep (ML specific)
    - calculate_position_size()            Will inherit from base
    - check_volume_condition()             Keep (SuperTrend specific)
    - place_order()                        Will inherit from base
    - place_dual_orders()                  Will inherit from base
    - modify_sl()                          Will inherit from base
    - check_and_move_sl_to_breakeven()     Will inherit from base
    - update_trailing_stop()               Keep (SuperTrend specific)
    - run_cycle()                          Will use base template
    - calculate_statistics()               Will inherit from base
    - run()                                Will inherit from base
    - shutdown()                           Will inherit from base
```

### Key Features to Preserve:
1.  **Multi-factor SuperTrend** calculation (min/max factor)
2.  **K-means clustering** for factor optimization
3.  **Volume-adjusted performance** tracking
4.  **Normalized volatility** adjustment
5.  **Cluster choice** (Best/Average/Worst)
6.  **Trailing stop** logic
7.  **Volume condition** filtering
8.  **Crypto support** in position sizing

---

## 📋 Refactoring Strategy

### Similar to ICTBot Pattern:

```python
# 1. Create SuperTrendConfig(BaseConfig)
@dataclass
class SuperTrendConfig(BaseConfig):
    # Inherits from BaseConfig: symbol, timeframe, risk_percent, etc.
    
    # SuperTrend-specific parameters
    atr_period: int = 10
    min_factor: float = 1.0
    max_factor: float = 5.0
    factor_step: float = 0.5
    perf_alpha: float = 10.0
    cluster_choice: str = "Best"  # "Best", "Average", "Worst"
    volume_ma_period: int = 20
    volume_multiplier: float = 1.2
    use_trailing: bool = True
    trail_activation: float = 1.5

# 2. Create SuperTrendBot(BaseTradingBot)
class SuperTrendBot(BaseTradingBot):
    def __init__(self, config: SuperTrendConfig):
        super().__init__(config)
        # SuperTrend-specific state
        self.supertrends = {}  # Cache supertrend calculations
        self.optimal_factor = None
        self.cluster_performance = None
    
    # 3. Implement required abstract methods
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SuperTrend with ML optimization"""
        # Add ATR, volume MA, volatility
        # Calculate multi-factor supertrends
        # Perform K-means clustering
        # Select optimal factor
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Generate signal based on optimal SuperTrend"""
        # Use optimal factor from clustering
        # Check volume condition
        # Check trailing stop conditions
        # Return signal dict
        pass
    
    # 4. Keep SuperTrend-specific methods
    def calculate_supertrends(self, df: pd.DataFrame) -> dict:
        """Calculate multiple SuperTrend indicators"""
        # Keep existing logic
        pass
    
    def perform_clustering(self, supertrends: dict) -> Tuple[float, float]:
        """K-means clustering for factor optimization"""
        # Keep existing logic
        pass
    
    def check_volume_condition(self, df: pd.DataFrame) -> bool:
        """Volume filter"""
        # Keep existing logic
        pass
    
    def update_trailing_stop(self, position, current_price: float, atr: float) -> bool:
        """Update trailing stop"""
        # Keep existing logic
        pass
    
    # 5. Add hooks for extensibility
    def hook_post_signal_generation(self, signal: Optional[Dict]) -> Optional[Dict]:
        """Log SuperTrend details"""
        if signal:
            self.logger.info(f"SuperTrend Factor: {self.optimal_factor}")
            self.logger.info(f"Cluster Performance: {self.cluster_performance}")
        return signal
```

---

## 🔄 Code Migration Plan

### Step 1: Create Data Classes (30 min)
```python
@dataclass
class SuperTrendConfig(BaseConfig):
    # ML-specific parameters
    atr_period: int = 10
    min_factor: float = 1.0
    max_factor: float = 5.0
    factor_step: float = 0.5
    perf_alpha: float = 10.0
    cluster_choice: str = "Best"
    
    # Volume parameters
    volume_ma_period: int = 20
    volume_multiplier: float = 1.2
    
    # Trailing stop
    use_trailing: bool = True
    trail_activation: float = 1.5
```

### Step 2: Create Class Structure (1 hour)
- Inherit from BaseTradingBot
- Initialize with SuperTrendConfig
- Set up ML-specific state variables

### Step 3: Implement Abstract Methods (2-3 hours)

#### calculate_indicators():
```python
def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all SuperTrend indicators with ML optimization"""
    
    # 1. Basic indicators
    df['hl2'] = (df['high'] + df['low']) / 2
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], self.config.atr_period)
    df['volume_ma'] = df['tick_volume'].rolling(window=self.config.volume_ma_period).mean()
    df['volatility'] = df['close'].rolling(window=self.config.atr_period).std()
    df['norm_volatility'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
    
    # 2. Multi-factor SuperTrends
    self.supertrends = self.calculate_supertrends(df)
    
    # 3. ML Clustering
    self.optimal_factor, self.cluster_performance = self.perform_clustering(self.supertrends)
    
    # 4. Add optimal SuperTrend to df
    optimal_st = self.supertrends[self.optimal_factor]
    df['st_trend'] = optimal_st['trend']
    df['st_output'] = optimal_st['output']
    df['st_perf'] = optimal_st['vol_adj_perf']
    
    return df
```

#### generate_signal():
```python
def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
    """Generate trading signal based on optimal SuperTrend"""
    
    if len(df) < 50:
        return None
    
    # Check volume condition
    if not self.check_volume_condition(df):
        return None
    
    # Get optimal SuperTrend
    optimal_st = self.supertrends.get(self.optimal_factor)
    if optimal_st is None:
        return None
    
    current_trend = optimal_st['trend'].iloc[-1]
    previous_trend = optimal_st['trend'].iloc[-2]
    current_price = df['close'].iloc[-1]
    st_level = optimal_st['output'].iloc[-1]
    atr = df['atr'].iloc[-1]
    
    # Detect trend change
    signal = None
    
    if previous_trend == 0 and current_trend == 1:
        # Bullish signal
        signal = {
            'type': 'BUY',
            'price': current_price,
            'stop_loss': st_level,
            'take_profit': current_price + (self.config.tp_multiplier * atr),
            'confidence': min(100, self.cluster_performance * 10) if self.cluster_performance else 50,
            'reason': f'SuperTrend bullish (factor={self.optimal_factor:.1f})',
            'atr': atr,
            'metadata': {
                'optimal_factor': self.optimal_factor,
                'cluster_performance': self.cluster_performance,
                'cluster_choice': self.config.cluster_choice,
                'st_level': st_level,
                'volume_ok': True
            }
        }
    
    elif previous_trend == 1 and current_trend == 0:
        # Bearish signal
        signal = {
            'type': 'SELL',
            'price': current_price,
            'stop_loss': st_level,
            'take_profit': current_price - (self.config.tp_multiplier * atr),
            'confidence': min(100, self.cluster_performance * 10) if self.cluster_performance else 50,
            'reason': f'SuperTrend bearish (factor={self.optimal_factor:.1f})',
            'atr': atr,
            'metadata': {
                'optimal_factor': self.optimal_factor,
                'cluster_performance': self.cluster_performance,
                'cluster_choice': self.config.cluster_choice,
                'st_level': st_level,
                'volume_ok': True
            }
        }
    
    return signal
```

### Step 4: Keep SuperTrend-Specific Methods (1 hour)
- calculate_supertrends()
- perform_clustering()
- check_volume_condition()
- update_trailing_stop()

### Step 5: Add Hooks (30 min)
```python
def hook_post_signal_generation(self, signal: Optional[Dict]) -> Optional[Dict]:
    """Log ML optimization details"""
    if signal:
        self.logger.info(f"ML Factor: {self.optimal_factor:.2f}")
        self.logger.info(f"Performance: {self.cluster_performance:.4f}")
    return signal

def hook_post_cycle(self, cycle_data: Dict):
    """Log clustering status"""
    if self.optimal_factor:
        self.logger.debug(f"Using factor: {self.optimal_factor:.2f} ({self.config.cluster_choice})")
```

### Step 6: Testing (2 hours)
- Create test script
- Compare with original
- Validate ML optimization
- Test with real MT5 data

---

##  Code Reduction Estimate

### Before (Original):
```
Total lines: 670
Common functionality: ~350 lines (will inherit from base)
SuperTrend-specific: ~320 lines (keep)
```

### After (Refactored):
```
Config: ~50 lines
SuperTrend-specific logic: ~320 lines
Hooks: ~20 lines
Total: ~390 lines
```

**Expected Reduction**: ~280 lines (-42%)

---

##  Success Criteria

1.  SuperTrendBot inherits from BaseTradingBot
2.  All ML features preserved (K-means, multi-factor)
3.  calculate_indicators() implements SuperTrend logic
4.  generate_signal() uses optimal factor
5.  All SuperTrend-specific methods working
6.  Volume condition filtering working
7.  Trailing stop logic preserved
8.  Crypto support maintained
9.  Tests pass with real data
10.  Code reduction achieved (-40%+)

---

##  Key Differences from ICTBot

| Aspect | ICTBot | SuperTrendBot |
|--------|--------|---------------|
| **Core Logic** | Order Blocks, FVGs, Market Structure | Multi-factor SuperTrend |
| **ML Component** | None | K-means clustering |
| **Optimization** | None | Factor selection via clustering |
| **Indicators** | Price action based | ATR-based with volatility adjustment |
| **Complexity** | Medium | High (ML + multiple factors) |
| **State** | order_blocks, fvgs, market_structure | supertrends dict, optimal_factor |

---

##  Implementation Steps

### Today's Session:
1.  Analyze current SuperTrendBot
2.  Create refactoring plan
3. ⏳ Implement SuperTrendConfig
4. ⏳ Implement SuperTrendBot class
5. ⏳ Implement calculate_indicators()
6. ⏳ Implement generate_signal()

### Next Session (if needed):
7. ⏳ Keep SuperTrend-specific methods
8. ⏳ Add hooks
9. ⏳ Create tests
10. ⏳ Validate with real data

---

##  Special Considerations

### 1. ML Optimization State
- Need to cache supertrends dict
- optimal_factor must be accessible
- cluster_performance for confidence

### 2. Multiple SuperTrends
- Calculate all factors (1.0 to 5.0, step 0.5)
- Store in dict: {factor: st_dataframe}
- Select best via clustering

### 3. Volume Filtering
- Additional entry condition
- Check before generating signal
- Part of signal metadata

### 4. Trailing Stop
- Different from base implementation
- Uses SuperTrend levels
- Needs special handling

---

##  Notes

- SuperTrendBot is MORE COMPLEX than ICTBot due to ML
- Need to preserve all clustering logic
- Factor optimization is core feature
- Testing will be critical

---

**Ready to start implementation!** 

---

*Planning completed: October 23, 2025*  
*Next: Begin implementation*
