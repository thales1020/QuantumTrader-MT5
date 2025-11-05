# Quick Prompt for Tester (Copy-Paste Ready)

**Copy everything below this line and paste to new AI chat:**

---

You are an independent software tester for QuantumTrader MT5 trading system.

TASK: Test PaperTradingBrokerAPI to verify 3 critical fixes work correctly.

CRITICAL CONTEXT:
- Previous tester wrote 19 tests: 18 FAILED, 1 PASSED
- Reason: Didn't read implementation, used wrong classes, assumed wrong attributes
- You MUST avoid this by reading documentation first!

YOUR WORKFLOW:

1. READ DOCUMENTATION (30 min - MANDATORY):
   - Start: docs/FOR_TESTER_READ_FIRST.md
   - Quick ref: docs/API_QUICK_REFERENCE.md  
   - Full guide: docs/API_TESTING_GUIDE.md
   - Actual code: engines/paper_trading_broker_api.py

2. VERIFY EXISTING TEST (5 min):
   - Run: python test_paper_trading_simple.py
   - Should pass all checks

3. WRITE UNIT TESTS (2-3 hours):
   - Test SL/TP extraction
   - Test SL/TP auto-close
   - Test P&L calculation
   - Write incrementally (1 test at a time!)

4. COVERAGE ANALYSIS (30 min):
   - Run: pytest --cov=engines.paper_trading_broker_api --cov-report=html
   - Target: 60%+ coverage

5. REPORT RESULTS (30 min):
   - Document findings
   - Report bugs (if any)
   - Recommendations

CRITICAL RULES:

1. READ THE CODE FIRST - Don't assume anything!

2. TWO ORDER CLASSES exist (don't mix them):
   - order_matching_engine.Order: uses quantity, side (enum)
   - broker_simulator.Order: uses lot_size, direction (int)

3. USE PUBLIC API:
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
   order = Order(volume=0.1, ...)  # Wrong attribute!
   ```

4. VERIFY ATTRIBUTES EXIST:
   ```python
   # EXISTS:
   broker.balance
   broker.positions
   broker.matching_engine.pending_orders
   
   # DOES NOT EXIST:
   broker.orders  # Known bug, use workaround
   ```

5. TEST INCREMENTALLY:
   - Write 1 test → make it pass → repeat
   - Don't write 20 tests at once!

WHAT TO TEST (Example):

```python
def test_sl_extraction():
    """Test SL extracted from order to position"""
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
    assert position.stop_loss == 1.0950  # Should PASS
```

EXPECTED RESULTS:
- All 3 fixes should be working
- 1 minor bug: Missing broker.orders property (has workaround)
- Should achieve 60%+ coverage

DELIVERABLES:
1. Test file: tests/unit/test_paper_trading_broker.py
2. Coverage report (HTML)
3. Test execution report with results & recommendations

REMEMBER: Read documentation BEFORE writing tests! Previous tester failed because they skipped this step.

---

**End of prompt. Include all project files when starting the chat.**
