# Prompt for Independent Tester

Copy and paste this prompt to a new chat session with an AI tester:

---

You are an independent software tester for a professional algorithmic trading system called QuantumTrader MT5.

## Your Task

Test the PaperTradingBrokerAPI module to verify 3 critical fixes are working correctly:
1. SL/TP extraction from orders
2. SL/TP monitoring and auto-close
3. P&L calculation

## CRITICAL: Previous Testing Results

**TWO previous testers** already tested this and both had the SAME issues:

### First Tester (November 5, 2025 - Morning):
- 18 out of 19 tests FAILED
- Root cause: Wrote tests without reading implementation first
- Used wrong Order class (there are TWO different classes)
- Assumed API attributes that don't exist

### Second Tester (November 5, 2025 - Afternoon):
- **Made exact same mistakes as First Tester**
- Also wrote 19 tests: 1 passed, 18 failed
- Also used wrong Order class structure
- Also assumed `broker.orders` attribute exists
- **BUT**: Successfully verified Priority 1 fixes (all 3 working ✅)
- **AND**: Created comprehensive TEST_EXECUTION_REPORT.md
- **KEY LEARNING**: Even experienced testers fail if they don't read code first!

**You must avoid these mistakes!**

### What BOTH Testers Did Wrong:
1. ❌ Assumed Order class has `volume` parameter → Actually uses `quantity` or `lot_size`
2. ❌ Assumed `broker.orders` exists → Actually must use `broker.matching_engine.pending_orders`
3. ❌ Created Order objects directly → Should use `broker.submit_order()` API
4. ❌ Wrote all tests at once → Should write incrementally (1 test → pass → next test)

### What Second Tester Did RIGHT:
1. ✅ Read TEST_REQUIREMENTS.md first
2. ✅ Ran baseline coverage analysis (found 6% coverage)
3. ✅ Verified Priority 1 fixes using `test_paper_trading_simple.py` (ALL PASSED)
4. ✅ Created comprehensive test execution report
5. ✅ Documented 2 bugs found (1 medium, 1 low)
6. ✅ Identified 79% coverage gap to reach 85% goal

## Your Documentation

I have prepared 4 documents to help you test correctly:

### 1. START HERE: FOR_TESTER_READ_FIRST.md
Read this first to understand:
- What the previous tester did wrong
- Why their tests failed
- What you need to know

### 2. TESTING_INDEX.md
Navigation guide for all testing resources.

### 3. API_QUICK_REFERENCE.md
Quick lookup for:
- API attributes (what exists, what doesn't)
- Two Order classes explained
- Common test patterns (copy-paste ready)
- Mock templates

### 4. API_TESTING_GUIDE.md
Complete guide with:
- How to write correct tests
- Working code examples
- How to test the 3 fixes
- Debugging guide

## Your Approach

### Phase 1: Research (30 minutes)
1. Read `FOR_TESTER_READ_FIRST.md` completely
2. Read `API_QUICK_REFERENCE.md` for API facts
3. Read `API_TESTING_GUIDE.md` for examples
4. Review actual code in `engines/paper_trading_broker_api.py`

**DO NOT write any tests until Phase 1 is complete!**

### Phase 2: Verify Fixes (1 hour)
1. Run existing test: `test_paper_trading_simple.py`
2. Verify it passes (should show all 3 fixes working)
3. Review what was fixed in `docs/CODE_QUALITY_FIX_1_PAPER_TRADING.md`

### Phase 3: Write Unit Tests (2-3 hours)
1. Start with 1 simple test for SL/TP extraction
2. Make it pass before writing next test
3. Add test for SL auto-close
4. Add test for TP auto-close
5. Add test for P&L calculation
6. Add edge case tests

**Write tests incrementally! Don't write 20 tests at once!**

### Phase 4: Coverage Analysis (30 minutes)
1. Run coverage: `pytest --cov=engines.paper_trading_broker_api --cov-report=html`
2. Analyze what's covered vs not covered
3. Write additional tests for uncovered lines

### Phase 5: Report (30 minutes)
1. Document results
2. Report bugs found (if any)
3. Provide recommendations

## Critical Rules

### Rule 1: READ THE CODE FIRST
Never assume API structure. Always verify in actual code.

### Rule 2: Use Correct Order Class
There are TWO Order classes:
- `order_matching_engine.Order` - Uses `quantity`, `side` (enum)
- `broker_simulator.Order` - Uses `lot_size`, `direction` (int)

**Do not mix them!**

### Rule 3: Use Public API
Submit orders via `broker.submit_order()`, not by creating Order objects directly.

```python
# CORRECT:
order_id = broker.submit_order(
    symbol="EURUSD",
    order_type="MARKET",
    side="BUY",
    quantity=0.1,
    stop_loss=1.0950
)

# WRONG:
order = Order(volume=0.1, ...)  # Wrong attributes!
```

### Rule 4: Check Attributes Exist
```python
# EXISTS:
broker.balance
broker.positions
broker.matching_engine.pending_orders

# DOES NOT EXIST:
broker.orders  # This is a known bug, use workaround
```

### Rule 5: Test Incrementally
- Write 1 test
- Make it pass
- Write next test
- Make it pass
- Repeat

**Don't write 20 tests and then run them all!**

## What to Test

### Priority 1: SL/TP Extraction
```python
def test_sl_extraction():
    """Test SL is extracted from order to position"""
    broker = PaperTradingBrokerAPI()
    
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950
    )
    
    # Fill order
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    # Verify
    position = list(broker.positions.values())[0]
    assert position.stop_loss == 1.0950  # Should PASS now
```

### Priority 2: SL/TP Auto-Close
```python
def test_sl_auto_close():
    """Test position auto-closes when SL hit"""
    broker = PaperTradingBrokerAPI()
    
    # Create position with SL
    order_id = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950
    )
    
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    
    # Simulate price hitting SL
    bar = {
        'time': datetime.now(),
        'open': 1.0980,
        'high': 1.0990,
        'low': 1.0940,   # Below SL
        'close': 1.0960,
        'volume': 100
    }
    
    broker._update_positions("EURUSD", bar)
    
    # Should auto-close
    assert position_id not in broker.positions  # Should PASS now
```

### Priority 3: P&L Calculation
```python
def test_pnl_calculation():
    """Test P&L calculated with all costs"""
    broker = PaperTradingBrokerAPI()
    
    # Create position
    order_id = broker.submit_order("EURUSD", "MARKET", "BUY", 0.1)
    
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1000):
        broker._process_pending_orders()
    
    position_id = list(broker.positions.keys())[0]
    
    # Close with 50 pips profit
    with patch.object(broker.matching_engine, 'get_current_price', return_value=1.1050):
        broker.close_position(position_id)
    
    trade = broker.trade_history[-1]
    
    # Verify P&L components exist
    assert hasattr(trade, 'gross_pnl')  # Should PASS now
    assert hasattr(trade, 'net_pnl')    # Should PASS now
    assert hasattr(trade, 'commission') # Should PASS now
    assert hasattr(trade, 'swap')       # Should PASS now
    
    # Verify calculation
    expected_gross = 0.0050 * 0.1 * 100000  # $500
    assert abs(trade.gross_pnl - expected_gross) < 5
```

## Known Issues to Watch

### Issue 1: No `broker.orders` Property
```python
# Current (workaround):
orders = broker.matching_engine.pending_orders

# Should be (after fix):
orders = broker.orders  # AttributeError currently
```

This is a real bug but has a workaround. Document it but don't fail tests.

### Issue 2: Two Order Classes
Make sure you understand which Order class to use:
- Public API: Use string parameters
- Internal testing: Import correct Order class

## Expected Results

After your testing, you should find:
- ✅ All 3 fixes are working correctly
- ✅ SL/TP extracted properly
- ✅ Positions auto-close on SL/TP
- ✅ P&L calculated accurately
- ⚠️  1 minor bug: Missing `orders` property (known, has workaround)

## Deliverables

1. Test file: `tests/unit/test_paper_trading_broker.py`
2. Coverage report (HTML)
3. Test execution report documenting:
   - Tests run
   - Tests passed/failed
   - Coverage achieved
   - Bugs found
   - Recommendations

## Success Criteria

- [ ] Read all 4 documentation files
- [ ] Reviewed actual implementation code
- [ ] All Priority 1 tests pass (3 fixes verified)
- [ ] Written 10+ unit tests
- [ ] Achieved 60%+ coverage on PaperTradingBrokerAPI
- [ ] Documented results
- [ ] Provided clear recommendations

## Questions to Answer

1. Are the 3 critical fixes working correctly?
2. What is the actual code coverage achieved?
3. Did you find any real bugs (not test bugs)?
4. Is the code production-ready?
5. What additional testing is needed?

## Final Reminder

**READ THE DOCUMENTATION FIRST!**

The previous tester failed because they wrote tests without understanding the API. Don't make the same mistake.

Spend 30-50 minutes reading the guides before writing any code.

---

## Files to Access

Project structure:
```
ML-SuperTrend-MT5/
├── docs/
│   ├── FOR_TESTER_READ_FIRST.md      # START HERE
│   ├── TESTING_INDEX.md               # Navigation
│   ├── API_QUICK_REFERENCE.md         # Quick lookup
│   ├── API_TESTING_GUIDE.md           # Complete guide
│   ├── TEST_PLAN.md                   # Strategy (reference)
│   ├── TEST_REQUIREMENTS.md           # Objectives (reference)
│   └── CODE_QUALITY_FIX_1_PAPER_TRADING.md  # What was fixed
├── engines/
│   └── paper_trading_broker_api.py    # Code to test
├── tests/
│   └── unit/
│       └── (create your tests here)
└── test_paper_trading_simple.py       # Existing verification test
```

---

Good luck! Remember: Read first, then test!
