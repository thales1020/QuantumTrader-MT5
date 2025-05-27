# Contributing to ML-SuperTrend-MT5

First off, thank you for considering contributing to ML-SuperTrend-MT5! It's people like you that make this project better.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include logs and screenshots if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the existing style
6. Issue that pull request!

## Development Process

1. **Setup Development Environment**
   ```bash
   git clone https://github.com/xPOURY4/ML-SuperTrend-MT5.git
   cd ML-SuperTrend-MT5
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Write clean, readable code
   - Add comments where necessary
   - Follow PEP 8 style guide
   - Update documentation

4. **Test Your Changes**
   ```bash
   pytest tests/
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

## Style Guidelines

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Example:
```python
def calculate_position_size(
    balance: float, 
    risk_percent: float, 
    stop_loss_pips: float
) -> float:
    """
    Calculate position size based on account risk.
    
    Args:
        balance: Account balance in base currency
        risk_percent: Risk percentage per trade
        stop_loss_pips: Stop loss distance in pips
        
    Returns:
        Position size in lots
    """
    risk_amount = balance * (risk_percent / 100)
    position_size = risk_amount / (stop_loss_pips * 10)
    return round(position_size, 2)
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting PR
- Aim for at least 80% code coverage
- Use meaningful test names

## Documentation

- Update README.md if you change functionality
- Update docstrings for any modified functions
- Add examples for new features
- Keep documentation clear and concise

## Questions?

Feel free to contact the maintainer at [@TheRealPourya](https://twitter.com/TheRealPourya) on Twitter.

Thank you for contributing! 🚀