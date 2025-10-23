# 🎯 PROJECT SCOPE - ML-SuperTrend-MT5

**Document Version**: 1.0  
**Date**: October 23, 2025  
**Author**: xPOURY4  
**Status**: Active Development

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#-executive-summary)
2. [Project Vision & Mission](#-project-vision--mission)
3. [Project Boundaries](#-project-boundaries)
4. [Core Features](#-core-features)
5. [Technical Scope](#-technical-scope)
6. [Target Users](#-target-users)
7. [Success Criteria](#-success-criteria)
8. [Out of Scope](#-out-of-scope)
9. [Dependencies](#-dependencies)
10. [Timeline & Milestones](#-timeline--milestones)

---

## 🎯 EXECUTIVE SUMMARY

**ML-SuperTrend-MT5** là một hệ thống automated trading bot cho MetaTrader 5, tập trung vào:

### **Primary Purpose**:
- 📚 **Educational**: Dạy về algorithmic trading, ML integration, và risk management
- 🤖 **Automated Trading**: Thực thi chiến lược trading tự động 24/7
- 📊 **Research Platform**: Thử nghiệm và optimize trading strategies

### **Core Value Proposition**:
```
"Một trading bot mã nguồn mở, dễ hiểu, dễ customize,
kết hợp Machine Learning với các chiến lược trading hiện đại"
```

### **Project Type**: 
- Open Source Educational Trading System
- Personal/Retail Trading Automation
- Python-based Algorithmic Trading Framework

---

## 🌟 PROJECT VISION & MISSION

### **Vision** (3-5 years):
> "Trở thành một trong những open-source trading bot phổ biến nhất cho MT5,
> với cộng đồng contributors mạnh mẽ và documentation xuất sắc"

### **Mission**:
1. **Democratize Algo Trading**: Làm cho algorithmic trading accessible cho mọi người
2. **Education First**: Cung cấp learning resource cho traders muốn học code
3. **Transparency**: Hoàn toàn open-source, không hidden features
4. **Community Building**: Xây dựng cộng đồng chia sẻ strategies và improvements

### **Core Values**:
- ✅ **Transparency**: Mọi thứ đều open và documented
- ✅ **Education**: Learning > Profits
- ✅ **Quality**: Code quality và testing là ưu tiên
- ✅ **Risk Awareness**: Luôn nhấn mạnh rủi ro của trading
- ✅ **Community**: Collaborative development

---

## 🔲 PROJECT BOUNDARIES

### **IN SCOPE** ✅

#### **1. Trading Strategies**
- ✅ SuperTrend with ML optimization (K-means clustering)
- ✅ ICT (Inner Circle Trader) concepts:
  - Order Blocks
  - Fair Value Gaps
  - Liquidity Sweeps
  - Market Structure (BOS/CHoCH)
- ✅ Dual Orders Strategy (RR 1:1 + Main RR)
- ✅ **NEW**: Breakeven SL Management

#### **2. Markets & Instruments**
- ✅ **Forex**: Major pairs (EUR/USD, GBP/USD, etc.)
- ✅ **Crypto**: BTC, ETH, major altcoins
- ✅ **Commodities**: Gold (XAU), Silver, Oil
- ✅ **Indices**: US30, NAS100, SPX500

#### **3. Platform Support**
- ✅ **MetaTrader 5**: Primary platform
- ✅ **Windows**: Main OS support
- ⚠️ **Linux/Mac**: Limited (MT5 constraints)

#### **4. Features**
- ✅ Automated position opening/closing
- ✅ Dynamic position sizing
- ✅ Risk management (SL/TP/trailing)
- ✅ Backtesting engine
- ✅ Performance analytics
- ✅ Multi-symbol support
- ✅ Logging & monitoring
- ✅ Configuration management

#### **5. Development**
- ✅ Python 3.8+
- ✅ Open source (MIT License)
- ✅ Unit testing
- ✅ Documentation
- ✅ Community contributions

---

### **OUT OF SCOPE** ❌

#### **1. NOT Included**:
❌ **Web Interface/Dashboard**: Không có web UI (CLI only)
❌ **Mobile App**: Không có iOS/Android app
❌ **Cloud Hosting**: Không cung cấp hosted solution
❌ **Copy Trading**: Không support signal distribution
❌ **Social Trading Features**: Không có follow/copy traders
❌ **Broker Integration**: Chỉ support MT5, không direct broker API

#### **2. NOT Responsible For**:
❌ **Broker Selection**: Users tự chọn broker
❌ **VPS Setup**: Users tự setup VPS nếu cần
❌ **Tax/Legal Advice**: Không cung cấp legal guidance
❌ **Guaranteed Profits**: Không bảo đảm lợi nhuận
❌ **Customer Support**: Community-driven support only

#### **3. Technical Limitations**:
❌ **HFT (High-Frequency Trading)**: Không phải HFT system
❌ **Tick-level Data**: Không xử lý tick data
❌ **Options/Futures**: Chỉ spot/CFD trading
❌ **Multi-broker**: Một bot = một MT5 account
❌ **Real-time News**: News filter là placeholder

---

## 💎 CORE FEATURES

### **Tier 1 - Must Have** (Critical)

#### **1. Trading Bots** 🤖
```python
core/
├── supertrend_bot.py    # ML-optimized SuperTrend
└── ict_bot.py           # ICT concepts bot
```

**Capabilities**:
- Signal generation
- Position management
- Risk calculation
- Order execution

#### **2. Risk Management** 🛡️
```python
Features:
- Dynamic position sizing (% of balance)
- ATR-based SL/TP
- Daily loss limits
- Trailing stop loss
- Dual orders risk split
- Breakeven SL movement
```

#### **3. Backtesting** 📊
```python
engines/
├── backtest_engine.py
└── ict_backtest_engine.py

Metrics:
- Win Rate
- Profit Factor
- Sharpe Ratio
- Max Drawdown
- Equity curve
```

#### **4. Configuration** ⚙️
```json
config/config.json

Supports:
- Multi-account (demo/live)
- Multi-symbol settings
- Risk parameters
- Strategy parameters
```

---

### **Tier 2 - Should Have** (Important)

#### **5. Testing Suite** 🧪
```
tests/
├── test_configuration.py     (19 tests)
├── test_risk_management.py   (32 tests)
├── test_live_trading.py      (34 tests)
└── test_crypto_trading.py    (16 tests)

Total: 85+ unit tests
```

#### **6. Documentation** 📚
```
docs/
├── QUICKSTART.md
├── FAQ.md
├── ICT_README.md
├── CRYPTO_TRADING_GUIDE.md
├── DUAL_ORDERS_IMPLEMENTATION.md
├── BREAKEVEN_SL_FEATURE.md
└── ... (13 files total)
```

#### **7. Utility Scripts** 🔧
```python
scripts/
├── runners/          # Bot execution scripts
├── backtest/         # Backtesting scripts
└── utils/            # Helper utilities
```

---

### **Tier 3 - Nice to Have** (Enhancement)

#### **8. Performance Monitoring** 📈
- Real-time stats display
- Equity curve visualization
- Trade history export
- Performance reports

#### **9. Multi-Symbol Trading** 🔄
- Simultaneous trading on multiple pairs
- Correlation management
- Portfolio-level risk

#### **10. Advanced Features** ⚡
- Volume confirmation
- Session management
- News filter framework (placeholder)
- Watchdog process

---

## 🔧 TECHNICAL SCOPE

### **Technology Stack**

#### **Core Technologies**:
```yaml
Language: Python 3.8+
Platform: MetaTrader 5
API: MetaTrader5 Python package
ML: scikit-learn (K-means)
TA: TA-Lib, pandas, numpy
```

#### **Dependencies**:
```python
# Core
MetaTrader5==5.0.45
pandas>=2.0.2
numpy==1.24.3
scikit-learn==1.3.0

# Visualization
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0

# (See requirements.txt for full list)
```

#### **Architecture**:
```
Pattern: Layered Architecture + DDD elements
Style: Modular Monolith
Design Patterns:
  - Strategy Pattern (bots)
  - Builder Pattern (config)
  - Factory Pattern (bot creation)
  - Observer Pattern (monitoring)
```

### **Code Standards**:
- ✅ PEP 8 compliance
- ✅ Type hints
- ✅ Docstrings
- ✅ Unit tests (>80% coverage target)
- ✅ Clean code principles

### **Performance Requirements**:
```yaml
Latency: <1 second per trading cycle
Memory: <500MB typical usage
CPU: Low intensity (single-core adequate)
Storage: <100MB excluding logs/reports
Uptime: 24/7 capability (with VPS)
```

---

## 👥 TARGET USERS

### **Primary Users** (Core Audience)

#### **1. Algorithmic Trading Learners** 🎓
```yaml
Profile:
  - Programming knowledge: Intermediate Python
  - Trading knowledge: Basic technical analysis
  - Goal: Learn algorithmic trading
  - Time: Part-time learners
  
Needs:
  - Clear documentation
  - Example code
  - Educational resources
  - Community support
```

#### **2. Retail Traders** 📊
```yaml
Profile:
  - Programming knowledge: Basic to Intermediate
  - Trading knowledge: Good (2+ years)
  - Goal: Automate existing strategies
  - Time: Active traders
  
Needs:
  - Reliable execution
  - Risk management
  - Performance tracking
  - Easy customization
```

#### **3. Python Developers** 💻
```yaml
Profile:
  - Programming knowledge: Advanced Python
  - Trading knowledge: Basic to Good
  - Goal: Build/customize trading systems
  - Time: Developers exploring fintech
  
Needs:
  - Clean codebase
  - Good architecture
  - Extension points
  - API documentation
```

---

### **Secondary Users** (Extended Audience)

#### **4. Trading Educators** 👨‍🏫
```yaml
Use Case: Teaching material for courses
Needs: Well-documented, easy to understand code
```

#### **5. Trading System Researchers** 🔬
```yaml
Use Case: Research platform for strategy testing
Needs: Robust backtesting, data export
```

#### **6. Open Source Contributors** 🤝
```yaml
Use Case: Contributing improvements
Needs: Clear contribution guidelines, good documentation
```

---

## ✅ SUCCESS CRITERIA

### **Technical Metrics**

#### **Code Quality**:
```yaml
✅ Test Coverage: >80%
✅ Documentation Coverage: 100% (all public APIs)
✅ Code Duplication: <5%
✅ Complexity: Cyclomatic <10 average
✅ Type Hints: >90% coverage
```

#### **Performance**:
```yaml
✅ Backtest Speed: >100 trades/second processing
✅ Live Trading Latency: <1s per cycle
✅ Memory Usage: <500MB steady state
✅ Uptime: >99% (with proper VPS setup)
```

#### **Reliability**:
```yaml
✅ Bug Rate: <1 critical bug per 1000 lines
✅ Test Pass Rate: 100%
✅ MT5 Connection Success: >99%
✅ Order Execution Success: >98%
```

---

### **User Success Metrics**

#### **Adoption**:
```yaml
✅ GitHub Stars: 100+ (milestone)
✅ PyPI Downloads: 1000+/month
✅ Active Users: 50+ regular users
✅ Contributors: 5+ active contributors
```

#### **Community**:
```yaml
✅ GitHub Issues Response: <48 hours
✅ Documentation Feedback: Positive (>80%)
✅ Community Contributions: 10+ PRs accepted
✅ Tutorial Views: 1000+ views
```

#### **Educational Impact**:
```yaml
✅ Learning Resources Created: 10+ tutorials/guides
✅ User Success Stories: 5+ testimonials
✅ Educational Projects Based On: 3+ forks with modifications
```

---

### **Trading Performance** (Backtesting)

```yaml
Target Metrics (Historical Data):
✅ Win Rate: >40% (realistic)
✅ Profit Factor: >1.2
✅ Max Drawdown: <15%
✅ Sharpe Ratio: >1.0
✅ Risk/Reward: 1:1.5 minimum

Note: Past performance ≠ Future results
These are BACKTESTING targets, not live guarantees
```

---

## 🚫 OUT OF SCOPE (Detailed)

### **Features Explicitly NOT Included**

#### **1. Web/Mobile Applications** ❌
```
NOT Building:
- Web dashboard
- Mobile apps (iOS/Android)
- REST API server
- WebSocket streaming
- Cloud-based platform

Why: Focus on core trading logic, not UI/infrastructure
Alternative: Users can build their own interfaces
```

#### **2. Broker Services** ❌
```
NOT Providing:
- Broker recommendations
- Broker partnerships
- Account management
- Deposit/withdrawal handling
- Broker API integration (non-MT5)

Why: Broker-agnostic, users choose their own
Alternative: Users use any MT5-compatible broker
```

#### **3. Financial Advisory** ❌
```
NOT Offering:
- Investment advice
- Portfolio management services
- Tax guidance
- Legal compliance advice
- Trading signals as a service

Why: Educational tool only, not a financial service
Alternative: Users consult licensed professionals
```

#### **4. Commercial Services** ❌
```
NOT Selling:
- Premium features/versions
- Managed accounts
- VPS hosting
- Training courses (paid)
- Consulting services

Why: Open source, community-driven project
Alternative: Free, self-hosted, self-managed
```

#### **5. Advanced Trading Features** ❌
```
NOT Supporting:
- High-Frequency Trading (HFT)
- Arbitrage strategies
- Market making
- Options trading
- Futures spreads
- Algorithmic order routing

Why: Scope limited to directional spot/CFD trading
Alternative: Use specialized platforms for these
```

#### **6. Enterprise Features** ❌
```
NOT Including:
- Multi-user system
- Role-based access control
- Audit logging
- Compliance reporting
- SLA guarantees
- Professional support

Why: Designed for individual traders, not institutions
Alternative: Fork and customize for enterprise needs
```

---

## 🔗 DEPENDENCIES

### **Critical Dependencies** (Project Cannot Function Without)

#### **1. MetaTrader 5**
```yaml
Type: External Platform
Version: MT5 Build 3000+
Status: Third-party, required
Risk: Medium (platform changes, API changes)
Mitigation: Version pinning, compatibility tests
```

#### **2. Python Ecosystem**
```yaml
Type: Runtime Environment
Version: Python 3.8+
Status: Stable, well-supported
Risk: Low (mature ecosystem)
Dependencies: See requirements.txt
```

#### **3. MT5 Broker Account**
```yaml
Type: External Service
Requirement: MT5-compatible broker
Status: User-provided
Risk: Medium (broker availability, costs)
Mitigation: Broker-agnostic design
```

---

### **Important Dependencies** (Project Degraded Without)

#### **4. Internet Connection**
```yaml
Requirement: Stable internet for MT5 connection
Bandwidth: Low (<1 Mbps adequate)
Latency: <100ms preferred for execution
Uptime: 99%+ for 24/7 trading
```

#### **5. Computing Resources**
```yaml
CPU: 1+ core, 2GHz+
RAM: 2GB+ available
Disk: 10GB+ free space
OS: Windows 10/11 (for MT5)
Optional: VPS for 24/7 operation
```

---

### **Optional Dependencies** (Enhanced Experience)

#### **6. Testing Tools**
```yaml
pytest: Unit testing
pytest-cov: Coverage reports
black: Code formatting
flake8: Linting
mypy: Type checking
```

#### **7. Development Tools**
```yaml
VS Code / PyCharm: IDE
Git: Version control
GitHub: Repository hosting
```

---

## 📅 TIMELINE & MILESTONES

### **Project History**

#### **Phase 1: Foundation** (Completed)
```yaml
Q4 2024:
✅ Initial SuperTrend bot
✅ MT5 integration
✅ Basic risk management
✅ Configuration system
Status: Completed
```

#### **Phase 2: Enhancement** (Completed)
```yaml
Q1 2025:
✅ ICT bot implementation
✅ Backtesting engine
✅ Multi-symbol support
✅ Documentation expansion
Status: Completed
```

#### **Phase 3: Optimization** (Completed)
```yaml
Q2-Q3 2025:
✅ Crypto trading support
✅ Dual orders strategy
✅ Breakeven SL feature
✅ SMC library integration (then removed)
✅ Testing suite (85+ tests)
Status: Completed
```

---

### **Current Phase: Refinement** (In Progress)

#### **Q4 2025 Goals**:
```yaml
🔄 Code cleanup and refactoring
🔄 Documentation updates
🔄 Bug fixes and stability
🔄 Community engagement
🔄 Performance optimization
Target: October-December 2025
```

#### **Specific Objectives**:
- [ ] Achieve 90%+ test coverage
- [ ] Complete API documentation
- [ ] Create video tutorials
- [ ] Improve error handling
- [ ] Add more example strategies
- [x] Remove SMC dependency issues

---

### **Future Roadmap** (Proposed)

#### **Phase 4: Expansion** (2026 Q1-Q2)
```yaml
Proposed Features:
- [ ] Additional strategy templates
- [ ] Enhanced backtesting (walk-forward)
- [ ] Portfolio-level risk management
- [ ] Integration with data providers
- [ ] Telegram/Discord notifications
- [ ] Docker containerization

Status: Planning
Priority: Medium
```

#### **Phase 5: Maturity** (2026 Q3-Q4)
```yaml
Proposed Features:
- [ ] Advanced analytics dashboard
- [ ] Strategy optimization tools
- [ ] Machine learning enhancements
- [ ] Community strategy library
- [ ] Educational course integration

Status: Conceptual
Priority: Low
```

---

### **Version Milestones**

```yaml
v0.1.0 (Nov 2024): Initial release - SuperTrend bot
v0.5.0 (Jan 2025): ICT bot + Backtesting
v0.8.0 (Mar 2025): Crypto support + Dual orders
v1.0.0 (Oct 2025): Stable release ← CURRENT TARGET
v1.1.0 (Q1 2026): Community features
v2.0.0 (Q3 2026): Major expansion
```

---

## 🎓 EDUCATIONAL SCOPE

### **Learning Objectives** (What Users Should Learn)

#### **1. Algorithmic Trading Fundamentals**
```yaml
Topics:
- Technical indicators (SuperTrend, ATR)
- Signal generation logic
- Entry/exit strategies
- Position sizing
- Risk management

Resources:
- Inline code comments
- Documentation guides
- Example implementations
```

#### **2. Python for Trading**
```yaml
Topics:
- API integration (MT5)
- Data processing (pandas)
- Object-oriented design
- Testing practices
- Logging and monitoring

Resources:
- Clean code examples
- Type hints
- Docstrings
- Unit test examples
```

#### **3. Machine Learning in Trading**
```yaml
Topics:
- K-means clustering
- Feature engineering
- Model evaluation
- Overfitting prevention
- Parameter optimization

Resources:
- ML implementation in bot
- Backtesting validation
- Performance metrics
```

#### **4. ICT Concepts**
```yaml
Topics:
- Order Blocks
- Fair Value Gaps
- Liquidity concepts
- Market structure
- Smart Money analysis

Resources:
- ICT bot implementation
- Documentation guides
- Visual examples (future)
```

---

## 📊 PROJECT METRICS & KPIs

### **Development Metrics**

```yaml
Codebase:
- Total Lines of Code: ~15,000
- Python Files: ~50
- Test Files: ~10
- Documentation Files: ~20

Quality:
- Test Coverage: 80%+
- Documentation Coverage: 90%+
- Code Duplication: <5%
- Average Complexity: <8
```

### **Community Metrics** (Targets)

```yaml
GitHub:
- Stars: 100+ (milestone)
- Forks: 50+
- Contributors: 10+
- Issues Closed: >90%

Usage:
- PyPI Downloads: 1000+/month
- Active Users: 50+
- Countries: 20+
```

### **Performance Metrics** (Backtesting)

```yaml
Processing:
- Trades/Second: 100+
- Data Points/Second: 10,000+
- Memory Usage: <500MB
- CPU Usage: <50% (single core)

Reliability:
- Uptime: 99%+
- Error Rate: <1%
- Connection Success: >99%
```

---

## 🔐 COMPLIANCE & LEGAL SCOPE

### **Legal Disclaimers**

#### **1. Educational Purpose**
```
⚠️ This software is provided for EDUCATIONAL PURPOSES ONLY.

NOT:
❌ Investment advice
❌ Financial advisory service
❌ Guaranteed profit system
❌ Professional trading tool

IS:
✅ Learning resource
✅ Research platform
✅ Open-source project
✅ Community-driven tool
```

#### **2. Trading Risks**
```
⚠️ Trading Disclaimer:

- Forex/CFD trading involves substantial risk
- You can lose all your invested capital
- Past performance ≠ Future results
- No guarantees of profitability
- Use at your own risk
- Test on demo accounts first
```

#### **3. License & Usage**
```
MIT License:

✅ Can: Use, modify, distribute
✅ Can: Commercial use
✅ Must: Include license and copyright
❌ No warranty provided
❌ No liability accepted
```

#### **4. User Responsibilities**
```
Users are responsible for:

✅ Complying with local trading regulations
✅ Managing their own trading accounts
✅ Understanding risks involved
✅ Testing before live usage
✅ Monitoring their bots
✅ Tax compliance (where applicable)
```

---

## 🎯 SCOPE MANAGEMENT

### **Change Control Process**

#### **Adding Features**:
```yaml
1. Proposal: Create GitHub issue with detailed description
2. Discussion: Community feedback period (7+ days)
3. Evaluation: Maintainer reviews alignment with scope
4. Decision: Accept/Reject with reasoning
5. Implementation: If accepted, proceed with PR
6. Review: Code review and testing
7. Merge: Integration into main branch
8. Documentation: Update docs accordingly
```

#### **Removing Features**:
```yaml
1. Deprecation Notice: Announce intent (30+ days notice)
2. Migration Path: Provide alternatives
3. Community Input: Gather feedback
4. Final Decision: Maintainer approval
5. Removal: Execute in major version bump
6. Documentation: Update all references
```

#### **Scope Creep Prevention**:
```yaml
Red Flags:
❌ "Can we add a web dashboard?"
❌ "Why not support broker X's API?"
❌ "Let's build a social trading platform"
❌ "We should offer cloud hosting"

Response:
✅ Evaluate against core mission
✅ Consider maintenance burden
✅ Check alignment with educational goal
✅ Assess community benefit vs. complexity
```

---

## 📞 STAKEHOLDER COMMUNICATION

### **Key Stakeholders**

#### **1. Project Maintainer** (xPOURY4)
```yaml
Role: Primary developer, decision maker
Responsibilities:
- Code review and merging
- Architecture decisions
- Release management
- Community moderation
Contact: GitHub, Twitter (@TheRealPourya)
```

#### **2. Contributors**
```yaml
Role: Code contributors, testers
Responsibilities:
- Feature development
- Bug fixes
- Testing
- Documentation
Communication: GitHub Issues, PRs
```

#### **3. Users**
```yaml
Role: End users, feedback providers
Responsibilities:
- Testing in real conditions
- Reporting bugs
- Suggesting improvements
Communication: GitHub Issues, Discussions
```

#### **4. Community**
```yaml
Role: Learning community, supporters
Responsibilities:
- Knowledge sharing
- Support each other
- Promote project
Communication: GitHub Discussions, Social media
```

---

## 🏁 CONCLUSION

### **Project Identity**

```yaml
What is ML-SuperTrend-MT5?
  ✅ Educational trading bot
  ✅ Open-source Python project
  ✅ Algorithmic trading framework
  ✅ Learning resource

What is it NOT?
  ❌ Professional trading platform
  ❌ Get-rich-quick scheme
  ❌ Commercial product
  ❌ Financial service
```

### **Core Principles**

1. **Education First**: Learning > Profits
2. **Transparency**: Open source, no secrets
3. **Quality**: Clean code, good tests
4. **Community**: Collaboration over competition
5. **Responsibility**: Risk awareness always

### **Success Definition**

```
Success = {
    Technical: Stable, well-tested, maintainable code
    Educational: Users learn algo trading & Python
    Community: Active contributors and supporters
    Impact: Helps traders understand automation
    Sustainability: Long-term maintenance possible
}
```

---

## 📝 DOCUMENT METADATA

```yaml
Version: 1.0
Created: October 23, 2025
Author: xPOURY4
Status: Active
Review Cycle: Quarterly
Next Review: January 2026
```

### **Document Change History**

```yaml
v1.0 (Oct 23, 2025):
- Initial scope document creation
- Comprehensive project analysis
- Defined boundaries and goals
- Established success criteria
```

---

## 🔗 RELATED DOCUMENTS

- [README.md](../README.md) - Project overview
- [PROJECT_EVALUATION.md](PROJECT_EVALUATION.md) - Technical evaluation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [ROADMAP.md](ROADMAP.md) - Future plans (if exists)
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

**End of Document**

---

**Note**: This scope document is a living document. It should be reviewed and updated regularly to reflect the project's evolution while maintaining focus on core objectives.

**Contact**: [@TheRealPourya](https://twitter.com/TheRealPourya) | [GitHub Issues](https://github.com/xPOURY4/ML-SuperTrend-MT5/issues)
