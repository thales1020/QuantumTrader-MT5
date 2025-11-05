#  Test Requirements Document

**Project**: QuantumTrader MT5  
**Version**: 1.0  
**Date**: November 5, 2025  
**For**: Independent Testers

---

##  Your Mission

You are an **independent tester** for a professional algorithmic trading system. Your job is to:

1. **Test objectively** - Don't assume code is correct
2. **Find bugs** - Look for what's broken
3. **Verify claims** - Confirm features work as documented
4. **Test edge cases** - Try to break things
5. **Document findings** - Report everything clearly

**Mindset**: "How can I break this?"

---

##  What You're Testing

### System Overview
**QuantumTrader MT5** is an automated trading system with:
- **2 strategies**: ICT (Inner Circle Trader) + SuperTrend
- **3 modes**: Backtest, Paper Trading, Live Trading
- **MT5 integration**: MetaTrader 5 broker connection
- **Database**: Trade tracking and analytics
- **Risk management**: SL/TP, position sizing

### Recent Changes (Just Fixed)
**Paper Trading Module** - 3 critical TODOs fixed:
1.  SL/TP extraction from orders
2.  SL/TP monitoring and auto-close
3.  P&L calculation

**Your job**: Verify these fixes actually work!

---

##  Setup Requirements

### 1. Environment Setup

**Python**: 3.11+
```bash
# Clone repo
git clone https://github.com/thales1020/QuantumTrader-MT5.git
cd QuantumTrader-MT5

# Create venv
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. MetaTrader 5 (Optional for full testing)
- Download MT5 from broker
- Open demo account
- Note: login, password, server

### 3. Configuration
```bash
# Copy example config
cp config/config.example.json config/config.json

# Edit with your settings (if testing MT5 integration)
```

---

##  Test Deliverables

### What You Need to Provide

1. **Test Execution Report**
   - Which tests ran
   - Pass/Fail results
   - Execution time
   - Coverage metrics

2. **Bug Reports** (if found)
   - Bug description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs
   - Severity (Critical/High/Medium/Low)

3. **Test Summary**
   - Overall assessment
   - Risk areas identified
   - Recommendations
   - Sign-off (Go/No-Go for production)

---

##  Test Suites

### Priority 1: Paper Trading Fixes  (CRITICAL)

**File**: `test_paper_trading_simple.py`

**What to test**:
1. SL/TP extraction from orders
2. SL/TP auto-close on trigger
3. P&L calculation accuracy

**How to run**:
```bash
python test_paper_trading_simple.py
```

**Expected**: All tests PASS

**What to check**:
-  Code compiles
-  SL/TP extracted from order
-  SL/TP monitoring logic exists
-  P&L calculation complete
-  No TODOs remain

**If fails**: Document which check failed

---

### Priority 2: Unit Tests (HIGH)

**File**: `tests/test_*.py` (to be created)

**Coverage**:
- Core module functions
- Engine calculations
- Utility helpers

**How to run**:
```bash
pytest tests/ -v
```

**Expected**: 95%+ pass rate

---

### Priority 3: Integration Tests (HIGH)

**File**: `tests/integration/test_*.py`

**Coverage**:
- Bot + Engine integration
- Database + Bot integration
- MT5 + Bot integration

**How to run**:
```bash
pytest tests/integration/ -v
```

**Expected**: All critical paths pass

---

### Priority 4: End-to-End Tests (MEDIUM)

**File**: `tests/e2e/test_*.py`

**Coverage**:
- Complete backtest workflow
- Complete paper trading session
- Strategy deployment

**How to run**:
```bash
pytest tests/e2e/ -v --slow
```

**Expected**: All workflows complete successfully

---

##  Critical Test Scenarios

### Scenario 1: Paper Trading SL Hit

**Objective**: Verify Stop Loss auto-closes position

**Steps**:
1. Create paper trading broker
2. Submit BUY order with SL = 1.0950
3. Simulate price drop below SL
4. Check position auto-closed
5. Verify P&L negative
6. Check trade saved to database

**Expected Results**:
-  Position closes automatically
-  Exit price = SL (with slippage)
-  P&L calculated correctly
-  Balance updated
-  Trade record created
-  Exit reason = "Stop Loss"

**Pass Criteria**: All 6 checks pass

**If fails**: Document which step failed

---

### Scenario 2: Paper Trading TP Hit

**Objective**: Verify Take Profit auto-closes position

**Steps**:
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

##  Sign-Off Criteria

### Before Saying "Ready for Production"

Check ALL of these:
- [ ] All Priority 1 tests pass (Paper Trading)
- [ ] All Priority 2 tests pass (Unit)
- [ ] All Priority 3 tests pass (Integration)
- [ ] Code coverage  85%
- [ ] No Critical or High severity bugs
- [ ] All Medium bugs documented
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Regression tests pass
- [ ] Manual testing complete

**Only sign off if ALL checked!**

---

##  Questions?

**Developer Contact**: Trn Trng Hiu (@thales1020)

**How to Ask Questions**:
1. Check documentation first
2. Search existing issues
3. Create new GitHub issue
4. Tag with `question` label

**Response Time**: Within 24 hours

---

##  Your First Steps

### Day 1: Setup & Orientation
1.  Read this document completely
2.  Setup development environment
3.  Run existing tests
4.  Review codebase structure
5.  Read TEST_PLAN.md

### Day 2-3: Priority 1 Testing
1.  Run `test_paper_trading_simple.py`
2.  Create additional paper trading tests
3.  Test with different symbols
4.  Document findings

### Day 4-5: Unit Testing
1.  Write unit tests for core modules
2.  Write unit tests for engines
3.  Achieve 85%+ coverage
4.  Document bugs

### Week 2: Integration & E2E
1.  Integration tests
2.  E2E workflows
3.  Performance testing
4.  Final report

---

##  Good Luck!

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

