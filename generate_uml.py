"""
Generate UML Diagrams from PlantUML code
=========================================
Converts PlantUML code to PNG images
"""

import re
from pathlib import Path

# Read the markdown file
md_file = Path("docs/UML_USECASE_DIAGRAM.md")
content = md_file.read_text(encoding='utf-8')

# Extract all PlantUML blocks
plantuml_blocks = re.findall(r'```plantuml\n(.*?)\n```', content, re.DOTALL)

print(f"Found {len(plantuml_blocks)} PlantUML diagrams")

# Create output directory
output_dir = Path("docs/uml_diagrams")
output_dir.mkdir(exist_ok=True)

# Extract diagram names and save to separate files
for i, block in enumerate(plantuml_blocks, 1):
    # Extract diagram name from @startuml
    name_match = re.search(r'@startuml\s+(\w+)', block)
    if name_match:
        diagram_name = name_match.group(1)
    else:
        diagram_name = f"diagram_{i}"
    
    # Save PlantUML code to .puml file
    puml_file = output_dir / f"{diagram_name}.puml"
    puml_file.write_text(block, encoding='utf-8')
    
    print(f"  [{i}] Saved: {puml_file.name}")

print(f"\n✅ All diagrams saved to: {output_dir}")
print(f"\nNext steps:")
print(f"1. Install PlantUML jar: Download from https://plantuml.com/download")
print(f"2. Or use online: https://www.plantuml.com/plantuml/uml/")
print(f"3. Or use VS Code extension: Already installed!")
print(f"\nTry opening any .puml file and press Alt+D")
