# PDF Semantic Materials Skill

A general-purpose agent skill for turning PDFs into agent-readable semantic material packs.

This is useful when a PDF should become structured context for downstream agents: every page gets its own folder, page image, page summary, and visual-asset description.

## Typical Use Cases

- Turning slide decks, proposals, reports, and brochures into page-by-page knowledge packs.
- Preparing PDF content for AI agents that need to understand page meaning, visual assets, and asset roles.
- Converting mixed text-and-image PDFs into structured Markdown plus rendered page images.
- Avoiding noisy raw PDF image extraction when a document contains duplicated masks, slices, icons, or background fragments.
- Building reusable source materials for downstream writing, design, product analysis, or implementation tasks.

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

Copy or clone this repository into your agent skills directory:

```bash
git clone https://github.com/Nomia/pdf-semantic-materials-skill.git /path/to/skills/pdf-semantic-materials
```

Restart or reload your agent runtime if the skill list does not refresh automatically.

## Usage

Ask your agent something like:

```text
Convert this PDF into a semantic material pack. Create one folder per page, include a rendered page image, write page.md, and write a Markdown description for each image.
```

Or run the scaffold script directly:

```bash
python3 scripts/build_pdf_materials.py /path/to/file.pdf /path/to/output --overwrite
```

The script creates the deterministic structure and draft Markdown. An agent should then inspect the rendered page images and rewrite the Markdown files with real semantic descriptions.

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
