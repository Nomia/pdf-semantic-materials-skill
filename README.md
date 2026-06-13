# PDF Semantic Materials Skill

A Codex skill for turning PDFs into agent-readable semantic material packs.

This is useful when a PDF should become structured context for downstream agents: every page gets its own folder, page image, page summary, and visual-asset description.

## What It Creates

```text
target-dir/
├── index.md
├── page-01/
│   ├── page.md
│   ├── image-01.png
│   └── image-01.md
├── page-02/
│   ├── page.md
│   ├── image-01.png
│   └── image-01.md
└── ...
```

The skill is designed for semantic PDF parsing, not raw embedded-image dumping. It avoids the common failure mode where `pdfimages -all` extracts thousands of duplicate masks, slices, icons, or background fragments.

## Install

Copy or clone this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Nomia/pdf-semantic-materials-skill.git ~/.codex/skills/pdf-semantic-materials
```

Restart Codex after installation if the skill list does not refresh automatically.

## Usage

Ask Codex something like:

```text
把这个 PDF 转成语义材料包，每页一个文件夹，每页要有页面图、page.md 和图片说明 md。
```

Or run the scaffold script directly:

```bash
python3 scripts/build_pdf_materials.py /path/to/file.pdf /path/to/output --overwrite
```

The script creates the deterministic structure and draft Markdown. Codex should then inspect the rendered page images and rewrite the Markdown files with real semantic descriptions.

## Requirements

The script expects Poppler command-line tools:

- `pdfinfo`
- `pdftoppm`
- optional: `pdftotext`

On macOS with Homebrew:

```bash
brew install poppler
```

## Markdown Rules

Generated materials should stay content-focused:

- `page.md` explains the page theme, main content, page assets, and asset role.
- `image-01.md` explains what the rendered page image communicates, its visible text, visual elements, and role on the page.
- Do not add generic "usage suggestions" sections unless explicitly requested.

## License

MIT
