#!/usr/bin/env python3
"""
Convert Jupyter notebook to clean Markdown format
Removes outputs, converts cells to proper markdown with code blocks
"""
import json
import sys
import re
from pathlib import Path


def clean_markdown_source(source):
    """Convert notebook markdown source to clean markdown text"""
    if isinstance(source, list):
        text = ''.join(source)
    else:
        text = source

    # Remove base64 encoded images
    text = re.sub(r'!\[.*?\]\(data:image/.*?;base64,.*?\)', '[Image omitted]', text)

    # Remove Colab badges
    text = re.sub(r'<a href="https://colab\.research\.google\.com/.*?</a>', '', text)

    return text.strip()


def clean_code_source(source):
    """Convert notebook code source to clean code text"""
    if isinstance(source, list):
        return ''.join(source).strip()
    return source.strip()


def notebook_to_markdown(input_file, output_file=None):
    """Convert Jupyter notebook to clean Markdown format"""

    input_path = Path(input_file)
    if output_file is None:
        output_file = input_path.with_suffix('.md')

    with open(input_file, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    markdown_lines = []

    # Add title from filename
    markdown_lines.append(f"# {input_path.stem}\n")

    # Add metadata if present
    if 'metadata' in notebook:
        if 'colab' in notebook['metadata']:
            markdown_lines.append("*This notebook was created for Google Colab*\n")
        if 'language_info' in notebook['metadata']:
            lang = notebook['metadata']['language_info'].get('name', 'unknown')
            markdown_lines.append(f"*Language: {lang}*\n")

    markdown_lines.append("---\n")

    # Process cells
    for i, cell in enumerate(notebook['cells'], 1):
        cell_type = cell['cell_type']

        if cell_type == 'markdown':
            content = clean_markdown_source(cell.get('source', ''))
            if content:
                markdown_lines.append(f"\n{content}\n")

        elif cell_type == 'code':
            source = clean_code_source(cell.get('source', ''))
            if source:
                # Add cell number as comment
                markdown_lines.append(f"\n## Code Cell {i}\n")

                # Determine language for syntax highlighting
                lang = 'python'  # default
                if 'metadata' in notebook and 'language_info' in notebook['metadata']:
                    lang = notebook['metadata']['language_info'].get('name', 'python')

                # Add code block
                markdown_lines.append(f"```{lang}")
                markdown_lines.append(source)
                markdown_lines.append("```\n")

                # Add outputs if they're text (not images or complex objects)
                if cell.get('outputs'):
                    has_text_output = False
                    for output in cell['outputs']:
                        if 'text' in output:
                            if not has_text_output:
                                markdown_lines.append("**Output:**")
                                markdown_lines.append("```")
                                has_text_output = True
                            markdown_lines.append(''.join(output['text']))
                        elif 'data' in output and 'text/plain' in output['data']:
                            if not has_text_output:
                                markdown_lines.append("**Output:**")
                                markdown_lines.append("```")
                                has_text_output = True
                            markdown_lines.append(''.join(output['data']['text/plain']))

                    if has_text_output:
                        markdown_lines.append("```\n")

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_lines))

    # Print statistics
    original_size = input_path.stat().st_size / 1024  # KB
    output_size = Path(output_file).stat().st_size / 1024  # KB

    print(f"✅ Conversion complete!")
    print(f"📄 Input: {input_file} ({original_size:.1f} KB)")
    print(f"📝 Output: {output_file} ({output_size:.1f} KB)")
    print(f"📉 Size reduction: {((original_size - output_size) / original_size * 100):.1f}%")

    # Count cells
    code_cells = sum(1 for c in notebook['cells'] if c['cell_type'] == 'code')
    md_cells = sum(1 for c in notebook['cells'] if c['cell_type'] == 'markdown')
    print(f"📊 Converted {code_cells} code cells and {md_cells} markdown cells")

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: python notebook_to_md.py <notebook.ipynb> [output.md]")
        print("\nThis script converts a Jupyter notebook to clean Markdown format.")
        print("- Removes cell outputs and embedded images")
        print("- Formats code cells with proper syntax highlighting")
        print("- Creates readable markdown suitable for documentation")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        notebook_to_markdown(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: '{input_file}' is not a valid Jupyter notebook")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()