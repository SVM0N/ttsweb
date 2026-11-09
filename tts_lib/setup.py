"""Automatic dependency installation for TTS notebook.

This module handles smart dependency installation based on user configuration.
Only installs the packages actually needed for the selected TTS model,
PDF extractor, and output formats.
"""

import subprocess
import sys


def install_package(package):
    """Install a package using pip."""
    print(f"Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
    print(f"✓ {package} installed")


def install_dependencies(
    tts_model,
    pdf_extractor=None,
    conversion_type="string",
    out_format="wav"
):
    """Install only the dependencies needed for the selected configuration.

    Args:
        tts_model: TTS model name ("kokoro_0.9", "kokoro_1.0", "maya1", "silero_v5")
        pdf_extractor: PDF extractor name ("unstructured", "pymupdf", "vision", "nougat", "chandra", None)
        conversion_type: Type of conversion ("string", "pdf", "epub")
        out_format: Output format ("wav" or "mp3")
    """
    print("="*60)
    print("INSTALLING DEPENDENCIES")
    print("="*60)

    # Core dependencies (always needed)
    print("\n📦 Installing core dependencies...")

    # Install PyTorch with CUDA support if needed
    try:
        import torch
        print(f"✓ torch already installed")
    except ImportError:
        # Detect if running in Colab (likely has GPU)
        try:
            import google.colab
            in_colab = True
        except ImportError:
            in_colab = False

        if in_colab:
            print("Installing torch with CUDA support for Colab...")
            # Install PyTorch with CUDA 12.1 support (Colab's default as of 2024)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-q",
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cu121"
            ])
            print("✓ torch installed with CUDA support")
        else:
            print("Installing torch (auto-detect CUDA)...")
            install_package("torch")

    # Install other core packages
    core_packages = ["soundfile", "numpy", "ebooklib", "pydub"]
    for pkg in core_packages:
        try:
            __import__(pkg.replace("-", "_"))
            print(f"✓ {pkg} already installed")
        except ImportError:
            install_package(pkg)

    # Note about ffmpeg for MP3
    if out_format == "mp3":
        print("\n⚠️  NOTE: MP3 encoding requires ffmpeg to be installed on your system:")
        print("   - macOS: brew install ffmpeg")
        print("   - Linux: sudo apt-get install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/")
        print("   - Colab: ffmpeg is pre-installed ✓")

    # TTS model dependencies
    print("\n🎤 Installing TTS model dependencies...")
    if tts_model.startswith("kokoro"):
        kokoro_packages = ["kokoro>=0.9.4", "misaki[en]"]
        for pkg in kokoro_packages:
            try:
                __import__("kokoro")
                print(f"✓ Kokoro already installed")
                break
            except ImportError:
                install_package(pkg)

    elif tts_model == "maya1":
        maya_packages = ["transformers", "snac"]
        for pkg in maya_packages:
            try:
                __import__(pkg.replace("-", "_"))
                print(f"✓ {pkg} already installed")
            except ImportError:
                install_package(pkg)
        print("\n⚠️  NOTE: Maya1 requires:")
        print("   - GPU with 16GB+ VRAM (A100, H100, or RTX 4090 recommended)")
        print("   - CUDA support (will not work well on CPU/MPS)")
        print("   - First run will download ~3GB model")

    elif tts_model == "silero_v5":
        try:
            __import__("omegaconf")
            print(f"✓ omegaconf already installed")
        except ImportError:
            install_package("omegaconf")
        print("✓ Silero loads via torch.hub (no additional packages needed)")

    elif tts_model.startswith("qwen3"):
        # Qwen3-TTS dependencies
        qwen_packages = ["qwen-tts", "transformers"]
        for pkg in qwen_packages:
            try:
                pkg_import = "qwen_tts" if pkg == "qwen-tts" else pkg
                __import__(pkg_import)
                print(f"✓ {pkg} already installed")
            except ImportError:
                install_package(pkg)

        # Check for flash-attn (optional but recommended for GPU)
        try:
            import torch
            if torch.cuda.is_available():
                print("\n💡 Optional: Installing Flash Attention 2 for faster GPU inference...")
                print("   This may take several minutes to compile...")
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "-q", "flash-attn", "--no-build-isolation"],
                        stderr=subprocess.PIPE
                    )
                    print("✓ Flash Attention 2 installed")
                except subprocess.CalledProcessError:
                    print("⚠️  Flash Attention 2 installation failed (not critical)")
                    print("   Model will use standard attention instead")
        except Exception:
            pass

        print("\n⚠️  NOTE: Qwen3-TTS features:")
        print("   - Supports 10 languages (Chinese, English, Japanese, Korean, etc.)")
        print("   - 3-second voice cloning capability")
        print("   - Natural language voice descriptions")
        print("   - First run will download ~1.7GB or ~600MB model")
        print("   - Recommended: GPU with 8GB+ VRAM for best performance")

    # PDF extractor dependencies
    if conversion_type == "pdf" and pdf_extractor:
        print("\n📄 Installing PDF extractor dependencies...")

        if pdf_extractor == "unstructured":
            # Install unstructured first
            try:
                __import__("unstructured")
                print(f"✓ unstructured already installed")
            except ImportError:
                install_package("unstructured[local-inference]")

            # Install detectron2 with smart wheel detection
            try:
                __import__("detectron2")
                print(f"✓ detectron2 already installed")
            except ImportError:
                print("Installing detectron2 (detecting optimal method)...")
                try:
                    import torch

                    # Get CUDA and PyTorch versions
                    if torch.cuda.is_available():
                        cuda_version = torch.version.cuda.replace(".", "")
                        torch_version = ".".join(torch.__version__.split(".")[:2])

                        # Try pre-built wheel first (fast)
                        wheel_url = f"https://dl.fbaipublicfiles.com/detectron2/wheels/cu{cuda_version}/torch{torch_version}/index.html"
                        print(f"   → Attempting pre-built wheel for CUDA {torch.version.cuda}, PyTorch {torch_version}...")

                        try:
                            subprocess.check_call(
                                [sys.executable, "-m", "pip", "install", "-q", "detectron2", "-f", wheel_url],
                                stderr=subprocess.PIPE
                            )
                            print(f"✓ detectron2 installed (pre-built wheel)")
                        except subprocess.CalledProcessError:
                            # Fallback to building from source
                            print(f"   → Pre-built wheel not available, building from source...")
                            install_package("git+https://github.com/facebookresearch/detectron2.git@v0.6")
                    else:
                        # CPU-only installation
                        print(f"   → No CUDA detected, building from source for CPU...")
                        install_package("git+https://github.com/facebookresearch/detectron2.git@v0.6")

                except Exception as e:
                    print(f"   ⚠️  Error during smart detection: {e}")
                    print(f"   → Falling back to standard installation...")
                    install_package("git+https://github.com/facebookresearch/detectron2.git@v0.6")

        elif pdf_extractor == "chandra":
            import os
            method = os.environ.get("TTS_CHANDRA_METHOD", "hf")
            if method not in {"hf", "vllm"}:
                raise ValueError("TTS_CHANDRA_METHOD must be 'hf' or 'vllm'")
            install_package("chandra-ocr[hf]" if method == "hf" else "chandra-ocr")
            install_package("pymupdf")
            install_package("beautifulsoup4")
            print("Chandra: local HF weights need GPU memory; vLLM requires a running server.")
            print("See CHANDRA_USAGE.md. No Detectron2 installation is needed for this extractor.")

        elif pdf_extractor == "pymupdf":
            try:
                __import__("fitz")
                print(f"✓ pymupdf already installed")
            except ImportError:
                install_package("pymupdf")

        elif pdf_extractor == "vision":
            import platform
            if platform.system() != "Darwin":
                print("⚠️  WARNING: Vision Framework is only available on macOS!")
            else:
                vision_packages = ["pyobjc-framework-Vision", "pyobjc-framework-Quartz"]
                for pkg in vision_packages:
                    try:
                        module_name = pkg.replace("-", "_").replace("pyobjc_framework_", "")
                        __import__(module_name)
                        print(f"✓ {pkg} already installed")
                    except ImportError:
                        install_package(pkg)

        elif pdf_extractor == "nougat":
            nougat_packages = ["nougat-ocr", "transformers"]
            for pkg in nougat_packages:
                try:
                    __import__(pkg.replace("-", "_"))
                    print(f"✓ {pkg} already installed")
                except ImportError:
                    install_package(pkg)

    # EPUB and MP3 dependencies are now part of core dependencies
    # (installed at the beginning)

    print("\n" + "="*60)
    print("✓ ALL DEPENDENCIES INSTALLED")
    print("="*60)
