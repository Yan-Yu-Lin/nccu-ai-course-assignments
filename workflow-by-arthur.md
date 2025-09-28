# 政大 AI Course Assignment Workflow

## Purpose
This workflow enables efficient local development of AI course assignments from 政大 (NCCU) by converting Google Colab notebooks to markdown format. This solves two critical problems:
1. **Token efficiency**: Jupyter notebooks (.ipynb) consume excessive tokens when working with AI assistants due to their JSON structure and embedded outputs
2. **Local editing**: Markdown files work seamlessly with neovim and other text editors

## Directory Structure
```
colab_assignment/
├── script/
│   ├── convert.py           # Main bidirectional converter
│   ├── notebook_to_md.py    # .ipynb → .md converter
│   └── md_to_notebook.py    # .md → .ipynb converter
├── HW 2/                    # Assignment folder
│   ├── *.ipynb             # Original Colab notebooks from teacher
│   └── *.md                # Converted markdown for local work
└── workflow-by-arthur.md    # This file
```

## Core Workflow

### Step 1: Download Assignment from Colab
1. Teacher shares Colab notebook link
2. Open in Google Colab
3. File → Download → Download .ipynb
4. Save to `HW 2/` folder (or appropriate assignment folder)

### Step 2: Convert to Markdown for Local Work
```bash
# Convert notebook to markdown (96% size reduction!)
uv run python script/convert.py "HW 2/assignment.ipynb"

# Creates: HW 2/assignment.md
```

### Step 3: Work Locally with AI Assistance
- Open the `.md` file in neovim
- Work with Claude Code or other AI assistants efficiently
- The markdown format uses **significantly fewer tokens** than notebook JSON
- Code blocks are clean and properly formatted

### Step 4: Convert Back to Notebook (When Ready to Test)
```bash
# Convert edited markdown back to notebook
uv run python script/convert.py "HW 2/assignment.md"

# Creates: HW 2/assignment_from_md.ipynb
```

### Step 5: Upload to Colab for GPU Testing
1. Open [Google Colab](https://colab.research.google.com)
2. File → Upload notebook
3. Select the converted `.ipynb` file
4. Run with GPU acceleration
5. Submit via Colab sharing link

## Why This Workflow Works

### Token Efficiency
- **Notebook (.ipynb)**: Contains JSON structure, outputs, base64 images, metadata
- **Markdown (.md)**: Clean text with code blocks only
- **Result**: ~96% reduction in file size and token usage

### Example Assignment (HW 2)
The current assignment involves building a 3-layer neural network for MNIST digit classification:
- Set neuron counts (N1, N2, N3) for each layer
- Uses TensorFlow/Keras
- Includes Gradio interface for testing
- Requires GPU for efficient training (hence Colab for final testing)

## Quick Commands Reference

```bash
# Check what assignments you have
ls "HW 2/"

# Convert notebook → markdown (for editing)
uv run python script/convert.py "HW 2/example-assignment-based-on-teacher.ipynb"

# Convert markdown → notebook (for Colab upload)
uv run python script/convert.py "HW 2/example-assignment-based-on-teacher.md"

# View markdown in terminal (quick check)
cat "HW 2/example-assignment-based-on-teacher.md"

# Edit with neovim
nvim "HW 2/example-assignment-based-on-teacher.md"
```

## Important Notes

1. **Always keep the original notebook** from the teacher as backup
2. **Work primarily in markdown** for efficiency
3. **Only convert to notebook** when ready to test on Colab GPU
4. **Submit via Colab link**, not the local files
5. **No git/gist needed** - direct download from Colab is the source

## Benefits Summary

✅ **Efficient AI assistance** - Uses far fewer tokens
✅ **Better editor support** - Works perfectly with neovim
✅ **Clean code view** - No JSON clutter or embedded outputs
✅ **Local development** - Work offline, test online
✅ **Preserves structure** - Maintains all cells and content

---
*Workflow created for 政大 AI course assignments - optimized for local development with AI assistance*
