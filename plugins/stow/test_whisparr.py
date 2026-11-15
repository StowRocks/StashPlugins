import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import mock

import whisparr


class FakeWhisparr(BaseHTTPRequestHandler):
    seen = []

    def log_message(self, *_args):
        pass

    def _reply(self, status, body, content_type="application/json"):
        raw = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode() if length else None
        FakeWhisparr.seen.append((self.command, self.path, self.headers.get("X-Api-Key"), body))
        if self.path.startswith("/api/v3/movie") and self.command == "POST":
            self._reply(400, '[{"errorMessage":"already added"}]')
        elif self.path == "/ping":
            self._reply(200, '{"status":"OK"}')
        else:
            self._reply(200, '[{"id": 1}]')

    do_GET = do_POST = do_DELETE = do_PUT = _handle


class ForwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeWhisparr)
        cls.settings = {
            "whisparrUrl": f"http://127.0.0.1:{cls.server.server_port}/",
            "whisparrApiKey": "secret-key",
        }
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        FakeWhisparr.seen.clear()

    def test_get_sends_the_key_and_returns_status_and_raw_body(self):
        reply = whisparr.forward(
            self.settings, {"method": "GET", "path": "api/v3/movie", "query": [["stashId", "abc"]]}
        )
        self.assertEqual(reply["status"], 200)
        self.assertEqual(reply["body"], '[{"id": 1}]')
        self.assertEqual(
            FakeWhisparr.seen, [("GET", "/api/v3/movie?stashId=abc", "secret-key", None)]
        )

    def test_repeated_query_names_keep_their_order(self):
        whisparr.forward(
            self.settings,
            {"path": "api/v3/queue", "query": [["page", "1"], ["movieIds", "3"], ["movieIds", "4"]]},
        )
        self.assertEqual(FakeWhisparr.seen[0][1], "/api/v3/queue?page=1&movieIds=3&movieIds=4")

    def test_ping_is_anonymous(self):
        whisparr.forward(self.settings, {"method": "GET", "path": "ping"})
        self.assertIsNone(FakeWhisparr.seen[0][2])

    def test_post_sends_the_body_and_error_statuses_come_back_as_they_are(self):
        reply = whisparr.forward(
            self.settings, {"method": "POST", "path": "api/v3/movie", "body": '{"title": "x"}'}
        )
        self.assertEqual(reply["status"], 400)
        self.assertIn("already added", reply["body"])
        self.assertEqual(FakeWhisparr.seen[0][3], '{"title": "x"}')

    def test_delete_and_put_are_forwarded(self):
        whisparr.forward(self.settings, {"method": "DELETE", "path": "api/v3/queue/42"})
        whisparr.forward(self.settings, {"method": "PUT", "path": "api/v3/studio/7", "body": "{}"})
        self.assertEqual([s[0] for s in FakeWhisparr.seen], ["DELETE", "PUT"])

    def test_paths_outside_the_list_are_refused_before_any_request(self):
        for method, path in [
            ("GET", "api/v3/config/host"),
            ("DELETE", "api/v3/movie"),
            ("DELETE", "api/v3/movie/1/../../config"),
            ("POST", "api/v3/queue"),
            ("GET", "../../etc/passwd"),
            ("PATCH", "api/v3/movie"),
            ("GET", ""),
        ]:
            with self.subTest(method=method, path=path):
                with self.assertRaises(ValueError):
                    whisparr.forward(self.settings, {"method": method, "path": path})
        self.assertEqual(FakeWhisparr.seen, [])

    def test_an_unreachable_server_is_a_connection_error(self):
        settings = {"whisparrUrl": "http://127.0.0.1:1/", "whisparrApiKey": "k"}
        with self.assertRaises(ConnectionError):
            whisparr.forward(settings, {"method": "GET", "path": "ping"})


class SettingsTests(unittest.TestCase):
    def test_missing_settings_are_refused(self):
        for settings in [{}, {"whisparrUrl": "http://x"}, {"whisparrApiKey": "k"}]:
            with self.subTest(settings=settings):
                with self.assertRaises(whisparr.WhisparrNotConfigured):
                    whisparr.base_url(settings)

    def test_url_must_be_http(self):
        with self.assertRaises(whisparr.WhisparrNotConfigured):
            whisparr.base_url({"whisparrUrl": "ftp://x", "whisparrApiKey": "k"})

    def test_base_url_gets_one_trailing_slash(self):
        self.assertEqual(
            whisparr.base_url({"whisparrUrl": " http://w:6969// ", "whisparrApiKey": " k "}),
            ("http://w:6969/", "k"),
        )

    def test_stash_url_uses_the_connection_and_never_a_wildcard_host(self):
        self.assertEqual(
            whisparr.stash_url({"Scheme": "https", "Host": "stash.lan", "Port": 9443}),
            "https://stash.lan:9443/graphql",
        )
        self.assertEqual(
            whisparr.stash_url({"Scheme": "http", "Host": "0.0.0.0", "Port": 9999}),
            "http://127.0.0.1:9999/graphql",
        )
        self.assertEqual(whisparr.stash_url({}), "http://127.0.0.1:9999/graphql")

    def test_settings_are_read_from_the_stash_configuration_with_the_session_cookie(self):
        reply = mock.MagicMock()
        reply.__enter__.return_value = reply
        reply.read.return_value = json.dumps(
            {"data": {"configuration": {"plugins": {"stow": {"whisparrUrl": "http://w"}}}}}
        ).encode()
        connection = {"Port": 9999, "SessionCookie": {"Name": "session", "Value": "abc"}}
        with mock.patch("urllib.request.urlopen", return_value=reply) as opened:
            with mock.patch("json.load", return_value=json.loads(reply.read.return_value)):
                settings = whisparr.read_settings(connection)
        self.assertEqual(settings, {"whisparrUrl": "http://w"})
        request = opened.call_args.args[0]
        self.assertEqual(request.get_header("Cookie"), "session=abc")

    def test_no_plugin_settings_means_empty(self):
        reply = mock.MagicMock()
        reply.__enter__.return_value = reply
        with mock.patch("urllib.request.urlopen", return_value=reply):
            with mock.patch("json.load", return_value={"data": {"configuration": {"plugins": {}}}}):
                self.assertEqual(whisparr.read_settings({}), {})

    def test_configured_is_false_when_stash_cannot_be_read(self):
        with mock.patch("whisparr.read_settings", side_effect=OSError("down")):
            self.assertFalse(whisparr.configured({}))
        with mock.patch("whisparr.read_settings", return_value={"whisparrUrl": "http://w", "whisparrApiKey": "k"}):
            self.assertTrue(whisparr.configured({}))


class ResolveTests(unittest.TestCase):
    OWN = {"whisparrUrl": "http://own:6969", "whisparrApiKey": "own-key"}
    OTHER = {"whisparrUrl": "http://other:6969", "whisparrApiKey": "other-key", "whisparrQualityProfile": "4"}

    def test_the_own_settings_win(self):
        settings, source = whisparr.resolve({"stow": self.OWN, "missingScenes": self.OTHER})
        self.assertEqual((settings, source), (self.OWN, "stow"))

    def test_the_missing_scenes_plugin_is_used_when_this_one_is_empty(self):
        settings, source = whisparr.resolve({"stow": {}, "missingScenes": self.OTHER})
        self.assertEqual(source, "missingScenes")
        self.assertEqual(settings, {"whisparrUrl": "http://other:6969", "whisparrApiKey": "other-key"})
        settings, source = whisparr.resolve({"missingScenes": self.OTHER})
        self.assertEqual(source, "missingScenes")

    def test_address_and_key_are_never_mixed_between_plugins(self):
        half = {"whisparrUrl": "http://own:6969", "whisparrApiKey": "  "}
        settings, source = whisparr.resolve({"stow": half, "missingScenes": self.OTHER})
        self.assertEqual(source, "missingScenes")
        self.assertEqual(settings["whisparrUrl"], "http://other:6969")
        settings, source = whisparr.resolve({"stow": half, "missingScenes": {"whisparrUrl": "http://other:6969"}})
        self.assertIsNone(source)
        self.assertEqual(settings, half)

    def test_nothing_set_means_no_source(self):
        self.assertEqual(whisparr.resolve({}), ({}, None))

    def test_read_settings_and_source_follow_the_resolution(self):
        plugins = {"stow": {}, "missingScenes": self.OTHER}
        with mock.patch("whisparr.read_all_settings", return_value=plugins):
            self.assertEqual(whisparr.read_settings({})["whisparrApiKey"], "other-key")
            self.assertEqual(whisparr.source({}), "missingScenes")
        with mock.patch("whisparr.read_all_settings", side_effect=OSError("down")):
            self.assertIsNone(whisparr.source({}))


class OperationTests(unittest.TestCase):
    def test_the_operation_reads_the_settings_and_forwards(self):
        with mock.patch("whisparr.read_settings", return_value={"a": 1}) as read:
            with mock.patch("whisparr.forward", return_value={"status": 200}) as forward:
                result = whisparr.op_whisparr({"path": "ping"}, {"Port": 1})
        read.assert_called_once_with({"Port": 1})
        forward.assert_called_once_with({"a": 1}, {"path": "ping"})
        self.assertEqual(result, {"status": 200})


if __name__ == "__main__":
    unittest.main()
