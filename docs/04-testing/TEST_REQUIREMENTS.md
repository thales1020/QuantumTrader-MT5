#  Test Requirements Document

**Project**: QuantumTrader MT5 - Professional Algorithmic Trading Platform  
**Version**: 2.0  
**Date**: November 5, 2025  
**For**: Professional QA Engineers & Independent Testers  
**Document Owner**: Testing Team Lead

---

##  Executive Summary

### Testing Status (As of Nov 5, 2025)
- ✅ **Backtest Engine**: 58/58 tests passing (100%)
- ✅ **Paper Trading Sequence**: 49/49 tests passing (100%)
- ✅ **Strategy Module**: 22/22 tests passing (100%)
- **Total Tests**: 129/129 PASSING (100% success rate)
- **Code Coverage**: 85%+ on critical modules
- **Test Execution Time**: <5 seconds for unit tests

---

##  Tester Role & Responsibilities

### Who You Are
You are a **professional QA engineer** working on a **mission-critical financial system** that:
- Manages real money in live trading environments
- Processes thousands of trades per day
- Requires 99.9% uptime and accuracy
- Has zero tolerance for calculation errors
- Impacts client profitability directly

### Your Core Mission

1. **VERIFY FINANCIAL ACCURACY** (TOP PRIORITY)
   - Every P&L calculation must be correct to the cent
   - SL/TP execution must be precise
   - Order matching must follow exchange rules
   - Risk management must enforce limits

2. **ENSURE SYSTEM RELIABILITY**
   - Test all failure scenarios
   - Verify error recovery mechanisms
   - Validate data consistency
   - Check concurrent operation safety

3. **VALIDATE BUSINESS LOGIC**
   - Trading strategies work as designed
   - Entry/exit rules execute correctly
   - Risk parameters are enforced
   - Performance metrics are accurate

4. **MAINTAIN TEST INFRASTRUCTURE**
   - Keep test suites up to date
   - Add tests for new features
   - Refactor brittle tests
   - Monitor test execution performance

5. **DOCUMENT & COMMUNICATE**
   - Clear bug reports with reproduction steps
   - Test coverage reports
   - Risk assessments for releases
   - Go/No-Go recommendations

**Critical Mindset**: "If this fails in production, clients lose money. How do I prevent that?"

---

##  System Architecture Overview

### What You're Testing

**QuantumTrader MT5** is a **production-grade automated trading platform** consisting of:

#### Core Components
1. **Strategy Engine**
   - Multiple strategy support (SMA, ICT, SuperTrend, Custom)
   - Strategy lifecycle management (Create → Test → Deploy → Update)
   - Version control and rollback capability
   - Performance monitoring and optimization

2. **Execution Engines**
   - **Backtest Engine**: Historical simulation with tick-level accuracy
   - **Paper Trading Engine**: Real-time simulation without real money
   - **Live Trading Engine**: Real money execution via MT5

3. **Order Management System**
   - Order matching engine with realistic slippage
   - Position tracking and management
   - SL/TP automation and monitoring
   - Multi-symbol concurrent trading

4. **Risk Management**
   - Per-trade risk limits (% of account)
   - Max daily loss limits
   - Position sizing algorithms
   - Drawdown protection

5. **Data & Analytics**
   - Database layer (SQLAlchemy ORM)
   - Real-time P&L calculation
   - Performance metrics (Sharpe, win rate, drawdown)
   - Trade journal and audit trail

6. **External Integrations**
   - MetaTrader 5 broker API
   - Supabase cloud database
   - Dashboard/UI notifications

### What's Already Tested (Your Foundation)

✅ **Backtest Engine Module** - 58 tests
- Historical data loading and validation
- Indicator calculations (SMA, SuperTrend, ICT)
- Signal generation accuracy
- Trade execution simulation
- Performance metrics calculation
- Multi-strategy backtesting

✅ **Paper Trading Sequence** - 49 tests
- Session initialization and setup
- Real-time market data processing
- Order matching and execution
- Position management (open/close)
- SL/TP monitoring and auto-close
- P&L calculation and tracking
- Database persistence
- Error recovery and resilience

✅ **Strategy Module** - 22 tests
- Strategy creation workflow
- Entry/exit rule definition
- Risk management configuration
- Unit testing and validation
- Backtest integration
- Deployment and activation
- Version control and updates
- Multi-strategy orchestration

### Your Testing Focus Areas

**What Still Needs Your Attention:**

1. **Live Trading Integration** (CRITICAL - NOT YET TESTED)
   - Real MT5 connection stability
   - Order submission to real broker
   - Position synchronization
   - Error handling with real API

2. **Edge Cases & Stress Testing** (HIGH PRIORITY)
   - Network failures and reconnection
   - Database corruption recovery
   - Extreme market conditions (gaps, flash crashes)
   - High-frequency trading scenarios (1000+ trades/day)

3. **Cross-Symbol & Cross-Strategy** (MEDIUM PRIORITY)
   - Multiple currency pairs simultaneously
   - Multiple strategies on same symbol
   - Resource usage and memory leaks
   - Performance degradation over time

4. **User Workflows** (MEDIUM PRIORITY)
   - Configuration management
   - Strategy deployment process
   - Monitoring and alerting
   - Error reporting and debugging

---

##  Environment Setup Requirements

### 1. Development Environment

**Required Software:**
- **Python**: 3.11+ (exact version: 3.11.0 recommended)
- **Git**: Latest version
- **Code Editor**: VS Code with Python extension (recommended)
- **Terminal**: PowerShell (Windows) or Bash (Linux/Mac)

**Installation Steps:**
```bash
# 1. Clone repository
git clone https://github.com/thales1020/QuantumTrader-MT5.git
cd QuantumTrader-MT5

# 2. Create isolated virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source venv/bin/activate      # Linux/Mac

# 4. Verify Python version
python --version  # Should show 3.11.x

# 5. Install all dependencies
pip install -r requirements.txt

# 6. Verify pytest installation
pytest --version  # Should show 8.4.2+
```

### 2. Testing Tools & Libraries

**Already Installed (via requirements.txt):**
- `pytest==8.4.2` - Test framework
- `pytest-cov==4.1.0` - Coverage reporting
- `pytest-mock==3.11.1` - Mocking utilities
- `SQLAlchemy==2.0.23` - Database ORM
- `pandas==2.1.3` - Data analysis
- `numpy==1.26.2` - Numerical computing

**Verify Installation:**
```bash
python -m pytest --version
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
python -c "import pandas; print(pandas.__version__)"
```

### 3. MetaTrader 5 (For Integration Testing)

**Required for Live Trading Tests:**
1. Download MT5 from your broker (e.g., FTMO, IC Markets)
2. Create **DEMO account** (never use real money for testing!)
3. Note credentials:
   - Login number
   - Password
   - Server address

**Enable Algo Trading:**
- Tools → Options → Expert Advisors
- ✅ Allow automated trading
- ✅ Allow DLL imports

### 4. Configuration Files

**Setup Config:**
```bash
# 1. Copy example configurations
cp config/config.example.json config/config.json
cp config/supabase.example.json config/supabase.json

# 2. Edit config.json with your settings
# (Use your favorite editor)

# 3. For testing, use DEMO account credentials only!
```

**Config Validation:**
```python
# Run validation script
python -c "from core.config_manager import ConfigManager; cm = ConfigManager(); print('Config valid!')"
```

### 5. Database Setup

**Local SQLite (Default for Testing):**
- No setup needed
- In-memory database for tests
- Automatically created/destroyed

**Supabase (Optional - for cloud testing):**
1. Create free account at supabase.com
2. Create new project
3. Run schema: `database/supabase_schema.sql`
4. Update `config/supabase.json` with credentials

### 6. Verify Setup

**Run Health Check:**
```bash
# 1. Run all existing tests (should all pass)
python -m pytest tests/unit/ -v

# Expected output:
# ====== 129 passed in ~5 seconds ======

# 2. Check code coverage
python -m pytest tests/unit/ --cov=core --cov=engines --cov-report=term

# Expected: >85% coverage on critical modules

# 3. Verify no import errors
python -c "from core.base_bot import BaseBot; print('Imports OK')"
```

**Common Setup Issues:**

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'MetaTrader5'` | Windows only - install: `pip install MetaTrader5` |
| `ImportError: TA-Lib` | Install wheel from `data/` folder: `pip install data/ta_lib-0.6.7-cp311-cp311-win_amd64.whl` |
| `pytest: command not found` | Activate venv first: `.\venv\Scripts\Activate.ps1` |
| Tests fail on import | Run from project root, not subdirectories |

---

##  Test Deliverables & Reporting

### Required Deliverables

As a professional tester on this project, you must provide:

#### 1. Daily Test Execution Reports
**Frequency:** End of each testing day  
**Template:** See "Daily Report Template" section below  

**Must Include:**
- Tests executed (count and list)
- Pass/Fail/Skip breakdown
- Execution time
- Coverage delta (% change from yesterday)
- New bugs found (count + severity)
- Blockers identified
- Next day plan

**Submission:** Via GitHub issue with label `test-report-daily`

---

#### 2. Bug Reports (As Discovered)
**Frequency:** Immediately when found  
**Severity Classification:**

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **CRITICAL** | System crash, data loss, financial loss | <4 hours | Wrong P&L calculation causing real money loss |
| **HIGH** | Major feature broken, workaround exists | <24 hours | SL/TP not triggering in edge case |
| **MEDIUM** | Minor feature broken, no workaround | <3 days | Dashboard not updating in real-time |
| **LOW** | Cosmetic, documentation, nice-to-have | <1 week | Typo in log message |

**Required Fields:**
- Bug ID (auto-assigned by GitHub)
- Severity (use table above)
- Component (which module/file)
- Description (what's wrong)
- Reproduction steps (numbered list)
- Expected vs Actual behavior
- Environment details
- Screenshots/logs (attached)
- Suggested fix (optional but appreciated)

**Submission:** GitHub issue with label `bug` + severity label

---

#### 3. Weekly Test Summary Report
**Frequency:** End of each week (Friday)  
**Audience:** Development team + Project manager  

**Sections Required:**

**A. Test Execution Summary**
- Total tests: [X] (change from last week: +/- Y)
- Pass rate: [X]%
- Coverage: [X]% (critical modules) / [X]% (overall)
- Execution time: [X] seconds

**B. Quality Metrics**
- Bugs found this week: [X]
  - Critical: [X]
  - High: [X]
  - Medium: [X]
  - Low: [X]
- Bugs fixed this week: [X]
- Bug backlog: [X] open bugs

**C. Risk Assessment**
- **High Risk Areas**: [List modules with concerns]
- **Low Coverage Areas**: [Modules <70% coverage]
- **Technical Debt**: [Brittle tests, slow tests, flaky tests]

**D. Recommendations**
- Priority fixes needed
- Suggested test improvements
- Resource needs (if any)

**E. Sign-Off Status**
- ✅ Ready for staging
- ⚠️ Ready with minor issues
- ❌ Not ready - blockers exist

**Submission:** Email + GitHub Wiki page

---

#### 4. Release Test Report (Before Each Release)
**Frequency:** Before every production deployment  
**Criticality:** **MANDATORY** - No release without this!  

**Checklist (All Must Pass):**
- [ ] All Priority 1 tests: 100% pass (129 tests currently)
- [ ] All Priority 2 tests: 95%+ pass
- [ ] Regression suite: 100% pass
- [ ] Code coverage: ≥85% on critical modules
- [ ] No CRITICAL or HIGH severity open bugs
- [ ] All MEDIUM bugs documented with workarounds
- [ ] Performance benchmarks met:
  - [ ] Backtest: <60s for 1 year data
  - [ ] Paper trading: <100ms signal latency
  - [ ] Live trading: <500ms order execution
- [ ] Manual testing complete:
  - [ ] Demo account tested (≥50 trades)
  - [ ] Multi-symbol tested (≥3 pairs)
  - [ ] Strategy switching tested
  - [ ] Recovery from crash tested
- [ ] Documentation updated
- [ ] Deployment checklist reviewed

**Go/No-Go Decision Matrix:**

| Criteria | Go | No-Go |
|----------|-----|-------|
| Critical bugs | 0 | ≥1 |
| High bugs | ≤2 (with workarounds) | >2 or no workarounds |
| Test pass rate | ≥95% | <95% |
| Coverage | ≥85% critical modules | <85% |
| Performance | All benchmarks met | Any benchmark failed |
| Manual testing | Complete, no issues | Incomplete or issues found |

**Your Recommendation:**
- ✅ **GO**: Safe to deploy to production
- ⚠️ **GO WITH CONDITIONS**: Deploy but monitor closely, document risks
- ❌ **NO-GO**: Do not deploy, critical issues exist

**Submission:** Email to dev lead + product manager with final recommendation

---

#### 5. Test Automation & Maintenance

**Ongoing Responsibilities:**

**A. Test Suite Maintenance** (Weekly)
- Update tests for new features
- Refactor brittle tests
- Remove obsolete tests
- Improve test readability

**B. Coverage Improvement** (Bi-weekly)
- Identify untested code paths
- Write tests for low-coverage modules
- Target: 85%+ on all critical modules

**C. Performance Optimization** (Monthly)
- Profile slow tests (>5s individual test)
- Optimize test data generation
- Reduce test suite execution time
- Target: <10s for full unit test suite

**D. CI/CD Integration** (As needed)
- Ensure tests run in CI pipeline
- Fix flaky tests (non-deterministic failures)
- Configure parallel test execution
- Set up coverage reporting automation

---

##  Test Suite Catalog

### ✅ Completed Test Suites (Your Reference)

#### Suite 1: Backtest Engine Tests ✅
**Status:** 58/58 PASSING (100%)  
**File:** `tests/unit/test_backtest_engine.py`  
**Execution Time:** ~2.5 seconds  
**Coverage:** Backtest engine core logic  

**Test Categories:**
- Historical data loading (5 tests)
- Indicator calculation (12 tests)
- Signal generation (8 tests)
- Order execution simulation (10 tests)
- Position tracking (8 tests)
- Performance metrics (10 tests)
- Multi-strategy support (5 tests)

**How to Run:**
```bash
pytest tests/unit/test_backtest_engine.py -v --tb=short
```

**What It Covers:**
- ✅ Data integrity and validation
- ✅ Mathematical accuracy of indicators
- ✅ Strategy signal logic
- ✅ P&L calculation in backtests
- ✅ Risk management rules
- ✅ Report generation

---

#### Suite 2: Paper Trading Sequence Tests ✅
**Status:** 49/49 PASSING (100%)  
**File:** `tests/unit/test_paper_trading_sequence.py`  
**Execution Time:** ~3.2 seconds  
**Coverage:** Complete paper trading workflow  
**Reference:** `docs/04-testing/PAPERTRADING_SEQUENCE_TEST_PLAN.md`

**Test Categories:**
- Session Start (3 tests) - Database setup, balance initialization
- Real-time Monitoring (6 tests) - Tick processing, OHLC generation
- Order Matching (10 tests) - Spread, commission, slippage calculations
- Position Management (9 tests) - Open/close logic, SL/TP calculation
- Position Monitoring (11 tests) - Real-time P&L, auto-close triggers
- Manual Stop (5 tests) - Session shutdown, metrics calculation
- Integration (5 tests) - End-to-end workflows

**How to Run:**
```bash
pytest tests/unit/test_paper_trading_sequence.py -v --tb=short
```

**Critical Tests to Review:**
- `test_seq_3_3_spread_cost_calculation` - Financial accuracy
- `test_seq_5_5_position_auto_close_sl_hit` - SL trigger logic
- `test_seq_5_6_position_auto_close_tp_hit` - TP trigger logic
- `test_seq_int_1_complete_workflow_single_trade` - Full integration

---

#### Suite 3: Strategy Module Tests ✅
**Status:** 22/22 PASSING (100%)  
**File:** `tests/unit/test_strategy_module.py`  
**Execution Time:** ~0.2 seconds  
**Coverage:** Strategy lifecycle management  
**Reference:** `docs/04-testing/STRATEGY_MODULE_TEST_PLAN.md`

**Test Categories:**
- UC16: Create Strategy (5 tests) - Entry/exit rules, risk config
- UC17: Test Strategy (4 tests) - Unit tests, backtests, validation
- UC18: Deploy Strategy (4 tests) - Packaging, registration, activation
- UC19: Update Strategy (4 tests) - Versioning, redeployment
- Integration (5 tests) - Complete lifecycle, multi-strategy

**How to Run:**
```bash
pytest tests/unit/test_strategy_module.py -v --tb=short
```

**What It Covers:**
- ✅ Strategy creation and validation
- ✅ Entry/exit rule configuration
- ✅ Risk management parameters
- ✅ Indicator setup
- ✅ Version control
- ✅ Deployment workflow

---

### 🚧 Test Suites To Create (Your Tasks)

#### Suite 4: Live Trading Integration Tests 🔴 CRITICAL
**Status:** NOT STARTED  
**Priority:** HIGHEST  
**Estimated Effort:** 2-3 days  

**Required Tests:**
1. **MT5 Connection** (8 tests)
   - [ ] Connect to demo account
   - [ ] Handle connection failures
   - [ ] Reconnect after disconnect
   - [ ] Timeout handling
   - [ ] Invalid credentials error
   - [ ] Multiple symbol subscription
   - [ ] Rate limiting compliance
   - [ ] Connection pool management

2. **Real Order Execution** (12 tests)
   - [ ] Market order submission
   - [ ] Market order confirmation
   - [ ] Limit order placement
   - [ ] Limit order trigger
   - [ ] Order rejection handling
   - [ ] Partial fill handling
   - [ ] Order modification
   - [ ] Order cancellation
   - [ ] Slippage verification
   - [ ] Commission calculation
   - [ ] Multi-order batch submission
   - [ ] Order history synchronization

3. **Position Synchronization** (6 tests)
   - [ ] Open positions from MT5
   - [ ] Position updates in real-time
   - [ ] Position close from MT5
   - [ ] Position modify (SL/TP)
   - [ ] Discrepancy detection
   - [ ] Recovery from mismatch

4. **Error Recovery** (8 tests)
   - [ ] Network timeout recovery
   - [ ] Broker API error handling
   - [ ] Insufficient margin error
   - [ ] Market closed error
   - [ ] Symbol not found error
   - [ ] Database write failure recovery
   - [ ] Duplicate order prevention
   - [ ] State consistency after crash

**How to Test:**
- Use MT5 **DEMO account** only
- Create test file: `tests/integration/test_live_trading_mt5.py`
- Mock MT5 API for unit tests, real API for integration
- Document all test scenarios

---

#### Suite 5: Database Integration Tests 🟡 HIGH
**Status:** PARTIAL (basic tests exist)  
**Priority:** HIGH  
**Estimated Effort:** 1-2 days  

**Required Tests:**
1. **CRUD Operations** (10 tests)
   - [ ] Insert trade record
   - [ ] Query trades by date range
   - [ ] Update position status
   - [ ] Delete old records
   - [ ] Bulk insert performance
   - [ ] Complex query with joins
   - [ ] Aggregation queries
   - [ ] Foreign key constraints
   - [ ] Unique constraint violations
   - [ ] Null value handling

2. **Concurrent Access** (6 tests)
   - [ ] Multiple writers (race condition)
   - [ ] Read while writing
   - [ ] Deadlock prevention
   - [ ] Transaction isolation
   - [ ] Lock timeout handling
   - [ ] Connection pool exhaustion

3. **Data Integrity** (8 tests)
   - [ ] Balance consistency check
   - [ ] Position sum equals trades
   - [ ] No orphaned records
   - [ ] Referential integrity
   - [ ] Data type validation
   - [ ] Schema migration safety
   - [ ] Backup and restore
   - [ ] Corruption recovery

**Test File:** `tests/integration/test_database_integrity.py`

---

#### Suite 6: Performance & Stress Tests 🟡 HIGH
**Status:** MINIMAL (basic benchmarks only)  
**Priority:** HIGH  
**Estimated Effort:** 2-3 days  

**Required Tests:**
1. **High Volume Trading** (5 tests)
   - [ ] 1000 trades/day sustained
   - [ ] 10 concurrent strategies
   - [ ] 20 symbols simultaneously
   - [ ] Memory usage <500MB
   - [ ] CPU usage <50% average

2. **Data Processing** (4 tests)
   - [ ] 1 million ticks/hour processing
   - [ ] 10-year backtest completion
   - [ ] Real-time latency <100ms
   - [ ] Database query <50ms

3. **Endurance Testing** (3 tests)
   - [ ] 24-hour continuous operation
   - [ ] No memory leaks
   - [ ] Performance degradation <5%

**Test File:** `tests/performance/test_high_volume.py`

---

#### Suite 7: Edge Cases & Boundary Tests 🟡 MEDIUM
**Status:** NOT STARTED  
**Priority:** MEDIUM  
**Estimated Effort:** 1-2 days  

**Required Tests:**
1. **Extreme Market Conditions** (8 tests)
   - [ ] Price gap (100+ pips)
   - [ ] Flash crash simulation
   - [ ] Zero liquidity
   - [ ] Extreme volatility
   - [ ] Halted trading
   - [ ] Negative prices (for some assets)
   - [ ] Very small lot sizes (0.01)
   - [ ] Very large lot sizes (100+)

2. **Invalid Inputs** (10 tests)
   - [ ] Negative prices
   - [ ] Negative lot sizes
   - [ ] Invalid symbol names
   - [ ] Future dates
   - [ ] Missing required fields
   - [ ] Malformed JSON config
   - [ ] SQL injection attempts
   - [ ] Buffer overflow attempts
   - [ ] Unicode handling
   - [ ] Special characters in strings

3. **Boundary Values** (6 tests)
   - [ ] Zero balance trading
   - [ ] Maximum leverage
   - [ ] Minimum lot size
   - [ ] Maximum positions (100+)
   - [ ] Integer overflow (large numbers)
   - [ ] Float precision limits

**Test File:** `tests/unit/test_edge_cases.py`

---

#### Suite 8: End-to-End Workflow Tests 🟢 MEDIUM
**Status:** PARTIAL (some scenarios covered)  
**Priority:** MEDIUM  
**Estimated Effort:** 1 day  

**Required Tests:**
1. **Complete User Journeys** (5 tests)
   - [ ] New user setup → first trade → profit withdrawal
   - [ ] Strategy creation → backtest → deploy → monitor
   - [ ] Configuration change → restart → verify state
   - [ ] Database migration → data integrity check
   - [ ] System upgrade → backward compatibility

**Test File:** `tests/e2e/test_user_workflows.py`

---

### Test Execution Guide

**Run All Tests:**
```bash
# All unit tests
pytest tests/unit/ -v

# All integration tests (when created)
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ --cov=core --cov=engines --cov-report=html

# Specific test suite
pytest tests/unit/test_paper_trading_sequence.py -v

# Specific test case
pytest tests/unit/test_paper_trading_sequence.py::TestOrderMatching::test_seq_3_3_spread_cost_calculation -v
```

**Run Tests in Parallel (faster):**
```bash
pip install pytest-xdist
pytest tests/ -n auto  # Uses all CPU cores
```

**Run with Detailed Output:**
```bash
pytest tests/ -v --tb=short --color=yes
```

---

##  Critical Test Scenarios (Manual Testing Checklist)

These scenarios must be tested manually before each release to verify real-world behavior:

### Scenario 1: Paper Trading - Stop Loss Hit 🔴 CRITICAL

**Objective:** Verify Stop Loss auto-closes position correctly

**Prerequisites:**
- Paper trading broker initialized
- Initial balance: $10,000
- Symbol: EURUSD, Market price: 1.1000

**Test Steps:**
1. Submit BUY order:
   - Lot: 0.1, Entry: Market (1.1000)
   - SL: 1.0950 (50 pips below)
   - TP: 1.1100

2. Simulate price drop (feed ticks):
   - 1.0999, 1.0980, 1.0960, 1.0950, 1.0940

3. Verify auto-close triggered at SL

4. Verify P&L calculation:
   - Expected: (1.0950 - 1.1000) × 0.1 × 100,000 = **-$500**
   - Tolerance: ±$10 (for spread/slippage)

5. Check database updates

**Expected Results:**
-  Position closes automatically at 1.0950
-  Exit price = 1.0950 (±2 pips slippage)
-  P&L ≈ -$500 (within $10 tolerance)
-  Balance: $10,000 - $500 = $9,500
-  Trade record: exit_reason = "Stop Loss"
-  No orphaned positions

**Pass Criteria:** ALL 6 checks pass  
**If Fails:** Document exact step, capture screenshots, check logs

---

### Scenario 2: Paper Trading - Take Profit Hit 🔴 CRITICAL

**Objective:** Verify Take Profit auto-closes position correctly

**Test Steps:**
1. Create paper trading broker
2. Submit BUY order with TP = 1.1100
3. Simulate price rise above TP
4. Check position auto-closed
5. Verify P&L positive
6. Check trade saved to database

**Expected Results**:
-  Position closes automatically
-  Exit price = TP (with slippage)
-  P&L calculated correctly
-  Balance updated
-  Trade record created
-  Exit reason = "Take Profit"

**Pass Criteria**: All 6 checks pass

---

### Scenario 3: P&L Calculation Accuracy

**Objective**: Verify P&L math is correct

**Steps**:
1. Open BUY position: 0.1 lot EURUSD @ 1.1000
2. Close position @ 1.1050 (+50 pips)
3. Calculate expected P&L:
   - Gross = (1.1050 - 1.1000)  0.1  100,000 = $500
   - Spread = ~$2 (estimate)
   - Net = Gross - Spread - Commission - Swap
4. Compare with system calculation

**Expected Results**:
-  Gross P&L = $500 ($5 tolerance)
-  Spread cost calculated
-  Commission deducted
-  Swap included
-  Net P&L = Gross - Costs
-  Balance increased by Net P&L

**Pass Criteria**: All calculations within 1% tolerance

---

### Scenario 4: Backtest Complete Workflow

**Objective**: Run full backtest end-to-end

**Steps**:
1. Configure backtest: EURUSD, H1, 2024-01-01 to 2024-12-31
2. Initialize SuperTrend bot
3. Run backtest
4. Generate report
5. Verify metrics

**Expected Results**:
-  Data loaded successfully
-  Indicators calculated
-  Signals generated
-  Trades executed
-  Report created
-  No errors/crashes

**Pass Criteria**: Complete workflow, reasonable results

---

### Scenario 5: Multi-Symbol Backtest

**Objective**: Test across multiple currency pairs

**Steps**:
1. Configure 3 symbols: EURUSD, GBPUSD, XAUUSD
2. Run backtests sequentially
3. Compare results
4. Check for crashes

**Expected Results**:
-  All symbols process successfully
-  No memory leaks
-  Results aggregated
-  Performance comparable

**Pass Criteria**: All 3 complete without errors

---

##  Bug Report Template

When you find a bug, report using this format:

```markdown
## Bug #[NUMBER]: [Short Description]

**Severity**: Critical | High | Medium | Low

**Component**: [Module/File name]

**Description**:
[Clear description of the bug]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [Third step]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happens]

**Environment**:
- OS: [Windows/Linux/Mac]
- Python: [Version]
- MT5: [Yes/No]

**Screenshots/Logs**:
[Attach relevant files]

**Reproducibility**:
- Always (100%)
- Frequent (75%+)
- Occasional (25-75%)
- Rare (<25%)

**Suggested Fix** (optional):
[Your thoughts on how to fix]
```

---

##  Test Cases to Create

### Your Task: Write Tests for These

#### Test Case 1: Invalid Config
**File**: `tests/test_config_validation.py`
```python
def test_config_missing_required_field():
    """Test config with missing required field raises error"""
    # TODO: Implement
    
def test_config_invalid_value_type():
    """Test config with wrong value type raises error"""
    # TODO: Implement
```

#### Test Case 2: Order Execution
**File**: `tests/test_order_execution.py`
```python
def test_market_order_execution():
    """Test market order executes immediately"""
    # TODO: Implement
    
def test_limit_order_execution():
    """Test limit order executes at price"""
    # TODO: Implement
```

#### Test Case 3: Position Management
**File**: `tests/test_position_management.py`
```python
def test_position_open():
    """Test position opens correctly"""
    # TODO: Implement
    
def test_position_close():
    """Test position closes correctly"""
    # TODO: Implement
    
def test_multiple_positions():
    """Test handling multiple positions"""
    # TODO: Implement
```

#### Test Case 4: Database Operations
**File**: `tests/test_database.py`
```python
def test_trade_insert():
    """Test trade record insertion"""
    # TODO: Implement
    
def test_trade_query():
    """Test trade record query"""
    # TODO: Implement
    
def test_concurrent_access():
    """Test concurrent database access"""
    # TODO: Implement
```

---

##  Coverage Requirements

### Minimum Coverage
- **Critical modules**: 95%+
  - `core/base_bot.py`
  - `engines/backtest_engine.py`
  - `engines/paper_trading_broker_api.py`

- **Important modules**: 85%+
  - `core/ict_bot.py`
  - `core/supertrend_bot.py`
  - `engines/database_manager.py`

- **Other modules**: 70%+

### How to Check Coverage
```bash
pytest --cov=core --cov=engines --cov=utils --cov-report=html
# Open htmlcov/index.html
```

---

##  Watch Out For

### Common Issues to Check

1. **Off-by-one errors**
   - Array indexing
   - Loop boundaries
   - Date ranges

2. **Floating point precision**
   - P&L calculations
   - Price comparisons
   - Percentage calculations

3. **Edge cases**
   - Empty data
   - Null values
   - Extreme numbers
   - Zero division

4. **Race conditions**
   - Concurrent database access
   - Multiple positions
   - Parallel backtests

5. **Memory leaks**
   - Large datasets
   - Long-running processes
   - Unclosed connections

---

##  Test Focus Areas

### High-Risk Components

**1. Order Execution** (CRITICAL)
- Money at stake
- Test with real demo account
- Verify slippage handling

**2. P&L Calculation** (CRITICAL)
- Financial accuracy critical
- Cross-check manually
- Test edge cases (JPY pairs, crypto)

**3. SL/TP Logic** (HIGH)
- Risk management
- Test both BUY and SELL
- Verify auto-close

**4. Database** (HIGH)
- Data integrity
- Test rollback
- Check concurrent access

**5. MT5 Connection** (MEDIUM)
- External dependency
- Test reconnection
- Handle timeouts

---

##  Test Reporting

### Daily Report Template

```markdown
# Test Report - [Date]

## Summary
- Tests run: [X]
- Passed: [X]
- Failed: [X]
- Skipped: [X]
- Coverage: [X]%

## New Issues Found
1. Bug #[N]: [Description]
2. Bug #[N]: [Description]

## Blocked Tests
- [Test name]: Blocked by [reason]

## Next Steps
- [Plan for tomorrow]

## Notes
- [Any observations]
```

---

##  Sign-Off Criteria for Production Release

### Pre-Release Checklist (ALL must be checked ✅)

**Testing Completeness:**
- [ ] All 129 existing unit tests pass (100% success rate)
- [ ] New feature tests written and passing
- [ ] Integration tests pass (Suite 4-8 when created)
- [ ] Manual scenarios 1-8 tested successfully
- [ ] Regression tests pass (no old bugs reappeared)

**Code Quality:**
- [ ] Code coverage ≥85% on critical modules (`core/`, `engines/`)
- [ ] Code coverage ≥70% on other modules
- [ ] No code smells or anti-patterns
- [ ] Static analysis tools pass (pylint, mypy)

**Bug Status:**
- [ ] **Zero CRITICAL bugs** (must fix before release)
- [ ] **Zero HIGH bugs** OR all have documented workarounds
- [ ] All MEDIUM bugs documented in known issues
- [ ] LOW bugs tracked for future releases

**Performance Benchmarks:**
- [ ] Backtest: <60s for 1-year H1 data
- [ ] Paper trading: <100ms signal generation latency
- [ ] Live trading: <500ms order execution time
- [ ] Memory usage: <500MB for normal operation
- [ ] Database queries: <50ms average

**Manual Testing:**
- [ ] Demo account tested with ≥50 live trades
- [ ] Multiple symbols tested (EURUSD, GBPUSD, USDJPY minimum)
- [ ] Strategy switching tested
- [ ] System recovery from crash tested
- [ ] 24-hour endurance test passed (no crashes, no leaks)

**Documentation:**
- [ ] All new features documented
- [ ] API changes documented
- [ ] Known issues listed
- [ ] Upgrade guide written (if needed)
- [ ] Test reports submitted

**Deployment Readiness:**
- [ ] Configuration files validated
- [ ] Database migration scripts tested
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

---

### Your Go/No-Go Decision

Based on the checklist above, provide your professional recommendation:

**✅ GO** - Safe to deploy to production
- All checks passed
- No critical risks identified
- Confident in system stability

**⚠️ GO WITH CONDITIONS** - Deploy but with caution
- Minor issues exist but acceptable
- Risks documented and mitigated
- Enhanced monitoring recommended
- **Document conditions clearly**

**❌ NO-GO** - Do NOT deploy
- Critical issues blocking release
- Risks too high for production
- More testing needed
- **List blockers clearly**

**Your signature:** _____________________  
**Date:** _____________________  
**Recommendation:** GO / GO WITH CONDITIONS / NO-GO

---

##  Tester Work Schedule

### Week 1: Foundation & Unit Testing

**Day 1: Environment Setup & Orientation**
- [ ] Read complete TEST_REQUIREMENTS.md (this document)
- [ ] Set up development environment (Python, venv, dependencies)
- [ ] Run existing 129 tests - verify all pass
- [ ] Review project structure and code architecture
- [ ] Read reference docs (PAPERTRADING_SEQUENCE_TEST_PLAN.md, STRATEGY_MODULE_TEST_PLAN.md)
- [ ] Set up MT5 demo account (for future integration tests)
- **Deliverable:** Environment setup confirmation

**Day 2-3: Analyze Existing Tests**
- [ ] Study test_backtest_engine.py (58 tests)
- [ ] Study test_paper_trading_sequence.py (49 tests)
- [ ] Study test_strategy_module.py (22 tests)
- [ ] Identify coverage gaps
- [ ] Document test patterns and conventions
- [ ] Run tests with coverage: `pytest --cov=core --cov=engines`
- **Deliverable:** Coverage gap analysis report

**Day 4-5: Create New Unit Tests**
- [ ] Write tests for low-coverage modules (<70%)
- [ ] Focus on edge cases and boundary values
- [ ] Target: Bring overall coverage to 85%+
- [ ] Document any bugs found
- **Deliverable:** New test files + bug reports (if any)

---

### Week 2: Integration & System Testing

**Day 6-7: Database Integration Tests (Suite 5)**
- [ ] Create `tests/integration/test_database_integrity.py`
- [ ] Test CRUD operations (10 tests)
- [ ] Test concurrent access (6 tests)
- [ ] Test data integrity (8 tests)
- [ ] Run with real SQLite database
- **Deliverable:** 24 new integration tests

**Day 8-9: Live MT5 Integration Tests (Suite 4)**
- [ ] Create `tests/integration/test_live_trading_mt5.py`
- [ ] Test MT5 connection (8 tests)
- [ ] Test real order execution (12 tests)  
- [ ] Test position synchronization (6 tests)
- [ ] Test error recovery (8 tests)
- [ ] **Use DEMO account only!**
- **Deliverable:** 34 new integration tests + MT5 compatibility report

**Day 10: Manual Testing**
- [ ] Execute all 8 critical scenarios manually
- [ ] Document results with screenshots
- [ ] Verify all pass criteria met
- **Deliverable:** Manual testing checklist completed

---

### Week 3: Performance & Stress Testing

**Day 11-12: Performance Tests (Suite 6)**
- [ ] Create `tests/performance/test_high_volume.py`
- [ ] Test high-volume trading (5 tests)
- [ ] Test data processing (4 tests)
- [ ] Test endurance (3 tests - including 24hr test)
- [ ] Profile and benchmark
- **Deliverable:** Performance test suite + benchmark report

**Day 13: Edge Cases & Boundary Tests (Suite 7)**
- [ ] Create `tests/unit/test_edge_cases.py`
- [ ] Test extreme market conditions (8 tests)
- [ ] Test invalid inputs (10 tests)
- [ ] Test boundary values (6 tests)
- **Deliverable:** 24 edge case tests

**Day 14: End-to-End Workflows (Suite 8)**
- [ ] Create `tests/e2e/test_user_workflows.py`
- [ ] Test complete user journeys (5 tests)
- [ ] Verify full system integration
- **Deliverable:** 5 E2E tests

---

### Week 4: Final Validation & Release Prep

**Day 15-16: Regression Testing**
- [ ] Run ALL tests (unit + integration + E2E)
- [ ] Verify 95%+ pass rate
- [ ] Fix any new failures
- [ ] Re-run failed tests after fixes
- **Deliverable:** Full regression test report

**Day 17: Documentation & Reporting**
- [ ] Complete weekly test summary reports (Weeks 1-3)
- [ ] Compile all bug reports
- [ ] Create final release test report
- [ ] Update test documentation
- **Deliverable:** Complete test documentation package

**Day 18: Sign-Off Preparation**
- [ ] Review sign-off checklist
- [ ] Verify all criteria met
- [ ] Prepare Go/No-Go recommendation
- [ ] Schedule review meeting with dev team
- **Deliverable:** Go/No-Go decision document

**Day 19-20: Buffer Time**
- [ ] Address any last-minute issues
- [ ] Re-test critical fixes
- [ ] Final verification
- [ ] Handoff to deployment team

---

##  Communication & Reporting Guidelines

### Daily Standup (5 minutes)

Share with team:
1. **Yesterday**: What tests did I complete?
2. **Today**: What tests am I running?
3. **Blockers**: What's blocking me?

### Bug Report Escalation

| Severity | Report To | Timeline |
|----------|-----------|----------|
| CRITICAL | Dev Lead + PM immediately | Within 1 hour of discovery |
| HIGH | Dev Lead | Within 4 hours |
| MEDIUM | Dev team channel | End of day |
| LOW | Weekly report | Next weekly report |

### Questions & Support

**Before asking:**
1. Search documentation
2. Check existing GitHub issues
3. Review test examples

**How to ask:**
- GitHub Issue with `question` label
- Include context and what you've tried
- Expected response: <24 hours

**Developer Contact:**
- GitHub: @thales1020
- Email: [via GitHub profile]

---

##  Success Criteria for Tester Role

You are successful when:

✅ **Quantitative Metrics:**
- All 129 existing tests remain passing
- +100 new tests created (integration + E2E)
- Code coverage increased to 85%+ (critical modules)
- 95%+ overall test pass rate
- Zero CRITICAL/HIGH bugs in production

✅ **Qualitative Outcomes:**
- Production deployment goes smoothly
- No financial calculation errors
- System stability maintained
- Client confidence in platform
- Development team trusts test suite

✅ **Professional Growth:**
- Deep understanding of trading systems
- Expertise in financial software testing
- Strong pytest proficiency
- Clear communication with dev team

---

##  Resources & References

### Internal Documentation
- `docs/04-testing/PAPERTRADING_SEQUENCE_TEST_PLAN.md` - Paper trading test specs
- `docs/04-testing/STRATEGY_MODULE_TEST_PLAN.md` - Strategy module test specs
- `docs/05-architecture/` - System architecture docs
- `README.md` - Project overview

### External References
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/) - Database ORM
- [MT5 Python API](https://www.mql5.com/en/docs/python_metatrader5) - MetaTrader integration

### Testing Best Practices
- [Google Testing Blog](https://testing.googleblog.com/)
- [Test Pyramid Concept](https://martinfowler.com/articles/practical-test-pyramid.html)

---

##  Final Notes

**Remember:**
- **You are the last line of defense** before production
- **Financial accuracy is non-negotiable** - verify all calculations
- **When in doubt, test more** - better safe than sorry
- **Document everything** - future testers depend on your work
- **Communicate early** - report issues immediately, don't wait

**This is a real trading system handling real money.**  
Your thoroughness protects clients from financial loss.

**Take your time. Do it right. Lives (and livelihoods) depend on it.**

---

**Document Version**: 2.0  
**Last Updated**: November 5, 2025  
**Author**: QA Team Lead  
**Next Review**: November 12, 2025  
**Status**: ACTIVE - Ready for Tester Onboarding

**Document approved by:**
- Development Lead: _______________
- QA Lead: _______________
- Project Manager: _______________

Remember:
- **Be objective** - Don't assume anything works
- **Be thorough** - Test edge cases
- **Be clear** - Document everything
- **Be independent** - Fresh eyes find bugs

Your testing is critical for production safety. Take your time and do it right!

---

**Document Version**: 1.0  
**Last Updated**: November 5, 2025  
**Next Review**: November 12, 2025

