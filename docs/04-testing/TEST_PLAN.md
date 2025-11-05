#  Comprehensive Test Plan - QuantumTrader MT5

**Version**: 1.0  
**Date**: November 5, 2025  
**Author**: Tran Trong Hieu (@thales1020)  
**Purpose**: Complete testing strategy for entire trading system

---

##  Test Objectives

### Primary Goals
1. **Functional Correctness**: Verify all features work as designed
2. **Performance Validation**: Ensure system meets speed/memory requirements
3. **Integration Testing**: Validate component interactions
4. **Regression Prevention**: Catch bugs before production
5. **Documentation Compliance**: Verify code matches specs

### Success Criteria
-  90%+ code coverage
-  All critical paths tested
-  Zero high-priority bugs
-  Performance benchmarks met
-  All integrations validated

---

##  Test Scope

### Modules to Test

#### 1. **Core Module** (`core/`)
- `base_bot.py` - Base trading bot functionality
- `config_manager.py` - Configuration loading/validation
- `strategy_registry.py` - Strategy registration system
- `performance_monitor.py` - Performance tracking
- `ict_bot.py` - ICT strategy implementation
- `supertrend_bot.py` - SuperTrend strategy implementation

#### 2. **Engines Module** (`engines/`)
- `backtest_engine.py` - Backtesting framework
- `ict_backtest_engine.py` - ICT-specific backtest
- `paper_trading_broker_api.py` - Paper trading broker  (DONE)
- `database_manager.py` - Database operations
- `supabase_database.py` - Supabase integration

#### 3. **Utils Module** (`utils/`)
- Data fetchers
- Logging utilities
- Helper functions
- Validators

#### 4. **Scripts** (`scripts/`)
- Runner scripts
- Backtest scripts
- Deployment scripts

---

##  Test Categories

### 1. Unit Tests
**Purpose**: Test individual functions/methods in isolation

**Coverage**:
- Function logic correctness
- Edge cases
- Error handling
- Input validation
- Return values

**Tools**: `pytest`, `pytest-mock`

### 2. Integration Tests
**Purpose**: Test component interactions

**Coverage**:
- Bot + Engine integration
- Database + Bot integration
- MT5 + Bot integration
- Config + All modules

**Tools**: `pytest`, `pytest-integration`

### 3. End-to-End Tests
**Purpose**: Test complete workflows

**Workflows**:
- Full backtest cycle
- Paper trading session
- Live trading cycle
- Strategy deployment

**Tools**: `pytest`, `selenium` (for dashboard)

### 4. Performance Tests
**Purpose**: Validate speed and resource usage

**Metrics**:
- Backtest speed (bars/second)
- Memory usage
- Database query time
- Signal generation latency

**Tools**: `pytest-benchmark`, `memory_profiler`

### 5. Regression Tests
**Purpose**: Ensure fixes don't break existing functionality

**Coverage**:
- All previously fixed bugs
- Critical user workflows
- API contract compliance

**Tools**: `pytest`, snapshot testing

---

##  Test Matrix

### Core Module Tests

| Component | Unit Tests | Integration | E2E | Performance | Priority |
|-----------|-----------|-------------|-----|-------------|----------|
| `base_bot.py` |  |  |  |  | HIGH |
| `config_manager.py` |  |  | - | - | HIGH |
| `strategy_registry.py` |  |  | - | - | MEDIUM |
| `performance_monitor.py` |  | - | - |  | MEDIUM |
| `ict_bot.py` |  |  |  |  | HIGH |
| `supertrend_bot.py` |  |  |  |  | HIGH |

### Engines Module Tests

| Component | Unit Tests | Integration | E2E | Performance | Priority |
|-----------|-----------|-------------|-----|-------------|----------|
| `backtest_engine.py` |  |  |  |  | HIGH |
| `ict_backtest_engine.py` |  |  |  |  | HIGH |
| `paper_trading_broker_api.py` |  |  |  | - | HIGH |
| `database_manager.py` |  |  | - |  | HIGH |
| `supabase_database.py` |  |  | - | - | MEDIUM |

### Utils Module Tests

| Component | Unit Tests | Integration | E2E | Performance | Priority |
|-----------|-----------|-------------|-----|-------------|----------|
| Data fetchers |  |  | - |  | MEDIUM |
| Logging utils |  | - | - | - | LOW |
| Validators |  | - | - | - | MEDIUM |
| Helpers |  | - | - | - | LOW |

---

##  Critical Test Scenarios

### Scenario 1: Complete Backtest Workflow
**Description**: Run full backtest from data fetch to report  
**Steps**:
1. Initialize bot with config
2. Fetch historical data
3. Calculate indicators
4. Generate signals
5. Execute trades (simulated)
6. Calculate P&L
7. Generate report

**Expected**: 
- All trades executed correctly
- P&L matches manual calculation
- Report generated successfully

**Priority**:  CRITICAL

---

### Scenario 2: Paper Trading Session
**Description**: Complete paper trading cycle  
**Steps**:
1. Start paper trading broker
2. Submit order with SL/TP
3. Monitor position
4. Hit SL/TP trigger
5. Auto-close position
6. Verify P&L calculation
7. Check database record

**Expected**:
- Order  Position correctly
- SL/TP auto-close works
- P&L accurate
- Database updated

**Priority**:  CRITICAL

---

### Scenario 3: Strategy Comparison
**Description**: Compare ICT vs SuperTrend  
**Steps**:
1. Run both on same data
2. Compare signals
3. Compare performance
4. Validate metrics

**Expected**:
- Both produce valid signals
- Performance metrics accurate
- No crashes/errors

**Priority**:  MEDIUM

---

### Scenario 4: Multi-Symbol Backtest
**Description**: Test across multiple pairs  
**Steps**:
1. Configure 5+ symbols
2. Run parallel backtests
3. Aggregate results
4. Generate comparison report

**Expected**:
- All symbols process correctly
- No memory leaks
- Results aggregated properly

**Priority**:  LOW

---

### Scenario 5: Database Stress Test
**Description**: Heavy database operations  
**Steps**:
1. Insert 10,000 trades
2. Query performance
3. Update operations
4. Delete operations

**Expected**:
- No data loss
- Query time < 100ms
- No deadlocks

**Priority**:  MEDIUM

---

##  Detailed Test Cases

### Test Suite 1: Core - BaseTradingBot

**File**: `tests/test_base_bot.py`

```python
# Test cases:
1. test_init_with_valid_config()
2. test_init_with_invalid_config()
3. test_connect_to_mt5()
4. test_connect_failure()
5. test_fetch_data()
6. test_calculate_indicators()
7. test_generate_signal()
8. test_execute_trade()
9. test_update_positions()
10. test_close_position()
11. test_calculate_lot_size()
12. test_risk_management()
13. test_error_handling()
14. test_logging()
15. test_cleanup()
```

**Priority**: HIGH  
**Estimated Time**: 4 hours

---

### Test Suite 2: Core - ConfigManager

**File**: `tests/test_config_manager.py`

```python
# Test cases:
1. test_load_valid_json()
2. test_load_invalid_json()
3. test_missing_config_file()
4. test_validate_required_fields()
5. test_default_values()
6. test_symbol_config()
7. test_account_config()
8. test_backtest_config()
9. test_global_settings()
10. test_config_update()
```

**Priority**: HIGH  
**Estimated Time**: 2 hours

---

### Test Suite 3: Core - StrategyRegistry

**File**: `tests/test_strategy_registry.py`

```python
# Test cases:
1. test_register_strategy()
2. test_duplicate_registration()
3. test_get_strategy()
4. test_strategy_not_found()
5. test_list_strategies()
6. test_get_metadata()
7. test_create_bot()
8. test_discover_strategies()
9. test_decorator_registration()
10. test_factory_pattern()
```

**Priority**: MEDIUM  
**Estimated Time**: 3 hours

---

### Test Suite 4: Engines - BacktestEngine

**File**: `tests/test_backtest_engine.py`

```python
# Test cases:
1. test_init_engine()
2. test_load_historical_data()
3. test_prepare_data()
4. test_calculate_supertrend()
5. test_generate_signal()
6. test_open_position()
7. test_update_position()
8. test_close_position()
9. test_sl_hit()
10. test_tp_hit()
11. test_dual_orders()
12. test_pnl_calculation()
13. test_equity_curve()
14. test_performance_metrics()
15. test_report_generation()
```

**Priority**: HIGH  
**Estimated Time**: 6 hours

---

### Test Suite 5: Engines - ICTBacktestEngine

**File**: `tests/test_ict_backtest_engine.py`

```python
# Test cases:
1. test_init_ict_engine()
2. test_order_block_detection()
3. test_fvg_detection()
4. test_market_structure()
5. test_liquidity_sweep()
6. test_signal_generation()
7. test_trade_execution()
8. test_position_management()
9. test_performance_tracking()
10. test_report_generation()
```

**Priority**: HIGH  
**Estimated Time**: 5 hours

---

### Test Suite 6: Engines - PaperTradingBrokerAPI 

**File**: `test_paper_trading_fixes.py` (EXISTS)

```python
# Test cases (COMPLETED):
1.  test_sl_tp_extraction()
2.  test_stop_loss_trigger()
3.  test_take_profit_trigger()
4.  test_pnl_calculation()
```

**Priority**: HIGH  
**Status**:  COMPLETE

---

### Test Suite 7: Engines - DatabaseManager

**File**: `tests/test_database_manager.py`

```python
# Test cases:
1. test_init_database()
2. test_create_tables()
3. test_insert_trade()
4. test_update_trade()
5. test_delete_trade()
6. test_get_trade()
7. test_get_all_trades()
8. test_query_performance()
9. test_transaction_rollback()
10. test_connection_pool()
```

**Priority**: HIGH  
**Estimated Time**: 4 hours

---

### Test Suite 8: Integration - Bot + Engine

**File**: `tests/integration/test_bot_engine_integration.py`

```python
# Test cases:
1. test_supertrend_bot_with_backtest_engine()
2. test_ict_bot_with_backtest_engine()
3. test_config_propagation()
4. test_data_flow()
5. test_signal_to_trade()
6. test_error_propagation()
```

**Priority**: HIGH  
**Estimated Time**: 3 hours

---

### Test Suite 9: Integration - Database Integration

**File**: `tests/integration/test_database_integration.py`

```python
# Test cases:
1. test_bot_database_integration()
2. test_trade_persistence()
3. test_position_tracking()
4. test_performance_logging()
5. test_concurrent_access()
```

**Priority**: MEDIUM  
**Estimated Time**: 2 hours

---

### Test Suite 10: End-to-End - Complete Workflows

**File**: `tests/e2e/test_complete_workflows.py`

```python
# Test cases:
1. test_complete_backtest_workflow()
2. test_complete_paper_trading_workflow()
3. test_strategy_deployment_workflow()
4. test_multi_symbol_workflow()
5. test_report_generation_workflow()
```

**Priority**: HIGH  
**Estimated Time**: 4 hours

---

##  Test Execution Plan

### Phase 1: Unit Tests (Week 1)
**Duration**: 5 days  
**Focus**: Individual component testing

**Day 1-2**: Core module tests
- base_bot.py
- config_manager.py
- strategy_registry.py

**Day 3-4**: Engines module tests
- backtest_engine.py
- ict_backtest_engine.py
- database_manager.py

**Day 5**: Utils module tests
- All utility functions

**Deliverable**: Unit test suite with 80%+ coverage

---

### Phase 2: Integration Tests (Week 2)
**Duration**: 3 days  
**Focus**: Component interaction testing

**Day 1**: Bot + Engine integration
**Day 2**: Database integration
**Day 3**: Config + All modules

**Deliverable**: Integration test suite

---

### Phase 3: E2E Tests (Week 2)
**Duration**: 2 days  
**Focus**: Complete workflow testing

**Day 1**: Backtest + Paper trading workflows
**Day 2**: Multi-symbol + Reporting workflows

**Deliverable**: E2E test suite

---

### Phase 4: Performance Tests (Week 3)
**Duration**: 2 days  
**Focus**: Speed and resource validation

**Day 1**: Backtest performance
**Day 2**: Database performance

**Deliverable**: Performance benchmarks

---

### Phase 5: Regression Tests (Week 3)
**Duration**: 1 day  
**Focus**: Verify all fixes remain fixed

**Day 1**: Run all previous bug fix tests

**Deliverable**: Regression test suite

---

##  Coverage Goals

### Code Coverage Targets
- **Critical modules**: 95%+ (core, engines)
- **Important modules**: 85%+ (utils, scripts)
- **Other modules**: 70%+
- **Overall project**: 85%+

### Test Type Distribution
- Unit tests: 60%
- Integration tests: 25%
- E2E tests: 10%
- Performance tests: 5%

---

##  Testing Tools

### Required Tools
```bash
# Test framework
pytest==7.4.0
pytest-cov==4.1.0
pytest-mock==3.11.1
pytest-benchmark==4.0.0

# Code coverage
coverage==7.3.0
pytest-html==3.2.0

# Performance
memory-profiler==0.61.0
line-profiler==4.0.0

# Mocking
pytest-mock==3.11.1
responses==0.23.0

# Database testing
pytest-postgresql==5.0.0
```

### Installation
```bash
pip install -r requirements-test.txt
```

---

##  Test Metrics

### Track These Metrics
1. **Test Count**: Total number of tests
2. **Pass Rate**: % tests passing
3. **Coverage**: Code coverage %
4. **Duration**: Test suite runtime
5. **Flakiness**: Tests failing intermittently

### Reporting
- Daily: Test results email
- Weekly: Coverage report
- Sprint: Full test metrics dashboard

---

##  Test Environments

### 1. Local Development
- Developer machine
- SQLite database
- Mock MT5 connection
- Fast feedback loop

### 2. Staging
- VPS server
- PostgreSQL database
- Real MT5 demo account
- Integration testing

### 3. Production-like
- Production VPS
- Production database (read-only)
- Live MT5 demo account
- Final validation

---

##  Test Data

### Data Requirements
1. **Historical Data**: 
   - EURUSD, GBPUSD, XAUUSD
   - H1, H4, D1 timeframes
   - 2+ years of data

2. **Mock Data**:
   - Edge case scenarios
   - Error conditions
   - Extreme market conditions

3. **Real Data**:
   - Live tick data (demo)
   - Real account info (sanitized)
   - Production configs (anonymized)

---

##  Risk Areas

### High-Risk Components
1. **Order Execution**: Money at stake
2. **P&L Calculation**: Financial accuracy critical
3. **Database**: Data integrity
4. **MT5 Connection**: External dependency
5. **SL/TP Logic**: Risk management

### Mitigation
- Extra test coverage (95%+)
- Manual verification
- Staged rollout
- Monitoring/alerts

---

##  Test Checklist

### Before Each Release
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Code coverage  85%
- [ ] No critical bugs
- [ ] Performance benchmarks met
- [ ] Regression tests pass
- [ ] Documentation updated
- [ ] Test report generated
- [ ] Stakeholder approval

---

##  Success Metrics

### Project-Level KPIs
-  0 critical bugs in production
-  95%+ test pass rate
-  85%+ code coverage
-  < 10 min test suite runtime
-  100% high-priority scenarios tested

### Quality Gates
- **Bronze**: 70% coverage, basic tests
- **Silver**: 80% coverage, integration tests
- **Gold**: 85% coverage, E2E tests
- **Platinum**: 90% coverage, performance tests

---

##  For Testers

### Getting Started
1. Read this test plan
2. Setup test environment
3. Review existing tests
4. Start with unit tests
5. Progress to integration
6. Finish with E2E

### Best Practices
- Write clear test names
- Use AAA pattern (Arrange, Act, Assert)
- Mock external dependencies
- Clean up after tests
- Document edge cases
- Keep tests independent

### Test Naming Convention
```python
def test_<component>_<scenario>_<expected_result>():
    # Example:
    # test_base_bot_invalid_config_raises_error()
    # test_backtest_engine_sl_hit_closes_position()
```

---

##  Support

**Test Lead**: Trn Trng Hiu (@thales1020)  
**Questions**: Create issue in GitHub  
**CI/CD**: Jenkins pipeline (coming soon)

---

**Last Updated**: November 5, 2025  
**Next Review**: November 12, 2025

