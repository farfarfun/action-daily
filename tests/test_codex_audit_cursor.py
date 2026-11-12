import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import codex_audit_cursor as cursor


class CursorTest(unittest.TestCase):
    def test_unavailable_archived_and_open_issue_repos_are_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mapping = root / "mapping.json"
            state = root / "cursor.json"
            batch = root / "batch.json"
            mapping.write_text(
                json.dumps(
                    [
                        {"repo": "ready", "archived": False},
                        {"repo": "gone", "archived": False},
                        {"repo": "already-open", "archived": False},
                        {"repo": "archived", "archived": True},
                    ]
                ),
                encoding="utf-8",
            )
            state.write_text('{"last_index": -1, "batch_size": 3}', encoding="utf-8")
            with (
                patch.object(cursor, "MAPPING_PATH", str(mapping)),
                patch.object(cursor, "CURSOR_PATH", str(state)),
                patch.object(cursor, "BATCH_PATH", str(batch)),
                patch.object(cursor, "visible_repos", return_value={"ready", "already-open"}),
                patch.object(cursor, "repos_with_open_issue", return_value={"already-open"}),
            ):
                cursor.main()

            self.assertEqual(json.loads(batch.read_text(encoding="utf-8")), ["ready"])
            self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_index"], 1)


if __name__ == "__main__":
    unittest.main()
