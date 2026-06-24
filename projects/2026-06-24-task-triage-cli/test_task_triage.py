import datetime as dt
import json
import unittest

import task_triage


class TaskTriageTests(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 6, 24)

    def test_parse_relative_due_dates(self):
        self.assertEqual(task_triage.parse_due("today", self.today), self.today)
        self.assertEqual(task_triage.parse_due("tomorrow", self.today), dt.date(2026, 6, 25))
        self.assertIsNone(task_triage.parse_due(" ", self.today))

    def test_load_tasks_sorts_high_value_work_first(self):
        lines = [
            "Later chore | low | 2026-07-01 | 10",
            "Tiny urgent task | urgent | today | 5",
            "Big urgent task | urgent | today | 120",
        ]

        tasks = task_triage.load_tasks(lines, self.today)

        self.assertEqual([task.title for task in tasks], [
            "Tiny urgent task",
            "Big urgent task",
            "Later chore",
        ])

    def test_invalid_priority_reports_line_number(self):
        with self.assertRaisesRegex(ValueError, "line 2"):
            task_triage.load_tasks([
                "Valid | low | today | 5",
                "Broken | someday | today | 5",
            ], self.today)

    def test_json_serializer_uses_iso_date(self):
        task = task_triage.parse_task("Call clinic | high | 2026-06-26 | 12", self.today)

        encoded = json.dumps(task_triage.task_to_json(task))

        self.assertIn('"due": "2026-06-26"', encoded)


if __name__ == "__main__":
    unittest.main()

