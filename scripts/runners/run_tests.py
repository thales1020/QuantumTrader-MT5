#!/usr/bin/env python3
"""
Test Runner for ML-SuperTrend-MT5
Run all or specific test suites
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all available tests"""
    print("=" * 70)
    print("Running All Core Tests (Config + Risk + Live Trading)")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add core tests that don't require SMC library
    suite.addTests(loader.loadTestsFromName('tests.test_configuration'))
    suite.addTests(loader.loadTestsFromName('tests.test_risk_management'))
    suite.addTests(loader.loadTestsFromName('tests.test_live_trading'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n[OK] ALL TESTS PASSED - System ready for demo trading!")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED - Review errors above")
        return 1

def run_configuration_tests():
    """Run configuration tests only"""
    print("=" * 70)
    print("Running Configuration Tests")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_configuration')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def run_risk_tests():
    """Run risk management tests only"""
    print("=" * 70)
    print("Running Risk Management Tests")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_risk_management')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def run_live_tests():
    """Run live trading tests only"""
    print("=" * 70)
    print("Running Live Trading Tests")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_live_trading')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def print_usage():
    """Print usage information"""
    print("ML-SuperTrend-MT5 Test Runner")
    print("")
    print("Usage: python run_tests.py [option]")
    print("")
    print("Options:")
    print("  --all         Run all core tests (default)")
    print("  --config      Run configuration tests only")
    print("  --risk        Run risk management tests only")
    print("  --live        Run live trading tests only")
    print("  --help        Show this help message")
    print("")
    print("Examples:")
    print("  python run_tests.py")
    print("  python run_tests.py --all")
    print("  python run_tests.py --config")
    print("  python run_tests.py --live")
    print("")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        if option in ['--help', '-h']:
            print_usage()
            sys.exit(0)
        elif option in ['--config', '-c']:
            sys.exit(run_configuration_tests())
        elif option in ['--risk', '-r']:
            sys.exit(run_risk_tests())
        elif option in ['--live', '-l']:
            sys.exit(run_live_tests())
        elif option in ['--all', '-a']:
            sys.exit(run_all_tests())
        else:
            print(f"Unknown option: {option}")
            print("")
            print_usage()
            sys.exit(1)
    else:
        # Default: run all tests
        sys.exit(run_all_tests())
