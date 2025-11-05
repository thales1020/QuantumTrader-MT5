# ML-SuperTrend-MT5 Documentation# ML-SuperTrend-MT5 Documentation



Welcome to the comprehensive documentation for ML-SuperTrend-MT5 algorithmic trading system.This folder contains all documentation for the ML-SuperTrend-MT5 project.



## 📚 Quick Navigation## 📚 Documentation Index



### 🚀 [01. Getting Started](./01-getting-started/)### Getting Started

New to the project? Start here!- [README.md](../README.md) - Main project overview

- Installation guide  - [QUICKSTART.md](QUICKSTART.md) - Quick start guide

- [Quick Start](./QUICKSTART.md)- [FAQ.md](FAQ.md) - Frequently asked questions

- Video tutorials

- Migration from older versions### Strategy Guides

- [ICT_README.md](ICT_README.md) - ICT Bot documentation

### 📖 [02. User Guides](./02-user-guides/)- [CRYPTO_TRADING_GUIDE.md](CRYPTO_TRADING_GUIDE.md) - Crypto trading guide (BTC, ETH)

Learn how to use the system effectively

- Crypto trading guide### Features & Implementation

- Customization options- [DUAL_ORDERS_IMPLEMENTATION.md](DUAL_ORDERS_IMPLEMENTATION.md) - Dual orders feature (RR 1:1 + Main RR)

- VPS deployment- [DUAL_ORDERS_CHANGES.md](DUAL_ORDERS_CHANGES.md) - Technical changelog for dual orders

- MT5 integration

### Performance & Optimization

### 💻 [03. Development](./03-development/)- [PERFORMANCE.md](PERFORMANCE.md) - Performance guidelines

Build and extend the system- [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md) - Optimization summary

- Project scope & architecture

- Technology stack### Development

- Plugin system- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

- Strategy templates- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

- Database integration

## 📖 Quick Links

### 🧪 [04. Testing](./04-testing/)

Quality assurance and testing documentation### Core Concepts

- Test plan & requirements- **Dual Orders**: Each signal opens 2 positions (RR 1:1 + Main RR) - [Details](DUAL_ORDERS_IMPLEMENTATION.md)

- API testing guide- **Crypto Trading**: Special handling for BTC, ETH, etc. - [Guide](CRYPTO_TRADING_GUIDE.md)

- Testing prompts for contributors

- Bug reports & fixes### Common Tasks

- **Run backtest**: `python run_backtest.py` (in parent directory)

### 🏗️ [05. Architecture](./05-architecture/)- **Run live bot**: `python run_bot.py` (in parent directory)

System design and technical architecture- **Run tests**: `python run_tests.py --all` (in parent directory)

- UML diagrams (Use Case & Process View)

- Paper trading system design### Configuration

- Backtest engine architecture  - Config file: `../config/config.json`

- Database schema- Risk settings: See [PERFORMANCE.md](PERFORMANCE.md)

- Crypto settings: See [CRYPTO_TRADING_GUIDE.md](CRYPTO_TRADING_GUIDE.md)

### ⚙️ [06. Technical Specifications](./06-technical-specs/)

Detailed technical documentation##  Search Tips

- Performance analysis

- Optimization detailsUse these keywords to find specific topics:

- Memory leak fixes- **"dual orders"** - RR 1:1 strategy

- Feature specifications- **"crypto"** - Bitcoin, Ethereum trading

- **"risk"** - Risk management

### 📜 [07. Project History](./07-project-history/)- **"backtest"** - Backtesting guides

Historical documentation and evolution- **"ICT"** - ICT trading concepts

- Development phases (Phase 1-4)- **"configuration"** - Setup and config

- Refactoring documentation

- Code quality improvements## 📞 Support

- Attribution & authorship

For questions or issues:

### 📋 [08. Project Management](./08-project-management/)1. Check [FAQ.md](FAQ.md)

Planning and evaluation docs2. Review [QUICKSTART.md](QUICKSTART.md)

- Project reviews3. See specific strategy guides above

- Post-launch checklists4. Open GitHub issue

- Evaluations

### 📚 [09. Reference](./09-reference/)
Bot-specific documentation
- ICT Bot guide
- Code examples

---

## 📄 Essential Documents

### Quick Access
- **[Quick Start Guide](./QUICKSTART.md)** - Get running in 5 minutes
- **[FAQ](./FAQ.md)** - Common questions & answers
- **[Changelog](./CHANGELOG.md)** - Version history
- **[Contributing](./CONTRIBUTING.md)** - How to contribute

---

## 🗂️ Documentation Structure

```
docs/
├── 01-getting-started/     # User onboarding
├── 02-user-guides/         # Feature guides
├── 03-development/         # Developer docs
├── 04-testing/            # QA & testing
├── 05-architecture/       # System design
├── 06-technical-specs/    # Technical details
├── 07-project-history/    # Archive
├── 08-project-management/ # Planning
├── 09-reference/          # Bot-specific
└── archive/               # Deprecated docs
```

---

## 🔍 How to Find Documentation

### By Role

**👤 I'm a trader/user:**
1. Start with [Quick Start](./QUICKSTART.md)
2. Read [User Guides](./02-user-guides/)
3. Check [FAQ](./FAQ.md) for common issues

**👨‍💻 I'm a developer:**
1. Read [Project Scope](./03-development/PROJECT_SCOPE.md)
2. Review [Architecture](./05-architecture/)
3. Study [Development Guides](./03-development/)

**🧪 I'm a tester:**
1. Start with [Testing Index](./04-testing/TESTING_INDEX.md)
2. Read [API Testing Guide](./04-testing/API_TESTING_GUIDE.md)
3. Use [Tester Prompts](./04-testing/TESTER_PROMPT.md)

**🏗️ I'm a system architect:**
1. Review [UML Diagrams](./05-architecture/uml/)
2. Study [Architecture Docs](./05-architecture/)
3. Check [Technical Specs](./06-technical-specs/)

### By Task

**📦 Deploying to VPS:**
- [VPS Deployment Guide](./02-user-guides/vps-deployment-guide.md)
- [MT5 VPS Setup](./02-user-guides/mt5-vps-deployment.md)

**🎯 Creating a strategy:**
- [Strategy Templates](./03-development/STRATEGY_TEMPLATES.md)
- [Plugin Quick Start](./03-development/PLUGIN_QUICK_START.md)

**🧪 Testing the system:**
- [Test Plan](./04-testing/TEST_PLAN.md)
- [API Quick Reference](./04-testing/API_QUICK_REFERENCE.md)

**📖 Understanding the codebase:**
- [UML Process View](./05-architecture/uml/UML_PROCESS_VIEW.md)
- [Architecture Overview](./05-architecture/)

---

## 📊 Documentation Stats

- **Total Categories:** 9 main sections + archive
- **Documentation Files:** 80+ markdown documents
- **UML Diagrams:** 14 diagrams (7 Use Case + 7 Process View)
- **Code Examples:** Available in [09-reference/examples/](./09-reference/examples/)
- **Test Coverage:** Documented in [04-testing/](./04-testing/)

---

## 🔄 Recent Updates

### Documentation Reorganization (Nov 2025)
- ✅ Reorganized 80+ files into 9 logical categories
- ✅ Created clear navigation structure
- ✅ Added README files for each section
- ✅ Improved discoverability

See [CHANGELOG.md](./CHANGELOG.md) for detailed version history.

---

**Last Updated:** November 5, 2025  
**Documentation Version:** 2.0 (Reorganized Structure)
