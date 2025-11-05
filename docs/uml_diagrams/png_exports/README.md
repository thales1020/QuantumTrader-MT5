# PNG Exports Directory

This directory contains PNG exports of all UML diagrams.

## How to Generate PNG Files

### Method 1: VS Code Command (Easiest)

1. Press `Ctrl+Shift+P`
2. Type: **PlantUML: Export Workspace Diagrams**
3. Select format: **png**
4. The diagrams will be exported automatically

### Method 2: Export Individual Diagrams

For each `.puml` file in the parent directory:

1. Open the file in VS Code
2. Press `Ctrl+Shift+P`
3. Type: **PlantUML: Export Current Diagram**
4. Select format: **png**
5. Choose this directory as output location

### Method 3: Export Current Diagram with Shortcut

1. Open any `.puml` file
2. Right-click in the editor
3. Select **Export Current Diagram**
4. Choose **PNG** format

## Expected PNG Files (13 total)

### Use Case View (6 files)
- ✓ Administration_Module_Detail.png
- ✓ Backtest_Module_Detail.png
- ✓ Monitoring_Module_Detail.png
- ✓ PaperTrading_Module_Detail.png
- ✓ QuantumTrader_Main_UseCase.png
- ✓ Strategy_Module_Detail.png

### Process View (7 files)
- ✓ Backtest_Process_Activity.png
- ✓ Backtest_Process_Sequence.png
- ✓ Dashboard_Monitoring_Process.png
- ✓ Deployment_Process.png
- ✓ PaperTrading_Process_Activity.png
- ✓ PaperTrading_Process_Sequence.png
- ✓ Strategy_Development_Process.png

## Viewing PNG Files

Once exported, you can:
- View in any image viewer
- Insert into documentation
- Share with team members
- Include in presentations
- Upload to wiki/documentation sites

## Alternative Export Formats

You can also export to:
- **SVG** - Scalable vector graphics (best for web)
- **PDF** - For printing
- **EPS** - For publications
- **LaTeX** - For academic papers

## Troubleshooting

### Diagrams not rendering?
1. Ensure GraphViz is installed: `dot -V`
2. Restart VS Code
3. Check PlantUML extension is enabled

### Export command not found?
1. Install PlantUML extension: `jebbs.plantuml`
2. Reload VS Code window

### Large diagrams cut off?
1. Use SVG format instead (scalable)
2. Or increase image DPI in PlantUML settings

---

**Last Updated**: 2024-11-05  
**Total Diagrams**: 13  
**Status**: Ready for export
