# Testing Resources Index

**For**: Independent Testers  
**Last Updated**: November 5, 2025

---

## START HERE

If you're new to testing this project, read documents in this order:

1. **TEST_REQUIREMENTS.md** - Your mission and what to test
2. **API_QUICK_REFERENCE.md** - Quick lookup for API attributes (5 min read)
3. **API_TESTING_GUIDE.md** - Detailed guide with examples (30 min read)
4. **TEST_PLAN.md** - Overall testing strategy (reference)

---

## Quick Links

### For Quick Answers
- **API Attributes**: See `API_QUICK_REFERENCE.md` Section "API Attributes Quick Lookup"
- **Order Classes**: See `API_QUICK_REFERENCE.md` Section "Order Class Quick Reference"
- **Test Patterns**: See `API_QUICK_REFERENCE.md` Section "Common Test Patterns"
- **Mock MT5**: See `API_QUICK_REFERENCE.md` Section "Mock MT5 Template"

### For Detailed Examples
- **Testing SL/TP**: See `API_TESTING_GUIDE.md` Section "Testing the 3 Critical Fixes"
- **Testing P&L**: See `API_TESTING_GUIDE.md` Section "Fix #3: P&L Calculation"
- **Complete Test Class**: See `API_TESTING_GUIDE.md` Section "Example: Complete Test Class"
- **Debugging**: See `API_TESTING_GUIDE.md` Section "Debugging Failed Tests"

### For Planning
- **Test Suites**: See `TEST_PLAN.md` Section "Detailed Test Cases"
- **Coverage Goals**: See `TEST_PLAN.md` Section "Coverage Goals"
- **Timeline**: See `TEST_PLAN.md` Section "Test Execution Plan"

---

## Document Summaries

### TEST_REQUIREMENTS.md
**Purpose**: Define what needs to be tested  
**Key Sections**:
- Your Mission
- System Overview
- Setup Requirements
- Test Deliverables
- Critical Test Scenarios
- Bug Report Template
- Sign-off Criteria

**When to use**: 
- First time setup
- Understanding project scope
- Writing bug reports
- Determining production readiness

---

### API_QUICK_REFERENCE.md
**Purpose**: Quick lookup for API details  
**Key Sections**:
- API Attributes (what exists, what doesn't)
- Order Class Reference
- Position/Trade Attributes
- Common Test Patterns
- Mock MT5 Template
- Common Errors and Fixes

**When to use**:
- Need to check if attribute exists
- Forgot Order class structure
- Need quick test pattern
- Getting AttributeError or TypeError

---

### API_TESTING_GUIDE.md
**Purpose**: Comprehensive testing guide  
**Key Sections**:
- Understanding PaperTradingBrokerAPI
- Two Order Classes Explained
- API Attributes Reference
- How to Write Correct Tests
- Testing the 3 Critical Fixes
- Complete Examples
- Debugging Guide

**When to use**:
- Writing new tests
- Tests failing, don't know why
- Need detailed examples
- Want to understand implementation

---

### TEST_PLAN.md
**Purpose**: Overall testing strategy  
**Key Sections**:
- Test Objectives
- Test Scope (all modules)
- Test Categories (Unit, Integration, E2E)
- Test Matrix
- Critical Test Scenarios
- Detailed Test Cases (10 suites)
- Execution Plan (4 phases)
- Coverage Goals

**When to use**:
- Planning testing work
- Understanding big picture
- Estimating effort
- Tracking progress

---

## Common Workflows

### Workflow 1: First Day Setup

1. Read `TEST_REQUIREMENTS.md` - Understand mission (15 min)
2. Setup environment following setup instructions (30 min)
3. Read `API_QUICK_REFERENCE.md` - Learn API (10 min)
4. Run existing test: `python test_paper_trading_simple.py` (5 min)
5. Read test report if exists: `TEST_EXECUTION_REPORT.md` (10 min)

**Total**: ~70 minutes

---

### Workflow 2: Writing New Tests

1. Check `API_QUICK_REFERENCE.md` for attribute names
2. Check `API_TESTING_GUIDE.md` for similar test example
3. Copy test pattern from guide
4. Modify for your specific test case
5. Run test: `pytest tests/unit/test_your_file.py -v`
6. If fails, check "Debugging Failed Tests" section
7. If passes, run coverage: `pytest --cov=... --cov-report=html`

---

### Workflow 3: Debugging Failed Test

1. Read error message completely
2. Check `API_QUICK_REFERENCE.md` "Common Errors and Fixes"
3. If AttributeError: Check "API Attributes Quick Lookup"
4. If TypeError: Check "Order Class Quick Reference"
5. Read actual code in `engines/paper_trading_broker_api.py`
6. Add print statements to see actual values
7. Still stuck? Read `API_TESTING_GUIDE.md` "Debugging Failed Tests"

---

### Workflow 4: Reporting Results

1. Run full test suite: `pytest tests/ -v`
2. Generate coverage: `pytest --cov=core --cov=engines --cov-report=html`
3. Document results using template in `TEST_REQUIREMENTS.md`
4. If bugs found, use bug report template
5. Update `TEST_EXECUTION_REPORT.md` with findings
6. Submit report with recommendations

---

## Files You'll Create

### Test Files
- `tests/unit/test_paper_trading_broker.py` - Unit tests for paper trading
- `tests/unit/test_backtest_engine.py` - Unit tests for backtest
- `tests/unit/test_database_manager.py` - Unit tests for database
- `tests/integration/test_bot_engine.py` - Integration tests
- `tests/e2e/test_workflows.py` - End-to-end tests

### Report Files
- `TEST_EXECUTION_REPORT.md` - Daily test results
- `BUG_REPORTS.md` - Bug tracking
- `COVERAGE_REPORT.md` - Coverage analysis
- `FINAL_TEST_REPORT.md` - Sign-off document

---

## Test Execution Commands

### Run Specific Test File
```bash
pytest tests/unit/test_paper_trading_broker.py -v
```

### Run Specific Test Class
```bash
pytest tests/unit/test_paper_trading_broker.py::TestSLTPExtraction -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_paper_trading_broker.py::TestSLTPExtraction::test_sl_extraction -v
```

### Run with Coverage
```bash
pytest tests/unit/test_paper_trading_broker.py \
  --cov=engines.paper_trading_broker_api \
  --cov-report=html
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Only Failed Tests
```bash
pytest --lf
```

### Run in Parallel (faster)
```bash
pytest tests/ -n auto
```

---

## Key Learnings from Previous Testing

### What Went Wrong
1. Tests assumed API structure without reading code
2. Used wrong Order class (assumed single class)
3. Tried to access `broker.orders` (doesn't exist)
4. 18/19 tests failed due to incorrect assumptions

### What to Do Differently
1. **READ THE CODE FIRST** before writing tests
2. Check if attributes exist before using them
3. Use correct Order class for context
4. Start with simple tests, then expand
5. Run tests incrementally (don't write 19 at once)

### Known Issues
- **Bug #1**: No `broker.orders` property (use `matching_engine.pending_orders`)
- **Bug #2**: Two different Order classes with different attributes
- **Coverage**: Only 6% baseline (need to improve to 85%)

---

## Success Criteria Reminder

Before sign-off for production:
- [ ] 85%+ overall coverage
- [ ] 95%+ coverage on critical modules (base_bot, engines)
- [ ] All Priority 1 tests passing (Paper Trading fixes)
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] No critical or high severity bugs
- [ ] All medium bugs documented with workarounds
- [ ] Test report submitted
- [ ] Final recommendation: GO/NO-GO

---

## Getting Help

### Questions About API
- Check `API_QUICK_REFERENCE.md` first
- Then read `API_TESTING_GUIDE.md`
- Still confused? Read actual code
- Last resort: Ask developer

### Questions About Testing Strategy
- Check `TEST_PLAN.md`
- See `TEST_REQUIREMENTS.md` for scope

### Questions About Specific Tests
- Check existing tests in `tests/` folder
- Look for similar test in `API_TESTING_GUIDE.md`
- Copy and modify pattern

---

## Tips for Success

1. **Read Before Writing**: Always read implementation before writing tests
2. **Start Small**: Write 1 test, make it pass, then write next
3. **Run Often**: Run tests after each change
4. **Mock Properly**: Always mock MT5 and external dependencies
5. **Check Coverage**: Aim for high coverage on critical code
6. **Document Everything**: Clear docstrings, bug reports, findings
7. **Ask Questions**: Better to ask than assume wrongly
8. **Be Objective**: Don't assume code is correct, find the bugs!

---

## Contact

**Developer**: Tran Trong Hieu (@thales1020)  
**Project**: QuantumTrader MT5  
**Repository**: https://github.com/thales1020/QuantumTrader-MT5

---

**Good luck with testing!**

Remember: Quality testing requires understanding the code first.
