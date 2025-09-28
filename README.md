# Colab Assignment Workflow 🚀

## Complete Bidirectional Workflow

### Tools Created:
1. **`convert.py`** - Auto-detects and converts between formats
2. **`notebook_to_md.py`** - Notebook → Markdown converter
3. **`md_to_notebook.py`** - Markdown → Notebook converter

## Quick Start

### One Command Conversion:
```bash
# Convert notebook to markdown (for Claude/editing)
uv run python convert.py assignment.ipynb
# Creates: assignment.md

# Convert markdown back to notebook (for Colab)
uv run python convert.py assignment.md
# Creates: assignment_from_md.ipynb
```

## Complete Workflow

### 1️⃣ Download from Colab/Gist
```bash
# If you have a gist
git clone https://gist.github.com/YOUR_GIST_ID.git

# Or download from Colab
# File → Download → Download .ipynb
```

### 2️⃣ Convert to Markdown for Local Editing
```bash
uv run python convert.py assignment.ipynb
# Creates assignment.md (96% smaller!)
```

### 3️⃣ Edit with Claude Code
- Open `assignment.md` in your editor
- Make changes with Claude's help
- Much more efficient (uses less context)

### 4️⃣ Convert Back to Notebook
```bash
uv run python convert.py assignment.md
# Creates assignment_from_md.ipynb
```

### 5️⃣ Upload to Colab
1. Open [Google Colab](https://colab.research.google.com)
2. File → Upload notebook
3. Select `assignment_from_md.ipynb`
4. Test with GPU
5. Share link with teacher

## Why This Works

### Benefits:
- ✅ **96% smaller files** when in Markdown
- ✅ **Preserves all code** and markdown cells
- ✅ **No outputs** = cleaner version control
- ✅ **Claude-friendly** = uses much less context
- ✅ **Round-trip safe** = convert back and forth

### The Problem It Solves:
- Gists don't sync with Colab (one-way export)
- Notebooks are huge (embedded images, outputs)
- Claude gets overwhelmed with notebook JSON
- You want to develop locally but test on Colab GPU

## Advanced Usage

### Custom Output Names:
```bash
# Specify output file
uv run python convert.py input.ipynb output.md
uv run python convert.py input.md output.ipynb
```

### Direct Script Usage:
```bash
# If you need specific converter
uv run python notebook_to_md.py assignment.ipynb
uv run python md_to_notebook.py assignment.md
```

## Tips

1. **Keep markdown version in git** (smaller, cleaner diffs)
2. **Only convert to notebook when ready to test**
3. **Use Colab for GPU, local for development**
4. **Share Colab link, not gist, for submissions**

## File Structure
```
colab_assignment/
├── assignment.ipynb         # Original notebook
├── assignment.md            # Markdown version (edit this)
├── assignment_from_md.ipynb # Converted back (upload to Colab)
├── convert.py               # Main converter
├── notebook_to_md.py        # Notebook → MD
├── md_to_notebook.py        # MD → Notebook
└── README.md               # This file
```

## Example Full Cycle
```bash
# 1. Start with notebook from teacher
uv run python convert.py teacher_demo.ipynb
# Creates: teacher_demo.md

# 2. Edit and improve
code teacher_demo.md  # or use vim, nano, etc.

# 3. Convert back
uv run python convert.py teacher_demo.md
# Creates: teacher_demo_from_md.ipynb

# 4. Upload to Colab and test
# 5. Share Colab link with teacher
```

## Requirements
- Python 3.6+
- uv (or regular python)
- No external dependencies! 🎉

---
*This workflow lets you develop locally, use Claude efficiently, and still submit via Colab!*