import json
import unittest
from pathlib import Path


class ParityFixtureTests(unittest.TestCase):
    def test_fixture_schema(self):
        fixture_dir = Path(__file__).parent / "fixtures" / "parity"
        files = sorted(fixture_dir.glob("*.json"))
        self.assertGreaterEqual(len(files), 12)
        for path in files:
            data = json.loads(path.read_text())
            self.assertIn("scenario", data)
            self.assertIn("input", data)
            self.assertIn("expected", data)
            self.assertIn("selected_strategy", data["expected"])
            self.assertIn("selected_sub_strategy", data["expected"])
            self.assertIn("write_decision", data["expected"])


if __name__ == "__main__":
    unittest.main()
