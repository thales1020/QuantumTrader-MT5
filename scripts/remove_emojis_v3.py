"""
Ultra-Safe Emoji Remover v3.0
Simply replaces emoji characters with empty string
Preserves ALL whitespace, indentation, and structure
"""

import os
from pathlib import Path

# List of specific emojis to remove
EMOJIS_TO_REMOVE = [
    '', '', '', '', '', '', '', '', '', '', 
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', '',
    '', '', '', '', '', '', '', '', '', ''
]

def remove_emojis_ultra_safe(content):
    """
    Remove emojis by simple character replacement.
    Does NOT touch any whitespace.
    """
    for emoji in EMOJIS_TO_REMOVE:
        content = content.replace(emoji, '')
    return content

def process_file(filepath):
    """Process a single file"""
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        # Remove emojis
        cleaned = remove_emojis_ultra_safe(original)
        
        # Write back if changed
        if cleaned != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            return True
        return False
        
    except Exception as e:
        print(f"Error {filepath}: {e}")
        return False

def main():
    """Main function"""
    root = Path(__file__).parent.parent
    print("=" * 70)
    print("Ultra-Safe Emoji Remover v3.0")
    print("=" * 70)
    print(f"Root: {root}\n")
    
    # Skip these directories
    skip = {'.git', '__pycache__', 'venv', 'env', 'node_modules', 
            '.vscode', 'ml_supertrend_mt5.egg-info'}
    
    md_count, py_count = 0, 0
    md_mod, py_mod = 0, 0
    
    # Process all files
    for root_dir, dirs, files in os.walk(root):
        # Remove skip dirs from dirs list
        dirs[:] = [d for d in dirs if d not in skip]
        
        for file in files:
            path = os.path.join(root_dir, file)
            
            if file.endswith('.md'):
                md_count += 1
                if process_file(path):
                    md_mod += 1
                    print(f" {path}")
            
            elif file.endswith('.py'):
                py_count += 1
                if process_file(path):
                    py_mod += 1
                    print(f" {path}")
    
    print("\n" + "=" * 70)
    print(f"Markdown: {md_mod}/{md_count} modified")
    print(f"Python:   {py_mod}/{py_count} modified")
    print(f"Total:    {md_mod + py_mod}/{md_count + py_count} modified")
    print("=" * 70)

if __name__ == '__main__':
    main()
