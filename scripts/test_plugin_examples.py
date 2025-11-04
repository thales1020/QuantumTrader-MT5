"""
Test script for plugin examples

Tests:
1. Advanced Risk Manager Plugin
2. Trade Analytics Plugin
3. Telegram Notifier Plugin

Checks:
- Import successful
- Instantiation successful
- Hook methods exist
- get_name() and get_version() work
- No syntax errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_risk_manager():
    """Test Advanced Risk Manager Plugin"""
    print("\n" + "=" * 70)
    print("Testing Advanced Risk Manager Plugin")
    print("=" * 70)
    
    try:
        from examples.plugins.advanced_risk_manager import AdvancedRiskManager
        
        print("✅ Import successful")
        
        # Create config
        config = {
            'max_daily_loss_percent': 2.0,
            'max_drawdown_percent': 10.0,
            'avoid_news_hours': True,
        }
        
        # Initialize
        plugin = AdvancedRiskManager(config)
        print(f"✅ Instantiation successful: {plugin.__class__.__name__}")
        
        # Check methods
        assert hasattr(plugin, 'before_trade'), "Missing before_trade hook"
        assert hasattr(plugin, 'after_trade'), "Missing after_trade hook"
        assert hasattr(plugin, 'on_position_close'), "Missing on_position_close hook"
        print("✅ All hook methods present")
        
        # Get info
        print(f"✅ Plugin name: {plugin.get_name()}")
        print(f"✅ Plugin version: {plugin.get_version()}")
        
        # Test functionality
        plugin.current_equity = 10000
        plugin.peak_equity = 10000
        
        trade_context = {
            'position_size': 0.1,
            'atr': 0.0015,
            'price': 1.1000,
            'account_balance': 10000,
        }
        
        result = plugin.validate_trade_risk(trade_context)
        print(f"✅ Risk validation works: approved={result['approved']}")
        
        print("\n🎉 Advanced Risk Manager Plugin: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Advanced Risk Manager Plugin FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics():
    """Test Trade Analytics Plugin"""
    print("\n" + "=" * 70)
    print("Testing Trade Analytics Plugin")
    print("=" * 70)
    
    try:
        from examples.plugins.trade_analytics import TradeAnalytics
        
        print("✅ Import successful")
        
        # Create config
        config = {
            'track_time_performance': True,
            'track_symbol_performance': True,
            'export_daily_report': False,
        }
        
        # Initialize
        plugin = TradeAnalytics(config)
        print(f"✅ Instantiation successful: {plugin.__class__.__name__}")
        
        # Check methods
        assert hasattr(plugin, 'after_trade'), "Missing after_trade hook"
        assert hasattr(plugin, 'on_position_close'), "Missing on_position_close hook"
        assert hasattr(plugin, 'daily_end'), "Missing daily_end hook"
        print("✅ All hook methods present")
        
        # Get info
        print(f"✅ Plugin name: {plugin.get_name()}")
        print(f"✅ Plugin version: {plugin.get_version()}")
        
        # Test functionality
        plugin.after_trade({
            'ticket': 'T001',
            'symbol': 'EURUSD',
            'type': 'BUY',
            'price': 1.1000,
            'position_size': 0.1,
        })
        
        plugin.on_position_close({
            'ticket': 'T001',
            'price': 1.1050,
            'profit': 50.00,
            'account_balance': 10000,
        })
        
        print(f"✅ Analytics tracking works: {plugin.total_trades} trade(s) recorded")
        
        report = plugin.generate_summary_report()
        print(f"✅ Report generation works: {len(report)} sections")
        
        print("\n🎉 Trade Analytics Plugin: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Trade Analytics Plugin FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_telegram_notifier():
    """Test Telegram Notifier Plugin"""
    print("\n" + "=" * 70)
    print("Testing Telegram Notifier Plugin")
    print("=" * 70)
    
    try:
        from examples.plugins.telegram_notifier import TelegramNotifier
        
        print("✅ Import successful")
        
        # Create config (demo mode)
        config = {
            'bot_token': '',  # Empty for demo
            'chat_id': '',
            'notify_trades': True,
            'use_emojis': True,
        }
        
        # Initialize
        plugin = TelegramNotifier(config)
        print(f"✅ Instantiation successful: {plugin.__class__.__name__}")
        
        # Check methods
        assert hasattr(plugin, 'after_trade'), "Missing after_trade hook"
        assert hasattr(plugin, 'on_position_close'), "Missing on_position_close hook"
        assert hasattr(plugin, 'daily_start'), "Missing daily_start hook"
        assert hasattr(plugin, 'daily_end'), "Missing daily_end hook"
        print("✅ All hook methods present")
        
        # Get info
        print(f"✅ Plugin name: {plugin.get_name()}")
        print(f"✅ Plugin version: {plugin.get_version()}")
        
        # Test functionality (demo mode)
        plugin.after_trade({
            'type': 'BUY',
            'symbol': 'EURUSD',
            'price': 1.1000,
            'position_size': 0.1,
        })
        print("✅ Trade notification works (demo mode)")
        
        plugin.on_position_close({
            'symbol': 'EURUSD',
            'price': 1.1050,
            'profit': 50.00,
        })
        print("✅ Exit notification works (demo mode)")
        
        print("\n🎉 Telegram Notifier Plugin: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Telegram Notifier Plugin FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("PLUGIN EXAMPLES TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test all plugins
    results.append(("Advanced Risk Manager", test_risk_manager()))
    results.append(("Trade Analytics", test_analytics()))
    results.append(("Telegram Notifier", test_telegram_notifier()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<50} {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
