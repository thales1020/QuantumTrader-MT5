# Strategy Module - Test Plan

**Project**: QuantumTrader MT5  
**Module**: Strategy Module (Use Cases UC16-UC19)  
**Version**: 1.0  
**Date**: November 5, 2025  
**Tester**: Independent Testing Team  
**Reference**: `docs/uml_diagrams/Strategy_Module_Detail.puml`

---

## 📋 Table of Contents

1. [Test Scope](#test-scope)
2. [Test Strategy](#test-strategy)
3. [Create Strategy Tests (UC16)](#create-strategy-tests-uc16)
4. [Test Strategy Tests (UC17)](#test-strategy-tests-uc17)
5. [Deploy Strategy Tests (UC18)](#deploy-strategy-tests-uc18)
6. [Update Strategy Tests (UC19)](#update-strategy-tests-uc19)
7. [Integration Tests](#integration-tests)
8. [Test Deliverables](#test-deliverables)

---

## 🎯 Test Scope

### In Scope
- ✅ Strategy creation workflow (UC16)
- ✅ Entry/Exit rules definition
- ✅ Risk management configuration
- ✅ Indicator setup
- ✅ Strategy testing (unit tests, backtest, signal validation)
- ✅ Strategy deployment and registration
- ✅ Strategy updates and version control
- ✅ Supported strategies: SMA Crossover, ICT, SuperTrend, Custom

### Out of Scope
- ❌ Live trading execution (covered in Paper Trading tests)
- ❌ UI/Frontend testing
- ❌ Third-party indicator libraries
- ❌ Strategy marketplace features

---

## 📊 Test Strategy

### Test Levels
1. **Unit Tests**: Individual strategy components (entry rules, exit rules, risk management)
2. **Integration Tests**: Strategy system integration
3. **Functional Tests**: Use case workflows (UC16-UC19)
4. **Performance Tests**: Strategy execution speed, backtest performance

### Coverage Target
- **Critical Paths**: 100%
- **Important Paths**: 95%
- **Error Handling**: 90%

---

## 🔨 Create Strategy Tests (UC16)

### UC16.1: Define Entry Rules
**Priority**: CRITICAL  
**Objective**: Verify entry rules can be defined correctly

**Test Steps**:
```python
1. Developer creates new strategy
2. Define entry conditions:
   - Indicator conditions (e.g., SMA cross above)
   - Price conditions (e.g., close > open)
   - Time conditions (e.g., only during London session)
3. Validate entry logic syntax
4. Save entry rules
```

**Expected Results**:
- ✅ Entry rules saved successfully
- ✅ Syntax validation passes
- ✅ Multiple conditions supported (AND/OR logic)
- ✅ Rules retrievable for editing

**Test Data**:
```python
entry_rules = {
    'conditions': [
        {'type': 'indicator', 'indicator': 'SMA_20', 'operator': '>', 'value': 'SMA_50'},
        {'type': 'price', 'indicator': 'close', 'operator': '>', 'value': 'open'},
    ],
    'logic': 'AND'  # All conditions must be true
}
```

**Pass Criteria**: Entry rules stored and validated

---

### UC16.2: Define Exit Rules
**Priority**: CRITICAL  
**Objective**: Verify exit rules (TP/SL) can be defined

**Test Steps**:
```python
1. Define Take Profit conditions:
   - Fixed pips (e.g., 100 pips)
   - Percentage (e.g., 2% of entry)
   - Indicator-based (e.g., when RSI > 70)
2. Define Stop Loss conditions:
   - Fixed pips (e.g., 50 pips)
   - ATR-based (e.g., 2x ATR)
   - Trailing stop
3. Validate exit logic
4. Save exit rules
```

**Expected Results**:
- ✅ TP rules saved
- ✅ SL rules saved
- ✅ Multiple exit strategies supported
- ✅ Trailing stop configurable

**Test Data**:
```python
exit_rules = {
    'take_profit': {
        'type': 'fixed_pips',
        'value': 100
    },
    'stop_loss': {
        'type': 'atr_based',
        'multiplier': 2
    },
    'trailing_stop': {
        'enabled': True,
        'trigger_pips': 50,
        'trail_pips': 20
    }
}
```

**Pass Criteria**: Exit rules validated and stored

---

### UC16.3: Set Risk Management
**Priority**: CRITICAL  
**Objective**: Verify risk management parameters configured

**Test Steps**:
```python
1. Set max risk per trade (e.g., 2% of balance)
2. Set max daily loss (e.g., 5%)
3. Set position sizing method:
   - Fixed lot size
   - Percentage of balance
   - Kelly Criterion
4. Set max concurrent positions
5. Validate risk parameters
```

**Expected Results**:
- ✅ Risk percentage validated (0-100%)
- ✅ Position sizing calculated correctly
- ✅ Max positions enforced
- ✅ Daily loss limit enforced

**Test Data**:
```python
risk_management = {
    'max_risk_per_trade': 2.0,  # 2% of balance
    'max_daily_loss': 5.0,       # 5% max drawdown per day
    'position_sizing': 'percentage',
    'max_concurrent_positions': 3
}
```

**Pass Criteria**: Risk management active and enforced

---

### UC16.4: Configure Indicators
**Priority**: HIGH  
**Objective**: Verify indicators can be added and configured

**Test Steps**:
```python
1. Add indicator to strategy (e.g., SMA)
2. Configure parameters:
   - SMA period: 20
   - SMA type: Simple
   - Applied to: Close price
3. Add multiple indicators (SMA, RSI, MACD)
4. Validate indicator calculations
```

**Expected Results**:
- ✅ Indicator added successfully
- ✅ Parameters validated
- ✅ Multiple indicators supported
- ✅ Indicator values calculated correctly

**Test Data**:
```python
indicators = [
    {'name': 'SMA_20', 'type': 'SMA', 'period': 20, 'applied_to': 'close'},
    {'name': 'SMA_50', 'type': 'SMA', 'period': 50, 'applied_to': 'close'},
    {'name': 'RSI', 'type': 'RSI', 'period': 14}
]
```

**Pass Criteria**: Indicators configured and operational

---

### UC16.5: Strategy Creation - Complete
**Priority**: CRITICAL  
**Objective**: Test complete strategy creation workflow

**Test Steps**:
```python
1. Create new strategy "SMA_Crossover_V1"
2. Define entry rules (SMA cross)
3. Define exit rules (TP/SL)
4. Set risk management (2% per trade)
5. Configure indicators (SMA 20, SMA 50)
6. Save strategy
7. Verify strategy file created
```

**Expected Results**:
- ✅ Strategy saved to file system
- ✅ Strategy metadata stored (name, version, author)
- ✅ All components present
- ✅ Strategy ready for testing

**Pass Criteria**: Complete strategy created successfully

---

## 🧪 Test Strategy Tests (UC17)

### UC17.1: Run Unit Tests
**Priority**: HIGH  
**Objective**: Verify strategy unit tests execute correctly

**Test Steps**:
```python
1. Load strategy for testing
2. Run unit tests:
   - Test entry rule logic
   - Test exit rule logic
   - Test risk calculations
   - Test indicator calculations
3. Verify all tests pass
4. Generate test report
```

**Expected Results**:
- ✅ All unit tests executed
- ✅ Test coverage > 80%
- ✅ No critical failures
- ✅ Report generated

**Test Data**:
```python
test_cases = [
    {'name': 'test_entry_sma_cross', 'expected': True},
    {'name': 'test_exit_tp_reached', 'expected': True},
    {'name': 'test_risk_2percent', 'expected': 0.02}
]
```

**Pass Criteria**: Unit tests pass with >80% coverage

---

### UC17.2: Run Backtest
**Priority**: CRITICAL  
**Objective**: Verify strategy backtesting functionality

**Test Steps**:
```python
1. Load historical data (EURUSD 2020-2024)
2. Run backtest with strategy
3. Calculate metrics:
   - Total trades
   - Win rate
   - Net P&L
   - Max drawdown
   - Sharpe ratio
4. Verify backtest completes successfully
```

**Expected Results**:
- ✅ Backtest completes without errors
- ✅ All metrics calculated
- ✅ Trade history generated
- ✅ Equity curve plotted

**Test Data**:
```python
backtest_config = {
    'symbol': 'EURUSD',
    'timeframe': 'H1',
    'start_date': '2020-01-01',
    'end_date': '2024-12-31',
    'initial_balance': 10000
}
```

**Expected Metrics**:
```python
expected_results = {
    'total_trades': '>= 100',
    'win_rate': '> 40%',
    'max_drawdown': '< 30%'
}
```

**Pass Criteria**: Backtest executes and produces valid metrics

---

### UC17.3: Validate Signals
**Priority**: CRITICAL  
**Objective**: Verify strategy generates correct signals

**Test Steps**:
```python
1. Load test market data
2. Run strategy signal generation
3. Verify signals:
   - BUY signal when SMA_20 crosses above SMA_50
   - SELL signal when SMA_20 crosses below SMA_50
   - No signal when no cross detected
4. Check signal timing accuracy
```

**Expected Results**:
- ✅ BUY signals generated correctly
- ✅ SELL signals generated correctly
- ✅ No false signals
- ✅ Signal timestamps accurate

**Test Data**:
```python
# Mock data with known crossover
test_data = [
    {'time': '2024-01-01 10:00', 'SMA_20': 1.0950, 'SMA_50': 1.1000, 'expected': None},
    {'time': '2024-01-01 11:00', 'SMA_20': 1.1010, 'SMA_50': 1.1000, 'expected': 'BUY'},
    {'time': '2024-01-01 12:00', 'SMA_20': 1.0990, 'SMA_50': 1.1000, 'expected': 'SELL'}
]
```

**Pass Criteria**: Signals match expected outcomes

---

### UC17.4: Check Performance
**Priority**: MEDIUM  
**Objective**: Verify strategy performance metrics

**Test Steps**:
```python
1. Run strategy on test dataset
2. Measure:
   - Signal generation speed (< 100ms)
   - Backtest execution time (< 60s for 1 year data)
   - Memory usage (< 500MB)
3. Compare against benchmarks
```

**Expected Results**:
- ✅ Signal generation: < 100ms per bar
- ✅ Backtest: < 60s for 1 year H1 data
- ✅ Memory: < 500MB
- ✅ No memory leaks

**Pass Criteria**: Performance within acceptable limits

---

## 🚀 Deploy Strategy Tests (UC18)

### UC18.1: Package Strategy
**Priority**: HIGH  
**Objective**: Verify strategy packaging for deployment

**Test Steps**:
```python
1. Package strategy files:
   - strategy.py (main code)
   - config.json (parameters)
   - README.md (documentation)
2. Create strategy archive (.zip)
3. Verify archive contents
4. Check file integrity
```

**Expected Results**:
- ✅ Archive created successfully
- ✅ All required files present
- ✅ No missing dependencies
- ✅ Archive size reasonable (< 10MB)

**Pass Criteria**: Strategy packaged correctly

---

### UC18.2: Register in System
**Priority**: CRITICAL  
**Objective**: Verify strategy registration in system

**Test Steps**:
```python
1. Call StrategyRegistry.register(strategy)
2. Verify strategy added to registry
3. Check strategy metadata:
   - Name
   - Version
   - Author
   - Created date
4. Verify strategy retrievable by name
```

**Expected Results**:
- ✅ Strategy registered successfully
- ✅ Metadata stored correctly
- ✅ Strategy ID generated
- ✅ Registry updated

**Test Data**:
```python
strategy_metadata = {
    'name': 'SMA_Crossover_V1',
    'version': '1.0.0',
    'author': 'Developer',
    'description': 'SMA 20/50 crossover strategy',
    'created_date': '2025-11-05'
}
```

**Pass Criteria**: Strategy appears in registry

---

### UC18.3: Set Parameters
**Priority**: HIGH  
**Objective**: Verify runtime parameters can be set

**Test Steps**:
```python
1. Load deployed strategy
2. Set runtime parameters:
   - Symbol: EURUSD
   - Timeframe: H1
   - Lot size: 0.1
   - Max positions: 3
3. Validate parameters
4. Save parameter configuration
```

**Expected Results**:
- ✅ Parameters accepted
- ✅ Validation passes
- ✅ Parameters persisted
- ✅ Strategy ready to run

**Test Data**:
```python
runtime_params = {
    'symbol': 'EURUSD',
    'timeframe': 'H1',
    'lot_size': 0.1,
    'max_positions': 3,
    'trading_hours': '00:00-24:00'
}
```

**Pass Criteria**: Parameters configured successfully

---

### UC18.4: Activate Strategy
**Priority**: CRITICAL  
**Objective**: Verify strategy activation for live/paper trading

**Test Steps**:
```python
1. Set strategy status to 'ACTIVE'
2. Verify strategy starts receiving market data
3. Check strategy processes data correctly
4. Verify signals can be generated
5. Confirm trading mode (paper/live)
```

**Expected Results**:
- ✅ Strategy status = 'ACTIVE'
- ✅ Market data received
- ✅ Strategy analyzing data
- ✅ Ready to generate signals
- ✅ Trading mode confirmed

**Pass Criteria**: Strategy activated and operational

---

## 🔄 Update Strategy Tests (UC19)

### UC19.1: Modify Logic
**Priority**: HIGH  
**Objective**: Verify strategy logic can be updated

**Test Steps**:
```python
1. Load existing strategy (SMA_Crossover_V1)
2. Modify entry rules:
   - Change SMA periods from 20/50 to 10/30
3. Update exit rules:
   - Change TP from 100 pips to 150 pips
4. Save modifications
5. Verify changes applied
```

**Expected Results**:
- ✅ Changes saved successfully
- ✅ Original version preserved
- ✅ New logic validated
- ✅ Strategy ready for re-testing

**Pass Criteria**: Logic updated correctly

---

### UC19.2: Test Changes
**Priority**: CRITICAL  
**Objective**: Verify updated strategy tested before deployment

**Test Steps**:
```python
1. Run unit tests on updated strategy
2. Run backtest with new parameters
3. Compare results with V1:
   - V1: Win rate 45%, Drawdown 20%
   - V2: Win rate 48%, Drawdown 18%
4. Validate improvements
```

**Expected Results**:
- ✅ All tests pass
- ✅ Backtest completes
- ✅ Comparison report generated
- ✅ Changes validated

**Pass Criteria**: Updated strategy passes all tests

---

### UC19.3: Version Control
**Priority**: HIGH  
**Objective**: Verify strategy versioning system

**Test Steps**:
```python
1. Create new version (V2)
2. Verify version history:
   - V1: 2025-11-01, SMA 20/50
   - V2: 2025-11-05, SMA 10/30
3. Check changelog generated
4. Verify rollback capability
```

**Expected Results**:
- ✅ New version created (V2)
- ✅ Version history maintained
- ✅ Changelog updated
- ✅ Can rollback to V1 if needed

**Test Data**:
```python
version_history = [
    {'version': '1.0.0', 'date': '2025-11-01', 'changes': 'Initial release'},
    {'version': '2.0.0', 'date': '2025-11-05', 'changes': 'Updated SMA periods'}
]
```

**Pass Criteria**: Versioning system working correctly

---

### UC19.4: Redeploy
**Priority**: CRITICAL  
**Objective**: Verify updated strategy can be redeployed

**Test Steps**:
```python
1. Deactivate V1 strategy
2. Package V2 strategy
3. Register V2 in system
4. Set V2 parameters
5. Activate V2
6. Verify V2 running correctly
```

**Expected Results**:
- ✅ V1 deactivated gracefully
- ✅ V2 deployed successfully
- ✅ No data loss
- ✅ V2 operational

**Pass Criteria**: Redeploy successful, V2 running

---

## 🔗 Integration Tests

### INT_1: Strategy Lifecycle - Complete
**Priority**: CRITICAL  
**Objective**: Test complete strategy lifecycle (Create → Test → Deploy → Update)

**Test Steps**:
```python
1. CREATE: Create SMA_Crossover_V1
2. TEST: Run unit tests and backtest
3. DEPLOY: Register and activate V1
4. RUN: Strategy processes data for 1 week (simulated)
5. UPDATE: Modify to V2
6. RETEST: Test V2 improvements
7. REDEPLOY: Activate V2
8. VERIFY: V2 operational
```

**Expected Results**:
- ✅ All lifecycle stages complete
- ✅ No errors or data loss
- ✅ Smooth transitions between versions
- ✅ Strategy operational end-to-end

**Pass Criteria**: Complete lifecycle successful

---

### INT_2: Multiple Strategies Concurrent
**Priority**: HIGH  
**Objective**: Test multiple strategies running simultaneously

**Test Steps**:
```python
1. Deploy 3 strategies:
   - SMA_Crossover
   - ICT_Strategy
   - SuperTrend
2. Activate all 3
3. Verify each processes data independently
4. Check no resource conflicts
5. Verify signals from each strategy
```

**Expected Results**:
- ✅ All 3 strategies active
- ✅ Independent signal generation
- ✅ No performance degradation
- ✅ No memory conflicts

**Pass Criteria**: Multi-strategy deployment works

---

### INT_3: Strategy Registry Consistency
**Priority**: HIGH  
**Objective**: Verify registry maintains data integrity

**Test Steps**:
```python
1. Register 5 different strategies
2. Update 2 strategies to V2
3. Delete 1 strategy
4. Verify registry state:
   - 4 strategies total
   - Version history intact
   - No orphaned data
5. Query strategies by name, version, author
```

**Expected Results**:
- ✅ Registry count correct (4)
- ✅ All metadata accurate
- ✅ Queries return correct results
- ✅ No data corruption

**Pass Criteria**: Registry integrity maintained

---

### INT_4: Custom Strategy Support
**Priority**: MEDIUM  
**Objective**: Verify custom user strategies supported

**Test Steps**:
```python
1. Developer creates custom strategy (not SMA/ICT/SuperTrend)
2. Custom strategy inherits from BaseStrategy
3. Implement required methods:
   - analyze()
   - on_tick()
   - on_trade()
4. Deploy custom strategy
5. Verify it works like built-in strategies
```

**Expected Results**:
- ✅ Custom strategy accepted
- ✅ All methods functional
- ✅ Backtesting works
- ✅ Live deployment works

**Pass Criteria**: Custom strategies fully supported

---

### INT_5: Strategy Performance Under Load
**Priority**: MEDIUM  
**Objective**: Test strategy system under high load

**Test Steps**:
```python
1. Deploy 10 strategies
2. Feed 1000 bars/second to each
3. Measure:
   - Signal generation latency
   - Memory usage
   - CPU usage
4. Verify no crashes or slowdowns
```

**Expected Results**:
- ✅ Latency < 100ms per strategy
- ✅ Memory < 2GB total
- ✅ CPU < 80%
- ✅ No crashes

**Pass Criteria**: System handles load gracefully

---

## 📦 Test Deliverables

### Test Artifacts
1. ✅ Test execution report (pass/fail for all test cases)
2. ✅ Code coverage report (target: 90%+)
3. ✅ Strategy backtest reports
4. ✅ Performance benchmark results
5. ✅ Strategy registry verification report
6. ✅ Version control audit log

### Success Criteria
- **All CRITICAL tests**: 100% pass
- **All HIGH tests**: 100% pass
- **All MEDIUM tests**: 95%+ pass
- **Code coverage**: 90%+
- **Backtest performance**: < 60s for 1 year data
- **Signal generation**: < 100ms per bar

---

## 📊 Test Summary

| Category | Test Cases | Priority |
|----------|-----------|----------|
| **Create Strategy (UC16)** | 5 | CRITICAL |
| **Test Strategy (UC17)** | 4 | CRITICAL |
| **Deploy Strategy (UC18)** | 4 | CRITICAL |
| **Update Strategy (UC19)** | 4 | HIGH |
| **Integration Tests** | 5 | HIGH |
| **TOTAL** | **22** | - |

---

## 📝 Supported Strategies

### Built-in Strategies
1. **SMA Crossover**: Simple Moving Average crossover (20/50)
2. **ICT Strategy**: Inner Circle Trader methodology
3. **SuperTrend**: SuperTrend indicator-based strategy
4. **Custom**: User-defined strategies via BaseStrategy class

---

**Approval**:
- [ ] Test Plan Reviewed by QA Lead
- [ ] Test Plan Approved by Project Manager
- [ ] Ready for Test Implementation

**Next Steps**:
1. Implement unit tests based on this plan
2. Set up strategy test fixtures
3. Create backtest test data
4. Execute test suite
5. Generate coverage report
6. Fix any defects found
7. Re-test and validate

---

*End of Test Plan*
