# 📸 HƯỚNG DẪN EXPORT UML DIAGRAMS SANG PNG

## ✅ Đã Cài Đặt
- ✓ PlantUML Extension (jebbs.plantuml)
- ✓ GraphViz
- ✓ 13 UML Diagrams ready

## 🎯 CÁCH EXPORT NHANH NHẤT

### **Cách 1: Export Tất Cả (Workspace)**

1. Nhấn `Ctrl+Shift+P` (mở Command Palette)
2. Gõ: `PlantUML: Export Workspace Diagrams`
3. Chọn nó và nhấn Enter
4. Chọn format: **png**
5. Chọn output directory (hoặc để mặc định)

**Kết quả**: Tất cả 13 diagrams sẽ được export cùng lúc!

---

### **Cách 2: Export Từng File (Current Diagram)**

1. Mở file `.puml` bất kỳ trong `docs/uml_diagrams/`
2. Nhấn `Ctrl+Shift+P`
3. Gõ: `PlantUML: Export Current Diagram`
4. Nhấn Enter
5. Chọn format: **png**
6. Chọn nơi lưu (khuyến nghị: `docs/uml_diagrams/png_exports/`)

**Lặp lại cho 13 files**

---

### **Cách 3: Right-Click Menu**

1. Mở file `.puml`
2. **Right-click** trong editor
3. Chọn **Export Current Diagram**
4. Chọn format và location

---

### **Cách 4: Preview → Export**

1. Mở file `.puml`
2. Nhấn `Alt+D` để preview
3. Trong preview window, click nút **Export** (icon camera/save)
4. Chọn format PNG

---

## 📋 DANH SÁCH 13 DIAGRAMS CẦN EXPORT

### Use Case View (6 diagrams):

1. ✓ `QuantumTrader_Main_UseCase.puml` → **Main_UseCase.png**
2. ✓ `Administration_Module_Detail.puml` → **Admin_Module.png**
3. ✓ `Backtest_Module_Detail.puml` → **Backtest_Module.png**
4. ✓ `Monitoring_Module_Detail.puml` → **Monitoring_Module.png**
5. ✓ `PaperTrading_Module_Detail.puml` → **PaperTrading_Module.png**
6. ✓ `Strategy_Module_Detail.puml` → **Strategy_Module.png**

### Process View (7 diagrams):

7. ✓ `Backtest_Process_Activity.puml` → **Backtest_Activity.png**
8. ✓ `Backtest_Process_Sequence.puml` → **Backtest_Sequence.png**
9. ✓ `Dashboard_Monitoring_Process.puml` → **Dashboard_Process.png**
10. ✓ `Deployment_Process.puml` → **Deployment_Process.png**
11. ✓ `PaperTrading_Process_Activity.puml` → **PaperTrading_Activity.png**
12. ✓ `PaperTrading_Process_Sequence.puml` → **PaperTrading_Sequence.png**
13. ✓ `Strategy_Development_Process.puml` → **Strategy_Development.png**

---

## 💡 TIPS & TRICKS

### Để Export Nhanh Tất Cả:

```
1. Ctrl+Shift+P
2. Gõ: "export workspace"
3. Chọn "PlantUML: Export Workspace Diagrams"
4. Format: png
5. Xong!
```

### Nếu Không Thấy Command:

1. Kiểm tra extension: `code --list-extensions | findstr plantuml`
2. Reload window: `Ctrl+Shift+P` → `Reload Window`
3. Thử lại

### Nếu Preview Trống:

1. Kiểm tra GraphViz: `dot -V` trong terminal
2. Restart VS Code
3. Thử export trực tiếp (không cần preview)

---

## 📁 RECOMMENDED OUTPUT STRUCTURE

```
docs/
└── uml_diagrams/
    ├── *.puml (source files)
    └── png_exports/
        ├── README.md
        ├── use_case_view/
        │   ├── Main_UseCase.png
        │   ├── Admin_Module.png
        │   ├── Backtest_Module.png
        │   ├── Monitoring_Module.png
        │   ├── PaperTrading_Module.png
        │   └── Strategy_Module.png
        └── process_view/
            ├── Backtest_Activity.png
            ├── Backtest_Sequence.png
            ├── Dashboard_Process.png
            ├── Deployment_Process.png
            ├── PaperTrading_Activity.png
            ├── PaperTrading_Sequence.png
            └── Strategy_Development.png
```

---

## 🚀 EXPORT NGAY BÂY GIỜ!

### Quick Start (3 bước):

**Bước 1**: Nhấn `Ctrl+Shift+P`

**Bước 2**: Gõ `export workspace` và chọn PlantUML command

**Bước 3**: Chọn `png` → Done!

---

## 🔧 ALTERNATIVE: Export bằng Command Line

Nếu có PlantUML JAR file:

```bash
# Download PlantUML JAR
# From: https://plantuml.com/download

# Export all diagrams
java -jar plantuml.jar -tpng "C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\*.puml" -o png_exports

# Export with high DPI
java -jar plantuml.jar -tpng -Sdpi=300 "*.puml" -o png_exports
```

---

## ✅ VERIFICATION

Sau khi export, kiểm tra:

```powershell
# Liệt kê tất cả PNG files
Get-ChildItem C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\png_exports -Filter *.png

# Đếm số lượng
(Get-ChildItem C:\github\ML-SuperTrend-MT5\docs\uml_diagrams\png_exports -Filter *.png).Count
# Should be: 13
```

---

## 📖 SỬ DỤNG PNG FILES

Sau khi export xong, bạn có thể:

- ✓ Insert vào README.md
- ✓ Thêm vào documentation
- ✓ Share với team
- ✓ Include trong presentations
- ✓ Upload lên Wiki
- ✓ Print để review

---

## 🎨 OTHER EXPORT FORMATS

Ngoài PNG, bạn cũng có thể export sang:

- **SVG** - Scalable, best cho web
- **PDF** - Cho printing
- **EPS** - Cho publications
- **LaTeX** - Cho academic papers

---

**Bắt đầu export ngay!** 🚀

Nhấn `Ctrl+Shift+P` → `PlantUML: Export Workspace Diagrams` → `png`
