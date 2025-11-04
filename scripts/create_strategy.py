#!/usr/bin/env python
"""
Strategy Generator CLI Tool

Interactive command-line tool to generate trading strategies from templates.

Usage:
    python scripts/create_strategy.py                    # Interactive mode
    python scripts/create_strategy.py --list             # List templates
    python scripts/create_strategy.py --info TEMPLATE    # Template info
    python scripts/create_strategy.py --template TEMPLATE --name NAME ...  # Direct mode

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
Phase: 3 - Strategy Templates
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.template_system import TemplateManager, StrategyGenerator, TemplateValidator


def print_banner():
    """Print CLI banner"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "QuantumTrader-MT5 Strategy Generator v1.0.0" + " " * 5 + "║")
    print("╚" + "═" * 58 + "╝")
    print()


def list_templates(template_mgr: TemplateManager):
    """List all available templates"""
    templates = template_mgr.list_templates()
    
    print("\n📋 Available Templates:\n")
    
    for idx, template in enumerate(templates, 1):
        difficulty_emoji = {
            'beginner': '⭐',
            'intermediate': '⭐⭐',
            'advanced': '⭐⭐⭐'
        }.get(template['difficulty'], '⭐')
        
        print(f"  {idx}. {template['name']} ({difficulty_emoji} {template['difficulty'].title()})")
        print(f"     {template['description']}")
        print(f"     Category: {template['category']}")
        print(f"     Tags: {', '.join(template['tags'])}")
        print()


def show_template_info(template_mgr: TemplateManager, template_name: str):
    """Show detailed information about a template"""
    try:
        template = template_mgr.get_template(template_name)
        metadata = template.to_dict()
        
        print(f"\n📄 Template: {metadata['name']}\n")
        print(f"Description: {metadata['description']}")
        print(f"Category: {metadata['category']}")
        print(f"Difficulty: {metadata['difficulty']}")
        print(f"Tags: {', '.join(metadata['tags'])}")
        
        print(f"\n✅ Required Variables:")
        for var in metadata['required_variables']:
            print(f"  - {var}")
        
        print(f"\n⚙️  Optional Variables (with defaults):")
        for var, default in metadata['optional_variables'].items():
            print(f"  - {var}: {default}")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("  ⚠️  This field is required")


def interactive_mode(template_mgr: TemplateManager, generator: StrategyGenerator):
    """Interactive strategy generation"""
    print_banner()
    
    # List templates
    templates = template_mgr.list_templates()
    list_templates(template_mgr)
    
    # Select template
    while True:
        try:
            choice = input(f"Select template (1-{len(templates)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                selected_template = templates[idx]
                break
            print(f"  ⚠️  Please enter a number between 1 and {len(templates)}")
        except ValueError:
            print("  ⚠️  Please enter a valid number")
    
    template_name = list(template_mgr.templates.keys())[idx]
    template = template_mgr.get_template(template_name)
    
    print(f"\n── {selected_template['name']} Template ──\n")
    
    # Collect required variables
    variables = {}
    
    # Strategy name
    variables['STRATEGY_NAME'] = get_user_input("Strategy Name")
    
    # Generate default ID from name
    default_id = variables['STRATEGY_NAME'].lower().replace(' ', '_').replace('-', '_')
    variables['STRATEGY_ID'] = get_user_input("Strategy ID (lowercase, underscores)", default_id)
    
    # Validate ID format
    validator = TemplateValidator()
    if not validator.validate_strategy_id(variables['STRATEGY_ID']):
        print("  ⚠️  Invalid strategy ID format. Using default.")
        variables['STRATEGY_ID'] = default_id
    
    # Generate default class name from ID
    default_class = ''.join(word.capitalize() for word in variables['STRATEGY_ID'].split('_'))
    variables['STRATEGY_CLASS_NAME'] = get_user_input("Strategy Class Name", default_class)
    
    # Validate class name format
    if not validator.validate_class_name(variables['STRATEGY_CLASS_NAME']):
        print("  ⚠️  Invalid class name format. Using default.")
        variables['STRATEGY_CLASS_NAME'] = default_class
    
    # Description
    variables['STRATEGY_DESCRIPTION'] = get_user_input("Description", f"{variables['STRATEGY_NAME']} trading strategy")
    
    # Template-specific parameters
    if template.optional_variables:
        print(f"\n── {selected_template['name']} Parameters ──\n")
        
        for param, default_value in template.optional_variables.items():
            # Skip auto-generated fields
            if param in ['AUTHOR', 'VERSION', 'GENERATED_DATE', 'TEMPLATE_NAME']:
                continue
            
            # Format parameter name for display
            param_display = param.replace('_', ' ').title()
            value = get_user_input(f"{param_display}", str(default_value))
            
            # Try to convert to appropriate type
            if isinstance(default_value, int):
                try:
                    variables[param] = int(value)
                except ValueError:
                    variables[param] = default_value
            elif isinstance(default_value, float):
                try:
                    variables[param] = float(value)
                except ValueError:
                    variables[param] = default_value
            else:
                variables[param] = value
    
    # Output options
    print("\n── Output Options ──\n")
    
    output_dir = get_user_input("Output directory", "./strategies")
    output_path = Path(output_dir) / f"{variables['STRATEGY_ID']}.py"
    
    generate_config = get_user_input("Generate config file? (Y/n)", "Y").upper() == 'Y'
    
    # Summary
    print("\n── Summary ──\n")
    print(f"Template: {selected_template['name']}")
    print(f"Strategy: {variables['STRATEGY_NAME']} ({variables['STRATEGY_ID']})")
    print(f"Output: {output_path}")
    if generate_config:
        print(f"Config: ./config/{variables['STRATEGY_ID']}.json")
    
    # Confirm
    confirm = get_user_input("\nGenerate strategy? (Y/n)", "Y").upper()
    if confirm != 'Y':
        print("\n❌ Cancelled\n")
        return
    
    # Generate
    try:
        result_path = generator.generate_strategy(
            template_name=template_name,
            output_path=output_path,
            variables=variables,
            overwrite=True
        )
        
        print(f"\n✅ Strategy created: {result_path}")
        
        if generate_config:
            config_path = Path("config") / f"{variables['STRATEGY_ID']}.json"
            generator.generate_config(
                strategy_name=variables['STRATEGY_ID'],
                output_path=config_path,
                template_name=template_name
            )
            print(f"✅ Config created: {config_path}")
        
        print("\nNext steps:")
        print(f"  1. Review generated files")
        print(f"  2. Customize if needed")
        print(f"  3. Add to config.json")
        print(f"  4. Run backtest: python -m engines.backtest_engine {variables['STRATEGY_ID']}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error generating strategy: {e}\n")


def command_line_mode(args, template_mgr: TemplateManager, generator: StrategyGenerator):
    """Non-interactive command-line mode"""
    variables = {
        'STRATEGY_NAME': args.name,
        'STRATEGY_CLASS_NAME': args.class_name or ''.join(word.capitalize() 
                                for word in args.name.replace(' ', '_').split('_')),
        'STRATEGY_ID': args.id or args.name.lower().replace(' ', '_'),
        'STRATEGY_DESCRIPTION': args.description or f"{args.name} trading strategy"
    }
    
    # Add any additional parameters from --param flags
    if args.params:
        for param in args.params:
            if '=' in param:
                key, value = param.split('=', 1)
                # Try to convert to number if possible
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                variables[key.upper()] = value
    
    output_path = Path(args.output) / f"{variables['STRATEGY_ID']}.py"
    
    try:
        result_path = generator.generate_strategy(
            template_name=args.template,
            output_path=output_path,
            variables=variables,
            overwrite=args.force
        )
        
        print(f"✅ Strategy created: {result_path}")
        
        if args.generate_config:
            config_path = Path("config") / f"{variables['STRATEGY_ID']}.json"
            generator.generate_config(
                strategy_name=variables['STRATEGY_ID'],
                output_path=config_path,
                template_name=args.template
            )
            print(f"✅ Config created: {config_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate trading strategies from templates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Modes
    parser.add_argument('--list', action='store_true', help='List all templates')
    parser.add_argument('--info', metavar='TEMPLATE', help='Show template information')
    
    # Strategy generation (command-line mode)
    parser.add_argument('--template', '-t', help='Template name')
    parser.add_argument('--name', '-n', help='Strategy name')
    parser.add_argument('--id', '-i', help='Strategy ID (default: generated from name)')
    parser.add_argument('--class-name', '-c', help='Strategy class name (default: generated from name)')
    parser.add_argument('--description', '-d', help='Strategy description')
    parser.add_argument('--output', '-o', default='./strategies', help='Output directory (default: ./strategies)')
    parser.add_argument('--param', '-p', action='append', dest='params', 
                       help='Additional parameters (e.g., -p FAST_PERIOD=10)')
    parser.add_argument('--generate-config', action='store_true', help='Generate config file')
    parser.add_argument('--force', '-f', action='store_true', help='Overwrite existing files')
    
    args = parser.parse_args()
    
    # Initialize template system
    template_mgr = TemplateManager()
    template_mgr.load_templates()
    generator = StrategyGenerator(template_mgr)
    
    # Handle different modes
    if args.list:
        list_templates(template_mgr)
        
    elif args.info:
        show_template_info(template_mgr, args.info)
        
    elif args.template and args.name:
        command_line_mode(args, template_mgr, generator)
        
    else:
        # Default: Interactive mode
        interactive_mode(template_mgr, generator)


if __name__ == '__main__':
    main()
