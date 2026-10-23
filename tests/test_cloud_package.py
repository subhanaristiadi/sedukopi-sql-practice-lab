import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    def test_json_and_exercise_references(self):
        exercises = json.loads((ROOT / "exercises.json").read_text(encoding="utf-8"))
        refs = json.loads((ROOT / "reference_queries.json").read_text(encoding="utf-8"))
        topics = json.loads((ROOT / "curriculum_topics.json").read_text(encoding="utf-8"))
        self.assertEqual(47, len(exercises))
        self.assertEqual(21, len(topics))
        self.assertEqual({x["id"] for x in exercises}, set(refs))
        self.assertIn("monthly_salary", refs["SAL-01"]["sql"])
    def test_deployment_files(self):
        for name in ("server.py", "render.yaml", "seed_neon.py", "create_reader_role.sql", "DEPLOYMENT.md", "publish_to_github.bat", "index.html", "requirements.txt"):
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertNotIn("DATABASE_URL=postgres://", (ROOT / ".env.example").read_text())
    def test_frontend_points_to_api(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("const API_BASE =", html)
        self.assertIn("API_BASE+url", html)
        self.assertIn("API_BASE+\"/health\"", html)

if __name__ == "__main__": unittest.main()
