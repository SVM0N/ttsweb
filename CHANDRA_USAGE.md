# Chandra for textbooks

Choose **Chandra OCR 2** (option 5) in `python tts_cli.py`, or set
`PDF_EXTRACTOR = "chandra"` in `TTS.ipynb`. The default remains Unstructured.
Selecting Chandra installs only its own extraction dependencies, not Detectron2.

## Hardware and installation

The [official checkpoint](https://huggingface.co/datalab-to/chandra-ocr-2/tree/main)
has a **10.6 GB weight file**, plus Python/PyTorch dependencies. Runtime memory
also includes images, activations and generation cache. Budget **16–24 GB GPU
memory** for local single-page inference; this is a planning estimate, not a
measured minimum. Larger pages and another loaded TTS model increase memory use.
CPU use is not a practical recommendation for processing whole books.

Local inference (the default):

```bash
pip install 'chandra-ocr[hf]' pymupdf beautifulsoup4
python tts_cli.py
```

Use a separate self-hosted vLLM server to keep OCR off your TTS machine:

```bash
pip install chandra-ocr pymupdf beautifulsoup4
export TTS_CHANDRA_METHOD=vllm
export VLLM_API_BASE=http://localhost:8000/v1
export VLLM_MODEL_NAME=chandra
python tts_cli.py
```

Start/configure the server using [Chandra's instructions](https://github.com/datalab-to/chandra#vllm-server-optional).
Set the model name to the name served by that server. These settings must be set
before Chandra is imported. This adapter supports HF and self-hosted vLLM, **not
Datalab's hosted API**; the hosted service uses a separate API and newer models.

## What is preserved

- Blocks follow Chandra's reading order; they are not sorted across columns by y.
- Metadata retains page number, block category, source HTML, box, and coordinate
  dimensions. Image-pixel boxes are converted to the displayed PDF page size.
- Tables with explicit HTML header cells are narrated as header/value pairs.
  Row/column spans are expanded, including multiple header rows. Tables without
  explicit header rows use “Column 1”, etc.; nested tables fall back to plain text.
  Inspect these cases before generating a whole book.
- Repeated page headers/footers and figure/diagram blocks are excluded by default;
  captions and footnotes remain. Image descriptions are not narrated automatically.
- The player highlights each block inside its column. Sentences from the same
  block share its box; these are not word-accurate or sentence-specific boxes.

Math is retained as extracted notation. Converting arbitrary LaTeX into natural
spoken mathematics is not implemented. OCR can still omit or misread content.

## Compare a sample before generating audio

Install Unstructured's dependencies using the existing setup if needed, then run:

```bash
python tools/compare_extractors.py book.pdf --pages 3-5,12,18-20 --out files/comparison
```

This processes only the selected pages with Chandra (Unstructured filters its
results after parsing). It generates `unstructured.json`, `chandra.json` and a
`review.html` with side-by-side text in extraction order. It generates no audio
and calculates no accuracy score. Review against the original PDF: column order,
omitted/duplicated text, table headers and values, footnotes, equations and boxes.
Use `--extractors pymupdf` for a fast smoke check without any OCR model.

The JSON files retain the `elements` accepted by the existing TTS backends, so
you can review/extract in a separate process before loading a large TTS model.

## Validation

```bash
python -m unittest discover -s tests -v
python tests/check_highlights.py
node tests/check_service_worker.cjs
```

The Python tests use generated PDFs and mocked Chandra responses to exercise
page selection, failures, coordinate scaling and table narration. They do not
measure real OCR accuracy. The highlight check uses Playwright's Chromium.
