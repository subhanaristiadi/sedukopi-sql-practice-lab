"""Static package tests; these do not require a PostgreSQL server."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PackageTests(unittest.TestCase):
    def test_json_is_valid(self):
        exercises = json.loads((ROOT / "exercises.json").read_text(encoding="utf-8"))
        refs = json.loads((ROOT / "reference_queries.json").read_text(encoding="utf-8"))
        self.assertEqual(len(exercises), 47)
        curriculum = json.loads((ROOT / "curriculum_topics.json").read_text(encoding="utf-8"))
        self.assertEqual(len(curriculum), 21)
        self.assertTrue(all(set(t["exercise_ids"]).issubset({e["id"] for e in exercises}) for t in curriculum))
        self.assertEqual({e["id"] for e in exercises}, set(refs))
        self.assertEqual(len({e["id"] for e in exercises}), len(exercises))
        for exercise in exercises:
            self.assertTrue(refs[exercise["id"]]["sql"].strip().upper().startswith(("SELECT", "WITH")))

    def test_required_files_exist(self):
        for name in ["server.py", "index.html", "README.md", "DEPLOYMENT.md",
                     "coverage_matrix.md", "requirements.txt", ".env.example",
                     ".gitignore", "render.yaml", "seed_neon.py", "create_reader_role.sql"]:
            self.assertTrue((ROOT / name).is_file(), name)

if __name__ == "__main__":
    unittest.main()
