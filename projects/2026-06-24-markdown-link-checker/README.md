# Markdown Link Checker

A small Python CLI that scans Markdown files for practical link problems without requiring third-party packages.

It reports:

- Empty link targets like `[label]()`
- Malformed inline links with missing labels or URLs
- Duplicate local anchors in the same document
- Links that point at anchors missing from the same document

## Run

```bash
python3 markdown_link_checker.py sample.md
```

Scan multiple files at once:

```bash
python3 markdown_link_checker.py README.md docs/notes.md
```

The command exits with status `1` when problems are found and `0` when all scanned files pass.

## Verify

```bash
python3 -m unittest discover . -v
python3 markdown_link_checker.py sample.md
```

