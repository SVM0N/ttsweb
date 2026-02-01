# TTS CLI - Command Line Interface

Interactive command-line tool for converting PDFs, EPUBs, and text to natural speech using state-of-the-art TTS models.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/SVM0N/ttsweb.git
cd ttsweb

# Run the CLI
python3 tts_cli.py
```

No pre-installation required! The CLI will automatically install dependencies as needed based on your selections.

## Features

### Interactive Menu System
- **Easy navigation**: Number-based menu system with clear options
- **Configuration validation**: Checks all settings before conversion
- **Progress tracking**: Real-time feedback during conversion
- **Error handling**: Helpful error messages and recovery

### Supported Conversions
1. **PDF to Audio**: Convert PDF documents to speech with synchronized text highlighting
2. **EPUB to Audio**: Convert EPUB books to per-chapter audio files (ZIP)
3. **Text to Audio**: Convert plain text to speech

### TTS Models (7 options)
1. **Kokoro v1.0** - 54 voices, 8 languages (Recommended)
2. **Kokoro v0.9** - 10 voices, English, stable
3. **Qwen3-TTS Custom Voice** - 10 languages, pre-configured speakers
4. **Qwen3-TTS Voice Design** - Natural language voice descriptions
5. **Qwen3-TTS Base** - 3-second voice cloning
6. **Maya1** - 20+ emotions, requires GPU
7. **Silero v5** - Russian language

### PDF Extractors (4 options)
1. **Unstructured** - Advanced layout analysis (Recommended)
2. **PyMuPDF** - Fast extraction for clean PDFs
3. **Apple Vision** - OCR for scanned PDFs (macOS only)
4. **Nougat** - Academic papers with equations

### Output Formats
- **MP3** - Compressed, smaller file size
- **WAV** - Uncompressed, higher quality

### Advanced Settings
- **Voice selection**: Choose specific voices/speakers
- **Speech speed**: Adjust speed (0.5-2.0x)
- **Device selection**: Auto, CUDA, CPU, or MPS
- **Page selection**: Process specific PDF pages
- **Output directory**: Customize save location

## Usage Guide

### Main Menu

```
MAIN MENU
----------------------------------------------------------------------
1. Configure conversion settings
2. Select input file/text
3. Run conversion
4. View current configuration
5. Advanced settings (voice, speed, device)
0. Exit
```

### Basic Workflow

1. **Start the CLI**
   ```bash
   python3 tts_cli.py
   ```

2. **Configure Settings** (Option 1)
   - Choose conversion type (PDF/EPUB/Text)
   - Select TTS model
   - Select PDF extractor (if converting PDF)
   - Choose output format (MP3/WAV)
   - Set output directory

3. **Select Input** (Option 2)
   - For PDF: Enter path to PDF file
   - For EPUB: Enter path to EPUB file
   - For Text: Type or paste text

4. **Run Conversion** (Option 3)
   - CLI will install dependencies if needed
   - Initialize TTS system
   - Process your input
   - Save audio and manifest files

5. **Upload to Web Player**
   - Visit https://svm0n.github.io/ttsweb/
   - Upload generated audio and manifest files
   - Enjoy synchronized reading experience

### Example Session

```
$ python3 tts_cli.py

======================================================================
  TTS CLI - Text-to-Speech Converter
  Convert PDFs, EPUBs, and Text to Natural Speech
======================================================================

Welcome! This tool converts PDFs, EPUBs, and text to speech.
Start by configuring your conversion settings (Option 1).

----------------------------------------------------------------------
MAIN MENU
----------------------------------------------------------------------
1. Configure conversion settings
2. Select input file/text
3. Run conversion
4. View current configuration
5. Advanced settings (voice, speed, device)
0. Exit
----------------------------------------------------------------------

Enter choice: 1

----------------------------------------------------------------------
CONFIGURATION MENU
----------------------------------------------------------------------
1. Set conversion type (PDF, EPUB, Text)
2. Select TTS model
3. Select PDF extractor (for PDF conversion)
4. Set output format (MP3, WAV)
5. Set output directory
0. Back to main menu
----------------------------------------------------------------------

Enter choice: 1

--------------------------------------------------
SELECT CONVERSION TYPE
--------------------------------------------------
1. PDF to audio
2. EPUB to audio (per-chapter ZIP)
3. Text string to audio
0. Cancel

Enter choice [1-3]: 1
✓ Conversion type set to: PDF

Enter choice: 2

--------------------------------------------------
SELECT TTS MODEL
--------------------------------------------------
1. Kokoro v1.0 (54 voices, 8 languages) [Recommended]
2. Kokoro v0.9 (10 voices, English, stable)
3. Qwen3-TTS Custom Voice (10 languages, pre-configured)
4. Qwen3-TTS Voice Design (natural language descriptions)
5. Qwen3-TTS Base (3-second voice cloning)
6. Maya1 (20+ emotions, requires GPU)
7. Silero v5 (Russian language)
0. Cancel

Enter choice [1-7]: 3
✓ TTS model set to: Qwen3-TTS Custom Voice

[... continue configuring ...]

Enter choice: 0  # Back to main menu

Enter choice: 2  # Select input file

----------------------------------------------------------------------
INPUT SELECTION
----------------------------------------------------------------------
Enter path to PDF file:
> files/my_document.pdf
✓ PDF file selected: files/my_document.pdf

Enter page numbers (e.g., '1,3,5-7') or press Enter for all pages:
✓ All pages will be processed

Enter choice: 3  # Run conversion

======================================================================
RUNNING CONVERSION
======================================================================

📦 Installing dependencies...
[... installation progress ...]

🚀 Initializing TTS system...
[... initialization ...]

🎤 Starting conversion...
[... conversion progress ...]

======================================================================
✓ CONVERSION COMPLETED SUCCESSFULLY
======================================================================
Audio file:    files/my_document_tts_qwen3_custom_voice.mp3
Manifest file: files/my_document_tts_qwen3_custom_voice_manifest.json

💡 You can now upload these files to the web player at:
   https://svm0n.github.io/ttsweb/

Press Enter to continue...

Enter choice: 0  # Exit

👋 Thank you for using TTS CLI!
Visit https://svm0n.github.io/ttsweb/ to use the web player.
```

## Configuration Options

### Conversion Types

**PDF to Audio**
- Extracts text with layout analysis
- Preserves document structure
- Creates timeline manifest for synchronized highlighting
- Supports page selection

**EPUB to Audio**
- Processes book chapter-by-chapter
- Creates separate audio file per chapter
- Packages everything in a ZIP file
- Preserves chapter titles

**Text to Audio**
- Quick conversion for plain text
- No file upload needed
- Direct text input via terminal
- Perfect for testing voices

### TTS Model Comparison

| Model | Languages | Voices | Special Features | Requirements |
|-------|-----------|--------|------------------|--------------|
| Kokoro v1.0 | 8 | 54 | Multi-language, stable | CPU/GPU |
| Kokoro v0.9 | 1 (English) | 10 | Very stable | CPU/GPU |
| Qwen3 Custom | 10 | 5+ | Pre-configured speakers | GPU recommended |
| Qwen3 Design | 10 | Unlimited | Natural language descriptions | GPU recommended |
| Qwen3 Base | 10 | Cloning | 3-second voice cloning | GPU recommended |
| Maya1 | 1 (English) | Unlimited | 20+ emotions, expressive | GPU required (16GB) |
| Silero v5 | 1 (Russian) | 6 | Russian language | CPU/GPU |

### PDF Extractor Comparison

| Extractor | Speed | Best For | Limitations |
|-----------|-------|----------|-------------|
| Unstructured | Medium | General PDFs, complex layouts | Requires ~500MB dependencies |
| PyMuPDF | Fast | Clean PDFs with text layers | Fails on scanned PDFs |
| Apple Vision | Medium | Scanned PDFs, images | macOS only |
| Nougat | Slow | Academic papers, equations | Requires GPU, ~1.5GB model |

## Advanced Features

### Page Selection

When converting PDFs, you can specify which pages to process:

```
Enter page numbers (e.g., '1,3,5-7') or press Enter for all pages: 1,3,5-7
✓ Pages selected: [1, 3, 5, 6, 7]
```

Syntax:
- Single pages: `1,3,5`
- Ranges: `1-10`
- Combined: `1,3,5-7,10-15`

### Voice Selection

Available voices depend on the TTS model:

**Kokoro Models:**
- `af_heart`, `af_bella`, `af_sarah` (female)
- `am_adam`, `am_michael` (male)
- Many more in v1.0

**Qwen3 Custom Voice:**
- `Vivian`, `Alice`, `Bob`, `Charlie`, `Diana`

**Qwen3 Voice Design:**
- Natural language descriptions
- Example: "A young female voice, cheerful and energetic"

**Maya1:**
- Natural language descriptions with emotions
- Example: "40-year-old male, warm, conversational"

**Silero v5:**
- `xenia`, `eugene`, `baya`, `kseniya`, `aleksandr`, `irina`

### Speech Speed

Adjust speech speed (Kokoro and Qwen3 only):
- **0.5x** - Half speed (clearer for learning)
- **1.0x** - Normal speed (default)
- **1.5x** - 50% faster
- **2.0x** - Double speed (faster playback)

### Device Selection

**Auto** (Recommended)
- Automatically selects best available device
- Priority: CUDA > MPS > CPU

**CUDA**
- NVIDIA GPU acceleration
- Best for Maya1 and Qwen3
- Requires CUDA-compatible GPU

**MPS**
- Apple Silicon acceleration
- Works on M1/M2/M3/M4 Macs
- Good performance for most models

**CPU**
- Works on any system
- Slower but reliable
- No GPU required

## Tips & Best Practices

### For Best Results

1. **Choose the right model**
   - English PDFs: Kokoro v1.0 or Qwen3
   - Multilingual: Qwen3 Custom Voice
   - Russian: Silero v5
   - Expressive speech: Maya1 (GPU required)

2. **Select appropriate PDF extractor**
   - Clean PDFs: PyMuPDF (fastest)
   - Complex layouts: Unstructured (best quality)
   - Scanned PDFs: Apple Vision or Nougat

3. **Optimize for your hardware**
   - GPU available: Use Qwen3 or Maya1
   - CPU only: Use Kokoro or Silero
   - Limited RAM: Use PyMuPDF extractor

4. **Test with small inputs first**
   - Try a few pages before processing entire document
   - Test different voices to find your preference
   - Verify output quality before batch processing

### Troubleshooting

**"PDF file not found"**
- Check file path is correct
- Use absolute paths or ensure you're in the right directory
- Verify file exists: `ls -la files/`

**"Configuration Error: No PDF extractor selected"**
- Go to Configuration Menu (Option 1)
- Select PDF extractor (Option 3)

**"Module not found" errors**
- CLI will auto-install dependencies
- If fails, manually install: `pip install <package>`
- Check internet connection for downloads

**Slow performance**
- Try smaller page ranges for testing
- Use PyMuPDF extractor for speed
- Consider GPU if available
- Reduce speech speed setting

**Out of memory**
- Process fewer pages at once
- Use lightweight models (Kokoro, PyMuPDF)
- Close other applications
- Consider smaller model variants

## Integration with Web Player

After conversion, upload your files to the web player:

1. Visit: https://svm0n.github.io/ttsweb/
2. Click "Upload Files"
3. Upload:
   - Your original PDF
   - Generated audio file (.mp3 or .wav)
   - Generated manifest file (_manifest.json)
4. Enjoy synchronized reading with audio!

The web player features:
- PDF rendering with synchronized highlighting
- Audio playback controls (play/pause, seek, speed)
- Click on text to jump to that audio position
- Dark mode support
- Mobile-friendly responsive design

## Development

### Project Structure

```
ttsweb/
├── tts_cli.py              # Main CLI script
├── tts_lib/                # Core library modules
│   ├── tts_backends.py     # TTS model implementations
│   ├── pdf_extractors.py   # PDF extraction strategies
│   ├── synthesis.py        # Audio synthesis pipeline
│   ├── setup.py            # Dependency installer
│   ├── config.py           # Configuration management
│   └── ...
├── TTS.ipynb               # Jupyter notebook interface
├── files/                  # Default output directory
└── README.md               # Main documentation
```

### Adding New Features

The CLI is modular and easy to extend:

1. **Add new TTS model**: Update `tts_lib/tts_backends.py`
2. **Add new PDF extractor**: Update `tts_lib/pdf_extractors.py`
3. **Add new menu option**: Modify `tts_cli.py` menu functions

## Requirements

### System Requirements
- Python 3.10+
- 8GB RAM minimum (16GB recommended)
- 5-10GB free disk space for models
- ffmpeg (for MP3 conversion)

### Python Packages
Automatically installed as needed:
- torch (PyTorch)
- soundfile, numpy
- Selected TTS model packages
- Selected PDF extractor packages

### Optional
- CUDA for GPU acceleration
- Apple Silicon for MPS acceleration
- Flash Attention 2 for Qwen3 speedup

## License

This project is licensed for non-commercial use only.
For commercial licensing, please contact SVM0N on GitHub.

## Credits

- Built on top of the ttsweb project
- Uses Kokoro TTS, Qwen3-TTS, Maya1, and Silero models
- PDF extraction via Unstructured, PyMuPDF, Vision, and Nougat

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/SVM0N/ttsweb
- Report bugs in the Issues section
- Contribute via Pull Requests

---

**Made with ❤️ for accessible reading**
