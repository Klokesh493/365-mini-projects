#!/usr/bin/env python3
"""Check local Markdown files for common link mistakes."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
INLINE_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]*)\)")
OPEN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\([^)]*$")
CLOSE_LINK_RE = re.compile(r"(?<!!)(?<!\[)\]\([^)]*\)")


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def slugify_heading(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text.strip().lower())
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def anchors_by_line(lines: list[str]) -> tuple[dict[str, int], list[Issue]]:
    anchors: dict[str, int] = {}
    issues: list[Issue] = []
    for line_number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        anchor = slugify_heading(match.group(2))
        if not anchor:
            continue
        if anchor in anchors:
            issues.append(Issue(Path("<memory>"), line_number, f"duplicate anchor #{anchor}"))
        else:
            anchors[anchor] = line_number
    return anchors, issues


def check_markdown(path: Path, text: str) -> list[Issue]:
    lines = text.splitlines()
    anchors, anchor_issues = anchors_by_line(lines)
    issues: list[Issue] = [
        Issue(path, issue.line, issue.message) for issue in anchor_issues
    ]

    for line_number, line in enumerate(lines, start=1):
        leftovers = INLINE_LINK_RE.sub("", line)
        if OPEN_LINK_RE.search(leftovers) or CLOSE_LINK_RE.search(leftovers):
            issues.append(Issue(path, line_number, "malformed inline link"))

        for label, target in INLINE_LINK_RE.findall(line):
            label = label.strip()
            target = target.strip()
            if not label:
                issues.append(Issue(path, line_number, "link label is empty"))
            if not target:
                issues.append(Issue(path, line_number, "link target is empty"))
                continue
            if target.startswith("#") and target[1:] not in anchors:
                issues.append(Issue(path, line_number, f"missing local anchor {target}"))

    return issues


def scan_paths(paths: list[Path]) -> list[Issue]:
    issues: list[Issue] = []
    for path in paths:
        if not path.exists():
            issues.append(Issue(path, 0, "file does not exist"))
            continue
        issues.extend(check_markdown(path, path.read_text(encoding="utf-8")))
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check Markdown links in local files.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files to scan.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    issues = scan_paths(args.paths)
    if issues:
        for issue in issues:
            print(issue.render())
        return 1
    print(f"OK: checked {len(args.paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
