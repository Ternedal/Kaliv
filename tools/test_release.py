"""Check drift reporting, deduplication and read-only behavior with an isolated API."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("release_check", Path(__file__).with_name("check-release.py"))
release_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_check)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.project = {"latest_release": {"version": "2.0.19"}}
        self.release = {"tag_name": "v2.0.20", "published_at": "2030-01-01T12:00:00Z", "draft": False, "prerelease": False}
        self.issue = release_check.issue_for(self.project, self.release)
        self.calls = []
        self.issues = []

    def api(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        return self.issues if method == "GET" else {"number": 42}

    def test_current_release_makes_no_issue_api_calls(self):
        self.release["tag_name"] = "v2.0.19"
        issue = release_check.issue_for(self.project, self.release)
        self.assertEqual(release_check.report_issue(self.api, "Ternedal/Kaliv", issue, True)["action"], "current")
        self.assertEqual(self.calls, [])

    def test_drift_creates_one_report_with_both_versions_and_source(self):
        result = release_check.report_issue(self.api, "Ternedal/Kaliv", self.issue, True)
        self.assertEqual(result, {"action": "created", "number": 42})
        self.assertEqual([c[0] for c in self.calls], ["GET", "POST"])
        self.assertIn("v2.0.19", self.calls[-1][2]["body"])
        self.assertIn("v2.0.20", self.calls[-1][2]["body"])
        self.assertIn("https://api.github.com/repos/Ternedal/ModelRig/releases/latest", self.calls[-1][2]["body"])

    def test_repeated_drift_reuses_bot_issue(self):
        self.issues = [{**self.issue, "user": {"login": "github-actions[bot]"}, "number": 42}]
        self.assertEqual(release_check.report_issue(self.api, "Ternedal/Kaliv", self.issue, True)["action"], "existing")
        self.assertEqual([c[0] for c in self.calls], ["GET"])
        newer = release_check.issue_for(self.project, {**self.release, "tag_name": "v2.0.21"})
        self.assertEqual(release_check.report_issue(self.api, "Ternedal/Kaliv", newer, True)["action"], "updated")
        self.assertEqual(self.calls[-1][0], "PATCH")

    def test_dry_run_does_not_write_or_reuse_a_persons_issue(self):
        self.issues = [{**self.issue, "user": {"login": "Ternedal"}, "number": 3}]
        result = release_check.report_issue(self.api, "Ternedal/Kaliv", self.issue)
        self.assertEqual(result["action"], "would-create")
        self.assertEqual([c[0] for c in self.calls], ["GET"])

    def test_finds_existing_report_on_the_second_page(self):
        existing = {**self.issue, "user": {"login": "github-actions[bot]"}, "number": 42}
        def paginated(method, path, payload=None):
            self.calls.append((method, path, payload))
            return [{"number": n} for n in range(100)] if path.endswith("page=1") else [existing]
        self.assertEqual(release_check.report_issue(paginated, "Ternedal/Kaliv", self.issue, True)["action"], "existing")
        self.assertEqual(len(self.calls), 2)

    def test_nonstable_or_draft_release_fails(self):
        for change in ({"draft": True}, {"prerelease": True}, {"tag_name": "v2.0.20-rc1"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                release_check.issue_for(self.project, {**self.release, **change})


if __name__ == "__main__":
    unittest.main()
