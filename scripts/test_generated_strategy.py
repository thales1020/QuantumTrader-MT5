"""Test importing generated strategies"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import_ema_golden_cross():
    """Test importing EMA Golden Cross strategy"""
    print("Testing EMA Golden Cross import...")
    
    try:
        from strategies.ema_golden_cross import EmaGoldenCross
        print("  ✅ Import successful")
        
        # Test instantiation
        config = {
            'symbol': 'EURUSD',
            'timeframe': 'M15',
            'risk_percent': 1.0,
            'magic_number': 123456,
            'fast_period': 50,
            'slow_period': 200,
            'ma_type': 'EMA'
        }
        
        bot = EmaGoldenCross(config)
        print(f"  ✅ Instantiation successful: {bot.__class__.__name__}")
        
        # Test get_strategy_info
        info = bot.get_strategy_info()
        print(f"  ✅ Strategy info retrieved: {info['name']}")
        print(f"     Class: {info['class']}")
        print(f"     ID: {info['id']}")
        print(f"     Template: {info['template']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  Generated Strategy Import Test")
    print("=" * 60 + "\n")
    
    success = test_import_ema_golden_cross()
    
    print("\n" + "=" * 60)
    if success:
        print("  ✅ All import tests passed!")
    else:
        print("  ❌ Import test failed")
    print("=" * 60 + "\n")
    
    sys.exit(0 if success else 1)
