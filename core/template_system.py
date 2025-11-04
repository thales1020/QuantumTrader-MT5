"""
Strategy Template System - Core Implementation

Provides template management, rendering, validation, and strategy generation.

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
Phase: 3 - Strategy Templates
Version: 1.0.0
"""

import re
import ast
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class TemplateError(Exception):
    """Base exception for template system errors"""
    pass


class TemplateNotFoundError(TemplateError):
    """Raised when template is not found"""
    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"Template not found: {template_name}")


class InvalidVariableError(TemplateError):
    """Raised when required variables are missing or invalid"""
    pass


# ============================================================================
# TEMPLATE CLASS
# ============================================================================

@dataclass
class Template:
    """Represents a strategy template"""
    name: str
    path: Path
    content: str
    category: str
    difficulty: str
    description: str
    tags: List[str]
    required_variables: List[str]
    optional_variables: Dict[str, Any]
    
    _variable_pattern: re.Pattern = field(
        default_factory=lambda: re.compile(r'\{\{(\w+)\}\}'),
        init=False,
        repr=False
    )
    
    def extract_variables(self) -> List[str]:
        """
        Extract all variable placeholders from template content
        
        Returns:
            List of variable names found in template
        """
        matches = self._variable_pattern.findall(self.content)
        return list(set(matches))  # Remove duplicates
    
    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render template with provided variables
        
        Args:
            variables: Dictionary of variable name -> value
            
        Returns:
            Rendered template string
            
        Raises:
            InvalidVariableError: If required variables are missing
        """
        # Check for missing required variables
        missing = set(self.required_variables) - set(variables.keys())
        if missing:
            raise InvalidVariableError(
                f"Missing required variables: {', '.join(sorted(missing))}"
            )
        
        # Merge with optional defaults
        all_variables = self.optional_variables.copy()
        all_variables.update(variables)
        
        # Render template
        rendered = self.content
        for var_name, var_value in all_variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            rendered = rendered.replace(placeholder, str(var_value))
        
        return rendered
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            'name': self.name,
            'category': self.category,
            'difficulty': self.difficulty,
            'description': self.description,
            'tags': self.tags,
            'required_variables': self.required_variables,
            'optional_variables': self.optional_variables
        }


# ============================================================================
# TEMPLATE VALIDATOR
# ============================================================================

class TemplateValidator:
    """Validates templates and generated code"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_python_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate Python code syntax
        
        Args:
            code: Python code string
            
        Returns:
            Tuple of (is_valid, error_list)
        """
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            error_msg = f"Syntax error at line {e.lineno}: {e.msg}"
            return False, [error_msg]
        except Exception as e:
            return False, [str(e)]
    
    def validate_class_name(self, class_name: str) -> bool:
        """
        Validate Python class name format
        
        Args:
            class_name: Class name to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Must start with uppercase, only alphanumeric and underscores
        pattern = r'^[A-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, class_name))
    
    def validate_strategy_id(self, strategy_id: str) -> bool:
        """
        Validate strategy ID format
        
        Args:
            strategy_id: Strategy ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Must be lowercase, only alphanumeric and underscores
        pattern = r'^[a-z][a-z0-9_]*$'
        return bool(re.match(pattern, strategy_id))
    
    def validate_template_structure(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate template structure and required elements
        
        Args:
            content: Template content string
            
        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []
        
        # Check for common required elements
        required_patterns = {
            'class definition': r'class\s+\{\{STRATEGY_CLASS_NAME\}\}',
            'imports': r'from core\.base_bot import BaseTradingBot',
            'calculate_indicators method': r'def calculate_indicators\(',
            'generate_signal method': r'def generate_signal\('
        }
        
        for element, pattern in required_patterns.items():
            if not re.search(pattern, content):
                errors.append(f"Missing {element}")
        
        return len(errors) == 0, errors
    
    def find_unreplaced_variables(self, code: str) -> List[str]:
        """
        Find unreplaced variable placeholders in code
        
        Args:
            code: Generated code string
            
        Returns:
            List of unreplaced variable names
        """
        pattern = re.compile(r'\{\{(\w+)\}\}')
        matches = pattern.findall(code)
        return list(set(matches))


# ============================================================================
# TEMPLATE MANAGER
# ============================================================================

class TemplateManager:
    """Manages template loading and rendering"""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize template manager
        
        Args:
            template_dir: Root directory for templates
        """
        self.template_dir = Path(template_dir)
        self.templates: Dict[str, Template] = {}
        self.metadata: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)
    
    def load_templates(self) -> None:
        """Load all templates from template directory"""
        strategies_dir = self.template_dir / 'strategies'
        metadata_file = self.template_dir / 'metadata' / 'templates.yaml'
        
        # Load metadata first
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self.metadata = data.get('templates', {})
            except Exception as e:
                self.logger.error(f"Error loading metadata: {e}")
                self.metadata = {}
        
        # Load template files
        if not strategies_dir.exists():
            self.logger.warning(f"Template directory not found: {strategies_dir}")
            return
        
        for template_file in strategies_dir.glob('*.template'):
            try:
                template_name = template_file.stem.replace('.py', '')
                
                # Read template content
                content = template_file.read_text(encoding='utf-8')
                
                # Get metadata for this template
                meta = self.metadata.get(template_name, {})
                
                # Create Template object
                template = Template(
                    name=template_name,
                    path=template_file,
                    content=content,
                    category=meta.get('category', 'Unknown'),
                    difficulty=meta.get('difficulty', 'beginner'),
                    description=meta.get('description', ''),
                    tags=meta.get('tags', []),
                    required_variables=meta.get('required_variables', []),
                    optional_variables=meta.get('optional_variables', {})
                )
                
                self.templates[template_name] = template
                self.logger.info(f"Loaded template: {template_name}")
                
            except Exception as e:
                self.logger.error(f"Error loading template {template_file}: {e}")
    
    def get_template(self, name: str) -> Template:
        """
        Get template by name
        
        Args:
            name: Template name
            
        Returns:
            Template object
            
        Raises:
            TemplateNotFoundError: If template not found
        """
        if name not in self.templates:
            raise TemplateNotFoundError(name)
        
        return self.templates[name]
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available templates
        
        Returns:
            List of template dictionaries with metadata
        """
        return [template.to_dict() for template in self.templates.values()]
    
    def validate_variables(self, template_name: str, variables: Dict[str, Any]) -> List[str]:
        """
        Validate variables for a template
        
        Args:
            template_name: Name of template
            variables: Variables to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        template = self.get_template(template_name)
        
        errors = []
        missing = set(template.required_variables) - set(variables.keys())
        
        for var in sorted(missing):
            errors.append(f"Missing required variable: {var}")
        
        return errors
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render template with variables
        
        Args:
            template_name: Name of template
            variables: Variables for rendering
            
        Returns:
            Rendered template string
        """
        template = self.get_template(template_name)
        return template.render(variables)


# ============================================================================
# STRATEGY GENERATOR
# ============================================================================

class StrategyGenerator:
    """Generates strategies from templates"""
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize strategy generator
        
        Args:
            template_manager: TemplateManager instance
        """
        self.template_manager = template_manager
        self.validator = TemplateValidator()
        self.logger = logging.getLogger(__name__)
    
    def generate_strategy(
        self,
        template_name: str,
        output_path: Path,
        variables: Dict[str, Any],
        overwrite: bool = False
    ) -> Path:
        """
        Generate strategy file from template
        
        Args:
            template_name: Name of template to use
            output_path: Path for output file
            variables: Variables for rendering
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to generated file
            
        Raises:
            InvalidVariableError: If variables are invalid
            FileExistsError: If file exists and overwrite=False
        """
        # Convert to Path if string
        output_path = Path(output_path)
        
        # Check if file exists
        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Output file already exists: {output_path}")
        
        # Validate variables
        errors = self.template_manager.validate_variables(template_name, variables)
        if errors:
            raise InvalidVariableError('\n'.join(errors))
        
        # Add auto-generated variables if not provided
        if 'GENERATED_DATE' not in variables:
            variables['GENERATED_DATE'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if 'TEMPLATE_NAME' not in variables:
            variables['TEMPLATE_NAME'] = template_name
        
        # Render template
        rendered = self.template_manager.render_template(template_name, variables)
        
        # Validate generated code
        if not self.validate_generated_code(rendered):
            raise TemplateError("Generated code has syntax errors")
        
        # Check for unreplaced variables
        unreplaced = self.validator.find_unreplaced_variables(rendered)
        if unreplaced:
            self.logger.warning(f"Unreplaced variables found: {unreplaced}")
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        output_path.write_text(rendered, encoding='utf-8')
        self.logger.info(f"Generated strategy: {output_path}")
        
        return output_path
    
    def generate_config(
        self,
        strategy_name: str,
        output_path: Path,
        template_name: Optional[str] = None,
        **kwargs
    ) -> Path:
        """
        Generate config file for strategy
        
        Args:
            strategy_name: Strategy ID/name
            output_path: Path for config file
            template_name: Template name (for template-specific defaults)
            **kwargs: Additional config parameters
            
        Returns:
            Path to generated config file
        """
        # Convert to Path if string
        output_path = Path(output_path)
        
        # Base config structure
        config = {
            'strategy_id': strategy_name,
            'enabled': True,
            'symbol': kwargs.get('symbol', 'EURUSD'),
            'timeframe': kwargs.get('timeframe', 'M15'),
            'risk_percent': kwargs.get('risk_percent', 1.0),
            'magic_number': kwargs.get('magic_number', 123456)
        }
        
        # Add template-specific defaults
        if template_name:
            try:
                template = self.template_manager.get_template(template_name)
                # Add optional variables as config parameters
                for key, value in template.optional_variables.items():
                    # Convert template variable names to config keys
                    config_key = key.lower()
                    if config_key not in config:
                        config[config_key] = value
            except TemplateNotFoundError:
                pass
        
        # Add any additional kwargs
        config.update(kwargs)
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"Generated config: {output_path}")
        
        return output_path
    
    def validate_generated_code(self, code: str) -> bool:
        """
        Validate generated Python code
        
        Args:
            code: Python code string
            
        Returns:
            True if valid, False otherwise
        """
        is_valid, errors = self.validator.validate_python_syntax(code)
        
        if not is_valid:
            for error in errors:
                self.logger.error(f"Validation error: {error}")
        
        return is_valid


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging(level: int = logging.INFO) -> None:
    """
    Setup logging for template system
    
    Args:
        level: Logging level
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    setup_logging(logging.DEBUG)
    
    # Example usage
    manager = TemplateManager('templates')
    manager.load_templates()
    
    print(f"\nLoaded {len(manager.templates)} templates:")
    for template in manager.list_templates():
        print(f"  - {template['name']}: {template['description']}")
