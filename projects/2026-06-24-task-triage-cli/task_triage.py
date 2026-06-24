#!/usr/bin/env python3
"""Rank simple task lists by urgency, due date, and effort."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import asdict, dataclass
from typing import Iterable


PRIORITY_POINTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "urgent": 4,
}


@dataclass(frozen=True)
class Task:
    title: str
    priority: str
    due: dt.date | None
    minutes: int
    score: int


def parse_due(value: str, today: dt.date) -> dt.date | None:
    cleaned = value.strip().lower()
    if not cleaned:
        return None
    if cleaned == "today":
        return today
    if cleaned == "tomorrow":
        return today + dt.timedelta(days=1)
    return dt.date.fromisoformat(cleaned)


def effort_bonus(minutes: int) -> int:
    if minutes <= 15:
        return 3
    if minutes <= 30:
        return 2
    if minutes <= 60:
        return 1
    return 0


def due_bonus(due: dt.date | None, today: dt.date) -> int:
    if due is None:
        return 0
    days_left = (due - today).days
    if days_left < 0:
        return 8
    if days_left == 0:
        return 6
    if days_left <= 2:
        return 4
    if days_left <= 7:
        return 2
    return 1


def parse_task(line: str, today: dt.date) -> Task:
    parts = [part.strip() for part in line.split("|")]
    if len(parts) != 4:
        raise ValueError("expected: title | priority | due date | minutes")

    title, priority, due_text, minutes_text = parts
    priority = priority.lower()
    if not title:
        raise ValueError("task title is required")
    if priority not in PRIORITY_POINTS:
        choices = ", ".join(PRIORITY_POINTS)
        raise ValueError(f"priority must be one of: {choices}")

    minutes = int(minutes_text)
    if minutes <= 0:
        raise ValueError("minutes must be greater than zero")

    due = parse_due(due_text, today)
    score = PRIORITY_POINTS[priority] * 10 + due_bonus(due, today) + effort_bonus(minutes)
    return Task(title=title, priority=priority, due=due, minutes=minutes, score=score)


def load_tasks(lines: Iterable[str], today: dt.date) -> list[Task]:
    tasks: list[Task] = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            tasks.append(parse_task(stripped, today))
        except ValueError as exc:
            raise ValueError(f"line {line_number}: {exc}") from exc
    return sorted(tasks, key=lambda task: (-task.score, task.due or dt.date.max, task.minutes, task.title.lower()))


def format_table(tasks: list[Task]) -> str:
    if not tasks:
        return "No tasks found."

    rows = [["Rank", "Score", "Priority", "Due", "Min", "Task"]]
    for index, task in enumerate(tasks, start=1):
        rows.append([
            str(index),
            str(task.score),
            task.priority,
            task.due.isoformat() if task.due else "-",
            str(task.minutes),
            task.title,
        ])

    widths = [max(len(row[column]) for row in rows) for column in range(len(rows[0]))]
    rendered = []
    for row_index, row in enumerate(rows):
        rendered.append("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
        if row_index == 0:
            rendered.append("  ".join("-" * width for width in widths))
    return "\n".join(rendered)


def task_to_json(task: Task) -> dict[str, object]:
    data = asdict(task)
    data["due"] = task.due.isoformat() if task.due else None
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank tasks from a simple pipe-delimited list.")
    parser.add_argument("path", nargs="?", help="Task file. Reads stdin when omitted.")
    parser.add_argument("--today", help="Override today's date with YYYY-MM-DD for repeatable runs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()

    if args.path:
        with open(args.path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    else:
        lines = sys.stdin.readlines()

    try:
        tasks = load_tasks(lines, today)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([task_to_json(task) for task in tasks], indent=2))
    else:
        print(format_table(tasks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

