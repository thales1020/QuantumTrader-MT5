"""
Test Paper Trading Fixes
========================

Tests the 3 TODO fixes in paper_trading_broker_api.py:
1. SL/TP extraction from orders
2. SL/TP monitoring and auto-close
3. P&L calculation

Author: Trần Trọng Hiếu
Date: November 5, 2025
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from engines.paper_trading_broker_api import PaperTradingBrokerAPI
from engines.database_manager import DatabaseManager
import logging
import colorlog

def setup_logger(name, log_dir="logs"):
    """Simple logger setup"""
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def test_sl_tp_extraction():
    """Test 1: Verify SL/TP extraction from orders"""
    print("\n" + "="*60)
    print("TEST 1: SL/TP Extraction from Orders")
    print("="*60)
    
    logger = setup_logger("test_paper_trading", log_dir="logs/tests")
    db = Database()
    
    broker = PaperTradingBrokerAPI(
        initial_balance=10000.0,
        leverage=100,
        database=db,
        logger=logger
    )
    
    # Submit order with SL/TP
    print("\n📝 Submitting BUY order with SL=1.0950 and TP=1.1100...")
    order = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,
        take_profit=1.1100
    )
    
    if order:
        print(f"✅ Order submitted: {order.order_id}")
        
        # Check if position has SL/TP
        if broker.positions:
            pos_id = list(broker.positions.keys())[0]
            pos = broker.positions[pos_id]
            
            print(f"\n📊 Position created: {pos_id}")
            print(f"   Entry Price: {pos.entry_price}")
            print(f"   Stop Loss: {pos.stop_loss}")
            print(f"   Take Profit: {pos.take_profit}")
            
            if pos.stop_loss and pos.take_profit:
                print("\n✅ TEST 1 PASSED: SL/TP extracted from order successfully!")
                return True
            else:
                print("\n❌ TEST 1 FAILED: SL/TP not set on position")
                return False
        else:
            print("\n❌ TEST 1 FAILED: No position created")
            return False
    else:
        print("\n❌ TEST 1 FAILED: Order submission failed")
        return False


def test_stop_loss_trigger():
    """Test 2: Verify Stop Loss auto-close"""
    print("\n" + "="*60)
    print("TEST 2: Stop Loss Trigger")
    print("="*60)
    
    logger = setup_logger("test_paper_trading", log_dir="logs/tests")
    db = Database()
    
    broker = PaperTradingBrokerAPI(
        initial_balance=10000.0,
        leverage=100,
        database=db,
        logger=logger
    )
    
    # Submit BUY order with SL below current price
    print("\n📝 Submitting BUY order at ~1.1000 with SL=1.0950...")
    order = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0950,  # 50 pips below entry
        take_profit=1.1100
    )
    
    if not order or not broker.positions:
        print("\n❌ TEST 2 FAILED: Could not create position")
        return False
    
    pos_id = list(broker.positions.keys())[0]
    pos = broker.positions[pos_id]
    entry_price = pos.entry_price
    
    print(f"\n✅ Position opened:")
    print(f"   Position ID: {pos_id}")
    print(f"   Entry: {entry_price}")
    print(f"   SL: {pos.stop_loss}")
    
    # Simulate price going down to hit SL
    print(f"\n📉 Simulating price drop to hit SL...")
    
    # Create bar that hits SL
    sl_bar = {
        'time': datetime.now(),
        'open': entry_price - 0.0020,  # 20 pips below entry
        'high': entry_price - 0.0010,  # 10 pips below entry
        'low': pos.stop_loss - 0.0005,  # 5 pips below SL (hits SL)
        'close': entry_price - 0.0030,  # 30 pips below entry
        'volume': 100
    }
    
    initial_balance = broker.balance
    
    # Update positions with SL-hitting bar
    broker._update_positions("EURUSD", sl_bar)
    
    # Check if position was closed
    if pos_id not in broker.positions:
        print(f"\n✅ Position auto-closed by Stop Loss!")
        
        # Check if trade was saved
        trades = db.get_all_trades()
        if trades and len(trades) > 0:
            last_trade = trades[-1]
            print(f"\n📊 Trade Details:")
            print(f"   Exit Reason: {last_trade.exit_reason}")
            print(f"   Entry: {last_trade.entry_price}")
            print(f"   Exit: {last_trade.exit_price}")
            print(f"   Gross P&L: ${last_trade.gross_pnl:.2f}")
            print(f"   Net P&L: ${last_trade.net_pnl:.2f}")
            
            final_balance = broker.balance
            balance_change = final_balance - initial_balance
            print(f"\n💰 Balance:")
            print(f"   Initial: ${initial_balance:.2f}")
            print(f"   Final: ${final_balance:.2f}")
            print(f"   Change: ${balance_change:.2f}")
            
            if last_trade.exit_reason == "Stop Loss" and balance_change < 0:
                print("\n✅ TEST 2 PASSED: Stop Loss triggered and P&L calculated!")
                return True
            else:
                print("\n❌ TEST 2 FAILED: Trade record incorrect")
                return False
        else:
            print("\n❌ TEST 2 FAILED: Trade not saved to database")
            return False
    else:
        print(f"\n❌ TEST 2 FAILED: Position still open (should be closed)")
        print(f"   Current unrealized P&L: ${pos.unrealized_pnl:.2f}")
        return False


def test_take_profit_trigger():
    """Test 3: Verify Take Profit auto-close"""
    print("\n" + "="*60)
    print("TEST 3: Take Profit Trigger")
    print("="*60)
    
    logger = setup_logger("test_paper_trading", log_dir="logs/tests")
    db = Database()
    
    broker = PaperTradingBrokerAPI(
        initial_balance=10000.0,
        leverage=100,
        database=db,
        logger=logger
    )
    
    # Submit BUY order with TP above current price
    print("\n📝 Submitting BUY order at ~1.1000 with TP=1.1100...")
    order = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1,
        stop_loss=1.0900,
        take_profit=1.1100  # 100 pips above entry
    )
    
    if not order or not broker.positions:
        print("\n❌ TEST 3 FAILED: Could not create position")
        return False
    
    pos_id = list(broker.positions.keys())[0]
    pos = broker.positions[pos_id]
    entry_price = pos.entry_price
    
    print(f"\n✅ Position opened:")
    print(f"   Position ID: {pos_id}")
    print(f"   Entry: {entry_price}")
    print(f"   TP: {pos.take_profit}")
    
    # Simulate price going up to hit TP
    print(f"\n📈 Simulating price rise to hit TP...")
    
    # Create bar that hits TP
    tp_bar = {
        'time': datetime.now(),
        'open': entry_price + 0.0020,  # 20 pips above entry
        'high': pos.take_profit + 0.0005,  # 5 pips above TP (hits TP)
        'low': entry_price + 0.0010,  # 10 pips above entry
        'close': entry_price + 0.0080,  # 80 pips above entry
        'volume': 100
    }
    
    initial_balance = broker.balance
    
    # Update positions with TP-hitting bar
    broker._update_positions("EURUSD", tp_bar)
    
    # Check if position was closed
    if pos_id not in broker.positions:
        print(f"\n✅ Position auto-closed by Take Profit!")
        
        # Check if trade was saved
        trades = db.get_all_trades()
        if trades and len(trades) > 0:
            last_trade = trades[-1]
            print(f"\n📊 Trade Details:")
            print(f"   Exit Reason: {last_trade.exit_reason}")
            print(f"   Entry: {last_trade.entry_price}")
            print(f"   Exit: {last_trade.exit_price}")
            print(f"   Gross P&L: ${last_trade.gross_pnl:.2f}")
            print(f"   Net P&L: ${last_trade.net_pnl:.2f}")
            
            final_balance = broker.balance
            balance_change = final_balance - initial_balance
            print(f"\n💰 Balance:")
            print(f"   Initial: ${initial_balance:.2f}")
            print(f"   Final: ${final_balance:.2f}")
            print(f"   Change: ${balance_change:.2f}")
            
            if last_trade.exit_reason == "Take Profit" and balance_change > 0:
                print("\n✅ TEST 3 PASSED: Take Profit triggered and P&L calculated!")
                return True
            else:
                print("\n❌ TEST 3 FAILED: Trade record incorrect")
                return False
        else:
            print("\n❌ TEST 3 FAILED: Trade not saved to database")
            return False
    else:
        print(f"\n❌ TEST 3 FAILED: Position still open (should be closed)")
        print(f"   Current unrealized P&L: ${pos.unrealized_pnl:.2f}")
        return False


def test_pnl_calculation():
    """Test 4: Verify P&L calculation accuracy"""
    print("\n" + "="*60)
    print("TEST 4: P&L Calculation Accuracy")
    print("="*60)
    
    logger = setup_logger("test_paper_trading", log_dir="logs/tests")
    db = Database()
    
    broker = PaperTradingBrokerAPI(
        initial_balance=10000.0,
        leverage=100,
        database=db,
        logger=logger
    )
    
    # Submit order
    print("\n📝 Submitting BUY 0.1 lot EURUSD...")
    order = broker.submit_order(
        symbol="EURUSD",
        order_type="MARKET",
        side="BUY",
        quantity=0.1
    )
    
    if not order or not broker.positions:
        print("\n❌ TEST 4 FAILED: Could not create position")
        return False
    
    pos_id = list(broker.positions.keys())[0]
    pos = broker.positions[pos_id]
    entry_price = pos.entry_price
    
    print(f"\n✅ Position opened:")
    print(f"   Entry Price: {entry_price}")
    print(f"   Lot Size: {pos.lot_size}")
    
    # Close with 50 pips profit
    exit_price = entry_price + 0.0050  # +50 pips
    
    print(f"\n📊 Closing position manually at {exit_price} (+50 pips)...")
    
    initial_balance = broker.balance
    broker.close_position(pos_id)
    final_balance = broker.balance
    
    # Expected calculation:
    # Gross P&L = (exit - entry) * lot_size * 100000
    # = (0.0050) * 0.1 * 100000 = 50 USD
    # Net P&L = Gross - (commission + swap + spread)
    
    expected_gross = 0.0050 * 0.1 * 100000  # 50 USD
    
    trades = db.get_all_trades()
    if trades and len(trades) > 0:
        last_trade = trades[-1]
        
        print(f"\n📊 P&L Breakdown:")
        print(f"   Gross P&L: ${last_trade.gross_pnl:.2f} (expected: ${expected_gross:.2f})")
        print(f"   Commission: ${last_trade.commission:.2f}")
        print(f"   Swap: ${last_trade.swap:.2f}")
        print(f"   Spread: ~${(last_trade.gross_pnl - last_trade.net_pnl - last_trade.commission - last_trade.swap):.2f}")
        print(f"   Net P&L: ${last_trade.net_pnl:.2f}")
        
        balance_change = final_balance - initial_balance
        print(f"\n💰 Balance Change: ${balance_change:.2f}")
        
        # Verify calculation
        gross_pnl_correct = abs(last_trade.gross_pnl - expected_gross) < 1.0  # Within $1
        balance_matches_net = abs(balance_change - last_trade.net_pnl) < 0.01  # Within 1 cent
        
        if gross_pnl_correct and balance_matches_net:
            print("\n✅ TEST 4 PASSED: P&L calculation accurate!")
            print(f"   ✓ Gross P&L matches expected value")
            print(f"   ✓ Balance change matches Net P&L")
            return True
        else:
            print("\n❌ TEST 4 FAILED: P&L calculation mismatch")
            if not gross_pnl_correct:
                print(f"   ✗ Gross P&L error: ${abs(last_trade.gross_pnl - expected_gross):.2f}")
            if not balance_matches_net:
                print(f"   ✗ Balance mismatch: ${abs(balance_change - last_trade.net_pnl):.2f}")
            return False
    else:
        print("\n❌ TEST 4 FAILED: Trade not saved")
        return False


def main():
    """Run all paper trading tests"""
    print("\n" + "="*60)
    print("PAPER TRADING FIX VALIDATION TESTS")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing 3 TODO fixes in paper_trading_broker_api.py")
    
    results = []
    
    try:
        # Test 1: SL/TP extraction
        results.append(("SL/TP Extraction", test_sl_tp_extraction()))
        
        # Test 2: Stop Loss trigger
        results.append(("Stop Loss Trigger", test_stop_loss_trigger()))
        
        # Test 3: Take Profit trigger
        results.append(("Take Profit Trigger", test_take_profit_trigger()))
        
        # Test 4: P&L calculation
        results.append(("P&L Calculation", test_pnl_calculation()))
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED WITH ERROR:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Paper trading fixes are working correctly!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
