import io
import json
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import stow

HERE = Path(__file__).parent


class StatusTests(unittest.TestCase):
    def test_status_reports_version_and_capabilities(self):
        result = stow.run({"args": {"op": "status"}})
        self.assertEqual(
            result,
            {"output": {"plugin": "stow", "version": stow.VERSION, "capabilities": ["qr"]}},
        )

    def test_version_matches_manifest(self):
        manifest = (HERE / "stow.yml").read_text(encoding="utf-8")
        declared = re.search(r"^version:\s*(\S+)\s*$", manifest, re.MULTILINE).group(1)
        self.assertEqual(stow.VERSION, declared)


class DispatchTests(unittest.TestCase):
    def test_missing_operation_is_an_error(self):
        self.assertIn("error", stow.run({"args": {}}))
        self.assertIn("error", stow.run({}))
        self.assertIn("error", stow.run({"args": {"op": 5}}))

    def test_unknown_operation_is_an_error(self):
        self.assertEqual(stow.run({"args": {"op": "nope"}}), {"error": "unknown operation: nope"})

    def test_a_failing_operation_becomes_an_error_message(self):
        def broken(_args, _connection):
            raise RuntimeError("boom")

        with mock.patch.dict(stow.OPERATIONS, {"broken": broken}):
            self.assertEqual(stow.run({"args": {"op": "broken"}}), {"error": "broken failed: boom"})


class MainTests(unittest.TestCase):
    def call(self, text):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(text)), redirect_stdout(out):
            stow.main()
        return json.loads(out.getvalue())

    def test_reads_stdin_and_prints_json(self):
        result = self.call(json.dumps({"args": {"op": "status"}}))
        self.assertEqual(result["output"]["plugin"], "stow")

    def test_invalid_input_is_reported(self):
        self.assertIn("invalid plugin input", self.call("not json")["error"])


if __name__ == "__main__":
    unittest.main()
