# 政大 AI Course Assignment Workflow

## Purpose
This workflow enables efficient local development of AI course assignments from 政大 (NCCU) by converting Google Colab notebooks to markdown format. This solves critical problems:
1. **Token efficiency**: Jupyter notebooks (.ipynb) consume excessive tokens when working with AI assistants due to their JSON structure and embedded outputs
2. **Local editing**: Markdown files work seamlessly with neovim and other text editors
3. **Local GPU execution**: Run assignments locally on Apple Silicon (M3 Pro) with Metal acceleration
4. **Version control**: Git integration with GitHub for tracking changes

## Directory Structure
```
colab_assignment/                    # Main repo: nccu-ai-course-assignments
├── script/
│   ├── convert.py                   # Main bidirectional converter
│   ├── notebook_to_md.py            # .ipynb → .md converter
│   └── md_to_notebook.py            # .md → .ipynb + .py converter (UPGRADED!)
├── HW 1/                            # Each HW gets its own folder/submodule
├── HW 2/                            # Submodule repo: nccu-ai-hw2
│   ├── pyproject.toml               # uv dependency management
│   ├── .venv/                       # Python 3.12 virtual environment
│   ├── *.ipynb                      # Colab notebooks
│   ├── *.md                         # Markdown for editing
│   └── *.py                         # Pure Python for local execution (NEW!)
├── HW 3/                            # Future assignments...
├── HW N/                            # Each can be its own git submodule
└── workflow-by-arthur.md            # This file
```

## GitHub Repository Structure
- **Main repo**: https://github.com/Yan-Yu-Lin/nccu-ai-course-assignments
- **HW submodules** (each assignment can be its own repo):
  - HW2: https://github.com/Yan-Yu-Lin/nccu-ai-hw2
  - HW3: https://github.com/Yan-Yu-Lin/nccu-ai-hw3 (future)
  - etc.

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

### Step 4: Convert Back to Notebook AND Python Script
```bash
# Convert edited markdown to BOTH notebook and Python script
uv run python script/convert.py "HW 2/assignment.md"

# Creates TWO files:
# - HW 2/assignment_from_md.ipynb  # For Colab
# - HW 2/assignment.py              # For local execution
```

**The converter automatically:**
- Filters out `!pip install` commands → `# COLAB ONLY: !pip install gradio`
- Comments magic commands → `# JUPYTER MAGIC: %matplotlib inline`
- Generates pure Python code ready for local execution

### Step 5A: Run Locally with GPU (Apple Silicon)
```bash
cd "HW 2"
# Dependencies managed by uv (requires Python 3.12 for tensorflow-metal)
uv sync
uv run python assignment.py
```

### Step 5B: Or Use GitHub + Colab Integration
1. Push to GitHub: `git push`
2. Open Colab → File → Open notebook → GitHub tab
3. Enter: `Yan-Yu-Lin/nccu-ai-hw2`
4. Select notebook and run with GPU
5. File → Save to GitHub creates a commit!

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
# Initialize assignment folder with uv
cd "HW 2"
uv init
uv python pin 3.12  # Required for tensorflow-metal
uv add tensorflow tensorflow-metal numpy matplotlib pillow gradio ipywidgets

# Convert notebook → markdown (for editing)
uv run python script/convert.py "HW 2/example-assignment-based-on-teacher.ipynb"

# Edit with neovim
nvim "HW 2/example-assignment-based-on-teacher.md"

# Convert markdown → notebook + Python script
uv run python script/convert.py "HW 2/example-assignment-based-on-teacher.md"
# Creates BOTH .ipynb and .py files!

# Run locally with GPU
uv run python "HW 2/example-assignment-based-on-teacher.py"

# Git operations
git add .
git commit -m "Update assignment"
git push  # Syncs to GitHub
```

## Important Notes

1. **Python Version**: Must use Python 3.12 for tensorflow-metal compatibility
2. **Converter now generates TWO outputs**: `.ipynb` for Colab AND `.py` for local execution
3. **Colab commands filtered**: `!pip` and `%magic` commands are automatically commented out in `.py`
4. **GitHub integration**: Saving in Colab creates commits in your GitHub repo
5. **Local GPU works**: M3 Pro Metal acceleration available with tensorflow-metal

## Dependencies Management with uv

```bash
# Key requirements for local GPU execution
Python 3.12 (not 3.13!)
tensorflow==2.16.2  # Compatible with tensorflow-metal
tensorflow-metal==1.2.0  # For Apple Silicon GPU
numpy<2.0  # Required by TensorFlow 2.16
```

## Benefits Summary

✅ **Token efficiency** - 96% reduction in file size for AI assistance
✅ **Dual output** - Generate both .ipynb and .py from single markdown source
✅ **Local GPU execution** - Run on M3 Pro with Metal acceleration
✅ **Version control** - GitHub repos for tracking changes
✅ **Colab integration** - Open from GitHub, save creates commits
✅ **Clean Python code** - Filtered for local execution without Colab dependencies
✅ **Neovim compatible** - Edit markdown efficiently in terminal

## Workflow Comparison

| Task | Old Way | New Way |
|------|---------|---------|
| Edit | Colab web editor | Neovim (local) |
| AI assistance | Upload huge .ipynb | Use tiny .md file |
| Run locally | Not possible | `uv run python script.py` with GPU |
| Version control | Manual download/upload | Git + GitHub |
| Submission | Share Colab link | Push to GitHub → Open in Colab |

---
*Enhanced workflow for 政大 AI course - Now with local GPU execution, GitHub integration, and dual notebook/Python output*
