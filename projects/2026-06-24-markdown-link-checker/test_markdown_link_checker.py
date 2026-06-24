import pathlib
import tempfile
import unittest

import markdown_link_checker as checker


class MarkdownLinkCheckerTests(unittest.TestCase):
    def test_slugifies_heading_text(self):
        self.assertEqual(checker.slugify_heading("Setup & Usage!"), "setup-usage")
        self.assertEqual(checker.slugify_heading("Use `code` Here"), "use-code-here")

    def test_reports_missing_local_anchor(self):
        issues = checker.check_markdown(pathlib.Path("notes.md"), "# Notes\nSee [missing](#missing).\n")

        self.assertEqual(len(issues), 1)
        self.assertIn("missing local anchor #missing", issues[0].message)

    def test_reports_empty_label_and_target(self):
        issues = checker.check_markdown(pathlib.Path("notes.md"), "# Notes\n[]()\n")

        messages = [issue.message for issue in issues]
        self.assertIn("link label is empty", messages)
        self.assertIn("link target is empty", messages)

    def test_reports_duplicate_anchors(self):
        issues = checker.check_markdown(pathlib.Path("notes.md"), "# Intro\n## Intro\n")

        self.assertEqual(issues[0].message, "duplicate anchor #intro")

    def test_scan_paths_reports_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = pathlib.Path(temp_dir) / "missing.md"

            issues = checker.scan_paths([missing])

        self.assertEqual(issues[0].line, 0)
        self.assertEqual(issues[0].message, "file does not exist")


if __name__ == "__main__":
    unittest.main()

