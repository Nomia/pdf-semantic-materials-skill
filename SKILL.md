---
name: pdf-semantic-materials
description: Convert PDFs into agent-readable semantic material packs. Use when the user asks to parse a PDF page by page, create per-page folders, render page images, write Markdown explanations, describe visual assets, or build a semantic PDF knowledge/materials package for downstream agents.
metadata:
  short-description: Turn PDFs into semantic material packs
---

# PDF Semantic Materials

Use this skill when a PDF should become a structured, agent-readable materials directory rather than a raw extraction dump.

## Output Contract

Default output structure:

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

Each `page.md` must explain:

- page theme
- main content
- page assets
- asset role
- links to asset Markdown files

Each `image-01.md` must explain:

- what the image communicates
- detailed visual description
- key visible text
- role on the page

Do not add generic sections such as `使用建议`, `Usage Suggestions`, or agent instructions inside generated page/material Markdown unless the user explicitly asks for them.

## Workflow

1. Confirm the PDF path and target directory.
2. Run `scripts/build_pdf_materials.py` to scaffold folders, render each page as `image-01.png`, extract any text layer, and create Markdown templates.
3. Inspect the rendered page images, preferably via contact sheets or direct page views.
4. Rewrite each generated Markdown file with semantic descriptions in the user's requested language.
5. Treat the rendered full page as the default asset. Only create additional cropped image assets when the user explicitly asks for separated visual elements or when a page contains multiple independent reusable assets that need separate descriptions.
6. Validate that every page folder has `page.md`, `image-01.png`, and `image-01.md`.
7. Validate that `index.md` links to all page folders.

## Important Rules

- Do not default to `pdfimages -all` for semantic material packs. PDF internals often contain thousands of duplicated masks, slices, icons, and background fragments.
- Use raw embedded-image extraction only when the user specifically asks for original embedded images.
- Prefer page rendering with `pdftoppm` because it preserves the visual context needed for semantic descriptions.
- If the PDF has a weak or missing text layer, rely on visual inspection of the rendered pages.
- If the PDF is a slide deck, one rendered page image per slide is usually the correct primary asset.
- Keep Markdown factual and content-focused. Avoid operational advice to future agents unless requested.

## Scaffold Command

From the skill directory:

```bash
python3 scripts/build_pdf_materials.py /path/to/file.pdf /path/to/target-dir --overwrite
```

The script creates mechanical structure and draft Markdown. The agent must still inspect the page images and replace placeholders with real semantic descriptions.
