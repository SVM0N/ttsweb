"""Extract selected pages without generating audio; save text/boxes for review."""

import argparse
import io
import json
import sys
import time
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tts_lib.pdf_extractors import get_available_extractors


def parse_pages(value):
    pages = set()
    for part in value.split(","):
        bounds = part.strip().split("-")
        if len(bounds) == 1:
            pages.add(int(bounds[0]))
        elif len(bounds) == 2:
            first, last = map(int, bounds)
            if first > last:
                raise ValueError("Page ranges must ascend")
            pages.update(range(first, last + 1))
        else:
            raise ValueError("Use page numbers/ranges such as 1-3,7,10")
    if not pages or min(pages) < 1:
        raise ValueError("Page numbers start at 1")
    return sorted(pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", required=True, help="For example: 1-3,7,10")
    parser.add_argument("--extractors", nargs="+", default=["unstructured", "chandra"],
                        choices=["unstructured", "chandra", "pymupdf"])
    parser.add_argument("--out", type=Path, default=Path("files/parser-comparison"))
    args = parser.parse_args()
    try:
        pages = parse_pages(args.pages)
    except ValueError as exc:
        parser.error(str(exc))
    args.out.mkdir(parents=True, exist_ok=True)
    data = args.pdf.read_bytes()
    sections, failed = [], False
    for name in args.extractors:
        started = time.perf_counter()
        try:
            extractor = get_available_extractors()[name]
            elements = extractor.extract(io.BytesIO(data), pages=pages)
            result = {"extractor": name, "pages": pages,
                      "seconds": round(time.perf_counter() - started, 2), "elements": elements}
            (args.out / f"{name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            blocks = []
            for item in elements:
                meta = item["metadata"]
                blocks.append(f'<h3>Page {meta.get("page_number")} · {escape(str(meta.get("category", "Text")))}</h3>'
                              f'<pre>{escape(item["text"])}</pre>')
            sections.append(f'<section><h2>{escape(name)} · {result["seconds"]} s</h2>{"".join(blocks)}</section>')
            print(f"{name}: {len(elements)} elements in {result['seconds']} seconds")
        except Exception as exc:
            failed = True
            sections.append(f'<section><h2>{escape(name)}</h2><pre>{escape(str(exc))}</pre></section>')
            print(f"{name} failed: {exc}", file=sys.stderr)
    report = '<!doctype html><meta charset="utf-8"><title>Parser comparison</title>' \
             '<style>body{font:16px system-ui;display:flex;gap:24px;padding:24px}section{flex:1;min-width:0}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
    (args.out / "review.html").write_text(report + "".join(sections), encoding="utf-8")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
