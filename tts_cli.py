#!/usr/bin/env python3
"""
TTS CLI - Text-to-Speech Command Line Interface

Interactive CLI tool for converting text, PDFs, and EPUBs to speech.
Supports multiple TTS models, PDF extractors, and output formats.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple


class TTSConfig:
    """Configuration for TTS CLI session."""

    def __init__(self):
        self.conversion_type = "pdf"
        self.tts_model = "kokoro_1.0"
        self.pdf_extractor = "unstructured"
        self.output_format = "mp3"
        self.device = "auto"
        self.output_dir = "files"
        self.pdf_path = None
        self.pdf_pages = None
        self.epub_path = None
        self.text_input = None
        self.voice = None
        self.speed = 1.0


def print_banner():
    """Print CLI banner."""
    print("\n" + "="*70)
    print("  TTS CLI - Text-to-Speech Converter")
    print("  Convert PDFs, EPUBs, and Text to Natural Speech")
    print("="*70 + "\n")


def print_menu():
    """Print main menu."""
    print("\n" + "-"*70)
    print("MAIN MENU")
    print("-"*70)
    print("1. Configure conversion settings")
    print("2. Select input file/text")
    print("3. Run conversion")
    print("4. View current configuration")
    print("5. Advanced settings (voice, speed, device)")
    print("0. Exit")
    print("-"*70)


def print_config_menu():
    """Print configuration menu."""
    print("\n" + "-"*70)
    print("CONFIGURATION MENU")
    print("-"*70)
    print("1. Set conversion type (PDF, EPUB, Text)")
    print("2. Select TTS model")
    print("3. Select PDF extractor (for PDF conversion)")
    print("4. Set output format (MP3, WAV)")
    print("5. Set output directory")
    print("0. Back to main menu")
    print("-"*70)


def select_conversion_type(config: TTSConfig):
    """Select conversion type."""
    print("\n" + "-"*50)
    print("SELECT CONVERSION TYPE")
    print("-"*50)
    print("1. PDF to audio")
    print("2. EPUB to audio (per-chapter ZIP)")
    print("3. Text string to audio")
    print("0. Cancel")

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        config.conversion_type = "pdf"
        print("✓ Conversion type set to: PDF")
    elif choice == "2":
        config.conversion_type = "epub"
        print("✓ Conversion type set to: EPUB")
    elif choice == "3":
        config.conversion_type = "string"
        print("✓ Conversion type set to: Text String")
    elif choice == "0":
        print("Cancelled")
    else:
        print("⚠️  Invalid choice")


def select_tts_model(config: TTSConfig):
    """Select TTS model."""
    print("\n" + "-"*50)
    print("SELECT TTS MODEL")
    print("-"*50)
    print("1. Kokoro v1.0 (54 voices, 8 languages) [Recommended]")
    print("2. Kokoro v0.9 (10 voices, English, stable)")
    print("3. Qwen3-TTS Custom Voice (10 languages, pre-configured)")
    print("4. Qwen3-TTS Voice Design (natural language descriptions)")
    print("5. Qwen3-TTS Base (3-second voice cloning)")
    print("6. Maya1 (20+ emotions, requires GPU)")
    print("7. Silero v5 (Russian language)")
    print("0. Cancel")

    choice = input("\nEnter choice [1-7]: ").strip()

    models = {
        "1": ("kokoro_1.0", "Kokoro v1.0"),
        "2": ("kokoro_0.9", "Kokoro v0.9"),
        "3": ("qwen3_custom_voice", "Qwen3-TTS Custom Voice"),
        "4": ("qwen3_voice_design", "Qwen3-TTS Voice Design"),
        "5": ("qwen3_base", "Qwen3-TTS Base"),
        "6": ("maya1", "Maya1"),
        "7": ("silero_v5", "Silero v5"),
    }

    if choice in models:
        config.tts_model = models[choice][0]
        print(f"✓ TTS model set to: {models[choice][1]}")
    elif choice == "0":
        print("Cancelled")
    else:
        print("⚠️  Invalid choice")


def select_pdf_extractor(config: TTSConfig):
    """Select PDF extractor."""
    print("\n" + "-"*50)
    print("SELECT PDF EXTRACTOR")
    print("-"*50)
    print("1. Unstructured (advanced layout analysis) [Recommended]")
    print("2. PyMuPDF (fast, for clean PDFs)")
    print("3. Apple Vision (OCR for scanned PDFs, macOS only)")
    print("4. Nougat (academic papers with equations)")
    print("0. Cancel")

    choice = input("\nEnter choice [1-4]: ").strip()

    extractors = {
        "1": ("unstructured", "Unstructured"),
        "2": ("pymupdf", "PyMuPDF"),
        "3": ("vision", "Apple Vision"),
        "4": ("nougat", "Nougat"),
    }

    if choice in extractors:
        config.pdf_extractor = extractors[choice][0]
        print(f"✓ PDF extractor set to: {extractors[choice][1]}")
    elif choice == "0":
        print("Cancelled")
    else:
        print("⚠️  Invalid choice")


def select_output_format(config: TTSConfig):
    """Select output format."""
    print("\n" + "-"*50)
    print("SELECT OUTPUT FORMAT")
    print("-"*50)
    print("1. MP3 (compressed, smaller file size)")
    print("2. WAV (uncompressed, higher quality)")
    print("0. Cancel")

    choice = input("\nEnter choice [1-2]: ").strip()

    if choice == "1":
        config.output_format = "mp3"
        print("✓ Output format set to: MP3")
    elif choice == "2":
        config.output_format = "wav"
        print("✓ Output format set to: WAV")
    elif choice == "0":
        print("Cancelled")
    else:
        print("⚠️  Invalid choice")


def set_output_directory(config: TTSConfig):
    """Set output directory."""
    print(f"\nCurrent output directory: {config.output_dir}")
    new_dir = input("Enter new output directory (or press Enter to keep current): ").strip()

    if new_dir:
        config.output_dir = new_dir
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"✓ Output directory set to: {config.output_dir}")


def select_input_file(config: TTSConfig):
    """Select input file or text."""
    print("\n" + "-"*70)
    print("INPUT SELECTION")
    print("-"*70)

    if config.conversion_type == "pdf":
        print("Enter path to PDF file:")
        pdf_path = input("> ").strip()
        if pdf_path and os.path.exists(pdf_path):
            config.pdf_path = pdf_path
            print(f"✓ PDF file selected: {pdf_path}")

            # Ask about page selection
            pages_input = input("\nEnter page numbers (e.g., '1,3,5-7') or press Enter for all pages: ").strip()
            if pages_input:
                config.pdf_pages = parse_page_numbers(pages_input)
                print(f"✓ Pages selected: {config.pdf_pages}")
            else:
                config.pdf_pages = None
                print("✓ All pages will be processed")
        else:
            print("⚠️  File not found or invalid path")

    elif config.conversion_type == "epub":
        print("Enter path to EPUB file:")
        epub_path = input("> ").strip()
        if epub_path and os.path.exists(epub_path):
            config.epub_path = epub_path
            print(f"✓ EPUB file selected: {epub_path}")
        else:
            print("⚠️  File not found or invalid path")

    elif config.conversion_type == "string":
        print("Enter text to convert to speech:")
        print("(Type your text and press Enter when done)")
        text = input("> ").strip()
        if text:
            config.text_input = text
            print(f"✓ Text input set ({len(text)} characters)")
        else:
            print("⚠️  No text entered")


def parse_page_numbers(pages_str: str) -> list:
    """Parse page numbers from string like '1,3,5-7' to [1,3,5,6,7]."""
    pages = []
    parts = pages_str.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            pages.append(int(part))

    return sorted(set(pages))


def configure_advanced_settings(config: TTSConfig):
    """Configure advanced settings."""
    print("\n" + "-"*70)
    print("ADVANCED SETTINGS")
    print("-"*70)
    print("1. Set voice/speaker")
    print("2. Set speech speed (Kokoro/Qwen3 only)")
    print("3. Set device (auto, cuda, cpu, mps)")
    print("0. Back to main menu")
    print("-"*70)

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        print(f"\nCurrent voice: {config.voice or 'Default'}")
        voice = input("Enter voice name (or press Enter for default): ").strip()
        if voice:
            config.voice = voice
            print(f"✓ Voice set to: {voice}")

    elif choice == "2":
        print(f"\nCurrent speed: {config.speed}")
        speed_str = input("Enter speed (0.5-2.0, default 1.0): ").strip()
        if speed_str:
            try:
                config.speed = float(speed_str)
                print(f"✓ Speed set to: {config.speed}")
            except ValueError:
                print("⚠️  Invalid speed value")

    elif choice == "3":
        print("\n1. Auto (recommended)")
        print("2. CUDA (GPU)")
        print("3. CPU")
        print("4. MPS (Apple Silicon)")
        device_choice = input("\nEnter choice [1-4]: ").strip()

        devices = {"1": "auto", "2": "cuda", "3": "cpu", "4": "mps"}
        if device_choice in devices:
            config.device = devices[device_choice]
            print(f"✓ Device set to: {config.device}")


def view_configuration(config: TTSConfig):
    """Display current configuration."""
    print("\n" + "="*70)
    print("CURRENT CONFIGURATION")
    print("="*70)
    print(f"Conversion Type:  {config.conversion_type.upper()}")
    print(f"TTS Model:        {config.tts_model}")
    print(f"PDF Extractor:    {config.pdf_extractor}")
    print(f"Output Format:    {config.output_format.upper()}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Device:           {config.device}")
    print(f"Voice:            {config.voice or 'Default'}")
    print(f"Speed:            {config.speed}")

    if config.conversion_type == "pdf":
        print(f"PDF Path:         {config.pdf_path or 'Not set'}")
        print(f"Pages:            {config.pdf_pages or 'All pages'}")
    elif config.conversion_type == "epub":
        print(f"EPUB Path:        {config.epub_path or 'Not set'}")
    elif config.conversion_type == "string":
        text_preview = config.text_input[:50] + "..." if config.text_input and len(config.text_input) > 50 else config.text_input
        print(f"Text:             {text_preview or 'Not set'}")

    print("="*70)


def validate_configuration(config: TTSConfig) -> Tuple[bool, str]:
    """Validate configuration before running conversion."""
    if config.conversion_type == "pdf":
        if not config.pdf_path:
            return False, "No PDF file selected"
        if not os.path.exists(config.pdf_path):
            return False, f"PDF file not found: {config.pdf_path}"
        if not config.pdf_extractor:
            return False, "No PDF extractor selected"

    elif config.conversion_type == "epub":
        if not config.epub_path:
            return False, "No EPUB file selected"
        if not os.path.exists(config.epub_path):
            return False, f"EPUB file not found: {config.epub_path}"

    elif config.conversion_type == "string":
        if not config.text_input:
            return False, "No text input provided"

    return True, "Configuration valid"


def run_conversion(config: TTSConfig):
    """Run the TTS conversion."""
    # Validate configuration
    valid, message = validate_configuration(config)
    if not valid:
        print(f"\n⚠️  Configuration Error: {message}")
        print("Please configure all required settings before running conversion.")
        input("\nPress Enter to continue...")
        return

    print("\n" + "="*70)
    print("RUNNING CONVERSION")
    print("="*70)

    try:
        # Import required modules
        from tts_lib.config import TTSConfig as TTSConfigLib
        from tts_lib.init_system import initialize_system
        from tts_lib.examples import run_conversion
        from tts_lib.setup import install_dependencies

        # Install dependencies
        print("\n📦 Installing dependencies...")
        install_dependencies(
            tts_model=config.tts_model,
            pdf_extractor=config.pdf_extractor,
            conversion_type=config.conversion_type,
            out_format=config.output_format
        )

        # Initialize system
        print("\n🚀 Initializing TTS system...")
        tts, config_lib, pdf_extractor = initialize_system(
            tts_model=config.tts_model,
            output_dir=config.output_dir,
            device=config.device,
            pdf_extractor_name=config.pdf_extractor if config.conversion_type == "pdf" else None,
            conversion_type=config.conversion_type
        )

        # Run conversion
        print("\n🎤 Starting conversion...")
        result = run_conversion(
            conversion_type=config.conversion_type,
            tts=tts,
            config=config_lib,
            pdf_extractor=pdf_extractor,
            tts_model=config.tts_model,
            out_format=config.output_format,
            pdf_path=config.pdf_path or "files/doc.pdf",
            pdf_pages=config.pdf_pages,
            epub_path=config.epub_path or "book.epub",
            zip_name=""
        )

        print("\n" + "="*70)
        print("✓ CONVERSION COMPLETED SUCCESSFULLY")
        print("="*70)

        if config.conversion_type in ["pdf", "string"]:
            audio_path, manifest_path = result
            print(f"Audio file:    {audio_path}")
            print(f"Manifest file: {manifest_path}")
        else:  # epub
            print(f"ZIP archive: {result}")

        print("\n💡 You can now upload these files to the web player at:")
        print("   https://svm0n.github.io/ttsweb/")

    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion cancelled by user")
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to continue...")


def configuration_menu(config: TTSConfig):
    """Handle configuration menu."""
    while True:
        print_config_menu()
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            select_conversion_type(config)
        elif choice == "2":
            select_tts_model(config)
        elif choice == "3":
            select_pdf_extractor(config)
        elif choice == "4":
            select_output_format(config)
        elif choice == "5":
            set_output_directory(config)
        elif choice == "0":
            break
        else:
            print("⚠️  Invalid choice. Please try again.")


def main():
    """Main CLI loop."""
    config = TTSConfig()

    print_banner()
    print("Welcome! This tool converts PDFs, EPUBs, and text to speech.")
    print("Start by configuring your conversion settings (Option 1).")

    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            configuration_menu(config)
        elif choice == "2":
            select_input_file(config)
        elif choice == "3":
            run_conversion(config)
        elif choice == "4":
            view_configuration(config)
        elif choice == "5":
            configure_advanced_settings(config)
        elif choice == "0":
            print("\n👋 Thank you for using TTS CLI!")
            print("Visit https://svm0n.github.io/ttsweb/ to use the web player.\n")
            sys.exit(0)
        else:
            print("⚠️  Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting TTS CLI. Goodbye!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
