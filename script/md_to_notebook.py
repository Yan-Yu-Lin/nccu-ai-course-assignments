#!/usr/bin/env python3
"""
Convert Markdown file back to Jupyter notebook format AND Python script
Parses markdown and recreates notebook structure with code and markdown cells
Also generates a clean Python script for local execution
"""
import json
import sys
import re
from pathlib import Path


def extract_python_code(markdown_content):
    """Extract only Python code from markdown, filtering out Colab-specific commands"""
    python_lines = []
    lines = markdown_content.split('\n')
    i = 0
    in_code_block = False

    while i < len(lines):
        line = lines[i]

        # Check for code block start
        if line.startswith('```python'):
            in_code_block = True
            i += 1
            continue
        elif line.startswith('```') and in_code_block:
            in_code_block = False
            python_lines.append('\n')  # Add blank line between code blocks
            i += 1
            continue

        # Process code content
        if in_code_block:
            # Skip Colab-specific commands
            if line.strip().startswith('!'):  # Skip shell commands like !pip install
                python_lines.append(f"# COLAB ONLY: {line}\n")
            elif line.strip().startswith('%'):  # Skip magic commands like %matplotlib
                python_lines.append(f"# JUPYTER MAGIC: {line}\n")
            else:
                python_lines.append(line + '\n')

        i += 1

    return ''.join(python_lines)


def parse_markdown_to_cells(markdown_content):
    """Parse markdown content and convert to notebook cells"""
    cells = []
    lines = markdown_content.split('\n')
    i = 0

    current_cell = None
    in_code_block = False
    code_language = None

    while i < len(lines):
        line = lines[i]

        # Check for code block start
        if line.startswith('```'):
            if not in_code_block:
                # Starting a code block
                # Save previous cell if exists
                if current_cell and current_cell['source']:
                    cells.append(current_cell)

                # Extract language if specified
                code_language = line[3:].strip() or 'python'
                in_code_block = True
                current_cell = {
                    'cell_type': 'code',
                    'metadata': {},
                    'source': [],
                    'outputs': [],
                    'execution_count': None
                }
            else:
                # Ending a code block
                in_code_block = False
                if current_cell:
                    # Join source lines
                    current_cell['source'] = ''.join(current_cell['source'])
                    cells.append(current_cell)
                    current_cell = None
                code_language = None

            i += 1
            continue

        # Process content based on context
        if in_code_block:
            # Add to code cell
            if current_cell:
                current_cell['source'].append(line + '\n')
        else:
            # Check if this is a "Code Cell" header (from our converter)
            if line.startswith('## Code Cell'):
                # Skip this line as it's just metadata from conversion
                i += 1
                continue

            # Check if this line starts output section
            if line == '**Output:**':
                # Skip output sections (we don't restore outputs)
                i += 1
                # Skip until we find the end of output block
                while i < len(lines) and not (lines[i].startswith('```') or lines[i].startswith('#')):
                    i += 1
                continue

            # Regular markdown content
            if current_cell is None or current_cell['cell_type'] != 'markdown':
                # Save previous cell if exists
                if current_cell and current_cell['source']:
                    cells.append(current_cell)

                current_cell = {
                    'cell_type': 'markdown',
                    'metadata': {},
                    'source': []
                }

            # Add line to markdown cell
            if current_cell:
                # Skip metadata lines from our converter
                if not (line.startswith('*This notebook was created') or
                       line.startswith('*Language:') or
                       (line == '---' and i < 10)):  # Skip early separator
                    current_cell['source'].append(line + '\n')

        i += 1

    # Don't forget the last cell
    if current_cell and current_cell['source']:
        cells.append(current_cell)

    # Clean up cells
    cleaned_cells = []
    for cell in cells:
        # Join source lines and strip extra whitespace
        if isinstance(cell['source'], list):
            cell['source'] = ''.join(cell['source']).strip()

        # Only keep non-empty cells
        if cell['source']:
            # Split source back into lines for notebook format
            cell['source'] = cell['source'].split('\n')
            # Add newline to all lines except the last
            for j in range(len(cell['source']) - 1):
                cell['source'][j] += '\n'

            cleaned_cells.append(cell)

    return cleaned_cells


def markdown_to_notebook(input_file, output_file=None):
    """Convert Markdown file to Jupyter notebook format AND Python script"""

    input_path = Path(input_file)
    if output_file is None:
        output_file = input_path.stem + '_from_md.ipynb'

    # Also determine Python output file name
    python_output_file = input_path.with_suffix('.py')

    # Read markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Parse markdown to cells for notebook
    cells = parse_markdown_to_cells(markdown_content)

    # Extract Python code for .py file
    python_code = extract_python_code(markdown_content)

    # Create notebook structure
    notebook = {
        'cells': cells,
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'codemirror_mode': {
                    'name': 'ipython',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.9.0'
            },
            'colab': {
                'provenance': [],
                'private_outputs': True
            }
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }

    # Write notebook
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)

    # Write Python script
    with open(python_output_file, 'w', encoding='utf-8') as f:
        f.write(f"#!/usr/bin/env python3\n")
        f.write(f'"""\n')
        f.write(f'Python script generated from: {input_file}\n')
        f.write(f'Generated on: {Path(input_file).stat().st_mtime}\n')
        f.write(f'Note: Colab-specific commands (!pip, %magic) have been commented out\n')
        f.write(f'"""\n\n')
        f.write(python_code)

    # Print statistics
    input_size = input_path.stat().st_size / 1024  # KB
    notebook_size = Path(output_file).stat().st_size / 1024  # KB
    python_size = Path(python_output_file).stat().st_size / 1024  # KB

    print(f"✅ Conversion complete!")
    print(f"📝 Input: {input_file} ({input_size:.1f} KB)")
    print(f"📓 Notebook: {output_file} ({notebook_size:.1f} KB)")
    print(f"🐍 Python: {python_output_file} ({python_size:.1f} KB)")

    # Count cells
    code_cells = sum(1 for c in cells if c['cell_type'] == 'code')
    md_cells = sum(1 for c in cells if c['cell_type'] == 'markdown')
    print(f"📊 Created {code_cells} code cells and {md_cells} markdown cells")
    print(f"🚀 Notebook ready for Colab, Python script ready for local execution!")

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_notebook.py <markdown.md> [output.ipynb]")
        print("\nThis script converts a Markdown file back to Jupyter notebook format.")
        print("- Recreates code and markdown cells")
        print("- Preserves cell structure")
        print("- Creates notebook ready for Colab")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        markdown_to_notebook(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()