#!/usr/bin/env python3
"""Scaffold a semantic materials pack from a PDF.

This script handles deterministic work only: page counting, page rendering,
text-layer extraction, directory creation, and Markdown template generation.
An agent should inspect the rendered images and replace template text with
semantic descriptions.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"Missing required tool: {name}")
    return path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def page_count(pdfinfo: str, pdf_path: Path) -> int:
    result = run([pdfinfo, str(pdf_path)])
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        raise SystemExit("Could not determine PDF page count from pdfinfo output")
    return int(match.group(1))


def extract_page_text(pdftotext: str | None, pdf_path: Path, page_number: int) -> str:
    if not pdftotext:
        return ""
    try:
        result = run(
            [
                pdftotext,
                "-layout",
                "-f",
                str(page_number),
                "-l",
                str(page_number),
                str(pdf_path),
                "-",
            ]
        )
    except subprocess.CalledProcessError:
        return ""
    return result.stdout.strip()


def render_pages(pdftoppm: str, pdf_path: Path, work_dir: Path, dpi: int) -> list[Path]:
    work_dir.mkdir(parents=True, exist_ok=True)
    prefix = work_dir / "page"
    run([pdftoppm, "-png", "-r", str(dpi), str(pdf_path), str(prefix)])
    return sorted(work_dir.glob("page-*.png"), key=page_sort_key)


def page_sort_key(path: Path) -> int:
    match = re.search(r"(\d+)$", path.stem)
    return int(match.group(1)) if match else 0


def write_text(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def scaffold(pdf_path: Path, target_dir: Path, dpi: int, overwrite: bool, keep_work: bool) -> None:
    pdfinfo = require_tool("pdfinfo")
    pdftoppm = require_tool("pdftoppm")
    pdftotext = shutil.which("pdftotext")

    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    total_pages = page_count(pdfinfo, pdf_path)
    width = max(2, len(str(total_pages)))
    target_dir.mkdir(parents=True, exist_ok=True)
    work_dir = target_dir / "_work" / "pages"

    rendered = render_pages(pdftoppm, pdf_path, work_dir, dpi)
    if len(rendered) != total_pages:
        raise SystemExit(f"Expected {total_pages} rendered pages, found {len(rendered)}")

    index_lines = [
        f"# {pdf_path.stem} PDF Semantic Materials Pack",
        "",
        f"Source PDF: `{pdf_path}`",
        "",
        "Each page folder contains a rendered page image, a page-level semantic note, and an image description.",
        "",
        "## Page Index",
        "",
    ]

    for idx, rendered_page in enumerate(rendered, start=1):
        page_id = f"page-{idx:0{width}d}"
        page_dir = target_dir / page_id
        page_dir.mkdir(parents=True, exist_ok=True)

        image_path = page_dir / "image-01.png"
        if overwrite or not image_path.exists():
            shutil.copy2(rendered_page, image_path)

        text_layer = extract_page_text(pdftotext, pdf_path, idx)
        visible_text = text_layer if text_layer else "To be identified from the rendered page image."

        page_md = f"""# Page {idx:0{width}d}: Untitled

## Page Theme
To be summarized from the rendered page image.

## Main Content
To be completed from the rendered page image and any extracted text layer.

## Page Assets
- [image-01.png](./image-01.png): Full-page visual asset. Describe screenshots, photos, charts, visible text, and layout.

## Asset Role
Explain how this asset supports the page theme.

## Related Asset Notes
- [image-01.md](./image-01.md): Detailed description of the full-page image.
"""

        image_md = f"""# image-01.png: Page {idx:0{width}d} Full-Page Image

## What The Image Communicates
To be summarized from the rendered page image.

## Detailed Visual Description
Describe objects, screenshots, photos, icons, charts, layout, and visual emphasis.

## Key Visible Text
{visible_text}

## Role On This Page
Explain the image's role in the page's message.
"""

        write_text(page_dir / "page.md", page_md, overwrite)
        write_text(page_dir / "image-01.md", image_md, overwrite)
        index_lines.append(f"- [Page {idx:0{width}d}](./{page_id}/page.md) - To be summarized")

    write_text(target_dir / "index.md", "\n".join(index_lines) + "\n", overwrite)

    if not keep_work:
        shutil.rmtree(target_dir / "_work", ignore_errors=True)

    print(f"Created semantic PDF scaffold: {target_dir}")
    print(f"Pages: {total_pages}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a semantic materials pack from a PDF.")
    parser.add_argument("pdf", type=Path, help="Input PDF path")
    parser.add_argument("target", type=Path, help="Output directory")
    parser.add_argument("--dpi", type=int, default=144, help="Render DPI for page images")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing Markdown/images")
    parser.add_argument("--keep-work", action="store_true", help="Keep temporary rendered page files")
    args = parser.parse_args()

    scaffold(args.pdf.expanduser().resolve(), args.target.expanduser().resolve(), args.dpi, args.overwrite, args.keep_work)
    return 0


if __name__ == "__main__":
    sys.exit(main())
