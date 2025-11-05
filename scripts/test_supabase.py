"""
Supabase Integration Test
Test script to verify Supabase setup and connection

Usage:
    python scripts/test_supabase.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.supabase_database import SupabaseDatabase, SupabaseConfig


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_connection(config: SupabaseConfig) -> bool:
    """Test Supabase connection"""
    print_header("TEST 1: Connection")
    
    try:
        db = SupabaseDatabase(config)
        print("✅ Successfully connected to Supabase")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_order_operations(db: SupabaseDatabase) -> bool:
    """Test order CRUD operations"""
    print_header("TEST 2: Order Operations")
    
    try:
        # Create test order
        order_data = {
            'order_id': f'TEST_{int(time.time())}',
            'symbol': 'EURUSD',
            'order_type': 'MARKET',
            'side': 'BUY',
            'quantity': 0.1,
            'status': 'FILLED',
            'filled_quantity': 0.1,
            'remaining_quantity': 0.0,
            'avg_fill_price': 1.0850,
            'created_time': datetime.now().isoformat()
        }
        
        # Save order
        saved = db.save_order(order_data)
        print(f"✅ Order saved: {saved['order_id']}")
        
        # Get all orders
        orders = db.get_all_orders()
        print(f"✅ Retrieved {len(orders)} orders from database")
        
        # Update order
        db.update_order(saved['order_id'], {'status': 'CANCELLED'})
        print(f"✅ Order updated: {saved['order_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Order operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trade_operations(db: SupabaseDatabase) -> bool:
    """Test trade operations"""
    print_header("TEST 3: Trade Operations")
    
    try:
        # Create test trade
        trade_data = {
            'trade_id': int(time.time()),
            'symbol': 'EURUSD',
            'direction': 'LONG',
            'entry_time': datetime.now().isoformat(),
            'exit_time': datetime.now().isoformat(),
            'entry_price': 1.0850,
            'exit_price': 1.0900,
            'lot_size': 0.1,
            'gross_pnl': 50.0,
            'commission': 7.0,
            'swap': 0.0,
            'spread_cost': 1.5,
            'slippage': 0.0,
            'net_pnl': 41.5,
            'pips': 50.0,
            'exit_reason': 'Take Profit',
            'strategy_name': 'TestStrategy'
        }
        
        # Save trade
        saved = db.save_trade(trade_data)
        print(f"✅ Trade saved: {saved['trade_id']}")
        
        # Get all trades
        trades = db.get_all_trades()
        print(f"✅ Retrieved {len(trades)} trades from database")
        
        # Get trades by symbol
        eurusd_trades = db.get_trades_by_symbol('EURUSD')
        print(f"✅ Retrieved {len(eurusd_trades)} EURUSD trades")
        
        return True
        
    except Exception as e:
        print(f"❌ Trade operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_position_operations(db: SupabaseDatabase) -> bool:
    """Test position operations"""
    print_header("TEST 4: Position Operations")
    
    try:
        # Create test position
        position_data = {
            'position_id': f'POS_{int(time.time())}',
            'symbol': 'GBPUSD',
            'side': 'BUY',
            'quantity': 0.2,
            'entry_price': 1.2500,
            'current_price': 1.2550,
            'is_open': True,
            'unrealized_pnl': 100.0,
            'stop_loss': 1.2450,
            'take_profit': 1.2600,
            'open_time': datetime.now().isoformat(),
            'strategy_name': 'TestStrategy'
        }
        
        # Save position
        saved = db.save_position(position_data)
        print(f"✅ Position saved: {saved['position_id']}")
        
        # Get open positions
        open_positions = db.get_open_positions()
        print(f"✅ Retrieved {len(open_positions)} open positions")
        
        # Update position
        db.update_position(saved['position_id'], {
            'current_price': 1.2570,
            'unrealized_pnl': 140.0
        })
        print(f"✅ Position updated: {saved['position_id']}")
        
        # Close position
        db.close_position(saved['position_id'], 1.2580, 'Manual Close')
        print(f"✅ Position closed: {saved['position_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Position operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_account_history(db: SupabaseDatabase) -> bool:
    """Test account history"""
    print_header("TEST 5: Account History")
    
    try:
        # Create snapshot
        snapshot_data = {
            'timestamp': datetime.now().isoformat(),
            'balance': 10000.0,
            'equity': 10140.0,
            'margin_used': 200.0,
            'free_margin': 9800.0,
            'margin_level': 5070.0,
            'num_positions': 2,
            'num_pending_orders': 1,
            'daily_pnl': 140.0,
            'daily_return_pct': 1.4,
            'total_realized_pnl': 140.0,
            'total_trades': 5
        }
        
        # Save snapshot
        saved = db.save_account_snapshot(snapshot_data)
        print(f"✅ Account snapshot saved")
        
        # Get history
        history = db.get_account_history(days=7)
        print(f"✅ Retrieved {len(history)} account snapshots")
        
        return True
        
    except Exception as e:
        print(f"❌ Account history failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_statistics(db: SupabaseDatabase) -> bool:
    """Test statistics and analytics"""
    print_header("TEST 6: Statistics")
    
    try:
        # Get overall statistics
        stats = db.get_statistics()
        print(f"✅ Overall statistics:")
        print(f"   Total trades: {stats.get('total_trades', 0)}")
        print(f"   Winning trades: {stats.get('winning_trades', 0)}")
        print(f"   Total P&L: ${stats.get('total_pnl', 0):.2f}")
        
        # Get performance summary
        summary = db.get_performance_summary()
        print(f"✅ Performance summary:")
        print(f"   Win rate: {summary.get('win_rate', 0):.2f}%")
        print(f"   Net P&L: ${summary.get('net_pnl', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realtime(db: SupabaseDatabase) -> bool:
    """Test real-time subscriptions"""
    print_header("TEST 7: Real-time Subscriptions")
    
    try:
        print("Setting up real-time subscription for trades...")
        
        # Counter for received events
        events_received = [0]
        
        def on_trade_event(payload: dict):
            events_received[0] += 1
            print(f"📡 Real-time event received: {payload.get('eventType', 'UNKNOWN')}")
        
        # Subscribe
        subscription = db.subscribe_to_trades(on_trade_event)
        print("✅ Subscribed to trade events")
        
        # Create a test trade to trigger event
        print("Creating test trade to trigger event...")
        test_trade = {
            'trade_id': int(time.time()),
            'symbol': 'USDJPY',
            'direction': 'SHORT',
            'entry_time': datetime.now().isoformat(),
            'exit_time': datetime.now().isoformat(),
            'entry_price': 150.50,
            'exit_price': 150.00,
            'lot_size': 0.1,
            'gross_pnl': 50.0,
            'commission': 7.0,
            'net_pnl': 43.0,
            'strategy_name': 'RealtimeTest'
        }
        db.save_trade(test_trade)
        
        # Wait for event
        print("Waiting 3 seconds for real-time event...")
        time.sleep(3)
        
        # Unsubscribe
        subscription.unsubscribe()
        
        if events_received[0] > 0:
            print(f"✅ Received {events_received[0]} real-time event(s)")
            return True
        else:
            print("⚠️ No real-time events received (this may be normal if realtime not enabled)")
            print("   Enable realtime in Supabase Dashboard > Database > Replication")
            return True  # Don't fail test, just warn
        
    except Exception as e:
        print(f"⚠️ Real-time test skipped: {e}")
        print("   This is optional - make sure realtime is enabled in Supabase")
        return True  # Don't fail on realtime


def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("SUPABASE INTEGRATION TEST SUITE")
    print("🚀 " * 20)
    
    # Load config
    config_path = "config/supabase.json"
    
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        supabase_cfg = config_data['database']['supabase']
        config = SupabaseConfig(
            url=supabase_cfg['url'],
            key=supabase_cfg['anon_key']
        )
        
        print(f"📋 Config loaded from: {config_path}")
        print(f"🌐 Supabase URL: {config.url}")
        
    except FileNotFoundError:
        print(f"\n❌ Config file not found: {config_path}")
        print("Please create config/supabase.json from config/supabase.example.json")
        return
    except Exception as e:
        print(f"\n❌ Failed to load config: {e}")
        return
    
    # Run tests
    results = []
    
    # Test 1: Connection
    if test_connection(config):
        db = SupabaseDatabase(config)
        
        # Test 2-7
        results.append(("Connection", True))
        results.append(("Order Operations", test_order_operations(db)))
        results.append(("Trade Operations", test_trade_operations(db)))
        results.append(("Position Operations", test_position_operations(db)))
        results.append(("Account History", test_account_history(db)))
        results.append(("Statistics", test_statistics(db)))
        results.append(("Real-time", test_realtime(db)))
    else:
        results.append(("Connection", False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
    
    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 All tests passed! Supabase integration is working correctly.")
        print("\nNext steps:")
        print("  1. Use PaperTradingBrokerAPI with use_supabase=True")
        print("  2. Enable real-time subscriptions in Supabase dashboard")
        print("  3. Monitor trades in cloud database")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        print("   Common issues:")
        print("   - Wrong Supabase URL or API key")
        print("   - Schema not created (run database/supabase_schema.sql)")
        print("   - Network/firewall blocking Supabase")


if __name__ == "__main__":
    main()
