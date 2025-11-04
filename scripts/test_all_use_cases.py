"""
Test All Use Cases

Run all use case simulations to demonstrate plugin system capabilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import logging
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_all_use_cases():
    """Run all use case simulations"""
    
    logger.info("=" * 80)
    logger.info(" RUNNING ALL PLUGIN SYSTEM USE CASES")
    logger.info("=" * 80)
    
    use_cases = [
        {
            'name': 'Conservative Trading',
            'file': 'examples.use_cases.use_case_1_conservative',
            'description': 'Multiple filters for high-quality signals only'
        },
        {
            'name': 'Aggressive Scalping',
            'file': 'examples.use_cases.use_case_2_scalping',
            'description': 'No filters, maximum trading opportunities'
        },
        {
            'name': 'Risk Management',
            'file': 'examples.use_cases.use_case_3_risk_management',
            'description': 'Custom plugins for capital protection'
        }
    ]
    
    results = []
    
    for i, use_case in enumerate(use_cases, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"USE CASE {i}/{ len(use_cases)}: {use_case['name']}")
        logger.info(f"Description: {use_case['description']}")
        logger.info(f"{'=' * 80}\n")
        
        try:
            # Import and run the use case
            module = __import__(use_case['file'], fromlist=['simulate'])
            
            # Find the simulate function (pattern: simulate_*)
            simulate_func = None
            for attr_name in dir(module):
                if attr_name.startswith('simulate_'):
                    simulate_func = getattr(module, attr_name)
                    break
            
            if simulate_func:
                simulate_func()
                results.append({
                    'use_case': use_case['name'],
                    'status': 'PASSED ✅'
                })
            else:
                logger.error(f"No simulation function found in {use_case['file']}")
                results.append({
                    'use_case': use_case['name'],
                    'status': 'FAILED ❌ (no simulate function)'
                })
            
        except Exception as e:
            logger.error(f"Error running {use_case['name']}: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'use_case': use_case['name'],
                'status': f'FAILED ❌ ({str(e)})'
            })
        
        logger.info(f"\n{'=' * 80}\n")
    
    # Print summary
    logger.info("=" * 80)
    logger.info(" SUMMARY")
    logger.info("=" * 80)
    
    for result in results:
        logger.info(f"{result['use_case']:<30} {result['status']}")
    
    logger.info("=" * 80)
    
    # Check if all passed
    all_passed = all('PASSED' in r['status'] for r in results)
    
    if all_passed:
        logger.info("\n✅ ALL USE CASES PASSED!")
        logger.info("\nPlugin system is working correctly.")
        logger.info("\nNext steps:")
        logger.info("1. Configure Telegram credentials in use cases")
        logger.info("2. Test with demo MT5 account")
        logger.info("3. Run live with small positions")
    else:
        logger.error("\n❌ SOME USE CASES FAILED")
        logger.error("Check errors above for details")
        return 1
    
    return 0


def run_specific_use_case(use_case_number: int):
    """Run a specific use case by number"""
    
    use_cases = {
        1: ('Use Case 1: Conservative Trading', 'examples.use_cases.use_case_1_conservative'),
        2: ('Use Case 2: Aggressive Scalping', 'examples.use_cases.use_case_2_scalping'),
        3: ('Use Case 3: Risk Management', 'examples.use_cases.use_case_3_risk_management')
    }
    
    if use_case_number not in use_cases:
        logger.error(f"Invalid use case number: {use_case_number}")
        logger.info(f"Valid options: 1-{len(use_cases)}")
        return 1
    
    name, module_path = use_cases[use_case_number]
    
    logger.info(f"Running {name}...")
    
    try:
        module = __import__(module_path, fromlist=['simulate'])
        
        # Find simulate function
        for attr_name in dir(module):
            if attr_name.startswith('simulate_'):
                simulate_func = getattr(module, attr_name)
                simulate_func()
                logger.info(f"\n✅ {name} completed successfully")
                return 0
        
        logger.error(f"No simulation function found")
        return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Test plugin system use cases',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run all use cases
    python scripts/test_all_use_cases.py
    
    # Run specific use case
    python scripts/test_all_use_cases.py --use-case 1
    
Use Cases:
    1 - Conservative Trading (multiple filters)
    2 - Aggressive Scalping (no filters)
    3 - Risk Management (custom plugins)
        """
    )
    
    parser.add_argument(
        '--use-case',
        type=int,
        choices=[1, 2, 3],
        help='Run specific use case (1-3)'
    )
    
    args = parser.parse_args()
    
    if args.use_case:
        exit_code = run_specific_use_case(args.use_case)
    else:
        exit_code = run_all_use_cases()
    
    sys.exit(exit_code)
