# Colab Assignment Workflow

## Setup Complete! 🎉

### What We've Created:
1. **`notebook_to_md.py`** - Converts Jupyter notebooks to clean Markdown
   - Removes outputs and base64 images
   - Creates proper code blocks with syntax highlighting
   - Reduces file size by ~96%

### Your Workflow:

#### 1. Local Development
```bash
# Edit your notebook locally with Jupyter or VSCode
jupyter notebook assignment.ipynb
# or
code assignment.ipynb
```

#### 2. Convert to Markdown for Review
```bash
# Convert notebook to markdown (reduces context usage in Claude)
uv run python notebook_to_md.py assignment.ipynb

# This creates assignment.md which is much easier to work with
```

#### 3. Upload to Colab for Testing
1. Open [Google Colab](https://colab.research.google.com)
2. File → Upload notebook → Select your `assignment.ipynb`
3. Run and test with GPU acceleration

#### 4. Generate Share Link for Teacher
1. In Colab: File → Share → Get shareable link
2. Or save to Drive: File → Save a copy in Drive
3. Share the link from Google Drive

### Alternative: GitHub Repo Approach (Better than Gist)
```bash
# Create a proper GitHub repo instead of Gist
git init
git add assignment.ipynb README.md
git commit -m "Initial assignment"
git remote add origin https://github.com/YOUR_USERNAME/colab-assignment.git
git push -u origin main
```

Then in Colab:
- File → Open notebook → GitHub tab
- Enter your repo URL
- This creates a better connection than Gist

### Tips:
- Keep a clean version locally (no outputs)
- Use the Markdown version for code reviews with Claude
- Test GPU-specific code in Colab
- Save final version with outputs to Colab/Drive for submission

### Quick Commands:
```bash
# Clean convert for Claude
uv run python notebook_to_md.py assignment.ipynb

# View markdown
cat assignment.md

# Open in Jupyter
jupyter notebook assignment.ipynb
```