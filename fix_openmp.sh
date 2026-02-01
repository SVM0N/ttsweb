#!/bin/bash
# Quick fix for OpenMP error in existing environment

echo "Fixing OpenMP issue in tts environment..."
conda activate tts
conda env config vars set KMP_DUPLICATE_LIB_OK=TRUE -n tts
echo ""
echo "✅ Fix applied!"
echo ""
echo "⚠️  IMPORTANT: You MUST restart your terminal or run:"
echo "   conda deactivate"
echo "   conda activate tts"
echo ""
echo "Then run: python3 tts_cli.py"
