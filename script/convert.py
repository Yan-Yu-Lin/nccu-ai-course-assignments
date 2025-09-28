#!/usr/bin/env python3
"""
Bidirectional converter between Jupyter notebooks and Markdown
Automatically detects file type and converts accordingly
"""
import sys
from pathlib import Path
from notebook_to_md import notebook_to_markdown
from md_to_notebook import markdown_to_notebook


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert.py <file.ipynb|file.md> [output_file]")
        print("\n🔄 Bidirectional Converter:")
        print("  • .ipynb → .md : For editing with Claude Code")
        print("  • .md → .ipynb : For running in Colab")
        print("\nExamples:")
        print("  python convert.py notebook.ipynb    # Creates notebook.md")
        print("  python convert.py notebook.md       # Creates notebook_from_md.ipynb")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)

    # Detect file type and convert
    if input_file.suffix == '.ipynb':
        print(f"📓 Converting notebook to markdown...")
        notebook_to_markdown(str(input_file), output_file)
    elif input_file.suffix == '.md':
        print(f"📝 Converting markdown to notebook...")
        markdown_to_notebook(str(input_file), output_file)
    else:
        print(f"❌ Error: Unsupported file type '{input_file.suffix}'")
        print("   Supported: .ipynb, .md")
        sys.exit(1)


if __name__ == "__main__":
    main()