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
        f"# {pdf_path.stem} PDF 语义材料包",
        "",
        f"来源 PDF：`{pdf_path}`",
        "",
        "说明：每个页面文件夹包含该页完整页面图、页面语义说明和素材图说明。",
        "",
        "## 页面索引",
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
        visible_text = text_layer if text_layer else "待根据页面图识别"

        page_md = f"""# 第 {idx:0{width}d} 页：待命名

## 页面主题
待根据页面图总结。

## 主要内容
待根据页面图和文本层补充。

## 页面素材
- [image-01.png](./image-01.png)：完整页面视觉素材。待描述页面中的截图、照片、图表、文字和布局。

## 素材作用
待说明该素材如何支撑本页主题。

## 关联素材说明
- [image-01.md](./image-01.md)：对完整页面图的详细描述。
"""

        image_md = f"""# image-01.png：第 {idx:0{width}d} 页完整页面图

## 图片讲述的内容
待根据页面图总结。

## 详细视觉描述
待描述页面中的物体、截图、照片、图标、图表、版式和视觉重点。

## 识别到的关键文字
{visible_text}

## 在本页中的作用
待说明该图片在本页中的表达作用。
"""

        write_text(page_dir / "page.md", page_md, overwrite)
        write_text(page_dir / "image-01.md", image_md, overwrite)
        index_lines.append(f"- [第 {idx:0{width}d} 页](./{page_id}/page.md) - 待总结")

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
