"""Quick test for EURUSD Breakout strategy"""

from strategies.eurusd_breakout import EurusdBreakout

print("Testing EURUSD Breakout strategy...\n")

# Test import
print("✅ Import successful")

# Test instantiation
config = {'bb_period': 15, 'bb_std': 2.5}
bot = EurusdBreakout(config)
print(f"✅ Instantiation successful: {bot.__class__.__name__}")

# Test get_strategy_info
info = bot.get_strategy_info()
print(f"✅ Strategy info retrieved:")
print(f"   Name: {info['name']}")
print(f"   ID: {info['id']}")
print(f"   Class: {bot.__class__.__name__}")

print("\n🎉 All tests passed!")
