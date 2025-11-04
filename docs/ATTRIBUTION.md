# 📜 Attribution & Credits

## Original Project

This project was **initially inspired by** various open-source MT5-SuperTrend implementations in the algorithmic trading community.

### Original Source
- **Inspiration**: Open-source MT5-SuperTrend trading bots
- **Concept**: Basic SuperTrend indicator with MT5 integration
- **Original Author**: Multiple contributors to MT5/SuperTrend community
- **Original License**: MIT License (common in the community)
- **Starting Point**: Early 2024

### What Was Used as Reference
The original implementations provided:
-  Basic SuperTrend indicator concept
-  MetaTrader 5 Python API usage patterns
-  Simple position management ideas
-  Basic project structure concept

---

## Significant Modifications & Enhancements

This project has been **substantially developed** from the ground up by **Trần Trọng Hiếu (xPOURY4 / thales1020 / TheRealPourya)** with **95%+ original code**:

### 🧠 Machine Learning Integration
- **NEW**: K-means clustering for dynamic parameter optimization
- **NEW**: ML-based factor selection based on volatility conditions
- **NEW**: Performance-weighted signal filtering
- **MODIFIED**: SuperTrend calculation enhanced with ML optimization

###  Advanced Trading Features
- **NEW**: Dual Orders Strategy (RR 1:1 + Main RR)
- **NEW**: Automatic Breakeven SL Movement
- **NEW**: ICT Bot with Order Blocks, Fair Value Gaps, Liquidity Sweeps
- **NEW**: Multi-strategy architecture with Strategy Registry
- **NEW**: Plugin system for extensibility
- **NEW**: Event-driven architecture with hooks
- **MODIFIED**: Risk management completely rewritten

###  Architecture & Code Quality
- **NEW**: Abstract base class pattern for all bots
- **NEW**: Strategy Registry with decorator-based registration
- **NEW**: Config Manager with YAML, profiles, env vars
- **NEW**: Extension points for customization
- **NEW**: Comprehensive test suite (85+ tests)
- **REWRITTEN**: Project structure following Clean Architecture principles
- **REWRITTEN**: All core modules for maintainability

###  Analysis & Monitoring
- **NEW**: Advanced backtesting engine with detailed metrics
- **NEW**: Performance monitoring dashboard
- **NEW**: Equity curve visualization
- **NEW**: Multi-symbol batch backtesting
- **NEW**: Comprehensive reporting system

### 📚 Documentation
- **NEW**: 15+ documentation files covering all aspects
- **NEW**: ICT strategy guide
- **NEW**: Crypto trading guide
- **NEW**: Customization guide
- **NEW**: VPS deployment guide
- **NEW**: Plugin development guide

###  DevOps & Deployment
- **NEW**: PyPI package publication
- **NEW**: VPS deployment scripts
- **NEW**: Docker support (planned)
- **NEW**: Automated testing & CI/CD (planned)

---

## Code Ownership Breakdown

### Original Reference Code (~2-5% concepts)
- Basic SuperTrend indicator concept (completely rewritten)
- MT5 API usage patterns (heavily modified)
- Simple order execution ideas (completely redesigned)

### New Code by Trần Trọng Hiếu (~95-98%)
- All ML-related code (K-means, optimization) - **100% original**
- All ICT strategy code - **100% original**
- All dual orders logic - **100% original**
- All breakeven SL logic - **100% original**
- All architectural improvements - **100% original**
- All plugin system code - **100% original**
- All event system code - **100% original**
- All extension points - **100% original**
- All testing code - **100% original**
- All documentation - **100% original**
- All backtest engines - **100% original**
- All monitoring & analytics - **100% original**

---

## License

This project is licensed under the **MIT License** (same as original).

**MIT License** allows:
-  Commercial use
-  Modification
-  Distribution
-  Private use

**Requirements**:
-  Include original license and copyright notice
-  State changes made (covered in this file)

See [LICENSE](../LICENSE) for full text.

---

## Why This Attribution Matters

This attribution file serves multiple purposes:

1. **Ethical**: Give credit to original author for their initial work
2. **Legal**: Comply with MIT license requirements
3. **Transparency**: Show evolution of the project
4. **Educational**: Demonstrate good open-source practices
5. **Professional**: Build trust with users and contributors

---

## How to Cite This Project

### Academic Citation
```
Trần Trọng Hiếu (xPOURY4/thales1020/TheRealPourya). (2024-2025). 
ML-SuperTrend-MT5: Machine Learning Enhanced SuperTrend Trading Bot for 
MetaTrader 5 [Inspired by open-source MT5-SuperTrend concepts]. 
GitHub. https://github.com/xPOURY4/ML-SuperTrend-MT5
```

### BibTeX
```bibtex
@software{ml_supertrend_mt5,
  author = {Trần Trọng Hiếu (xPOURY4/thales1020/TheRealPourya)},
  title = {ML-SuperTrend-MT5: Machine Learning Enhanced SuperTrend Trading Bot},
  year = {2024-2025},
  publisher = {GitHub},
  url = {https://github.com/xPOURY4/ML-SuperTrend-MT5},
  note = {Inspired by open-source MT5-SuperTrend community implementations}
}
```

### Markdown Link
```markdown
[ML-SuperTrend-MT5](https://github.com/xPOURY4/ML-SuperTrend-MT5) by 
[Trần Trọng Hiếu](https://github.com/thales1020) - 
Original implementation inspired by open-source MT5-SuperTrend community

Author's GitHub: https://github.com/thales1020
Project Repository: https://github.com/xPOURY4/ML-SuperTrend-MT5
```

---

## Contributing

If you found this project helpful, please:

1.  **Star this repository**
2.  **Report bugs** via Issues
3.  **Suggest features** via Issues
4. 🔀 **Submit pull requests**
5.  **Share with others**
6. 💬 **Follow on Twitter**: [@TheRealPourya](https://twitter.com/TheRealPourya)

---

## Contact

**Author & Maintainer**: Trần Trọng Hiếu

- **Personal GitHub**: [@thales1020](https://github.com/thales1020)  Main Profile
- **Project Repository**: [@xPOURY4/ML-SuperTrend-MT5](https://github.com/xPOURY4/ML-SuperTrend-MT5)
- **Twitter**: [@TheRealPourya](https://twitter.com/TheRealPourya)

---

## Acknowledgments

### Special Thanks To:

1. **Open-Source MT5/SuperTrend Community** - For sharing knowledge and implementations that inspired this project
2. **MetaTrader 5** - For providing excellent API and platform
3. **Python Community** - For amazing libraries (pandas, numpy, scikit-learn, talib)
4. **Trading Community** - For feedback and suggestions
5. **Contributors** - Everyone who contributed code, documentation, or ideas

---

## Future Plans

This project continues to evolve with planned features:

- 🔮 Deep Learning integration (LSTM, Transformers)
-  Multi-broker support
- 📱 Mobile app for monitoring
- 🤖 Telegram bot for control
-  Web dashboard
- 🐳 Docker containerization
- ☁️ Cloud deployment options
- 🔄 Portfolio management
-  Advanced risk analytics

---

**Last Updated**: October 23, 2025  
**Project Status**:  Active Development  
**Author**: Trần Trọng Hiếu (xPOURY4 | thales1020)

---

>  **Note**: This is an original implementation inspired by open-source concepts. The vast majority (95%+) of the code is original work developed from scratch.
