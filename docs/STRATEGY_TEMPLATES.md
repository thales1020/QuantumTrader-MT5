# Strategy Templates System - Design Document

**Version:** 1.0.0  
**Date:** November 4, 2025  
**Status:** Phase 3 Implementation  
**Author:** QuantumTrader-MT5 Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Template Structure](#template-structure)
4. [Template System Components](#template-system-components)
5. [Template Variables](#template-variables)
6. [CLI Generator Tool](#cli-generator-tool)
7. [Built-in Templates](#built-in-templates)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)
10. [Testing Strategy](#testing-strategy)

---

## 🎯 Overview

### **Problem Statement**

Users want to create new trading strategies quickly but face several challenges:

1. **Boilerplate Code**: Every strategy requires the same basic structure (config, indicators, signals, risk management)
2. **Learning Curve**: New users must understand entire codebase before creating first strategy
3. **Best Practices**: Hard to know proper structure, error handling, logging patterns
4. **Time Consuming**: Building from scratch takes hours, even for simple strategies
5. **Inconsistency**: Each developer creates strategies differently

### **Solution: Strategy Templates**

A template system that provides:

- **Pre-built Templates**: Common strategy patterns ready to customize
- **Variable Substitution**: Simple placeholders for customization (strategy name, parameters, etc.)
- **CLI Generator**: Interactive tool to generate strategies from templates
- **Validation**: Ensure generated strategies follow best practices
- **Documentation**: Each template includes inline docs and usage examples

### **Goals**

- ✅ Reduce strategy creation time from hours to **minutes**
- ✅ Enable **non-programmers** to create basic strategies
- ✅ Ensure **consistency** across all strategies
- ✅ Provide **educational value** through well-documented templates
- ✅ Support **rapid prototyping** for testing ideas

---

## 🏗️ Architecture

### **System Components**

```
templates/
├── strategies/                    # Template files
│   ├── ma_crossover.py.template
│   ├── rsi_mean_reversion.py.template
│   ├── breakout.py.template
│   ├── grid_trading.py.template
│   └── multi_indicator.py.template
├── configs/                       # Config templates
│   └── strategy_config.json.template
└── metadata/                      # Template metadata
    └── templates.yaml

core/
└── template_system.py             # Core template engine

scripts/
└── create_strategy.py             # CLI generator tool

tests/
└── test_template_system.py        # Tests
```

### **Component Responsibilities**

| Component | Responsibility |
|-----------|---------------|
| **TemplateManager** | Load, validate, render templates |
| **TemplateValidator** | Validate template syntax, required variables |
| **StrategyGenerator** | Generate strategies from templates with user input |
| **CLI Tool** | Interactive command-line interface |
| **Template Files** | Pre-built strategy patterns |
| **Metadata** | Template descriptions, variables, categories |

---

## 📄 Template Structure

### **Template File Format**

Templates use Python files with special placeholder syntax:

```python
# File: templates/strategies/example.py.template
"""
{{STRATEGY_NAME}} - {{STRATEGY_DESCRIPTION}}

Generated from template: {{TEMPLATE_NAME}}
Created: {{GENERATED_DATE}}
"""

from core.base_bot import BaseTradingBot
from core.strategy_registry import StrategyRegistry
import talib
import pandas as pd
from typing import Dict, Optional


@StrategyRegistry.register("{{STRATEGY_ID}}")
class {{STRATEGY_CLASS_NAME}}(BaseTradingBot):
    """
    {{STRATEGY_DESCRIPTION}}
    
    Indicators:
{{INDICATOR_LIST}}
    
    Entry Rules:
{{ENTRY_RULES}}
    
    Exit Rules:
{{EXIT_RULES}}
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        # Strategy-specific parameters
{{PARAMETER_INIT}}
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
{{INDICATOR_CALCULATION}}
        return df
    
    def generate_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Generate trading signals"""
        df = self.calculate_indicators(df)
        
        # Get current values
{{CURRENT_VALUES}}
        
        # Entry logic
{{ENTRY_LOGIC}}
        
        return None
    
    def calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size based on risk"""
{{POSITION_SIZING}}
        return lot_size
```

### **Variable Types**

1. **Required Variables** (must be provided):
   - `{{STRATEGY_NAME}}`: Human-readable name
   - `{{STRATEGY_CLASS_NAME}}`: Python class name
   - `{{STRATEGY_ID}}`: Registry identifier
   - `{{STRATEGY_DESCRIPTION}}`: Brief description

2. **Optional Variables** (have defaults):
   - `{{TEMPLATE_NAME}}`: Source template
   - `{{GENERATED_DATE}}`: Timestamp
   - `{{AUTHOR}}`: Creator name

3. **Multi-line Variables** (code blocks):
   - `{{INDICATOR_CALCULATION}}`: Indicator code
   - `{{ENTRY_LOGIC}}`: Entry conditions
   - `{{EXIT_LOGIC}}`: Exit conditions

4. **List Variables** (bullet points):
   - `{{INDICATOR_LIST}}`: List of indicators
   - `{{ENTRY_RULES}}`: Entry criteria
   - `{{EXIT_RULES}}`: Exit criteria

---

## 🔧 Template System Components

### **1. TemplateManager**

```python
class TemplateManager:
    """Manages template loading and rendering"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.templates: Dict[str, Template] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def load_templates(self) -> None:
        """Load all templates from template directory"""
        pass
    
    def get_template(self, name: str) -> Template:
        """Get a specific template by name"""
        pass
    
    def list_templates(self) -> List[Dict]:
        """List all available templates with metadata"""
        pass
    
    def render_template(self, template_name: str, variables: Dict) -> str:
        """Render template with provided variables"""
        pass
    
    def validate_variables(self, template_name: str, variables: Dict) -> List[str]:
        """Validate that all required variables are provided"""
        pass
```

### **2. Template Class**

```python
@dataclass
class Template:
    """Represents a strategy template"""
    name: str
    path: Path
    content: str
    variables: List[str]
    required_variables: List[str]
    optional_variables: Dict[str, Any]
    category: str
    description: str
    difficulty: str  # beginner, intermediate, advanced
    tags: List[str]
    
    def render(self, variables: Dict) -> str:
        """Render template with variables"""
        pass
    
    def extract_variables(self) -> List[str]:
        """Extract all variable placeholders from template"""
        pass
```

### **3. StrategyGenerator**

```python
class StrategyGenerator:
    """Generates strategies from templates"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
    
    def generate_strategy(
        self,
        template_name: str,
        output_path: Path,
        variables: Dict,
        overwrite: bool = False
    ) -> Path:
        """Generate strategy file from template"""
        pass
    
    def generate_config(
        self,
        strategy_name: str,
        output_path: Path
    ) -> Path:
        """Generate config file for strategy"""
        pass
    
    def validate_generated_code(self, code: str) -> bool:
        """Validate generated Python code syntax"""
        pass
```

---

## 🎨 Template Variables

### **Standard Variables (All Templates)**

```yaml
# Required
STRATEGY_NAME: "My Strategy"              # Display name
STRATEGY_CLASS_NAME: "MyStrategy"         # Python class name
STRATEGY_ID: "my_strategy"                # Registry ID (lowercase, underscores)
STRATEGY_DESCRIPTION: "Brief description"

# Optional (auto-generated)
TEMPLATE_NAME: "ma_crossover"
GENERATED_DATE: "2025-11-04 10:30:00"
AUTHOR: "Your Name"
VERSION: "1.0.0"
```

### **Strategy-Specific Variables**

Each template defines its own variables:

**MA Crossover Template:**
```yaml
FAST_PERIOD: 10
SLOW_PERIOD: 30
MA_TYPE: "SMA"  # SMA, EMA, WMA
```

**RSI Mean Reversion Template:**
```yaml
RSI_PERIOD: 14
OVERSOLD_LEVEL: 30
OVERBOUGHT_LEVEL: 70
```

**Breakout Template:**
```yaml
LOOKBACK_PERIOD: 20
BREAKOUT_THRESHOLD: 1.5  # ATR multiplier
```

---

## 💻 CLI Generator Tool

### **Interactive Mode**

```bash
PS> python scripts/create_strategy.py

╔══════════════════════════════════════════════════════════╗
║     QuantumTrader-MT5 Strategy Generator v1.0.0          ║
╚══════════════════════════════════════════════════════════╝

Available Templates:
  1. MA Crossover (Beginner) - Moving average crossover strategy
  2. RSI Mean Reversion (Beginner) - RSI-based mean reversion
  3. Breakout (Intermediate) - Price breakout strategy
  4. Grid Trading (Advanced) - Grid-based trading system
  5. Multi-Indicator (Advanced) - Combine multiple indicators

Select template (1-5): 1

── MA Crossover Template ──

Strategy Name: My MA Strategy
Strategy ID (lowercase, underscores): my_ma_strategy
Description: Simple moving average crossover

── MA Crossover Parameters ──
Fast MA Period [10]: 10
Slow MA Period [30]: 50
MA Type (SMA/EMA/WMA) [SMA]: EMA

── Output Options ──
Output directory [./strategies]: ./strategies
Generate config file? [Y/n]: Y

── Summary ──
Template: MA Crossover
Strategy: My MA Strategy (my_ma_strategy)
Output: ./strategies/my_ma_strategy.py
Config: ./config/my_ma_strategy.json

Generate strategy? [Y/n]: Y

✅ Strategy created: ./strategies/my_ma_strategy.py
✅ Config created: ./config/my_ma_strategy.json

Next steps:
  1. Review generated files
  2. Customize if needed
  3. Add to config.json
  4. Run backtest: python -m engines.backtest_engine my_ma_strategy
```

### **Command-Line Mode**

```bash
# Quick generation with all parameters
python scripts/create_strategy.py \
  --template ma_crossover \
  --name "My MA Strategy" \
  --id my_ma_strategy \
  --output ./strategies \
  --fast-period 10 \
  --slow-period 50 \
  --ma-type EMA \
  --generate-config

# List all templates
python scripts/create_strategy.py --list

# Show template details
python scripts/create_strategy.py --info ma_crossover

# Use config file for variables
python scripts/create_strategy.py \
  --template ma_crossover \
  --config template_vars.json
```

---

## 📚 Built-in Templates

### **1. MA Crossover (Beginner)**

**Category:** Trend Following  
**Indicators:** SMA/EMA/WMA  
**Difficulty:** ⭐ Beginner

**Entry:**
- Buy: Fast MA crosses above Slow MA
- Sell: Fast MA crosses below Slow MA

**Variables:**
- `FAST_PERIOD`: Fast MA period (default: 10)
- `SLOW_PERIOD`: Slow MA period (default: 30)
- `MA_TYPE`: MA type - SMA/EMA/WMA (default: SMA)

**Use Cases:**
- Learning trading bot basics
- Trend following in trending markets
- Foundation for more complex strategies

---

### **2. RSI Mean Reversion (Beginner)**

**Category:** Mean Reversion  
**Indicators:** RSI  
**Difficulty:** ⭐ Beginner

**Entry:**
- Buy: RSI < oversold level (e.g., 30)
- Sell: RSI > overbought level (e.g., 70)

**Exit:**
- Take profit when RSI reaches neutral (50)
- Stop loss based on ATR

**Variables:**
- `RSI_PERIOD`: RSI period (default: 14)
- `OVERSOLD_LEVEL`: Oversold threshold (default: 30)
- `OVERBOUGHT_LEVEL`: Overbought threshold (default: 70)
- `TP_MULTIPLIER`: Take profit ATR multiplier (default: 2.0)
- `SL_MULTIPLIER`: Stop loss ATR multiplier (default: 1.5)

**Use Cases:**
- Range-bound markets
- Counter-trend trading
- Quick scalping setups

---

### **3. Breakout (Intermediate)**

**Category:** Breakout  
**Indicators:** Bollinger Bands, ATR, Volume  
**Difficulty:** ⭐⭐ Intermediate

**Entry:**
- Buy: Price breaks above upper Bollinger Band + volume confirmation
- Sell: Price breaks below lower Bollinger Band + volume confirmation

**Exit:**
- Trailing stop based on ATR
- Time-based exit after N bars

**Variables:**
- `BB_PERIOD`: Bollinger Bands period (default: 20)
- `BB_STD`: Standard deviation multiplier (default: 2.0)
- `VOLUME_MULTIPLIER`: Volume confirmation (default: 1.5x average)
- `TRAILING_ATR`: Trailing stop ATR multiplier (default: 2.0)
- `MAX_BARS`: Max bars to hold position (default: 50)

**Use Cases:**
- Volatile markets
- News trading
- Momentum strategies

---

### **4. Grid Trading (Advanced)**

**Category:** Grid  
**Indicators:** None (price-based)  
**Difficulty:** ⭐⭐⭐ Advanced

**Strategy:**
- Place buy/sell orders at regular price intervals (grid)
- Profit from range-bound oscillations
- Dynamic grid adjustment based on volatility

**Entry:**
- Buy orders below current price at grid intervals
- Sell orders above current price at grid intervals

**Exit:**
- Close opposite orders when price moves
- Adjust grid when volatility changes

**Variables:**
- `GRID_SIZE`: Grid interval in pips (default: 50)
- `NUM_LEVELS`: Number of grid levels (default: 10)
- `LOT_SIZE`: Lot size per level (default: 0.01)
- `TAKE_PROFIT`: TP per level in pips (default: 50)
- `MAX_POSITIONS`: Max simultaneous positions (default: 20)

**Use Cases:**
- Range-bound markets
- Forex pairs with tight ranges
- Automated market making

⚠️ **Warning:** Grid trading carries high risk. Requires proper risk management.

---

### **5. Multi-Indicator (Advanced)**

**Category:** Hybrid  
**Indicators:** Multiple (customizable)  
**Difficulty:** ⭐⭐⭐ Advanced

**Strategy:**
- Combine multiple indicators for confluence
- Weighted scoring system
- Minimum score threshold for entry

**Entry:**
- Calculate score from each indicator
- Enter when total score > threshold
- Direction based on highest-weighted signal

**Variables:**
- `INDICATORS`: List of indicators to use
- `WEIGHTS`: Weight for each indicator
- `THRESHOLD`: Minimum score to enter (default: 0.7)
- `CONFIRMATION_BARS`: Bars to confirm signal (default: 2)

**Example Configuration:**
```json
{
  "indicators": ["RSI", "MACD", "BB", "STOCH"],
  "weights": {
    "RSI": 0.3,
    "MACD": 0.3,
    "BB": 0.2,
    "STOCH": 0.2
  },
  "threshold": 0.7
}
```

**Use Cases:**
- Complex strategy development
- Reducing false signals
- High-confidence setups

---

## 📖 Usage Examples

### **Example 1: Generate MA Crossover Strategy**

```python
from core.template_system import TemplateManager, StrategyGenerator

# Initialize
template_mgr = TemplateManager()
template_mgr.load_templates()

generator = StrategyGenerator(template_mgr)

# Define variables
variables = {
    'STRATEGY_NAME': 'EMA Golden Cross',
    'STRATEGY_CLASS_NAME': 'EMAGoldenCross',
    'STRATEGY_ID': 'ema_golden_cross',
    'STRATEGY_DESCRIPTION': 'EMA 50/200 crossover strategy',
    'FAST_PERIOD': 50,
    'SLOW_PERIOD': 200,
    'MA_TYPE': 'EMA'
}

# Generate strategy
output_path = generator.generate_strategy(
    template_name='ma_crossover',
    output_path=Path('./strategies/ema_golden_cross.py'),
    variables=variables
)

print(f"✅ Strategy created: {output_path}")
```

### **Example 2: List All Templates**

```python
from core.template_system import TemplateManager

template_mgr = TemplateManager()
template_mgr.load_templates()

templates = template_mgr.list_templates()

for template in templates:
    print(f"""
Name: {template['name']}
Category: {template['category']}
Difficulty: {template['difficulty']}
Description: {template['description']}
Variables: {', '.join(template['required_variables'])}
    """)
```

### **Example 3: Validate Before Generation**

```python
from core.template_system import TemplateManager

template_mgr = TemplateManager()
template_mgr.load_templates()

variables = {
    'STRATEGY_NAME': 'My Strategy',
    'STRATEGY_ID': 'my_strategy'
    # Missing STRATEGY_CLASS_NAME and STRATEGY_DESCRIPTION
}

# Validate
errors = template_mgr.validate_variables('ma_crossover', variables)

if errors:
    print("❌ Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ All required variables provided")
```

---

## ✅ Best Practices

### **For Template Creators**

1. **Documentation:**
   - Include comprehensive docstrings
   - Add inline comments for complex logic
   - Provide usage examples

2. **Validation:**
   - Validate all input parameters
   - Add type hints
   - Handle edge cases

3. **Defaults:**
   - Provide sensible default values
   - Make most parameters optional
   - Document why defaults were chosen

4. **Testing:**
   - Include example test cases
   - Test with various parameter combinations
   - Validate generated code syntax

### **For Template Users**

1. **Start Simple:**
   - Begin with beginner templates
   - Understand each component before customization
   - Test thoroughly on demo account

2. **Customization:**
   - Review generated code before using
   - Adjust parameters based on backtesting
   - Add plugins for additional features

3. **Risk Management:**
   - Always implement stop losses
   - Test position sizing carefully
   - Monitor live trading closely

4. **Version Control:**
   - Commit generated strategies to git
   - Document changes and reasons
   - Keep backup of working versions

---

## 🧪 Testing Strategy

### **Unit Tests**

```python
# Test template loading
def test_load_templates():
    """Test that all templates load successfully"""
    pass

# Test variable extraction
def test_extract_variables():
    """Test extracting variables from template"""
    pass

# Test rendering
def test_render_template():
    """Test template rendering with variables"""
    pass

# Test validation
def test_validate_required_variables():
    """Test validation of required variables"""
    pass

# Test generation
def test_generate_strategy():
    """Test full strategy generation"""
    pass
```

### **Integration Tests**

```python
# Test CLI tool
def test_cli_generator():
    """Test command-line generator tool"""
    pass

# Test generated code
def test_generated_code_valid():
    """Test that generated code is valid Python"""
    pass

# Test generated strategy runs
def test_generated_strategy_runs():
    """Test that generated strategy can execute"""
    pass
```

### **Validation Tests**

```python
# Test each template generates valid code
@pytest.mark.parametrize("template_name", [
    "ma_crossover",
    "rsi_mean_reversion",
    "breakout",
    "grid_trading",
    "multi_indicator"
])
def test_template_generates_valid_code(template_name):
    """Test each template generates syntactically valid code"""
    pass
```

---

## 🔄 Template Metadata Format

### **templates/metadata/templates.yaml**

```yaml
templates:
  ma_crossover:
    name: "MA Crossover"
    category: "Trend Following"
    difficulty: "beginner"
    description: "Moving average crossover strategy"
    tags: ["trend", "crossover", "beginner"]
    file: "strategies/ma_crossover.py.template"
    config: "configs/ma_crossover.json.template"
    required_variables:
      - STRATEGY_NAME
      - STRATEGY_CLASS_NAME
      - STRATEGY_ID
      - STRATEGY_DESCRIPTION
    optional_variables:
      FAST_PERIOD: 10
      SLOW_PERIOD: 30
      MA_TYPE: "SMA"
      AUTHOR: "QuantumTrader"
      VERSION: "1.0.0"
    examples:
      - name: "EMA Golden Cross"
        description: "Classic 50/200 EMA crossover"
        variables:
          FAST_PERIOD: 50
          SLOW_PERIOD: 200
          MA_TYPE: "EMA"

  rsi_mean_reversion:
    name: "RSI Mean Reversion"
    category: "Mean Reversion"
    difficulty: "beginner"
    description: "RSI-based mean reversion strategy"
    tags: ["rsi", "mean-reversion", "beginner"]
    file: "strategies/rsi_mean_reversion.py.template"
    required_variables:
      - STRATEGY_NAME
      - STRATEGY_CLASS_NAME
      - STRATEGY_ID
      - STRATEGY_DESCRIPTION
    optional_variables:
      RSI_PERIOD: 14
      OVERSOLD_LEVEL: 30
      OVERBOUGHT_LEVEL: 70
      TP_MULTIPLIER: 2.0
      SL_MULTIPLIER: 1.5
```

---

## 📊 Success Metrics

After Phase 3 completion, we should achieve:

- ✅ **5+ Templates**: Cover common strategy patterns
- ✅ **<5 Minutes**: Time to generate new strategy
- ✅ **100% Valid**: All generated code is syntactically valid
- ✅ **80% Usable**: Generated strategies work with minimal modification
- ✅ **Easy Onboarding**: New users can create strategies without reading entire codebase

---

## 🚀 Future Enhancements

### **Phase 3.1: Advanced Features**
- Template inheritance (base template + variations)
- Multi-file templates (strategy + tests + docs)
- Web-based template editor
- Template marketplace/sharing

### **Phase 3.2: AI Integration**
- AI-powered template suggestion based on description
- Parameter optimization suggestions
- Automatic documentation generation

### **Phase 3.3: Visual Template Builder**
- Drag-and-drop strategy builder
- Visual indicator configuration
- Real-time preview of generated code

---

## 📝 Summary

Strategy Templates System provides:

✅ **Speed**: Generate strategies in minutes  
✅ **Consistency**: All strategies follow best practices  
✅ **Education**: Learn from well-documented examples  
✅ **Flexibility**: Easy customization and extension  
✅ **Quality**: Validated, tested, production-ready code

**Phase 3 Deliverables:**
1. Core template system (`core/template_system.py`)
2. 5+ strategy templates
3. CLI generator tool (`scripts/create_strategy.py`)
4. Comprehensive tests
5. Documentation and examples

**Next Steps:** Begin implementation with TDD approach! 🎯
