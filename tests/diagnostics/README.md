# Diagnostic Tools

Diagnostic and verification scripts for troubleshooting and analysis.

## Files

- `diagnose_ict_signal.py` - ICT signal generation diagnostics
- `verify_crypto_dual_orders.py` - Crypto dual order system verification

## Usage

### ICT Signal Diagnostics

Diagnose ICT strategy signal generation issues:

```bash
cd tests/diagnostics
python diagnose_ict_signal.py
```

**Purpose**: 
- Verify ICT signal logic
- Check FVG (Fair Value Gap) detection
- Validate order block identification
- Debug signal generation problems

### Crypto Dual Orders Verification

Verify cryptocurrency dual order system:

```bash
cd tests/diagnostics
python verify_crypto_dual_orders.py
```

**Purpose**:
- Verify long + short order placement
- Check position management
- Validate dual order closing logic
- Test crypto-specific features

## When to Use

Use diagnostic tools when:
- ❌ Strategy not generating expected signals
- ❌ Orders not executing as expected
- ❌ Position management issues
- ❌ Need to verify specific feature behavior
- 🔍 Troubleshooting production issues
- 📊 Analyzing strategy performance

## Output

Diagnostic scripts provide detailed output:
- Step-by-step execution trace
- Signal generation details
- Order placement confirmation
- Error messages and warnings
- Performance metrics

## Notes

⚠️ **Note**: These are diagnostic tools, not automated tests. Review output manually.

💡 **Tip**: Redirect output to file for detailed analysis:
```bash
python diagnose_ict_signal.py > diagnosis.log 2>&1
```
