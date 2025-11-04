"""
Strategy Registry - Dynamic Strategy Management System

This module provides a registry pattern for managing trading strategies.
It allows:
- Decorator-based registration
- Dynamic strategy loading
- Factory pattern for bot creation
- Strategy discovery and listing

Author: xPOURY4
Date: October 23, 2025
Version: 1.0.0
"""

from typing import Dict, Type, List, Optional
from core.base_bot import BaseTradingBot, BaseConfig
import inspect


class StrategyRegistry:
    """
    Registry pattern for managing trading strategies.
    
    This class allows strategies to be registered dynamically and created
    through a factory method. Makes it easy to:
    - Switch between strategies
    - List available strategies
    - Create bots without importing specific classes
    
    Usage:
        # Register a strategy
        @StrategyRegistry.register("my_strategy")
        class MyStrategy(BaseTradingBot):
            pass
        
        # Create bot instance
        bot = StrategyRegistry.create_bot("my_strategy", config)
        
        # List all strategies
        strategies = StrategyRegistry.list_strategies()
    """
    
    # Class-level storage for registered strategies
    _strategies: Dict[str, Type[BaseTradingBot]] = {}
    _metadata: Dict[str, Dict] = {}  # Store strategy metadata
    
    @classmethod
    def register(cls, name: str, description: str = "", author: str = "", 
                 version: str = "1.0.0", tags: List[str] = None):
        """
        Decorator to register a trading strategy.
        
        Args:
            name: Unique name for the strategy
            description: Brief description of the strategy
            author: Strategy author
            version: Strategy version
            tags: List of tags for categorization
        
        Returns:
            Decorator function
        
        Example:
            @StrategyRegistry.register(
                "supertrend",
                description="ML-optimized SuperTrend strategy",
                author="xPOURY4",
                tags=["ml", "trend-following"]
            )
            class SuperTrendBot(BaseTradingBot):
                pass
        """
        def decorator(strategy_class: Type[BaseTradingBot]):
            # Validate that class inherits from BaseTradingBot
            if not issubclass(strategy_class, BaseTradingBot):
                raise TypeError(
                    f"{strategy_class.__name__} must inherit from BaseTradingBot"
                )
            
            # Check for duplicate names
            if name in cls._strategies:
                raise ValueError(
                    f"Strategy '{name}' is already registered by "
                    f"{cls._strategies[name].__name__}"
                )
            
            # Register strategy
            cls._strategies[name] = strategy_class
            
            # Store metadata
            cls._metadata[name] = {
                'name': name,
                'class': strategy_class.__name__,
                'description': description or strategy_class.__doc__ or "No description",
                'author': author,
                'version': version,
                'tags': tags or [],
                'module': strategy_class.__module__,
            }
            
            # Add registry info to class
            strategy_class._registry_name = name
            strategy_class._registry_metadata = cls._metadata[name]
            
            print(f" Registered strategy: '{name}' ({strategy_class.__name__})")
            
            return strategy_class
        
        return decorator
    
    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        Unregister a strategy.
        
        Args:
            name: Name of strategy to unregister
        
        Returns:
            True if unregistered successfully
        """
        if name in cls._strategies:
            del cls._strategies[name]
            if name in cls._metadata:
                del cls._metadata[name]
            print(f"🔌 Unregistered strategy: '{name}'")
            return True
        return False
    
    @classmethod
    def get_strategy(cls, name: str) -> Type[BaseTradingBot]:
        """
        Get strategy class by name.
        
        Args:
            name: Strategy name
        
        Returns:
            Strategy class
        
        Raises:
            ValueError: If strategy not found
        """
        if name not in cls._strategies:
            available = ', '.join(cls.list_strategies())
            raise ValueError(
                f"Strategy '{name}' not found. "
                f"Available strategies: {available}"
            )
        
        return cls._strategies[name]
    
    @classmethod
    def create_bot(cls, strategy_name: str, config: BaseConfig, 
                   **kwargs) -> BaseTradingBot:
        """
        Factory method to create bot instance.
        
        Args:
            strategy_name: Name of registered strategy
            config: Configuration object
            **kwargs: Additional arguments to pass to bot constructor
        
        Returns:
            Bot instance
        
        Example:
            config = SuperTrendConfig(symbol="EURUSD", risk_percent=1.0)
            bot = StrategyRegistry.create_bot("supertrend", config)
            bot.connect(login, password, server)
            bot.run_cycle()
        """
        strategy_class = cls.get_strategy(strategy_name)
        
        # Create instance
        bot = strategy_class(config, **kwargs)
        
        return bot
    
    @classmethod
    def list_strategies(cls) -> List[str]:
        """
        List all registered strategy names.
        
        Returns:
            List of strategy names
        """
        return list(cls._strategies.keys())
    
    @classmethod
    def get_metadata(cls, name: str) -> Dict:
        """
        Get metadata for a strategy.
        
        Args:
            name: Strategy name
        
        Returns:
            Metadata dictionary
        """
        if name not in cls._metadata:
            raise ValueError(f"Strategy '{name}' not found")
        
        return cls._metadata[name].copy()
    
    @classmethod
    def list_all_metadata(cls) -> List[Dict]:
        """
        List metadata for all registered strategies.
        
        Returns:
            List of metadata dictionaries
        """
        return [meta.copy() for meta in cls._metadata.values()]
    
    @classmethod
    def find_strategies(cls, tag: str = None, author: str = None) -> List[str]:
        """
        Find strategies by tag or author.
        
        Args:
            tag: Tag to filter by
            author: Author to filter by
        
        Returns:
            List of matching strategy names
        
        Example:
            # Find all ML strategies
            ml_strategies = StrategyRegistry.find_strategies(tag="ml")
            
            # Find strategies by author
            my_strategies = StrategyRegistry.find_strategies(author="xPOURY4")
        """
        results = []
        
        for name, meta in cls._metadata.items():
            match = True
            
            if tag and tag not in meta['tags']:
                match = False
            
            if author and meta['author'] != author:
                match = False
            
            if match:
                results.append(name)
        
        return results
    
    @classmethod
    def print_strategies(cls):
        """
        Print all registered strategies in a nice format.
        
        Useful for debugging and discovering available strategies.
        """
        if not cls._strategies:
            print("No strategies registered.")
            return
        
        print("\n" + "="*70)
        print(f"{'REGISTERED STRATEGIES':^70}")
        print("="*70)
        
        for name, meta in sorted(cls._metadata.items()):
            print(f"\n {name}")
            print(f"   Class: {meta['class']}")
            print(f"   Description: {meta['description'][:60]}...")
            if meta['author']:
                print(f"   Author: {meta['author']}")
            print(f"   Version: {meta['version']}")
            if meta['tags']:
                print(f"   Tags: {', '.join(meta['tags'])}")
        
        print("\n" + "="*70)
        print(f"Total: {len(cls._strategies)} strategies")
        print("="*70 + "\n")
    
    @classmethod
    def validate_strategies(cls) -> Dict[str, List[str]]:
        """
        Validate all registered strategies.
        
        Checks that each strategy properly implements required methods.
        
        Returns:
            Dictionary with validation results:
            {
                'valid': ['strategy1', 'strategy2'],
                'invalid': [
                    ('strategy3', 'Missing generate_signal method'),
                    ('strategy4', 'Missing calculate_indicators method')
                ]
            }
        """
        valid = []
        invalid = []
        
        required_methods = ['generate_signal', 'calculate_indicators']
        
        for name, strategy_class in cls._strategies.items():
            issues = []
            
            # Check for required methods
            for method_name in required_methods:
                if not hasattr(strategy_class, method_name):
                    issues.append(f"Missing {method_name} method")
                else:
                    method = getattr(strategy_class, method_name)
                    # Check if it's abstract (not implemented)
                    if hasattr(method, '__isabstractmethod__'):
                        issues.append(f"{method_name} is not implemented")
            
            if issues:
                invalid.append((name, ', '.join(issues)))
            else:
                valid.append(name)
        
        return {'valid': valid, 'invalid': invalid}
    
    @classmethod
    def clear_registry(cls):
        """
        Clear all registered strategies.
        
        Useful for testing or resetting the registry.
        """
        cls._strategies.clear()
        cls._metadata.clear()
        print("🗑️  Registry cleared")
    
    @classmethod
    def export_registry(cls) -> Dict:
        """
        Export registry metadata to dictionary.
        
        Useful for saving registry state or API endpoints.
        
        Returns:
            Dictionary with all strategies and metadata
        """
        return {
            'strategies': list(cls._strategies.keys()),
            'metadata': cls.list_all_metadata(),
            'count': len(cls._strategies)
        }


# Convenience function for quick bot creation
def create_bot(strategy: str, config: BaseConfig, **kwargs) -> BaseTradingBot:
    """
    Convenience function to create a bot.
    
    Args:
        strategy: Strategy name
        config: Configuration object
        **kwargs: Additional arguments
    
    Returns:
        Bot instance
    
    Example:
        from core.strategy_registry import create_bot
        
        config = ICTConfig(symbol="XAUUSD")
        bot = create_bot("ict", config)
        bot.connect(login, password, server)
        bot.run_cycle()
    """
    return StrategyRegistry.create_bot(strategy, config, **kwargs)


def list_strategies() -> List[str]:
    """
    Convenience function to list strategies.
    
    Returns:
        List of strategy names
    """
    return StrategyRegistry.list_strategies()


def get_strategy_info(name: str) -> Dict:
    """
    Convenience function to get strategy metadata.
    
    Args:
        name: Strategy name
    
    Returns:
        Metadata dictionary
    """
    return StrategyRegistry.get_metadata(name)


# Auto-discovery function
def discover_strategies(module_names: List[str] = None):
    """
    Auto-discover and register strategies from modules.
    
    This function imports modules and automatically registers any
    BaseTradingBot subclasses that have the @StrategyRegistry.register
    decorator.
    
    Args:
        module_names: List of module names to import
                     If None, uses default list
    
    Example:
        from core.strategy_registry import discover_strategies
        
        # Discover strategies in core module
        discover_strategies(['core.ict_bot', 'core.supertrend_bot'])
        
        # List discovered strategies
        print(list_strategies())
    """
    if module_names is None:
        # Default modules to scan
        module_names = [
            'core.ict_bot',
            'core.supertrend_bot',
        ]
    
    import importlib
    
    for module_name in module_names:
        try:
            importlib.import_module(module_name)
            print(f" Loaded module: {module_name}")
        except Exception as e:
            print(f" Error loading module {module_name}: {e}")


if __name__ == "__main__":
    # Demo/test code
    print("Strategy Registry Demo")
    print("=" * 50)
    
    # Example registration (for testing)
    @StrategyRegistry.register(
        "demo_strategy",
        description="Demo strategy for testing",
        author="Test Author",
        tags=["demo", "test"]
    )
    class DemoStrategy(BaseTradingBot):
        def generate_signal(self, df):
            return None
        
        def calculate_indicators(self, df):
            return df
    
    # List strategies
    print("\nListing strategies:")
    StrategyRegistry.print_strategies()
    
    # Find strategies
    print("\nFinding strategies with 'demo' tag:")
    demo_strategies = StrategyRegistry.find_strategies(tag="demo")
    print(demo_strategies)
    
    # Validate strategies
    print("\nValidating strategies:")
    validation = StrategyRegistry.validate_strategies()
    print(f"Valid: {validation['valid']}")
    print(f"Invalid: {validation['invalid']}")
    
    # Export registry
    print("\nExporting registry:")
    export = StrategyRegistry.export_registry()
    print(f"Total strategies: {export['count']}")
