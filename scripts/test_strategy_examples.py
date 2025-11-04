"""
Test script for new strategy examples

Tests:
1. Multi-Timeframe Strategy
2. Portfolio Strategy  
3. Custom Indicators Strategy

Checks:
- Import successful
- Instantiation successful
- get_strategy_info() works
- No syntax errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_multi_timeframe():
    """Test Multi-Timeframe Strategy"""
    print("\n" + "=" * 70)
    print("Testing Multi-Timeframe Strategy")
    print("=" * 70)
    
    try:
        from examples.strategies.multi_timeframe import MultiTimeframeStrategy
        import MetaTrader5 as mt5
        
        print("✅ Import successful")
        
        # Create config
        config = {
            'symbol': 'EURUSD',
            'timeframe': 'M15',
            'lower_timeframe': mt5.TIMEFRAME_M15,
            'higher_timeframe': mt5.TIMEFRAME_H1,
            'risk_percent': 1.0,
            'magic_number': 100001,
        }
        
        # Initialize
        bot = MultiTimeframeStrategy(config)
        print(f"✅ Instantiation successful: {bot.__class__.__name__}")
        
        # Get info
        info = bot.get_strategy_info()
        print(f"✅ Strategy info retrieved:")
        print(f"   Name: {info['name']}")
        print(f"   ID: {info['id']}")
        print(f"   Timeframes: {info['timeframes']}")
        
        print("\n🎉 Multi-Timeframe Strategy: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Multi-Timeframe Strategy FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_portfolio():
    """Test Portfolio Strategy"""
    print("\n" + "=" * 70)
    print("Testing Portfolio Strategy")
    print("=" * 70)
    
    try:
        from examples.strategies.portfolio import PortfolioStrategy
        import MetaTrader5 as mt5
        
        print("✅ Import successful")
        
        # Create config
        config = {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
            'timeframe': mt5.TIMEFRAME_H1,
            'total_risk_percent': 3.0,
            'max_positions': 3,
            'magic_number': 100002,
        }
        
        # Initialize
        bot = PortfolioStrategy(config)
        print(f"✅ Instantiation successful: {bot.__class__.__name__}")
        
        # Get info
        info = bot.get_strategy_info()
        print(f"✅ Strategy info retrieved:")
        print(f"   Name: {info['name']}")
        print(f"   ID: {info['id']}")
        print(f"   Symbols: {', '.join(info['symbols'])}")
        print(f"   Total Risk: {info['total_risk']}")
        
        print("\n🎉 Portfolio Strategy: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Portfolio Strategy FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_indicators():
    """Test Custom Indicators Strategy"""
    print("\n" + "=" * 70)
    print("Testing Custom Indicators Strategy")
    print("=" * 70)
    
    try:
        from examples.strategies.custom_indicators import CustomIndicatorStrategy
        import MetaTrader5 as mt5
        
        print("✅ Import successful")
        
        # Create config
        config = {
            'symbol': 'EURUSD',
            'timeframe': mt5.TIMEFRAME_H1,
            'risk_percent': 1.0,
            'tenkan_period': 9,
            'kijun_period': 26,
            'magic_number': 100003,
        }
        
        # Initialize
        bot = CustomIndicatorStrategy(config)
        print(f"✅ Instantiation successful: {bot.__class__.__name__}")
        
        # Get info
        info = bot.get_strategy_info()
        print(f"✅ Strategy info retrieved:")
        print(f"   Name: {info['name']}")
        print(f"   ID: {info['id']}")
        print(f"   Indicators: {list(info['indicators'].keys())}")
        
        print("\n🎉 Custom Indicators Strategy: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Custom Indicators Strategy FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("STRATEGY EXAMPLES TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test all strategies
    results.append(("Multi-Timeframe", test_multi_timeframe()))
    results.append(("Portfolio", test_portfolio()))
    results.append(("Custom Indicators", test_custom_indicators()))
    
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
