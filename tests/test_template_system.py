"""
Test Suite for Strategy Template System

Tests for template loading, rendering, validation, and strategy generation.
Following TDD approach - write tests before implementation.

Author: QuantumTrader-MT5 Team
Date: November 4, 2025
Phase: 3 - Strategy Templates
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import tempfile
import shutil

# Import components to test (will implement these)
from core.template_system import (
    Template,
    TemplateManager,
    TemplateValidator,
    StrategyGenerator,
    TemplateError,
    TemplateNotFoundError,
    InvalidVariableError
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_template_content():
    """Sample template content with variables"""
    return '''"""
{{STRATEGY_NAME}} - {{STRATEGY_DESCRIPTION}}
Generated: {{GENERATED_DATE}}
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import talib


@StrategyRegistry.register("{{STRATEGY_ID}}")
class {{STRATEGY_CLASS_NAME}}(BaseTradingBot):
    """{{STRATEGY_DESCRIPTION}}"""
    
    def __init__(self, config):
        super().__init__(config)
        self.fast_period = {{FAST_PERIOD}}
        self.slow_period = {{SLOW_PERIOD}}
    
    def calculate_indicators(self, df):
        df['ma_fast'] = talib.{{MA_TYPE}}(df['close'], timeperiod=self.fast_period)
        df['ma_slow'] = talib.{{MA_TYPE}}(df['close'], timeperiod=self.slow_period)
        return df
    
    def generate_signal(self, df):
        # Entry logic here
        pass
'''


@pytest.fixture
def sample_metadata():
    """Sample template metadata"""
    return {
        'name': 'MA Crossover',
        'category': 'Trend Following',
        'difficulty': 'beginner',
        'description': 'Moving average crossover strategy',
        'tags': ['trend', 'crossover', 'beginner'],
        'required_variables': [
            'STRATEGY_NAME',
            'STRATEGY_CLASS_NAME',
            'STRATEGY_ID',
            'STRATEGY_DESCRIPTION'
        ],
        'optional_variables': {
            'FAST_PERIOD': 10,
            'SLOW_PERIOD': 30,
            'MA_TYPE': 'SMA',
            'GENERATED_DATE': '2025-11-04'
        }
    }


@pytest.fixture
def sample_variables():
    """Sample variables for rendering"""
    return {
        'STRATEGY_NAME': 'Test MA Strategy',
        'STRATEGY_CLASS_NAME': 'TestMAStrategy',
        'STRATEGY_ID': 'test_ma_strategy',
        'STRATEGY_DESCRIPTION': 'Test moving average strategy',
        'FAST_PERIOD': 10,
        'SLOW_PERIOD': 30,
        'MA_TYPE': 'SMA',
        'GENERATED_DATE': '2025-11-04 10:30:00'
    }


@pytest.fixture
def template_manager(temp_dir):
    """Create TemplateManager instance with temp directory"""
    manager = TemplateManager(template_dir=str(temp_dir))
    return manager


@pytest.fixture
def setup_template_files(temp_dir, sample_template_content, sample_metadata):
    """Setup template files in temp directory"""
    # Create directory structure
    strategies_dir = temp_dir / 'strategies'
    metadata_dir = temp_dir / 'metadata'
    strategies_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)
    
    # Create template file
    template_file = strategies_dir / 'ma_crossover.py.template'
    template_file.write_text(sample_template_content)
    
    # Create metadata file
    metadata_file = metadata_dir / 'templates.yaml'
    with open(metadata_file, 'w') as f:
        yaml.dump({'templates': {'ma_crossover': sample_metadata}}, f)
    
    return {
        'template_dir': temp_dir,
        'template_file': template_file,
        'metadata_file': metadata_file
    }


# ============================================================================
# TEMPLATE CLASS TESTS
# ============================================================================

class TestTemplate:
    """Test Template class"""
    
    def test_template_initialization(self, sample_template_content, sample_metadata):
        """Test Template object initialization"""
        # Remove 'name' from metadata since we pass it explicitly
        metadata = {k: v for k, v in sample_metadata.items() if k != 'name'}
        
        template = Template(
            name='ma_crossover',
            path=Path('templates/strategies/ma_crossover.py.template'),
            content=sample_template_content,
            **metadata
        )
        
        assert template.name == 'ma_crossover'
        assert template.category == 'Trend Following'
        assert template.difficulty == 'beginner'
        assert 'STRATEGY_NAME' in template.required_variables
        assert template.optional_variables['FAST_PERIOD'] == 10
    
    def test_extract_variables_from_content(self, sample_template_content):
        """Test extracting variable placeholders from template content"""
        template = Template(
            name='test',
            path=Path('test.template'),
            content=sample_template_content,
            category='test',
            difficulty='beginner',
            description='test',
            tags=[],
            required_variables=[],
            optional_variables={}
        )
        
        variables = template.extract_variables()
        
        assert 'STRATEGY_NAME' in variables
        assert 'STRATEGY_CLASS_NAME' in variables
        assert 'STRATEGY_ID' in variables
        assert 'FAST_PERIOD' in variables
        assert 'SLOW_PERIOD' in variables
        assert 'MA_TYPE' in variables
    
    def test_render_template_with_variables(self, sample_template_content, sample_variables):
        """Test rendering template with provided variables"""
        template = Template(
            name='test',
            path=Path('test.template'),
            content=sample_template_content,
            category='test',
            difficulty='beginner',
            description='test',
            tags=[],
            required_variables=list(sample_variables.keys()),
            optional_variables={}
        )
        
        rendered = template.render(sample_variables)
        
        assert 'Test MA Strategy' in rendered
        assert 'TestMAStrategy' in rendered
        assert 'test_ma_strategy' in rendered
        assert '{{STRATEGY_NAME}}' not in rendered  # No unreplaced variables
        assert 'self.fast_period = 10' in rendered
        assert 'talib.SMA' in rendered
    
    def test_render_fails_with_missing_required_variables(self, sample_template_content):
        """Test that rendering fails when required variables are missing"""
        template = Template(
            name='test',
            path=Path('test.template'),
            content=sample_template_content,
            category='test',
            difficulty='beginner',
            description='test',
            tags=[],
            required_variables=['STRATEGY_NAME', 'STRATEGY_CLASS_NAME'],
            optional_variables={}
        )
        
        incomplete_variables = {'STRATEGY_NAME': 'Test'}  # Missing STRATEGY_CLASS_NAME
        
        with pytest.raises(InvalidVariableError) as exc_info:
            template.render(incomplete_variables)
        
        assert 'STRATEGY_CLASS_NAME' in str(exc_info.value)
    
    def test_render_uses_optional_defaults(self, sample_template_content):
        """Test that rendering uses default values for optional variables"""
        template = Template(
            name='test',
            path=Path('test.template'),
            content=sample_template_content,
            category='test',
            difficulty='beginner',
            description='test',
            tags=[],
            required_variables=['STRATEGY_NAME', 'STRATEGY_CLASS_NAME', 'STRATEGY_ID', 'STRATEGY_DESCRIPTION'],
            optional_variables={
                'FAST_PERIOD': 20,
                'SLOW_PERIOD': 50,
                'MA_TYPE': 'EMA',
                'GENERATED_DATE': '2025-11-04'
            }
        )
        
        minimal_variables = {
            'STRATEGY_NAME': 'Test',
            'STRATEGY_CLASS_NAME': 'Test',
            'STRATEGY_ID': 'test',
            'STRATEGY_DESCRIPTION': 'Test'
        }
        
        rendered = template.render(minimal_variables)
        
        assert 'self.fast_period = 20' in rendered  # Used default
        assert 'self.slow_period = 50' in rendered  # Used default
        assert 'talib.EMA' in rendered  # Used default


# ============================================================================
# TEMPLATE MANAGER TESTS
# ============================================================================

class TestTemplateManager:
    """Test TemplateManager class"""
    
    def test_initialization(self, temp_dir):
        """Test TemplateManager initialization"""
        manager = TemplateManager(template_dir=str(temp_dir))
        
        assert manager.template_dir == temp_dir
        assert isinstance(manager.templates, dict)
        assert isinstance(manager.metadata, dict)
    
    def test_load_templates_from_directory(self, template_manager, setup_template_files):
        """Test loading templates from directory"""
        template_manager.load_templates()
        
        assert 'ma_crossover' in template_manager.templates
        assert 'ma_crossover' in template_manager.metadata
        
        template = template_manager.templates['ma_crossover']
        assert template.name == 'ma_crossover'
        assert template.category == 'Trend Following'
    
    def test_load_templates_creates_missing_directories(self, temp_dir):
        """Test that load_templates creates missing directories gracefully"""
        manager = TemplateManager(template_dir=str(temp_dir / 'nonexistent'))
        
        # Should not raise error
        manager.load_templates()
        
        assert len(manager.templates) == 0
    
    def test_get_template_by_name(self, template_manager, setup_template_files):
        """Test retrieving template by name"""
        template_manager.load_templates()
        
        template = template_manager.get_template('ma_crossover')
        
        assert template.name == 'ma_crossover'
        assert isinstance(template, Template)
    
    def test_get_template_raises_error_for_nonexistent(self, template_manager):
        """Test that getting nonexistent template raises error"""
        with pytest.raises(TemplateNotFoundError) as exc_info:
            template_manager.get_template('nonexistent_template')
        
        assert 'nonexistent_template' in str(exc_info.value)
    
    def test_list_templates(self, template_manager, setup_template_files):
        """Test listing all templates"""
        template_manager.load_templates()
        
        templates = template_manager.list_templates()
        
        assert len(templates) > 0
        assert any(t['name'] == 'ma_crossover' for t in templates)
        
        ma_template = next(t for t in templates if t['name'] == 'ma_crossover')
        assert 'category' in ma_template
        assert 'difficulty' in ma_template
        assert 'description' in ma_template
    
    def test_validate_variables_success(self, template_manager, setup_template_files, sample_variables):
        """Test validating complete set of variables"""
        template_manager.load_templates()
        
        errors = template_manager.validate_variables('ma_crossover', sample_variables)
        
        assert len(errors) == 0
    
    def test_validate_variables_detects_missing(self, template_manager, setup_template_files):
        """Test validation detects missing required variables"""
        template_manager.load_templates()
        
        incomplete_vars = {
            'STRATEGY_NAME': 'Test',
            'STRATEGY_ID': 'test'
            # Missing STRATEGY_CLASS_NAME and STRATEGY_DESCRIPTION
        }
        
        errors = template_manager.validate_variables('ma_crossover', incomplete_vars)
        
        assert len(errors) > 0
        assert any('STRATEGY_CLASS_NAME' in error for error in errors)
        assert any('STRATEGY_DESCRIPTION' in error for error in errors)
    
    def test_render_template(self, template_manager, setup_template_files, sample_variables):
        """Test rendering template through manager"""
        template_manager.load_templates()
        
        rendered = template_manager.render_template('ma_crossover', sample_variables)
        
        assert 'Test MA Strategy' in rendered
        assert 'TestMAStrategy' in rendered
        assert '{{' not in rendered  # No unreplaced variables


# ============================================================================
# TEMPLATE VALIDATOR TESTS
# ============================================================================

class TestTemplateValidator:
    """Test TemplateValidator class"""
    
    def test_validate_python_syntax_valid(self):
        """Test validation of valid Python code"""
        validator = TemplateValidator()
        
        valid_code = '''
def test_function():
    return True

class TestClass:
    pass
'''
        
        is_valid, errors = validator.validate_python_syntax(valid_code)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_python_syntax_invalid(self):
        """Test validation of invalid Python code"""
        validator = TemplateValidator()
        
        invalid_code = '''
def test_function(
    # Missing closing parenthesis
    return True
'''
        
        is_valid, errors = validator.validate_python_syntax(invalid_code)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_class_name_format(self):
        """Test validation of class name format"""
        validator = TemplateValidator()
        
        assert validator.validate_class_name('MyStrategy') is True
        assert validator.validate_class_name('MyStrategyV2') is True
        assert validator.validate_class_name('my_strategy') is False  # Lowercase
        assert validator.validate_class_name('123Strategy') is False  # Starts with number
        assert validator.validate_class_name('My-Strategy') is False  # Invalid char
    
    def test_validate_strategy_id_format(self):
        """Test validation of strategy ID format"""
        validator = TemplateValidator()
        
        assert validator.validate_strategy_id('my_strategy') is True
        assert validator.validate_strategy_id('my_strategy_v2') is True
        assert validator.validate_strategy_id('MyStrategy') is False  # Uppercase
        assert validator.validate_strategy_id('my-strategy') is False  # Hyphen
        assert validator.validate_strategy_id('my strategy') is False  # Space
    
    def test_validate_template_structure(self, sample_template_content):
        """Test validation of template structure"""
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template_structure(sample_template_content)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_detect_unreplaced_variables(self):
        """Test detection of unreplaced variable placeholders"""
        validator = TemplateValidator()
        
        code_with_unreplaced = '''
class MyStrategy:
    def __init__(self):
        self.name = "{{STRATEGY_NAME}}"  # Unreplaced!
'''
        
        unreplaced = validator.find_unreplaced_variables(code_with_unreplaced)
        
        assert len(unreplaced) > 0
        assert 'STRATEGY_NAME' in unreplaced


# ============================================================================
# STRATEGY GENERATOR TESTS
# ============================================================================

class TestStrategyGenerator:
    """Test StrategyGenerator class"""
    
    def test_initialization(self, template_manager):
        """Test StrategyGenerator initialization"""
        generator = StrategyGenerator(template_manager)
        
        assert generator.template_manager == template_manager
        assert isinstance(generator.validator, TemplateValidator)
    
    def test_generate_strategy_creates_file(
        self, template_manager, setup_template_files, sample_variables, temp_dir
    ):
        """Test that generate_strategy creates output file"""
        template_manager.load_templates()
        generator = StrategyGenerator(template_manager)
        
        output_path = temp_dir / 'output' / 'test_strategy.py'
        
        result_path = generator.generate_strategy(
            template_name='ma_crossover',
            output_path=output_path,
            variables=sample_variables
        )
        
        assert result_path.exists()
        assert result_path.is_file()
        
        content = result_path.read_text()
        assert 'Test MA Strategy' in content
        assert 'TestMAStrategy' in content
    
    def test_generate_strategy_validates_before_writing(
        self, template_manager, setup_template_files, temp_dir
    ):
        """Test that generator validates variables before writing"""
        template_manager.load_templates()
        generator = StrategyGenerator(template_manager)
        
        incomplete_vars = {'STRATEGY_NAME': 'Test'}  # Missing required vars
        output_path = temp_dir / 'output' / 'test_strategy.py'
        
        with pytest.raises(InvalidVariableError):
            generator.generate_strategy(
                template_name='ma_crossover',
                output_path=output_path,
                variables=incomplete_vars
            )
        
        assert not output_path.exists()  # File should not be created
    
    def test_generate_strategy_respects_overwrite_flag(
        self, template_manager, setup_template_files, sample_variables, temp_dir
    ):
        """Test that overwrite flag is respected"""
        template_manager.load_templates()
        generator = StrategyGenerator(template_manager)
        
        output_path = temp_dir / 'output' / 'test_strategy.py'
        
        # Generate first time
        generator.generate_strategy(
            template_name='ma_crossover',
            output_path=output_path,
            variables=sample_variables
        )
        
        # Try to generate again without overwrite
        with pytest.raises(FileExistsError):
            generator.generate_strategy(
                template_name='ma_crossover',
                output_path=output_path,
                variables=sample_variables,
                overwrite=False
            )
        
        # Generate again with overwrite
        result = generator.generate_strategy(
            template_name='ma_crossover',
            output_path=output_path,
            variables=sample_variables,
            overwrite=True
        )
        
        assert result.exists()
    
    def test_generate_config_creates_json_file(
        self, template_manager, setup_template_files, temp_dir
    ):
        """Test generating config file for strategy"""
        template_manager.load_templates()
        generator = StrategyGenerator(template_manager)
        
        config_path = temp_dir / 'output' / 'test_strategy.json'
        
        result_path = generator.generate_config(
            strategy_name='test_ma_strategy',
            output_path=config_path,
            template_name='ma_crossover'
        )
        
        assert result_path.exists()
        
        with open(result_path) as f:
            config = json.load(f)
        
        assert 'strategy_id' in config
        assert config['strategy_id'] == 'test_ma_strategy'
    
    def test_validate_generated_code(self, template_manager):
        """Test validation of generated Python code"""
        generator = StrategyGenerator(template_manager)
        
        valid_code = '''
class TestStrategy:
    def __init__(self):
        pass
'''
        
        invalid_code = '''
class TestStrategy
    # Missing colon
    pass
'''
        
        assert generator.validate_generated_code(valid_code) is True
        assert generator.validate_generated_code(invalid_code) is False


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_template_error_base_class(self):
        """Test TemplateError exception"""
        with pytest.raises(TemplateError):
            raise TemplateError("Test error")
    
    def test_template_not_found_error(self):
        """Test TemplateNotFoundError exception"""
        with pytest.raises(TemplateNotFoundError):
            raise TemplateNotFoundError("template_name")
    
    def test_invalid_variable_error(self):
        """Test InvalidVariableError exception"""
        with pytest.raises(InvalidVariableError):
            raise InvalidVariableError("Missing variable: STRATEGY_NAME")
    
    def test_handle_malformed_template_file(self, template_manager, temp_dir):
        """Test handling of malformed template files"""
        # Create template with unclosed variable placeholder
        strategies_dir = temp_dir / 'strategies'
        strategies_dir.mkdir(parents=True)
        
        malformed_file = strategies_dir / 'malformed.py.template'
        # Unclosed variable won't match pattern - will be treated as literal text
        malformed_file.write_text('{{UNCLOSED_VARIABLE')
        
        # Template loads successfully (it's just text)
        template_manager.load_templates()
        assert 'malformed' in template_manager.templates
        
        # Extract variables - should find none since pattern requires closing braces
        template = template_manager.get_template('malformed')
        variables = template.extract_variables()
        assert len(variables) == 0  # Unclosed variable not recognized
        
        # Can still render (will output literal text)
        rendered = template.render({})
        assert '{{UNCLOSED_VARIABLE' in rendered  # Literal text preserved
    
    def test_handle_missing_metadata(self, template_manager, temp_dir, sample_template_content):
        """Test handling of template without metadata"""
        # Create template without metadata
        strategies_dir = temp_dir / 'strategies'
        strategies_dir.mkdir(parents=True)
        
        template_file = strategies_dir / 'no_metadata.py.template'
        template_file.write_text(sample_template_content)
        
        # Load templates (metadata directory doesn't exist)
        template_manager.load_templates()
        
        # Should handle gracefully (or load with minimal metadata)
        # Specific behavior depends on implementation


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_workflow_template_to_strategy(
        self, template_manager, setup_template_files, sample_variables, temp_dir
    ):
        """Test complete workflow from template to generated strategy"""
        # 1. Load templates
        template_manager.load_templates()
        
        # 2. List available templates
        templates = template_manager.list_templates()
        assert len(templates) > 0
        
        # 3. Validate variables
        errors = template_manager.validate_variables('ma_crossover', sample_variables)
        assert len(errors) == 0
        
        # 4. Generate strategy
        generator = StrategyGenerator(template_manager)
        output_path = temp_dir / 'output' / 'my_strategy.py'
        
        result_path = generator.generate_strategy(
            template_name='ma_crossover',
            output_path=output_path,
            variables=sample_variables
        )
        
        # 5. Verify output
        assert result_path.exists()
        content = result_path.read_text()
        assert 'TestMAStrategy' in content
        assert '{{' not in content  # No unreplaced variables
        
        # 6. Validate generated code
        assert generator.validate_generated_code(content) is True
    
    def test_multiple_templates_can_coexist(self, temp_dir):
        """Test that multiple templates can be loaded and used"""
        # Create multiple templates
        strategies_dir = temp_dir / 'strategies'
        metadata_dir = temp_dir / 'metadata'
        strategies_dir.mkdir(parents=True)
        metadata_dir.mkdir(parents=True)
        
        # Template 1
        (strategies_dir / 'template1.py.template').write_text(
            'class {{STRATEGY_CLASS_NAME}}: pass'
        )
        
        # Template 2
        (strategies_dir / 'template2.py.template').write_text(
            'class {{STRATEGY_CLASS_NAME}}: pass'
        )
        
        # Metadata
        metadata = {
            'templates': {
                'template1': {
                    'name': 'Template 1',
                    'category': 'Test',
                    'difficulty': 'beginner',
                    'description': 'Test 1',
                    'tags': [],
                    'required_variables': ['STRATEGY_CLASS_NAME'],
                    'optional_variables': {}
                },
                'template2': {
                    'name': 'Template 2',
                    'category': 'Test',
                    'difficulty': 'beginner',
                    'description': 'Test 2',
                    'tags': [],
                    'required_variables': ['STRATEGY_CLASS_NAME'],
                    'optional_variables': {}
                }
            }
        }
        
        with open(metadata_dir / 'templates.yaml', 'w') as f:
            yaml.dump(metadata, f)
        
        # Load and verify
        manager = TemplateManager(template_dir=str(temp_dir))
        manager.load_templates()
        
        assert 'template1' in manager.templates
        assert 'template2' in manager.templates
        assert len(manager.list_templates()) == 2


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance tests"""
    
    def test_load_many_templates_efficiently(self, temp_dir):
        """Test that loading many templates is efficient"""
        # Create 50 templates
        strategies_dir = temp_dir / 'strategies'
        metadata_dir = temp_dir / 'metadata'
        strategies_dir.mkdir(parents=True)
        metadata_dir.mkdir(parents=True)
        
        templates_metadata = {'templates': {}}
        
        for i in range(50):
            template_name = f'template_{i}'
            (strategies_dir / f'{template_name}.py.template').write_text(
                f'class {{{{STRATEGY_CLASS_NAME}}}}: pass'
            )
            
            templates_metadata['templates'][template_name] = {
                'name': f'Template {i}',
                'category': 'Test',
                'difficulty': 'beginner',
                'description': f'Test template {i}',
                'tags': [],
                'required_variables': ['STRATEGY_CLASS_NAME'],
                'optional_variables': {}
            }
        
        with open(metadata_dir / 'templates.yaml', 'w') as f:
            yaml.dump(templates_metadata, f)
        
        # Time the loading
        import time
        start = time.time()
        
        manager = TemplateManager(template_dir=str(temp_dir))
        manager.load_templates()
        
        elapsed = time.time() - start
        
        assert len(manager.templates) == 50
        assert elapsed < 2.0  # Should load 50 templates in under 2 seconds


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
