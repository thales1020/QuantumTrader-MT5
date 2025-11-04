#!/usr/bin/env python
"""
Template Validation Script

Tests all strategy templates by generating strategies and validating them.

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.template_system import TemplateManager, StrategyGenerator, TemplateValidator
import tempfile
import shutil
import ast
import importlib.util


def print_header(text):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def validate_python_syntax(code, filename):
    """Validate Python code syntax"""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in {filename} at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error parsing {filename}: {str(e)}"


def test_template_generation(template_mgr, generator, template_name, test_params, temp_dir):
    """Test generating a strategy from a template"""
    print(f"Testing template: {template_name}")
    
    # Get template metadata
    template = template_mgr.get_template(template_name)
    
    # Create test variables
    strategy_id = f"test_{template_name}"
    variables = {
        'STRATEGY_NAME': f"Test {template_name.replace('_', ' ').title()}",
        'STRATEGY_CLASS_NAME': ''.join(word.capitalize() for word in strategy_id.split('_')),
        'STRATEGY_ID': strategy_id,
        'STRATEGY_DESCRIPTION': f"Test strategy for {template_name} template"
    }
    
    # Add template-specific test parameters
    if test_params:
        variables.update(test_params)
    
    # Generate strategy
    output_path = temp_dir / f"{strategy_id}.py"
    
    try:
        result_path = generator.generate_strategy(
            template_name=template_name,
            output_path=output_path,
            variables=variables,
            overwrite=True
        )
        
        # Read generated code
        code = result_path.read_text(encoding='utf-8')
        
        # Validate syntax
        is_valid, error = validate_python_syntax(code, result_path.name)
        
        if not is_valid:
            print(f"  ❌ FAILED: {error}")
            return False
        
        # Check for unreplaced variables
        validator = TemplateValidator()
        unreplaced = validator.find_unreplaced_variables(code)
        
        if unreplaced:
            print(f"  ⚠️  WARNING: Unreplaced variables: {unreplaced}")
        
        # Try to import (without MT5 dependencies)
        print(f"  ✅ PASSED: Generated valid Python code ({len(code)} chars)")
        print(f"     File: {result_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: {str(e)}")
        return False


def test_all_templates():
    """Test all templates"""
    print_header("Template Validation Test Suite")
    
    # Initialize template system
    print("Initializing template system...")
    template_mgr = TemplateManager()
    template_mgr.load_templates()
    generator = StrategyGenerator(template_mgr)
    
    print(f"Loaded {len(template_mgr.templates)} templates")
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="template_test_"))
    print(f"Test directory: {temp_dir}\n")
    
    # Test configurations for each template
    test_configs = {
        'ma_crossover': [
            # Default SMA
            {'FAST_PERIOD': 10, 'SLOW_PERIOD': 30, 'MA_TYPE': 'SMA'},
            # EMA Golden Cross
            {'FAST_PERIOD': 50, 'SLOW_PERIOD': 200, 'MA_TYPE': 'EMA'},
            # WMA Quick
            {'FAST_PERIOD': 5, 'SLOW_PERIOD': 15, 'MA_TYPE': 'WMA'}
        ],
        'rsi_mean_reversion': [
            # Default
            {'RSI_PERIOD': 14, 'OVERSOLD_LEVEL': 30, 'OVERBOUGHT_LEVEL': 70},
            # Conservative
            {'RSI_PERIOD': 14, 'OVERSOLD_LEVEL': 25, 'OVERBOUGHT_LEVEL': 75,
             'TP_MULTIPLIER': 3.0, 'SL_MULTIPLIER': 2.0},
            # Aggressive
            {'RSI_PERIOD': 9, 'OVERSOLD_LEVEL': 35, 'OVERBOUGHT_LEVEL': 65,
             'TP_MULTIPLIER': 1.5, 'SL_MULTIPLIER': 1.0}
        ],
        'breakout': [
            # Default
            {'BB_PERIOD': 20, 'BB_STD': 2.0, 'VOLUME_MULTIPLIER': 1.5},
            # Wide bands
            {'BB_PERIOD': 20, 'BB_STD': 2.5, 'VOLUME_MULTIPLIER': 2.0,
             'TRAILING_ATR': 3.0, 'MAX_BARS': 100},
            # Tight bands
            {'BB_PERIOD': 15, 'BB_STD': 1.5, 'VOLUME_MULTIPLIER': 1.2,
             'TRAILING_ATR': 1.5, 'MAX_BARS': 30}
        ],
        'grid_trading': [
            # Conservative grid
            {'GRID_SIZE': 100, 'NUM_LEVELS': 5, 'LOT_SIZE': 0.01,
             'TAKE_PROFIT': 100, 'MAX_POSITIONS': 10},
            # Standard grid
            {'GRID_SIZE': 50, 'NUM_LEVELS': 10, 'LOT_SIZE': 0.01,
             'TAKE_PROFIT': 50, 'MAX_POSITIONS': 20},
            # Aggressive grid
            {'GRID_SIZE': 20, 'NUM_LEVELS': 20, 'LOT_SIZE': 0.01,
             'TAKE_PROFIT': 30, 'MAX_POSITIONS': 40}
        ],
        'multi_indicator': [
            # Balanced
            {'RSI_WEIGHT': 0.25, 'MACD_WEIGHT': 0.25, 'BB_WEIGHT': 0.25,
             'STOCH_WEIGHT': 0.25, 'THRESHOLD': 0.7},
            # MACD focused
            {'RSI_WEIGHT': 0.20, 'MACD_WEIGHT': 0.50, 'BB_WEIGHT': 0.15,
             'STOCH_WEIGHT': 0.15, 'THRESHOLD': 0.6},
            # High threshold
            {'RSI_WEIGHT': 0.25, 'MACD_WEIGHT': 0.30, 'BB_WEIGHT': 0.25,
             'STOCH_WEIGHT': 0.20, 'THRESHOLD': 0.8}
        ]
    }
    
    # Run tests
    results = {}
    total_tests = 0
    passed_tests = 0
    
    for template_name in sorted(template_mgr.templates.keys()):
        print_header(f"Testing: {template_name}")
        
        configs = test_configs.get(template_name, [{}])
        template_results = []
        
        for idx, config in enumerate(configs, 1):
            print(f"\n[Config {idx}/{len(configs)}]")
            if config:
                print(f"Parameters: {config}")
            
            total_tests += 1
            success = test_template_generation(
                template_mgr, generator, template_name, config, temp_dir
            )
            
            if success:
                passed_tests += 1
            
            template_results.append(success)
        
        results[template_name] = template_results
    
    # Summary
    print_header("Test Summary")
    
    print(f"Total tests run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    print("Results by template:")
    for template_name, template_results in sorted(results.items()):
        passed = sum(template_results)
        total = len(template_results)
        status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
        print(f"  {status} {template_name}: {passed}/{total} tests passed")
    
    # Cleanup
    print(f"\nCleaning up test directory: {temp_dir}")
    shutil.rmtree(temp_dir)
    
    # Return exit code
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!\n")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(test_all_templates())
