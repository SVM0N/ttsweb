"""Optional Chandra OCR 2 adapter. No model is loaded until extraction starts."""

import math
import os
import re

from .pdf_extractors import PDFExtractor


def html_to_speech(content):
    """Render table headers alongside values; keep raw HTML separately for review."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(content, "html.parser")
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    for table in soup.find_all("table"):
        if table.find_parent("table"):
            continue
        if table.find("table"):
            # Nested tables have no unambiguous flat row/column narration.
            table.replace_with(soup.new_string(table.get_text(" ", strip=True)))
            continue
        # Expand spans so multi-level headers stay associated with their columns.
        grid, header_rows, occupied = [], [], {}
        for row_idx, row in enumerate(table.find_all("tr")):
            cells = row.find_all(["td", "th"], recursive=False)
            if not cells:
                continue
            col = 0
            for cell in cells:
                while (row_idx, col) in occupied:
                    col += 1
                text = cell.get_text(" ", strip=True)
                try:
                    rowspan = min(100, max(1, int(cell.get("rowspan", 1))))
                    colspan = min(100, max(1, int(cell.get("colspan", 1))))
                except (ValueError, TypeError):
                    rowspan = colspan = 1
                for dy in range(rowspan):
                    for dx in range(colspan):
                        occupied[row_idx + dy, col + dx] = text
                col += colspan
            width = max((c + 1 for r, c in occupied if r == row_idx), default=0)
            grid.append([occupied.get((row_idx, c), "") for c in range(width)])
            # A leading row entirely made of th is a column header, not a data row.
            header_rows.append(bool(row.find_parent("thead")) or all(c.name == "th" for c in cells))
        header_count = 0
        for is_header in header_rows:
            if not is_header:
                break
            header_count += 1
        spoken = []
        caption = table.find("caption")
        if caption:
            spoken.append(caption.get_text(" ", strip=True) + ".")
        for row in grid[header_count:]:
            fields = []
            for col, value in enumerate(row):
                labels = []
                for header in grid[:header_count]:
                    label = header[col] if col < len(header) else ""
                    if label and label not in labels:
                        labels.append(label)
                label = ", ".join(labels) or f"Column {col + 1}"
                fields.append(f"{label}: {value or 'blank'}")
            spoken.append("; ".join(fields) + ".")
        if not spoken:
            spoken.append(table.get_text(" ", strip=True))
        table.replace_with(soup.new_string("\n\n".join(spoken)))
    for br in soup.find_all("br"):
        br.replace_with("\n")
    for block in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "pre"]):
        block.append("\n\n")
    text = soup.get_text()
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n", "\n\n", text).strip()


def chunks_to_elements(chunks, page_number, image_size, page_size, include_headers_footers=False):
    """Chandra chunks are in reading order with boxes in rendered image pixels."""
    image_width, image_height = image_size
    page_width, page_height = page_size
    elements = []
    for chunk in chunks:
        label = chunk.get("label", "Text")
        if label in {"Blank-Page", "Image", "Figure", "Diagram"}:
            continue
        if not include_headers_footers and label in {"Page-Header", "Page-Footer"}:
            continue
        content = chunk.get("content", "")
        text = html_to_speech(content)
        if not text:
            continue
        points = None
        bbox = chunk.get("bbox")
        if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
            try:
                x0, y0, x1, y1 = map(float, bbox)
                if all(math.isfinite(v) for v in (x0, y0, x1, y1)):
                    x0, x1 = [max(0, min(image_width, x)) * page_width / image_width for x in (x0, x1)]
                    y0, y1 = [max(0, min(image_height, y)) * page_height / image_height for y in (y0, y1)]
                    if x1 > x0 and y1 > y0:
                        points = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
            except (ValueError, TypeError):
                pass
        elements.append({
            "text": text,
            "metadata": {
                "page_number": page_number, "points": points,
                "coordinate_width": page_width, "coordinate_height": page_height,
                "category": label, "source_html": content, "source": "chandra",
            },
        })
    return elements


class ChandraExtractor(PDFExtractor):
    """Local HF weights or a self-hosted vLLM server; not the Datalab hosted API."""

    def __init__(self, method=None, include_headers_footers=False):
        self.method = method  # Resolve environment at extraction time, not registration.
        self.include_headers_footers = include_headers_footers
        self._manager = None

    def extract(self, file_like, pages=None):
        import fitz

        method = self.method or os.environ.get("TTS_CHANDRA_METHOD", "hf")
        if method not in {"hf", "vllm"}:
            raise ValueError("TTS_CHANDRA_METHOD must be 'hf' or 'vllm'")
        pdf = fitz.open(stream=file_like.getvalue(), filetype="pdf")
        try:
            selected = list(range(1, len(pdf) + 1)) if pages is None else sorted(set(pages))
            if any(type(p) is not int or p < 1 or p > len(pdf) for p in selected):
                raise ValueError(f"Pages must be integers between 1 and {len(pdf)}")
            if not selected:
                return []
            try:
                from chandra.model import InferenceManager
                from chandra.model.schema import BatchInputItem
            except ImportError as exc:
                raise RuntimeError(
                    "Install chandra-ocr[hf] for local inference, or chandra-ocr for vLLM, "
                    "plus pymupdf and beautifulsoup4. See CHANDRA_USAGE.md."
                ) from exc
            if self._manager is None:
                self._manager = InferenceManager(method=method)
            elements = []
            # One page at a time bounds image memory and local GPU batch size.
            for number in selected:
                page = pdf[number - 1]
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = pixmap.pil_image().convert("RGB")
                try:
                    result = self._manager.generate(
                        [BatchInputItem(image=image, prompt_type="ocr_layout")],
                        include_images=False,
                        include_headers_footers=self.include_headers_footers,
                    )
                    if len(result) != 1 or result[0].error:
                        raise RuntimeError(f"Chandra failed on page {number}; no audio was generated")
                    page_elements = chunks_to_elements(
                        result[0].chunks, number, image.size,
                        (page.rect.width, page.rect.height), self.include_headers_footers,
                    )
                    elements.extend(page_elements)
                finally:
                    image.close()
            if not elements:
                raise RuntimeError("Chandra returned no speakable text; review the PDF and OCR output")
            return elements
        finally:
            pdf.close()

    def get_name(self):
        return "Chandra OCR 2 (Textbooks)"

    def get_description(self):
        return "OCR with reading order, structured tables and block highlighting. Local GPU or vLLM server."
