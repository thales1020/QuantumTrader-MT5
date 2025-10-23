"""
Config Manager - Advanced Configuration Management System

This module provides enhanced configuration management with:
- Multiple formats (JSON, YAML, Python)
- Environment variable overrides
- Profile support (dev, prod, test)
- Hierarchical configuration
- Validation
- Type safety

Author: xPOURY4
Date: October 23, 2025
Version: 1.0.0
"""

from dataclasses import dataclass, field, fields
from typing import Dict, Any, Optional, Type, List
from pathlib import Path
import os
import yaml
import json
import logging


# Setup logger
logger = logging.getLogger('ConfigManager')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)


class ConfigManager:
    """
    Advanced configuration management system.
    
    Features:
    - Load from YAML, JSON, or Python dict
    - Profile-based configs (dev, prod, test)
    - Environment variable overrides
    - Hierarchical merging
    - Validation
    - Type conversion
    
    Priority Order (highest to lowest):
    1. Environment variables
    2. Profile-specific file (config.prod.yaml)
    3. Base file (config.yaml)
    4. Default values in dataclass
    
    Usage:
        # Create config manager
        config_manager = ConfigManager(config_dir="config")
        
        # Load config
        config = config_manager.load("supertrend", SuperTrendConfig)
        
        # Use config
        bot = SuperTrendBot(config)
        
        # Override with environment variable:
        # export SUPERTREND_RISK_PERCENT=2.0
        # export TRADING_PROFILE=production
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize ConfigManager.
        
        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir)
        self.profile = os.getenv("TRADING_PROFILE", "default")
        self._configs: Dict[str, Any] = {}
        
        logger.info(f"ConfigManager initialized")
        logger.info(f"  Config directory: {self.config_dir}")
        logger.info(f"  Active profile: {self.profile}")
        
        # Create config directory if doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self, name: str, config_class: Type, 
             profile: Optional[str] = None) -> Any:
        """
        Load configuration with hierarchical override.
        
        Loading order:
        1. Base config file (config/{name}.yaml)
        2. Profile config file (config/{name}.{profile}.yaml)
        3. Environment variables ({NAME}_{KEY})
        
        Args:
            name: Config name (e.g., "supertrend", "ict")
            config_class: Dataclass type to instantiate
            profile: Profile name (overrides TRADING_PROFILE env var)
        
        Returns:
            Config instance
        
        Example:
            config = config_manager.load("supertrend", SuperTrendConfig)
            config = config_manager.load("ict", ICTConfig, profile="production")
        """
        # Use provided profile or default
        profile = profile or self.profile
        
        logger.info(f"Loading config '{name}' with profile '{profile}'")
        
        # Start with empty config
        config_data = {}
        
        # 1. Load base config
        base_files = [
            self.config_dir / f"{name}.yaml",
            self.config_dir / f"{name}.yml",
            self.config_dir / f"{name}.json",
        ]
        
        base_loaded = False
        for base_file in base_files:
            if base_file.exists():
                logger.info(f"  Loading base: {base_file.name}")
                config_data = self._load_file(base_file)
                base_loaded = True
                break
        
        if not base_loaded:
            logger.warning(f"  No base config found for '{name}', using defaults")
        
        # 2. Load profile-specific overrides
        if profile and profile != "default":
            profile_files = [
                self.config_dir / f"{name}.{profile}.yaml",
                self.config_dir / f"{name}.{profile}.yml",
                self.config_dir / f"{name}.{profile}.json",
            ]
            
            for profile_file in profile_files:
                if profile_file.exists():
                    logger.info(f"  Loading profile: {profile_file.name}")
                    profile_data = self._load_file(profile_file)
                    config_data = self._merge_configs(config_data, profile_data)
                    break
        
        # 3. Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data, name)
        
        # 4. Create config instance
        try:
            config = config_class.from_dict(config_data) if hasattr(config_class, 'from_dict') else config_class(**config_data)
        except Exception as e:
            logger.error(f"Failed to create config instance: {e}")
            logger.info("Creating with default values")
            config = config_class()
        
        # 5. Validate config
        validation_errors = self._validate_config(config)
        if validation_errors:
            logger.warning(f"Config validation issues:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
        
        # 6. Cache config
        self._configs[name] = config
        
        logger.info(f"✅ Config '{name}' loaded successfully")
        return config
    
    def save(self, name: str, config: Any, format: str = "yaml", 
             profile: Optional[str] = None):
        """
        Save configuration to file.
        
        Args:
            name: Config name
            config: Config object to save
            format: File format ('yaml' or 'json')
            profile: Profile name (if None, saves to base file)
        
        Example:
            config_manager.save("supertrend", config, format="yaml")
            config_manager.save("ict", config, format="yaml", profile="prod")
        """
        # Convert config to dict
        if hasattr(config, 'to_dict'):
            data = config.to_dict()
        elif hasattr(config, '__dict__'):
            data = {k: v for k, v in config.__dict__.items() 
                   if not k.startswith('_')}
        else:
            raise ValueError("Config must have to_dict() or __dict__")
        
        # Determine filename
        if profile and profile != "default":
            filename = f"{name}.{profile}.{format}"
        else:
            filename = f"{name}.{format}"
        
        filepath = self.config_dir / filename
        
        # Save based on format
        if format == "yaml" or format == "yml":
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        elif format == "json":
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"✅ Saved config to {filepath}")
    
    def _load_file(self, filepath: Path) -> Dict:
        """
        Load config from file.
        
        Args:
            filepath: Path to config file
        
        Returns:
            Config dictionary
        """
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            if filepath.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif filepath.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        return data if data else {}
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two config dictionaries.
        
        Args:
            base: Base configuration
            override: Override configuration
        
        Returns:
            Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dicts
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override value
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict, prefix: str) -> Dict:
        """
        Apply environment variable overrides.
        
        Environment variables should be named:
        {PREFIX}_{KEY}
        
        Example:
            SUPERTREND_RISK_PERCENT=2.0
            ICT_SYMBOL=XAUUSD
        
        Args:
            config: Config dictionary
            prefix: Prefix for environment variables
        
        Returns:
            Config with environment overrides applied
        """
        prefix_upper = prefix.upper()
        overrides_applied = 0
        
        for key, value in config.items():
            env_key = f"{prefix_upper}_{key.upper()}"
            
            if env_key in os.environ:
                env_value = os.environ[env_key]
                
                # Convert to appropriate type
                try:
                    if isinstance(value, bool):
                        config[key] = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(value, int):
                        config[key] = int(env_value)
                    elif isinstance(value, float):
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value
                    
                    logger.info(f"  Override from env: {key} = {config[key]}")
                    overrides_applied += 1
                
                except ValueError as e:
                    logger.warning(f"  Failed to parse {env_key}: {e}")
        
        if overrides_applied > 0:
            logger.info(f"  Applied {overrides_applied} environment override(s)")
        
        return config
    
    def _validate_config(self, config: Any) -> List[str]:
        """
        Validate configuration values.
        
        Args:
            config: Config object to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Common validations
        if hasattr(config, 'risk_percent'):
            if config.risk_percent <= 0 or config.risk_percent > 100:
                errors.append(
                    f"risk_percent must be between 0 and 100, got {config.risk_percent}"
                )
        
        if hasattr(config, 'rr_ratio'):
            if config.rr_ratio <= 0:
                errors.append(
                    f"rr_ratio must be positive, got {config.rr_ratio}"
                )
        
        if hasattr(config, 'max_positions'):
            if config.max_positions < 1:
                errors.append(
                    f"max_positions must be at least 1, got {config.max_positions}"
                )
        
        if hasattr(config, 'symbol'):
            if not config.symbol:
                errors.append("symbol cannot be empty")
        
        # Add more validation rules as needed
        
        return errors
    
    def get_config(self, name: str) -> Optional[Any]:
        """
        Get cached config by name.
        
        Args:
            name: Config name
        
        Returns:
            Cached config or None
        """
        return self._configs.get(name)
    
    def reload(self, name: str) -> Any:
        """
        Reload configuration from files.
        
        Args:
            name: Config name
        
        Returns:
            Reloaded config
        """
        if name in self._configs:
            config_class = type(self._configs[name])
            return self.load(name, config_class)
        else:
            raise ValueError(f"Config '{name}' not found in cache")
    
    def list_configs(self) -> List[str]:
        """
        List all config files in config directory.
        
        Returns:
            List of config names
        """
        config_files = []
        
        for filepath in self.config_dir.glob("*"):
            if filepath.suffix in ['.yaml', '.yml', '.json']:
                # Extract base name (without profile and extension)
                name = filepath.stem
                if '.' in name:
                    # Has profile (e.g., supertrend.prod)
                    name = name.split('.')[0]
                
                if name not in config_files:
                    config_files.append(name)
        
        return sorted(config_files)
    
    def create_template(self, name: str, config_class: Type, format: str = "yaml"):
        """
        Create a config template file with default values.
        
        Args:
            name: Config name
            config_class: Config dataclass
            format: File format
        
        Example:
            config_manager.create_template("supertrend", SuperTrendConfig)
        """
        # Create instance with defaults
        config = config_class()
        
        # Save to file
        self.save(name, config, format=format)
        
        logger.info(f"✅ Created config template: {name}.{format}")


# Convenience function
def load_config(name: str, config_class: Type, config_dir: str = "config", 
                profile: Optional[str] = None) -> Any:
    """
    Convenience function to load config in one line.
    
    Args:
        name: Config name
        config_class: Config dataclass type
        config_dir: Config directory
        profile: Profile name
    
    Returns:
        Config instance
    
    Example:
        from core.config_manager import load_config
        from core.supertrend_bot import SuperTrendConfig
        
        config = load_config("supertrend", SuperTrendConfig)
        bot = SuperTrendBot(config)
    """
    manager = ConfigManager(config_dir)
    return manager.load(name, config_class, profile)


if __name__ == "__main__":
    # Demo/test code
    from core.base_bot import BaseConfig
    
    print("Config Manager Demo")
    print("=" * 50)
    
    # Create test config class
    @dataclass
    class TestConfig(BaseConfig):
        test_param: str = "default_value"
        test_number: int = 42
    
    # Create config manager
    manager = ConfigManager(config_dir="config")
    
    # Create template
    print("\nCreating config template...")
    manager.create_template("test", TestConfig)
    
    # Load config
    print("\nLoading config...")
    config = manager.load("test", TestConfig)
    
    print(f"\nLoaded config:")
    print(f"  symbol: {config.symbol}")
    print(f"  risk_percent: {config.risk_percent}")
    print(f"  test_param: {config.test_param}")
    
    # List configs
    print("\nAvailable configs:")
    for cfg in manager.list_configs():
        print(f"  - {cfg}")
    
    print("\n" + "=" * 50)
