# 📊 Hướng Dẫn Xem UML Diagrams

## Cách Xem Diagrams trong VS Code

### ✅ Đã cài đặt:
- PlantUML Extension (by jebbs)
- GraphViz

### 🎯 Các cách xem:

#### **Cách 1: Preview trực tiếp (Khuyến nghị)**

1. Mở bất kỳ file `.puml` nào trong `docs/uml_diagrams/`
2. Nhấn **`Alt+D`** để preview
3. Hoặc `Ctrl+Shift+P` → gõ "PlantUML: Preview"

#### **Cách 2: Export sang PNG/SVG**

1. Mở file `.puml`
2. `Ctrl+Shift+P` → gõ "PlantUML: Export Current Diagram"
3. Chọn format (PNG, SVG, PDF)

---

## 📁 Danh Sách Diagrams

### 🎯 USE CASE VIEW (7 diagrams)

#### 1. **System Overview**
- File: `QuantumTrader_Main_UseCase.puml`
- Mô tả: Tổng quan toàn hệ thống với 30 use cases
- Actors: Trader, Admin, MT5, Supabase
- Modules: 7 modules chính

#### 2. **Backtest Module**
- File: `Backtest_Module_Detail.puml`
- Mô tả: Chi tiết backtest workflows
- Use cases: Run backtest, Validate data, Generate report, Optimize parameters

#### 3. **Paper Trading Module**
- File: `PaperTrading_Module_Detail.puml`
- Mô tả: Virtual trading simulation
- Use cases: Start session, Execute virtual order, Close position, Monitor performance

#### 4. **Strategy Module**
- File: `Strategy_Module_Detail.puml` ← **Đang mở**
- Mô tả: Strategy development lifecycle
- Use cases: Create strategy, Test strategy, Deploy strategy

#### 5. **Monitoring Module**
- File: `Monitoring_Module_Detail.puml`
- Mô tả: Dashboard & health monitoring
- Use cases: View dashboard, Export reports, Check system health

#### 6. **Administration Module**
- File: `Administration_Module_Detail.puml`
- Mô tả: System configuration & management
- Use cases: Configure bot, Manage API keys, Update settings

---

### ⚡ PROCESS VIEW (7 diagrams)

#### 7. **Backtest Process - Activity**
- File: `Backtest_Process_Activity.puml`
- Type: Activity Diagram
- Swimlanes: 7 (Trader, System, MT5, Engine, Strategy, Broker, Analyzer)
- Highlights: Critical time index fix, Cost calculations, Parallel reporting

#### 8. **Backtest Process - Sequence**
- File: `Backtest_Process_Sequence.puml`
- Type: Sequence Diagram
- Participants: 8 components
- Real data: AUDUSD 830 trades, Win rate 41.2%, PF 0.84

#### 9. **Paper Trading Process - Activity**
- File: `PaperTrading_Process_Activity.puml`
- Type: Activity Diagram
- Swimlanes: 9 (including Supabase, Dashboard)
- Features: Real-time sync, 5 database tables, 1-second polling

#### 10. **Paper Trading Process - Sequence**
- File: `PaperTrading_Process_Sequence.puml`
- Type: Sequence Diagram
- Session lifecycle: Start → Trading loop → Stop
- Real example: 45 trades, 53.3% win rate, +$345.67 P&L

#### 11. **Strategy Development Process**
- File: `Strategy_Development_Process.puml`
- Type: Activity Diagram
- Phases: 6 phases (Development → Testing → Optimization → Validation → Paper → Production)
- Example: Parameter optimization with 80 combinations

#### 12. **Dashboard Monitoring Process**
- File: `Dashboard_Monitoring_Process.puml`
- Type: Activity Diagram
- Tabs: 5 tabs (Overview, Performance, Trades, Risk, Advanced)
- Features: Real-time updates, Supabase subscription, Health monitoring

#### 13. **Deployment Process**
- File: `Deployment_Process.puml`
- Type: Activity Diagram
- Steps: VPS setup, Configuration, Database, Monitoring, Maintenance
- Includes: Windows Service config, Health checks, Scaling strategies

---

## 🚀 Quick Start

### Xem tất cả diagrams nhanh:

```powershell
# Mở tất cả diagrams trong VS Code
cd C:\github\ML-SuperTrend-MT5\docs\uml_diagrams

# List tất cả files
ls *.puml
```

### Diagrams nên xem đầu tiên:

1. **`QuantumTrader_Main_UseCase.puml`** - Hiểu tổng quan hệ thống
2. **`Backtest_Process_Activity.puml`** - Workflow backtest chi tiết
3. **`PaperTrading_Process_Activity.puml`** - Workflow paper trading
4. **`Strategy_Development_Process.puml`** - Quy trình phát triển strategy

---

## 📖 Documentation

- **Use Case View**: `docs/UML_USECASE_DIAGRAM.md`
- **Process View**: `docs/UML_PROCESS_VIEW.md`
- **Summary**: `docs/UML_DOCUMENTATION_SUMMARY.md`

---

## 💡 Tips

### Preview không hiện?
1. Kiểm tra GraphViz đã cài: `dot -V` trong terminal
2. Restart VS Code
3. Thử export sang PNG thay vì preview

### Diagram quá lớn?
1. Zoom in/out trong preview window
2. Export sang SVG (scalable)
3. Mở từng module riêng lẻ

### Muốn edit diagram?
1. Edit file `.puml`
2. Preview sẽ auto-refresh
3. Syntax reference: https://plantuml.com/

---

## 📊 Statistics

- **Total Diagrams**: 14
- **Use Case Diagrams**: 7
- **Process Diagrams**: 7
  - Activity: 5
  - Sequence: 2
- **Total Use Cases**: 30
- **Total Actors**: 4
- **Lines of PlantUML**: ~2,000+

---

## 🎨 Export All Diagrams

Nếu muốn export tất cả diagrams sang PNG:

```powershell
# Trong VS Code, mở Command Palette (Ctrl+Shift+P)
# Gõ: "PlantUML: Export Workspace Diagrams"
```

Hoặc export từng file:
1. Mở file `.puml`
2. `Ctrl+Shift+P`
3. "PlantUML: Export Current Diagram"
4. Chọn PNG/SVG/PDF

---

**Bắt đầu xem diagrams ngay!** 🚀

Mở file đầu tiên: `QuantumTrader_Main_UseCase.puml` và nhấn `Alt+D`
