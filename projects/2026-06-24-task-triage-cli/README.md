# Task Triage CLI

Task Triage is a small dependency-free Python command line tool that turns a simple task list into an ordered action plan.

Each input line uses this format:

```text
task title | priority | due date | minutes
```

- `priority`: `low`, `medium`, `high`, or `urgent`
- `due date`: `YYYY-MM-DD`, `today`, `tomorrow`, or blank
- `minutes`: estimated effort as a whole number

## Run

```bash
python3 task_triage.py sample_tasks.txt
```

You can also pipe tasks through standard input:

```bash
printf 'Pay invoice | high | today | 10\nRefactor form | medium | 2026-06-30 | 90\n' | python3 task_triage.py
```

Use JSON output when another script needs the result:

```bash
python3 task_triage.py sample_tasks.txt --json
```

## Verify

```bash
python3 -m unittest discover . -v
python3 task_triage.py sample_tasks.txt
```

