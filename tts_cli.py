#!/usr/bin/env python3
"""
TTS CLI - Text-to-Speech Command Line Interface

Interactive CLI tool for converting text, PDFs, and EPUBs to speech.
Supports multiple TTS models, PDF extractors, and output formats.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Tuple


# ANSI color codes for terminal formatting
class Colors:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


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

    def to_dict(self):
        """Convert config to dictionary for saving."""
        return {
            'conversion_type': self.conversion_type,
            'tts_model': self.tts_model,
            'pdf_extractor': self.pdf_extractor,
            'output_format': self.output_format,
            'device': self.device,
            'output_dir': self.output_dir,
            'voice': self.voice,
            'speed': self.speed
        }

    def from_dict(self, data):
        """Load config from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save_to_file(self, filename=".tts_cli_config.json"):
        """Save configuration to file."""
        config_path = Path.home() / filename
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        return config_path

    def load_from_file(self, filename=".tts_cli_config.json"):
        """Load configuration from file."""
        config_path = Path.home() / filename
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.from_dict(data)
            return True
        return False


def get_model_display_name(model_key):
    """Get display name for TTS model."""
    names = {
        "kokoro_1.0": "Kokoro v1.0",
        "kokoro_0.9": "Kokoro v0.9",
        "qwen3_custom_voice": "Qwen3 Custom",
        "qwen3_voice_design": "Qwen3 Design",
        "qwen3_base": "Qwen3 Base",
        "maya1": "Maya1",
        "silero_v5": "Silero v5",
    }
    return names.get(model_key, model_key)


def get_extractor_display_name(extractor_key):
    """Get display name for PDF extractor."""
    names = {
        "unstructured": "Unstructured",
        "pymupdf": "PyMuPDF",
        "vision": "Vision",
        "nougat": "Nougat",
    }
    return names.get(extractor_key, extractor_key)


def print_banner():
    """Print CLI banner."""
    print("\n" + "="*70)
    print("  TTS CLI - Text-to-Speech Converter")
    print("  Convert PDFs, EPUBs, and Text to Natural Speech")
    print("="*70 + "\n")


def print_current_config_inline(config: TTSConfig):
    """Print current configuration inline (compact view)."""
    type_display = config.conversion_type.upper()
    model_display = get_model_display_name(config.tts_model)
    extractor_display = get_extractor_display_name(config.pdf_extractor)
    format_display = config.output_format.upper()

    print(f"{Colors.DIM}Current: {type_display} | {model_display} | "
          f"{extractor_display} | {format_display}{Colors.END}")


def print_menu(config: TTSConfig):
    """Print main menu with current config."""
    print("\n" + "-"*70)
    print("MAIN MENU")
    print("-"*70)
    print(f"1. Configure conversion settings")
    print(f"2. Select input file/text")
    print(f"3. Run conversion")
    print(f"4. View full configuration")
    print(f"5. Advanced settings (voice, speed, device)")
    print(f"6. {Colors.BOLD}Save current configuration{Colors.END}")
    print(f"7. {Colors.BOLD}Load saved configuration{Colors.END}")
    print(f"0. Exit")
    print("-"*70)
    print_current_config_inline(config)


def print_config_menu(config: TTSConfig):
    """Print configuration menu."""
    print("\n" + "-"*70)
    print("CONFIGURATION MENU")
    print("-"*70)

    # Highlight current selections
    type_indicator = f" {Colors.BOLD}[{config.conversion_type.upper()}]{Colors.END}"
    model_indicator = f" {Colors.BOLD}[{get_model_display_name(config.tts_model)}]{Colors.END}"
    extractor_indicator = f" {Colors.BOLD}[{get_extractor_display_name(config.pdf_extractor)}]{Colors.END}"
    format_indicator = f" {Colors.BOLD}[{config.output_format.upper()}]{Colors.END}"

    print(f"1. Set conversion type{type_indicator}")
    print(f"2. Select TTS model{model_indicator}")
    print(f"3. Select PDF extractor{extractor_indicator}")
    print(f"4. Set output format{format_indicator}")
    print(f"5. Set output directory {Colors.DIM}[{config.output_dir}]{Colors.END}")
    print(f"0. Back to main menu")
    print("-"*70)


def select_conversion_type(config: TTSConfig):
    """Select conversion type."""
    print("\n" + "-"*50)
    print("SELECT CONVERSION TYPE")
    print("-"*50)

    current = config.conversion_type
    print(f"1. PDF to audio{' ' + Colors.BOLD + '[CURRENT]' + Colors.END if current == 'pdf' else ''}")
    print(f"2. EPUB to audio (per-chapter ZIP){' ' + Colors.BOLD + '[CURRENT]' + Colors.END if current == 'epub' else ''}")
    print(f"3. Text string to audio{' ' + Colors.BOLD + '[CURRENT]' + Colors.END if current == 'string' else ''}")
    print("0. Cancel")

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        config.conversion_type = "pdf"
        print(f"{Colors.GREEN}✓ Conversion type set to: PDF{Colors.END}")
    elif choice == "2":
        config.conversion_type = "epub"
        print(f"{Colors.GREEN}✓ Conversion type set to: EPUB{Colors.END}")
    elif choice == "3":
        config.conversion_type = "string"
        print(f"{Colors.GREEN}✓ Conversion type set to: Text String{Colors.END}")
    elif choice == "0":
        print("Cancelled")
    else:
        print(f"{Colors.YELLOW}⚠️  Invalid choice{Colors.END}")


def select_tts_model(config: TTSConfig):
    """Select TTS model."""
    print("\n" + "-"*50)
    print("SELECT TTS MODEL")
    print("-"*50)

    current = config.tts_model
    models = [
        ("1", "kokoro_1.0", "Kokoro v1.0 (54 voices, 8 languages) [Recommended]"),
        ("2", "kokoro_0.9", "Kokoro v0.9 (10 voices, English, stable)"),
        ("3", "qwen3_custom_voice", "Qwen3-TTS Custom Voice (10 languages, pre-configured)"),
        ("4", "qwen3_voice_design", "Qwen3-TTS Voice Design (natural language descriptions)"),
        ("5", "qwen3_base", "Qwen3-TTS Base (3-second voice cloning)"),
        ("6", "maya1", "Maya1 (20+ emotions, requires GPU)"),
        ("7", "silero_v5", "Silero v5 (Russian language)"),
    ]

    for num, key, desc in models:
        indicator = f" {Colors.BOLD}[CURRENT]{Colors.END}" if current == key else ""
        print(f"{num}. {desc}{indicator}")
    print("0. Cancel")

    choice = input("\nEnter choice [1-7]: ").strip()

    model_map = {m[0]: (m[1], m[2].split(' (')[0]) for m in models}

    if choice in model_map:
        config.tts_model = model_map[choice][0]
        print(f"{Colors.GREEN}✓ TTS model set to: {model_map[choice][1]}{Colors.END}")
    elif choice == "0":
        print("Cancelled")
    else:
        print(f"{Colors.YELLOW}⚠️  Invalid choice{Colors.END}")


def select_pdf_extractor(config: TTSConfig):
    """Select PDF extractor."""
    print("\n" + "-"*50)
    print("SELECT PDF EXTRACTOR")
    print("-"*50)

    current = config.pdf_extractor
    extractors = [
        ("1", "unstructured", "Unstructured (advanced layout analysis) [Recommended]"),
        ("2", "pymupdf", "PyMuPDF (fast, for clean PDFs)"),
        ("3", "vision", "Apple Vision (OCR for scanned PDFs, macOS only)"),
        ("4", "nougat", "Nougat (academic papers with equations)"),
    ]

    for num, key, desc in extractors:
        indicator = f" {Colors.BOLD}[CURRENT]{Colors.END}" if current == key else ""
        print(f"{num}. {desc}{indicator}")
    print("0. Cancel")

    choice = input("\nEnter choice [1-4]: ").strip()

    extractor_map = {e[0]: (e[1], e[2].split(' (')[0]) for e in extractors}

    if choice in extractor_map:
        config.pdf_extractor = extractor_map[choice][0]
        print(f"{Colors.GREEN}✓ PDF extractor set to: {extractor_map[choice][1]}{Colors.END}")
    elif choice == "0":
        print("Cancelled")
    else:
        print(f"{Colors.YELLOW}⚠️  Invalid choice{Colors.END}")


def select_output_format(config: TTSConfig):
    """Select output format."""
    print("\n" + "-"*50)
    print("SELECT OUTPUT FORMAT")
    print("-"*50)

    current = config.output_format
    print(f"1. MP3 (compressed, smaller file size){' ' + Colors.BOLD + '[CURRENT]' + Colors.END if current == 'mp3' else ''}")
    print(f"2. WAV (uncompressed, higher quality){' ' + Colors.BOLD + '[CURRENT]' + Colors.END if current == 'wav' else ''}")
    print("0. Cancel")

    choice = input("\nEnter choice [1-2]: ").strip()

    if choice == "1":
        config.output_format = "mp3"
        print(f"{Colors.GREEN}✓ Output format set to: MP3{Colors.END}")
    elif choice == "2":
        config.output_format = "wav"
        print(f"{Colors.GREEN}✓ Output format set to: WAV{Colors.END}")
    elif choice == "0":
        print("Cancelled")
    else:
        print(f"{Colors.YELLOW}⚠️  Invalid choice{Colors.END}")


def set_output_directory(config: TTSConfig):
    """Set output directory."""
    print(f"\nCurrent output directory: {Colors.CYAN}{config.output_dir}{Colors.END}")
    new_dir = input("Enter new output directory (or press Enter to keep current): ").strip()

    if new_dir:
        config.output_dir = new_dir
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}✓ Output directory set to: {config.output_dir}{Colors.END}")


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
            print(f"{Colors.GREEN}✓ PDF file selected: {pdf_path}{Colors.END}")

            # Ask about page selection
            pages_input = input("\nEnter page numbers (e.g., '1,3,5-7') or press Enter for all pages: ").strip()
            if pages_input:
                config.pdf_pages = parse_page_numbers(pages_input)
                print(f"{Colors.GREEN}✓ Pages selected: {config.pdf_pages}{Colors.END}")
            else:
                config.pdf_pages = None
                print(f"{Colors.GREEN}✓ All pages will be processed{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  File not found or invalid path{Colors.END}")

    elif config.conversion_type == "epub":
        print("Enter path to EPUB file:")
        epub_path = input("> ").strip()
        if epub_path and os.path.exists(epub_path):
            config.epub_path = epub_path
            print(f"{Colors.GREEN}✓ EPUB file selected: {epub_path}{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  File not found or invalid path{Colors.END}")

    elif config.conversion_type == "string":
        print("Enter text to convert to speech:")
        print("(Type your text and press Enter when done)")
        text = input("> ").strip()
        if text:
            config.text_input = text
            print(f"{Colors.GREEN}✓ Text input set ({len(text)} characters){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No text entered{Colors.END}")


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
    print(f"1. Set voice/speaker {Colors.DIM}[{config.voice or 'Default'}]{Colors.END}")
    print(f"2. Set speech speed {Colors.DIM}[{config.speed}]{Colors.END}")
    print(f"3. Set device {Colors.DIM}[{config.device}]{Colors.END}")
    print("0. Back to main menu")
    print("-"*70)

    choice = input("\nEnter choice [1-3]: ").strip()

    if choice == "1":
        print(f"\nCurrent voice: {Colors.CYAN}{config.voice or 'Default'}{Colors.END}")
        voice = input("Enter voice name (or press Enter for default): ").strip()
        if voice:
            config.voice = voice
            print(f"{Colors.GREEN}✓ Voice set to: {voice}{Colors.END}")

    elif choice == "2":
        print(f"\nCurrent speed: {Colors.CYAN}{config.speed}{Colors.END}")
        speed_str = input("Enter speed (0.5-2.0, default 1.0): ").strip()
        if speed_str:
            try:
                config.speed = float(speed_str)
                print(f"{Colors.GREEN}✓ Speed set to: {config.speed}{Colors.END}")
            except ValueError:
                print(f"{Colors.YELLOW}⚠️  Invalid speed value{Colors.END}")

    elif choice == "3":
        print("\n1. Auto (recommended)")
        print("2. CUDA (GPU)")
        print("3. CPU")
        print("4. MPS (Apple Silicon)")
        device_choice = input("\nEnter choice [1-4]: ").strip()

        devices = {"1": "auto", "2": "cuda", "3": "cpu", "4": "mps"}
        if device_choice in devices:
            config.device = devices[device_choice]
            print(f"{Colors.GREEN}✓ Device set to: {config.device}{Colors.END}")


def save_configuration(config: TTSConfig):
    """Save current configuration to file."""
    try:
        config_path = config.save_to_file()
        print(f"\n{Colors.GREEN}✓ Configuration saved to: {config_path}{Colors.END}")
        print(f"{Colors.DIM}You can load this configuration later using option 7.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.YELLOW}✗ Failed to save configuration: {e}{Colors.END}")

    input("\nPress Enter to continue...")


def load_configuration(config: TTSConfig):
    """Load configuration from file."""
    try:
        if config.load_from_file():
            print(f"\n{Colors.GREEN}✓ Configuration loaded successfully{Colors.END}")
            view_configuration(config)
        else:
            print(f"\n{Colors.YELLOW}⚠️  No saved configuration found{Colors.END}")
            print(f"{Colors.DIM}Save a configuration first using option 6.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.YELLOW}✗ Failed to load configuration: {e}{Colors.END}")

    input("\nPress Enter to continue...")


def view_configuration(config: TTSConfig):
    """Display current configuration."""
    print("\n" + "="*70)
    print("CURRENT CONFIGURATION")
    print("="*70)
    print(f"Conversion Type:  {Colors.BOLD}{config.conversion_type.upper()}{Colors.END}")
    print(f"TTS Model:        {Colors.BOLD}{get_model_display_name(config.tts_model)}{Colors.END}")
    print(f"PDF Extractor:    {Colors.BOLD}{get_extractor_display_name(config.pdf_extractor)}{Colors.END}")
    print(f"Output Format:    {Colors.BOLD}{config.output_format.upper()}{Colors.END}")
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


def fix_transformers_compatibility():
    """Fix PyTorch/transformers compatibility issue."""
    try:
        import subprocess
        import sys

        print(f"\n{Colors.YELLOW}⚠️  Fixing PyTorch/transformers compatibility...{Colors.END}")
        print(f"{Colors.DIM}   This is a known issue with newer PyTorch versions.{Colors.END}")

        # Upgrade transformers to a compatible version
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "--upgrade", "transformers>=4.41.0"],
            stderr=subprocess.DEVNULL
        )
        print(f"{Colors.GREEN}✓ Compatibility fix applied{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Could not apply fix automatically: {e}{Colors.END}")
        print(f"{Colors.DIM}   Try: pip install --upgrade transformers{Colors.END}")
        return False


def run_conversion(config: TTSConfig):
    """Run the TTS conversion."""
    # Validate configuration
    valid, message = validate_configuration(config)
    if not valid:
        print(f"\n{Colors.YELLOW}⚠️  Configuration Error: {message}{Colors.END}")
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
        try:
            install_dependencies(
                tts_model=config.tts_model,
                pdf_extractor=config.pdf_extractor,
                conversion_type=config.conversion_type,
                out_format=config.output_format
            )
        except AttributeError as e:
            if "PyTreeSpec" in str(e):
                # Handle transformers compatibility issue
                print(f"\n{Colors.YELLOW}⚠️  PyTorch/transformers compatibility issue detected{Colors.END}")
                if fix_transformers_compatibility():
                    print(f"{Colors.GREEN}✓ Please restart the CLI to apply the fix{Colors.END}")
                    input("\nPress Enter to exit...")
                    sys.exit(0)
                else:
                    raise
            else:
                raise

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
        print(f"{Colors.GREEN}✓ CONVERSION COMPLETED SUCCESSFULLY{Colors.END}")
        print("="*70)

        if config.conversion_type in ["pdf", "string"]:
            audio_path, manifest_path = result
            print(f"Audio file:    {Colors.CYAN}{audio_path}{Colors.END}")
            print(f"Manifest file: {Colors.CYAN}{manifest_path}{Colors.END}")
        else:  # epub
            print(f"ZIP archive: {Colors.CYAN}{result}{Colors.END}")

        print(f"\n💡 You can now upload these files to the web player at:")
        print(f"   {Colors.BLUE}https://svm0n.github.io/ttsweb/{Colors.END}")

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Conversion cancelled by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.YELLOW}✗ Error during conversion: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to continue...")


def configuration_menu(config: TTSConfig):
    """Handle configuration menu."""
    while True:
        print_config_menu(config)
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
            print(f"{Colors.YELLOW}⚠️  Invalid choice. Please try again.{Colors.END}")


def main():
    """Main CLI loop."""
    config = TTSConfig()

    # Try to load saved configuration
    config.load_from_file()

    print_banner()
    print("Welcome! This tool converts PDFs, EPUBs, and text to speech.")
    print("Start by configuring your conversion settings (Option 1).")

    while True:
        print_menu(config)
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
        elif choice == "6":
            save_configuration(config)
        elif choice == "7":
            load_configuration(config)
        elif choice == "0":
            print(f"\n{Colors.CYAN}👋 Thank you for using TTS CLI!{Colors.END}")
            print(f"Visit {Colors.BLUE}https://svm0n.github.io/ttsweb/{Colors.END} to use the web player.\n")
            sys.exit(0)
        else:
            print(f"{Colors.YELLOW}⚠️  Invalid choice. Please try again.{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}👋 Exiting TTS CLI. Goodbye!{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.YELLOW}✗ Fatal error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
