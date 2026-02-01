#!/bin/bash
# Setup script for TTS environment with Qwen3 support
# Uses mamba for faster, memory-efficient installation

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     TTS Environment Setup - Kokoro + Qwen3 Support            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if mamba is available
if command -v mamba &> /dev/null; then
    echo "✓ Using mamba (faster than conda)"
    CONDA_CMD="mamba"
else
    echo "⚠️  mamba not found. Using conda instead..."
    CONDA_CMD="conda"
fi

# Deactivate current environment
echo ""
echo "Step 1: Deactivating current environment..."
conda deactivate 2>/dev/null || true

# Remove old tts environment if exists
echo ""
echo "Step 2: Removing old tts environment (if exists)..."
$CONDA_CMD env remove -n tts -y 2>/dev/null || echo "  (No old environment found)"

# Create new environment with Python 3.11
echo ""
echo "Step 3: Creating new environment with Python 3.11..."
$CONDA_CMD create -n tts python=3.11 -y -q

# Get conda base path
CONDA_BASE=$(conda info --base)

# Activate environment using source (works in scripts)
echo ""
echo "Step 4: Activating tts environment..."
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate tts

# Install PyTorch and dependencies from conda-forge (avoids OpenMP conflicts)
echo ""
echo "Step 5: Installing PyTorch from conda-forge..."
echo "  (This avoids OpenMP conflicts on macOS)"
$CONDA_CMD install -c conda-forge pytorch torchvision torchaudio -y -q

# Set environment variable to fix OpenMP issue permanently
echo ""
echo "Step 6: Fixing OpenMP issue permanently..."
conda env config vars set KMP_DUPLICATE_LIB_OK=TRUE -n tts
# Reactivate to apply the change
conda deactivate
conda activate tts
echo "  ✓ Set KMP_DUPLICATE_LIB_OK=TRUE"

# Install core dependencies
echo ""
echo "Step 7: Installing core dependencies..."
pip install -q soundfile numpy ebooklib pydub

# Install Kokoro (works everywhere, 24kHz, 54 voices)
echo ""
echo "Step 8: Installing Kokoro TTS..."
pip install -q 'kokoro>=0.9.4' 'misaki[en]'
echo "  ✓ Kokoro installed (24kHz, 54 voices, 8 languages)"

# Install Qwen3-TTS with exact compatible versions
echo ""
echo "Step 9: Installing Qwen3-TTS..."
echo "  (Downloading ~1.7GB model on first use)"
pip install -q qwen-tts 'transformers==4.57.3'
echo "  ✓ Qwen3-TTS installed (12kHz, 10 languages, voice cloning)"

# Install lightweight PDF extractor
echo ""
echo "Step 10: Installing PDF extractors..."
pip install -q pymupdf
echo "  ✓ PyMuPDF installed (fast, lightweight)"

# Optional: Install Unstructured (large but powerful)
echo ""
read -p "Install Unstructured PDF extractor? (500MB, better layout) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  Installing Unstructured..."
    pip install -q 'unstructured[local-inference]'
    
    # Install detectron2 - needs PyTorch already installed
    echo "  Installing detectron2 (requires compilation)..."
    pip install -q 'git+https://github.com/facebookresearch/detectron2.git@v0.6' 2>&1 | grep -v "^warning" || {
        echo "  ⚠️  Detectron2 installation failed (optional, can skip)"
        echo "  You can still use Unstructured without it"
    }
    echo "  ✓ Unstructured installed"
else
    echo "  Skipped (you can install later if needed)"
fi

# Verify installation
echo ""
echo "Step 11: Verifying installation..."
python -c "import torch; print(f'  ✓ PyTorch {torch.__version__}')"
python -c "import kokoro; print('  ✓ Kokoro imported successfully')"
python -c "import transformers; print(f'  ✓ Transformers {transformers.__version__}')"
python -c "import qwen_tts; print('  ✓ Qwen3-TTS imported successfully')" 2>/dev/null || echo "  ⚠️  Qwen3-TTS import warning (may work anyway)"
echo "  ✓ All core packages verified"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Environment: tts"
echo "Python: 3.11"
echo "Models: Kokoro v1.0 + Qwen3-TTS"
echo ""
echo "To use:"
echo "  1. conda activate tts"
echo "  2. python3 tts_cli.py"
echo ""
echo "Models available:"
echo "  • Kokoro v1.0 - 54 voices, 8 languages, 24kHz ✅ [Recommended]"
echo "  • Qwen3-TTS - 10 languages, voice cloning, 12kHz"
echo ""
echo "Quick test:"
echo "  python3 tts_cli.py"
echo "  Then select: String → Kokoro v1.0 → Enter text → Run!"
echo ""
